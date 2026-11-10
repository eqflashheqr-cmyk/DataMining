"""S10aa · Table 4: them dong Isolation Forest (AP 0.1763, AUC-ROC 0.9407,
F1@0.5 0.2877) -- §4.3 dua ra ket luan tu IF nhung IF khong co trong bang
duoc trich dan (loi §1.10). Cac cot bi rang buoc P95 ghi '---' vi IF khong dat
duoc nguong do."""
from pathlib import Path

p = Path("report/Sections/4-Results.tex")
s = p.read_text(encoding="utf-8")

OLD = """Logistic Regression & none & --- & 0.7092 & 0.9627 & 0.2561 & 0.1479 & 0.9545 & \\$659.75 \\\\
\\midrule"""

NEW = """Logistic Regression & none & --- & 0.7092 & 0.9627 & 0.2561 & 0.1479 & 0.9545 & \\$659.75 \\\\
\\midrule
Isolation Forest & none & --- & 0.1763 & 0.9407 & 0.2877 & --- & --- & --- \\\\
\\bottomrule"""

if OLD not in s:
    raise SystemExit("anchor not found")

s = s.replace(OLD, NEW, 1)

# them ghi chu: IF khong dat nguong P95
OLD2 = """Regression, Decision Tree and Random Forest only.
\\end{table}"""

NEW2 = """Regression, Decision Tree and Random Forest only. Isolation Forest was run
without resampling only, and it does not reach the 95\\% precision constraint at
any usable threshold, so its constrained columns are left empty; its F1 is
measured at the default 0.5 threshold, where it flags 3{,}521 transactions.
\\end{table}"""

if OLD2 not in s:
    raise SystemExit("anchor2 not found")

s = s.replace(OLD2, NEW2, 1)
p.write_text(s, encoding="utf-8")
print("[ok] Table 4 gains Isolation Forest row")
