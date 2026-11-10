"""S11c · Rut gon van ban de quay lai 20 trang, giu nguyen moi sua doi logic.
KHONG doi con so nao.
"""
from pathlib import Path

EDITS = []


def add(path, old, new, tag):
    EDITS.append((path, old, new, tag))


# --- Table 7 caption: rut gon 5 -> 4 dong, van dung so dong hien thi
add("report/Sections/4-Results.tex",
    """directly from \\texttt{feature\\_importances\\_} of the fitted forest. The table shows
the five highest-ranked features by permutation importance, the seventh-ranked
\\texttt{V9}, and three engineered temporal features (\\texttt{Day},
\\texttt{Hour\\_of\\_Day}, \\texttt{Is\\_Night}) reported for contrast; the
remaining 26 of the 35 are omitted for space, and the full ranking is archived
in \\texttt{artifacts/tables/s8\\_importance\\_comparison.csv}.}""",
    """directly from \\texttt{feature\\_importances\\_} of the fitted forest. The table shows
the five highest-ranked features by permutation importance, the seventh-ranked
\\texttt{V9}, and three engineered temporal features reported for contrast; the
other 26 of the 35 are omitted for space, and the full ranking is archived in
\\texttt{artifacts/tables/s8\\_importance\\_comparison.csv}.}""",
    "T7 caption: rut gon 1 dong")

# --- Table 16 caption: rut gon
add("report/Sections/5-Cost.tex",
    """cost of one manual review. The threshold rises from 0.0405 to 0.4605 as the
review cost increases twenty-fold. Every row in this table is an
\\emph{unconstrained} cost optimum: their review workloads run from 193.3 to
685.0 transactions per day and therefore \\emph{exceed} the 100-review-per-day
capacity of a single analyst. This is precisely why the single-threshold
family is not deployable at any review price, whereas the two-tier policy of
Section~\\ref{sec:twotier} remains feasible at every price because
auto-blocking consumes no analyst time.}""",
    """cost of one manual review. The threshold rises from 0.0405 to 0.4605 as the
review cost increases twenty-fold. Every row is an \\emph{unconstrained} cost
optimum whose review workload (193.3 to 685.0 transactions per day) exceeds
the 100-review-per-day capacity of a single analyst, which is why no single
threshold is deployable at any review price, whereas the two-tier policy of
Section~\\ref{sec:twotier} stays feasible at every price because auto-blocking
consumes no analyst time.}""",
    "T16 caption: rut gon 2 dong")

# --- 5-Cost: tra ve dong goc (dung nghĩa)
add("report/Sections/5-Cost.tex",
    """best achievable cost}, SMOTE and no resampling tie at USD 170.45 --- reached at
the same precision-constrained operating point as the final model --- and
SMOTE-ENN's best is USD 214.05.""",
    """best achievable cost}, SMOTE and no resampling tie at USD 170.45 --- at the same
precision-constrained operating point as the final model --- and SMOTE-ENN's
best is USD 214.05.""",
    "5-Cost: rut gon 1 dong")

# --- 6-Discuss: rut gon phan tie-break
add("report/Sections/6-Discuss.tex",
    """present a tie explicitly in Section~\\ref{sec:results}: two configurations
reach an identical operating point, and our choice among them rests on a
tie-break declared in advance --- Average Precision --- rather than on a
statistically significant difference.""",
    """present a tie explicitly in Section~\\ref{sec:results}: two configurations
reach an identical operating point, and our choice among them rests on a
tie-break declared in advance (Average Precision) rather than on a
statistically significant difference.""",
    "6-Discuss: rut gon 1 dong")

# --- 1-Title: rut gon
add("report/Sections/1-Title.tex",
    """day --- an operational gain over the cheapest single threshold near that
operating point, which needs 232 reviews per day for a comparable recall.""",
    """day --- an operational gain over the cheapest single threshold near that
operating point, which needs 232 reviews per day for comparable recall.""",
    "1-Title: rut gon 1 dong")

# --- 7-Conclu: rut gon
add("report/Sections/7-Conclu.tex",
    """operational improvement rather than a re-labelling: the comparable recall
reached by the cheapest single threshold near that operating point (0.1767,
recall 0.8028) would need 232 reviews per day, more than twice the available
capacity.""",
    """operational improvement rather than a re-labelling: the comparable recall
reached by the cheapest single threshold near that operating point (0.1767,
recall 0.8028) would need 232 reviews per day, more than twice the capacity.""",
    "7-Conclu: rut gon 1 dong")

# --- 3-Method: rut gon (net -1 dong so)
add("report/Sections/3-Method.tex",
    """Search spaces were kept deliberately modest, because Section~\\ref{sec:search}
reports an observation consistent with an aggressive search on 331 fraud
examples not paying off.""",
    """Search spaces were kept deliberately modest, because Section~\\ref{sec:search}
reports an observation consistent with an aggressive search on 331 fraud examples
not paying off.""",
    "3-Method: rut gon 1 dong")

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
