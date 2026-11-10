"""S10 · main.tex: thêm float spacing settings + cập nhật comment."""
from pathlib import Path

p = Path("report/main.tex")
s = p.read_text(encoding="utf-8")

old = r"""\setlength{\emergencystretch}{2em}
\include{Sections/1-Title}"""

new = r"""\setlength{\emergencystretch}{2em}
% Tighten float separation: the report carries many floats (14 figures and
% 19 tables) on 20 pages, so every millimetre of vertical padding around a
% float is a millimetre of content.
\setlength{\textfloatsep}{7pt plus 2pt minus 2pt}
\setlength{\floatsep}{5pt plus 2pt minus 2pt}
\setlength{\intextsep}{6pt plus 2pt minus 2pt}
\setlength{\dblfloatsep}{6pt plus 2pt minus 2pt}
\setlength{\dbltextfloatsep}{6pt plus 2pt minus 2pt}
\setlength{\abovecaptionskip}{4pt}
\setlength{\belowcaptionskip}{0pt}
\include{Sections/1-Title}"""

if s.count(old) != 1:
    raise SystemExit(f"anchor count = {s.count(old)}")
s = s.replace(old, new)

s = s.replace(
    "% keeping all 11 figures and all result tables.",
    "% keeping all 14 figures and all result tables.",
)

p.write_text(s, encoding="utf-8")
print("[ok] main.tex")
