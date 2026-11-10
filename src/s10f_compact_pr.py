"""
S10f · Rút gọn chiều cao các figure còn lại (giữ nguyên nội dung).

Mục tiêu: giảm ~3 trang. Cách làm: giảm chiều cao figure (dùng figsize
thấp hơn, đặt legend bên trong) thay vì cắt nội dung.
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
from sklearn.metrics import average_precision_score, precision_recall_curve, roc_auc_score, roc_curve

from src.config import PALETTE

ART = "artifacts/tables"
CHARTS = "artifacts/charts"

sp = joblib.load("artifacts/models/split_with_features.joblib")
y_test = np.asarray(sp["y_test"]).astype(int)
score = np.load("artifacts/models/s5_predictions/FINAL_y_score_test.npy")

# ---------------------------------------------------------------------------
# 1. PR/ROC operating point -> gọn
# ---------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.0))

prec, rec, _ = precision_recall_curve(y_test, score)
ax1.plot(rec, prec, lw=2.0, color=PALETTE["primary"], label="RF + SMOTE (1:100)")
ax1.axhline(0.95, color=PALETTE["danger"], ls="--", lw=1.6,
            label="95% precision floor")
ax1.scatter([0.7817], [0.9569], color=PALETTE["danger"], zorder=6, s=80,
            marker="D")
ax1.annotate("Operating point\nthr = 0.52\nP 95.7%, R 78.2%", (0.7817, 0.9569),
             xytext=(0.28, 0.80), fontsize=9, color=PALETTE["danger"],
             arrowprops=dict(arrowstyle="->", color=PALETTE["danger"], lw=1.3))
ax1.set_xlabel("Recall", fontsize=9.5)
ax1.set_ylabel("Precision", fontsize=9.5)
ax1.set_title("(a) Precision-Recall curve", fontsize=11, fontweight="bold",
              color=PALETTE["primary"])
ax1.set_xlim(0, 1)
ax1.set_ylim(0, 1.02)
ax1.grid(alpha=0.25, ls="--")
ax1.legend(fontsize=8.5, loc="lower left")
ax1.tick_params(labelsize=8.5)

fpr, tpr, _ = roc_curve(y_test, score)
ax2.plot(fpr, tpr, lw=2.0, color=PALETTE["accent"], label="RF + SMOTE (1:100)")
ax2.plot([0, 1], [0, 1], ls="--", color="gray", lw=1.2, label="Random")
ax2.set_xlabel("False positive rate", fontsize=9.5)
ax2.set_ylabel("True positive rate", fontsize=9.5)
ax2.set_title(f"(b) ROC curve (AUC = {roc_auc_score(y_test, score):.4f})",
              fontsize=11, fontweight="bold", color=PALETTE["primary"])
ax2.set_xlim(0, 1)
ax2.set_ylim(0, 1.02)
ax2.grid(alpha=0.25, ls="--")
ax2.legend(fontsize=8.5, loc="lower right")
ax2.tick_params(labelsize=8.5)

fig.suptitle("Final model: precision-recall and ROC (AP = "
             f"{average_precision_score(y_test, score):.4f})",
             fontsize=12.5, fontweight="bold", color=PALETTE["primary"])
plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig(f"{CHARTS}/s7_pr_roc_operating_point.png", dpi=140,
            bbox_inches="tight", facecolor="white")
plt.close()
print("[saved] s7_pr_roc_operating_point.png")
