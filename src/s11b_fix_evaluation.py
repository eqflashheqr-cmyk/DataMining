"""S11b · Sua cac diem con lai + lam khop logic tong the.
KHONG doi con so nao; chi sua phan dien dat.
"""
from pathlib import Path

EDITS = []


def add(path, old, new, tag):
    EDITS.append((path, old, new, tag))


# --------------------------------------------- 1) 3-Method: soften claim
add("report/Sections/3-Method.tex",
    """Search spaces were kept deliberately modest, because Section~\\ref{sec:search}
shows that an aggressive search on 331 fraud examples degrades test
performance.""",
    """Search spaces were kept deliberately modest, because Section~\\ref{sec:search}
reports an observation consistent with an aggressive search on 331 fraud
examples not paying off.""",
    "1) 3-Method: soften 'degrades' -> 'not paying off'")

# ---------------------------------- 2) Table 7 caption: so dong hien thi
add("report/Sections/4-Results.tex",
    """directly from \\texttt{feature\\_importances\\_} of the fitted forest. The table shows
the eight highest-ranked features by permutation importance out of 35; the
remaining 27 are omitted for space, and the full ranking is archived in
\\texttt{artifacts/tables/s8\\_importance\\_comparison.csv}.}""",
    """directly from \\texttt{feature\\_importances\\_} of the fitted forest. The table shows
the six features ranked in the top seven by permutation importance, together
with the three engineered temporal features (\\texttt{Day},
\\texttt{Hour\\_of\\_Day}, \\texttt{Is\\_Night}) reported for contrast; the
remaining 26 of the 35 are omitted for space, and the full ranking is archived
in \\texttt{artifacts/tables/s8\\_importance\\_comparison.csv}.}""",
    "2) Table 7 caption: so dong that thuc su hien thi")

# ------------------------------- 3) Table 16 caption: deployable claim
add("report/Sections/5-Cost.tex",
    """cost of one manual review. The threshold rises from 0.0405 to 0.4605 as the
review cost increases twenty-fold. The first three rows exceed the
100-review-per-day analyst capacity and are therefore reported as the
unconstrained cost optimum for reference; only the rows at and above USD 1.00
are deployable under a single analyst, and among those the two-tier policy of
Section~\\ref{sec:twotier} remains feasible at every review price because
auto-blocking consumes no analyst time.}""",
    """cost of one manual review. The threshold rises from 0.0405 to 0.4605 as the
review cost increases twenty-fold. Every row in this table is an
\emph{unconstrained} cost optimum: their review workloads run from 193.3 to
685.0 transactions per day and therefore \emph{exceed} the 100-review-per-day
capacity of a single analyst. This is precisely why the single-threshold
family is not deployable at any review price, whereas the two-tier policy of
Section~\\ref{sec:twotier} remains feasible at every price because
auto-blocking consumes no analyst time.}""",
    "3) Table 16 caption: khong con 'rows >= $1.00 deployable'")

# ------------------------------------- 4) Table 17 Q4: 'a 80%' -> 'an 80%'
add("report/Sections/5-Cost.tex",
    """at \\$154.65} per 85{,}118 transactions --- a \\textbf{80\\% reduction} in annual fraud cost""",
    """at \\$154.65} per 85{,}118 transactions --- an \\textbf{80\\% reduction} in annual fraud cost""",
    "4) Table 17 Q4: 'a 80%' -> 'an 80%'")

# ------------------ 5) 5-Cost: 'tie at 170.45 --- same operating point'
add("report/Sections/5-Cost.tex",
    """best achievable cost}, SMOTE and no resampling tie at USD 170.45 --- the same
operating point as the final model --- and SMOTE-ENN's best is USD 214.05.""",
    """best achievable cost}, SMOTE and no resampling tie at USD 170.45 --- reached at
the same precision-constrained operating point as the final model --- and
SMOTE-ENN's best is USD 214.05.""",
    "5) 5-Cost: 'same operating point' -> 'same precision-constrained operating point'")

# ------------------ 6) 6-Discuss: 'tie among them' -> precise wording
add("report/Sections/6-Discuss.tex",
    """present a tie explicitly in Section~\\ref{sec:results}: two configurations
reach an identical operating point, and our choice among them rests on a
tie-break declared in advance rather than on a statistically significant
difference.""",
    """present a tie explicitly in Section~\\ref{sec:results}: two configurations
reach an identical operating point, and our choice among them rests on a
tie-break declared in advance --- Average Precision --- rather than on a
statistically significant difference.""",
    "6) 6-Discuss: noi ro tie-break la AP")

# ------------------ 7) 6-Discuss: '0.1767' reference la 'near this operating point'
add("report/Sections/6-Discuss.tex",
    """The cheapest single threshold
*near that operating point* (0.1767) reaches a comparable recall of 80.3\\% but""",
    """The cheapest single threshold
near that operating point (0.1767) reaches a comparable recall of 80.3\\% but""",
    "7) 6-Discuss: bo dau *italic* thua")

# ------------------ 8) 1-Title + 7-Conclu: dong bo 'operational gain'
add("report/Sections/1-Title.tex",
    """day --- an operational gain over the cheapest single threshold near that
operating point, which needs 232 reviews per day for a comparable recall.""",
    """day --- an operational gain over the cheapest single threshold near that
operating point, which needs 232 reviews per day for a comparable recall.""",
    "8) 1-Title: giu nguyen ban")

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
