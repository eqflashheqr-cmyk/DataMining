"""S10r · Appendix: sửa 3 lỗi còn sót
  (1) 'pinned' -> chỉ các package lõi được pin, jupyter/notebook dùng >= (nói rõ).
  (2) Đếm artifact: 44 bảng (không phải 43), 33 hình -> giữ 33, sửa 43->44.
  (3) Mô tả pitfall ColumnTransformer sai (không liên quan 'tên cột remainder')
      -> thay bằng mô tả đúng: remainder='drop' yêu cầu feature list tường minh.
"""
from pathlib import Path

p = Path("report/Sections/8-Appendix.tex")
s = p.read_text(encoding="utf-8")

OLD1 = """All experiments were executed with Python 3.11.9 on Windows. The dependency set
is pinned in \\texttt{requirements.txt} (pandas 2.3.3, numpy 2.2.6, scipy 1.17.1,
scikit-learn 1.9.1, imbalanced-learn 0.14.2, xgboost 3.2.0, shap 0.51.0,
joblib 1.6.0, matplotlib 3.10.9, seaborn 0.13.2, plotly 7.1.0)."""

NEW1 = """All experiments were executed with Python 3.11.9 on Windows. The numerical
core of the dependency set is pinned exactly in \\texttt{requirements.txt}
(pandas 2.3.3, numpy 2.2.6, scipy 1.17.1, scikit-learn 1.9.1,
imbalanced-learn 0.14.2, xgboost 3.2.0, shap 0.51.0, joblib 1.6.0,
matplotlib 3.10.9, seaborn 0.13.2, plotly 7.1.0); only the notebook tooling
(jupyter, notebook) is left as a lower bound, since it does not affect any
reported number. Every figure and table in this report can therefore be
regenerated from the pinned versions alone."""

OLD2 = """\\texttt{final\\_model\\_metadata.joblib}; the directory \\texttt{artifacts/tables/}
holds 43 result tables and \\texttt{artifacts/charts/} 33 figures."""

NEW2 = """\\texttt{final\\_model\\_metadata.joblib}; the directory \\texttt{artifacts/tables/}
holds 44 result tables and \\texttt{artifacts/charts/} 33 figures."""

OLD3 = """Three implementation subtleties were resolved during the work and are recorded
here because they affect reproducibility. First, \\texttt{ColumnTransformer} must
be given an explicit feature list with \\texttt{remainder="drop"}, otherwise the
string \\texttt{"remainder"} is interpreted as a column name."""

NEW3 = """Three implementation subtleties were resolved during the work and are recorded
here because they affect reproducibility. First, because the split has already
engineered the five new columns, the \\texttt{ColumnTransformer} is declared
with \\texttt{remainder="drop"} and an explicit list of the columns to
transform, so that any column not named is discarded deliberately rather than
passed through by accident."""

for old, new in [(OLD1, NEW1), (OLD2, NEW2), (OLD3, NEW3)]:
    if old not in s:
        print("[skip]", old[:60].replace("\n", " "))
        continue
    s = s.replace(old, new, 1)
    print("[ok]", new[:55].replace("\n", " "))

p.write_text(s, encoding="utf-8")
