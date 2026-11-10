"""
data.py — Load, clean, split và kiểm tra chất lượng dữ liệu.

Thứ tự BẮT BUỘC (xem PIPELINE.md bước S1):
    raw load  →  drop duplicates  →  STRATIFIED split  →  resample (chỉ trên train)

Sai thứ tự này (đặc biệt resample trước rồi mới split) sẽ làm mọi kết quả
về sau trở nên vô giá trị.
"""

from __future__ import annotations

import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from .config import (
    DATA_CSV,
    MODELS,
    SEED,
    N_DUPLICATES,
    N_ROWS_RAW,
)

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# LOAD
# ---------------------------------------------------------------------------


def load_raw() -> pd.DataFrame:
    """Đọc creditcard.csv và kiểm tra shape có đúng như kỳ vọng không."""
    df = pd.read_csv(DATA_CSV)
    if df.shape != (N_ROWS_RAW, 31):
        print(
            f"[WARNING] Shape = {df.shape}, expected {(N_ROWS_RAW, 31)}. "
            "Tiếp tục xử lý nhưng hãy kiểm tra lại file nguồn."
        )
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Loại bỏ dòng trùng lặp.

    Lý do: dataset gốc có 1.081 dòng trùng (1.062 ở class 0, 19 ở class 1).
    Giữ lại sẽ khiến mô hình overfit các mẫu lặp và làm lệch độ nhạy
    (recall) của lớp fraud. Vì dùng `stratify=y` nên tỷ lệ class không đổi.
    """
    n_before = len(df)
    df_clean = df.drop_duplicates().reset_index(drop=True)
    removed = n_before - len(df_clean)
    print(f"[clean] removed {removed} duplicate rows -> {df_clean.shape}")
    if removed != N_DUPLICATES:
        print(f"[WARNING] Expected {N_DUPLICATES} duplicates, got {removed}.")
    return df_clean


# ---------------------------------------------------------------------------
# SPLIT
# ---------------------------------------------------------------------------


def make_split(
    df_clean: pd.DataFrame,
    test_size: float = 0.30,
    seed: int = SEED,
):
    """
    Tách tập TRAIN/TEST với stratify theo target.

    - stratify=y : giữ tỷ lệ fraud ~0.17% trong CẢ HAI tập. Bắt buộc với
      imbalance 1:599 — nếu không, một tập có thể rất ít fraud.
    - random_state=seed : tái lập được.

    Ghi chú học thuật: Dal Pozzolo et al. (2014) và Leal-Avila et al. (2023)
    dùng đúng protocol stratified random split trên dataset này, nên ta
    theo cùng cách để kết quả so sánh được với literature.
    """
    X = df_clean.drop(columns=["Class"])
    y = df_clean["Class"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=seed
    )
    return X_train, X_test, y_train, y_test


def save_split(X_train, X_test, y_train, y_test, path=None) -> str:
    """Lưu split để MỌI notebook sau đó dùng chung — không notebook nào tự tách tập."""
    path = path or (MODELS / "split.joblib")
    joblib.dump(
        {"X_train": X_train, "X_test": X_test, "y_train": y_train, "y_test": y_test},
        path,
    )
    print(f"[split] saved -> {path}")
    return str(path)


def load_split(path=None) -> dict:
    """Nạp split đã lưu."""
    path = path or (MODELS / "split.joblib")
    if not path.exists():
        raise FileNotFoundError(
            f"{path} chưa tồn tại. Chạy notebook 00_setup_and_split.ipynb trước."
        )
    return joblib.load(path)


def print_split_summary(y_train, y_test) -> None:
    """In tỷ lệ class của từng tập để đối chiếu với kỳ vọng."""
    for name, yy in (("train", y_train), ("test", y_test)):
        fraud = int(yy.sum())
        legit = int((yy == 0).sum())
        print(
            f"{name:>5}: n={len(yy):>7,}  fraud={fraud:>4}  "
            f"rate={yy.mean() * 100:.4f}%  "
            f"imbalance=1:{legit // max(fraud, 1)}"
        )


# ---------------------------------------------------------------------------
# DATA QUALITY REPORT
# ---------------------------------------------------------------------------


def quality_report(df_raw: pd.DataFrame, df_clean: pd.DataFrame) -> pd.DataFrame:
    """Bảng kiểm tra chất lượng dữ liệu — đưa thẳng vào report."""
    dup = df_raw.duplicated()
    rows = {
        "check": [
            "shape_raw",
            "shape_clean",
            "missing_values_total",
            "duplicate_rows",
            "duplicates_in_legit",
            "duplicates_in_fraud",
            "fraud_count_clean",
            "legit_count_clean",
            "imbalance_ratio_1_to",
            "amount_negative",
            "amount_zero",
            "time_monotonic_increasing",
            "feature_count",
            "target_column",
        ],
        "value": [
            str(df_raw.shape),
            str(df_clean.shape),
            int(df_clean.isna().sum().sum()),
            int(dup.sum()),
            int((dup & (df_raw["Class"] == 0)).sum()),
            int((dup & (df_raw["Class"] == 1)).sum()),
            int((df_clean["Class"] == 1).sum()),
            int((df_clean["Class"] == 0).sum()),
            round(
                (df_clean["Class"] == 0).sum() / (df_clean["Class"] == 1).sum(), 1
            ),
            int((df_clean["Amount"] < 0).sum()),
            int((df_clean["Amount"] == 0).sum()),
            bool(df_clean["Time"].is_monotonic_increasing),
            int(df_clean.shape[1] - 1),
            "Class (0=legit, 1=fraud)",
        ],
    }
    return pd.DataFrame(rows)
