import re

def _auto_heal_ocr_spaces(text: str) -> str:
    """Globally heals arbitrary OCR fractures (e.g. NA WAB, ST ATE) caused by diagonal letter tracking."""
    import re

    def repl(m):
        w1, w2 = m.group(1), m.group(2)
        # If both fragments are suspiciously long, it's probably two valid words
        if len(w1) > 3 and len(w2) > 3:
            return m.group(0)
        
        w1_u, w2_u = w1.upper(), w2.upper()
        # Prevent merging known valid short English words
        if w1_u in ('AT','THAT','AND','TO','IN','IT','IS','THE','A','OF','ON','AS','AN','NO','OR','SO','BY','MY','UP','VS','V') or \
           w2_u in ('A','ALL','ARE','AND','THE','OF','AT','IT','AS','AN','AM','NO','ON','IN','IF','IS','SO','OR','UP','US','VS','V'):
            return m.group(0)
            
        return w1 + w2

    # 1. Word ending in diagonal/overhang letter + Word starting with vowel
    text = re.sub(r'\b([A-Za-z]{1,7}[WTVPYFKwtvpyfk])\s+([AaEeIiOoUu][A-Za-z]{1,7})\b', repl, text)
    
    # 2. Word ending in vowel + Word starting with diagonal/overhang letter
    text = re.sub(r'\b([A-Za-z]{1,7}[AaEeIiOoUu])\s+([WTVPYFKwtvpyfk][A-Za-z]{1,7})\b', repl, text)
    
    # 3. Single isolated initial letters merging into a vowel word (W AHEED, P ARVEEN)
    text = re.sub(r'\b([WTVPYFKwtvpyfk])\s+([AaEeIiOoUu][A-Za-z]{2,7})\b', repl, text)
    
    # 4. Stray single consonant at end of word (FAMIL Y -> FAMILY)
    text = re.sub(r'\b([A-Za-z]{3,})\s+([B-DF-HJ-NP-TV-Z])\b', repl, text)
    
    # 5. Stray single consonant at start of word (T ARIQ -> TARIQ) 
    text = re.sub(r'\b([B-DF-HJ-NP-TV-Z])\s+([A-Za-z]{3,})\b', repl, text)

    # 6. Manual target for S TATE (S and T don't fit above vowel rules perfectly)
    text = re.sub(r'\b([Ss])\s+(TATE|tate)\b', r'\1\2', text)
    
    # 7. Aggressive domain-specific overrides - ignoring weird boundaries and numbers
    text = re.sub(r'(?i)moht\s*arma', 'MOHTARMA', text)
    text = re.sub(r'(?i)df?edera\s*tion', 'FEDERATION', text)
    text = re.sub(r'(?i)pakist\s*an', 'PAKISTAN', text)
    text = re.sub(r'(?i)secret\s*ary', 'SECRETARY', text)
    text = re.sub(r'(?i)bhutt\s*o', 'BHUTTO', text)
    text = re.sub(r'(?i)res\s*pondent', 'RESPONDENT', text)
    text = re.sub(r'(?i)dep\s*artment', 'DEPARTMENT', text)
    text = re.sub(r'(?i)sharia\s*t', 'SHARIAT', text)
    text = re.sub(r'(?i)f\s*asih', 'FASIH', text)
    
    # Finally, fix VEDANT and COMMISSIONER manual bugs as seen globally
    text = text.replace('VDANT', 'VEDANT')
    text = text.replace('OMMISSIONER', 'COMMISSIONER')
    
    return text

COURT_CANONICAL = {
    r'supreme\s+court': 'Supreme Court of Pakistan',
    r'federal\s+shariat': 'Federal Shariat Court',
    r'lahore\s+high': 'Lahore High Court',
    r'high\s+court\s+of\s+sindh|sindh\s+high': 'High Court of Sindh',
    r'islamabad\s+high': 'Islamabad High Court',
    r'peshawar\s+high': 'Peshawar High Court',
    r'balochistan\s+high|high\s+court\s+of\s+balochistan': 'Balochistan High Court',
    r'west\s+pakistan': 'High Court of West Pakistan',
    r'east\s+pakistan': 'High Court of East Pakistan',
    r'shariat\s+court\s+of\s+azad\s+jammu\s+and\s+kashmir|shariat\s+court.*?aj&k': 'Shariat Court of Azad Jammu and Kashmir',
    r'aj&k|azad\s+jammu\s+and\s+kashmir': 'Azad Jammu and Kashmir Supreme Court',
}

def canonical_court(text: str) -> str:
    """Return the canonical court name from any text mentioning a court."""
    import re
    # Fix extreme OCR spacing
    text = re.sub(r'(?<![a-zA-Z])(?:[a-zA-Z]\s+){3,}[a-zA-Z](?![a-zA-Z])', lambda m: m.group(0).replace(' ', ''), text)
    
    t = text.strip()
    for pat, name in COURT_CANONICAL.items():
        if re.search(pat, t, re.IGNORECASE):
            return name
    # Remove leading "THE " and title-case
    t = re.sub(r'(?i)^the\s+', '', t).strip()
    
    t = t.replace('Appella Te', 'Appellate')
    t = t.replace('P Akist An', 'Pakistan')
    t = t.replace('Tribunal Appella Te', 'Tribunal Appellate')
    
    return re.sub(r'\s+', ' ', t).title() if t else ""

def extract_court(db_court: str, header_text: str) -> str:
    """Intelligently extract and format the court from DB meta or OCR header."""
    db_court = str(db_court or "").strip()
    header_text = str(header_text or "")[:800]
    
    # 1. Prefer OCR extraction if it's explicitly stated in an Easy Law header block!
    court_hdr = re.search(r'\bCourt\s*\:\s*([A-Z][a-zA-Z0-9\s]+?)(?=\s+(?:Date|Appeal|Judge|Journal|Parties)\b|$)', header_text, re.IGNORECASE)
    if not court_hdr:
        court_hdr = re.search(r'\bCourt\b\s+([A-Z][A-Z\s]+?)(?=\s+(?:Date|Appeal|Judge|Journal|Parties)\b|$)', header_text, re.IGNORECASE)
    
    if court_hdr and len(court_hdr.group(1).strip()) > 3:
        # Check against canon
        c_court = canonical_court(court_hdr.group(1))
        if c_court: return c_court

    # 2. Prefer database metadata field if it exists and is valid
    if db_court and len(db_court) > 3:
        return canonical_court(db_court)
        
    return ""

def extract_full_metadata(header_text: str) -> dict:
    """Extract full metadata block from EasyLaw headers for the UI."""
    header_text = str(header_text or "")[:1500]
    meta = {
        "journal": "",
        "court": "",
        "date": "",
        "appeal_no": "",
        "judge": "",
        "parties": "",
        "lawyers": "",
        "statutes": ""
    }
    
    # Simple regex grabs for the structured blocks EasyLaw puts at the top
    journal_match = re.search(r'Journal[\:\s]+([^C]*?)(?=\s+Court\b)', header_text, re.IGNORECASE)
    if journal_match: meta["journal"] = journal_match.group(1).strip()
    
    court_match = re.search(r'Court[\:\s]+(.*?)(?=\s+Date\b)', header_text, re.IGNORECASE)
    if court_match: meta["court"] = canonical_court(court_match.group(1).strip())
    
    date_match = re.search(r'Date[\:\s]+([\w\s\-]+?)(?=\s+Appeal\b)', header_text, re.IGNORECASE)
    if date_match: meta["date"] = date_match.group(1).strip()
    
    appeal_match = re.search(r'Appeal(?:\s+No\.?)?[\:\s]+(.*?)(?=\s+Judge\b)', header_text, re.IGNORECASE)
    if appeal_match: meta["appeal_no"] = appeal_match.group(1).strip()
    
    judge_match = re.search(r'Judge[\:\s]+(.*?)(?=\s+Parties\b)', header_text, re.IGNORECASE)
    if judge_match: meta["judge"] = judge_match.group(1).strip()
    
    parties_match = re.search(r'(?:Parties|arties)[\:\s]+(.*?)(?=\s+(?:Lawyers\b|$|\n))', header_text, re.IGNORECASE)
    if parties_match: meta["parties"] = parties_match.group(1).strip()
    
    lawyers_match = re.search(r'Lawyers[\:\s]+(.*?)(?=\s+(?:Statut?es\b|$|\n))', header_text, re.IGNORECASE)
    if lawyers_match: meta["lawyers"] = _auto_heal_ocr_spaces(lawyers_match.group(1).strip())
    
    statues_match = re.search(r'Statut?es[\:\s]+(.*?)(?=\s+(?:Judgment\b|$|\n))', header_text, re.IGNORECASE)
    if statues_match: meta["statutes"] = statues_match.group(1).strip()
    
    return meta

def format_judgment_title(citation: str, court: str, original_title: str = "", excerpt: str = "", source_file: str = "") -> str:
    """
    Generate a professional Pakistani legal citation title.

    Pakistani Standard Format:
      [Parties] v. [Parties] — [Case Type/No.] — [Reporter Citation] ([Court])
    
    Minimum Format (no parties found):
      [Reporter Citation] — [Court]

    Priority order:
    1. Parse EasyLaw filename → YEAR REPORTER PAGE (most reliable, direct metadata)
    2. Parse structured OCR header block in first 600 chars (Journal/Court/Appeal No./Parties)
    3. Pakistani reporter citation regex in first 600 chars of excerpt
    4. Parties in first 600 chars + case type/no
    5. Case type/number alone from first 600 chars
    6. Year + court fallback, or original title if clean
    """
    citation    = str(citation    or "").strip()
    court       = str(court       or "").strip()
    original_title = str(original_title or "").strip()
    excerpt     = str(excerpt     or "").strip()
    source_file = str(source_file or "").strip()

    # ── Helpers ───────────────────────────────────────────────────────────────
    REPORTER_PAT = r'(?P<year>\d{4})\s+(?P<rep>PLD|SCMR|YLR|CLC|PCrLJ|MLD|PSC|PTD|PTCL|NLR|KLR|PLJ|DLD|SBLR|CLD|MLD|PLC|PLR)\s+(?P<page>\d+)'

    CASE_TYPE_PAT = (
        r'(?:Writ\s+Petition|W\.P\.?|Constitution\s+Petition|C\.P\.?|'
        r'C\.P\.L\.A\.?|'
        r'Civil\s+(?:Appeal|Revision|Suit)|Criminal\s+Appeal|Crl\.?\s*Appeal|'
        r'Civil\s+Appeal|C\.A\.?|'
        r'Criminal\s+Misc\.?(?:\s+Application)?|'
        r'Special\s+Leave\s+(?:to\s+Appeal)?|S\.L\.P\.?|'
        r'Civil\s+Misc\.?(?:\s+Application)?)\s*(?:No\.?)?\s*[\d\-\/]+(?:\s+of\s+\d{4})?'
    )

    def _clean_party(name: str) -> str:
        """Strip noise words and role labels from a party name."""
        import re
        
        # Repair extreme OCR spacing (S U P R E M E -> SUPREME)
        name = re.sub(r'(?<![a-zA-Z])(?:[a-zA-Z]\s+){3,}[a-zA-Z](?![a-zA-Z])', lambda m: m.group(0).replace(' ', ''), name)
        
        # Smart Heuristic to fix broken OCR words (NA WAB, ANW AR, ST ATE) globally
        name = _auto_heal_ocr_spaces(name)
        
        # Remove any leading garbage prefixes (like "arties:" or ". ")
        name = re.sub(r'^(?:[Pp]arty|[Pp]arties|[Aa]rties|PARTIES)[\s:]*', '', name).strip()
        name = re.sub(r'^[\.\-\,\s]+', '', name)
        
        # Remove anything before and including a stray closing parenthesis if it exists at the start
        name = re.sub(r'^[^()]*\)\s*', '', name)
        
        # Remove colon/dot labeled roles: "RESPONDENT :DEP ARTMENT", "ASSESSEE.APPELLANT :"
        name = re.sub(r'(?i)\b(?:RESPONDENTS?|APPELLANTS?|PETITIONERS?|PLAINTIFFS?|DEFENDANTS?|ASSESSEES?)[\s\:\.]+', '', name)
        name = re.sub(r'(?i)[\s\:\.]+(?:RESPONDENTS?|APPELLANTS?|PETITIONERS?|PLAINTIFFS?|DEFENDANTS?|ASSESSEES?)\b', '', name)
        
        # Remove parenthetical role labels and OCR junk like (In CA 2148) or (In Both Cases)
        name = re.sub(r'\s*\((?:Appellant|Petitioner|Plaintiff|Respondent|Defendant|APPELLANT|PETITIONER|PLAINTIFF|RESPONDENT|DEFENDANT|Applicant|APPLICANT)s?\)', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*\([iI]n\s+(?:Both\s+)?(?:C[A-Z0-9\.\s]+|\bCases?|\bC\.\s*A\.\s*).*?\)', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*\([iI]n\s+CA[\s\.,].*?\)', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*\([iI]n\s+CAS[\s\.,].*?\)', '', name, flags=re.IGNORECASE)
        # Strip any alias phrase completely
        name = re.sub(r'\b(?:alias|aka)\b.*', '', name, flags=re.IGNORECASE)
        # Strip '& [x] others' or 'and [x] others'
        name = re.sub(r'\b(?:and|&)\s+\d+\s+others?\b', '', name, flags=re.IGNORECASE)
        
        # Replace 1 -> I in capital words (like D1N, ANSAR1, AS1H)
        name = re.sub(r'([A-Za-z])1([A-Za-z])', r'\1I\2', name)
        name = re.sub(r'([A-Za-z])1\b', r'\1I', name)
        name = re.sub(r'\b1([A-Za-z])', r'I\1', name)
        name = name.replace('DEP ARTMENT', 'DEPARTMENT')
        name = name.replace('F ASIH', 'FASIH')
        
        # Remove directly attached roles at the end of names like ANWARPETITIONER -> ANWAR
        name = re.sub(r'(?i)(.*?)(PETITIONER|RESPONDENT|APPELLANT|PLAINTIFF|DEFENDANT|APPLICANT)S?', r'\1', name)
        
        noise = r'\b(the|and|through|LRs?|deceased|decd|mr|mrs|mst|etc|others?|another|alias|parties|party|\d+)\b'
        name  = re.sub(noise, '', name, flags=re.IGNORECASE)
        name  = re.sub(r'\s+', ' ', name).strip().strip('(),. ')
        return name[:60]

    def _finalize_title(t: str) -> str:
        """Final sweep to catch broken strings like 'v. ERSUS' before rendering."""
        t = re.sub(r'^(?i).*?(?:bench|nch|\bcourt)\s*,\s*(?:[a-zA-Z\s\.]+\s+)?in\s+', '', t).strip()
        t = re.sub(r'^(?i).*?(?:bench|nch)\s*,\s*', '', t).strip()
        
        t = _auto_heal_ocr_spaces(t)
        
        # Hard fallback regex replacements ignoring word boundaries to catch attached garbage like "BHUTT O2" or "DFEDERA TION"
        t = re.sub(r'(?i)moht\s*arma', 'MOHTARMA', t)
        t = re.sub(r'(?i)df?edera\s*tion', 'FEDERATION', t)
        t = re.sub(r'(?i)secret\s*ary', 'SECRETARY', t)
        t = re.sub(r'(?i)pakist\s*an', 'PAKISTAN', t)
        t = re.sub(r'(?i)bhutt\s*o', 'BHUTTO', t)
        t = re.sub(r'(?i)res\s*pondent', 'RESPONDENT', t)
        t = re.sub(r'(?i)dep\s*artment', 'DEPARTMENT', t)
        t = re.sub(r'(?i)sharia\s*t', 'SHARIAT', t)
        t = re.sub(r'(?i)f\s*asih', 'FASIH', t)
        
        t = re.sub(r'v\.\s*[Ee][rR][sS][uU][sS]', 'v.', t)
        t = re.sub(r'\bVERSUS\b', 'v.', t, flags=re.IGNORECASE)
        t = t.replace('KAUSARPARVEEN . STATE', 'KAUSAR PARVEEN')
        t = t.replace('KAUSARPARVEEN', 'KAUSAR PARVEEN')
        t = t.replace('VDANT', 'VEDANT')
        t = t.replace('OMMISSIONER', 'COMMISSIONER')
        t = t.replace('P AK', 'PAK')
        t = t.replace('Shairia T', 'Shariat')
        t = t.replace('Shairiat', 'Shariat')
        t = t.replace('()', '')
        t = re.sub(r' +', ' ', t).strip()
        return t

    # ── PRIORITY 1: EasyLaw filename ─────────────────────────────────────────
    # Filenames like EasyLaw_1999_SCMR_255_RANDOMID.pdf
    fn_match = re.search(r'EasyLaw_(\d{4})_([A-Z0-9]+)_(\d+)', source_file, re.IGNORECASE)
    file_reporter_str = ""
    if fn_match:
        fy   = fn_match.group(1)
        frep = fn_match.group(2).upper().replace('_', ' ')
        fpg  = fn_match.group(3)
        file_reporter_str = f"{fy} {frep} {fpg}"

    # Also try existing citation field
    if not file_reporter_str:
        cit_match = re.search(REPORTER_PAT, citation, re.IGNORECASE)
        if cit_match:
            file_reporter_str = f"{cit_match.group('year')} {cit_match.group('rep').upper()} {cit_match.group('page')}"

    # ── PRIORITY 2: Structured OCR header block ───────────────────────────────
    # Many OCR'd EasyLaw docs start with:
    # "Journal 1999 SCMR 255 Court SUPREME COURT Date 1998-11-12 Appeal No. CIVIL APPEAL NO. 1296 OF 1998 Judge ... Parties MUAHAMMAD AHMED (APP...) Vs RESPONDENT..."
    header_text = excerpt[:800]

    ocr_court     = ""
    ocr_appeal_no = ""
    ocr_parties   = ""

    # Court from header block or database metadata via exposed wrapper
    ocr_court = extract_court(court, header_text)

    # Appeal / Case number from OCR header block
    appeal_hdr = re.search(
        r'(?:Appeal\s+No\.?|Case\s+No\.?)\s*([A-Z][A-Z0-9\.\s\-\/]+?(?:OF|of)\s+\d{4})',
        header_text, re.IGNORECASE
    )
    if appeal_hdr:
        ocr_appeal_no = re.sub(r'\s+', ' ', appeal_hdr.group(1)).strip()

    # Parties from OCR header block (labelled "Parties ... Vs ...")
    parties_hdr = re.search(
        r'(?:Parties|arties)\s*(?:[\:\.]\s*)?(.{5,100}?)\s+(?:VERSUS|VESUS|v\.\s*[Ee]rsus|v\.?\s*versus|versus|Vs?\.?|V\.)\s*(.{5,100}?)(?:\s*(?:APPELLAN|PETITION|PLAINTIFF|RESPOND|DEFENDANT|$|\n|Lawyers|Statutes?))',
        header_text, re.IGNORECASE
    )
    if parties_hdr:
        p1 = _clean_party(parties_hdr.group(1))
        p2 = _clean_party(parties_hdr.group(2))
        if len(p1) > 2 and len(p2) > 2:
            ocr_parties = f"{p1} v. {p2}"

    # ── PRIORITY 3: Reporter citation in first 600 chars of excerpt ───────────
    excerpt_head = excerpt[:600]
    rep_match = re.search(REPORTER_PAT, excerpt_head, re.IGNORECASE)
    excerpt_reporter = ""
    if rep_match:
        excerpt_reporter = f"{rep_match.group('year')} {rep_match.group('rep').upper()} {rep_match.group('page')}"

    # Best reporter citation (filename wins over excerpt)
    best_reporter = file_reporter_str or excerpt_reporter or ""
    # Best court
    best_court = ocr_court or ""

    # ── PRIORITY 4: Parties regex (HEADER AREA ONLY) ─────────────────────────
    parties_str = ocr_parties  # already extracted from OCR header above

    if not parties_str:
        # Formal labelled pattern: "Name (Appellant) Versus Name (Respondent)"
        for pat in [
            r'((?:(?!(?:Judge|Court|Date|Parties)).){2,60}?)(?:\s+|\s*\()(?:Appellant|Petitioner|Plaintiff|Respondent|Defendant)(?:\s*\(s\)|s)?\)?\s*(?:Versus|VERSUS|VESUS|Vs?\.?|v\.?)\s*([A-Za-z][\w\s\.\(\)&]{2,60}?)(?:\s+|\s*\()(?:Appellant|Petitioner|Plaintiff|Respondent|Defendant)(?:\s*\(s\)|s)?\)?',
        ]:
            m = re.search(pat, excerpt_head, re.IGNORECASE)
            if m:
                p1 = _clean_party(m.group(1))
                p2 = _clean_party(m.group(2))
                if p1 and p2:
                    parties_str = f"{p1} v. {p2}"
                    break

    # ── PRIORITY 5: Statute / Act (for non-judgment docs) ────────────────────
    statute_pats = [
        r'(?:THE\s+)?([A-Z][A-Z\s\(\)]{4,80}?(?:ACT|ORDINANCE|CODE|RULES?|REGULATION|ORDER|DECREE|CONSTITUTION)(?:\s*\(AMENDMENT\))?,?\s*(?:NO\.\s*\w+\s+OF\s+)?\d{4})',
        r'([A-Z][a-zA-Z\s\-]{4,70}(?:Act|Ordinance|Code|Rules?|Regulation|Order|Decree|Constitution),?\s*\d{4})',
    ]
    for sp in statute_pats:
        sm = re.search(sp, excerpt_head)
        if sm:
            s = re.sub(r'\s+', ' ', sm.group(1)).strip().rstrip(',')
            if len(s) > 10 and ' ' in s and not best_reporter:
                return f"{s} — {best_court}" if best_court else s

    # ── Case type / number annotation ────────────────────────────────────────
    case_type_str = ""
    ct_match = re.search(CASE_TYPE_PAT, excerpt_head, re.IGNORECASE)
    if ct_match:
        case_type_str = re.sub(r'\s+', ' ', ct_match.group(0)).strip()

    is_placeholder = (
        not original_title
        or any(x in original_title for x in ["Document from", "EasyLaw", "Untitled", "administrator"])
        or bool(re.search(r'^(He Has|In The Case|This Court|The Petitioner|In State|Commissioner)', original_title))
    )

    # ── Assemble final title ─────────────────────────────────────────────────
    if best_reporter or best_court:        # Clean specific trailing strings like "By High Court"
        best_court = best_court.replace('By High Court', 'High Court')
        best_court = best_court.replace('by High Court', 'High Court')
        best_court = best_court.replace('of pakistan', 'of Pakistan')
        # Build citation string
        citation_str = f"{best_reporter} — {best_court}" if (best_reporter and best_court) else (best_reporter or best_court)
        
        if parties_str and case_type_str:
            return _finalize_title(f"{parties_str} [{case_type_str}] — {citation_str}")
        elif parties_str:
            return _finalize_title(f"{parties_str} — {citation_str}")
        elif not is_placeholder:
            # If we couldn't extract OCR parties but original title has substance, use it
            return _finalize_title(original_title)
        else:
            return _finalize_title(citation_str)

    # ── Fallback: use original_title if it's not a placeholder ───────────────
    if not is_placeholder:
        return _finalize_title(original_title)

    # ── Last resort: year + court ─────────────────────────────────────────────
    ym = re.search(r'\b((?:19|20)\d{2})\b', excerpt_head)
    year_str = ym.group(1) if ym else ""
    if best_court and year_str:
        return _finalize_title(f"Judgment — {best_court} ({year_str})")
    return _finalize_title(f"Judgment — {best_court}" if best_court else "Untitled Judgment")
