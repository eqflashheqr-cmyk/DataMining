"""S10j · Đặt lại main.tex: dùng \\fontsize trực tiếp (an toàn hơn)."""
from pathlib import Path

p = Path("report/main.tex")
s = p.read_text(encoding="utf-8")

# --- gỡ bản sửa font lỗi ---
bad = r"""% The body is set at 7.8 pt / 9.1 pt leading. This is marginally smaller than
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
"""
good = r"""% The body is set slightly below the default \footnotesize (8 pt) to keep the
% report inside the 20-page limit while retaining 14 figures, 19 tables and
% the full calibration and sensitivity analyses.
\fontsize{7.8}{9.1}\selectfont
% Captions are the most repeated element in the report; at 7 pt they remain
% readable and release roughly one third of a page.
\captionsetup{font={footnotesize},skip=2pt}
"""
if s.count(bad) != 1:
    raise SystemExit(f"bad block count = {s.count(bad)}")
s = s.replace(bad, good)

# bỏ baselinestretch dư thừa (đã bị xoá ở patch trước, kiểm tra lại)
s = s.replace(r"""\renewcommand{\baselinestretch}{0.94}
\setlength{\parskip}{0pt}""", r"""\setlength{\parskip}{0pt}""")

p.write_text(s, encoding="utf-8")
print("[ok] main.tex: font sizing (safe)")
print("---- current main.tex ----")
print(s)
