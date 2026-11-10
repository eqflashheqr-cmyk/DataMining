"""
evaluation.py — Metrics, threshold tuning, cost analysis và biểu đồ.

Tập trung vào hai điều:
  1. Đánh giá ĐÚNG cho dữ liệu mất cân bằng (Recall/Precision/F1/AUC-PR,
     không bao giờ dùng accuracy làm metric chính).
  2. Trả lời 7 câu hỏi kinh doanh của Nhóm 1/2/3 bằng SỐ LIỆU.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
    f1_score,
)

from .config import (
    CLASS_NAMES,
    COLORS,
    COST_PER_FN,
    COST_PER_FP,
    DATASET_DAYS,
    MIN_PRECISION,
    PALETTE,
    REFERENCE_TRANSACTIONS,
)


# ---------------------------------------------------------------------------
# METRICS
# ---------------------------------------------------------------------------


def evaluate(y_true, y_pred, y_score) -> dict:
    """Bộ metric đầy đủ cho một lần dự đoán."""
    return {
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "auc_roc": float(roc_auc_score(y_true, y_score)),
        "auc_pr": float(average_precision_score(y_true, y_score)),
        "n_pred_pos": int(np.sum(y_pred)),
        "n_true_pos": int(np.sum(y_true)),
    }


def confusion_counts(y_true, y_pred) -> dict:
    """Tách TN/FP/FN/TP từ confusion matrix."""
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}


# ---------------------------------------------------------------------------
# ACCURACY PARADOX — minh hoạ bằng số (dùng trong slide & Q&A)
# ---------------------------------------------------------------------------


def accuracy_paradox(y_test) -> dict:
    """
    Model "ngây thơ" dự đoán tất cả là hợp lệ:
      accuracy ≈ 99.83% nhưng recall = 0.
    Đây là lý do không dùng accuracy làm metric chính.
    """
    y_naive = np.zeros_like(y_test)
    return {
        "accuracy": float(accuracy_score(y_test, y_naive)),
        "recall": float(recall_score(y_test, y_naive, zero_division=0)),
        "precision": float(precision_score(y_test, y_naive, zero_division=0)),
        "f1": float(f1_score(y_test, y_naive, zero_division=0)),
    }


# ---------------------------------------------------------------------------
# THRESHOLD TUNING — trả lời câu hỏi kinh doanh #2
# ---------------------------------------------------------------------------


def find_threshold(y_true, y_score, min_precision: float = MIN_PRECISION):
    """
    Tìm ngưỡng có precision >= min_precision mà recall CAO NHẤT.

    Đây chính là câu hỏi kinh doanh số 2 của Nhóm 1:
      "Với precision tối thiểu 95% (block nhầm tối đa 5%), recall đạt
       được bao nhiêu?"
    """
    precision, recall, thresholds = precision_recall_curve(y_true, y_score)

    # thresholds tương ứng với precision[:-1], recall[:-1]
    best = None
    for i in range(len(thresholds)):
        if precision[i] >= min_precision:
            if best is None or recall[i] > best["recall"]:
                best = {
                    "threshold": float(thresholds[i]),
                    "precision": float(precision[i]),
                    "recall": float(recall[i]),
                    "f1": float(
                        2 * precision[i] * recall[i] / (precision[i] + recall[i])
                    ) if (precision[i] + recall[i]) > 0 else 0.0,
                }
    return best


def threshold_curve(y_true, y_score) -> pd.DataFrame:
    """Bảng trade-off recall / precision / cost theo từng threshold."""
    precision, recall, thresholds = precision_recall_curve(y_true, y_score)
    rows = []
    n_fraud = int(np.sum(y_true))
    for i, thr in enumerate(thresholds):
        p, r = precision[i], recall[i]
        tp = r * n_fraud
        fp = (tp / p) - tp if p > 0 else 0.0
        fn = n_fraud - tp
        rows.append(
            {
                "threshold": float(thr),
                "precision": float(p),
                "recall": float(r),
                "f1": float(2 * p * r / (p + r)) if (p + r) > 0 else 0.0,
                "tp": tp,
                "fp": max(fp, 0.0),
                "fn": max(fn, 0.0),
                "total_cost": float(fn * COST_PER_FN + fp * COST_PER_FP),
            }
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# COST ANALYSIS
# ---------------------------------------------------------------------------


def total_cost(y_true, y_pred) -> dict:
    """
    Tổng chi phí của một mô hình trên tập test.

      Total Cost = n_FN × Cost_per_FN + n_FP × Cost_per_FP
    """
    c = confusion_counts(y_true, y_pred)
    cost = c["fn"] * COST_PER_FN + c["fp"] * COST_PER_FP
    return {
        **c,
        "cost_fn": c["fn"] * COST_PER_FN,
        "cost_fp": c["fp"] * COST_PER_FP,
        "total_cost": float(cost),
        "cost_per_fraud_missed": COST_PER_FN,
        "cost_per_false_alarm": COST_PER_FP,
    }


def annualize(n_test: int, dataset_days: int = DATASET_DAYS) -> float:
    """Hệ số quy đổi từ khoảng thời gian dataset lên 1 năm."""
    return (365.0 / dataset_days) * (n_test / n_test)  # giữ nguyên logic minh bạch


def scale_to_reference(n_test: int, reference: int = REFERENCE_TRANSACTIONS) -> float:
    """Hệ số quy đổi từ tập test sang quy mô tham chiếu (per 1M transactions)."""
    return reference / n_test


def scenario_cost(
    n_txn_per_day: int,
    fraud_rate: float,
    recall: float,
    precision: float,
    review_cost: float = COST_PER_FP,
    fn_cost: float = COST_PER_FN,
    days: int = 365,
) -> dict:
    """
    Chi phí năm theo một kịch bản vận hành.

    Với mỗi ngày có n_txn_per_day giao dịch và tỷ lệ fraud fraud_rate:
      - số fraud thật/ngày   = n_txn_per_day × fraud_rate
      - số fraud bị bắt     = n_fraud × recall
      - số giao dịch bị flag = n_caught / precision
      - số false positive    = n_flagged − n_caught
      - chi phí năm          = (FN × fn_cost + FP × review_cost) × 365
    """
    n_fraud_day = n_txn_per_day * fraud_rate
    caught = n_fraud_day * recall
    flagged = caught / precision if precision > 0 else 0.0
    fp = flagged - caught
    fn = n_fraud_day - caught
    annual = (fn * fn_cost + fp * review_cost) * days
    return {
        "txn_per_day": n_txn_per_day,
        "fraud_rate": fraud_rate,
        "recall": recall,
        "precision": precision,
        "fraud_per_day": n_fraud_day,
        "caught_per_day": caught,
        "flagged_per_day": flagged,
        "fp_per_day": fp,
        "fn_per_day": fn,
        "annual_cost": annual,
    }


def scenario_table(
    fraud_rate: float,
    recalls=(0.70, 0.80, 0.90, 0.95),
    precisions=(0.95,),
    volumes=(100_000, 500_000, 1_000_000),
) -> pd.DataFrame:
    """Bảng kịch bản cho slide trả lời câu hỏi kinh doanh Nhóm 2 & 3."""
    rows = []
    for v in volumes:
        for r in recalls:
            for p in precisions:
                rows.append(scenario_cost(v, fraud_rate, r, p))
    return pd.DataFrame(rows)


def review_capacity_check(
    y_true, y_score, threshold: float, capacity: int = 100, days: int = DATASET_DAYS
) -> dict:
    """
    Câu hỏi Nhóm 2 số 4: nếu ngân hàng chỉ review được 100 giao dịch bị
    flag/ngày thì chi phí vận hành là bao nhiêu, có đủ không?
    """
    flagged_total = int(np.sum(y_score >= threshold))
    flagged_day = flagged_total / days
    over = flagged_day - capacity
    return {
        "threshold": float(threshold),
        "flagged_total_in_test": flagged_total,
        "flagged_per_day": flagged_day,
        "review_capacity_per_day": capacity,
        "utilisation": flagged_day / capacity if capacity else np.nan,
        "over_capacity": bool(over > 0),
        "over_by_per_day": max(over, 0.0),
        "daily_review_cost": capacity * COST_PER_FP,
        "annual_review_cost": capacity * COST_PER_FP * 365,
    }


def amount_threshold_analysis(
    y_true, y_pred, amount: pd.Series, thresholds=(50, 100, 200, 500)
) -> pd.DataFrame:
    """
    Câu hỏi Nhóm 2 số 5: nên chạy model trên MỌI giao dịch hay chỉ trên
    giao dịch vượt một ngưỡng tiền nào đó?
    """
    rows = []
    for thr in list(thresholds) + [None]:
        if thr is None:
            mask = np.ones(len(y_true), dtype=bool)
            label = "All transactions"
        else:
            mask = (amount.values > thr)
            label = f"Amount > ${thr}"
        y_t = np.asarray(y_true)[mask]
        y_p = np.asarray(y_pred)[mask]
        n_fraud = int(np.sum(y_t))
        rows.append(
            {
                "segment": label,
                "n_transactions": int(mask.sum()),
                "share_of_all_pct": float(mask.sum() / len(y_true) * 100),
                "n_fraud": n_fraud,
                "fraud_captured_pct": float(
                    n_fraud / np.sum(y_true) * 100
                ) if np.sum(y_true) else 0.0,
                "recall": float(recall_score(y_t, y_p, zero_division=0)) if n_fraud else 0.0,
                "precision": float(precision_score(y_t, y_p, zero_division=0)),
                "n_flagged": int(np.sum(y_p)),
            }
        )
    return pd.DataFrame(rows)


def measure_latency(pipeline, X, n_samples: int = 1000, repeats: int = 5) -> dict:
    """
    Câu hỏi Nhóm 3 số 6: đo latency thực tế để trả lời "nhân rộng được không?"
    """
    import time

    sample = X.head(n_samples)
    pipeline.predict(sample)  # warm-up

    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        pipeline.predict(sample)
        times.append((time.perf_counter() - t0) / n_samples * 1000)  # ms/transaction

    ms = float(np.mean(times))
    return {
        "ms_per_transaction": ms,
        "cpu_seconds_per_1M_txns": ms * 1_000_000 / 1000,
        "cpu_hours_per_1M_txns": ms * 1_000_000 / 1000 / 3600,
    }


# ---------------------------------------------------------------------------
# CHARTS
# ---------------------------------------------------------------------------


def plot_pr_roc(y_true, y_score, path, title_suffix: str = ""):
    """PR curve + ROC curve."""
    import matplotlib.pyplot as plt

    precision, recall, _ = precision_recall_curve(y_true, y_score)
    fpr, tpr, _ = roc_curve(y_true, y_score)
    auc_roc = roc_auc_score(y_true, y_score)
    auc_pr = average_precision_score(y_true, y_score)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))

    axes[0].plot(recall[::-1], precision[::-1], color=PALETTE["danger"], lw=2)
    axes[0].fill_between(recall[::-1], precision[::-1], color=PALETTE["danger"], alpha=0.12)
    axes[0].axhline(MIN_PRECISION, ls="--", color=PALETTE["warn"], lw=1.5,
                    label=f"Precision = {MIN_PRECISION:.0%} constraint")
    axes[0].set_xlabel("Recall", fontsize=11)
    axes[0].set_ylabel("Precision", fontsize=11)
    axes[0].set_title(f"Precision–Recall Curve  (AUC-PR = {auc_pr:.4f})",
                      fontsize=13, fontweight="bold", color=PALETTE["primary"])
    axes[0].legend(fontsize=9)
    axes[0].grid(alpha=0.25, linestyle="--")

    axes[1].plot(fpr, tpr, color=PALETTE["primary"], lw=2, label=f"AUC = {auc_roc:.4f}")
    axes[1].plot([0, 1], [0, 1], "k--", alpha=0.4, label="Random")
    axes[1].set_xlabel("False Positive Rate", fontsize=11)
    axes[1].set_ylabel("True Positive Rate", fontsize=11)
    axes[1].set_title(f"ROC Curve  (AUC = {auc_roc:.4f})", fontsize=13,
                      fontweight="bold", color=PALETTE["primary"])
    axes[1].legend(fontsize=9)
    axes[1].grid(alpha=0.25, linestyle="--")

    if title_suffix:
        fig.suptitle(title_suffix, fontsize=13, color=PALETTE["primary"])
    plt.tight_layout()
    plt.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"[eval] chart saved -> {path}")


def plot_confusion_matrix(y_true, y_pred, path, threshold: float = 0.5):
    """Confusion matrix đẹp, có chú thích tiếng Anh."""
    import matplotlib.pyplot as plt
    import seaborn as sns

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    fig, ax = plt.subplots(figsize=(6, 5.2))
    sns.heatmap(cm, annot=True, fmt=",d", cmap="Blues",
                xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES,
                annot_kws={"size": 15}, ax=ax, cbar_kws={"shrink": 0.8})
    ax.set_xlabel("Predicted", fontsize=12)
    ax.set_ylabel("Actual", fontsize=12)
    ax.set_title(f"Confusion Matrix  (threshold = {threshold:.4f})", fontsize=13,
                 fontweight="bold", color=PALETTE["primary"])
    plt.tight_layout()
    plt.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"[eval] chart saved -> {path}")


def plot_cost_tradeoff(curve: pd.DataFrame, path, best_threshold: float = None):
    """
    Trade-off curve: trục X = recall, trục Y = tổng chi phí.
    Mỗi điểm là một threshold → cho thấy "operating point" tối ưu.
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    ax.plot(curve["recall"], curve["total_cost"], color=PALETTE["primary"], lw=2)
    ax.scatter(curve["recall"], curve["total_cost"], s=8,
               color=PALETTE["accent"], alpha=0.6)

    if best_threshold is not None:
        row = curve.iloc[(curve["threshold"] - best_threshold).abs().argmin()]
        ax.scatter(row["recall"], row["total_cost"], s=180, marker="*",
                   color=PALETTE["danger"], zorder=5,
                   label=f"Chosen threshold = {best_threshold:.4f}")
        ax.annotate(
            f"recall {row['recall']:.1%}\nprecision {row['precision']:.1%}",
            xy=(row["recall"], row["total_cost"]),
            xytext=(row["recall"] + 0.08, row["total_cost"]),
            fontsize=10, color=PALETTE["danger"],
            arrowprops=dict(arrowstyle="->", color=PALETTE["danger"]),
        )
    ax.set_xlabel("Recall (fraud caught)", fontsize=11)
    ax.set_ylabel("Total cost on test set (USD)", fontsize=11)
    ax.set_title("Cost–Recall Trade-off", fontsize=13, fontweight="bold",
                 color=PALETTE["primary"])
    ax.legend(fontsize=9)
    ax.grid(alpha=0.25, linestyle="--")
    plt.tight_layout()
    plt.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"[eval] chart saved -> {path}")


def plot_scenario_cost(scen: pd.DataFrame, path):
    """Chi phí năm theo số giao dịch/ngày, một đường cho mỗi mức recall."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for rec, grp in scen.groupby("recall"):
        grp = grp.sort_values("txn_per_day")
        ax.plot(grp["txn_per_day"], grp["annual_cost"], marker="o", lw=2,
                label=f"recall = {rec:.0%}")
    ax.set_xlabel("Transactions per day", fontsize=11)
    ax.set_ylabel("Annual cost of fraud (USD)", fontsize=11)
    ax.set_title("Scenario Analysis — Annual Cost vs. Transaction Volume",
                 fontsize=13, fontweight="bold", color=PALETTE["primary"])
    ax.legend(fontsize=9)
    ax.grid(alpha=0.25, linestyle="--")
    ax.ticklabel_format(axis="y", style="plain")
    plt.tight_layout()
    plt.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"[eval] chart saved -> {path}")


# ---------------------------------------------------------------------------
# BIỂU ĐỒ BỔ SUNG CHO S6
# ---------------------------------------------------------------------------


def plot_pr_overlay(y_true, score_map: dict, path, title="Precision–Recall Curve"):
    """
    Vẽ nhiều PR curve chồng lên nhau để so sánh các model.

    score_map: {tên_model: y_score}
    """
    import matplotlib.pyplot as plt
    from sklearn.metrics import average_precision_score, precision_recall_curve

    fig, ax = plt.subplots(figsize=(8.5, 6))
    for i, (name, score) in enumerate(score_map.items()):
        precision, recall, _ = precision_recall_curve(y_true, score)
        ap = average_precision_score(y_true, score)
        ax.plot(recall, precision, lw=2, label=f"{name}  (AUC-PR = {ap:.4f})",
                color=COLORS[i % len(COLORS)])

    ax.axhline(MIN_PRECISION, ls="--", color=PALETTE["warn"], lw=1.5,
               label=f"Precision constraint = {MIN_PRECISION:.0%}")
    ax.set_xlabel("Recall (fraud caught)", fontsize=11)
    ax.set_ylabel("Precision", fontsize=11)
    ax.set_title(title, fontsize=13, fontweight="bold", color=PALETTE["primary"])
    ax.legend(fontsize=9, loc="lower left")
    ax.grid(alpha=0.25, linestyle="--")
    plt.tight_layout()
    plt.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"[eval] chart saved -> {path}")


def plot_roc_overlay(y_true, score_map: dict, path, title="ROC Curve"):
    """Vẽ nhiều ROC curve chồng lên nhau."""
    import matplotlib.pyplot as plt
    from sklearn.metrics import roc_auc_score, roc_curve

    fig, ax = plt.subplots(figsize=(7.5, 6))
    for i, (name, score) in enumerate(score_map.items()):
        fpr, tpr, _ = roc_curve(y_true, score)
        auc = roc_auc_score(y_true, score)
        ax.plot(fpr, tpr, lw=2, label=f"{name}  (AUC = {auc:.4f})",
                color=COLORS[i % len(COLORS)])

    ax.plot([0, 1], [0, 1], "k--", alpha=0.4, label="Random")
    ax.set_xlabel("False Positive Rate", fontsize=11)
    ax.set_ylabel("True Positive Rate", fontsize=11)
    ax.set_title(title, fontsize=13, fontweight="bold", color=PALETTE["primary"])
    ax.legend(fontsize=9, loc="lower right")
    ax.grid(alpha=0.25, linestyle="--")
    plt.tight_layout()
    plt.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"[eval] chart saved -> {path}")


def plot_reliability(y_true, score, path, n_bins: int = 10,
                     label="Model"):
    """
    Reliability diagram — đo mức ĐỘ TIN CẬY của xác suất dự đoán.

    Nếu xác suất dự đoán đáng tin (well-calibrated), đường cong nằm sát
    đường chéo. Đây là điều kiện tiên quyết để dùng threshold trực tiếp
    như một "xác suất rủi ro" mà ngân hàng có thể hiểu được.
    """
    import matplotlib.pyplot as plt
    from sklearn.calibration import calibration_curve

    prob_true, prob_pred = calibration_curve(y_true, score, n_bins=n_bins,
                                             strategy="quantile")
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot([0, 1], [0, 1], "k--", alpha=0.4, label="Perfect calibration")
    ax.plot(prob_pred, prob_true, marker="o", lw=2, color=PALETTE["primary"],
            label=label)
    ax.set_xlabel("Mean predicted probability", fontsize=11)
    ax.set_ylabel("Observed fraud rate", fontsize=11)
    ax.set_title("Reliability Diagram", fontsize=13, fontweight="bold",
                 color=PALETTE["primary"])
    ax.legend(fontsize=9)
    ax.grid(alpha=0.25, linestyle="--")
    plt.tight_layout()
    plt.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"[eval] chart saved -> {path}")
