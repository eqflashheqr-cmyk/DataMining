"""S10ad · Abstract: ha cap claim 'show that a wider hyper-parameter search
overfits the CV folds' -> 'report an observation consistent with overfitting',
dong bo voi §4.4 va Contribution (ii)."""
from pathlib import Path

p = Path("report/Sections/1-Title.tex")
s = p.read_text(encoding="utf-8")

OLD = """on the test set, show that a wider hyper-parameter search overfits
the cross-validation folds, and demonstrate that permutation importance and
SHAP both rank \\texttt{Amount} first where the default impurity importance
ranks it 21st of 35."""

NEW = """on the test set, report an observation consistent with a wider hyper-parameter
search overfitting the cross-validation folds, and demonstrate that permutation
importance and SHAP both rank \\texttt{Amount} first where the default impurity
importance ranks it 21st of 35."""

if OLD not in s:
    raise SystemExit("anchor not found")

s = s.replace(OLD, NEW, 1)
p.write_text(s, encoding="utf-8")
print("[ok] Abstract over-searching claim downgraded")
