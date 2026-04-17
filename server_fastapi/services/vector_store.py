"""
Vector Store Service
Manages FAISS index for efficient similarity search of legal documents.
Metadata is stored in SQLite (instead of a monolithic pickle) to handle
large corpora (200k+ chunks) without out-of-memory errors.
"""

import faiss
import numpy as np
import pickle
import os
import sqlite3
import json
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class VectorStore:
    """
    FAISS-based vector store for semantic search of legal judgments.

    Features:
    - Fast similarity search using FAISS IndexFlatL2
    - SQLite metadata backend (handles millions of chunks without OOM)
    - Persistent storage (save/load index)
    - Backward-compatible: migrates legacy metadata.pkl on first boot
    """

    def __init__(self, dimension: int = 384, index_path: str = "data/faiss_index"):
        self.dimension = dimension
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)

        # FAISS index
        self.index = faiss.IndexFlatL2(dimension)

        # SQLite path for metadata
        self.db_path = self.index_path / "metadata.db"

        # Legacy in-memory list kept for backward compatibility with code
        # that accesses vector_store.metadata directly.
        # We lazy-populate it only when accessed (see property below).
        self._metadata_cache: Optional[List[Dict[str, Any]]] = None

        # Set up SQLite schema
        self._init_db()

        # Load FAISS binary index (fast – does NOT load metadata into RAM)
        self._load_index()

        # Migrate legacy pickle if SQLite is empty
        self._maybe_migrate_pickle()

    # ------------------------------------------------------------------
    # DB setup
    # ------------------------------------------------------------------
    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    row_id      INTEGER PRIMARY KEY,
                    mock_id     TEXT,
                    title       TEXT,
                    source_file TEXT,
                    court       TEXT,
                    judge       TEXT,
                    date        TEXT,
                    case_number TEXT,
                    case_type   TEXT,
                    category    TEXT,
                    excerpt     TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_mock   ON chunks(mock_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_title  ON chunks(title)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_source ON chunks(source_file)")

    def _get_conn(self):
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        # Performance tuning
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    # ------------------------------------------------------------------
    # Migration from legacy pickle
    # ------------------------------------------------------------------
    def _maybe_migrate_pickle(self):
        pkl_path = self.index_path / "metadata.pkl"
        if not pkl_path.exists():
            return

        # Check if SQLite already has data
        with self._get_conn() as conn:
            count = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
            if count > 0:
                logger.info(f"SQLite already has {count} chunks – skipping pickle migration.")
                return

        logger.info("Migrating legacy metadata.pkl → SQLite (streaming)…")
        try:
            import pickle, hashlib
            CHUNK = 5000
            batch = []
            inserted = 0

            with open(pkl_path, "rb") as f:
                all_meta = pickle.load(f)

            for i, item in enumerate(all_meta):
                batch.append(self._dict_to_row(item))
                if len(batch) >= CHUNK:
                    self._insert_rows(batch)
                    inserted += len(batch)
                    batch = []
                    logger.info(f"  Migrated {inserted} chunks…")

            if batch:
                self._insert_rows(batch)
                inserted += len(batch)

            logger.info(f"✅ Migration complete – {inserted} chunks in SQLite.")
            pkl_path.rename(str(pkl_path) + ".migrated")

        except MemoryError:
            logger.warning(
                "metadata.pkl is too large to migrate in one shot. "
                "Run scripts/migrate_metadata_to_sqlite.py manually."
            )
        except Exception as e:
            logger.warning(f"Pickle migration skipped: {e}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    KNOWN_COLS = {"title", "source_file", "court", "judge", "date",
                  "case_number", "case_type", "category", "excerpt"}

    def _dict_to_row(self, d: dict) -> tuple:
        import hashlib
        title    = d.get("title") or "Untitled"
        source   = str(d.get("source_file") or d.get("source") or "")
        case_num = str(d.get("case_number") or "")
        doc_key  = title + "||" + source + "||" + case_num
        mock_id  = hashlib.md5(doc_key.encode()).hexdigest()[:24]

        excerpt = d.get("excerpt") or d.get("content") or ""
        return (
            mock_id,
            str(title)[:500],
            str(source)[:300],
            str(d.get("court") or "")[:200],
            str(d.get("judge") or "")[:300],
            str(d.get("date") or "")[:50],
            str(case_num)[:200],
            str(d.get("case_type") or "")[:100],
            str(d.get("category") or "")[:100],
            str(excerpt)[:500],
        )

    def _insert_rows(self, rows: list):
        with self._get_conn() as conn:
            conn.executemany("""
                INSERT INTO chunks
                (mock_id, title, source_file, court, judge, date, case_number,
                 case_type, category, excerpt)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, rows)

    def _row_to_dict(self, row) -> dict:
        return dict(row)



    # ------------------------------------------------------------------
    # metadata property – lazy full-load (kept for backward compat)
    # ------------------------------------------------------------------
    @property
    def metadata(self) -> List[Dict[str, Any]]:
        """
        Backward-compatible access to metadata as a list.
        For very large corpora this returns only the first 50k rows to
        prevent OOM – real searches go through the search() method.
        """
        if self._metadata_cache is None:
            with self._get_conn() as conn:
                rows = conn.execute(
                    "SELECT * FROM chunks ORDER BY row_id LIMIT 50000"
                ).fetchall()
            self._metadata_cache = [self._row_to_dict(r) for r in rows]
            logger.info(f"Loaded {len(self._metadata_cache)} metadata rows into cache (capped at 50k).")
        return self._metadata_cache

    @metadata.setter
    def metadata(self, value: list):
        """Allow code that does self.metadata = [] to reset the cache."""
        self._metadata_cache = value

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def add_documents(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]) -> None:
        try:
            if len(embeddings) != len(metadata):
                raise ValueError("Number of embeddings must match metadata count")

            embeddings = embeddings.astype("float32")
            self.index.add(embeddings)

            rows = [self._dict_to_row(m) for m in metadata]
            self._insert_rows(rows)

            # Invalidate cache so next access re-reads from DB
            self._metadata_cache = None

            logger.info(f"✅ Added {len(embeddings)} documents. Total: {self.index.ntotal}")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    def search(self, query_embedding: np.ndarray, k: int = 5, expand_context: bool = True) -> List[Dict[str, Any]]:
        try:
            if self.index.ntotal == 0:
                logger.warning("Vector store is empty")
                return []

            query_embedding = query_embedding.reshape(1, -1).astype("float32")
            distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))

            results = []
            row_ids = [int(idx) + 1 for idx, dist in zip(indices[0], distances[0]) if idx != -1]   # SQLite row_id is 1-based

            if not row_ids:
                return []

            # Setup context window loading without re-embedding
            fetch_ids = set(row_ids)
            if expand_context:
                for rid in row_ids:
                    fetch_ids.add(rid - 1)
                    fetch_ids.add(rid + 1)
            fetch_ids = [r for r in fetch_ids if r > 0]

            placeholders = ",".join("?" * len(fetch_ids))
            with self._get_conn() as conn:
                rows = conn.execute(
                    f"SELECT * FROM chunks WHERE row_id IN ({placeholders})",
                    list(fetch_ids)
                ).fetchall()

            # Map back to FAISS result order
            row_map = {r["row_id"]: self._row_to_dict(r) for r in rows}
            for dist, idx in zip(distances[0], indices[0]):
                if idx == -1:
                    continue
                row_id = int(idx) + 1
                if row_id in row_map:
                    result = row_map[row_id].copy()
                    
                    if expand_context:
                        source_file = result.get("source_file")
                        expanded_excerpt = result.get("excerpt", "")
                        
                        prev_chunk = row_map.get(row_id - 1)
                        if prev_chunk and prev_chunk.get("source_file") == source_file:
                            expanded_excerpt = "(Previous Context):\n" + str(prev_chunk.get("excerpt", "")) + "\n\n" + expanded_excerpt
                            
                        next_chunk = row_map.get(row_id + 1)
                        if next_chunk and next_chunk.get("source_file") == source_file:
                            expanded_excerpt = expanded_excerpt + "\n\n(Next Context):\n" + str(next_chunk.get("excerpt", ""))
                            
                        result["excerpt"] = expanded_excerpt
                        
                    result["score"] = float(dist)
                    result["similarity"] = float(1 / (1 + dist))
                    results.append(result)

            logger.info(f"Found {len(results)} similar documents (with expanded context)")
            return results
        except Exception as e:
            logger.error(f"Error searching index: {e}")
            raise

    def search_keywords(self, query: str, k: int = 5, expand_context: bool = True) -> List[Dict[str, Any]]:
        try:
            import re
            words = [w for w in re.split(r'\s+', query.strip()) if len(w) > 2 and w.lower() not in {"the", "and", "for", "with", "case", "cases", "court", "high"}]
            if not words:
                words = [query.strip()]

            where_clauses = []
            params = []
            for word in words:
                like_pattern = f"%{word}%"
                where_clauses.append("(title LIKE ? OR excerpt LIKE ? OR case_number LIKE ? OR court LIKE ?)")
                params.extend([like_pattern, like_pattern, like_pattern, like_pattern])

            where_stmt = " AND ".join(where_clauses)
            
            with self._get_conn() as conn:
                rows = conn.execute(f"SELECT MIN(row_id) as row_id, mock_id FROM chunks WHERE {where_stmt} GROUP BY mock_id LIMIT {k * 2}", params).fetchall()

            if not rows:
                return []

            row_ids = [int(r["row_id"]) for r in rows]
            
            fetch_ids = set(row_ids)
            if expand_context:
                for rid in row_ids:
                    fetch_ids.add(rid - 1)
                    fetch_ids.add(rid + 1)
            fetch_ids = [r for r in fetch_ids if r > 0]
            
            placeholders = ",".join("?" * len(fetch_ids))
            with self._get_conn() as conn:
                full_rows = conn.execute(f"SELECT * FROM chunks WHERE row_id IN ({placeholders})", list(fetch_ids)).fetchall()
                
            row_map = {int(r["row_id"]): self._row_to_dict(r) for r in full_rows}
            
            results = []
            for rid in row_ids:
                if rid in row_map:
                    result = row_map[rid].copy()
                    if expand_context:
                         source_file = result.get("source_file")
                         expanded_excerpt = result.get("excerpt", "")
                         prev_chunk = row_map.get(rid - 1)
                         if prev_chunk and prev_chunk.get("source_file") == source_file:
                             expanded_excerpt = "(Previous Context):\n" + str(prev_chunk.get("excerpt", "")) + "\n\n" + expanded_excerpt
                         next_chunk = row_map.get(rid + 1)
                         if next_chunk and next_chunk.get("source_file") == source_file:
                             expanded_excerpt = expanded_excerpt + "\n\n(Next Context):\n" + str(next_chunk.get("excerpt", ""))
                         result["excerpt"] = expanded_excerpt
                    
                    result["score"] = 1.0
                    result["similarity"] = 1.0
                    results.append(result)

            logger.info(f"Found {len(results)} exact keyword documents in SQLite chunks.")
            return results[:k]
        except Exception as e:
            logger.error(f"Error keyword searching index: {e}")
            raise

    def get_document_count(self) -> int:
        return self.index.ntotal

    def clear(self) -> None:
        self.index.reset()
        with self._get_conn() as conn:
            conn.execute("DELETE FROM chunks")
        self._metadata_cache = None
        logger.info("✅ Vector store cleared")

    def save_index(self) -> None:
        try:
            index_file = self.index_path / "faiss.index"
            faiss.write_index(self.index, str(index_file))
            logger.info(f"✅ Saved FAISS index ({self.index.ntotal} vectors) to {index_file}")
            # Note: metadata is written to SQLite incrementally in add_documents()
        except Exception as e:
            logger.error(f"Error saving index: {e}")
            raise

    def _load_index(self) -> None:
        try:
            index_file = self.index_path / "faiss.index"
            if index_file.exists():
                self.index = faiss.read_index(str(index_file))
                logger.info(f"✅ Loaded FAISS index with {self.index.ntotal} vectors")
            else:
                logger.info("No existing FAISS index found. Starting fresh.")
        except Exception as e:
            logger.warning(f"Could not load index: {e}. Starting fresh.")
            self.index = faiss.IndexFlatL2(self.dimension)

    def get_stats(self) -> Dict[str, Any]:
        with self._get_conn() as conn:
            db_count = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        return {
            "total_vectors": self.index.ntotal,
            "total_metadata_chunks": db_count,
            "dimension": self.dimension,
            "index_type": "IndexFlatL2",
            "metadata_backend": "SQLite",
        }


# Singleton instance
_vector_store = None

def get_vector_store(dimension: int = 384) -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore(dimension=dimension)
    return _vector_store
