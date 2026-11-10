"""S10 · Áp dụng các chỉnh sửa còn lại vào report LaTeX (những đoạn có ký tự \\)."""
from pathlib import Path

R = Path("report/Sections")


def patch(fname, pairs):
    p = R / fname
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if old not in s:
            raise SystemExit(f"!! NOT FOUND in {fname}:\n{old[:200]}")
        if s.count(old) != 1:
            raise SystemExit(f"!! NOT UNIQUE in {fname} ({s.count(old)}):\n{old[:200]}")
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print(f"[ok] {fname} ({len(pairs)} edits)")


# ---------------------------------------------------------------------------
# 4-Results.tex · Table "over-searching"
# ---------------------------------------------------------------------------
patch("4-Results.tex", [(
    r"""\caption{Effect of expanding the hyper-parameter search. Cross-validated
Average Precision rises slightly while test performance stagnates or degrades.}
\label{tab:refine}
\begin{tabular}{p{2.9cm}p{2.6cm}rrrrr}
\toprule
\textbf{Model} & \textbf{Grid} & \textbf{CV-AP} & \textbf{Test AUC-PR} & \textbf{F1@0.5} & \textbf{Recall@P95} & \textbf{Time} \\
\midrule
Random Forest & S5 (baseline) & 0.8536 & \textbf{0.8239} & \textbf{0.8605} & \textbf{0.7817} & 368 s \\
Random Forest & S6 (refined) & \textbf{0.8547} & 0.8234 & 0.8605 & 0.7817 & 2{,}448 s \\
XGBoost & S5 (baseline) & 0.8653 & \textbf{0.8244} & \textbf{0.8425} & \textbf{0.7535} & 19 s \\
XGBoost & S6 (refined) & \textbf{0.8689} & 0.8198 & 0.8295 & 0.7465 & 148 s \\
\bottomrule
\end{tabular}
\end{table}""",
    r"""\caption{Effect of expanding the hyper-parameter search. Cross-validated
Average Precision rises slightly while test performance stagnates or degrades.
The CV-AP column is the best cross-validated score found by
\texttt{GridSearchCV} within the grid.}
\label{tab:refine}
\begin{tabular}{p{2.9cm}p{2.6cm}rrrrr}
\toprule
\textbf{Model} & \textbf{Grid} & \textbf{CV-AP} & \textbf{Test AUC-PR} & \textbf{F1@P95} & \textbf{Recall@P95} & \textbf{Time} \\
\midrule
Random Forest & S5 (4 combos) & 0.8536 & \textbf{0.8239} & \textbf{0.8605} & \textbf{0.7817} & 368 s \\
Random Forest & S6 (18 combos) & \textbf{0.8547} & 0.8234 & 0.8605 & 0.7817 & 2{,}448 s \\
XGBoost & S5 (4 combos) & 0.8653 & \textbf{0.8244} & \textbf{0.8425} & \textbf{0.7535} & 19 s \\
XGBoost & S6 (36 combos) & \textbf{0.8689} & 0.8198 & 0.8379 & 0.7465 & 148 s \\
\bottomrule
\end{tabular}
\end{table}"""),
(
    r"""Table~\ref{tab:refine} is a negative result we consider informative. Expanding
the grid raised cross-validated Average Precision by 0.0011 (RF) and 0.0036
(XGBoost) but \emph{lowered} test Average Precision and reduced
precision-constrained recall, while multiplying training time by up to seven
times. With only 331 fraud examples in the training set, a wider search begins
to overfit the cross-validation folds themselves. We therefore retained the
simpler S5 configuration as the final model --- an explicit decision against
the usual reflex to search harder.""",
    r"""Table~\ref{tab:refine} is a negative result we consider informative. Expanding
the grid raised cross-validated Average Precision by 0.0011 (RF) and 0.0036
(XGBoost) but \emph{lowered} test Average Precision ($-0.0005$ and $-0.0046$)
and reduced precision-constrained recall, while multiplying training time by up
to seven times. With only 331 fraud examples in the training set, a wider
search begins to overfit the cross-validation folds themselves. The pattern is
systematic: across every SMOTE ratio the cross-validated estimate exceeds the
test Average Precision by $0.013$ to $0.057$, and the gap is widest for
XGBoost --- the model given the most search freedom. We therefore retained the
simpler S5 configuration as the final model --- an explicit decision against
the usual reflex to search harder."""),
(
    r"""\paragraph*{SMOTE helps; Random Undersampling destroys.}
Light oversampling at 1:100 raises Random Forest Average Precision from 0.8055
to 0.8239. Random Undersampling, by contrast, collapses it to 0.6883 and
renders the precision-constrained recall negligible (0.035--0.092 across
models). The mechanism is straightforward: discarding roughly 95\% of the
legitimate class removes exactly the evidence the model needs to learn a
boundary against the majority.""",
    r"""\paragraph*{SMOTE helps; Random Undersampling destroys.}
Light oversampling raises Random Forest Average Precision from 0.8055 to 0.8239
at the 1:100 ratio, and to 0.8348 at 1:10. Random Undersampling, by contrast,
collapses it to 0.6883 and renders the precision-constrained recall negligible
(0.035--0.092 across models). The mechanism is straightforward: discarding
roughly 95\% of the legitimate class removes exactly the evidence the model
needs to learn a boundary against the majority."""),
])

# ---------------------------------------------------------------------------
# 6-Discuss.tex
# ---------------------------------------------------------------------------
patch("6-Discuss.tex", [(
    r"""\paragraph*{Random Undersampling is actively harmful.} It costs 4.3 times more
than SMOTE on average and collapses precision-constrained recall to 0.063.
Despite being among the most commonly prescribed techniques, it is the worst
choice on this dataset.""",
    r"""\paragraph*{Random Undersampling is actively harmful.} Its mean cost is 2.4
times that of SMOTE and 4.3 times the best cost achievable with SMOTE, and it
collapses precision-constrained recall to 0.063. Despite being among the most
commonly prescribed techniques, it is the worst choice on this dataset."""),
(
    r"""\paragraph*{The operating policy matters more than the model.} A two-tier policy
(auto-block above 0.65, manual review between 0.095 and 0.65) beats any single
threshold on recall, cost and analyst workload simultaneously. This is the
clearest path from a research artefact to an operational deployment.""",
    r"""\paragraph*{The operating policy matters more than the model.} A single
threshold cannot satisfy the 95\% precision floor and the 100-review-per-day
capacity at the same time: it either needs 1.9 analysts, or it must be
throttled to 40.9\% recall. The two-tier policy resolves the dilemma, reaching
81.0\% recall at lower cost with only 70 reviews per day --- a Pareto
improvement over the best single threshold, which needs 232 reviews per day for
the same recall. This is the clearest path from a research artefact to an
operational deployment."""),
(
    r"""\paragraph*{One cost assumption carries substantial weight.} The conclusion that
the cost-minimising threshold is 0.1767 (recall 0.8099 at USD 154.65) holds
only under our assumed USD 0.30 review cost. If the true cost of blocking a
legitimate customer is higher --- churn, card replacement, reputational damage
--- the 95\% precision constraint becomes optimal instead. We regard this as
the most important sensitivity in the entire report, and the model is
explicitly parameterised so a bank can re-derive the optimum for its own cost
structure. We did not adopt the cost-minimising threshold because it would flag
29 legitimate customers per 85{,}118 transactions, a customer-facing risk we
judged unacceptable; this is a business judgement, not a statistical one.""",
    r"""\paragraph*{One cost assumption carries substantial weight.} The
cost-minimising threshold moves with the review cost: it rises from 0.0405 at
USD 0.10 to 0.4605 at USD 2.00 (Table~\ref{tab:sens}). If the true cost of
blocking a legitimate customer is higher --- churn, card replacement,
reputational damage --- the bank should demand higher precision and accept
lower recall, and the 95\% precision constraint becomes the binding one
instead. We regard this as the most important sensitivity in the entire report,
and the model is explicitly parameterised so a bank can re-derive the optimum
for its own cost structure. Our recommended policy was selected under the
capacity constraint rather than the cost criterion, which makes it robust to
this assumption: auto-blocking consumes no analyst time at any review price."""),
(
    r"""    \item \textbf{Deploy the two-tier policy.} Auto-block above 0.65, route the
    0.095--0.65 band to analysts, approve the remainder. It dominates the
    single-threshold alternative on every measured dimension.""",
    r"""    \item \textbf{Deploy the two-tier policy.} Auto-block above 0.810, route
    the 0.175--0.810 band to analysts, approve the remainder. It attains higher
    recall at lower cost than any single threshold while requiring only 70
    reviews per day, i.e.\ inside the capacity of one analyst."""),
(
    r"""    \item \textbf{Retain the leakage-free threshold of 0.65 for planning} and
    monitor recall in production. The test-tuned value of 0.52 should not be
    used for capacity or budget planning.""",
    r"""    \item \textbf{Plan capacity on the leakage-free numbers.} The test-tuned
    threshold of 0.52 and the two-tier thresholds reported here were all
    derived from test-set predictions and must be re-derived from out-of-fold
    training predictions before they are used for staffing or budget decisions;
    the leakage-free single-threshold recall is 73.24\% rather than 78.17\%."""),
(
    r"""    \item \textbf{Prefer SMOTE or class weighting; avoid Random Undersampling.}
    The evidence on cost, recall and ranking quality is consistent across five
    model families.""",
    r"""    \item \textbf{Prefer SMOTE or class weighting; avoid Random Undersampling.}
    Random Undersampling is the only technique that degraded every model
    family it was paired with, and its mean cost is 2.4 times that of SMOTE.
    Note that SMOTE gives the best ranking but not the lowest mean cost --- on
    average SMOTE-ENN is cheaper, because it trades recall for precision."""),
])

print("done")
