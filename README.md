# Credit Card Fraud Detection — Handling Class Imbalance and Designing a Cost-Aware Operating Policy

**Final Report · Group 7 · College of Technology, Faculty of Data Science and Artificial Intelligence, National Economics University, Hanoi**

Course: Data Mining (DA) · Autumn 2026 · National Economics University, Hanoi

---

## 1. Problem

Credit card fraud is imbalanced to the extreme: on the ULB dataset, 142 of 85,118 held-out transactions are fraudulent (0.167 %, a 1 : 598.8 ratio). A classifier that labels everything legitimate reaches 99.83 % accuracy and catches no fraud at all. This project therefore treats the problem as a **business decision problem** rather than a pure classification exercise: how much fraud can a bank catch, at what cost to its customers and its analysts?

## 2. Headline result

| | |
|---|---|
| Best model | Random Forest + SMOTE (1 : 100) |
| Operating point (test-tuned) | precision 0.9569, recall 0.7817, F1 0.8605, cost \$170.45 per 85,118 transactions |
| Operating point (leakage-free, out-of-fold threshold) | recall 0.7324, cost \$208.30 |
| Recommended policy | **Two-tier**: auto-block ≥ 0.810, analyst review 0.175 – 0.810 |
| Two-tier outcome | **recall 0.8099 at \$154.65**, only **70 analyst reviews/day** (0.70 analyst) |
| Throughput | 0.045 ms per transaction; compute under USD 2.30/year at 10 M txns/day |

The two-tier policy is an **operational** win, not a claim of a lower business cost: the unconstrained global cost minimum is \$149.70 at threshold 0.0905, but it needs 301.7 reviews/day — three times the capacity of a single analyst. The two-tier design reaches a slightly *higher* recall at a slightly *lower* cost while cutting analyst workload by roughly 70 % at comparable recall.

## 3. Pipeline

```
load & audit  →  clean  →  feature engineering  →  stratified split (seed 42)
                                                     │
             ┌───────────────────────────────────────┴──────────────────────────┐
             │  imbalance benchmark (5 model families × 5 techniques, 27 configs) │
             │  →  threshold selection at a 95 % precision floor                 │
             │  →  two-tier policy search under a 100 reviews/day capacity      │
             │  →  cost model  C = n_FN · 5.45 + n_FP · 0.30                   │
             │  →  explainability (permutation importance, SHAP)                │
             │  →  calibration, latency, business questions                    │
             └──────────────────────────────────────────────────────────────┘
```

Resampling is performed **inside** an `imblearn` `Pipeline`, so synthetic examples are generated per training fold and never see validation rows. The scaler is fitted inside the pipeline on training data only.

## 4. Repository layout

```
src/                 pipeline modules (config, data, features, modeling, evaluation)
                     + numbered S10/S11 scripts that regenerate every table & chart
notebooks/           6 executed Jupyter notebooks (S0 – S5)
artifacts/tables/    44 result tables (CSV) — the numeric backbone of the report
artifacts/charts/    33 figures (PNG) used by the report
report/              LaTeX source of the report (Sections/*.tex, main.tex)
charts/              EDA figures
```

`artifacts/models/` (trained `.joblib` models, ~618 MB) and the raw `creditcard.csv` are **not** committed: they are large binaries, and the dataset is public on Kaggle.

## 5. Reproducing

```bash
pip install -r requirements.txt
```

Then run the notebooks in order (`00_setup_and_split.ipynb` → `05_cost_analysis.ipynb`), or regenerate the report artifacts directly:

```bash
python src/s10_policy_corrected.py     # two-tier policy + per-day normalisation
python src/s10_regen_charts.py         # report figures
python src/s10_c_final_policy.py       # policy comparison tables
```

The random seed is fixed at **42** throughout, so every figure in the report is exactly reproducible.

### Daily-rate normalisation (important)

The cleaned dataset holds 283,726 transactions over ≈ 48 h, i.e. **141,863 transactions/day**. The held-out test set has 85,118 rows — that is **0.6 days** of stream, not two days. Every test-set count is therefore converted to a daily rate by the factor

$$\frac{1}{0.6} = \frac{5}{3}$$

Getting this wrong understates all workloads and costs by a factor of 3.33. See `report/Sections/8-Appendix.tex` and `src/s10_policy_corrected.py`.

## 6. Honest limitations

- Only ~48 h of data from one region; no seasonality, no temporal split.
- Operating thresholds (benchmark, single-threshold and two-tier) were selected on test-set predictions. The magnitude of this bias was quantified at **4.9 percentage points** of recall for the single-threshold case; the two-tier thresholds (0.810 / 0.175) must be re-derived out-of-fold before use operationally.
- The USD 0.30 review cost is an explicit assumption of ours, not a published figure. `report/Sections/5-Cost.tex` gives the sensitivity analysis.
- `V1`–`V28` are anonymised PCA components and cannot be given a business meaning.
- With 142 test frauds, differences below a few percentage points should not be over-interpreted.

## 7. Report

The compiled report is `report/main.pdf` (20 pages including references). Build it with:

```bash
cd report
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

## 8. Data source

Université Libre de Bruxelles, *Credit Card Fraud Detection* dataset, via Kaggle: <https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud>. Licensed for research use.

## 9. Acknowledgements

Group 7 — Data Mining (DA), Autumn 2026. Special thanks to the instructor for the guidance on the cost-aware framing of the project.
