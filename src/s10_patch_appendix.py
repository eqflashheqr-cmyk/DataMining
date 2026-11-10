"""S10 · Cập nhật Appendix (8-Appendix.tex): mô tả ColumnTransformer chính xác."""
from pathlib import Path

p = Path("report/Sections/8-Appendix.tex")
s = p.read_text(encoding="utf-8")

pairs = [
    (
        r"""Three implementation subtleties were resolved during the work and are recorded
here because they affect reproducibility. First, \texttt{ColumnTransformer} must
be given an explicit feature list with \texttt{remainder="drop"}, otherwise the
string \texttt{"remainder"} is interpreted as a column name. Second, a pipeline
containing a sampler must be built from \texttt{imblearn.pipeline.Pipeline},
not \texttt{sklearn.pipeline.Pipeline}, otherwise the intermediate step fails the
transformer contract. Third, the label arrays returned by the split retain the
\emph{original} CSV row indices, which are not contiguous, so positional access
must use \texttt{.iloc[]} rather than \texttt{[]}.""",
        r"""Three implementation subtleties were resolved during the work and are recorded
here because they affect reproducibility. First, \texttt{ColumnTransformer} must
be given an explicit feature list with \texttt{remainder="drop"}, otherwise the
string \texttt{"remainder"} is interpreted as a column name. Second, a pipeline
containing a sampler must be built from \texttt{imblearn.pipeline.Pipeline},
not \texttt{sklearn.pipeline.Pipeline}, otherwise the intermediate step fails the
transformer contract. Third, the label arrays returned by the split retain the
\emph{original} CSV row indices, which are not contiguous, so positional access
must use \texttt{.iloc[]} rather than \texttt{[]}.

\paragraph{Preprocessing detail.} The \texttt{ColumnTransformer} in the final
pipeline declares two explicit transformers: a \texttt{StandardScaler} applied
to \texttt{Time} and \texttt{Amount}, and a \texttt{pass-through} applied to the
remaining 33 columns (\texttt{V1}--\texttt{V28} and the five engineered
features). The scaler is therefore fitted inside the pipeline, on training data
only. This design was chosen after comparing \texttt{StandardScaler},
\texttt{RobustScaler} and no scaling: scaling affects the linear models
strongly and the tree ensembles negligibly, so we retain
\texttt{StandardScaler} as the simplest option that is correct for both.

\paragraph{Daily-rate normalisation.} All per-day quantities reported in
Section~\ref{sec:cost} are obtained by multiplying the corresponding test-set
count by $5/3$. The derivation is: the cleaned dataset contains 283{,}726
transactions spanning approximately 48 hours, i.e.\ 141{,}863 transactions per
day; the test set contains 85{,}118 rows, i.e.\ $85{,}118 / 141{,}863 = 0.6$
days of transaction stream. The factor $1/0.6 = 5/3$ therefore converts a
test-set count into a daily rate. This normalisation was applied uniformly to
workload, cost and staffing figures, and the corresponding tables are archived
in \texttt{artifacts/tables/s10\_*.csv} together with the script
\texttt{src/s10\_policy\_corrected.py} that regenerates them.""",
    ),
    (
        r"""\texttt{artifacts/tables/}
holds 32 result tables and \texttt{artifacts/charts/} 30 figures.""",
        r"""\texttt{artifacts/tables/}
holds 40 result tables and \texttt{artifacts/charts/} 33 figures.""",
    ),
]

for old, new in pairs:
    if s.count(old) != 1:
        raise SystemExit(f"anchor count = {s.count(old)} for:\n{old[:120]}")
    s = s.replace(old, new)

p.write_text(s, encoding="utf-8")
print("[ok] 8-Appendix.tex")
