"""S10ag · 6-Discuss: ha cap 'the wider hyper-parameter search failed' ->
'did not pay off', nhat quy voi §4.4 va Contribution (ii)."""
from pathlib import Path

p = Path("report/Sections/6-Discuss.tex")
s = p.read_text(encoding="utf-8")

OLD = """This is also why the wider hyper-parameter search failed: with 331 training frauds, the search space
itself becomes a source of overfitting."""

NEW = """This is also why the wider hyper-parameter search did not pay off: with 331 training frauds, the search space
itself is a plausible source of overfitting, although --- as Section~\\ref{sec:search}
sets out --- a single seed cannot establish that as a proof."""

if OLD not in s:
    raise SystemExit("anchor not found")

s = s.replace(OLD, NEW, 1)
p.write_text(s, encoding="utf-8")
print("[ok] Discuss over-searching claim downgraded")
