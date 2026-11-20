"""
4ft-Miner: booking lead time x company booking -> cancellation.

Analytical question:
    How do the booking lead time and the company character of a booking influence the
    probability that the stay is cancelled?

Hypothesis:
    Company bookings made far in advance are cancelled less often than other
    bookings with the same lead time.

Task structure for 4ft-Miner (CleverMiner, https://www.cleverminer.org/doc/):
    antecedent : has_company (subset, 1 category), optionally market_segment (subset,
                 1 category); 1-2 literals in conjunction
    succedent  : is_canceled = 0 (the stay was NOT cancelled)
    condition  : lead_time_cat (seq, 1-2 neighbouring bands)
    quantifiers: Base >= BASE_MIN and aad >= AAD_MIN
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from cleverminer import cleverminer

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "processed" / "hotel_bookings_categorized.csv"

# Attributes used by the task
ATTRIBUTES = ["is_canceled", "lead_time_cat", "has_company", "market_segment"]

# Quantifier thresholds
BASE_MIN = 300  # minimum number of not cancelled bookings of the group in the band
AAD_MIN = 0.4   # group keeps bookings at least 40 % more often than its lead-time band average


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, dtype=str)
    return df[ATTRIBUTES]


def run_task(df: pd.DataFrame) -> cleverminer:
    return cleverminer(
        df=df,
        proc="4ftMiner",
        quantifiers={"Base": BASE_MIN, "aad": AAD_MIN},
        ante={
            "attributes": [
                {"name": "has_company", "type": "subset", "minlen": 1, "maxlen": 1},
                {"name": "market_segment", "type": "subset", "minlen": 1, "maxlen": 1},
            ],
            "minlen": 1,
            "maxlen": 2,
            "type": "con",
        },
        succ={
            "attributes": [
                {"name": "is_canceled", "type": "one", "value": 0},
            ],
            "minlen": 1,
            "maxlen": 1,
            "type": "con",
        },
        cond={
            "attributes": [
                {"name": "lead_time_cat", "type": "seq", "minlen": 1, "maxlen": 2},
            ],
            "minlen": 1,
            "maxlen": 1,
            "type": "con",
        },
    )


def print_results(clm: cleverminer) -> None:
    clm.print_summary()
    clm.print_rulelist(sortby="aad")
    print()
    print("Rule details (fourfold table a, b, c, d is computed within the condition):")
    for rule_id in range(1, clm.get_rulecount() + 1):
        clm.print_rule(rule_id)


def main() -> None:
    df = load_data()
    print(f"Loaded {len(df)} rows, attributes: {', '.join(ATTRIBUTES)}")
    clm = run_task(df)
    print_results(clm)


if __name__ == "__main__":
    main()
