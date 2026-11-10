"""
features.py — Feature engineering (bước S3 của PIPELINE.md).

Mỗi feature mới đều được sinh ra từ một phát hiện cụ thể trong EDA, và phải
trả lời được câu hỏi "tại sao thêm feature này?" khi thầy hỏi.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import SEED


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sinh 5 feature mới từ Time và Amount.

    | Feature          | Công thức                        | Lý do (từ EDA)                          |
    |------------------|----------------------------------|------------------------------------------|
    | Hour_of_Day      | (Time/3600).astype(int) % 24     | Peak fraud rate ở giờ 2 (1.45%)          |
    | Day              | (Time/86400).astype(int)         | Day 0: 272 fraud vs Day 1: 201            |
    | Is_Night         | Hour ∈ {22..5}                   | Nhóm giờ thấp điểm gian lận              |
    | Amount_log       | log1p(Amount)                    | Amount right-skewed (max 25,691)         |
    | Is_Zero_Amount   | Amount == 0                      | 1,695 giao dịch 0 USD là pattern bất thường|

    KHÔNG thêm `Amount_z`: StandardScaler trong sklearn Pipeline (S4) đã làm
    đúng việc chuẩn hóa, thêm z-score thủ công sẽ gây tranh luận về data
    leakage mà không đem lại lợi ích gì.

    Lưu ý: hàm này KHÔNG dùng thống kê của tập test, nên an toàn khi gọi
    riêng lẻ trên train và test.
    """
    X = df.copy()

    X["Hour_of_Day"] = (X["Time"] / 3600).astype(int) % 24
    X["Day"] = (X["Time"] / 86400).astype(int)
    X["Is_Night"] = X["Hour_of_Day"].isin([22, 23, 0, 1, 2, 3, 4, 5]).astype(int)
    X["Amount_log"] = np.log1p(X["Amount"])
    X["Is_Zero_Amount"] = (X["Amount"] == 0).astype(int)

    return X


NEW_FEATURES = [
    "Hour_of_Day",
    "Day",
    "Is_Night",
    "Amount_log",
    "Is_Zero_Amount",
]


def mutual_information_table(X_train, y_train, top_n=20) -> pd.Series:
    """
    Kiểm chứng feature mới thực sự có tín hiệu (làm TRÊN TẬP TRAIN).

    Mutual information đo phụ thuộc phi tuyến giữa feature và target —
    phù hợp hơn tương quan Pearson cho các feature dạng số như Hour_of_Day.
    """
    from sklearn.feature_selection import mutual_info_classif

    mi = mutual_info_classif(
        X_train, y_train, random_state=SEED, n_neighbors=3, discrete_features=False
    )
    return (
        pd.Series(mi, index=X_train.columns)
        .sort_values(ascending=False)
        .head(top_n)
    )


def feature_evidence_chart(X_train, y_train, path):
    """
    Chart bằng chứng cho feature engineering (đưa vào report):
      (a) tỷ lệ fraud theo giờ
      (b) boxplot Amount_log theo class
      (c) heatmap tỷ lệ fraud theo giờ x ngày
    """
    import matplotlib.pyplot as plt
    import seaborn as sns

    from .config import PALETTE

    d = X_train.copy()
    d["_y"] = y_train.values

    fig, axes = plt.subplots(1, 3, figsize=(19, 5.5))

    # (a) fraud rate theo giờ
    rate = d.groupby("Hour_of_Day")["_y"].mean() * 100
    cnt = d.groupby("Hour_of_Day")["_y"].sum()
    ax = axes[0]
    ax.bar(rate.index, rate.values, color=PALETTE["danger"], alpha=0.85, edgecolor="white")
    ax2 = ax.twinx()
    ax2.plot(cnt.index, cnt.values, color=PALETTE["accent"], marker="o", lw=2, label="Fraud count")
    ax.set_xlabel("Hour of Day", fontsize=11)
    ax.set_ylabel("Fraud rate (%)", fontsize=11, color=PALETTE["danger"])
    ax2.set_ylabel("Fraud count", fontsize=11, color=PALETTE["accent"])
    ax.set_title("(a) Fraud rate by hour-of-day", fontsize=13, fontweight="bold",
                 color=PALETTE["primary"])
    peak = rate.idxmax()
    ax.annotate(f"peak: {peak}h ({rate.max():.3f}%)", xy=(peak, rate.max()),
                xytext=(peak + 2.5, rate.max() * 0.75), fontsize=10,
                color=PALETTE["danger"],
                arrowprops=dict(arrowstyle="->", color=PALETTE["danger"]))
    ax.grid(alpha=0.25, axis="y", linestyle="--")

    # (b) boxplot Amount_log
    ax = axes[1]
    data = [
        np.log1p(d.loc[d["_y"] == 0, "Amount"]),
        np.log1p(d.loc[d["_y"] == 1, "Amount"]),
    ]
    bp = ax.boxplot(data, labels=["Legitimate", "Fraud"], patch_artist=True,
                    widths=0.55, showfliers=False)
    for patch, color in zip(bp["boxes"], [PALETTE["primary"], PALETTE["danger"]]):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)
    ax.set_ylabel("log1p(Amount)", fontsize=11)
    ax.set_title("(b) Amount distribution by class", fontsize=13, fontweight="bold",
                 color=PALETTE["primary"])
    ax.grid(alpha=0.25, axis="y", linestyle="--")

    # (c) heatmap hour x day
    ax = axes[2]
    pivot = (
        d.pivot_table(index="Day", columns="Hour_of_Day", values="_y", aggfunc="mean")
        * 100
    )
    sns.heatmap(pivot, cmap="YlOrRd", annot=True, fmt=".2f", ax=ax,
                cbar_kws={"label": "Fraud rate (%)"}, linewidths=0.4)
    ax.set_title("(c) Fraud rate: hour x day", fontsize=13, fontweight="bold",
                 color=PALETTE["primary"])
    ax.set_xlabel("Hour of Day", fontsize=11)
    ax.set_ylabel("Day", fontsize=11)

    fig.suptitle(
        "Feature Engineering Evidence — Group 7, Data Mining (DA)",
        fontsize=15, fontweight="bold", color=PALETTE["primary"], y=1.02,
    )
    plt.tight_layout()
    plt.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"[features] chart saved -> {path}")
