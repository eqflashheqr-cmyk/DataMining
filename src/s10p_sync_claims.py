"""S10p · Đồng bộ các claim 'Pareto improvement' / 'dominates' ở Discuss,
Conclu, Title -- sửa theo phát hiện §1.2: hai tầng KHÔNG cải thiện cost so
với ngưỡng đơn tối ưu toàn cục; nó giảm tải analyst + nằm trong capacity."""
from pathlib import Path

EDITS = [
    # --- 6-Discuss.tex ---
    ("report/Sections/6-Discuss.tex",
     """The two-tier policy resolves the dilemma, reaching
81.0\\% recall at lower cost with only 70 reviews per day --- a Pareto
improvement over the best single threshold, which needs 232 reviews per day for
the same recall. This is the clearest path from a research artefact to an
operational deployment.""",
     """The two-tier policy resolves the dilemma, reaching
81.0\\% recall with only 70 reviews per day. The cheapest single threshold
(0.1767) reaches a comparable recall of 80.3\\% but needs 232 reviews per day,
which is more than twice the available capacity. The gain is therefore
operational rather than financial: the two-tier design buys the analyst-time
saving that the cost model alone does not price. This is the clearest path from
a research artefact to an operational deployment."""),
    # --- 6-Discuss.tex recommendation 1 ---
    ("report/Sections/6-Discuss.tex",
     """    \\item \\textbf{Deploy the two-tier policy.} Auto-block above 0.810, route
    the 0.175--0.810 band to analysts, approve the remainder. It attains higher
    recall at lower cost than any single threshold while requiring only 70
    reviews per day, i.e.\\ inside the capacity of one analyst.""",
     """    \\item \\textbf{Deploy the two-tier policy.} Auto-block above 0.810, route
    the 0.175--0.810 band to analysts, approve the remainder. It attains higher
    recall than any single threshold that respects the capacity constraint,
    while requiring only 70 reviews per day, i.e.\\ inside the capacity of one
    analyst."""),
    # --- 7-Conclu.tex ---
    ("report/Sections/7-Conclu.tex",
     """Because auto-blocking consumes no analyst
time, the two tiers can be tuned independently, and the result is a genuine
Pareto improvement rather than a re-labelling: the same recall reached by the
best single threshold would need 232 reviews per day.""",
     """Because auto-blocking consumes no analyst
time, the two tiers can be tuned independently, and the result is an
operational improvement rather than a re-labelling: the comparable recall
reached by the cheapest single threshold (0.1767, recall 0.8028) would need 232
reviews per day, more than twice the available capacity."""),
]

for path, old, new in EDITS:
    p = Path(path)
    s = p.read_text(encoding="utf-8")
    if old not in s:
        print("[skip]", path, old[:50].replace("\n", " "))
        continue
    s = s.replace(old, new, 1)
    p.write_text(s, encoding="utf-8")
    print("[ok]", path, "->", new[:45].replace("\n", " "))
