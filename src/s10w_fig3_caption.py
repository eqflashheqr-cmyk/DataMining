"""S10w · Figure 3 caption: nhắc CẢ HAI operating point (0.52 test-tuned và
0.65 out-of-fold) -- sửa lỗi §5.2 (chỉ nêu 0.52 là điểm lạc quan)."""
from pathlib import Path

p = Path("report/Sections/4-Results.tex")
s = p.read_text(encoding="utf-8")

OLD = """\\caption{Precision--recall and ROC curves for the final model. The chosen
operating point (threshold 0.52) attains 95.7\\% precision at 78.2\\% recall and
is marked on the PR curve. The dashed horizontal line indicates the 95\\%
precision constraint.}"""

NEW = """\\caption{Precision--recall and ROC curves for the final model. Two operating
points are marked on the PR curve: the test-tuned threshold 0.52 (diamond,
95.7\\% precision at 78.2\\% recall) and the leakage-free out-of-fold threshold
0.65 (circle, 96.3\\% precision at 73.2\\% recall). The dashed horizontal line
indicates the 95\\% precision constraint. The gap between the two markers is the
price of tuning the threshold on the test set (Section~\\ref{sec:leakage}).}"""

if OLD not in s:
    raise SystemExit("anchor not found")

s = s.replace(OLD, NEW, 1)
p.write_text(s, encoding="utf-8")
print("[ok] Figure 3 caption mentions both thresholds")
