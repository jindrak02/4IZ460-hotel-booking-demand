"""Prepare the shared cleaned dataset from the raw Kaggle Hotel Booking Demand file.

Input:  data/raw/hotel_bookings.csv (original, unmodified)
Output: data/processed/hotel_bookings_clean.csv  - cleaned rows, original columns + a few derived numerics
        data/processed/codebook.md               - auto-generated column overview and cleaning log

Run from the repository root:

    uv run python scripts/prepare_data.py

The script is fully deterministic (no randomness, no external calls), so re-running it
always regenerates identical outputs. Every row-dropping rule is listed in CLEANING_RULES
below and its effect is logged into the codebook, so the report can cite exact counts.

Decisions (agreed in the team):
  * Exact duplicate rows are KEPT. The dataset has no booking id and group bookings
    naturally produce identical rows; dropping them would distort the Groups segment.
  * reservation_status / reservation_status_date are DROPPED (they restate the target).
  * assigned_room_type and booking_changes are KEPT (post-booking information; whether to
    use them in a given analysis is decided per analysis).
  * No categorisation / binning happens here - that is a separate step producing
    hotel_bookings_cat.csv later.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "raw" / "hotel_bookings.csv"
OUT_DIR = ROOT / "data" / "processed"
CLEAN_PATH = OUT_DIR / "hotel_bookings_clean.csv"
CODEBOOK_PATH = OUT_DIR / "codebook.md"

# Columns that are an alternative encoding of the target (is_canceled) -> leakage.
TARGET_LEAK_COLUMNS = ["reservation_status", "reservation_status_date"]

# Columns where the literal string "NULL" means a missing value.
NULL_STRING_COLUMNS = ["country", "agent", "company"]

MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

# Columns documented as categorical in the codebook (everything else is numeric).
CATEGORICAL_COLUMNS = [
    "hotel", "arrival_date_month", "meal", "country", "market_segment",
    "distribution_channel", "reserved_room_type", "assigned_room_type",
    "deposit_type", "customer_type",
]

# Column descriptions for the codebook (source: Antonio, de Almeida & Nunes, 2019).
COLUMN_DESCRIPTIONS = {
    "hotel": "Hotel type: City Hotel or Resort Hotel (main segmentation of the project).",
    "is_canceled": "TARGET. 1 = booking was canceled (incl. no-show), 0 = guest checked out.",
    "lead_time": "Days between booking creation and arrival date.",
    "arrival_date_year": "Year of arrival (2015 covers only Jul-Dec, 2017 only Jan-Aug).",
    "arrival_date_month": "Month of arrival (English name).",
    "arrival_date_week_number": "ISO week number of arrival.",
    "arrival_date_day_of_month": "Day of month of arrival.",
    "arrival_date": "DERIVED. Arrival date as ISO date (from year/month/day).",
    "stays_in_weekend_nights": "Nights on Saturday/Sunday.",
    "stays_in_week_nights": "Nights Monday-Friday.",
    "total_nights": "DERIVED. stays_in_weekend_nights + stays_in_week_nights.",
    "adults": "Number of adults.",
    "children": "Number of children (raw 'NA' recoded to 0).",
    "babies": "Number of babies.",
    "total_guests": "DERIVED. adults + children + babies.",
    "meal": "Meal package: BB, HB, FB, SC (raw 'Undefined' merged into SC).",
    "country": "Country of origin, ISO 3166-3 code; empty = unknown.",
    "market_segment": "Market segment (Online TA, Offline TA/TO, Groups, Direct, Corporate, ...).",
    "distribution_channel": "Distribution channel (TA/TO, Direct, Corporate, GDS).",
    "is_repeated_guest": "1 = repeated guest.",
    "previous_cancellations": "Number of previous bookings canceled by the customer.",
    "previous_bookings_not_canceled": "Number of previous bookings not canceled by the customer.",
    "reserved_room_type": "Room type code reserved.",
    "assigned_room_type": "Room type code assigned (post-booking information, may differ from reserved).",
    "booking_changes": "Number of changes made to the booking (post-booking information).",
    "deposit_type": "No Deposit / Non Refund / Refundable.",
    "agent": "ID of the travel agency; empty = booked without an agent.",
    "company": "ID of the company; empty = not a company booking.",
    "days_in_waiting_list": "Days the booking waited before confirmation.",
    "customer_type": "Transient / Transient-Party / Contract / Group.",
    "adr": "Average daily rate (sum of lodging transactions / staying nights).",
    "required_car_parking_spaces": "Number of parking spaces required.",
    "total_of_special_requests": "Number of special requests.",
}


def load_raw(path: Path) -> pd.DataFrame:
    """Read the raw CSV without pandas' default NA guessing.

    keep_default_na=False is essential: otherwise the literal strings 'NA' (in children)
    and 'NULL' would be silently turned into NaN and we could not report them.
    """
    return pd.read_csv(path, keep_default_na=False, na_values=[""], low_memory=False)


def fix_types(df: pd.DataFrame, log: list[str]) -> pd.DataFrame:
    df = df.copy()

    # children: 4 rows contain the string 'NA' -> treat as 0 children.
    n_na = int((df["children"] == "NA").sum())
    df["children"] = pd.to_numeric(df["children"], errors="coerce").fillna(0).astype("int64")
    log.append(f"children: {n_na} rows with text 'NA' recoded to 0; column cast to integer.")

    # 'NULL' strings -> real missing values.
    for col in NULL_STRING_COLUMNS:
        n_null = int((df[col] == "NULL").sum())
        df[col] = df[col].replace("NULL", pd.NA)
        log.append(f"{col}: {n_null} rows with text 'NULL' converted to missing (empty in CSV).")

    # agent / company are integer ids stored as text; keep them as nullable integers.
    for col in ["agent", "company"]:
        df[col] = pd.to_numeric(df[col], errors="raise").astype("Int64")

    # meal: 'Undefined' is documented as equivalent to SC (no meal package).
    n_undef = int((df["meal"] == "Undefined").sum())
    df["meal"] = df["meal"].replace("Undefined", "SC")
    log.append(f"meal: {n_undef} rows with 'Undefined' merged into 'SC'.")

    return df


def add_derived(df: pd.DataFrame, log: list[str]) -> pd.DataFrame:
    df = df.copy()
    df["total_nights"] = df["stays_in_weekend_nights"] + df["stays_in_week_nights"]
    df["total_guests"] = df["adults"] + df["children"] + df["babies"]
    df["arrival_date"] = pd.to_datetime(
        df["arrival_date_year"].astype(str)
        + "-" + df["arrival_date_month"]
        + "-" + df["arrival_date_day_of_month"].astype(str),
        format="%Y-%B-%d",
    ).dt.date
    log.append("Derived numeric helper columns added: total_nights, total_guests, arrival_date.")
    return df


# Each rule: (name, reason, predicate returning a boolean mask of rows to DROP).
CLEANING_RULES = [
    (
        "no guests",
        "adults + children + babies == 0 (booking without a single guest is invalid)",
        lambda d: d["total_guests"] == 0,
    ),
    (
        "zero nights",
        "stays_in_weekend_nights + stays_in_week_nights == 0 (no stay)",
        lambda d: d["total_nights"] == 0,
    ),
    (
        "negative adr",
        "adr < 0 (invalid price)",
        lambda d: d["adr"] < 0,
    ),
    (
        "extreme adr",
        "adr > 1000 (single outlier of 5400)",
        lambda d: d["adr"] > 1000,
    ),
    (
        "undefined market segment",
        "market_segment == 'Undefined'",
        lambda d: d["market_segment"] == "Undefined",
    ),
    (
        "undefined distribution channel",
        "distribution_channel == 'Undefined'",
        lambda d: d["distribution_channel"] == "Undefined",
    ),
]


def drop_invalid_rows(df: pd.DataFrame, log: list[str]) -> pd.DataFrame:
    """Apply CLEANING_RULES sequentially and log how many rows each one removed."""
    for name, reason, predicate in CLEANING_RULES:
        mask = predicate(df)
        n = int(mask.sum())
        df = df.loc[~mask]
        log.append(f"Dropped {n} rows - {name}: {reason}.")
    return df


def drop_leak_columns(df: pd.DataFrame, log: list[str]) -> pd.DataFrame:
    df = df.drop(columns=TARGET_LEAK_COLUMNS)
    log.append(
        "Dropped columns " + ", ".join(TARGET_LEAK_COLUMNS)
        + " (alternative encoding of the target is_canceled)."
    )
    return df


def build_codebook(raw: pd.DataFrame, clean: pd.DataFrame, log: list[str]) -> str:
    lines: list[str] = []
    lines.append("# Codebook - hotel_bookings_clean.csv")
    lines.append("")
    lines.append("Generated automatically by `scripts/prepare_data.py`. Do not edit by hand.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Raw rows: {len(raw)}")
    lines.append(f"- Clean rows: {len(clean)} ({len(raw) - len(clean)} removed)")
    lines.append(f"- Columns: {clean.shape[1]}")
    n_dup = int(clean.duplicated().sum())
    lines.append(f"- Exact duplicate rows kept on purpose: {n_dup}")
    lines.append("")
    lines.append("### Cancellation rate by hotel")
    lines.append("")
    lines.append("| hotel | bookings | canceled | cancel rate |")
    lines.append("|---|---|---|---|")
    for hotel, grp in clean.groupby("hotel"):
        lines.append(f"| {hotel} | {len(grp)} | {int(grp['is_canceled'].sum())} | {grp['is_canceled'].mean():.1%} |")
    lines.append(f"| **Total** | {len(clean)} | {int(clean['is_canceled'].sum())} | {clean['is_canceled'].mean():.1%} |")
    lines.append("")
    lines.append("## Cleaning log")
    lines.append("")
    for entry in log:
        lines.append(f"- {entry}")
    lines.append("")
    lines.append("## Columns")
    lines.append("")
    for col in clean.columns:
        s = clean[col]
        missing = int(s.isna().sum())
        lines.append(f"### `{col}`")
        lines.append("")
        lines.append(COLUMN_DESCRIPTIONS.get(col, ""))
        lines.append("")
        lines.append(f"- dtype: `{s.dtype}`, missing: {missing}")
        if col in CATEGORICAL_COLUMNS or col == "is_canceled":
            vc = s.value_counts(dropna=False)
            if col == "arrival_date_month":
                vc = vc.reindex(MONTH_ORDER)
            top = vc if len(vc) <= 15 else vc.head(15)
            lines.append(f"- distinct values: {s.nunique(dropna=True)}")
            lines.append("")
            lines.append("| value | count | share | cancel rate |")
            lines.append("|---|---|---|---|")
            for val, cnt in top.items():
                label = "(missing)" if pd.isna(val) else str(val)
                sub = clean.loc[s.isna()] if pd.isna(val) else clean.loc[s == val]
                rate = sub["is_canceled"].mean() if len(sub) else float("nan")
                lines.append(f"| {label} | {int(cnt)} | {cnt / len(clean):.1%} | {rate:.1%} |")
            if len(vc) > 15:
                lines.append(f"| ... ({len(vc) - 15} more values) | | | |")
        elif col == "arrival_date":
            lines.append(f"- range: {s.min()} to {s.max()}")
        else:
            desc = s.describe()
            lines.append(
                f"- min {desc['min']:g}, 25% {desc['25%']:g}, median {desc['50%']:g}, "
                f"75% {desc['75%']:g}, max {desc['max']:g}, mean {desc['mean']:.2f}"
            )
            lines.append(f"- distinct values: {s.nunique(dropna=True)}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    log: list[str] = []
    raw = load_raw(RAW_PATH)
    log.append(f"Loaded raw file with {len(raw)} rows and {raw.shape[1]} columns.")

    df = fix_types(raw, log)
    df = add_derived(df, log)
    df = drop_invalid_rows(df, log)
    df = drop_leak_columns(df, log)
    df = df.reset_index(drop=True)
    log.append(f"Final clean dataset: {len(df)} rows, {df.shape[1]} columns.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False)
    CODEBOOK_PATH.write_text(build_codebook(raw, df, log), encoding="utf-8")

    for entry in log:
        print(entry)
    print(f"\nWritten: {CLEAN_PATH.relative_to(ROOT)}")
    print(f"Written: {CODEBOOK_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
