"""S10ae · Table 13 caption: bo claim 'higher recall at lower cost' coi nhu
toan cuc (global cost min 0.0905 re hon nhung vuot capacity) -- noi ro pham vi
so sanh de tranh bi phan bieng 'cherry-picking'."""
from pathlib import Path

p = Path("report/Sections/5-Cost.tex")
s = p.read_text(encoding="utf-8")

OLD = """\\caption{Single-threshold versus two-tier deployment. The two-tier policy
attains higher recall at lower cost while using well under one analyst.}"""

NEW = """\\caption{Single-threshold versus two-tier deployment. Compared with the three
single thresholds listed, the two-tier policy attains higher recall at lower
cost while using well under one analyst. The comparison is not against the
global cost minimum of the threshold curve (0.0905), which is cheaper still but
needs 301.7 reviews per day; see the discussion below.}"""

if OLD not in s:
    raise SystemExit("anchor not found")

s = s.replace(OLD, NEW, 1)
p.write_text(s, encoding="utf-8")
print("[ok] Table 13 caption scoped")
