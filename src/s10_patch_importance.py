"""S10 · Sửa Table 7 (feature importance) + lời giải thích cơ chế, Section 4."""
from pathlib import Path

p = Path("report/Sections/4-Results.tex")
s = p.read_text(encoding="utf-8")

pairs = [
    # --- Table 7: sửa rank impurity theo dữ liệu thực tế ---
    (
        r"""\begin{table}[h!]
\centering
\caption{Feature importance measured three ways. Spearman correlation between
permutation importance and SHAP: $\rho = 0.766$ ($p = 8.3 \times 10^{-8}$).}
\label{tab:imp}
\begin{tabular}{lrrr}
\toprule
\textbf{Feature} & \textbf{Permutation rank} & \textbf{SHAP rank} & \textbf{Impurity rank} \\
\midrule
\texttt{Amount\_log} & \textbf{1} & 2 & 15 \\
\texttt{Amount} & 2 & \textbf{1} & \textbf{21} \\
\texttt{V14} & 3 & 3 & 1 \\
\texttt{V17} & 5 & 4 & 2 \\
\texttt{V4} & 4 & 9 & 8 \\
\texttt{V9} & 7 & 20 & 9 \\
\texttt{Day} & 15 & \textbf{5} & 31 \\
\texttt{Hour\_of\_Day} & 14 & 12 & 14 \\
\texttt{Is\_Night} & 31 & 29 & 30 \\
\bottomrule
\end{tabular}
\end{table}""",
        r"""\begin{table}[h!]
\centering
\caption{Feature importance measured three ways, all on the same test set and
the same final model. Spearman correlation between permutation importance and
SHAP: $\rho = 0.766$ ($p = 8.3 \times 10^{-8}$). Impurity ranks are computed
directly from \texttt{feature\_importances\_} of the fitted forest.}
\label{tab:imp}
\begin{tabular}{lrrr}
\toprule
\textbf{Feature} & \textbf{Permutation rank} & \textbf{SHAP rank} & \textbf{Impurity rank} \\
\midrule
\texttt{Amount\_log} & \textbf{1} & 2 & 15 \\
\texttt{Amount} & 2 & \textbf{1} & 21 \\
\texttt{V14} & 3 & 3 & \textbf{1} \\
\texttt{V17} & 5 & 4 & \textbf{2} \\
\texttt{V4} & 4 & 9 & 8 \\
\texttt{V9} & 7 & 20 & 9 \\
\texttt{Day} & 15 & \textbf{5} & 31 \\
\texttt{Hour\_of\_Day} & 14 & 12 & 26 \\
\texttt{Is\_Night} & 31 & 29 & 34 \\
\bottomrule
\end{tabular}
\end{table}""",
    ),
    # --- lời giải thích cơ chế ---
    (
        r"""\paragraph*{The default importance measure is wrong on this data.}
Table~\ref{tab:imp} shows that Random Forest's built-in impurity importance
ranks \texttt{Amount} only 21st of 35 features, while permutation importance
ranks it 2nd and SHAP ranks it 1st. The reason is distributional: transaction
amounts are extremely heavy-tailed, so a single split on \texttt{Amount} produces
a large impurity decrease even though the feature is close to useless in
isolation. Reporting \texttt{feature\_importances\_} would have hidden the
single most informative feature in the dataset. The Spearman correlation
between permutation importance and SHAP is 0.766, indicating broad agreement in
ranking.""",
        r"""\paragraph*{The default importance measure is wrong on this data.}
Table~\ref{tab:imp} shows that Random Forest's built-in impurity importance
ranks \texttt{Amount} only 21st of 35 features, while permutation importance
ranks it 2nd and SHAP ranks it 1st. The two criteria answer different
questions, and on this data they disagree sharply. Impurity importance measures
the \emph{mean decrease in Gini impurity} attributable to the splits chosen on a
feature, weighted by how pure the resulting leaves are. Because 99.83\% of the
transactions are legitimate, the Gini baseline is already close to zero, and the
absolute impurity decrease contributed by \texttt{Amount} --- whose
discriminative power is essentially threshold-like (small amounts are
legitimate) and therefore diffuse across many splits --- is small even though
destroying that feature costs the model a great deal of accuracy. The PCA
components \texttt{V14} and \texttt{V17}, by contrast, produce few, very pure
leaves and therefore dominate the impurity ranking.

Reporting \texttt{feature\_importances\_} alone would have hidden the single
most informative feature in the dataset --- and, with it, the fact that the
model's signal is mostly about transaction size, which is exactly the insight
a bank needs in order to design an amount-gating policy. The Spearman
correlation between permutation importance and SHAP is 0.766, indicating broad
agreement in ranking between the two measure-based approaches.""",
    ),
]

for old, new in pairs:
    if s.count(old) != 1:
        raise SystemExit(f"anchor count = {s.count(old)} for:\n{old[:150]}")
    s = s.replace(old, new)

p.write_text(s, encoding="utf-8")
print("[ok] 4-Results.tex: Table 7 + impurity explanation")
