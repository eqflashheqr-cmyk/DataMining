"""S10z · main.tex: dong bo comment so voi so lieu that (12 hinh, 18 bang)."""
from pathlib import Path

p = Path("report/main.tex")
s = p.read_text(encoding="utf-8")

REPL = [
    ("% Body text is set at \\footnotesize (8 pt) to meet the 20-page limit while\n"
     "% keeping all 14 figures and all result tables.\n",
     "% Body text is set at \\footnotesize (8 pt) to meet the 20-page limit while\n"
     "% keeping all 12 figures and all 18 result tables.\n"),
    ("% The body is set slightly below the default \\footnotesize (8 pt) to keep the\n"
     "% report inside the 20-page limit while retaining 14 figures, 19 tables and\n"
     "% the full calibration and sensitivity analyses.\n",
     "% The body is set slightly below the default \\footnotesize (8 pt) to keep the\n"
     "% report inside the 20-page limit while retaining 12 figures, 18 tables and\n"
     "% the full calibration and sensitivity analyses.\n"),
    ("% Tighten float separation: the report carries many floats (14 figures and\n"
     "% 19 tables) on 20 pages, so every millimetre of vertical padding around a\n"
     "% float is a millimetre of content.\n",
     "% Tighten float separation: the report carries many floats (12 figures and\n"
     "% 18 tables) on 20 pages, so every millimetre of vertical padding around a\n"
     "% float is a millimetre of content.\n"),
]

for old, new in REPL:
    if old not in s:
        print("[skip]", old[:50].replace("\n", " "))
        continue
    s = s.replace(old, new, 1)
    print("[ok]", new[:45].replace("\n", " "))

p.write_text(s, encoding="utf-8")
