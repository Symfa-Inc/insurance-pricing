# Train Module

`src/train` contains the end-to-end ML pipeline used to generate EDA outputs, prepare data, train the AutoGluon model and evaluate quality.

The module is designed with two execution modes:

1. run the whole pipeline from one entrypoint (`src/train/main.py`)
2. run each stage independently (`src/train/stages/*.py`)

## What This Module Does

- Loads source insurance data.
- Fits and saves a reusable feature/target transformer artifact.
- Builds transformed train/test datasets.
- Trains an AutoGluon `TabularPredictor`.
- Evaluates model quality and writes a Markdown report.
- Optionally runs EDA and writes report + figures.

## Structure

```text
src/train/
├── main.py
├── settings.py
└── stages/
    ├── prepare_data.py
    ├── train_model.py
    ├── evaluate_model.py
    └── run_eda.py
```

## Run The Whole Pipeline

From `backend/`:

```bash
uv run python src/train/main.py
```

Default stage order:
- `prepare`
- `train`
- `evaluate`

Run custom stage selection:

```bash
uv run python src/train/main.py --stages prepare train evaluate
uv run python src/train/main.py --stages all
```

## Run Individual Stages

From `backend/`:

```bash
uv run python src/train/stages/prepare_data.py
uv run python src/train/stages/train_model.py
uv run python src/train/stages/evaluate_model.py
uv run python src/train/stages/run_eda.py
```

## Stage Artifacts

### `run_eda.py`

Purpose:
- run exploratory analysis and generate plots/report

Reads:
- `backend/data/source.csv`

Writes:
- `backend/reports/eda_report.md`
- `backend/reports/_eda_figures/*.png`

### `prepare_data.py`

Purpose:
- split source dataset into train/test
- fit reusable transformer on train split
- transform features/target for model training

Reads:
- `backend/data/source.csv`

Writes:
- `backend/models/feature_transformer.joblib`
- `backend/data/train.csv`
- `backend/data/test.csv`

### `train_model.py`

Purpose:
- train AutoGluon model on prepared train data

Reads:
- `backend/data/train.csv`

Writes:
- `backend/models/ag_insurance/` (AutoGluon predictor directory)

### `evaluate_model.py`

Purpose:
- evaluate trained model on prepared test split
- inverse-transform target back to original charge space

Reads:
- `backend/models/ag_insurance/`
- `backend/models/feature_transformer.joblib`
- `backend/data/test.csv`

Writes:
- `backend/reports/evaluation_report.md`

## Settings And Environment Variables

`settings.py` centralizes configuration via `ScriptsSettings`.

Useful environment variables:
- `SOURCE_DATA_PATH`
- `TRAIN_DATA_PATH`
- `TEST_DATA_PATH`
- `TRANSFORMER_PATH`
- `PREDICTOR_DIR`
- `EVALUATION_REPORT_PATH`
- `EDA_REPORT_PATH`
- `EDA_FIGURES_DIR`
- `TIME_LIMIT`
- `NUM_BAG_FOLDS`
- `NUM_BAG_SETS`
- `OPENAI_API_KEY` (only needed for LLM narrative text in EDA)

Example:

```bash
TRANSFORMER_PATH=backend/models/feature_transformer.joblib \
PREDICTOR_DIR=backend/models/ag_insurance \
uv run python src/train/main.py --stages prepare train evaluate
```
