"""S10h · Sửa float placement: tránh trang gần như trống chỉ vì một figure bị đẩy."""
from pathlib import Path

p = Path("report/main.tex")
s = p.read_text(encoding="utf-8")

old = r"""\setlength{\abovecaptionskip}{4pt}
\setlength{\belowcaptionskip}{0pt}"""

new = r"""\setlength{\abovecaptionskip}{4pt}
\setlength{\belowcaptionskip}{0pt}
% Float placement: allow a float to occupy up to 88% of a page so that a large
% figure is not pushed onto a page of its own, and require only a small
% minimum of text on a float page. Without these the calibration and
% feature-engineering figures each stranded most of a blank page.
\renewcommand{\topfraction}{0.88}
\renewcommand{\bottomfraction}{0.75}
\renewcommand{\textfraction}{0.06}
\renewcommand{\floatpagefraction}{0.80}
\setcounter{topnumber}{3}
\setcounter{bottomnumber}{2}
\setcounter{totalnumber}{5}"""

if s.count(old) != 1:
    raise SystemExit(f"anchor = {s.count(old)}")
s = s.replace(old, new)
p.write_text(s, encoding="utf-8")
print("[ok] main.tex: float placement parameters")
