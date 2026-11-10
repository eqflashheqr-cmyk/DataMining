"""S10ah · §5.3: scope claim 'higher recall than the best single threshold'
-> 'than any single threshold that respects the capacity constraint' (dong bo
voi §6.3, Abstract, Conclusion)."""
from pathlib import Path

p = Path("report/Sections/5-Cost.tex")
s = p.read_text(encoding="utf-8")

OLD = """the two-tier policy of Section~\\ref{sec:twotier} resolves
the dilemma: it attains \\emph{higher} recall than the best single threshold
while requiring only 70 reviews per day, which is inside the capacity of a
single analyst."""

NEW = """the two-tier policy of Section~\\ref{sec:twotier} resolves
the dilemma: it attains \\emph{higher} recall than any single threshold that
respects the capacity constraint, while requiring only 70 reviews per day,
which is inside the capacity of a single analyst."""

if OLD not in s:
    raise SystemExit("anchor not found")

s = s.replace(OLD, NEW, 1)
p.write_text(s, encoding="utf-8")
print("[ok] §5.3 recall claim scoped")
