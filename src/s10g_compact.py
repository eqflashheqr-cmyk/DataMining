"""S10g · Cắt 2 trang: giảm line-spacing + thu nhỏ figure + giảm spacing list."""
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. main.tex: giảm khoảng cách dòng và spacing của list
# ---------------------------------------------------------------------------
p = Path("report/main.tex")
s = p.read_text(encoding="utf-8")

old = r"""\setlength{\abovecaptionskip}{4pt}
\setlength{\belowcaptionskip}{0pt}"""

new = r"""\setlength{\abovecaptionskip}{4pt}
\setlength{\belowcaptionskip}{0pt}
% Slightly tighter leading: at \footnotesize the default baseline of 9.5 pt is
% generous for a technical report, and 6% recovers roughly one page of text.
\renewcommand{\baselinestretch}{0.94}
\setlength{\parskip}{0pt}
\setlength{\parsep}{0pt}
\setlength{\topsep}{3pt plus 1pt minus 1pt}
\setlength{\itemsep}{1pt plus 1pt minus 1pt}
\setlength{\parindent}{0pt}"""

if s.count(old) != 1:
    raise SystemExit(f"main.tex anchor = {s.count(old)}")
s = s.replace(old, new)
p.write_text(s, encoding="utf-8")
print("[ok] main.tex: leading + list spacing")

# ---------------------------------------------------------------------------
# 2. Thu nhỏ các figure cao
# ---------------------------------------------------------------------------
FIGS = {
    "report/Sections/4-Results.tex": [
        (r"\includegraphics[width=\textwidth]{Images/charts/s7_pr_roc_operating_point.png}",
         r"\includegraphics[width=0.95\textwidth]{Images/charts/s7_pr_roc_operating_point.png}"),
        (r"\includegraphics[width=0.82\textwidth]{Images/charts/s5_aucpr_by_technique.png}",
         r"\includegraphics[width=0.70\textwidth]{Images/charts/s5_aucpr_by_technique.png}"),
        (r"\includegraphics[width=0.92\textwidth]{Images/charts/s8_shap_summary.png}",
         r"\includegraphics[width=0.78\textwidth]{Images/charts/s8_shap_summary.png}"),
        (r"\includegraphics[width=\textwidth, trim=0 0 0 0, clip]{Images/charts/s8_shap_waterfall_fn.png}",
         r"\includegraphics[width=0.90\textwidth, trim=0 0 0 0, clip]{Images/charts/s8_shap_waterfall_fn.png}"),
    ],
    "report/Sections/3-Method.tex": [
        (r"\includegraphics[width=\textwidth]{Images/charts/s5_heatmap_model_x_imbalance.png}",
         r"\includegraphics[width=0.90\textwidth]{Images/charts/s5_heatmap_model_x_imbalance.png}"),
        (r"\includegraphics[width=0.85\textwidth]{Images/charts/feature_engineering_evidence.png}",
         r"\includegraphics[width=0.72\textwidth]{Images/charts/feature_engineering_evidence.png}"),
    ],
    "report/Sections/5-Cost.tex": [
        (r"\includegraphics[width=\textwidth]{Images/charts/s9_rule_vs_model.png}",
         r"\includegraphics[width=0.88\textwidth]{Images/charts/s9_rule_vs_model.png}"),
        (r"\includegraphics[width=0.95\textwidth]{Images/charts/s10_capacity_tradeoff.png}",
         r"\includegraphics[width=0.88\textwidth]{Images/charts/s10_capacity_tradeoff.png}"),
        (r"\includegraphics[width=\textwidth]{Images/charts/s9_amount_threshold_analysis.png}",
         r"\includegraphics[width=0.90\textwidth]{Images/charts/s9_amount_threshold_analysis.png}"),
        (r"\includegraphics[width=0.92\textwidth]{Images/charts/s9_two_tier_diagram.png}",
         r"\includegraphics[width=\textwidth]{Images/charts/s9_two_tier_diagram.png}"),
    ],
}

for fname, pairs in FIGS.items():
    pp = Path(fname)
    ss = pp.read_text(encoding="utf-8")
    for old_s, new_s in pairs:
        if ss.count(old_s) != 1:
            raise SystemExit(f"{fname}: anchor {old_s[:60]} = {ss.count(old_s)}")
        ss = ss.replace(old_s, new_s)
    pp.write_text(ss, encoding="utf-8")
    print(f"[ok] {fname}: {len(pairs)} figure widths")
