"""S10 · Chèn Abstract + Keywords vào trang bìa (file 1-Title.tex)."""
from pathlib import Path

p = Path("report/Sections/1-Title.tex")
s = p.read_text(encoding="utf-8")

old = "\\vspace{0.6cm}\n\n\\begin{center}\n\\begin{tabular}{p{9cm}}\n"

new = r"""\vspace{0.45cm}

\begin{center}
\begin{tabular}{p{12.4cm}}
\textbf{\textit{Abstract.}} Fraud detection on transactional data is an
imbalanced, cost-sensitive problem: only 0.167\% of the 283{,}726 transactions
in the ULB credit card dataset are fraudulent, so accuracy is uninformative
and the operating point matters more than the classifier. We evaluate 27
configurations spanning five model families (Logistic Regression, Decision
Tree, Random Forest, XGBoost, Isolation Forest) and five imbalance-handling
techniques under a leakage-controlled workflow, and we translate the winning
model into a deployable operating policy. Random Forest with SMOTE at a 1:100
ratio is selected (F1 = 0.8605, Average Precision = 0.8239), reaching 78.17\%
recall at a 95\% precision floor, or 73.24\% with a leakage-free threshold.
Central to the business answer is the capacity constraint: at 141{,}863
transactions per day no single threshold can satisfy both the 95\% precision
floor and a 100-review-per-day analyst capacity --- it either demands 1.9
analysts or throttles recall to 40.9\%. A two-tier policy that auto-blocks
above 0.810 and reviews only the 0.175--0.810 band resolves this, attaining
81.0\% recall at USD 154.65 per 85{,}118 transactions with just 70 reviews per
day --- a Pareto improvement over the best single threshold, which needs 232
reviews per day for the same recall. We also quantify the effect of tuning the
threshold on the test set, show that a wider hyper-parameter search overfits
the cross-validation folds, and demonstrate that permutation importance and
SHAP both rank \texttt{Amount} first where the default impurity importance
ranks it 21st of 35.

\vspace{0.25cm}
\textbf{\textit{Keywords:}} credit card fraud detection; class imbalance;
SMOTE; cost-sensitive learning; precision--recall trade-off; threshold
calibration; operating policy; SHAP.
\end{tabular}
\end{center}

\vspace{0.5cm}
\begin{center}
\begin{tabular}{p{9cm}}
"""

if s.count(old) != 1:
    raise SystemExit(f"anchor count = {s.count(old)}")
s = s.replace(old, new)
p.write_text(s, encoding="utf-8")
print("[ok] 1-Title.tex: abstract + keywords inserted")
