"""S10af · Table 16 (sensitivity): cac dong co Workload/day vuot 100/ngay
(685.0, 301.7, 233.3) -- chua ghi chu se mau thuan voi rang buoc capacity
ma report dat ra o §5.3. Them ghi chu: cac diem nay KHONG duoc chon duoi
rang buoc 100 review/ngay, va do do la duong cost toi uu chung (co ca
constraint), con policy hai tang la diem duy nhat duoc chon duoi constraint."""
from pathlib import Path

p = Path("report/Sections/5-Cost.tex")
s = p.read_text(encoding="utf-8")

OLD = """\\caption{Sensitivity of the cost-minimising operating point to the assumed
cost of one manual review. The threshold rises from 0.0405 to 0.4605 as the
review cost increases twenty-fold.}"""

NEW = """\\caption{Sensitivity of the cost-minimising operating point to the assumed
cost of one manual review. The threshold rises from 0.0405 to 0.4605 as the
review cost increases twenty-fold. The first three rows exceed the
100-review-per-day analyst capacity and are therefore reported as the
unconstrained cost optimum for reference; only the rows at and above USD 1.00
are deployable under a single analyst, and among those the two-tier policy of
Section~\\ref{sec:twotier} remains feasible at every review price because
auto-blocking consumes no analyst time.}"""

if OLD not in s:
    raise SystemExit("anchor not found")

s = s.replace(OLD, NEW, 1)
p.write_text(s, encoding="utf-8")
print("[ok] Table 16 caption notes capacity violation")
