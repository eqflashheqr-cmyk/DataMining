"""S10m · Gọn văn bản Section 3 để hút trang 7 (chỉ 1 dòng vọt) về trang 6."""
from pathlib import Path

p = Path("report/Sections/3-Method.tex")
s = p.read_text(encoding="utf-8")

PAIRS = [
    # 1. caveat paragraph -- gọn
    ("""confirms this by showing a near-zero effect. Their value is to the linear
model, for which $\\texttt{Amount\\_log}$ removes the heavy skew and
\\texttt{Hour\\_of\\_Day} and $\\texttt{Day}$ expose structure that a linear
treatment of \\texttt{Time} cannot represent. $\\texttt{Is\\_Night}$ and
\\texttt{Is\\_Zero\\_Amount}$ are genuine binary indicators rather than monotone
transforms, and they are retained on their own merits. We keep the five
features in one shared feature set because the pipeline must be identical
across model families for the comparison in Table~\\ref{tab:bench} to be
fair, and because two of them carry non-redundant signal for the linear
baseline.""",
     """confirms this with a near-zero effect. Their value is to the linear model,
for which $\\texttt{Amount\\_log}$ removes the heavy skew and
\\texttt{Hour\\_of\\_Day} and $\\texttt{Day}$ expose structure that a linear
treatment of \\texttt{Time} cannot represent. $\\texttt{Is\\_Night}$ and
$\\texttt{Is\\_Zero\\_Amount}$ are genuine binary indicators rather than monotone
transforms, and are retained on their own merits. We keep all five in one
shared feature set because the pipeline must be identical across model
families for the comparison in Table~\\ref{tab:bench} to be fair, and because
two of them carry non-redundant signal for the linear baseline."""),
    # 2. Stage 5 -- gọn
    ("""\\texttt{GridSearchCV} with three-fold stratified CV scored on Average
Precision, and every test-set prediction was computed \\emph{once} per
configuration, from a model fitted on the training set only.""",
     """\\texttt{GridSearchCV} with three-fold stratified CV scored on Average
Precision, and every test-set prediction was computed once per configuration
from a model fitted on the training set only."""),
    # 3. Stage 3 -- gọn
    ("""Five features were derived from Time and Amount: Hour_of_Day = (Time/3600) mod 24,
Day = ⌊Time/86400⌋, Is_Night, Amount_log = log(1 + Amount), and Is_Zero_Amount. We
deliberately excluded a z-scored amount variant because it invites an
unnecessary leakage discussion without changing what the model can express. The
resulting 35-feature set was adopted after an ablation study showed that the
engineered features cost nothing and carry genuine signal, though the gain
itself is small (Section~\\ref{sec:preprocess}).""",
     """Five features were derived from Time and Amount: Hour_of_Day = (Time/3600) mod 24,
Day = ⌊Time/86400⌋, Is_Night, Amount_log = log(1 + Amount), and Is_Zero_Amount. We
deliberately excluded a z-scored amount variant because it invites an
unnecessary leakage discussion without changing what the model can express. The
resulting 35-feature set was adopted after an ablation study showed that the
engineered features cost nothing, though the gain itself is small
(Section~\\ref{sec:preprocess})."""),
    # 4. Stage 4 -- gọn
    ("""A \\texttt{ColumnTransformer} with \\texttt{remainder="drop"} passes the 33
non-scaled columns through untouched and applies \\texttt{StandardScaler} only
to \\texttt{Time} and \\texttt{Amount}, which have radically different scales.
We compared \\texttt{StandardScaler}, \\texttt{RobustScaler} and no scaling;
scaling affects linear models strongly and tree ensembles negligibly, so we
retain \\texttt{StandardScaler}.""",
     """A \\texttt{ColumnTransformer} with \\texttt{remainder="drop"} passes the 33
non-scaled columns through untouched and applies \\texttt{StandardScaler} only
to \\texttt{Time} and \\texttt{Amount}, which have radically different scales.
We compared \\texttt{StandardScaler}, \\texttt{RobustScaler} and no scaling;
scaling affects linear models strongly and tree ensembles negligibly, so we
retain \\texttt{StandardScaler}."""),
]

for old, new in PAIRS:
    if old not in s:
        print("[skip] not found:", old[:60].replace("\n", " "))
        continue
    s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("[ok] 3-Method.tex compacted")
