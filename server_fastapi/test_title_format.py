"""
Quick test of the new format_judgment_title() function with real-world examples.
"""
import sys
sys.path.insert(0, '.')
from routes.judgments import format_judgment_title

print("="*70)
print("TEST 1: EasyLaw SCMR filename (most common pattern)")
t = format_judgment_title(
    citation="255",
    court="Supreme Court of Pakistan",
    original_title="Document from EasyLaw_1999_SCMR_255_JDM1MY98",
    excerpt="Journal 1999 SCMR 255 Court SUPREME COUR T Date 1998-11-12 Appeal No. CIVIL APPEAL NO. 1296 OF 1998, Judge SAIDUZZAMAN SIDDIQUI Parties MUAHAMMAD AHMED (APPELLANT) Vs RESPONDENT",
    source_file="EasyLaw_1999_SCMR_255_JDM1MY98YRBYCE898C.pdf"
)
print(f"  Result: {t}")
print(f"  Expected: Muhammad Ahmed v. Respondent [Civil Appeal No. 1296 OF 1998] 1999 SCMR 255 — Supreme Court of Pakistan")

print()
print("TEST 2: PLD filename - parties extracted from body")
t = format_judgment_title(
    citation="365",
    court="Supreme Court of Pakistan",
    original_title="He Has Referred In This Context To The Judgment Rendered By v. Haris Steel Industries, 2011 PLD 365",
    excerpt="commencing on 9th February, 2011 which was not permissible under section 6(b)(i) of the National Accountability Ordinance 1999",
    source_file="EasyLaw_2011_PLD_365_OX3D0UQO94C9HTOCYH.pdf"
)
print(f"  Result: {t}")
print(f"  Expected: 2011 PLD 365 — Supreme Court of Pakistan")

print()
print("TEST 3: PCrLJ filename")
t = format_judgment_title(
    citation="963",
    court="Supreme Court of Pakistan",
    original_title="Khan And v. Malik Baz Muhammad Khan And Others, 2002 PCrLJ 963",
    excerpt="Khan and vs. Malik Baz Muhammad Khan and others (PLD 1983 Quetta 30) referred to.",
    source_file="EasyLaw_2002_PCrLJ_963_2DJAEM3KE5FJ0OPJXC.pdf"
)
print(f"  Result: {t}")
print(f"  Expected: 2002 PCrLJ 963 — Supreme Court of Pakistan")

print()
print("TEST 4: Non-EasyLaw (uploaded judgment with parties in header)")
t = format_judgment_title(
    citation="",
    court="SUPREME COURT OF PAKISTAN",
    original_title="Commissioner Inland Revenue v. Ms",
    excerpt="murad Sugar Mills Limited others and (50) C.P.L.A.545-K2023 Commissioner Inland Revenue (Petitioner) Versus Arif Sugar Mills (Respondent) dated 07.2.2023",
    source_file="c.p._824_k_2023.pdf"
)
print(f"  Result: {t}")
print(f"  Expected: Commissioner Inland Revenue v. Arif Sugar Mills — Supreme Court Of Pakistan")

print()
print("TEST 5: Writ Petition format (no EasyLaw)")
t = format_judgment_title(
    citation="WP-282-B-2012",
    court="Islamabad High Court",
    original_title="Ahmad v. Federation",
    excerpt="W.P. No. 282-B/2012 Ahmad Khan (Petitioner) Versus Federation of Pakistan (Respondent)",
    source_file="WP_282_2012.pdf"
)
print(f"  Result: {t}")
print(f"  Expected: Ahmad Khan v. Federation Of Pakistan [W.P. No 282-B/2012] — Islamabad High Court")

print()
print("TEST 6: YLR PSC - should NOT pick up referenced case from body")
t = format_judgment_title(
    citation="701",
    court="",
    original_title="In State Life Insurance v. Federal Government, 1997 PSC 701",
    excerpt="In State Life Insurance Employees Federation v. Federal Government of Pakistan (1994 SCMR 1341) it was held that violation of Articles 4 and 5 of the Constitution",
    source_file="EasyLaw_1997_PSC_701_QH59FGLSWGIWXILFPW.pdf"
)
print(f"  Result: {t}")
print(f"  Expected: 1997 PSC 701 (no court available)")
