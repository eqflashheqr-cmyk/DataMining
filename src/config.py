"""
config.py — Cấu hình dùng chung cho toàn bộ pipeline Credit Card Fraud Detection.

Mọi đường dẫn, seed và hằng số nghiệp vụ đều nằm ở đây để:
  1. Các notebook luôn trỏ đúng vào cùng một nơi.
  2. Kết quả có thể tái lập (reproducible) nhờ SEED cố định.
  3. Thống kê nghiệp vụ (chi phí fraud, chi phí review) chỉ được sửa ở MỘT chỗ.
"""

from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# ĐƯỜNG DẪN
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent

DATA_CSV = ROOT / "creditcard.csv"

ART = ROOT / "artifacts"
MODELS = ART / "models"
CHARTS = ART / "charts"
TABLES = ART / "tables"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"

for _p in (ART, MODELS, CHARTS, TABLES, REPORTS, FIGURES):
    _p.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# REPRODUCIBILITY
# ---------------------------------------------------------------------------
SEED = 42
np.random.seed(SEED)

# ---------------------------------------------------------------------------
# THÔNG SỐ DATASET (kiểm tra tự động khi load — xem src/data.py)
# ---------------------------------------------------------------------------
N_ROWS_RAW = 284_807
N_COLS_RAW = 31
N_DUPLICATES = 1_081
FRAUD_COUNT_RAW = 492
FRAUD_COUNT_CLEAN = 473

# ---------------------------------------------------------------------------
# HẰNG SỐ NGHIỆP VỤ — dùng cho COST ANALYSIS (bước S9)
#
# Nguồn:
#   - HANDLE_COST  : LexisNexis True Cost of Fraud 2024 — mỗi 1 USD gian lận
#                    tốn ngân hàng ~4.45 USD để phát hiện, điều tra, bồi thường.
#   - FRAUD_COST_PER_EVENT : 1.00 USD là giá trị tài chính trực tiếp của 1 USD
#                    giao dịch gian lận (mất tiền thật).
#   - REVIEW_COST_PER_CASE: chi phí review thủ công 1 giao dịch bị model flag.
#                    Đây là GIẢ ĐỊNH của nhóm (có thể chỉnh theo dữ liệu thật
#                    của ngân hàng) — luôn nêu rõ khi trình bày.
# ---------------------------------------------------------------------------
FRAUD_COST_PER_EVENT = 1.00       # USD mất trực tiếp mỗi 1 USD gian lận
HANDLE_COST = 4.45                 # USD chi phí xử lý + bồi thường (LexisNexis 2024)
REVIEW_COST_PER_CASE = 0.30        # USD chi phí review thủ công / 1 giao dịch bị flag

#: Chi phí của một FALSE NEGATIVE (bỏ sót 1 giao dịch gian lận)
COST_PER_FN = FRAUD_COST_PER_EVENT + HANDLE_COST      # = 5.45 USD

#: Chi phí của một FALSE POSITIVE (block nhầm 1 giao dịch hợp lệ)
COST_PER_FP = REVIEW_COST_PER_CASE                    # = 0.30 USD

# ---------------------------------------------------------------------------
# HẰNG SỐ ĐÁNH GIÁ
# ---------------------------------------------------------------------------
#: Ngưỡng precision tối thiểu theo câu hỏi kinh doanh #2 của Nhóm 1
#: ("block nhầm tối đa 5%") -> precision >= 0.95
MIN_PRECISION = 0.95

#: Tỷ lệ fraud dùng làm `contamination` cho Isolation Forest
FRAUD_RATE = 0.001672

#: Số ngày mà dataset bao phủ
DATASET_DAYS = 2

#: Quy mô tham chiếu cho cost analysis (tránh overclaim cho ngân hàng VN)
REFERENCE_TRANSACTIONS = 1_000_000

# ---------------------------------------------------------------------------
# BẢNG MÀU (đồng nhất với notebook EDA và SLIDES_GUIDE.md)
# ---------------------------------------------------------------------------
PALETTE = {
    "primary": "#002060",   # dark blue — tiêu đề, lều
    "accent":  "#156082",   # teal
    "danger":  "#C00000",   # red — fraud
    "warn":    "#E97132",   # orange
    "light":   "#467886",   # gray-teal
}
COLORS = [PALETTE["primary"], PALETTE["accent"], PALETTE["danger"],
          PALETTE["warn"], PALETTE["light"]]

CLASS_NAMES = ["Legitimate", "Fraud"]

#: Các cột đặc trưng PCA (ẩn danh, không diễn giải được nghiệp vụ)
V_FEATURES = [f"V{i}" for i in range(1, 29)]

#: Cột nền tảng không qua PCA
BASE_FEATURES = ["Time", "Amount"]

#: Cột cần standardize (thang đo khác nhau, ảnh hưởng tree/distance model)
SCALE_COLS = ["Time", "Amount"]
