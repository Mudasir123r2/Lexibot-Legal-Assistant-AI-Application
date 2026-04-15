from utils.formatters import format_judgment_title

content = """SUPREME COURT OF PAKISTAN (Appellate Jurisdiction) Present: Justice Yahya Afridi, CJ Justice Muhammad Shafi Siddiqui Justice Shakeel Ahmad C.P.L.A. 181 of 2023 (Against the judgment dated 31.10.20 22 passed by the Peshawar High Court, Mingora Bench in Civil Revision No. 371-M of 20 20) Aziz Ahmad and others Petitioner (s) Versus Mst. Musarat Respondent(s) For the Petitioner (s) : Mr. Asghar Ali, ASC Syed Rifaqat Hussain Shah, AOR For R espondent (s) : N.R Date of Hearing : 09.04.2025 JUDGMENT"""

print(format_judgment_title("", "Supreme Court of Pakistan", "Original", content, ""))
