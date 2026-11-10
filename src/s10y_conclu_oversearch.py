"""S10y · 7-Conclu.tex: hạ cấp claim 'indicating overfitting' -> 'consistent
with overfitting of the search itself', đồng bộ với §4.4 và Contribution (ii)."""
from pathlib import Path

p = Path("report/Sections/7-Conclu.tex")
s = p.read_text(encoding="utf-8")

OLD = """practice. Expanding the hyper-parameter search degraded test performance while
improving cross-validated scores, indicating overfitting of the search itself
on a small minority class."""

NEW = """practice. Expanding the hyper-parameter search degraded test performance while
improving cross-validated scores --- consistently across both model families,
and consistent with overfitting of the search itself on a small minority class,
though a single seed and a small CV gap do not establish this as a proof."""

if OLD not in s:
    raise SystemExit("anchor not found")

s = s.replace(OLD, NEW, 1)
p.write_text(s, encoding="utf-8")
print("[ok] 7-Conclu.tex over-searching claim downgraded")
