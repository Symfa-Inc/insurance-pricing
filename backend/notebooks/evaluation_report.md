# Model evaluation report

## Setup

- **Model:** AutoGluon predictor loaded from `ag_insurance/`
- **Test set:** 268 rows (holdout from prepared data)
- **Target:** charges (in original dollars; predictions inverse-transformed from log-scale)

## Metrics

| Metric | Value |
|--------|--------|
| R² | 0.8258 |
| MAPE | 15.58 % |
| SMAPE | 8.80 % |

## Interpretation

- The R² value is 0.83, which means the model explains 83% of the variation in annual insurance charges. In practical terms, this indicates a strong relationship; the model can effectively predict most of the changes we see in insurance costs based on input factors.
- The MAPE is approximately 15.58%. If we consider a typical annual insurance charge of \$10,000, this means that the predictions made by our model may be off by around \$1,558. While this is a significant difference, it still allows us to make reasonably informed decisions about pricing.
- The SMAPE is about 8.80%, which translates to a portion of the predicted values being reasonably close to the actual charges. In practical terms, this level of accuracy means our predictions are often within about \$880 of the true value for an average charge of \$10,000, which is a clear indicator of reliability.
