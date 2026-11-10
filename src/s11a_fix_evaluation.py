"""S11a · Sua 4 loi da phat hien trong danh gia report + lam roi logic tong the.
KHONG doi bat ky con so nao (tat ca da verify khop artifact).

1) 2-Intro.tex : "a observation" -> "an observation"          (loi ngu phap)
2) 4-Results.tex: "Three configurations tie" -> "Two"           (SMOTE 1:20
   co recall 0,7606 / $186,80, KHONG tie)
3) 6-Discuss.tex + 7-Conclu.tex + 1-Title.tex: "cheapest single
   threshold (0.1767)" -> "cheapest single threshold near that
   operating point" (global min la 0.0905 $149,70)   (mau thuan noi tai)
4) 5-Cost.tex Table 17 Q5: doi "discards 90% of the fraud" ->
   "catches only 9,9% of the fraud"                (nhat voi §5.4)
   + "two thirds" -> "roughly two thirds (64,5%)"
5) 4-Results.tex Table 3: "Zero amounts 1,808" -> ghi ro "across the
   full cleaned dataset", them "of which 25 fraudulent"
6) 6-Discuss.tex: "three configurations reach an identical operating
   point" -> "two configurations"
"""
from pathlib import Path

EDITS = []


def add(path, old, new, tag):
    EDITS.append((path, old, new, tag))


# ---------------------------------------------------------------- 1) ngu phap
add("report/Sections/2-Intro.tex",
    """class-imbalance techniques across five model families on the ULB dataset; (ii) a
observation that a wider hyper-parameter search \\emph{degrades} test""",
    """class-imbalance techniques across five model families on the ULB dataset; (ii) an
observation that a wider hyper-parameter search \\emph{degrades} test""",
    "1) 'a observation' -> 'an observation'")

# ------------------------------------------------- 2) so config tie (chi 2)
add("report/Sections/4-Results.tex",
    """\\paragraph*{Three configurations tie at the operating point, and we say so.}
Random Forest with SMOTE at 1:100, Random Forest with SMOTE at 1:20 (under a
different selection rule) and Random Forest without resampling all reach
recall 0.7817 at USD 170.45 on the test set.""",
    """\\paragraph*{Two configurations tie at the operating point, and we say so.}
Random Forest with SMOTE at 1:100 and Random Forest without resampling both
reach recall 0.7817 at USD 170.45 on the test set.""",
    "2) 'three configurations tie' -> 'two'")

# ------------------------------------------- 6) cung 2 config tie (Discuss)
add("report/Sections/6-Discuss.tex",
    """present a tie explicitly in Section~\\ref{sec:results}: three configurations
reach an identical operating point, and our choice among them rests on a""",
    """present a tie explicitly in Section~\\ref{sec:results}: two configurations
reach an identical operating point, and our choice among them rests on a""",
    "6) 'three configurations' -> 'two' (Discuss)")

# --------------------------------- 3) "cheapest single threshold" -> scope
add("report/Sections/6-Discuss.tex",
    """81.0\\% recall with only 70 reviews per day. The cheapest single threshold
(0.1767) reaches a comparable recall of 80.3\\% but needs 232 reviews per day,
which is more than twice the available capacity.""",
    """81.0\\% recall with only 70 reviews per day. The cheapest single threshold
*near that operating point* (0.1767) reaches a comparable recall of 80.3\\% but
needs 232 reviews per day, which is more than twice the available capacity.""",
    "3) scope 'cheapest single threshold' (Discuss)")

add("report/Sections/7-Conclu.tex",
    """operational improvement rather than a re-labelling: the comparable recall
reached by the cheapest single threshold (0.1767, recall 0.8028) would need 232
reviews per day, more than twice the available capacity.""",
    """operational improvement rather than a re-labelling: the comparable recall
reached by the cheapest single threshold near that operating point (0.1767,
recall 0.8028) would need 232 reviews per day, more than twice the available
capacity.""",
    "3) scope 'cheapest single threshold' (Conclusion)")

add("report/Sections/1-Title.tex",
    """day --- an operational gain over the cheapest single threshold, which needs
232 reviews per day for a comparable recall.""",
    """day --- an operational gain over the cheapest single threshold near that
operating point, which needs 232 reviews per day for a comparable recall.""",
    "3) scope 'cheapest single threshold' (Abstract)")

# ------------------------------------------------ 4) Table 17 Q5 + two thirds
add("report/Sections/5-Cost.tex",
    """5 & Score all transactions, or only those above an amount threshold? & \\textbf{Score all.} Filtering above \\$500 (3.2\\% of traffic) discards \\textbf{90\\%} of the fraud; two thirds of missed frauds are below \\$10 \\\\""",
    """5 & Score all transactions, or only those above an amount threshold? & \\textbf{Score all.} Filtering above \\$500 keeps only 3.2\\% of the traffic but catches just \\textbf{9.9\\%} of the fraud; roughly two thirds of the missed frauds are below \\$10 \\\\""",
    "4) Q5: 'discards 90% of the fraud' -> 'catches only 9,9%'")

# 'two thirds' -> precise (3 noi)
add("report/Sections/5-Cost.tex",
    """The reason is visible in the false-negative analysis: two thirds of missed
frauds are below \\$10,""",
    """The reason is visible in the false-negative analysis: roughly two thirds of
the missed frauds (64.5\\%) are below \\$10,""",
    "4) 'two thirds' -> 'roughly two thirds (64,5%)' (Cost)")

add("report/Sections/4-Results.tex",
    """\\paragraph*{What the model cannot catch.}
Figure~\\ref{fig:waterfallfn} explains the 31 missed frauds. Two thirds of them
have amounts below \\$10,""",
    """\\paragraph*{What the model cannot catch.}
Figure~\\ref{fig:waterfallfn} explains the 31 missed frauds. Roughly two thirds
of them (64.5\\%) have amounts below \\$10,""",
    "4) 'two thirds' -> 'roughly two thirds (64,5%)' (Results)")

# --------------------------------------------- 5) Table 3 zero amount scope
add("report/Sections/4-Results.tex",
    """Zero amounts & 1,808 retained, flagged by
Is\\_Zero\\_Amount \\\\""",
    """Zero amounts & 1,808 in the full cleaned dataset (25 of them fraudulent); retained, flagged by Is\\_Zero\\_Amount \\\\""",
    "5) Table 3: scope the 1,808 zero amounts")

# ------------------------------------------------------------------ apply
for path, old, new, tag in EDITS:
    p = Path(path)
    s = p.read_text(encoding="utf-8")
    if old not in s:
        print(f"[SKIP] {tag}  ({path})")
        continue
    s = s.replace(old, new, 1)
    p.write_text(s, encoding="utf-8")
    print(f"[OK]   {tag}")
