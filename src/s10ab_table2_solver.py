"""S10ab · Table 2: Logistic Regression thuc te dung solver mac dinh cua
sklearn (lbfgs), khong phai 'saga' -- sua loi mo ta sai hanh vi code (§2.9)."""
from pathlib import Path

p = Path("report/Sections/3-Method.tex")
s = p.read_text(encoding="utf-8")

OLD = """Logistic Regression & $C \\in \\{0.01, 0.1, 1.0\\}$, L2 penalty, \\texttt{saga} solver \\\\"""
NEW = """Logistic Regression & $C \\in \\{0.01, 0.1, 1.0\\}$, L2 penalty, \\texttt{lbfgs} solver (sklearn default) \\\\"""

if OLD not in s:
    raise SystemExit("anchor not found")

s = s.replace(OLD, NEW, 1)
p.write_text(s, encoding="utf-8")
print("[ok] Table 2 LR solver corrected to lbfgs")
