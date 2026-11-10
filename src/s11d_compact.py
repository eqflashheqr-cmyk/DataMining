"""S11d · Rut gon ~5 dong van ban de huy 2 trang trong (trang 7 va 12 chi con
1-2 dong), dua tong bao cao ve lai 20 trang. KHONG doi con so, KHONG doi y nghiaa.
"""
from pathlib import Path

EDITS = []


def add(path, old, new, tag):
    EDITS.append((path, old, new, tag))


# --- §3.2 caveat: rut gon ~2 dong
add("report/Sections/3-Method.tex",
    """\\texttt{Amount\\_log} --- so for Random Forest and XGBoost these three features
are formally redundant, and the ablation in Section~\\ref{sec:preprocess}
confirms this by showing a near-zero effect. Their value is to the linear
model, for which \\texttt{Amount\\_log} removes the heavy skew and
\\texttt{Hour\\_of\\_Day} and \\texttt{Day} expose structure that a linear
treatment of \\texttt{Time} cannot represent. \\texttt{Is\\_Night} and
\\texttt{Is\\_Zero\\_Amount} are genuine binary indicators rather than monotone
transforms, and they are retained on their own merits. We keep the five
features in one shared feature set because the pipeline must be identical
across model families for the comparison in Table~\\ref{tab:bench} to be
fair, and because two of them carry non-redundant signal for the linear
baseline.""",
    """\\texttt{Amount\\_log} --- so for Random Forest and XGBoost these three features
are formally redundant, and the ablation in Section~\\ref{sec:preprocess}
confirms a near-zero effect. Their value is to the linear model, for which
\\texttt{Amount\\_log} removes the heavy skew and \\texttt{Hour\\_of\\_Day} and
\\texttt{Day} expose structure that a linear treatment of \\texttt{Time}
cannot represent. \\texttt{Is\\_Night} and \\texttt{Is\\_Zero\\_Amount} are
genuine binary indicators rather than monotone transforms, and are retained on
their own merits. We keep all five in one shared set because the pipeline must
be identical across model families for the comparison in Table~\\ref{tab:bench}
to be fair, and because two carry non-redundant signal for the linear
baseline.""",
    "3.2 caveat: rut gon ~2 dong")

# --- §3.5 ablation: rut gon ~2 dong
add("report/Sections/3-Method.tex",
    """We therefore adopt the 35-column set on grounds other than the ablation
delta: the CV estimate is non-negative for every model tested, the test-set
change is well inside noise, and three of the five engineered features
($\\texttt{Amount\\_log}$, $\\texttt{Day}$, $\\texttt{Hour\\_of\\_Day}$) appear in
the top fifteen by permutation importance, with $\\texttt{Day}$ reaching SHAP
rank 5 (Section~\\ref{sec:results}). The ablation does \\emph{not} show that
feature engineering is worth much on this dataset; it shows that it costs
nothing, which is consistent with the mutual-information evidence in
Figure~\\ref{fig:feateng}.""",
    """We therefore adopt the 35-column set on grounds other than the ablation
delta: the CV estimate is non-negative for every model tested, the test-set
change is well inside noise, and three of the five engineered features
($\\texttt{Amount\\_log}$, $\\texttt{Day}$, $\\texttt{Hour\\_of\\_Day}$) appear in
the top fifteen by permutation importance, with $\\texttt{Day}$ reaching SHAP
rank 5 (Section~\\ref{sec:results}). The ablation does \\emph{not} show that
feature engineering is worth much here; it shows that it costs nothing,
consistent with the mutual-information evidence in
Figure~\\ref{fig:feateng}.""",
    "3.5 ablation: rut gon ~2 dong")

# --- §4.6 impurity: rut gon ~2 dong
add("report/Sections/4-Results.tex",
    """Reporting \\texttt{feature\\_importances\\_} alone would have hidden the single
most informative feature in the dataset --- and, with it, the fact that the
model's signal is mostly about transaction size, which is exactly the insight
a bank needs in order to design an amount-gating policy. The Spearman
correlation between permutation importance and SHAP is 0.766, indicating broad
agreement in ranking between the two measure-based approaches.""",
    """Reporting \\texttt{feature\\_importances\\_} alone would have hidden the most
informative feature in the dataset --- and, with it, the fact that the model's
signal is mostly about transaction size, which is exactly the insight a bank
needs to design an amount-gating policy. The Spearman correlation between
permutation importance and SHAP is 0.766, indicating broad agreement between
the two measure-based approaches.""",
    "4.6 impurity: rut gon ~2 dong")

# --- §4.7 calibration: rut gon ~2 dong
add("report/Sections/4-Results.tex",
    """score of 0.000448 is barely above the 0.001668 \\times (1 \\minus0.001668) = 0.001665 of the trivial always-legitimate predictor expressed in the
same units, because the model is nearly always correct when it predicts
``legitimate''. The reliability diagram in Figure~\\ref{fig:calib} shows why
this matters: the score distribution is extremely concentrated --- 99.9\\% of
all transactions score below 0.1 --- so the model behaves as a
near-perfect ranker with sharp separation, not as a smoothly calibrated
probability surface. It is well calibrated in the tail
that the policy actually uses, which is the only property the operating
policy requires.""",
    """score of 0.000448 is barely above the 0.001665 of the trivial
always-legitimate predictor, because the model is nearly always correct when
it predicts ``legitimate''. The reliability diagram in Figure~\\ref{fig:calib}
shows why this matters: the score distribution is extremely concentrated ---
99.9\\% of all transactions score below 0.1 --- so the model behaves as a
near-perfect ranker with sharp separation, not as a smoothly calibrated
probability surface. It is well calibrated in the tail that the policy
actually uses, which is the only property the operating policy requires.""",
    "4.7 calibration: rut gon ~2 dong")

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
