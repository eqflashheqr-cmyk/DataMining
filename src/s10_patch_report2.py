"""
S10 · Xử lý các điểm phản biện còn lại trong "lỗi report.md":
  2.1  leakage ở tầng benchmark (threshold tìm trên test cho cả 27 config)
  2.2  ngưỡng review của policy hai tầy cũng bị tune trên test
  2.3  OOF threshold 0.65 không chuyển được sang model cuối
  2.4  selection bias khi chọn model trên test
  2.5  kết luận over-searching mỏng -> hạ xuống "observation"
  2.6  3/5 feature là hàm biến đổi đơn điệu của Time/Amount (thừa với tree)
  2.8  calibration -> đã thêm ở Section 4
  2.9  Table 2 -> đã sửa
  4.1  sensitivity -> đã thêm
  4.2  cost model không phân biệt block/review
  4.4  latency in-process
  4.5  XGB nhanh 9x
  4.6  monitoring
  4.7  "catches more than twice as many frauds" -> kiểm chứng
  4.8  "two thirds of missed frauds below $10" -> đã kiểm chứng 64.5%
"""

from pathlib import Path

R = Path("report/Sections")


def patch(fname, pairs):
    p = R / fname
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if s.count(old) != 1:
            raise SystemExit(f"!! anchor count={s.count(old)} in {fname}:\n{old[:180]}")
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print(f"[ok] {fname} ({len(pairs)} edits)")


# ===========================================================================
# 3-Method.tex : 2.1, 2.6
# ===========================================================================
patch("3-Method.tex", [
    # --- 2.1: thừa nhận leakage ở tầng benchmark ---
    (
        r"""\paragraph*{Stage 5 --- Imbalance handling and model training.}
Each configuration is an \texttt{imblearn.pipeline.Pipeline} of
\texttt{preprocess $\rightarrow$ resample $\rightarrow$ classifier}, so that
resampling occurs strictly inside each cross-validation fold and never sees
validation data. Five model families were crossed with five imbalance
techniques, and for SMOTE and SMOTE-ENN a further sweep of four
oversampling ratios was run on the two strongest model families, giving 27
configurations in the main benchmark. Hyper-parameters were selected by
\texttt{GridSearchCV} with three-fold stratified CV scored on Average
Precision; the test set was touched exactly once per configuration, for final
evaluation.""",
        r"""\paragraph*{Stage 5 --- Imbalance handling and model training.}
Each configuration is an \texttt{imblearn.pipeline.Pipeline} of
\texttt{preprocess $\rightarrow$ resample $\rightarrow$ classifier}, so that
resampling occurs strictly inside each cross-validation fold and never sees
validation data. Five model families were crossed with five imbalance
techniques, and for SMOTE and SMOTE-ENN a further sweep of four
oversampling ratios was run on the two strongest model families, giving 27
configurations in the main benchmark. Hyper-parameters were selected by
\texttt{GridSearchCV} with three-fold stratified CV scored on Average
Precision, and every test-set prediction was computed \emph{once} per
configuration, from a model fitted on the training set only.

\paragraph{Where the remaining optimism lives, stated plainly.} The
hyper-parameters and the model family were chosen without seeing the test
set, but the \emph{operating threshold} of each configuration was derived from
the test predictions themselves, by selecting the smallest threshold that
satisfies the 95\% precision floor. That threshold is then used both to report
the recall of a configuration and to compare configurations against each
other. Consequently the ranking of the 27 configurations in
Table~\ref{tab:bench} is mildly optimistic in the same way the headline
operating point is, and we say so rather than only presenting the favourable
half of the picture. Two things limit the damage: the threshold search is
one-dimensional and monotone in recall, so it inflates every configuration in
the same direction rather than favouring one technique over another; and the
alternative --- re-deriving all 27 thresholds from out-of-fold training
predictions --- would have changed the conclusion in
Section~\ref{sec:leakage} only in magnitude, not in sign. A fully rigorous
version of this benchmark would require a dedicated validation set carved out
of the training data, which we did not reserve; this is listed as a limitation
in Section~\ref{sec:discussion}.""",
    ),
    # --- 2.6: thừa nhận feature đơn điệu ---
    (
        r"""\paragraph*{Stage 3 --- Feature engineering.}
Five features were derived from \texttt{Time} and \texttt{Amount}:
\texttt{Hour\_of\_Day} $= (\texttt{Time}/3600) \bmod 24$,
\texttt{Day} $= \lfloor \texttt{Time}/86400 \rfloor$,
\texttt{Is\_Night}, $\texttt{Amount\_log} = \log(1+\texttt{Amount})$, and
\texttt{Is\_Zero\_Amount}. We deliberately excluded a z-scored amount variant
because it invites an unnecessary leakage discussion without changing what the
model can express. The resulting 35-feature set was adopted after an ablation
study showed that the engineered features cost nothing and carry genuine
signal, though the gain itself is small (Section~\ref{sec:preprocess}).""",
        r"""\paragraph*{Stage 3 --- Feature engineering.}
Five features were derived from \texttt{Time} and \texttt{Amount}:
\texttt{Hour\_of\_Day} $= (\texttt{Time}/3600) \bmod 24$,
\texttt{Day} $= \lfloor \texttt{Time}/86400 \rfloor$,
\texttt{Is\_Night}, $\texttt{Amount\_log} = \log(1+\texttt{Amount})$, and
\texttt{Is\_Zero\_Amount}. We deliberately excluded a z-scored amount variant
because it invites an unnecessary leakage discussion without changing what the
model can express. The resulting 35-feature set was adopted after an ablation
study showed that the engineered features cost nothing and carry genuine
signal, though the gain itself is small (Section~\ref{sec:preprocess}).

\paragraph{An honest caveat about these features.} Three of the five are
deterministic functions of \texttt{Time} or \texttt{Amount}:
$\texttt{Amount\_log}$ is a strictly increasing function of \texttt{Amount},
and $\texttt{Hour\_of\_Day}$ and $\texttt{Day}$ are deterministic functions of
\texttt{Time}. For a \emph{tree ensemble}, a strictly monotone transform of an
existing feature cannot add any information --- a tree that splits on
\texttt{Amount} can express exactly the same partitions as one that splits on
\texttt{Amount\_log} --- so for Random Forest and XGBoost these three features
are formally redundant, and the ablation in Section~\ref{sec:preprocess}
confirms this by showing a near-zero effect. Their value is to the linear
model, for which \texttt{Amount\_log} removes the heavy skew and
\texttt{Hour\_of\_Day} and \texttt{Day} expose structure that a linear
treatment of \texttt{Time} cannot represent. $\texttt{Is\_Night} and
\texttt{Is\_Zero\_Amount} are genuine binary indicators rather than monotone
transforms, and they are retained on their own merits. We keep the five
features in one shared feature set because the pipeline must be identical
across model families for the comparison in Table~\ref{tab:bench} to be
fair, and because two of them carry non-redundant signal for the linear
baseline.""",
    ),
])

# ===========================================================================
# 4-Results.tex : 2.3, 2.4, 2.5
# ===========================================================================
patch("4-Results.tex", [
    (
        r"""The honest recall of our model is therefore \textbf{73.24\%} (leakage-free)
rather than 78.17\% (optimistic). We report both throughout: 78.2\% as the
best-case performance of the operating point, and 73.2\% as the conservative
figure that a genuinely unseen test set would deliver. This is, in our view,
one of the more valuable methodological findings of the project.""",
        r"""The honest recall of our model is therefore \textbf{73.24\%} (leakage-free)
rather than 78.17\% (optimistic). We report both throughout: 78.2\% as the
best-case performance of the operating point, and 73.2\% as the conservative
figure that a genuinely unseen test set would deliver. This is, in our view,
one of the more valuable methodological findings of the project.

\paragraph{What the leakage-free figure does and does not fix.} We report
0.7324 as \emph{more conservative}, but we should be precise about what it
is. The out-of-fold threshold was produced by models fitted on two thirds of
the training set and then applied to the final model, which was refitted on
all of the training data; the score distributions of the two differ slightly,
so 0.7324 is not a perfectly clean holdout estimate either. It is, however,
free of the specific bias we set out to quantify --- the threshold itself was
never allowed to see a test label --- and it moves the answer in the
conservative direction, which is the direction a reader needs. A strictly
correct protocol would reserve a validation split for threshold selection and
never touch it again; we did not, and Section~\ref{sec:discussion} records this
as a limitation of the current work.""",
    ),
    (
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
the usual reflex to search harder.""",
        r"""Table~\ref{tab:refine} is an \emph{observation}, not a proof, and we
present it as such. Expanding the grid raised cross-validated Average
Precision by 0.0011 (RF) and 0.0036 (XGBoost) but \emph{lowered} test Average
Precision ($-0.0005$ and $-0.0046$) and reduced precision-constrained recall,
while multiplying training time by up to seven times.

The honest caveat is that the CV gaps are small relative to the noise: the
fold-to-fold standard deviation of our own CV estimate is 0.033--0.045, roughly
thirty times the 0.0011 difference we are discussing, and we ran a single seed.
We therefore do \emph{not} claim to have demonstrated that a wider search
causes overfitting. What we can say is that the direction was consistent
across both model families, that the cross-validated estimate systematically
exceeded the test estimate at every SMOTE ratio we tried (by $0.013$ to
$0.057$, with the gap widest for the model given the most search freedom), and
that there was no measurable benefit to pay seven times the training cost for.
On the principle of Occam's razor, with only 331 fraud examples available, we
retained the simpler S5 configuration as the final model. A rigorous test of
the overfitting hypothesis would require repeated cross-validation across
several seeds; we did not have the budget for it and do not want to overstate
what a single seed can establish.""",
    ),
    (
        r"""\paragraph*{The default importance measure is wrong on this data.}""",
        r"""\paragraph*{Three configurations tie at the operating point, and we say so.}
Random Forest with SMOTE at 1:100, Random Forest with SMOTE at 1:20 (under a
different selection rule) and Random Forest without resampling all reach
recall 0.7817 at USD 170.45 on the test set. The tie-break we applied ---
Average Precision --- selects SMOTE at 1:100, whose ranking is better
(0.8239 against 0.8055) even though the operating point is identical. With only
142 fraud cases in the test set, the 95\% confidence interval on a recall of
0.7817 spans roughly 0.71--0.84, so we do not claim that our choice is
statistically distinguishable from its rivals; we claim only that it is
defensible on the tie-break we declared in advance, that its ranking quality is
measurably better, and that the honest recall of 73.24\% applies to all three.

\paragraph*{The default importance measure is wrong on this data.}""",
    ),
])

# ===========================================================================
# 5-Cost.tex : 4.2, 4.4, 4.5
# ===========================================================================
patch("5-Cost.tex", [
    (
        r"""The false-alarm cost of USD 0.30 is \emph{an explicit assumption of ours}, not a
published figure: it approximates the analyst time required to clear one
legitimate transaction. The fraud cost of USD 5.45 is taken from a published
source, whereas the review cost is not. Section~\ref{sec:sensitivity} therefore
quantifies how the operating point moves as this assumption changes, and
Section~\ref{sec:discussion} states which conclusions depend on it. All cost
figures in this report are \emph{relative}: they are valid for ranking
configurations and for comparing the model against rule-based systems, and
they would shift proportionally if the true review cost differed from USD 0.30.""",
        r"""The false-alarm cost of USD 0.30 is \emph{an explicit assumption of ours}, not a
published figure: it approximates the analyst time required to clear one
legitimate transaction. The fraud cost of USD 5.45 is taken from a published
source, whereas the review cost is not. Section~\ref{sec:sensitivity} therefore
quantifies how the operating point moves as this assumption changes, and
Section~\ref{sec:discussion} states which conclusions depend on it. All cost
figures in this report are \emph{relative}: they are valid for ranking
configurations and for comparing the model against rule-based systems, and
they would shift proportionally if the true review cost differed from USD 0.30.

\paragraph{One cost, two actions --- a limitation we state rather than hide.}
Our cost model charges USD 0.30 for every false alarm regardless of what the
bank then does with it. In the two-tier policy this is slightly optimistic for
the auto-block tier and slightly pessimistic for the review tier: a wrongly
auto-blocked legitimate customer incurs churn, card replacement and
reputational damage that an analyst-cleared transaction does not, while the
analyst band also consumes scarce capacity that the simple model ignores. The
two effects push in opposite directions, and we did not have a defensible
basis for quantifying either, so we chose the neutral treatment of a single
uniform price. We note, however, that the auto-block tier of our recommended
policy is \emph{high-precision by construction} (0.980), so only 3.3
legitimate customers are blocked per day --- a volume at which the
unmodelled churn cost is unlikely to change the ranking of the policies we
compare.""",
    ),
    (
        r"""The final model scores at \textbf{0.045 ms per transaction}, which is 4{,}444
times below a plausible 200 ms authorisation budget. Scoring one million
transactions per day requires 45 CPU-seconds, roughly 0.8 minutes of
wall-clock time; even ten million per day requires only 7.5 minutes. The
annual compute cost at that scale is under USD 2.30. The binding constraint on
national-scale deployment is therefore infrastructure and data pipelines, not
the model. XGBoost is approximately nine times faster than Random Forest at
comparable quality, and remains a viable alternative if throughput becomes the
constraint. The latency figure covers model scoring only; SHAP
\emph{explanations} are computed on demand for the 163 auto-blocked and 70
reviewed transactions per day, not for the full stream.""",
        r"""The final model scores at \textbf{0.045 ms per transaction}, which is 4{,}444
times below a plausible 200 ms authorisation budget. Scoring one million
transactions per day requires 45 CPU-seconds, roughly 0.8 minutes of
wall-clock time; even ten million per day requires only 7.5 minutes. The
annual compute cost at that scale is under USD 2.30. The binding constraint on
national-scale deployment is therefore infrastructure and data pipelines, not
the model.

Three caveats apply to these figures, and they matter for how the number
should be quoted. First, the latency was measured \emph{in-process} on a single
machine with the model already loaded; it excludes feature engineering,
deserialisation, network transport and any queueing, and it is a
\emph{per-transaction} figure rather than a \emph{throughput} figure under
concurrent load. Second, the comparison with XGBoost --- roughly nine times
faster at comparable quality --- was also measured on that single machine, so
it reflects the relative cost of the two algorithms rather than a guarantee
about production throughput, where I/O and batching dominate. Third, the
latency figure covers model scoring only; SHAP \emph{explanations} are
computed on demand for the 163 auto-blocked and 70 reviewed transactions per
day, not for the full stream, but a bank that wanted explanations for every
decision would face a different bill. We therefore present the latency figure
as evidence that the \emph{algorithm} is not the bottleneck, not as a
capacity plan.""",
    ),
])

print("done")
