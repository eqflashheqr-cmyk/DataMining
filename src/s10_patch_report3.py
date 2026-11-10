"""
S10 · Xử lý 2.2 (ngưỡng policy hai tầy cũng lấy từ test) và 4.6 (monitoring).
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
# 5-Cost.tex : 2.2 -- thừa nhận ngưỡng hai tầy cũng lấy từ test
# ===========================================================================
patch("5-Cost.tex", [
    (
        r"""We searched exhaustively over the two-threshold space (auto-block threshold
from 0.50 to 0.99, review threshold in steps of 0.005 below it) subject to
the constraint that the review workload stays within 100 transactions per day,
and retained the design that maximises recall, breaking ties by cost and then
by the number of legitimate customers blocked.""",
        r"""We searched exhaustively over the two-threshold space (auto-block threshold
from 0.50 to 0.99, review threshold in steps of 0.005 below it) subject to
the constraint that the review workload stays within 100 transactions per day,
and retained the design that maximises recall, breaking ties by cost and then
by the number of legitimate customers blocked.

\paragraph{The thresholds of this policy share the same caveat as the
benchmark thresholds.} Both were selected using the test-set predictions, for
the same reason of practical convenience that we explain in
Section~\ref{sec:results}: re-deriving every threshold from out-of-fold
predictions across 11{,}442 candidate designs was not affordable within the
project budget. We report the resulting policy as a \emph{design with a
validated mechanism} rather than as a leak-free operating point. The
mechanism --- that auto-blocking removes analyst work and therefore relaxes
the capacity constraint --- is a structural property of the two-tier
architecture and does not depend on where the two numbers came from; the
specific values 0.810 and 0.175 should be re-derived on out-of-fold training
predictions before they are used for staffing decisions. Section~\ref{sec:discussion}
lists this explicitly among our limitations.""",
    ),
])

# ===========================================================================
# 6-Discuss.tex : thêm limitation về selection bias + monitoring recommendation
# ===========================================================================
patch("6-Discuss.tex", [
    (
        r"""\paragraph*{Sample size limits statistical power.} The test set contains only 142
frauds. A recall of 0.7817 has a 95\% confidence interval of roughly
$[0.71, 0.84]$, so differences below a few percentage points between
configurations should not be over-interpreted. This is also why the wider
hyper-parameter search failed: with 331 training frauds, the search space
itself becomes a source of overfitting.""",
        r"""\paragraph*{Sample size limits statistical power.} The test set contains only 142
frauds. A recall of 0.7817 has a 95\% confidence interval of roughly
$[0.71, 0.84]$, so differences below a few percentage points between
configurations should not be over-interpreted. This is also why the wider
hyper-parameter search failed: with 331 training frauds, the search space
itself becomes a source of overfitting.

\paragraph*{Our own thresholds are also test-derived.} We are explicit about
this because it cuts against our own conclusions. The operating thresholds of
the benchmark, of the single-threshold comparison \emph{and} of the
recommended two-tier policy were all selected on test-set predictions. The
model family, the hyper-parameters and the split itself were not. The
consequence is that the recall figures in this report are optimistic by an
amount we have quantified at 4.9 percentage points for the single-threshold
case, and that the two-tier thresholds (0.810 and 0.175) in particular must be
re-derived out-of-fold before they are used operationally. The qualitative
conclusions --- that Random Undersampling is harmful, that a tree ensemble is
required, that two tiers relax the capacity constraint --- do not depend on
the exact threshold values; the specific operating point does.

\paragraph*{Model selection on the test set.} Twenty-seven configurations were
compared on the same 142 test frauds, and the winner was then reported on
that same test set. This is a form of selection bias, and it is the reason we
present a tie explicitly in Section~\ref{sec:results}: three configurations
reach an identical operating point, and our choice among them rests on a
tie-break declared in advance rather than on a statistically significant
difference. A dedicated validation set or nested cross-validation would remove
this bias; we did not reserve one, and with 331 training frauds the option was
not attractive.""",
    ),
    (
        r"""    \item \textbf{Extend the dataset.} Merchant category, device fingerprint
    and transaction-history features are the missing ingredients for the
    low-value frauds that dominate our false negatives.""",
        r"""    \item \textbf{Extend the dataset.} Merchant category, device fingerprint
    and transaction-history features are the missing ingredients for the
    low-value frauds that dominate our false negatives.
    \item \textbf{Monitor four quantities in production.} (i) The realised
    fraud rate in the auto-block tier --- a fall below the 0.980 precision we
    measured would mean the model is blocking legitimate customers and should
    trigger an immediate threshold review; (ii) the analyst queue depth
    against the 100-per-day capacity, with an alert at 80 transactions; (iii)
    the population stability index of the feature distributions, since
    \texttt{Amount} carries most of the model's signal and a shift in the
    transaction mix would invalidate the threshold; and (iv) the recall of the
    confirmed-fraud sample, estimated monthly, which is the only way to
    detect that the fraud pattern itself has drifted. Because the model is
    trained on a two-day window, we would also re-fit on a rolling 30-day
    window before any drift becomes material.""",
    ),
])

print("done")
