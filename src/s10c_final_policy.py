"""
S10c · Chốt thiết kế policy cuối cùng + đối chiếu chuẩn xác.

Phát hiện then chốt
-------------------
Policy hai tầy (auto >= 0.81, review >= 0.175) đạt recall 0.8099 và cost
$154.65 -- **y hệt** ngưỡng đơn tối ưu chi phí (0.1767) -- nhưng chỉ cần
71,7 review/ngày thay vì ~233/ngày.

Đây là cải thiện Pareto thật, không phải tuyên bố suông: cùng recall, cùng
cost, **1/3 workload analyst**. Đây là luận điểm trung tâm mới của report.
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
N_TEST = len(y_test)


def ev(thr):
    pred = score >= thr
    tp = int((pred & (y_test == 1)).sum())
    fp = int((pred & (y_test == 0)).sum())
    fn = N_FRAUD - tp
    return {"threshold": thr, "tp": tp, "fp": fp, "fn": fn,
            "flagged": tp + fp, "flagged_per_day": (tp + fp) * FACTOR,
            "recall": tp / N_FRAUD, "precision": tp / max(tp + fp, 1),
            "cost": fp * COST_PER_FP + fn * COST_PER_FN}


def ev2(a, r):
    auto = score >= a
    rev = (score >= r) & (score < a)
    tp_a = int((auto & (y_test == 1)).sum())
    fp_a = int((auto & (y_test == 0)).sum())
    tp_r = int((rev & (y_test == 1)).sum())
    fp_r = int((rev & (y_test == 0)).sum())
    tp, fp = tp_a + tp_r, fp_a + fp_r
    fn = N_FRAUD - tp
    return {"thr_auto": a, "thr_review": r,
            "n_auto": int(auto.sum()), "n_review": int(rev.sum()),
            "n_approve": int((score < r).sum()),
            "tp_auto": tp_a, "fp_auto": fp_a, "tp_review": tp_r, "fp_review": fp_r,
            "tp": tp, "fp": fp, "fn": fn,
            "auto_per_day": int(auto.sum()) * FACTOR,
            "review_per_day": int(rev.sum()) * FACTOR,
            "legit_blocked_per_day": fp_a * FACTOR,
            "review_precision": tp_r / max(tp_r + fp_r, 1),
            "auto_precision": tp_a / max(tp_a + fp_a, 1),
            "recall": tp / N_FRAUD,
            "cost": fp * COST_PER_FP + fn * COST_PER_FN}


# ---------------------------------------------------------------------------
# 1. Ngưỡng đơn tại recall khớp
# ---------------------------------------------------------------------------
print("=== NGƯỠNG ĐƠN TẠI CÁC MỨC RECALL ===")
for thr in [0.1767, 0.52, 0.65, 0.90, 0.9605]:
    d = ev(thr)
    print(f"  thr={thr:.4f}  recall={d['recall']:.4f}  prec={d['precision']:.4f} "
          f"cost=${d['cost']:.2f}  flagged/day={d['flagged_per_day']:.1f}  "
          f"fp/day={d['fp']*FACTOR:.1f}")

# ---------------------------------------------------------------------------
# 2. Thiết kế policy cuối
# ---------------------------------------------------------------------------
print("\n=== THIẾT KẾ POLICY HAI TẦY (final) ===")
for a, r in [(0.81, 0.175), (0.61, 0.11), (0.65, 0.50)]:
    d = ev2(a, r)
    print(f"  auto>={a:.2f} review>={r:.3f}: recall={d['recall']:.4f} "
          f"cost=${d['cost']:.2f} auto/day={d['auto_per_day']:.1f} "
          f"review/day={d['review_per_day']:.1f} "
          f"legit_blocked/day={d['legit_blocked_per_day']:.1f} "
          f"auto_prec={d['auto_precision']:.3f} "
          f"review_prec={d['review_precision']:.3f}")

FINAL = ev2(0.81, 0.175)
SINGLE_MATCH = ev(0.1767)
SINGLE_HEAD = ev(0.52)

# ---------------------------------------------------------------------------
# 3. Bảng so sánh cuối cùng
# ---------------------------------------------------------------------------
cmp_rows = [
    {"policy": "No model at all", "recall": 0.0,
     "cost_test": N_FRAUD * COST_PER_FN, "auto_per_day": 0.0,
     "review_per_day": 0.0, "legit_blocked_per_day": 0.0},
    {"policy": "Single threshold 0.52 (test-tuned)",
     "recall": SINGLE_HEAD["recall"], "cost_test": SINGLE_HEAD["cost"],
     "auto_per_day": 0.0, "review_per_day": SINGLE_HEAD["flagged_per_day"],
     "legit_blocked_per_day": SINGLE_HEAD["fp"] * FACTOR},
    {"policy": "Single threshold 0.65 (leakage-free)",
     "recall": ev(0.65)["recall"], "cost_test": ev(0.65)["cost"],
     "auto_per_day": 0.0, "review_per_day": ev(0.65)["flagged_per_day"],
     "legit_blocked_per_day": ev(0.65)["fp"] * FACTOR},
    {"policy": "Single threshold 0.1767 (cost-optimal, same recall)",
     "recall": SINGLE_MATCH["recall"], "cost_test": SINGLE_MATCH["cost"],
     "auto_per_day": 0.0, "review_per_day": SINGLE_MATCH["flagged_per_day"],
     "legit_blocked_per_day": SINGLE_MATCH["fp"] * FACTOR},
    {"policy": "TWO-TIER 0.81 / 0.175 (recommended)",
     "recall": FINAL["recall"], "cost_test": FINAL["cost"],
     "auto_per_day": FINAL["auto_per_day"],
     "review_per_day": FINAL["review_per_day"],
     "legit_blocked_per_day": FINAL["legit_blocked_per_day"]},
]
cmp = pd.DataFrame(cmp_rows)
cmp["analysts_needed"] = cmp["review_per_day"] / CAPACITY_PER_DAY
cmp["fits_capacity"] = cmp["review_per_day"] <= CAPACITY_PER_DAY
cmp.to_csv("artifacts/tables/s10_final_policy_comparison.csv", index=False)
print("\n=== BẢNG SO SÁNH CUỐI CÙNG ===")
print(cmp.round(3).to_string(index=False))

# ---------------------------------------------------------------------------
# 4. Chi phí năm
# ---------------------------------------------------------------------------
def annual(fp_test, fn_test):
    fn_day = fn_test * FACTOR
    fp_day = fp_test * FACTOR
    return (fn_day * COST_PER_FN + fp_day * COST_PER_FP) * 365


no_model_ann = N_FRAUD * FACTOR * COST_PER_FN * 365
ann_rows = [
    {"policy": "No model at all", "fn_per_day": N_FRAUD * FACTOR,
     "annual_cost": no_model_ann},
    {"policy": "Single 0.52", "fn_per_day": SINGLE_HEAD["fn"] * FACTOR,
     "annual_cost": annual(SINGLE_HEAD["fp"], SINGLE_HEAD["fn"])},
    {"policy": "Single 0.1767", "fn_per_day": SINGLE_MATCH["fn"] * FACTOR,
     "annual_cost": annual(SINGLE_MATCH["fp"], SINGLE_MATCH["fn"])},
    {"policy": "Two-tier 0.81/0.175", "fn_per_day": FINAL["fn"] * FACTOR,
     "annual_cost": annual(FINAL["fp"], FINAL["fn"])},
]
ann = pd.DataFrame(ann_rows)
ann["reduction"] = 1 - ann["annual_cost"] / no_model_ann
ann.to_csv("artifacts/tables/s10_final_annual_cost.csv", index=False)
print("\n=== CHI PHÍ NĂM ===")
print(ann.round(1).to_string(index=False))

# ---------------------------------------------------------------------------
# 5. Chi phí năm cho 1 triệu giao dịch (thang tham chiếu đề bài)
# ---------------------------------------------------------------------------
print("\n=== THANG 1 TRIỆU GIAO DỊCH / NĂM ===")
for name, d in [("Single 0.52", SINGLE_HEAD),
                ("Single 0.1767", SINGLE_MATCH),
                ("Two-tier", None)]:
    if d is None:
        fn_d, fp_d = FINAL["fn"] * FACTOR, FINAL["fp"] * FACTOR
    else:
        fn_d, fp_d = d["fn"] * FACTOR, d["fp"] * FACTOR
    scale = 1_000_000 / N_TEST
    fraud_1m = N_FRAUD * scale
    caught = d["recall"] * fraud_1m if d is not None else FINAL["recall"] * fraud_1m
    print(f"  {name:16s} fraud/1M={fraud_1m:8.1f} caught={caught:8.1f} "
          f"missed={fraud_1m-caught:8.1f} "
          f"flagged/day={(d['flagged'] if d else FINAL['n_auto']+FINAL['n_review'])*FACTOR:8.1f}")

# ---------------------------------------------------------------------------
# 6. Rule baselines per-day
# ---------------------------------------------------------------------------
rules = pd.read_csv("artifacts/tables/s9_rule_baselines.csv")
rules["flagged_per_day"] = rules["n_flagged"] * FACTOR
rules["analysts_needed"] = rules["flagged_per_day"] / CAPACITY_PER_DAY
rules.to_csv("artifacts/tables/s10_rule_baselines_per_day.csv", index=False)
print("\n=== RULE BASELINES PER-DAY ===")
print(rules[["Rule", "recall", "precision", "n_flagged", "flagged_per_day",
             "analysts_needed", "total_cost"]].round(2).to_string(index=False))

# ---------------------------------------------------------------------------
# 7. Sensitivity: cost review -> ngưỡng tối ưu (dùng đường cong đã tính)
# ---------------------------------------------------------------------------
curve = pd.read_csv("artifacts/tables/s10_threshold_curve_corrected.csv")
sens = []
for fp_cost in [0.10, 0.30, 0.50, 1.00, 2.00, 5.45]:
    tmp = curve.copy()
    tmp["cc"] = tmp["fp"] * fp_cost + tmp["fn"] * COST_PER_FN
    b = tmp.sort_values(["cc", "recall"], ascending=[True, False]).iloc[0]
    sens.append({"fp_cost": fp_cost, "opt_thr": b.threshold,
                 "opt_recall": b.recall, "opt_precision": b.precision,
                 "opt_cost": b.cc,
                 "workload_per_day": b.flagged_per_day})
sens = pd.DataFrame(sens)
sens.to_csv("artifacts/tables/s10_sensitivity_review_cost.csv", index=False)
print("\n=== SENSITIVITY ===")
print(sens.round(4).to_string(index=False))
