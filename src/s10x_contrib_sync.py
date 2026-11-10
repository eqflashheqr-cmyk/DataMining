"""S10x · §2 Contribution (iv) và (ii): đồng bộ với các claim đã hạ cấp
- (iv) 'higher recall at lower cost than any single threshold' -> nói đúng là
  'higher recall than any single threshold that respects the capacity
  constraint, at 70 reviews/day'.
- (ii) 'a demonstration that a wider hyper-parameter search degrades test
  performance' -> hạ cấp thành 'an observation ... consistent with' (như §4.4)."""
from pathlib import Path

p = Path("report/Sections/2-Intro.tex")
s = p.read_text(encoding="utf-8")

OLD = """demonstration that a wider hyper-parameter search \\emph{degrades} test
performance when only 331 fraud examples are available; (iii) a quantified
assessment of the cost of each imbalance technique; and (iv) a two-tier
operating policy that attains higher recall at lower cost than any single
threshold while requiring only 70 analyst reviews per day, which satisfies the
100-per-day review capacity stated in the brief."""

NEW = """observation that a wider hyper-parameter search \\emph{degrades} test
performance when only 331 fraud examples are available --- an observation we
report with its statistical caveat rather than as a proof; (iii) a quantified
assessment of the cost of each imbalance technique, including the mean-versus-best
distinction that the technique ranking depends on; and (iv) a two-tier operating
policy that attains higher recall than any single threshold that respects the
100-per-day review capacity stated in the brief, while requiring only 70 analyst
reviews per day."""

if OLD not in s:
    raise SystemExit("anchor not found")

s = s.replace(OLD, NEW, 1)
p.write_text(s, encoding="utf-8")
print("[ok] 2-Intro.tex contribution synced")
