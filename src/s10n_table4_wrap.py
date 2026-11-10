"""S10n · Table 4: đưa các dòng chú thích ra khỏi tabular (đặt dưới tabular,
trong chính table float) để không còn overfull hbox do \\multicolumn quá rộng."""
from pathlib import Path

p = Path("report/Sections/4-Results.tex")
s = p.read_text(encoding="utf-8")

OLD = """\\multicolumn{8}{@{}p{0.995\\textwidth}@{}}{\\footnotesize\\textit{Recall} and \\textit{Precision} are measured at the threshold satisfying the 95\\% precision constraint; \\textit{F1} is measured at that same threshold, and \\textit{Cost} is the total business cost on the test set there.}\\\\
\\multicolumn{8}{@{}p{0.995\\textwidth}@{}}{\\footnotesize XGBoost does not accept a \\texttt{class\\_weight} argument, so its \\texttt{class\\_weight} run is identical to its no-resampling run and is omitted here; \\emph{class weighting} was therefore evaluated on Logistic Regression, Decision Tree and Random Forest only.}\\\\
\\bottomrule
\\end{tabular}
\\end{table}"""

NEW = """\\bottomrule
\\end{tabular}

\\vspace{2pt}
\\footnotesize
\\textit{Recall} and \\textit{Precision} are measured at the threshold
satisfying the 95\\% precision constraint; \\textit{F1} is measured at that
same threshold, and \\textit{Cost} is the total business cost on the test set
there. XGBoost does not accept a \\texttt{class\\_weight} argument, so its
\\texttt{class\\_weight} run is identical to its no-resampling run and is
omitted here; \\emph{class weighting} was therefore evaluated on Logistic
Regression, Decision Tree and Random Forest only.
\\end{table}"""

if OLD not in s:
    raise SystemExit("anchor not found")

s = s.replace(OLD, NEW, 1)
p.write_text(s, encoding="utf-8")
print("[ok] Table 4 notes moved out of tabular")
