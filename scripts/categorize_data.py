"""Build the categorised dataset for CleverMiner (4ft-Miner, SD4ft-Miner, CF-Miner).

Input:  data/processed/hotel_bookings_clean.csv   (produced by scripts/prepare_data.py)
Output: data/processed/hotel_bookings_categorized.csv
        data/processed/codebook_categorized.md

Run from the repository root (after prepare_data.py):

    uv run python scripts/categorize_data.py

Every column in the output is categorical. Conventions:
  * Ordinal attributes get a numeric prefix in the label (e.g. "2_8-30") so that plain
    lexicographic sorting - which CleverMiner uses for `seq` coefficients - matches the
    real order of the categories.
  * Binary derived attributes are named with a verb/prefix (has_, is_, needs_, was_)
    and coded 0 / 1.
  * Month and weekday are plain numbers (1 = January, 1 = Monday).
  * Post-booking columns (assigned_room_type, booking_changes) and raw ids (agent,
    company) are intentionally NOT included.

Load the output with dtype=str (see codebook) so that mixed labels like "0", "1", "2+"
are not partially parsed as integers.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CLEAN_PATH = ROOT / "data" / "processed" / "hotel_bookings_clean.csv"
OUT_PATH = ROOT / "data" / "processed" / "hotel_bookings_categorized.csv"
CODEBOOK_PATH = ROOT / "data" / "processed" / "codebook_categorized.md"

MONTH_NUMBER = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12,
}
SEASON_OF_MONTH = {
    12: "1_winter", 1: "1_winter", 2: "1_winter",
    3: "2_spring", 4: "2_spring", 5: "2_spring",
    6: "3_summer", 7: "3_summer", 8: "3_summer",
    9: "4_autumn", 10: "4_autumn", 11: "4_autumn",
}
COUNTRY_KEEP = ["PRT", "GBR", "FRA", "ESP", "DEU"]
ROOM_TYPE_KEEP = ["A", "D", "E", "F", "G"]


def bin_numeric(series: pd.Series, edges: list[float], labels: list[str]) -> pd.Series:
    """Right-closed bins: edges[i] < x <= edges[i+1] gets labels[i]."""
    return pd.cut(series, bins=edges, labels=labels, right=True, include_lowest=True).astype(str)


def categorize(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)

    # --- target and main segmentation -------------------------------------------------
    out["hotel"] = df["hotel"]
    out["is_canceled"] = df["is_canceled"]

    # --- timing ----------------------------------------------------------------------
    out["lead_time_cat"] = bin_numeric(
        df["lead_time"],
        edges=[-1, 7, 30, 90, 180, 365, float("inf")],
        labels=["1_0-7", "2_8-30", "3_31-90", "4_91-180", "5_181-365", "6_365+"],
    )
    out["arrival_year"] = df["arrival_date_year"]
    out["arrival_month"] = df["arrival_date_month"].map(MONTH_NUMBER)
    out["season"] = out["arrival_month"].map(SEASON_OF_MONTH)
    arrival = pd.to_datetime(df["arrival_date"])
    out["arrival_weekday"] = arrival.dt.day_of_week + 1  # 1 = Monday ... 7 = Sunday
    out["is_weekend_arrival"] = (out["arrival_weekday"] >= 6).astype(int)

    # --- stay ------------------------------------------------------------------------
    out["total_nights_cat"] = bin_numeric(
        df["total_nights"],
        edges=[0, 1, 3, 7, float("inf")],
        labels=["1_1", "2_2-3", "3_4-7", "4_8+"],
    )
    weekend = df["stays_in_weekend_nights"] > 0
    weekday = df["stays_in_week_nights"] > 0
    out["stay_type"] = pd.Series("mixed", index=df.index)
    out.loc[weekend & ~weekday, "stay_type"] = "weekend_only"
    out.loc[~weekend & weekday, "stay_type"] = "weekday_only"

    # --- guests ----------------------------------------------------------------------
    out["guests_cat"] = bin_numeric(
        df["total_guests"], edges=[0, 1, 2, float("inf")], labels=["1", "2", "3+"]
    )
    out["has_children"] = ((df["children"] + df["babies"]) > 0).astype(int)
    out["meal"] = df["meal"]
    out["country_group"] = df["country"].where(df["country"].isin(COUNTRY_KEEP), "Other")
    out.loc[df["country"].isna(), "country_group"] = "Unknown"

    # --- booking characteristics -----------------------------------------------------
    out["market_segment"] = df["market_segment"]
    out["distribution_channel"] = df["distribution_channel"]
    out["customer_type"] = df["customer_type"]
    out["deposit_type"] = df["deposit_type"]
    out["is_repeated_guest"] = df["is_repeated_guest"]
    out["previous_cancellations_cat"] = bin_numeric(
        df["previous_cancellations"], edges=[-1, 0, 1, float("inf")], labels=["0", "1", "2+"]
    )
    out["previous_bookings_not_canceled_cat"] = bin_numeric(
        df["previous_bookings_not_canceled"], edges=[-1, 0, float("inf")], labels=["0", "1+"]
    )
    out["reserved_room_type_cat"] = df["reserved_room_type"].where(
        df["reserved_room_type"].isin(ROOM_TYPE_KEEP), "Other"
    )
    out["has_agent"] = df["agent"].notna().astype(int)
    out["has_company"] = df["company"].notna().astype(int)
    out["was_on_waiting_list"] = (df["days_in_waiting_list"] > 0).astype(int)
    out["adr_cat"] = bin_numeric(
        df["adr"],
        edges=[-0.001, 0, 75, 125, 200, float("inf")],
        labels=["1_0", "2_1-75", "3_76-125", "4_126-200", "5_200+"],
    )
    out["needs_parking"] = (df["required_car_parking_spaces"] > 0).astype(int)
    out["special_requests_cat"] = bin_numeric(
        df["total_of_special_requests"], edges=[-1, 0, 1, float("inf")], labels=["0", "1", "2+"]
    )
    return out


COLUMN_DESCRIPTIONS = {
    "hotel": "Main segmentation: City Hotel / Resort Hotel (unchanged).",
    "is_canceled": "TARGET. 1 = canceled (incl. no-show), 0 = checked out (unchanged).",
    "lead_time_cat": "Days between booking and arrival: 0-7, 8-30, 31-90, 91-180, 181-365, 365+ (ordinal, prefixed).",
    "arrival_year": "Year of arrival. 2015 covers only Jul-Dec, 2017 only Jan-Aug.",
    "arrival_month": "Month of arrival as number, 1 = January ... 12 = December.",
    "season": "Meteorological season of arrival: winter (Dec-Feb), spring (Mar-May), summer (Jun-Aug), autumn (Sep-Nov).",
    "arrival_weekday": "Day of week of arrival as number, 1 = Monday ... 7 = Sunday.",
    "is_weekend_arrival": "1 = arrival on Saturday or Sunday.",
    "total_nights_cat": "Length of stay in nights: 1, 2-3, 4-7, 8+ (ordinal, prefixed).",
    "stay_type": "weekend_only / weekday_only / mixed, from weekend vs. week nights.",
    "guests_cat": "Total guests (adults + children + babies): 1, 2, 3+.",
    "has_children": "1 = at least one child or baby in the booking.",
    "meal": "Meal package BB / HB / FB / SC (unchanged).",
    "country_group": "Country of origin: PRT / GBR / FRA / ESP / DEU / Other / Unknown.",
    "market_segment": "Market segment (unchanged).",
    "distribution_channel": "Distribution channel (unchanged).",
    "customer_type": "Customer type (unchanged).",
    "deposit_type": "Deposit type (unchanged).",
    "is_repeated_guest": "1 = repeated guest (unchanged).",
    "previous_cancellations_cat": "Previous cancellations by the customer: 0 / 1 / 2+.",
    "previous_bookings_not_canceled_cat": "Previous non-canceled bookings by the customer: 0 / 1+.",
    "reserved_room_type_cat": "Reserved room type: A / D / E / F / G / Other.",
    "has_agent": "1 = booked through a travel agent (agent id present).",
    "has_company": "1 = company booking (company id present).",
    "was_on_waiting_list": "1 = booking spent at least one day on the waiting list.",
    "adr_cat": "Average daily rate: 0 / 1-75 / 76-125 / 126-200 / 200+ (ordinal, prefixed).",
    "needs_parking": "1 = at least one car parking space required.",
    "special_requests_cat": "Number of special requests: 0 / 1 / 2+.",
}


def build_codebook(df: pd.DataFrame) -> str:
    lines = [
        "# Codebook - hotel_bookings_categorized.csv",
        "",
        "Generated automatically by `scripts/categorize_data.py` from `hotel_bookings_clean.csv`. Do not edit by hand.",
        "",
        "All columns are categorical. Ordinal attributes carry a numeric prefix so that sorted order",
        "equals real order (needed for CleverMiner `seq` coefficients). Binary derived attributes are",
        "named with a verb/prefix and coded 0 / 1. Month and weekday are plain numbers.",
        "",
        "Load the file with all columns as text, otherwise pandas infers mixed int/str types in",
        "columns such as `previous_cancellations_cat` (values 0, 1, 2+):",
        "",
        "```python",
        "df = pd.read_csv('data/processed/hotel_bookings_categorized.csv', dtype=str)",
        "```",
        "",
        f"- Rows: {len(df)}",
        f"- Columns: {df.shape[1]}",
        "- Not included on purpose: assigned_room_type, booking_changes (post-booking information),",
        "  agent, company (raw ids), arrival_date_week_number, arrival_date_day_of_month.",
        "",
        "## Columns",
        "",
    ]
    for col in df.columns:
        s = df[col]
        vc = s.value_counts(dropna=False).sort_index()
        lines += [f"### `{col}`", "", COLUMN_DESCRIPTIONS.get(col, ""), "",
                  f"- distinct values: {s.nunique(dropna=True)}, missing: {int(s.isna().sum())}", "",
                  "| value | count | share | cancel rate |", "|---|---|---|---|"]
        for val, cnt in vc.items():
            rate = df.loc[s == val, "is_canceled"].mean()
            lines.append(f"| {val} | {int(cnt)} | {cnt / len(df):.1%} | {rate:.1%} |")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    df = pd.read_csv(CLEAN_PATH)
    out = categorize(df)
    assert out.isna().sum().sum() == 0, "categorised dataset must not contain missing values"
    out.to_csv(OUT_PATH, index=False)
    CODEBOOK_PATH.write_text(build_codebook(out), encoding="utf-8")
    print(f"Written: {OUT_PATH.relative_to(ROOT)} ({len(out)} rows, {out.shape[1]} columns)")
    print(f"Written: {CODEBOOK_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
