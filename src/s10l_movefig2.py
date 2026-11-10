"""S10l · Chuyển Figure 2 (mutual information) sang Section 3.2 (Stage 3),
ngay sau đoạn feature engineering -- vị trí tự nhiên về mặt nội dung và
giúp lấp đầy trang 7 vốn gần như trống."""
from pathlib import Path

p = Path("report/Sections/3-Method.tex")
s = p.read_text(encoding="utf-8")

FIG = r"""\begin{figure}[h!]
\centering
\includegraphics[width=0.72\textwidth]{Images/charts/feature_engineering_evidence.png}
\caption{Mutual information between candidate features and the target class.
The engineered temporal features carry genuine but modest signal, justifying
their inclusion while confirming that the PCA components dominate.}
\label{fig:feateng}
\end{figure}
"""

# 1. gỡ khỏi Section 3.5
if s.count(FIG) != 1:
    raise SystemExit(f"figure count = {s.count(FIG)}")
s = s.replace("\n" + FIG, "")

# 2. chèn sau đoạn Stage 3 trong Section 3.2
ANCHOR = r"""study showed that the engineered features cost nothing and carry genuine
signal, though the gain itself is small (Section~\ref{sec:preprocess}).
"""
if s.count(ANCHOR) != 1:
    raise SystemExit(f"anchor count = {s.count(ANCHOR)}")
s = s.replace(ANCHOR, ANCHOR + "\n" + FIG)

p.write_text(s, encoding="utf-8")
print("[ok] 3-Method.tex: Figure 2 moved to Section 3.2")
