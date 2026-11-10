"""S10k · Di chuyển Figure 2 (mutual information) lên giữa Section 3.5 để
tránh bị đẩy sang trang riêng (trang 7 gần như trống)."""
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

# 1. gỡ figure khỏi cuối section
if s.count(FIG) != 1:
    raise SystemExit(f"figure block count = {s.count(FIG)}")
s = s.replace("\n" + FIG, "")

# 2. chèn lại ngay sau đoạn mở đầu của Section 3.5
ANCHOR = r"""We compared three feature sets --- the 30 original columns, the 35-column set
with the five engineered features, and a variant adding an hour-of-day feature
to the base set. The results are deliberately reported in full, including the
part that does not favour us.
"""
if s.count(ANCHOR) != 1:
    raise SystemExit(f"anchor count = {s.count(ANCHOR)}")
s = s.replace(ANCHOR, ANCHOR + "\n" + FIG)

# 3. chỉnh câu cuối cho tự nhiên
old_tail = r"""consistent with the mutual-information evidence in
Figure~\ref{fig:feateng}."""
new_tail = r"""consistent with the mutual-information evidence in
Figure~\ref{fig:feateng}, which shows that the engineered features carry real
but modest signal."""
if s.count(old_tail) != 1:
    raise SystemExit(f"tail count = {s.count(old_tail)}")
s = s.replace(old_tail, new_tail)

p.write_text(s, encoding="utf-8")
print("[ok] 3-Method.tex: Figure 2 relocated")