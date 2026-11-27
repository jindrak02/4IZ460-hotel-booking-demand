"""Train the shared cancellation-prediction model (Random Forest) for XAI analyses.

Input:  data/processed/hotel_bookings_clean.csv
Output: models/cancellation_rf/model.joblib   - fitted sklearn Pipeline (one-hot encoding + Random Forest)
        models/cancellation_rf/train.csv      - training split, model features + is_canceled
        models/cancellation_rf/test.csv       - test split, model features + is_canceled
        models/cancellation_rf/metadata.json  - features, excluded columns, hyperparameters, versions, metrics

Run from the repository root:

    uv run python models/train_cancellation_rf.py

The whole team builds XAI methods (PFI, ICE, ALE, ...) on top of this ONE model, so the
script is fully deterministic: a fixed random_state drives both the train/test split and
the forest. With the same locked library versions (uv.lock), re-running it reproduces the
same model and the same split.

The saved object is the whole Pipeline, so it takes the raw feature columns of
train.csv / test.csv (strings for categorical features). XAI methods therefore work with
the original features (e.g. permuting `market_segment` as a whole, not single one-hot
dummies) and in their original units.
"""

from __future__ import annotations

import json
import platform
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parent.parent
CLEAN_PATH = ROOT / "data" / "processed" / "hotel_bookings_clean.csv"
OUT_DIR = ROOT / "models" / "cancellation_rf"
MODEL_PATH = OUT_DIR / "model.joblib"
TRAIN_PATH = OUT_DIR / "train.csv"
TEST_PATH = OUT_DIR / "test.csv"
METADATA_PATH = OUT_DIR / "metadata.json"

TARGET = "is_canceled"
RANDOM_STATE = 42
TEST_SIZE = 0.2

MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

# Categorical model inputs (strings; one-hot encoded inside the pipeline).
CATEGORICAL_FEATURES = [
    "hotel",
    "meal",
    "market_segment",
    "distribution_channel",
    "reserved_room_type",
    "deposit_type",
    "customer_type",
]

# Numeric model inputs (passed to the forest as they are).
NUMERIC_FEATURES = [
    "lead_time",
    "arrival_month",                    # DERIVED: arrival_date_month as number 1-12
    "total_nights",
    "adults",
    "children",
    "babies",
    "is_repeated_guest",
    "previous_cancellations",
    "previous_bookings_not_canceled",
    "days_in_waiting_list",
    "adr",
    "total_of_special_requests",
    "has_agent",                        # DERIVED: 1 = booked through a travel agency
    "has_company",                      # DERIVED: 1 = company booking
]

FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES

# Columns of the clean dataset that are deliberately NOT model inputs, with the reason.
EXCLUDED_COLUMNS = {
    "required_car_parking_spaces": "leakage: no booking with a parking space is ever canceled (recorded on arrival)",
    "country": "artefact: country is verified only at check-in, so canceled bookings keep the default PRT",
    "assigned_room_type": "post-booking information (known only at arrival)",
    "booking_changes": "post-booking information (changes accumulate until arrival)",
    "arrival_date_year": "time trend; 2015 and 2017 are incomplete years, does not generalise",
    "agent": "high-cardinality id (333 values); replaced by has_agent",
    "company": "high-cardinality id (347 values); replaced by has_company",
    "arrival_date_month": "redundant date column; replaced by numeric arrival_month",
    "arrival_date_week_number": "redundant with arrival_month",
    "arrival_date_day_of_month": "redundant date column, no seasonal meaning",
    "arrival_date": "redundant date column",
    "stays_in_weekend_nights": "redundant with total_nights",
    "stays_in_week_nights": "redundant with total_nights",
    "total_guests": "redundant with adults + children + babies",
}

RF_PARAMS = {
    "n_estimators": 300,
    "max_features": "sqrt",
    # Trade-off chosen by OOB ROC AUC / compressed file size on the training split:
    #   leaf 1: 0.915 / 132 MB (over GitHub's 100 MB limit), 3: 0.907 / 43 MB,
    #   leaf 5: 0.901 / 29 MB, 10: 0.892 / 18 MB, 20: 0.885 / 12 MB.
    # Larger leaves also make ICE/ALE curves smoother.
    "min_samples_leaf": 5,
    "oob_score": True,
    "n_jobs": -1,
    "random_state": RANDOM_STATE,
}


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive model features from the clean dataset and keep only FEATURES + TARGET."""
    df = df.copy()
    df["arrival_month"] = df["arrival_date_month"].map(
        {name: i for i, name in enumerate(MONTH_ORDER, start=1)}
    ).astype("int64")
    df["has_agent"] = df["agent"].notna().astype("int64")
    df["has_company"] = df["company"].notna().astype("int64")

    unaccounted = set(df.columns) - set(FEATURES) - set(EXCLUDED_COLUMNS) - {TARGET}
    if unaccounted:
        raise ValueError(f"Columns neither used nor excluded: {sorted(unaccounted)}")

    # sklearn's partial_dependence (ICE/PDP) refuses integer columns, so all numeric
    # inputs are floats. Written as e.g. "14.0", they are read back from CSV as float64.
    df[NUMERIC_FEATURES] = df[NUMERIC_FEATURES].astype("float64")
    return df[FEATURES + [TARGET]]


def split(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Stratified split by hotel x target, so both hotels keep their cancel rate in both parts."""
    strata = data["hotel"] + "_" + data[TARGET].astype(str)
    train, test = train_test_split(
        data, test_size=TEST_SIZE, stratify=strata, random_state=RANDOM_STATE
    )
    return train.reset_index(drop=True), test.reset_index(drop=True)


def build_pipeline() -> Pipeline:
    preprocess = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
            ("num", "passthrough", NUMERIC_FEATURES),
        ],
        verbose_feature_names_out=False,
    )
    return Pipeline(
        [
            ("preprocess", preprocess),
            ("model", RandomForestClassifier(**RF_PARAMS)),
        ]
    )


def evaluate(y_true: pd.Series, proba: pd.Series) -> dict:
    pred = (proba >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred).ravel()
    return {
        "roc_auc": round(roc_auc_score(y_true, proba), 4),
        "accuracy": round(accuracy_score(y_true, pred), 4),
        "precision": round(precision_score(y_true, pred), 4),
        "recall": round(recall_score(y_true, pred), 4),
        "f1": round(f1_score(y_true, pred), 4),
        "log_loss": round(log_loss(y_true, proba), 4),
        "brier": round(brier_score_loss(y_true, proba), 4),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }


def main() -> None:
    clean = pd.read_csv(CLEAN_PATH)
    data = build_features(clean)
    train, test = split(data)

    X_train, y_train = train[FEATURES], train[TARGET]
    X_test, y_test = test[FEATURES], test[TARGET]

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)
    forest = pipeline.named_steps["model"]

    proba = pd.Series(pipeline.predict_proba(X_test)[:, 1], index=X_test.index)
    by_hotel = {}
    for hotel in sorted(X_test["hotel"].unique()):
        mask = X_test["hotel"] == hotel
        by_hotel[hotel] = evaluate(y_test[mask], proba[mask])
    metrics = {
        "test": evaluate(y_test, proba),
        "test_by_hotel": by_hotel,
        "train_oob_accuracy": round(forest.oob_score_, 4),
        "train_oob_roc_auc": round(roc_auc_score(y_train, forest.oob_decision_function_[:, 1]), 4),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH, compress=3)
    train.to_csv(TRAIN_PATH, index=False)
    test.to_csv(TEST_PATH, index=False)

    metadata = {
        "description": "Shared Random Forest predicting hotel booking cancellation (is_canceled).",
        "generated_by": "models/train_cancellation_rf.py",
        "source_data": str(CLEAN_PATH.relative_to(ROOT)),
        "target": TARGET,
        "positive_class": "1 = booking canceled",
        "categorical_features": CATEGORICAL_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "encoded_feature_names": list(pipeline.named_steps["preprocess"].get_feature_names_out()),
        "excluded_columns": EXCLUDED_COLUMNS,
        "split": {
            "method": "stratified by hotel x is_canceled",
            "test_size": TEST_SIZE,
            "random_state": RANDOM_STATE,
            "n_train": len(train),
            "n_test": len(test),
            "cancel_rate_train": round(y_train.mean(), 4),
            "cancel_rate_test": round(y_test.mean(), 4),
        },
        "model": {"class": "sklearn RandomForestClassifier", "params": RF_PARAMS},
        "metrics": metrics,
        "versions": {
            "python": platform.python_version(),
            "scikit-learn": sklearn.__version__,
            "pandas": pd.__version__,
            "joblib": joblib.__version__,
        },
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    print(f"Train: {len(train)} rows, test: {len(test)} rows, {len(FEATURES)} features")
    print(f"OOB ROC AUC (train): {metrics['train_oob_roc_auc']}")
    for name, value in metrics["test"].items():
        print(f"test {name}: {value}")
    for hotel, m in metrics["test_by_hotel"].items():
        print(f"test ROC AUC {hotel}: {m['roc_auc']}")
    for path in [MODEL_PATH, TRAIN_PATH, TEST_PATH, METADATA_PATH]:
        print(f"Written: {path.relative_to(ROOT)} ({path.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
