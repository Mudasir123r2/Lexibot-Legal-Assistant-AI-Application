from fastapi import APIRouter, Depends, HTTPException, status, Query
from config.database import get_db
from models.judgment import JudgmentCreate, JudgmentUpdate, JudgmentResponse, JudgmentSearchRequest
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
import re
import logging
import asyncio
from utils.formatters import format_judgment_title, extract_court

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/judgments", tags=["Judgments"])


@router.get("/search")
async def search_judgments(
    query: Optional[str] = Query(None, description="Search in title, case number, keywords, summary"),
    caseType: Optional[str] = Query(None, description="Filter by case type"),
    court: Optional[str] = Query(None, description="Filter by court name"),
    year: Optional[str] = Query(None, description="Filter by year (extracted from date or title)"),
    limit: int = Query(20, le=100),
    page: int = Query(1, ge=1)
):
    import traceback
    try:
        from services.rag_pipeline import get_rag_pipeline
        from services.llm_service import get_llm_service
        rag = get_rag_pipeline()
        vector_store = rag.vector_store

        all_judgments = []

        # ── Semantic search path (preferred) ──────────────────────────────
        if query and len(query.strip()) > 2:
            try:
                # search_judgments returns _format_sources output:
                # [{id, title, case_type, court, date, similarity, excerpt}, ...]
                semantic_docs = rag.search_judgments(query, top_k=limit * 10) # Reduced from 50x to 10x for massive speedup
                
                # ENFORCE EASY LAW ONLY FILTER & REMOVE STATUTES
                easylaw_docs = []
                for doc in semantic_docs:
                    journal = str(doc.get("journal") or "")
                    case_num = str(doc.get("case_number") or doc.get("caseNumber") or "")
                    src = str(doc.get("source_file") or "")
                    cat = str(doc.get("category") or doc.get("case_type") or doc.get("caseType") or "")
                    title = str(doc.get("title") or "")
                    
                    # Hard filter to remove Acts and Ordinances
                    title_l = title.lower()
                    if (
                        cat.lower() in ("statute", "law", "act") 
                        or "laws/" in src.lower() 
                        or ("ordinance" in title_l)
                        or (("act," in title_l or "act 19" in title_l or "act 20" in title_l) and " vs " not in title_l and " v " not in title_l and " v. " not in title_l)
                    ):
                        continue

                    # Strict Court/Location Enforcer (Fixes Semantic Bleed across High Courts)
                    query_l = query.lower()
                    doc_court_l = str(doc.get("court") or "").lower()
                    doc_content_l = str(doc.get("excerpt") or doc.get("content") or "").lower()
                    loc_keys = ["sindh", "karachi", "lahore", "peshawar", "balochistan", "islamabad", "supreme", "federal shariat"]
                    
                    should_skip_due_to_location = False
                    for loc in loc_keys:
                        # If user specifically typed a court location, the document MUST contain that location.
                        if loc in query_l:
                            if loc not in title_l and loc not in doc_court_l and loc not in doc_content_l:
                                should_skip_due_to_location = True
                                break
                                
                    if should_skip_due_to_location:
                        continue

                    # Only allow Easy Law judgments (usually represented by journal)
                    if journal or "Appeal No" in case_num or src.startswith("administrator"):
                        easylaw_docs.append(doc)
                
                semantic_docs = easylaw_docs

                seen_keys = set()
                for doc in semantic_docs:
                    # Use the pre-calculated ID from the search results (repaired mock_id)
                    mock_id = doc.get("id") or doc.get("_id")
                    
                    if mock_id in seen_keys:
                        continue
                    seen_keys.add(mock_id)
                    
                    all_judgments.append({
                        "_id":           mock_id,
                        "title":         doc.get("title") or "Untitled Judgment",
                        "caseNumber":    doc.get("case_number") or "N/A",
                        "caseType":      doc.get("case_type") or doc.get("category") or doc.get("caseType") or ("Statute" if "Act" in doc.get("title", "") or "Ordinance" in doc.get("title", "") else "Judgment"),
                        "court":         doc.get("court")       or "Supreme Court of Pakistan",
                        "dateOfJudgment": doc.get("date")        or "",
                        "judge":         doc.get("judge")       or "",
                        "summary":       doc.get("excerpt")     or "",
                        "score":         doc.get("similarity")  or 0.0,
                        "journal":       doc.get("journal")     or "",
                        "parties":       doc.get("parties")     or "",
                        "lawyers":       doc.get("lawyers")     or "",
                        "statutes":      doc.get("statutes")    or ""
                    })

            except Exception as sem_err:
                logger.error(f"Semantic search failed, falling back to metadata scan: {sem_err}\n{traceback.format_exc()}")
                # Fall through to metadata scan below

        # ── EXACT KEYWORD MATCH (Metadata & Full-text Scan) ────
        # Run alongside Semantic Search to guarantee Lawyer Names, Judges, Case Numbers appear!
        import sqlite3, json as _json
        db_path = vector_store.index_path / "metadata.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path), check_same_thread=False)
            conn.row_factory = sqlite3.Row
            try:
                # Build WHERE clause
                # Enforce strictly Easy Law documents as requested by user
                conditions = ["(excerpt LIKE '%Journal %' OR excerpt LIKE '%\nAppeal No.%' OR source_file LIKE 'administrator%')"]
                conditions.append("(category != 'Statute' AND title NOT LIKE '%Ordinance%' AND title NOT LIKE '%Act, %')")
                params = []
                if query:
                    # Expanded FAST fallback query focusing on keywords, lawyers, judges, titles
                    conditions.insert(0,
                        "(title LIKE ? OR court LIKE ? OR judge LIKE ? OR excerpt LIKE ? OR case_number LIKE ?)"
                    )
                    q_like = f"%{query}%"
                    params += [q_like, q_like, q_like, q_like, q_like]
                if caseType:
                    conditions.append("(case_type LIKE ? OR category LIKE ?)")
                    ct_like = f"%{caseType}%"
                    params += [ct_like, ct_like]
                if court:
                    conditions.append("court LIKE ?")
                    params.append(f"%{court}%")

                where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

                # Get distinct documents (group by mock_id to handle repaired titles)
                sql = f"""
                    SELECT mock_id, title, source_file, court, judge, date,
                           case_number, case_type, category, excerpt,
                           MIN(row_id) as row_id
                    FROM chunks
                    {where}
                    GROUP BY mock_id
                    ORDER BY row_id
                    LIMIT {limit * 10}
                """
                rows = conn.execute(sql, params).fetchall()
                
                exact_matches = []
                for row in rows:
                    title    = row["title"] or "Untitled"
                    source   = row["source_file"] or ""
                    case_num = row["case_number"] or ""
                    # Use pre-calculated mock_id from SQLite repair
                    mock_id  = row["mock_id"]
                    
                    if mock_id in seen_keys:
                        continue
                    seen_keys.add(mock_id)
                    
                    from utils.formatters import extract_full_metadata
                    full_meta = extract_full_metadata(row["excerpt"])
                    
                    exact_matches.append({
                        "_id":            mock_id,
                        "title": format_judgment_title(case_num, row["court"], title, row["excerpt"], source),
                        "caseNumber": case_num or "N/A",
                        "caseType":       str(row["case_type"] or row["category"] or ("Statute" if "Act" in title or "Ordinance" in title else "Judgment")),
                        "court":          str(extract_court(row["court"], row["excerpt"]) or "Supreme Court of Pakistan"),
                        "dateOfJudgment": str(row["date"] or ""),
                        "judge":          full_meta["judge"] or row["judge"] or "",
                        "summary":        (row["excerpt"] or "")[:300] + "...",
                        "score":          1.0,
                        "journal":        full_meta["journal"],
                        "parties":        full_meta["parties"],
                        "lawyers":        full_meta["lawyers"],
                        "statutes":       full_meta["statutes"]
                    })
                
                # Prepend exact SQL text matches to Semantic search for true hybrid functionality
                all_judgments = exact_matches + all_judgments

            except Exception as e:
                logger.error(f"Metadata scan failed: {e}")
            finally:
                conn.close()
        else:
            # Last resort: capped metadata property (50k limit)
            for chunk in vector_store.metadata:
                exc = str(chunk.get("excerpt") or chunk.get("content") or "")
                src = str(chunk.get("source_file") or chunk.get("sourceFile") or "")
                if "Journal " not in exc and "\nAppeal No." not in exc and not src.startswith("administrator"):
                    continue
                
                mock_id   = chunk.get("mock_id")
                title     = chunk.get("title") or "Untitled"
                if not any(j["_id"] == mock_id for j in all_judgments):
                    from utils.formatters import extract_full_metadata
                    full_meta = extract_full_metadata(chunk.get("excerpt") or chunk.get("content", ""))
                    all_judgments.append({
                        "_id":            mock_id,
                        "title":          format_judgment_title(chunk.get("case_number"), chunk.get("court"), title, chunk.get("excerpt"), chunk.get("source_file", "")),
                        "caseNumber":     chunk.get("case_number") or "N/A",
                        "caseType":       str(chunk.get("case_type") or chunk.get("category") or ("Statute" if "Act" in title or "Ordinance" in title else "Judgment")),
                        "court":          str(extract_court(chunk.get("court"), chunk.get("excerpt")) or "Supreme Court of Pakistan"),
                        "dateOfJudgment": str(chunk.get("date") or ""),
                        "judge":          full_meta["judge"] or chunk.get("judge") or "",
                        "summary":        (chunk.get("excerpt") or chunk.get("content", "")[:300]) + "...",
                        "score":          0.0,
                        "journal":        full_meta["journal"],
                        "parties":        full_meta["parties"],
                        "lawyers":        full_meta["lawyers"],
                        "statutes":       full_meta["statutes"]
                    })


        # ── Clean Year & Optional field filters ─────────────────────────────
        import re

        for j in all_judgments:
            found_year = None
            date_str = str(j.get("dateOfJudgment") or "")
            title_str = str(j.get("title") or "")
            
            # 1. Try to pluck standard 19xx/20xx year from DateOfJudgment
            date_match = re.search(r'\b(19\d{2}|20\d{2})\b', date_str)
            if date_match:
                found_year = date_match.group(1)
            else:
                # 2. Try to pull it from the title (like 1974 PLD 185)
                title_match = re.search(r'\b(19\d{2}|20\d{2})\b', title_str)
                if title_match:
                    found_year = title_match.group(1)
            
            j["year"] = found_year or "Unknown"

        if year:
            all_judgments = [j for j in all_judgments if j.get("year") == str(year)]

        if caseType:
            c_lower = caseType.lower()
            all_judgments = [j for j in all_judgments if c_lower in str(j.get("caseType") or "").lower()]

        if court:
            court_lower = court.lower()
            all_judgments = [j for j in all_judgments if court_lower in str(j.get("court") or "").lower()]

        # ── Pagination ────────────────────────────────────────────────────
        total = len(all_judgments)
        skip  = (page - 1) * limit
        paginated = all_judgments[skip: skip + limit]

        return {
            "judgments": paginated,
            "pagination": {
                "total":  total,
                "page":   page,
                "limit":  limit,
                "pages":  (total + limit - 1) // limit
            }
        }

    except Exception as e:
        tb = traceback.format_exc()
        print(f"Error searching judgments: {e}\n{tb}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search judgments: {str(e)}"
        )


@router.get("/{judgment_id}", response_model=JudgmentResponse)
async def get_judgment(judgment_id: str, db = Depends(get_db)):
    """Get a specific judgment by ID"""
    try:
        from bson.errors import InvalidId
        from services.rag_pipeline import get_rag_pipeline
        from services.llm_service import get_llm_service
        import sqlite3
        
        # 1. Try finding in MongoDB first (Legacy or New high-level JSON)
        judgment = None
        if ObjectId.is_valid(judgment_id):
            try:
                # Set a tight timeout for MongoDB to prevent UI hangs
                judgment = await asyncio.wait_for(
                    db.judgments.find_one({"_id": ObjectId(judgment_id)}),
                    timeout=1.5
                )
            except (InvalidId, asyncio.TimeoutError, Exception) as e:
                logger.warning(f"Note: MongoDB lookup skipped/failed for {judgment_id} (Falling back to SQLite): {e}")
                judgment = None

        if judgment:
            raw_text = judgment.get("content") or judgment.get("fullText") or ""
            # OCR Cleaning
            metadata_dict = {
                "title": judgment.get("title") or judgment.get("name") or "",
                "case_number": judgment.get("caseNumber") or judgment.get("case_number") or "",
                "court": judgment.get("court") or "",
                "date": judgment.get("dateOfJudgment") or judgment.get("date") or "",
                "case_type": judgment.get("caseType") or judgment.get("category") or ""
            }
            print(f"Cleaning OCR text for MongoDB judgment {judgment_id}...")
            
            from starlette.concurrency import run_in_threadpool
            cleaned_text = await run_in_threadpool(get_llm_service().clean_ocr_text, raw_text, metadata=metadata_dict)

            from utils.formatters import extract_full_metadata
            full_meta = extract_full_metadata(raw_text)

            return {
                "_id": str(judgment["_id"]),
                "title": format_judgment_title(
                    judgment.get("caseNumber") or judgment.get("case_number"),
                    judgment.get("court"),
                    judgment.get("title") or judgment.get("name"),
                    judgment.get("summary") or judgment.get("fullText", "")[:1000],
                    judgment.get("sourceFile") or judgment.get("source_file", "")
                ),
                "content": cleaned_text,
                "caseNumber": judgment.get("caseNumber") or judgment.get("case_number") or "N/A",
                "court": judgment.get("court") or "Supreme Court of Pakistan",
                "dateOfJudgment": judgment.get("dateOfJudgment") or judgment.get("date") or "",
                "judge": full_meta["judge"] or judgment.get("judge") or "Hon'ble Court",
                "caseType": judgment.get("caseType") or judgment.get("category") or "Judgment",
                "summary": judgment.get("summary") or judgment.get("excerpt") or "",
                "fullText": cleaned_text,
                "journal": full_meta["journal"] or judgment.get("journal"),
                "parties": full_meta["parties"] or judgment.get("parties"),
                "lawyers": full_meta["lawyers"] or judgment.get("lawyers"),
                "statutes": full_meta["statutes"] or judgment.get("statutes")
            }

        # 2. Try SQLite fallback (Repaired large datasets)
        vector_store = get_rag_pipeline().vector_store
        db_path = vector_store.index_path / "metadata.db"
        
        if db_path.exists():
            conn = sqlite3.connect(str(db_path), check_same_thread=False)
            conn.row_factory = sqlite3.Row
            try:
                # Fetch metadata for this ID
                ref_row = conn.execute(
                    "SELECT * FROM chunks WHERE mock_id = ? LIMIT 1",
                    (judgment_id,)
                ).fetchone()

                if ref_row:
                    # Reconstruct full text from all related chunks
                    chunks = conn.execute(
                        "SELECT excerpt FROM chunks WHERE mock_id = ? ORDER BY row_id",
                        (judgment_id,)
                    ).fetchall()
                    
                    full_text = "\n\n".join([c["excerpt"] for c in chunks if c["excerpt"]])

                    # The user explicitly requested LLM-powered perfect structuring over fast Regex!
                    # This routes the raw SQLite FAISS text through Cerebras for a deep clean and schema structure.
                    from services.llm_service import get_llm_service
                    metadata_dict = {
                        "title": ref_row["title"] or "",
                        "case_number": ref_row["case_number"] or "",
                        "court": ref_row["court"] or "",
                        "date": ref_row["date"] or "",
                        "case_type": ref_row["case_type"] or ""
                    }
                    
                    try:
                        print(f"Cleaning OCR text via LLM Restructurer for FAISS SQLite judgment {judgment_id}...")
                        from starlette.concurrency import run_in_threadpool
                        llm_cleaned = await run_in_threadpool(get_llm_service().clean_ocr_text, full_text, metadata=metadata_dict)
                        if llm_cleaned and len(llm_cleaned) > 50:
                            full_text = llm_cleaned
                    except Exception as ll_e:
                        print(f"LLM Cleaning failed, falling back to raw: {ll_e}")

                    from utils.formatters import extract_full_metadata
                    full_meta = extract_full_metadata(ref_row["excerpt"] or full_text[:1500])

                    # Convert date string to datetime object for Pydantic validation
                    judgment_date = None
                    raw_date = full_meta["date"] or ref_row["date"]
                    if raw_date:
                        try:
                            from dateutil import parser
                            judgment_date = parser.parse(raw_date, fuzzy=True)
                        except:
                            judgment_date = datetime.utcnow()
                    else:
                        judgment_date = datetime.utcnow()

                    clean_title = format_judgment_title(
                        ref_row["case_number"], ref_row["court"], ref_row["title"],
                        ref_row["excerpt"], ref_row["source_file"] or ""
                    )

                    return {
                        "_id":            ref_row["mock_id"],
                        "id":             ref_row["mock_id"],
                        "title":          clean_title,
                        "caseNumber":     ref_row["case_number"] or "N/A",
                        "caseType":       ref_row["case_type"] or ref_row["category"] or "Judgment",
                        "court":          extract_court(ref_row["court"], ref_row["excerpt"]) or "Supreme Court of Pakistan",
                        "dateOfJudgment": judgment_date,
                        "judge":          full_meta["judge"] or ref_row["judge"] or "Hon'ble Bench",
                        "fullText":       full_text,
                        "content":        full_text,
                        "summary":        (ref_row["excerpt"] or "")[:500] if ref_row["excerpt"] else "",
                        "keywords":       [],
                        "citations":      [],
                        "sourceFile":     ref_row["source_file"] or f"{judgment_id}.txt",
                        "journal":        full_meta["journal"],
                        "parties":        full_meta["parties"],
                        "lawyers":        full_meta["lawyers"],
                        "statutes":       full_meta["statutes"]
                    }
            finally:
                conn.close()

        # If not found anywhere
        logger.warning(f"Judgment {judgment_id} not found in MongoDB or SQLite.")
        raise HTTPException(
            status_code=404, 
            detail="Judgment not found. Your search results may be outdated. Please refresh your search."
        )

    except Exception as e:
        import traceback
        error_msg = f"CRITICAL Error in get_judgment for ID {judgment_id}: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        logger.error(error_msg)
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=JudgmentResponse, status_code=status.HTTP_201_CREATED)
async def create_judgment(judgment_data: JudgmentCreate, db = Depends(get_db)):
    """Create a new judgment"""
    try:
        # Auto-extract year if not provided
        year = judgment_data.year
        if not year and judgment_data.dateOfJudgment:
            year = judgment_data.dateOfJudgment.year
        
        judgment_doc = {
            "caseNumber": judgment_data.caseNumber,
            "title": judgment_data.title,
            "court": judgment_data.court,
            "judge": judgment_data.judge,
            "dateOfJudgment": judgment_data.dateOfJudgment,
            "fullText": judgment_data.fullText,
            "summary": judgment_data.summary,
            "keyInformation": judgment_data.keyInformation.model_dump() if judgment_data.keyInformation else {
                "parties": [],
                "issues": [],
                "decisions": [],
                "deadlines": [],
                "obligations": []
            },
            "caseType": judgment_data.caseType,
            "keywords": judgment_data.keywords,
            "citations": judgment_data.citations,
            "referencedCases": [],
            "jurisdiction": judgment_data.jurisdiction,
            "year": year,
            "tags": judgment_data.tags,
            "embedding": None,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = await db.judgments.insert_one(judgment_doc)
        judgment_doc["_id"] = str(result.inserted_id)
        
        return judgment_doc
        
    except Exception as e:
        print(f"Error creating judgment: {e}")
        if "duplicate key error" in str(e).lower() or "caseNumber" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Case number already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create judgment"
        )
