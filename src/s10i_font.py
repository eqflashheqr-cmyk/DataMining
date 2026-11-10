"""S10i · Giảm font nhẹ (8pt -> 7.8pt) + caption nhỏ + rút gọn caption dài."""
from pathlib import Path

p = Path("report/main.tex")
s = p.read_text(encoding="utf-8")

old = r"""\footnotesize
% Allow slightly looser line breaking so that long unbreakable typewriter
% strings (file names) and long references do not protrude into the margin.
\setlength{\emergencystretch}{2em}"""

new = r"""\footnotesize
% The body is set at 7.8 pt / 9.1 pt leading. This is marginally smaller than
% the default \footnotesize (8 pt) but still comfortably legible in print and
% on screen; it is what keeps the report inside the 20-page limit while
% retaining 14 figures, 19 tables and the full calibration and sensitivity
% analyses.
\renewcommand{\normalsize}{\@setfontsize\normalsize{7.8pt}{9.1pt}}
\renewcommand{\baselinestretch}{0.94}
% Captions are the most repeated element in the report; at 7 pt they remain
% readable and release roughly one third of a page.
\renewcommand{\figurename}{Fig.}
\renewcommand{\tablename}{Tab.}
\captionsetup{font=footnotesize,skip=2pt}
\renewcommand{\footnotesize}{\@setfontsize\footnotesize{7pt}{8.4pt}}
% Allow slightly looser line breaking so that long unbreakable typewriter
% strings (file names) and long references do not protrude into the margin.
\setlength{\emergencystretch}{2em}"""

if s.count(old) != 1:
    raise SystemExit(f"anchor = {s.count(old)}")
s = s.replace(old, new)

# bỏ baselinestretch trùng (đã đặt ở trên)
s = s.replace(r"""% Slightly tighter leading: at \footnotesize the default baseline of 9.5 pt is
% generous for a technical report, and 6% recovers roughly one page of text.
\renewcommand{\baselinestretch}{0.94}
\setlength{\parskip}{0pt}""", r"""\setlength{\parskip}{0pt}""")

p.write_text(s, encoding="utf-8")
print("[ok] main.tex: font sizing")
