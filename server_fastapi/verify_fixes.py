"""
Verify Fix 1: Test the new format_judgment_title() with test cases.
Verify Fix 2: Test langchain_openai import has no deprecation warnings.
"""
import sys, re, warnings
sys.path.insert(0, '.')

# ----------------------------------------------------------------
# Inline the function from rag_pipeline.py to avoid faiss imports
# ----------------------------------------------------------------
def format_judgment_title(citation: str, court: str, original_title: str = "", excerpt: str = "") -> str:
    citation = str(citation or "").strip()
    court = str(court or "").strip()
    original_title = str(original_title or "").strip()
    excerpt = str(excerpt or "").strip()

    def _clean_court(c, text):
        court_patterns = [
            r'Supreme Court of Pakistan', r'Federal Shariat Court',
            r'Lahore High Court(?:\s*,\s*Lahore)?',
            r'High Court of Sindh(?:\s*,\s*Karachi)?', r'Sindh High Court(?:\s*,\s*Karachi)?',
            r'Islamabad High Court', r'Peshawar High Court',
            r'Balochistan High Court(?:\s*,\s*Quetta)?', r'High Court of Balochistan',
            r'(?:IN THE )?(?:COURT OF |COURT\s+OF\s+)?(?:SENIOR\s+)?CIVIL\s+JUDGE[^,\n]*',
            r'(?:IN THE )?(?:DISTRICT\s+)?(?:AND\s+)?(?:SESSIONS?\s+)?(?:COURT|JUDGE)[^,\n]{0,30}',
            r'(?:Federal|Provincial)\s+(?:Service\s+)?(?:Tribunal)[^,\n]{0,30}',
            r'Income\s+Tax\s+(?:Appellate\s+)?Tribunal',
        ]
        for pat in court_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                return re.sub(r'\s+', ' ', m.group(0)).strip()
        if c.lower().startswith("the "):
            return c[4:].strip().title()
        return c

    real_court = _clean_court(court, excerpt) if excerpt else court

    # Priority 1: Statute
    for pat in [
        r'(?:THE\s+)?([A-Z][A-Z\s\(\)]{4,80}(?:ACT|ORDINANCE|CODE|RULES?|REGULATION|ORDER|DECREE|CONSTITUTION)(?:\s*\(AMENDMENT\))?,?\s*(?:NO\.\s*\w+\s+OF\s+)?\d{4})',
        r'([A-Z][a-zA-Z\s\-]{4,70}(?:Act|Ordinance|Code|Rules?|Regulation|Order|Decree),?\s*\d{4})',
    ]:
        m = re.search(pat, excerpt)
        if m:
            s = re.sub(r'\s+', ' ', m.group(1)).strip().rstrip(',')
            if len(s) > 10 and ' ' in s:
                return f"{s} — {real_court}" if real_court else s

    # Priority 2: Reporter citation
    rep_pat = r'(\d{4})\s+(PLD|SCMR|YLR|CLC|PCrLJ|MLD|PSC|PTD|PTCL|NLR|KLR|PLJ|DLD)\s+(\d+)'
    m = re.search(rep_pat, excerpt, re.IGNORECASE) or (citation and re.search(rep_pat, citation, re.IGNORECASE))
    if m:
        rc = f"{m.group(1)} {m.group(2).upper()} {m.group(3)}"
        return f"{rc} — {real_court}" if real_court else rc

    # Priority 3: Parties
    for pat in [
        r'([A-Za-z][A-Za-z\s\.\(\)\&]{2,60}?)\s*\((?:Appellant|Petitioner|Plaintiff)s?\)\s*(?:Versus|VERSUS|Vs?\.?)\s*([A-Za-z][A-Za-z\s\.\(\)\&]{2,60}?)\s*\((?:Respondent|Defendant)s?\)',
        r'([A-Za-z][A-Za-z\s\.]{2,50}?)\s+(?:Appellant|Petitioner|Plaintiff)\s+(?:Versus|VERSUS|Vs?\.?)\s+([A-Za-z][A-Za-z\s\.]{2,50}?)\s+(?:Respondent|Defendant)',
        r'([A-Za-z][A-Za-z\s\.]{2,50}?)\s+(?:VERSUS|Versus|Vs\.?)\s+([A-Za-z][A-Za-z\s\.]{2,50})(?:\s|$|\n)',
    ]:
        m = re.search(pat, excerpt, re.IGNORECASE)
        if m:
            p1 = re.sub(r'\b(the|and|through|LRs?|deceased|decd|mr|mst|etc)\b', '', re.sub(r'\s+', ' ', m.group(1)), flags=re.IGNORECASE).strip().strip('()')
            p2 = re.sub(r'\b(the|and|through|LRs?|deceased|decd|mr|mst|etc)\b', '', re.sub(r'\s+', ' ', m.group(2)), flags=re.IGNORECASE).strip().strip('()')
            if len(p1) > 2 and len(p2) > 2:
                ps = f"{p1} v. {p2}"
                cm = re.search(r'((?:W\.P|C\.P|Writ Petition|Civil Appeal|Criminal Appeal|Civil Revision|Civil Suit|Crl\.?\s*Appeal|Cr\.?\s*Revision|Special Appeal|Constitution Petition)\.?\s*(?:No\.?)?\s*[\d\-\/]+(?:\s+of\s+\d{4})?)', excerpt, re.IGNORECASE)
                if cm:
                    cs = re.sub(r'\s+', ' ', cm.group(1)).strip()
                    return f"{ps} [{cs}] — {real_court}" if real_court else f"{ps} [{cs}]"
                return f"{ps} — {real_court}" if real_court else ps

    # Priority 4: Case number alone
    for pat in [r'((?:Writ Petition|W\.P\.?|Constitution Petition|C\.P\.?|Civil Appeal|Crl\.?\s*Appeal|Criminal Appeal|Civil Suit|Civil Revision|C\.R\.?|Special Leave|S\.L\.P\.?|Criminal Misc\.?|Crl\.?\s*Misc\.?)\s*(?:No\.?)?\s*[\d\-\/]+(?:\s+(?:of|dated)\s+\d{4})?)']:
        m = re.search(pat, excerpt, re.IGNORECASE)
        if m:
            cs = re.sub(r'\s+', ' ', m.group(1)).strip()
            return f"{cs} — {real_court}" if real_court else cs

    # Priority 5: Year + court fallback
    ym = re.search(r'\b((?:19|20)\d{2})\b', excerpt)
    ys = ym.group(1) if ym else ""
    is_placeholder = (not original_title or any(x in original_title for x in ["Document from", "EasyLaw", "Untitled"]) or "administrator" in original_title.lower())
    if not is_placeholder:
        return original_title
    if real_court and ys:
        return f"Judgment — {real_court} ({ys})"
    if real_court:
        return f"Judgment — {real_court}"
    return "Untitled Judgment"


print("=" * 60)
print("FIX 1: Testing format_judgment_title()")
print("=" * 60)

tests = [
    ("Statute — Privatisation Commission Ordinance 2000",
     "", "Supreme Court of Pakistan", "Document from administrator00532129aba2e10fe (Supreme Court of Pakistan)",
     "Page 1 of 19 THE PRIVATISATION COMMISSION ORDINANCE, 2000 CONTENTS PART I.GENERAL SECTIONS:"),
    ("Statute — Federal Excise Act 2005",
     "", "the High Court", "Document from administrator06f0200ef997b5098 (the High Court)",
     "inserted by Finance Act, 2020. The Federal Excise Act, 2005 48 (i) where the appellant is a company"),
    ("Reporter citation PLD in excerpt",
     "", "Lahore High Court", "Document from xxx",
     "Reported in 1994 PLD 456 decided by Lahore High Court regarding property disputes."),
    ("Reporter citation SCMR in citation field",
     "1972 SCMR 584", "Supreme Court of Pakistan", "Document from xxx",
     "The court reviewed the matter under criminal jurisdiction."),
    ("Parties formal style (Appellant vs Respondent)",
     "", "High Court of Sindh", "Document from xxx",
     "Muhammad Ali (Appellant) Versus State of Pakistan (Respondent) Criminal Appeal No. 45/2022"),
    ("Case number — W.P. No.",
     "", "Islamabad High Court", "Document from xxx",
     "W.P. No. 1234/2023 was filed challenging the administrative order issued."),
    ("Year + court fallback",
     "", "Peshawar High Court", "Document from xxx",
     "In 2020, the matter was disposed of on merits by the Peshawar High Court."),
    ("Anti-Terrorism Act 1997",
     "", "Supreme Court of Pakistan", "Document from administrator0c000814 (Supreme Court of Pakistan)",
     "firearms as defined in the Arms Ordinance, 1965; The Anti-terrorism Act, 1997 and all Rules"),
]

all_passed = True
for desc, citation, court, original_title, excerpt in tests:
    result = format_judgment_title(citation, court, original_title, excerpt)
    is_bad = "Document from" in result or "administrator" in result.lower() or result == "Untitled Judgment"
    status = "[PASS]" if not is_bad else "[FAIL]"
    if is_bad:
        all_passed = False
    print(f"{status} [{desc}]")
    print(f"   => {result}")

print()
print("=" * 60)
print("FIX 2: Testing langchain_openai import (no deprecation)")
print("=" * 60)

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    from langchain_openai import ChatOpenAI
    langchain_depr = [w for w in caught if issubclass(w.category, (DeprecationWarning, PendingDeprecationWarning)) and "langchain" in (str(w.message) + str(w.filename)).lower() and "community" in (str(w.message) + str(w.filename)).lower()]

if langchain_depr:
    print("[FAIL] Deprecation still present:")
    for w in langchain_depr:
        print(f"   {w.message}")
else:
    print("[PASS] langchain_openai imported cleanly -- no langchain_community deprecation warnings")

print()
print(f"Fix 1 all passed: {'YES' if all_passed else 'SOME FAILED'}")
