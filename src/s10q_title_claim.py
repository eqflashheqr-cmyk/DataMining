"""S10q · Đồng bộ claim 'Pareto improvement' trong Abstract (1-Title.tex)."""
from pathlib import Path

p = Path("report/Sections/1-Title.tex")
s = p.read_text(encoding="utf-8")

OLD = """day --- a Pareto improvement over the best single threshold, which needs 232
reviews per day for the same recall."""

NEW = """day --- an operational gain over the cheapest single threshold, which needs
232 reviews per day for a comparable recall."""

if OLD not in s:
    raise SystemExit("anchor not found")

s = s.replace(OLD, NEW, 1)
p.write_text(s, encoding="utf-8")
print("[ok] 1-Title.tex abstract synced")
