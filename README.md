# Buyer-Intent-Revenue-Intelligence-Engine

An interactive analytics dashboard that classifies Amazon products by the type of buyer they attract, explains each classification with SHAP, and identifies products placed in the wrong tier along with the revenue lost as a result.

## Objectives

1. **Classify buyer intent.** Assign every product to a buyer segment (Deal Seeker, Quality First, Social Proof, Niche Explorer) based on pricing, trust, rating and review signals.
2. **Explain the model.** Show which features drive each classification so that results are transparent and auditable, not a black box.
3. **Quantify the revenue gap.** Estimate the revenue uplift available if products reach the right buyer segment, and the leakage caused by misplacement.
4. **Recommend action.** Give sellers and category managers a prioritised, product-level fix for every mismatched listing.

## Key Findings

- The model reaches a **Macro F1 of 0.9948** on a 5-class, heavily imbalanced problem.
- **The discount paradox:** a high savings ratio (above 0.35) carries a negative SHAP weight for the Quality First segment. Heavy discounting repels the buyers who deliver the highest revenue per product.
- The catalogue of **1,463 products** shows a revenue opportunity of roughly **₹149 Cr**, with about **₹12 Cr** of leakage from **611 misplaced products**.

## Features

| Module | Purpose |
|---|---|
| Home | Executive overview, segment distribution and headline insights |
| Market Intelligence | Segment mix, revenue landscape and placement quality by category |
| ML Engine Room | Model performance, cross-validation results and training diagnostics |
| Explainability Studio | SHAP bar, beeswarm and waterfall views of classification drivers |
| Mismatch Alerts | Misplaced products with severity, SHAP driver and blocker, and up to three prioritised fixes each |
| Buyer DNA | Buyer archetype fingerprints, radar profiles and top products |
| Product Intelligence | Product search, classification decoding and segment upgrade simulation |

**Platform-wide capabilities**

- Global category and segment filters that update every page and KPI.
- A KPI strip covering products in view, mismatch rate, revenue opportunity, leakage, average uplift and top category.
- Mismatch Alerts adds leakage concentration, largest leaking category, and trust, rating and discount gaps between mismatched and well placed products.
- Rule-based fix engine that turns each product's own numbers (savings ratio, trust, rating, review volume, target segment) into specific actions.
- A shared light theme with a consistent segment palette and status colors (green for good, amber for caution, red for loss).

## Methodology

| Component | Detail |
|---|---|
| Engineered features | 69 |
| Model | XGBoost ensemble |
| Class imbalance | SMOTE with k=5 resampling on training data |
| Tuning | Optuna hyperparameter search, 50 trials |
| Validation | 5-fold stratified cross-validation, plus a held-out test set |
| Explainability | SHAP values per product and per class |

## Tech Stack

Python, Streamlit, Pandas, NumPy, Plotly, XGBoost, SHAP, Optuna, imbalanced-learn.

## Project Structure

```
.
├── app.py                  Entry point: config, theme, sidebar, filters, routing
├── .streamlit/config.toml  Light theme settings
├── data/                   Processed features, importances and SHAP values
├── pages/
│   ├── p0_home.py
│   ├── p1_market.py
│   ├── p2_model.py
│   ├── p3_shap.py
│   ├── p4_mismatch.py
│   ├── p5_dna.py
│   └── p6_product.py
└── utils/
    ├── style.py            Segment colors, formatting helpers
    ├── theme.py            Design system, CSS and Plotly template
    └── data_loader.py      Cached data loading and filtering
```

## Getting Started

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the dashboard
streamlit run app.py
```

The app expects the processed data files inside the `data/` folder. If a page reports a missing column, check the "Data mapping used by this page" panel at the bottom of Mismatch Alerts and adjust the `CANDIDATES` list at the top of `pages/p4_mismatch.py`.

## How to Use

1. Pick a page from the sidebar navigation.
2. Narrow the analysis with the category and segment filters.
3. Start at Mismatch Alerts to find the highest-leakage products, sort by severity, and follow the recommended fixes.
4. Use Explainability Studio or Product Intelligence to understand why a given product was classified the way it was.

## Limitations

- Revenue uplift and leakage are model-based estimates, not observed sales.
- Fix recommendations are rule-based guidance and should be validated with A/B tests before large-scale rollout.
- Results reflect the current product catalogue and should be refreshed when the data changes.
