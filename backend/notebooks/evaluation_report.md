# Model evaluation report

## Setup

- **Model:** AutoGluon predictor loaded from `ag_insurance/`
- **Test set:** 268 rows (holdout from prepared data)
- **Target:** charges (in original dollars; predictions inverse-transformed from log-scale)

## Metrics

| Metric | Value |
|--------|--------|
| MAE | 1839.60 |
| RMSE | 4257.26 |
| MAPE | 15.58 % |
| SMAPE | 8.80 % |
