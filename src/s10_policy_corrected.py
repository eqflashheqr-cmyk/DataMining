"""
S10 · Corrected operating-policy analysis (per-day normalisation + capacity).

Mục đích: chuẩn hoá lại toàn bộ số liệu "per day" của report về đúng
mốc thời gian, và tối ưu lại policy theo ràng buộc capacity 100 review/ngày
mà đề bài đưa ra.

Bối cảnh quan trọng
-------------------
Dataset gốc: 283.726 giao dịch trong ~2 ngày  ->  141.863 giao dịch/ngày.
Tập test chiếm 30%  ->  85.118 dòng  ->  **0,6 ngày**.

Bản sửa cũ chia mọi số đếm lấy từ tập test cho DATASET_DAYS = 2, tức coi
85.118 dòng là 2 ngày. Sai 3,33 lần. Script này dùng đúng DAY_SPAN_TEST.

Thiết kế policy mới
-------------------
Vì capacity 100 review/ngày là con số CỐ ĐỊNH từ đề bài, ta tối ưu:

  1. NGƯỠNG ĐƠN tối ưu recall trong ràng buộc capacity
     -> cho biết cái giá của việc chỉ có 1 analyst.

  2. POLICY HAI TẦY: auto-block (score >= thr_auto, KHÔNG tốn analyst) +
     manual review (thr_review <= score < thr_auto, TỐN analyst).
     -> giảm tải analyst xuống dưới 100/ngày trong khi vẫn giữ recall cao.

Ràng buộc thêm: thr_auto >= 0.50 (auto-block phải là tầng "high confidence"),
và số khách hàng hợp lệ bị block nhầm phải được báo cáo minh bạch.
"""

from __future__ import annotations

import joblib
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# HẰNG SỐ
# ---------------------------------------------------------------------------
COST_PER_FN = 5.45          # 1.00 direct loss + 4.45 handling (LexisNexis 2024)
COST_PER_FP = 0.30          # giả định của nhóm: chi phí review 1 giao dịch hợp lệ
MIN_PRECISION = 0.95
CAPACITY_PER_DAY = 100       # ràng buộc cố định từ đề bài (câu hỏi #4)

N_CLEAN = 283_726
DATASET_DAYS = 2
ROWS_PER_DAY = N_CLEAN / DATASET_DAYS          # 141.863
TEST_ROWS = 85_118
DAY_SPAN_TEST = TEST_ROWS / ROWS_PER_DAY       # 0,6 ngày
FACTOR = 1.0 / DAY_SPAN_TEST                  # 3,3333

MIN_AUTO_THRESHOLD = 0.50     # auto-block phải là tầng high-confidence

ART = "artifacts/tables"

sp = joblib.load("artifacts/models/split_with_features.joblib")
y_test = np.asarray(sp["y_test"]).astype(int)
score = np.load("artifacts/models/s5_predictions/FINAL_y_score_test.npy")

N_FRAUD = int(y_test.sum())                   # 142


def confusion(y, s, thr):
    pred = (s >= thr)
    tp = int(((pred == 1) & (y == 1)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    tn = int(((pred == 0) & (y == 0)).sum())
    return tn, fp, fn, tp


def cost_of(fp, fn):
    return fp * COST_PER_FP + fn * COST_PER_FN


def per_day(n):
    return n * FACTOR


def analysts(load_per_day):
    return load_per_day / CAPACITY_PER_DAY


# ===========================================================================
# 1. NGƯỠNG ĐƠN
# ===========================================================================
rows = []
for thr in [0.52, 0.65]:
    tn, fp, fn, tp = confusion(y_test, score, thr)
    flagged = tp + fp
    rows.append({
        "threshold": thr, "flagged_test": flagged,
        "flagged_per_day": per_day(flagged),
        "fp_per_day": per_day(fp), "fn_per_day": per_day(fn),
        "recall": tp / N_FRAUD, "precision": tp / flagged,
        "cost_test": cost_of(fp, fn),
        "analysts_needed": analysts(per_day(flagged)),
    })
single_thresholds = pd.DataFrame(rows)
single_thresholds.to_csv(f"{ART}/s10_single_threshold_per_day.csv", index=False)
print("=== 1. NGƯỠNG ĐƠN, CHUẨN HOÁ PER-DAY ===")
print(single_thresholds.round(3).to_string(index=False))

# ===========================================================================
# 2. ĐƯỜNG CONG NGƯỠNG
# ===========================================================================
recs = []
for thr in np.linspace(0.0, 1.0, 2001):
    tn, fp, fn, tp = confusion(y_test, score, thr)
    flagged = tp + fp
    if flagged == 0:
        continue
    recs.append({
        "threshold": thr, "tp": tp, "fp": fp, "fn": fn, "flagged": flagged,
        "flagged_per_day": per_day(flagged),
        "precision": tp / flagged, "recall": tp / N_FRAUD,
        "cost": cost_of(fp, fn),
        "fits_capacity": per_day(flagged) <= CAPACITY_PER_DAY,
    })
curve = pd.DataFrame(recs)
curve.to_csv(f"{ART}/s10_threshold_curve_corrected.csv", index=False)

feasible = curve[curve["fits_capacity"]]
best_single = feasible.sort_values(
    ["recall", "cost"], ascending=[False, True]).iloc[0]
best_single_unc = curve.sort_values(
    ["cost", "recall"], ascending=[True, False]).iloc[0]
print("\n=== 2. NGƯỠNG ĐƠN TỐI ƯU ===")
print("[a] trong ràng buộc capacity 100/ngày:")
print(best_single.astype(float).round(4).to_string())
print("\n[b] tối ưu chi phí, KHÔNG ràng buộc capacity:")
print(best_single_unc.astype(float).round(4).to_string())

# ===========================================================================
# 3. POLICY HAI TẦY
# ===========================================================================
def two_tier(thr_auto, thr_review):
    auto = score >= thr_auto
    rev = (score >= thr_review) & (score < thr_auto)
    tp = int((auto & (y_test == 1)).sum()) + int((rev & (y_test == 1)).sum())
    fp = int((auto & (y_test == 0)).sum()) + int((rev & (y_test == 0)).sum())
    fn = N_FRAUD - tp
    return {
        "thr_auto": thr_auto, "thr_review": thr_review,
        "n_auto": int(auto.sum()), "n_review": int(rev.sum()),
        "n_approve": int((score < thr_review).sum()),
        "tp": tp, "fn": fn,
        "fp_auto": int((auto & (y_test == 0)).sum()),
        "fp_review": int((rev & (y_test == 0)).sum()),
        "recall": tp / N_FRAUD,
        "review_per_day": per_day(int(rev.sum())),
        "auto_per_day": per_day(int(auto.sum())),
        "legit_blocked_per_day": per_day(int((auto & (y_test == 0)).sum())),
        "total_cost": cost_of(fp, fn),
    }


tt = []
for a in np.arange(MIN_AUTO_THRESHOLD, 0.96, 0.01):
    for r in np.arange(0.01, a, 0.005):
        d = two_tier(a, r)
        d["fits_capacity"] = d["review_per_day"] <= CAPACITY_PER_DAY
        d["analysts"] = analysts(d["review_per_day"])
        tt.append(d)
tt = pd.DataFrame(tt)
tt.to_csv(f"{ART}/s10_two_tier_corrected.csv", index=False)

tt_ok = tt[tt["fits_capacity"]]
# ưu tiên: recall cao nhất -> cost thấp nhất -> số khách hợp lệ bị block ít nhất
best_tt = tt_ok.sort_values(
    ["recall", "total_cost", "legit_blocked_per_day"],
    ascending=[False, True, True]).iloc[0]
print("\n=== 3. POLICY HAI TẦY TỐI ƯU (recall cao nhất, capacity 100/ngày) ===")
print(best_tt.astype(float).round(4).to_string())

# phiên bản: ưu tiên giảm block nhầm (rủi ro khách hàng) trước
best_tt_cust = tt_ok.sort_values(
    ["legit_blocked_per_day", "recall", "total_cost"],
    ascending=[True, False, True]).iloc[0]
print("\n--- phương án ưu tiên tối thiểu khách hàng bị block nhầm ---")
print(best_tt_cust.astype(float).round(4).to_string())

# ===========================================================================
# 4. SO SÁNH CÁC PHƯƠNG ÁN
# ===========================================================================
cands = []
for thr in [0.52, 0.65]:
    tn, fp, fn, tp = confusion(y_test, score, thr)
    flagged = tp + fp
    cands.append({
        "policy": f"Single {thr:.2f}",
        "recall": tp / N_FRAUD, "cost_test": cost_of(fp, fn),
        "auto_per_day": 0.0, "review_per_day": per_day(flagged),
        "analysts": analysts(per_day(flagged)),
        "legit_blocked_per_day": 0.0,
        "fits_capacity": per_day(flagged) <= CAPACITY_PER_DAY,
    })
cands.append({
    "policy": f"Single {best_single.threshold:.4f} (1 analyst)",
    "recall": best_single.recall, "cost_test": best_single.cost,
    "auto_per_day": 0.0, "review_per_day": best_single.flagged_per_day,
    "analysts": analysts(best_single.flagged_per_day),
    "legit_blocked_per_day": 0.0, "fits_capacity": True,
})
for a, r in [(0.65, 0.095), (0.65, 0.11), (0.55, 0.11), (0.50, 0.11),
             (float(best_tt.thr_auto), float(best_tt.thr_review)),
             (float(best_tt_cust.thr_auto), float(best_tt_cust.thr_review))]:
    d = two_tier(a, r)
    cands.append({
        "policy": f"Two-tier {a:.2f}/{r:.3f}",
        "recall": d["recall"], "cost_test": d["total_cost"],
        "auto_per_day": d["auto_per_day"], "review_per_day": d["review_per_day"],
        "analysts": d["review_per_day"] / CAPACITY_PER_DAY,
        "legit_blocked_per_day": d["legit_blocked_per_day"],
        "fits_capacity": d["review_per_day"] <= CAPACITY_PER_DAY,
    })
cmp_df = pd.DataFrame(cands).drop_duplicates(subset=["policy"])
cmp_df.to_csv(f"{ART}/s10_policy_comparison.csv", index=False)
print("\n=== 4. SO SÁNH CÁC PHƯƠNG ÁN ===")
print(cmp_df.round(3).to_string(index=False))

# ===========================================================================
# 5. CHI PHÍ NĂM
# ===========================================================================
def annual(fp_test, fn_test):
    return (per_day(fn_test) * COST_PER_FN
            + per_day(fp_test) * COST_PER_FP) * 365


no_model = annual(0, N_FRAUD)
ann_rows = [{"policy": "No model at all", "fn_per_day": per_day(N_FRAUD),
             "annual_cost": no_model}]
for label, thr in [("Single 0.52", 0.52), ("Single 0.65", 0.65)]:
    tn, fp, fn, tp = confusion(y_test, score, thr)
    ann_rows.append({"policy": label, "fn_per_day": per_day(fn),
                      "annual_cost": annual(fp, fn)})
ann_rows.append({"policy": f"Single {best_single.threshold:.4f} (1 analyst)",
                 "fn_per_day": per_day(int(best_single.fn)),
                 "annual_cost": annual(int(best_single.fp), int(best_single.fn))})
for tag, b in [("Two-tier (recall-max)", best_tt),
               ("Two-tier (customer-safe)", best_tt_cust)]:
    d = two_tier(float(b.thr_auto), float(b.thr_review))
    ann_rows.append({
        "policy": f"{tag} {b.thr_auto:.2f}/{b.thr_review:.3f}",
        "fn_per_day": per_day(d["fn"]),
        "annual_cost": annual(d["fp_auto"] + d["fp_review"], d["fn"])})
ann = pd.DataFrame(ann_rows)
ann["reduction_vs_no_model"] = 1 - ann["annual_cost"] / no_model
ann.to_csv(f"{ART}/s10_annual_cost.csv", index=False)
print("\n=== 5. CHI PHÍ NĂM ===")
print(ann.round(1).to_string(index=False))

# ===========================================================================
# 6. SENSITIVITY THEO CHI PHÍ REVIEW
# ===========================================================================
sens = []
for fp_cost in [0.10, 0.30, 0.50, 1.00, 2.00, 5.45]:
    tmp = curve.copy()
    tmp["cost_c"] = tmp["fp"] * fp_cost + tmp["fn"] * COST_PER_FN
    b = tmp.sort_values(["cost_c", "recall"], ascending=[True, False]).iloc[0]
    b2 = tmp[tmp["fits_capacity"]].sort_values(
        ["recall", "cost_c"], ascending=[False, True]).iloc[0]
    sens.append({
        "fp_cost": fp_cost,
        "argmin_thr": b.threshold, "argmin_recall": b.recall,
        "argmin_cost": b.cost_c, "argmin_precision": b.precision,
        "capacity_thr": b2.threshold, "capacity_recall": b2.recall,
        "capacity_cost": b2.cost_c,
    })
sens = pd.DataFrame(sens)
sens.to_csv(f"{ART}/s10_sensitivity_review_cost.csv", index=False)
print("\n=== 6. SENSITIVITY THEO CHI PHÍ REVIEW ===")
print(sens.round(4).to_string(index=False))

# ===========================================================================
# 7. CALIBRATION
# ===========================================================================
from sklearn.metrics import brier_score_loss  # noqa: E402

bins = np.linspace(0, 1, 11)
cal = []
for i in range(10):
    lo, hi = bins[i], bins[i + 1]
    m = (score >= lo) & (score < hi) if i < 9 else (score >= lo) & (score <= hi)
    if m.sum() > 0:
        cal.append({"bin_lo": lo, "bin_hi": hi, "n": int(m.sum()),
                    "mean_score": float(score[m].mean()),
                    "empirical_rate": float(y_test[m].mean())})
cal = pd.DataFrame(cal)
cal.to_csv(f"{ART}/s10_calibration.csv", index=False)
print("\n=== 7. CALIBRATION ===")
print(cal.round(4).to_string(index=False))
print("Brier:", round(brier_score_loss(y_test, score), 6),
      "| base rate:", round(float(y_test.mean()), 6))

# ===========================================================================
# 8. RULE BASELINES -> per-day
# ===========================================================================
rules = pd.read_csv(f"{ART}/s9_rule_baselines.csv")
rules["flagged_per_day"] = rules["n_flagged"] * FACTOR
rules["analysts_needed"] = rules["flagged_per_day"] / CAPACITY_PER_DAY
rules.to_csv(f"{ART}/s10_rule_baselines_per_day.csv", index=False)
print("\n=== 8. RULE BASELINES (per-day) ===")
print(rules[["Rule", "recall", "precision", "n_flagged", "flagged_per_day",
             "analysts_needed", "total_cost"]].round(2).to_string(index=False))

print("\n=== TỔNG KẾT ===")
print(f"ROWS_PER_DAY          = {ROWS_PER_DAY:,.1f}")
print(f"DAY_SPAN_TEST         = {DAY_SPAN_TEST:.4f} ngày")
print(f"FACTOR (per-day mult) = {FACTOR:.4f}")
