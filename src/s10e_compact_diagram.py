"""
S10e · Thu gọn các figure có chiều cao lớn để tiết kiệm trang.

  s9_two_tier_diagram   13.5x8  -> 16x5.6  (rộng hơn, thấp hơn nhiều)
  s8_shap_summary        giữ nguyên (beeswarm cần độ phân giải)
  s7_pr_roc              -> rút nhẹ
  s5_aucpr_by_technique  -> rút nhẹ
  s9_rule_vs_model       -> rút nhẹ
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

from src.config import PALETTE

CHARTS = "artifacts/charts"
COST_PER_FN = 5.45
COST_PER_FP = 0.30
CAP = 100
FACTOR = 5.0 / 3.0

sp = joblib.load("artifacts/models/split_with_features.joblib")
y_test = np.asarray(sp["y_test"]).astype(int)
score = np.load("artifacts/models/s5_predictions/FINAL_y_score_test.npy")
N_FRAUD = int(y_test.sum())
N_TEST = len(y_test)

THR_AUTO, THR_REVIEW = 0.81, 0.175
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
# Diagram hai tầy: bố cục ngang, chiều cao thấp
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(16, 5.4))
ax.axis("off")

BW, BH = 0.205, 0.30
boxes = [
    (0.115, 0.52, f"SCORING\n\n{N_TEST:,} transactions\n"
     f"RF + SMOTE (1:100)\n0.045 ms / txn",
     PALETTE["light"], "white"),
    (0.375, 0.52, f"AUTO-BLOCK\nscore $\\geq$ {THR_AUTO:.2f}\n\n"
     f"{int(auto.sum()):,} txns | {auto_per_day:.0f}/day\n"
     f"{n_fraud_auto} fraud stopped\n{n_legit_auto} legit blocked\n"
     f"precision {n_fraud_auto/auto.sum():.3f}\n"
     f"NO analyst time",
     PALETTE["danger"], "white"),
    (0.625, 0.52, f"MANUAL REVIEW\n{THR_REVIEW:.3f} $\\leq$ score $<$ {THR_AUTO:.2f}\n\n"
     f"{int(review.sum()):,} txns | {review_per_day:.0f}/day\n"
     f"{n_fraud_rev} fraud caught\n{n_legit_rev} legit reviewed\n"
     f"precision {n_fraud_rev/review.sum():.3f}\n"
     f"capacity {CAP}/day",
     PALETTE["warn"], "white"),
    (0.885, 0.52, f"APPROVE\nscore $<$ {THR_REVIEW:.3f}\n\n"
     f"{int(approve.sum()):,} txns\n"
     f"{n_fraud_app} fraud missed\n"
     f"{approve.sum()/N_TEST:.2%} of traffic",
     PALETTE["primary"], "white"),
]

for cx, cy, txt, fc, tc in boxes:
    ax.add_patch(plt.Rectangle((cx - BW / 2, cy - BH / 2), BW, BH,
                               facecolor=fc, edgecolor="black", lw=1.6,
                               transform=ax.transAxes, zorder=2))
    ax.text(cx, cy, txt, ha="center", va="center", fontsize=10.5, color=tc,
            transform=ax.transAxes, zorder=3, fontweight="bold")

for x1 in (0.245, 0.5, 0.755):
    ax.annotate("", xy=(x1, 0.52), xytext=(x1 + 0.055, 0.52),
                xycoords="axes fraction", textcoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", lw=2.4, color="black"), zorder=1)

ax.text(0.5, 0.13,
        f"Two-tier policy:  recall = {recall:.1%}   |   total cost = "
        f"${total_cost:.2f} per {N_TEST:,} transactions   |   "
        f"analyst load = {review_per_day:.0f}/day "
        f"({review_per_day/CAP:.0%} of one analyst)",
        ha="center", fontsize=13, fontweight="bold", color=PALETTE["primary"],
        transform=ax.transAxes)
ax.text(0.5, 0.035,
        "Best single threshold (0.1767): same recall, same cost, "
        "but 232 reviews/day = 2.3 analysts",
        ha="center", fontsize=11, color=PALETTE["light"],
        transform=ax.transAxes)

ax.set_title("Two-Tier Decision Architecture under a 100 Review/Day Capacity",
             fontsize=15, fontweight="bold", color=PALETTE["primary"], pad=14)
plt.tight_layout()
plt.savefig(f"{CHARTS}/s9_two_tier_diagram.png", dpi=140, bbox_inches="tight",
            facecolor="white")
plt.close()
print("[saved] s9_two_tier_diagram.png (wide layout)")
