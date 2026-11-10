"""
modeling.py — Định nghĩa pipeline, 5 mô hình và benchmark kỹ thuật imbalance.

Nguyên tắc bất di bất dịch:
  - Scaler và resampler LUÔN nằm TRONG Pipeline → tự động fit trên train mỗi
    fold, không bao giờ chạm vào test set.
  - Isolation Forest không dùng cùng cơ chế (không có predict_proba, không
    có class_weight) nên được xử lý riêng.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.tree import DecisionTreeClassifier

# imblearn >= 0.14 đã đổi tên module `combined` -> `combine`
try:
    from imblearn.combine import SMOTEENN
except ImportError:  # fallback cho imblearn < 0.14
    from imblearn.combined import SMOTEENN
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.under_sampling import RandomUnderSampler

from .config import FRAUD_RATE, SCALE_COLS, SEED

#: Tỷ lệ lớp thiểu số sau resampling (1 fraud : 10 legit) — cấu hình chính.
#: Chọn 1:10 thay vì 1:1 vì 1:1 sẽ tạo ~198K mẫu giả → chậm và nhiễu.
DEFAULT_SAMPLING_STRATEGY = 0.1

warnings.filterwarnings("ignore")


# ---------------------------------------------------------------------------
# PREPROCESSING
# ---------------------------------------------------------------------------


def make_preprocessor(
    scaler: str = "standard", feature_cols: list[str] | None = None
) -> ColumnTransformer:
    """
    Chỉ scale Time và Amount. V1–V28 đã là output của PCA nên đã chuẩn hóa
    sẵn (mean ≈ 0, std ≈ 1) — scale lại chúng là vô nghĩa.

    `feature_cols` : danh sách TẤT CẢ cột đầu vào. Các cột còn lại được giữ
    nguyên (passthrough). Bắt buộc phải truyền vào khi dùng `remainder="drop"`
    mặc định — nếu không, ColumnTransformer không biết cột nào là "phần còn
    lại".
    """
    sc = StandardScaler() if scaler == "standard" else RobustScaler()

    if scaler == "none":
        # Biến thể đối chứng: KHÔNG scale. Dùng để chứng minh scale có cần thiết
        # hay không (câu hỏi Q&A kinh điển: "why do you scale?").
        return ColumnTransformer(
            transformers=[("pass", "passthrough", list(feature_cols or SCALE_COLS))],
            remainder="drop",
            verbose_feature_names_out=False,
        )

    if feature_cols is None:
        # Fallback: dùng toàn bộ cột ngoài SCALE_COLS làm passthrough
        return ColumnTransformer(
            transformers=[
                ("scale", sc, SCALE_COLS),
                ("pass", "passthrough", "remainder"),
            ],
            remainder="passthrough",
            verbose_feature_names_out=False,
        )

    pass_cols = [c for c in feature_cols if c not in SCALE_COLS]
    return ColumnTransformer(
        transformers=[
            ("scale", sc, SCALE_COLS),
            ("pass", "passthrough", pass_cols),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


# ---------------------------------------------------------------------------
# IMBALANCE SAMPLERS
# ---------------------------------------------------------------------------


def make_sampler(technique: str, strategy=None):
    """
    Trả về sampler hoặc None.

    technique:
      "none"        — không resample
      "undersample" — RandomUnderSampler
      "smote"       — SMOTE
      "smoteenn"    — SMOTE + ENN
      "class_weight"— không resample, xử lý ở tầng model

    Về `sampling_strategy` (float trong (0,1]):
      - SMOTE: tỷ lệ lớp thiểu số SAU khi oversample so với lớp đa số
        → strategy=0.1 nghĩa là 1 fraud : 10 legit.
      - RandomUnderSampler: tỷ lệ lớp thiểu số (giữ nguyên) so với lớp đa
        số SAU khi rút bớt → strategy=0.1 cũng nghĩa là 1 fraud : 10 legit.
      → Cả hai cùng dẫn tới tỷ lệ 1:10, giúp so sánh công bằng.
    """
    if technique in ("none", "class_weight"):
        return None

    if strategy is None:
        strategy = DEFAULT_SAMPLING_STRATEGY

    if technique == "undersample":
        # Giữ toàn bộ lớp fraud (331 dòng), rút lớp legit xuống cùng tỷ lệ
        return RandomUnderSampler(sampling_strategy=strategy, random_state=SEED)
    if technique == "smote":
        return SMOTE(sampling_strategy=strategy, random_state=SEED)
    if technique == "smoteenn":
        return SMOTEENN(sampling_strategy=strategy, random_state=SEED)
    raise ValueError(f"Unknown technique: {technique}")


# ---------------------------------------------------------------------------
# MODELS
# ---------------------------------------------------------------------------


def make_estimator(model: str, class_weight="balanced"):
    """Tạo estimator gốc (chưa bọc trong pipeline)."""
    if model == "logreg":
        return LogisticRegression(
            max_iter=1000, class_weight=class_weight, random_state=SEED, n_jobs=None
        )
    if model == "dtree":
        return DecisionTreeClassifier(
            class_weight=class_weight, random_state=SEED
        )
    if model == "rf":
        return RandomForestClassifier(
            n_estimators=300, class_weight=class_weight,
            random_state=SEED, n_jobs=-1,
        )
    if model == "xgb":
        from xgboost import XGBClassifier

        return XGBClassifier(
            n_estimators=300, learning_rate=0.1, max_depth=6,
            tree_method="hist", eval_metric="aucpr",
            scale_pos_weight=1.0, random_state=SEED, n_jobs=-1,
            enable_categorical=False,
        )
    if model == "iforest":
        return IsolationForest(
            contamination=FRAUD_RATE, n_estimators=300, random_state=SEED, n_jobs=-1
        )
    raise ValueError(f"Unknown model: {model}")


# ---------------------------------------------------------------------------
# PIPELINE ASSEMBLY
# ---------------------------------------------------------------------------


def make_pipeline(
    model: str,
    imbalance: str = "none",
    sampler_strategy=None,
    scaler: str = "standard",
    class_weight="balanced",
    feature_cols: list[str] | None = None,
) -> Pipeline:
    """
    Pipeline: preprocess → (resample) → classify.

    - Nếu imbalance == "class_weight": không resample, thay vào đó truyền
      class_weight="balanced" cho estimator.
    - Nếu imbalance == "none": dùng class_weight=None (baseline thuần, để
      đo được hiệu quả thật của imbalance).
    - feature_cols: danh sách cột đầu vào — BẮT BUỘC truyền vào để
      ColumnTransformer biết cột nào passthrough.
    """
    steps = [("preprocess", make_preprocessor(scaler, feature_cols))]

    sampler = make_sampler(imbalance, sampler_strategy)
    if sampler is not None:
        steps.append(("resample", sampler))

    if imbalance == "class_weight":
        cw = class_weight
    elif imbalance == "none":
        cw = None
    else:
        cw = None  # đã cân bằng bằng resample, không cần class_weight

    steps.append(("clf", make_estimator(model, class_weight=cw)))

    # BẮT BUỘC dùng imblearn.pipeline.Pipeline khi có bước resample.
    # sklearn.pipeline.Pipeline sẽ raise TypeError vì SMOTE không phải
    # transformer (nó không có .transform()).
    # imblearn.Pipeline cũng lo việc resample lại trong TỪNG fold của CV —
    # đây chính là điều kiện bắt buộc để tránh data leakage trong CV.
    if len(steps) > 2:
        return ImbPipeline(steps)
    return Pipeline(steps)


#: Danh sách model dùng trong benchmark
MODELS = ["logreg", "dtree", "rf", "xgb", "iforest"]

#: Danh sách kỹ thuật imbalance (iforest chỉ dùng "none" vì unsupervised)
IMBALANCE_TECHNIQUES = ["none", "undersample", "smote", "smoteenn", "class_weight"]

MODEL_LABELS = {
    "logreg": "Logistic Regression",
    "dtree": "Decision Tree",
    "rf": "Random Forest",
    "xgb": "XGBoost",
    "iforest": "Isolation Forest",
}

IMBALANCE_LABELS = {
    "none": "No resampling",
    "undersample": "Random Undersampling",
    "smote": "SMOTE",
    "smoteenn": "SMOTE + ENN",
    "class_weight": "class_weight=balanced",
}


def allowed_imbalances(model: str) -> list[str]:
    """Isolation Forest là unsupervised → không resample, không class_weight."""
    if model == "iforest":
        return ["none"]
    return IMBALANCE_TECHNIQUES


# ---------------------------------------------------------------------------
# ISOLATION FOREST — đánh giá riêng
# ---------------------------------------------------------------------------


def fit_isolation_forest(
    X_train, y_train, X_test, y_test, scaler="standard", feature_cols=None
):
    """
    Isolation Forest không dùng Pipeline chuẩn vì:
      - không có predict_proba → phải dùng score_samples()
      - không có predict theo nhãn 0/1 mặc định (predict trả -1/1)
      - nhãn -1 = anomaly, 1 = normal (ngược với Class)

    Ta chấp nhận điều này và chuyển đổi thủ công.
    """
    pre = make_preprocessor(scaler, feature_cols=feature_cols or list(X_train.columns))
    Xtr = pre.fit_transform(X_train)
    Xte = pre.transform(X_test)

    iso = make_estimator("iforest")
    iso.fit(Xtr)

    # score_samples: điểm càng thấp (= âm hơn) càng bất thường
    score_te = iso.score_samples(Xte)
    # anomaly score dương: càng lớn càng bất thường
    anomaly_te = -score_te

    # Ngưỡng: dùng đúng tỷ lệ fraud của tập train
    thr = np.quantile(anomaly_te, 1 - FRAUD_RATE)
    y_pred = (anomaly_te >= thr).astype(int)

    # AUC dùng score liên tục
    from sklearn.metrics import average_precision_score, roc_auc_score

    return {
        "y_pred": y_pred,
        "y_score": anomaly_te,
        "threshold": float(thr),
        "auc_roc": float(roc_auc_score(y_test, anomaly_te)),
        "auc_pr": float(average_precision_score(y_test, anomaly_te)),
    }, iso, pre


def clone_pipeline(pipe: Pipeline) -> Pipeline:
    """Clone pipeline (dùng trong GridSearchCV / CV lặp)."""
    return clone(pipe)


# ---------------------------------------------------------------------------
# CROSS-VALIDATION — dùng để chọn cấu hình mà KHÔNG chạm vào test set
# ---------------------------------------------------------------------------


def cv_evaluate(
    pipe: Pipeline,
    X_tr,
    y_tr,
    X_te,
    y_te,
    n_splits: int = 5,
    seed: int = SEED,
    scoring: str = "average_precision",
) -> dict:
    """
    Đánh giá bằng Stratified k-Fold CV trên TẬP TRAIN, rồi đánh giá MỘT LẦN
    trên tập test.

    Quy trình đúng (tránh overfit test set):
      1. CV trên train → ước lượng hiệu năng kỳ vọng
      2. Fit lại trên toàn bộ train
      3. Đánh giá 1 lần duy nhất trên test → đây là con số báo cáo

    Với imblearn.Pipeline, SMOTE được fit LẠI trong từng fold → không rò rỉ.
    """
    from sklearn.model_selection import StratifiedKFold, cross_val_score

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    scores = cross_val_score(pipe, X_tr, y_tr, cv=skf, scoring=scoring, n_jobs=1)

    pipe.fit(X_tr, y_tr)
    y_pred = pipe.predict(X_te)
    y_score = pipe.predict_proba(X_te)[:, 1]

    from .evaluation import evaluate

    return {
        "cv_score_mean": float(scores.mean()),
        "cv_score_std": float(scores.std()),
        **evaluate(y_te, y_pred, y_score),
    }


def compare_configs(
    configs: dict,
    X_tr,
    y_tr,
    X_te,
    y_te,
    n_splits: int = 5,
    seed: int = SEED,
) -> pd.DataFrame:
    """
    So sánh nhiều cấu hình pipeline trên cùng một split.

    configs: {tên_cấu_hình: pipeline}
    Trả về DataFrame có cv_score_mean (chọn cấu hình) và metric trên test.
    """
    rows = []
    for name, pipe in configs.items():
        res = cv_evaluate(pipe, X_tr, y_tr, X_te, y_te, n_splits=n_splits, seed=seed)
        rows.append({"config": name, **res})
        print(
            f"  {name:<42s} CV-AP={res['cv_score_mean']:.4f} "
            f"test P={res['precision']:.3f} R={res['recall']:.3f} "
            f"F1={res['f1']:.3f} AP={res['auc_pr']:.4f}"
        )
    return pd.DataFrame(rows)
