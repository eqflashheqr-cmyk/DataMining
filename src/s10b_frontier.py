"""
S10b · Khảo sát Pareto frontier của policy hai tầy để chọn thiết kế
có lập luận vững nhất (không chỉ tối ưu một con số).

Câu hỏi thiết kế
----------------
1. Band "manual review" nên có precision bao nhiêu? Rất thấp nghĩa là
   analyst chủ yếu đi làm việc vô ích. Nhưng đó là hệ quả của cost model
   ($0.30/review), và phải được báo cáo minh bạch.
2. Ngưỡng auto-block cao giúp giảm số khách hàng bị block nhầm.
3. Có design nào vừa recall cao, vừa cost thấp, vừa tôn trọng capacity
   100 review/ngày, vừa block nhầm ít không?
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import joblib
import numpy as np
import pandas as pd

COST_PER_FN = 5.45
COST_PER_FP = 0.30
CAPACITY_PER_DAY = 100
FACTOR = 5.0 / 3.0

sp = joblib.load("artifacts/models/split_with_features.joblib")
y_test = np.asarray(sp["y_test"]).astype(int)
score = np.load("artifacts/models/s5_predictions/FINAL_y_score_test.npy")
N_FRAUD = int(y_test.sum())

# ---------------------------------------------------------------------------
# Phân phối score
# ---------------------------------------------------------------------------
print("=== PHÂN PHỐI SCORE (test set) ===")
qs = [0.5, 0.9, 0.99, 0.999, 1.0]
print("all txns  quantiles:", {q: round(float(np.quantile(score, q)), 4)
                               for q in qs})
fraud_scores = score[y_test == 1]
qs2 = [0.05, 0.1, 0.25, 0.5, 0.75, 0.9]
print("frauds    quantiles:", {q: round(float(np.quantile(fraud_scores, q)), 4)
                               for q in qs2})
print("fraud scores >0.5:", int((fraud_scores > 0.5).sum()), "/", N_FRAUD)
print("fraud scores >0.9:", int((fraud_scores > 0.9).sum()))
print("fraud scores >0.99:", int((fraud_scores > 0.99).sum()))

# ---------------------------------------------------------------------------
# Frontier đầy đủ
# ---------------------------------------------------------------------------
rows = []
for a in np.arange(0.50, 0.995, 0.005):
    for r in np.arange(0.005, a, 0.005):
        auto = score >= a
        rev = (score >= r) & (score < a)
        tp_a = int((auto & (y_test == 1)).sum())
        fp_a = int((auto & (y_test == 0)).sum())
        tp_r = int((rev & (y_test == 1)).sum())
        fp_r = int((rev & (y_test == 0)).sum())
        tp, fp = tp_a + tp_r, fp_a + fp_r
        fn = N_FRAUD - tp
        rev_day = int(rev.sum()) * FACTOR
        rows.append({
            "thr_auto": a, "thr_review": r,
            "n_auto": int(auto.sum()), "n_review": int(rev.sum()),
            "tp_auto": tp_a, "fp_auto": fp_a, "tp_review": tp_r, "fp_review": fp_r,
            "tp": tp, "fp": fp, "fn": fn,
            "recall": tp / N_FRAUD,
            "cost": fp * COST_PER_FP + fn * COST_PER_FN,
            "review_per_day": rev_day,
            "auto_per_day": int(auto.sum()) * FACTOR,
            "legit_blocked_per_day": fp_a * FACTOR,
            "review_precision": tp_r / max(tp_r + fp_r, 1),
            "auto_precision": tp_a / max(tp_a + fp_a, 1),
            "fits": rev_day <= CAPACITY_PER_DAY,
        })
fr = pd.DataFrame(rows)
fr.to_csv("artifacts/tables/s10_two_tier_frontier.csv", index=False)

feas = fr[fr["fits"]].copy()
print("\n=== FRONTIER TRONG RÀNG BUỘC CAPACITY 100/NGÀY ===")
print("Tổng số design khả thi:", len(feas))
print("Recall cao nhất:", round(feas["recall"].max(), 4))
print("Cost thấp nhất  :", round(feas["cost"].min(), 2))

cols = ["thr_auto", "thr_review", "recall", "cost", "review_per_day",
        "auto_per_day", "legit_blocked_per_day", "review_precision",
        "auto_precision"]

print("\n--- top 12 theo recall (tie-break cost, rồi ít block nhầm) ---")
top = feas.sort_values(["recall", "cost", "legit_blocked_per_day"],
                        ascending=[False, True, True]).head(12)
print(top[cols].round(3).to_string(index=False))

print("\n--- top 12 theo cost (trong ràng buộc) ---")
cheap = feas.sort_values(["cost", "recall"], ascending=[True, False]).head(12)
print(cheap[cols].round(3).to_string(index=False))

print("\n--- top 12 theo ít khách hàng bị block nhầm (tie-break recall) ---")
safe = feas.sort_values(["legit_blocked_per_day", "recall", "cost"],
                         ascending=[True, False, True]).head(12)
print(safe[cols].round(3).to_string(index=False))

# ---------------------------------------------------------------------------
# Các design "cân bằng": recall >= 0.80, cost <= 160, review <= 100,
# block nhầm tối thiểu
# ---------------------------------------------------------------------------
bal = feas[(feas["recall"] >= 0.80) & (feas["cost"] <= 160.0)]
bal = bal.sort_values(["legit_blocked_per_day", "cost"], ascending=[True, True])
print("\n=== DESIGN CÂN BẰNG (recall>=0.80, cost<=160, capacity OK) ===")
print("số lựa chọn:", len(bal))
print(bal.head(15)[cols].round(3).to_string(index=False))

# ---------------------------------------------------------------------------
# Thiết kế tham chiếu
# ---------------------------------------------------------------------------
print("\n=== THAM KHẢO: một số design được chọn tay ===")
for a, r in [(0.52, 0.45), (0.52, 0.40), (0.65, 0.50), (0.52, 0.30),
             (0.52, 0.20), (0.61, 0.11), (0.81, 0.175)]:
    auto = score >= a
    rev = (score >= r) & (score < a)
    tp_a = int((auto & (y_test == 1)).sum())
    fp_a = int((auto & (y_test == 0)).sum())
    tp_r = int((rev & (y_test == 1)).sum())
    fp_r = int((rev & (y_test == 0)).sum())
    tp, fp = tp_a + tp_r, fp_a + fp_r
    fn = N_FRAUD - tp
    print(f"  auto>={a:.2f} review>={r:.3f} | recall={tp/N_FRAUD:.4f} "
          f"cost=${fp*COST_PER_FP+fn*COST_PER_FN:7.2f} "
          f"review/day={int(rev.sum())*FACTOR:7.1f} "
          f"auto/day={int(auto.sum())*FACTOR:6.1f} "
          f"legit_blocked/day={fp_a*FACTOR:5.1f} "
          f"review_prec={tp_r/max(tp_r+fp_r,1):.3f} "
          f"auto_prec={tp_a/max(tp_a+fp_a,1):.3f}")
