"""S10v · Figure 3 (PR/ROC): đánh dấu CẢ HAI operating point -- 0.52 (test-tuned,
lạc quan) và 0.65 (out-of-fold, leakage-free). Sửa lỗi §5.2: caption cũ chỉ
nêu 0.52 nên đánh dấu điểm lạc quan là 'bẫy' cho giảng viên phản biện.
Ghi ra artifacts/charts/ và copy sang report/Images/charts/.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import average_precision_score, precision_recall_curve, roc_auc_score, roc_curve

from src.config import PALETTE

ART = "artifacts/charts"
DST = "report/Images/charts"

sp = joblib.load("artifacts/models/split_with_features.joblib")
y_test = np.asarray(sp["y_test"]).astype(int)
score = np.load("artifacts/models/s5_predictions/FINAL_y_score_test.npy")


def stats(thr: float):
    pred = (score >= thr).astype(int)
    tp = int(((pred == 1) & (y_test == 1)).sum())
    fp = int(((pred == 1) & (y_test == 0)).sum())
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / int((y_test == 1).sum())
    return p, r


p52, r52 = stats(0.52)
p65, r65 = stats(0.65)
print(f"thr 0.52 -> P {p52:.4f} R {r52:.4f}")
print(f"thr 0.65 -> P {p65:.4f} R {r65:.4f}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.0))

prec, rec, _ = precision_recall_curve(y_test, score)
ax1.plot(rec, prec, lw=2.0, color=PALETTE["primary"], label="RF + SMOTE (1:100)")
ax1.axhline(0.95, color=PALETTE["danger"], ls="--", lw=1.6,
            label="95% precision floor")
ax1.scatter([r52], [p52], color=PALETTE["danger"], zorder=6, s=80, marker="D")
ax1.annotate(f"Test-tuned thr = 0.52\nP {p52*100:.1f}%, R {r52*100:.1f}%",
             (r52, p52), xytext=(0.20, 0.78), fontsize=9,
             color=PALETTE["danger"],
             arrowprops=dict(arrowstyle="->", color=PALETTE["danger"], lw=1.3))
ax1.scatter([r65], [p65], color=PALETTE["accent"], zorder=6, s=80, marker="o")
ax1.annotate(f"Out-of-fold thr = 0.65\nP {p65*100:.1f}%, R {r65*100:.1f}%",
             (r65, p65), xytext=(0.34, 0.90), fontsize=9,
             color=PALETTE["accent"],
             arrowprops=dict(arrowstyle="->", color=PALETTE["accent"], lw=1.3))
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
plt.savefig(f"{ART}/s7_pr_roc_operating_point.png", dpi=140,
            bbox_inches="tight", facecolor="white")
plt.close()
shutil.copy(f"{ART}/s7_pr_roc_operating_point.png",
            f"{DST}/s7_pr_roc_operating_point.png")
print("[saved] s7_pr_roc_operating_point.png (both operating points marked)")
