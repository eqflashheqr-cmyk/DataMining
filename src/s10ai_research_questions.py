"""S10ai · §1.2: them 'Research Questions' tuong minh -- dong lop hole
§3.13 (khong co framing research question / threat-to-validity). 4 RQ ngan
gon, moi RQ deu tra loi duoc o report."""
from pathlib import Path

p = Path("report/Sections/2-Intro.tex")
s = p.read_text(encoding="utf-8")

ANCHOR = """\\subsection{Problem Definition}"""

RQ = """\\subsection{Research Questions}

The project is organised around four questions, each of which is answered
by a specific part of this report:

\\begin{enumerate}
    \\item \\textbf{RQ1 (Detection).} Which model family and imbalance-handling
    technique maximise fraud detection on this dataset under a leakage-controlled
    evaluation protocol? (Sections 3--4.)
    \\item \\textbf{RQ2 (Cost).} At a precision floor of 95\\%, what does each
    operating point cost in monetary terms, and how does the ranking of
    techniques change once a business cost is attached to a false alarm?
    (Section 5.)
    \\item \\textbf{RQ3 (Capacity).} What is the maximum fraud that can be
    caught if the bank can review only 100 flagged transactions per day, and
    what decision architecture satisfies that constraint? (Section 5.)
    \\item \\textbf{RQ4 (Validity).} How much of the measured performance
    survives the threats to validity that this design admits --- threshold
    leakage, model selection on the test set, a two-day sample and a single
    random seed? (Sections 4.5 and 6.2.)
\\end{enumerate}

"""

if ANCHOR not in s:
    raise SystemExit("anchor not found")

s = s.replace(ANCHOR, RQ + ANCHOR, 1)
p.write_text(s, encoding="utf-8")
print("[ok] Research Questions subsection added")
