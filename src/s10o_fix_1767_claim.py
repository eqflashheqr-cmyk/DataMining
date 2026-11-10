"""S10o · Sửa lỗi còn sót: §5.5 gọi ngưỡng đơn 0.1767 là 'cost-minimising
nhất' nhưng artifact cho thấy global minimum là 0.0905 ($149.70, recall
0.8310, 301.7 review/ngày). Viết lại đoạn so sánh cho trung thực:
- 0.0905 là global cost minimum nhưng VI PHẠM capacity (302/ngày > 100).
- 0.1767 là ngưỡng đơn rẻ nhất *vẫn nằm trong vùng recall tương đương*
  (231.7/ngày, vẫn > 100/ngày).
- Kết luận đúng: hai tầng không cải thiện cost so với ngưỡng đơn tối ưu
  toàn cục; nó GIẢM TẢI ANALYST, và đó là ưu điểm vận hành."""
from pathlib import Path

p = Path("report/Sections/5-Cost.tex")
s = p.read_text(encoding="utf-8")

OLD = """The comparison with the third row is the sharpest statement of the result.
The cost-minimising single threshold, 0.1767, reaches essentially the same
recall (0.8028) at essentially the same cost (\\$160.10) --- but it does so by
sending \\emph{231.7 transactions per day} to human analysts, more than two
full teams. The two-tier policy reaches \\emph{higher} recall (0.8099) at
\\emph{lower} cost (\\$154.65) while requiring only \\textbf{70 reviews per day},
because the 163 auto-blocked transactions per day are removed by software
rather than by people. This is a genuine Pareto improvement, not a
re-labelling: the two-tier design cuts analyst workload by 70\\% relative to the
best single threshold \\emph{at the same recall}."""

NEW = """The comparison with the third row is the sharpest statement of the result, and
we state it without overclaiming. The cheapest \\emph{single} threshold over
the whole curve is 0.0905, which reaches recall 0.8310 at USD 149.70 --- but it
does so by sending \\emph{301.7 transactions per day} to human analysts, three
times the capacity the bank has. Among the thresholds that stay near this
operating point, 0.1767 is the cheapest: recall 0.8028 at USD 160.10, still
with \\emph{231.7 transactions per day} for the analysts, more than two full
teams. So the two-tier policy does \\emph{not} claim a cheaper operating point
than the global cost minimum; what it claims is that at essentially the same
recall it attains a slightly \\emph{higher} recall (0.8099) at a slightly
\\emph{lower} cost (\\$154.65) while requiring only \\textbf{70 reviews per
day}, because the 163 auto-blocked transactions per day are removed by software
rather than by people. The gain is therefore an \\emph{operational} one --- a
70\\% cut in analyst workload at the same recall --- not a reduction of the
business cost, which the cost model already minimises."""

if OLD not in s:
    raise SystemExit("anchor not found")

s = s.replace(OLD, NEW, 1)
p.write_text(s, encoding="utf-8")
print("[ok] 5-Cost.tex: comparison paragraph rewritten honestly")
