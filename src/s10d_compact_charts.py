"""
S10d · Sinh lại các figure mới ở dạng gọn hơn (chiều cao nhỏ) để tiết kiệm
trang, đồng thời giữ nguyên thông tin.

Các figure được thu gọn:
  s10_capacity_tradeoff.png   -> 2 panel, figsize ngắn hơn
  s10_calibration.png          -> 1 panel reliability (bỏ panel histogram)
  s10_sensitivity_review_cost.png -> twin-axis 1 panel thay vì 2 panel
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.config import PALETTE

ART = "artifacts/tables"
CHARTS = "artifacts/charts"
CAP = 100

# ---------------------------------------------------------------------------
# 1. Trade-off capacity (2 panel, gọn)
# ---------------------------------------------------------------------------
curve = pd.read_csv(f"{ART}/s10_threshold_curve_corrected.csv")
tt = pd.read_csv(f"{ART}/s10_two_tier_corrected.csv")
tt_ok = tt[tt["fits_capacity"]]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 3.9))

ax1.plot(curve["flagged_per_day"], curve["recall"], lw=2.0,
         color=PALETTE["primary"])
ax1.axvline(CAP, color=PALETTE["danger"], ls="--", lw=1.6,
            label=f"Capacity = {CAP}/day")
ax1.axhline(0.7817, color=PALETTE["accent"], ls=":", lw=1.3)
ax1.scatter([193.3], [0.7817], color=PALETTE["accent"], zorder=5, s=55)
ax1.annotate("Single thr. 0.52\nrecall 78.2%, 193/day", (193.3, 0.7817),
              xytext=(228, 0.55), fontsize=8, color=PALETTE["accent"],
              arrowprops=dict(arrowstyle="->", color=PALETTE["accent"], lw=1.1))
ax1.set_xlabel("Analyst workload (transactions/day)", fontsize=9)
ax1.set_ylabel("Recall at the 95% precision floor", fontsize=9)
ax1.set_title("(a) A single threshold cannot satisfy both constraints",
              fontsize=10.5, fontweight="bold", color=PALETTE["primary"])
ax1.legend(fontsize=8, loc="lower right")
ax1.grid(alpha=0.25, ls="--")
ax1.tick_params(labelsize=8)

ax2.plot(curve["flagged_per_day"], curve["recall"], lw=2.0,
         color=PALETTE["light"], label="Single threshold")
ax2.plot(tt_ok["review_per_day"], tt_ok["recall"], lw=2.0,
         color=PALETTE["warn"], label="Two-tier (feasible region)")
ax2.axvline(CAP, color=PALETTE["danger"], ls="--", lw=1.6)
ax2.scatter([70.0], [0.8099], color=PALETTE["danger"], zorder=6, s=70,
            marker="D")
ax2.annotate("Recommended policy\n70/day, recall 81.0%", (70.0, 0.8099),
              xytext=(95, 0.66), fontsize=8, color=PALETTE["danger"],
              arrowprops=dict(arrowstyle="->", color=PALETTE["danger"], lw=1.1))
ax2.set_xlabel("Transactions routed to a human analyst per day", fontsize=9)
ax2.set_ylabel("Recall", fontsize=9)
ax2.set_title("(b) Two tiers: 81.0% recall with only 70 reviews/day",
              fontsize=10.5, fontweight="bold", color=PALETTE["primary"])
ax2.legend(fontsize=8, loc="lower right")
ax2.grid(alpha=0.25, ls="--")
ax2.tick_params(labelsize=8)

fig.suptitle("Why two tiers are necessary — Group 7", fontsize=12,
             fontweight="bold", color=PALETTE["primary"])
plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig(f"{CHARTS}/s10_capacity_tradeoff.png", dpi=140, bbox_inches="tight",
            facecolor="white")
plt.close()
print("[saved] s10_capacity_tradeoff.png")

# ---------------------------------------------------------------------------
# 2. Reliability (1 panel, gọn)
# ---------------------------------------------------------------------------
cal = pd.read_csv(f"{ART}/s10_calibration.csv")
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.plot([0, 1], [0, 1], ls="--", color="gray", lw=1.5,
        label="Perfect calibration")
ax.plot(cal["mean_score"], cal["empirical_rate"], "o-",
        color=PALETTE["danger"], lw=2.0, ms=7, label="RF + SMOTE (1:100)")
ax.set_xlabel("Mean predicted score", fontsize=9.5)
ax.set_ylabel("Empirical fraud rate", fontsize=9.5)
ax.set_title("Reliability diagram (Brier = 0.000448)", fontsize=11,
             fontweight="bold", color=PALETTE["primary"])
ax.set_xlim(-0.02, 1.02)
ax.set_ylim(-0.02, 1.02)
ax.grid(alpha=0.25, ls="--")
ax.legend(fontsize=8.5, loc="upper left")
ax.tick_params(labelsize=8.5)
plt.tight_layout()
plt.savefig(f"{CHARTS}/s10_calibration.png", dpi=140, bbox_inches="tight",
            facecolor="white")
plt.close()
print("[saved] s10_calibration.png")

# ---------------------------------------------------------------------------
# 3. Sensitivity (twin-axis 1 panel, gọn)
# ---------------------------------------------------------------------------
sens = pd.read_csv(f"{ART}/s10_sensitivity_review_cost.csv")
fig, ax = plt.subplots(figsize=(6.4, 4.0))
ax.plot(sens["fp_cost"], sens["opt_thr"], "o-", color=PALETTE["primary"],
        lw=2.0, ms=7, label="Cost-minimising threshold")
ax2 = ax.twinx()
ax2.plot(sens["fp_cost"], sens["opt_recall"], "s--", color=PALETTE["danger"],
         lw=1.6, ms=6, label="Recall at that threshold")
ax.set_xlabel("Cost of one false alarm (USD)", fontsize=9.5)
ax.set_ylabel("Optimal threshold", fontsize=9.5)
ax2.set_ylabel("Recall", fontsize=9.5, color=PALETTE["danger"])
ax.set_title("Sensitivity of the operating point to the review cost",
             fontsize=11, fontweight="bold", color=PALETTE["primary"])
ax.grid(alpha=0.25, ls="--")
ax.tick_params(labelsize=8.5)
ax2.tick_params(labelsize=8.5)
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, fontsize=8, loc="upper left")
plt.tight_layout()
plt.savefig(f"{CHARTS}/s10_sensitivity_review_cost.png", dpi=140,
            bbox_inches="tight", facecolor="white")
plt.close()
print("[saved] s10_sensitivity_review_cost.png")