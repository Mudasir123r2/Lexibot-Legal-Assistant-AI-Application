import sys
from utils.formatters import format_judgment_title

print("Test 1:", format_judgment_title("", "High Court", "", "arties: FEDERA TION OF P AKIST AN v. MIAN MUHAMMAD NAWAZ SHARIF \n 2009 PLD 284"))
print("Test 2:", format_judgment_title("", "Supreme Court of pakistan", "", "arties: . MUNI v. HABIB KHAN \n 1956 PLD 403"))
print("Test 3:", format_judgment_title("", "by High Court", "", "arties: MUKHT AR AHMAD v. UME KALSOOM \n 1975 PLD 805"))
