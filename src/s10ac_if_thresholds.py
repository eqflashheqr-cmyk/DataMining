"""S10ac · Isolation Forest:
(1) Table 4 -- F1 0.2877 do o o contamination threshold (143 flagged), khong
    phai o nguong P95 (IF khong dat P95) va khong phai o 0.5. Ghi ro.
(2) §4.3 -- thu nhan rang nguong cua IF duoc tinh tren test-score quantile
    (dang leakage) va noi ro 3.521 la nguong 0.5 mac dinh chu khong phai
    nguong contamination (loi §1.7)."""
from pathlib import Path

# --- 1. Table 4 note ---
p4 = Path("report/Sections/4-Results.tex")
s4 = p4.read_text(encoding="utf-8")

OLD4 = """Regression, Decision Tree and Random Forest only. Isolation Forest was run
without resampling only, and it does not reach the 95\\% precision constraint at
any usable threshold, so its constrained columns are left empty; its F1 is
measured at the default 0.5 threshold, where it flags 3{,}521 transactions.
\\end{table}"""

NEW4 = """Regression, Decision Tree and Random Forest only. Isolation Forest was run
without resampling only, and it does not reach the 95\\% precision constraint at
any usable threshold, so its constrained columns are left empty. Its F1 of
0.2877 is measured at its own contamination threshold (143 flagged
transactions, precision 0.2867, recall 0.2887), not at a 95\\%-precision
threshold; at the default 0.5 threshold the same model flags 3{,}521
transactions to reach 81.7\\% recall.
\\end{table}"""

if OLD4 not in s4:
    raise SystemExit("table4 anchor not found")
s4 = s4.replace(OLD4, NEW4, 1)
p4.write_text(s4, encoding="utf-8")
print("[ok] Table 4 IF note clarified")

# --- 2. §4.3 paragraph ---
p4b = Path("report/Sections/4-Results.tex")
s4b = p4b.read_text(encoding="utf-8")

OLD43 = """\\paragraph*{Unsupervised detection is not operationally viable.}
Isolation Forest attains Average Precision 0.1763 and AUC-ROC 0.9407. The
latter looks respectable, which illustrates precisely why ROC is the wrong
metric on this data. Operationally, however, Isolation Forest is unusable as a
decision system: at a threshold that flags only 0.167\\% of transactions --- the
same rate as the fraud prevalence --- it catches only 28.9\\% of frauds with a
precision of 28.7\\%, and to reach 81.7\\% recall it must flag 3{,}521
transactions (roughly thirty times the workload of the supervised model at the
default 0.5 threshold). Unsupervised detection is useful as a supplementary
monitoring signal, not as a decision system."""

NEW43 = """\\paragraph*{Unsupervised detection is not operationally viable.}
Isolation Forest attains Average Precision 0.1763 and AUC-ROC 0.9407. The
latter looks respectable, which illustrates precisely why ROC is the wrong
metric on this data. Operationally, however, Isolation Forest is unusable as a
decision system: at a threshold that flags only 0.167\\% of transactions --- the
same rate as the fraud prevalence --- it catches only 28.9\\% of frauds with a
precision of 28.7\\%, and to reach 81.7\\% recall it must flag 3{,}521
transactions, roughly thirty times the workload of the supervised model. The
two figures come from two different thresholds, and we label them because the
distinction is easy to blur: the contamination threshold (143 flagged
transactions) gives the 28.9\\% recall, while the 3{,}521 figure corresponds to
the default 0.5 score threshold. We note also that this model's threshold is a
quantile of the \emph{test} anomaly scores, so it carries the same
threshold-leakage caveat as the supervised operating points --- the caveat does
not change the conclusion, since the model is unviable by a wide margin either
way. Unsupervised detection is useful as a supplementary monitoring signal,
not as a decision system."""

if OLD43 not in s4b:
    raise SystemExit("sec43 anchor not found")
s4b = s4b.replace(OLD43, NEW43, 1)
p4b.write_text(s4b, encoding="utf-8")
print("[ok] §4.3 IF thresholds labelled + leakage disclosed")
