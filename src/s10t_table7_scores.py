"""S10t · Table 7: thêm cột GIÁ TRỊ permutation importance (lỗi §3.12).
Dùng regex để không phụ thuộc whitespace."""
import re
from pathlib import Path

p = Path("report/Sections/4-Results.tex")
s = p.read_text(encoding="utf-8")

# 1. caption: them ghi chu "8/35" + duong danh CSV
old_cap = "directly from \\texttt{feature\\_importances\\_} of the fitted forest.}"
new_cap = ("directly from \\texttt{feature\\_importances\\_} of the fitted forest. The table shows\n"
           "the eight highest-ranked features by permutation importance out of 35; the\n"
           "remaining 27 are omitted for space, and the full ranking is archived in\n"
           "\\texttt{artifacts/tables/s8\\_importance\\_comparison.csv}.}")
assert s.count(old_cap) == 1, s.count(old_cap)
s = s.replace(old_cap, new_cap, 1)

# 2. header: them cot Perm. imp.
old_hdr = """\\textbf{Feature} & \\textbf{Permutation rank} & \\textbf{SHAP rank} & \\textbf{Impurity rank} \\\\"""
new_hdr = """\\textbf{Feature} & \\textbf{Perm. imp.} & \\textbf{Permutation rank} & \\textbf{SHAP rank} & \\textbf{Impurity rank} \\\\"""
assert s.count(old_hdr) == 1
s = s.replace(old_hdr, new_hdr, 1)

# 3. rows: them gia tri permutation importance
ROWS = {
    "Amount\\_log": "0.0819",
    "Amount": "0.0801",
    "V14": "0.0629",
    "V17": "0.0431",
    "V4": "0.0551",
    "V9": "0.0392",
    "Day": "0.0099",
    "Hour\\_of\\_Day": "0.0104",
    "Is\\_Night": "0.0008",
}
n = 0
for feat, val in ROWS.items():
    pat = re.compile(r"(\\texttt\{" + re.escape(feat) + r"\}) & ")
    m = pat.search(s)
    assert m, feat
    s = s[:m.end()] + val + " & " + s[m.end():]
    n += 1

# 4. tabular: 4 cot -> 5 cot
old_tab = "\\begin{tabular}{lrrr}\n\\toprule\n\\textbf{Feature} & \\textbf{Perm. imp.}"
new_tab = "\\begin{tabular}{lrrrr}\n\\toprule\n\\textbf{Feature} & \\textbf{Perm. imp.}"
assert s.count(old_tab) == 1
s = s.replace(old_tab, new_tab, 1)

p.write_text(s, encoding="utf-8")
print(f"[ok] Table 7 updated ({n} rows)")
