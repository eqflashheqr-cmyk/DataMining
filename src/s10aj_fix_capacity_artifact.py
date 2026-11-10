"""S10aj · Regenerate artifacts/tables/s9_review_capacity.csv voi he so
chuuan hoa dung (5/3 = 1/0.6 ngay) thay cho 2 ngay sai. Report da in
193.3/ngay; artifact cu van in 58.0/ngay -> thay giao khong doi chieu duoc.
Giu nguyen ten cot, chi sua gia tri daily_review_cost/annual_review_cost
theo so review thuc te (khong con nhan capacity 100 lam so flag).
"""
from pathlib import Path

import pandas as pd

REVIEW_COST = 0.30
FACTOR = 5 / 3  # test set spans 0.6 days

p = Path("artifacts/tables/s9_review_capacity.csv")
df = pd.read_csv(p)

rows = []
for _, r in df.iterrows():
    flagged_test = int(r["flagged_total_in_test"])
    flagged_day = flagged_test * FACTOR
    utilisation = flagged_day / r["review_capacity_per_day"]
    daily_cost = flagged_day * REVIEW_COST
    rows.append({
        "Threshold method": r["Threshold method"],
        "threshold": r["threshold"],
        "flagged_total_in_test": flagged_test,
        "flagged_per_day": round(flagged_day, 4),
        "review_capacity_per_day": int(r["review_capacity_per_day"]),
        "utilisation": round(utilisation, 4),
        "over_capacity": bool(utilisation > 1.0),
        "over_by_per_day": round(max(0.0, flagged_day - r["review_capacity_per_day"]), 4),
        "daily_review_cost": round(daily_cost, 2),
        "annual_review_cost": round(daily_cost * 365, 2),
    })

out = pd.DataFrame(rows)
out.to_csv(p, index=False)
print(out.to_string())
print(f"\n[ok] rewritten with 5/3 normalisation -> {p}")
