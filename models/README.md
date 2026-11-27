# Shared model – cancellation prediction (Random Forest)

One shared classifier predicting whether a booking will be canceled (`is_canceled`).
All XAI analyses (PFI, ICE, ALE, ...) are built on top of **this one model and this one
train/test split**, so results of different methods are comparable.

## Files

| File | Content |
|---|---|
| `train_cancellation_rf.py` | Deterministic training script (fixed `random_state`) |
| `cancellation_rf/model.joblib` | Fitted sklearn `Pipeline`: one-hot encoding + `RandomForestClassifier` |
| `cancellation_rf/train.csv` | Training split (94 846 rows): model features + `is_canceled` |
| `cancellation_rf/test.csv` | Test split (23 712 rows): model features + `is_canceled` |
| `cancellation_rf/metadata.json` | Features, excluded columns, hyperparameters, library versions, metrics |

Regenerate everything (from the repository root):

```bash
uv run python models/train_cancellation_rf.py
```

Don't edit the files in `cancellation_rf/` by hand. If you retrain the model, commit the
script and all outputs together.

## Usage in an analysis

From a notebook in `analyses/<method>/`:

```python
import joblib
import pandas as pd

MODEL_DIR = "../../models/cancellation_rf"
model = joblib.load(f"{MODEL_DIR}/model.joblib")
test = pd.read_csv(f"{MODEL_DIR}/test.csv")
X_test, y_test = test.drop(columns="is_canceled"), test["is_canceled"]

proba = model.predict_proba(X_test)[:, 1]   # P(canceled)
```

- The model takes the **raw feature columns**: strings for categorical features, `float64`
  for the rest. Numeric features are floats even when they hold counts, because sklearn's
  `partial_dependence` (ICE/PDP) refuses integer columns. `pd.read_csv` reads them back as
  floats. Encoding happens inside the pipeline, so XAI methods work on the original
  features. For example, PFI permutes `market_segment` as a whole, not single dummies.
  Use the whole `model` with sklearn tools such as
  `sklearn.inspection.permutation_importance(model, X_test, y_test, ...)` or
  `PartialDependenceDisplay.from_estimator(model, X_test, ..., kind="individual")`.
- Compute explanations on **`test.csv`** (data the model has not seen). Use `train.csv` only
  when a method explicitly needs training data, such as a background sample.
- To compare the hotels, filter by `X_test["hotel"]`. The model is shared, and `hotel` is one
  of its features.
- The forest itself (for tree-specific methods such as SHAP `TreeExplainer`) is
  `model.named_steps["model"]`. It works on encoded columns:
  `model.named_steps["preprocess"].transform(X_test)`.

## Features (21)

**Categorical (7):** `hotel`, `meal`, `market_segment`, `distribution_channel`,
`reserved_room_type`, `deposit_type`, `customer_type`

**Numeric (14):** `lead_time`, `arrival_month`, `total_nights`, `adults`, `children`, `babies`,
`is_repeated_guest`, `previous_cancellations`, `previous_bookings_not_canceled`,
`days_in_waiting_list`, `adr`, `total_of_special_requests`, `has_agent`, `has_company`

Derived features (the rest are copied from `data/processed/hotel_bookings_clean.csv`):

- `arrival_month` – `arrival_date_month` as a number 1–12, so ICE/ALE give a seasonal curve.
- `has_agent` / `has_company` – 1 if the `agent` / `company` id is filled in.

## Excluded columns

| Column | Reason |
|---|---|
| `required_car_parking_spaces` | Leakage: no booking with a parking space is ever canceled (0 % of 7 392), it is recorded on arrival |
| `country` | Artefact: country is verified only at check-in, so canceled bookings keep the default PRT (57 % vs 24 % cancel rate) |
| `assigned_room_type`, `booking_changes` | Post-booking information |
| `arrival_date_year` | Time trend; 2015 and 2017 are incomplete years |
| `agent`, `company` | High-cardinality ids (333 / 347 values), replaced by `has_agent` / `has_company` |
| `arrival_date_month`, `arrival_date_week_number`, `arrival_date_day_of_month`, `arrival_date` | Redundant date columns, replaced by `arrival_month` |
| `stays_in_weekend_nights`, `stays_in_week_nights` | Redundant with `total_nights` |
| `total_guests` | Redundant with `adults` + `children` + `babies` |

From every group of redundant columns only one variant is kept. Correlated features distort
PFI, which splits importance between the "twins", and ICE/PDP, where permutation creates
impossible combinations.

## Split and model

- Stratified 80/20 split by `hotel` × `is_canceled`, `random_state = 42`.
- `RandomForestClassifier(n_estimators=300, max_features="sqrt", min_samples_leaf=5,
  random_state=42)`. `min_samples_leaf` is a trade-off between accuracy and file size, see
  the comment in the script: fully grown trees have OOB AUC 0.915 but 132 MB.

## Performance (test set, threshold 0.5)

| | ROC AUC | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|---|
| All | 0.903 | 0.833 | 0.861 | 0.657 | 0.746 |
| City Hotel | 0.912 | | | | |
| Resort Hotel | 0.874 | | | | |

The full metrics, including per-hotel ones and the confusion matrix, are in
`cancellation_rf/metadata.json`.

## Known limitations

- `deposit_type = Non Refund` is canceled in ~99 % of cases. This is a known quirk of the
  dataset. The feature is kept because it is known at booking time and is a topic of the
  project, but expect it to dominate the explanations.
- Exact duplicate rows are kept in the data (group bookings, see `data/processed/codebook.md`).
  With a random split some duplicates end up in both train and test, which inflates the test
  metrics slightly.
- XAI methods explain **the model**, not reality. Any artefact the model learned shows up in
  the explanations as an "effect".
