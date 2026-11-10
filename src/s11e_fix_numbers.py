"""S11e · Sua 3 loi so lieu/logic phat hien o lan rà soát cuối.
1) Table 4 (4-Results): dong Decision Tree class_weight dung AUC-PR 0.7043 /
   AUC-ROC 0.9546 -> 0.7130 / 0.9003 (gia tri thuc te trong
   artifacts/tables/imbalance_benchmark.csv va khop voi
   artifacts/models/s5_predictions/dtree__class_weight__na.npy).
2) Table 11 (5-Cost): cot "% of all fraud caught" -> "% of all fraud in
   segment" va "Recall" -> "Recall in segment" (gia tri 39,4% / 9,9% la
   phan gian lan NAM TRONG segment, khong phai so gian lan model bat duoc).
3) Table 17 Q5 (5-Cost): sua cau cho dung nghia.
"""
from pathlib import Path

EDITS = []


def add(path, old, new, tag):
    EDITS.append((path, old, new, tag))


# --- 1) Table 4: dong Decision Tree
add("report/Sections/4-Results.tex",
    "Decision Tree & class\\_weight & --- & 0.7043 & 0.9546 & 0.7022 & 0.5563 & 0.9518 & \\$344.55 \\\\",
    "Decision Tree & class\\_weight & --- & 0.7130 & 0.9003 & 0.7022 & 0.5563 & 0.9518 & \\$344.55 \\\\",
    "T4: DT class_weight AUC-PR/AUC-ROC sai -> 0.7130 / 0.9003")

# --- 2) Table 11: nhan cot
add("report/Sections/5-Cost.tex",
    "\\textbf{Segment} & \\textbf{Transactions} & \\textbf{\\% of all} & \\textbf{Frauds} & \\textbf{\\% of all fraud caught} & \\textbf{Recall} \\\\",
    "\\textbf{Segment} & \\textbf{Transactions} & \\textbf{\\% of all} & \\textbf{Frauds} & \\textbf{\\% of all fraud in segment} & \\textbf{Recall in segment} \\\\",
    "T11: nhan cot sai nghia")

# --- 3) Table 11 caption
add("report/Sections/5-Cost.tex",
    """\\caption{Detection performance restricted to transactions above various
amount thresholds.}""",
    """\\caption{Detection performance restricted to transactions above various
amount thresholds. The fifth column is the share of all frauds that lie in the
segment; the sixth is the model's recall \\emph{within} the segment.}""",
    "T11: caption giai thich cot")

# --- 4) doan van ban sau Table 11
add("report/Sections/5-Cost.tex",
    """Restricting the model to large transactions is counter-productive. Filtering
above \\$500 discards 96.8\\% of the transaction stream in order to review only
9.9\\% of the fraud --- and even within that segment, recall falls to 0.7143.""",
    """Restricting the model to large transactions is counter-productive. Filtering
above \\$500 discards 96.8\\% of the transaction stream, and the 3.2\\% that
remains contains only 9.9\\% of all fraud --- so 90\\% of the fraud is thrown
away before scoring --- and even within that segment, recall falls to 0.7143.""",
    "T11: doan dien giai lai")

# --- 5) Table 17 Q5
add("report/Sections/5-Cost.tex",
    """5 & Score all transactions, or only those above an amount threshold? & \\textbf{Score all.} Filtering above \\$500 keeps only 3.2\\% of the traffic but catches just \\textbf{9.9\\%} of the fraud; roughly two thirds of the missed frauds are below \\$10 \\\\""",
    """5 & Score all transactions, or only those above an amount threshold? & \\textbf{Score all.} Only 3.2\\% of the traffic lies above \\$500, and it contains just \\textbf{9.9\\%} of all fraud --- an amount gate discards 90\\% of the fraud before scoring; roughly two thirds of the missed frauds are below \\$10 \\\\""",
    "T17 Q5: sua cho dung nghia")

# ------------------------------------------------------------------ apply
for path, old, new, tag in EDITS:
    p = Path(path)
    s = p.read_text(encoding="utf-8")
    if old not in s:
        print(f"[SKIP] {tag}")
        continue
    s = s.replace(old, new, 1)
    p.write_text(s, encoding="utf-8")
    print(f"[OK]   {tag}")
