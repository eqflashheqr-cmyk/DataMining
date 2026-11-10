"""
S10 · Regenerate the report figures whose numbers changed after the
per-day normalisation fix.

Affected figures
----------------
  s9_two_tier_diagram.png          policy hai tầy: ngưỡng + workload mới
  s10_capacity_tradeoff.png       trade-off recall vs analyst load (MỚI)
  s10_calibration.png              reliability diagram (MỚI)
  s10_sensitivity_review_cost.png  độ nhạy ngưỡng tối ưu theo chi phí review (MỚI)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import PALETTE

ART = "artifacts/tables"
CHARTS = "artifacts/charts"

COST_PER_FN = 5.45
COST_PER_FP = 0.30
CAPACITY_PER_DAY = 100
FACTOR = 5.0 / 3.0          # 1 / 0.6

sp = joblib.load("artifacts/models/split_with_features.joblib")
y_test = np.asarray(sp["y_test"]).astype(int)
score = np.load("artifacts/models/s5_predictions/FINAL_y_score_test.npy")
N_FRAUD = int(y_test.sum())
N_TEST = len(y_test)

# ---------------------------------------------------------------------------
# Ngưỡng mới: policy hai tầy ưu tiên tối đa recall trong ràng buộc capacity
# ---------------------------------------------------------------------------
THR_AUTO = 0.81
THR_REVIEW = 0.175

auto = score >= THR_AUTO
review = (score >= THR_REVIEW) & (score < THR_AUTO)
approve = score < THR_REVIEW

fraud = y_test == 1
n_fraud_auto = int((fraud & auto).sum())
n_legit_auto = int((~fraud & auto).sum())
n_fraud_rev = int((fraud & review).sum())
n_legit_rev = int((~fraud & review).sum())
n_fraud_app = int((fraud & approve).sum())

tp = n_fraud_auto + n_fraud_rev
fn = N_FRAUD - tp
fp = n_legit_auto + n_legit_rev
recall = tp / N_FRAUD
total_cost = fp * COST_PER_FP + fn * COST_PER_FN
review_per_day = int(review.sum()) * FACTOR
auto_per_day = int(auto.sum()) * FACTOR

# ---------------------------------------------------------------------------
# 1. Diagram policy hai tầy
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(13.5, 8))
ax.axis("off")

boxes = [
    (0.5, 0.89, f"{N_TEST:,} transactions scored\nby the model",
     PALETTE["light"], "white"),
    (0.18, 0.58, f"AUTO-BLOCK\nscore >= {THR_AUTO:.2f}\n\n"
     f"{int(auto.sum()):,} txns ({auto.sum()/N_TEST:.2%})\n"
     f"{auto_per_day:.0f}/day\n"
     f"{n_fraud_auto} fraud stopped, {n_legit_auto} FP",
     PALETTE["danger"], "white"),
    (0.50, 0.58, f"MANUAL REVIEW\n{THR_REVIEW:.2f} <= score < {THR_AUTO:.2f}\n\n"
     f"{int(review.sum()):,} txns ({review.sum()/N_TEST:.2%})\n"
     f"{review_per_day:.0f}/day - within capacity\n"
     f"{n_fraud_rev} fraud caught, {n_legit_rev} FP",
     PALETTE["warn"], "white"),
    (0.82, 0.58, f"APPROVE\nscore < {THR_REVIEW:.2f}\n\n"
     f"{int(approve.sum()):,} txns ({approve.sum()/N_TEST:.2%})\n"
     f"{n_fraud_app} fraud missed",
     PALETTE["primary"], "white"),
]

for cx, cy, txt, fc, tc in boxes:
    ax.add_patch(plt.Rectangle((cx - 0.145, cy - 0.105), 0.29, 0.21,
                               facecolor=fc, edgecolor="black", lw=1.5,
                               transform=ax.transAxes, zorder=2))
    ax.text(cx, cy, txt, ha="center", va="center", fontsize=9, color=tc,
            transform=ax.transAxes, zorder=3, fontweight="bold")

for x1 in (0.18, 0.50, 0.82):
    ax.annotate("", xy=(x1, 0.675), xytext=(0.5, 0.795),
                xycoords="axes fraction", textcoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", lw=1.8, color="black"), zorder=1)

ax.text(0.5, 0.35,
        f"Two-tier:  recall = {recall:.1%}   |   "
        f"total cost = ${total_cost:.2f}   |   "
        f"analyst load = {review_per_day:.0f}/day "
        f"({review_per_day/CAPACITY_PER_DAY:.0%} of one analyst)",
        ha="center", fontsize=12, fontweight="bold", color=PALETTE["primary"],
        transform=ax.transAxes)
ax.text(0.5, 0.25,
        "Single threshold 0.1767 (same recall, same cost): "
        "232/day = 2.3 analysts",
        ha="center", fontsize=10.5, color=PALETTE["light"],
        transform=ax.transAxes)

ax.set_title("Two-Tier Decision Architecture under a 100 Review/Day Capacity",
             fontsize=15, fontweight="bold", color=PALETTE["primary"], pad=20)
plt.savefig(f"{CHARTS}/s9_two_tier_diagram.png", dpi=140, bbox_inches="tight",
            facecolor="white")
plt.close()
print("[saved] s9_two_tier_diagram.png")

# ---------------------------------------------------------------------------
# 2. Trade-off recall vs analyst load (MỚI)
# ---------------------------------------------------------------------------
curve = pd.read_csv(f"{ART}/s10_threshold_curve_corrected.csv")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.6))

ax1.plot(curve["flagged_per_day"], curve["recall"], lw=2.2,
         color=PALETTE["primary"])
ax1.axvline(CAPACITY_PER_DAY, color=PALETTE["danger"], ls="--", lw=1.8,
            label=f"Capacity = {CAPACITY_PER_DAY} reviews/day")
ax1.axhline(0.7817, color=PALETTE["accent"], ls=":", lw=1.5)
ax1.scatter([193.3], [0.7817], color=PALETTE["accent"], zorder=5, s=70)
ax1.annotate("Single thr. 0.52\nrecall 78.2%, 193/day", (193.3, 0.7817),
              xytext=(225, 0.58), fontsize=9, color=PALETTE["accent"],
              arrowprops=dict(arrowstyle="->", color=PALETTE["accent"]))
ax1.set_xlabel("Analyst workload (transactions/day)")
ax1.set_ylabel("Recall at the 95% precision floor")
ax1.set_title("(a) A single threshold cannot satisfy both\n"
              "the 95% precision floor and the 100/day capacity",
              fontsize=12, fontweight="bold", color=PALETTE["primary"])
ax1.legend(fontsize=9, loc="lower right")
ax1.grid(alpha=0.25, ls="--")

ax2.plot(curve["flagged_per_day"], curve["recall"], lw=2.2,
         color=PALETTE["light"], label="Single threshold")
tt = pd.read_csv(f"{ART}/s10_two_tier_corrected.csv")
tt_ok = tt[tt["fits_capacity"]]
ax2.plot(tt_ok["review_per_day"], tt_ok["recall"], lw=2.2,
         color=PALETTE["warn"], label="Two-tier (feasible region)")
ax2.axvline(CAPACITY_PER_DAY, color=PALETTE["danger"], ls="--", lw=1.8)
ax2.scatter([review_per_day], [recall], color=PALETTE["danger"], zorder=6, s=90,
            marker="D")
ax2.annotate(f"Recommended policy\n{review_per_day:.0f}/day, recall {recall:.1%}",
              (review_per_day, recall), xytext=(30, 0.66), fontsize=9,
              color=PALETTE["danger"],
              arrowprops=dict(arrowstyle="->", color=PALETTE["danger"]))
ax2.set_xlabel("Transactions routed to a human analyst per day")
ax2.set_ylabel("Recall")
ax2.set_title("(b) The two-tier architecture reaches 81.0% recall\n"
              "with 70 reviews/day — one analyst suffices",
              fontsize=12, fontweight="bold", color=PALETTE["primary"])
ax2.legend(fontsize=9, loc="lower right")
ax2.grid(alpha=0.25, ls="--")

fig.suptitle("Why two tiers are necessary — Group 7, Data Mining (DA)",
             fontsize=14, fontweight="bold", color=PALETTE["primary"])
plt.tight_layout()
plt.savefig(f"{CHARTS}/s10_capacity_tradeoff.png", dpi=140, bbox_inches="tight",
            facecolor="white")
plt.close()
print("[saved] s10_capacity_tradeoff.png")

# ---------------------------------------------------------------------------
# 3. Reliability diagram (calibration) (MỚI)
# ---------------------------------------------------------------------------
cal = pd.read_csv(f"{ART}/s10_calibration.csv")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.4),
                               gridspec_kw={"width_ratios": [1.15, 1]})

ax1.plot([0, 1], [0, 1], ls="--", color="gray", lw=1.6,
         label="Perfect calibration")
ax1.plot(cal["mean_score"], cal["empirical_rate"], "o-", color=PALETTE["danger"],
         lw=2.2, ms=8, label="RF + SMOTE (1:100)")
ax1.set_xlabel("Mean predicted score")
ax1.set_ylabel("Empirical fraud rate")
ax1.set_title("(a) Reliability diagram", fontsize=12, fontweight="bold",
              color=PALETTE["primary"])
ax1.set_xlim(-0.02, 1.02)
ax1.set_ylim(-0.02, 1.02)
ax1.grid(alpha=0.25, ls="--")
ax1.legend(fontsize=9, loc="upper left")

labels = [f"{lo:.1f}-{hi:.1f}" for lo, hi in zip(cal["bin_lo"], cal["bin_hi"])]
ax2.barh(labels, cal["n"], color=PALETTE["accent"], alpha=0.85)
ax2.set_yscale("log")
ax2.set_xlabel("Transactions in bin (log scale)")
ax2.set_ylabel("Score bin")
ax2.set_title("(b) Score distribution — almost all mass below 0.1",
              fontsize=12, fontweight="bold", color=PALETTE["primary"])
ax2.grid(alpha=0.25, axis="x", ls="--")

fig.suptitle("Calibration of the final model (Brier = 0.000448) — Group 7",
             fontsize=14, fontweight="bold", color=PALETTE["primary"])
plt.tight_layout()
plt.savefig(f"{CHARTS}/s10_calibration.png", dpi=140, bbox_inches="tight",
            facecolor="white")
plt.close()
print("[saved] s10_calibration.png")

# ---------------------------------------------------------------------------
# 4. Sensitivity theo chi phí review (MỚI)
# ---------------------------------------------------------------------------
sens = pd.read_csv(f"{ART}/s10_sensitivity_review_cost.csv")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.2))

ax1.plot(sens["fp_cost"], sens["opt_thr"], "o-", color=PALETTE["primary"],
         lw=2.2, ms=8, label="Cost-minimising threshold")
ax1.plot(sens["fp_cost"], sens["opt_recall"], "s--", color=PALETTE["danger"],
         lw=1.8, ms=7, label="Recall at that threshold")
ax1.set_xlabel("Cost of one false alarm (USD)")
ax1.set_ylabel("Threshold / recall")
ax1.set_title("(a) The optimal threshold rises as review\n"
              "becomes more expensive", fontsize=12, fontweight="bold",
              color=PALETTE["primary"])
ax1.grid(alpha=0.25, ls="--")
ax1.legend(fontsize=9)

ax2.plot(sens["fp_cost"], sens["opt_cost"], "o-", color=PALETTE["warn"],
         lw=2.2, ms=8)
ax2.set_xlabel("Cost of one false alarm (USD)")
ax2.set_ylabel("Total cost on the test set (USD)")
ax2.set_title("(b) Total cost under the cost-minimising threshold",
              fontsize=12, fontweight="bold", color=PALETTE["primary"])
ax2.grid(alpha=0.25, ls="--")

fig.suptitle("Sensitivity of the operating point to the review-cost "
             "assumption — Group 7", fontsize=14, fontweight="bold",
             color=PALETTE["primary"])
plt.tight_layout()
plt.savefig(f"{CHARTS}/s10_sensitivity_review_cost.png", dpi=140,
            bbox_inches="tight", facecolor="white")
plt.close()
print("[saved] s10_sensitivity_review_cost.png")

print("\n--- two-tier summary ---")
print(f"thr_auto={THR_AUTO} thr_review={THR_REVIEW}")
print(f"auto={int(auto.sum())} review={int(review.sum())} "
      f"approve={int(approve.sum())}")
print(f"tp={tp} fp={fp} fn={fn} recall={recall:.4f} cost=${total_cost:.2f}")
print(f"review/day={review_per_day:.1f} auto/day={auto_per_day:.1f}")
