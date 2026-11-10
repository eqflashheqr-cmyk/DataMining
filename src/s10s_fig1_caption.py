"""S10s · Figure 1 caption: 'full grid' -> nói rõ 21/25 ô có giá trị
(Isolation Forest chỉ chạy 1 cấu hình không resampling), đúng với lỗi §3.4."""
from pathlib import Path

p = Path("report/Sections/3-Method.tex")
s = p.read_text(encoding="utf-8")

OLD = """\\caption{Heatmap of Average Precision across the full grid of five model
families and five imbalance techniques. The highest Average Precision in the
grid (0.8348) is attained by Random Forest combined with SMOTE at the
\\emph{1:10} ratio --- the mildest oversampling that still changes the class
prior."""

NEW = """\\caption{Heatmap of Average Precision across the five model families and
five imbalance techniques. Of the 25 cells, 21 were executed: Isolation
Forest was run only without resampling, since it has no class label to
resample. The highest Average Precision in the grid (0.8348) is attained by
Random Forest combined with SMOTE at the \\emph{1:10} ratio --- the mildest
oversampling that still changes the class prior."""

if OLD not in s:
    raise SystemExit("anchor not found")

s = s.replace(OLD, NEW, 1)
p.write_text(s, encoding="utf-8")
print("[ok] Figure 1 caption corrected")
