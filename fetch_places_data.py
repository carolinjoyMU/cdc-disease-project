"""Create a county-level, long-format CSV from the downloaded CDC PLACES data.

Run: python3 fetch_places_data.py
Input: swc5-untb.json
Output: places_raw_long.csv
"""

import csv
import json
from collections import Counter
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
INPUT_PATH = PROJECT_DIR / "swc5-untb.json"
OUTPUT_PATH = PROJECT_DIR / "places_raw_long.csv"
STATES = {"WI", "IL", "MI"}
MEASURES = {"DIABETES", "OBESITY", "BPHIGH", "ACCESS2", "CHECKUP", "CHOLSCREEN"}
YEAR = "2023"
VALUE_TYPE = "Crude prevalence"
COLUMNS = [
    "year", "stateabbr", "statedesc", "locationname", "locationid",
    "measureid", "data_value", "low_confidence_limit",
    "high_confidence_limit", "totalpopulation", "totalpop18plus",
]


def main():
    with INPUT_PATH.open(encoding="utf-8") as source:
        records = json.load(source)

    rows = [
        {column: record.get(column, "") for column in COLUMNS}
        for record in records
        if record.get("year") == YEAR
        and record.get("stateabbr") in STATES
        and record.get("measureid") in MEASURES
        and record.get("data_value_type") == VALUE_TYPE
    ]
    rows.sort(key=lambda row: (row["locationid"], row["measureid"]))

    if not rows:
        raise ValueError("No matching records found in the downloaded PLACES data")

    keys = [(row["locationid"], row["measureid"]) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate county and measure pairs found")

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    counties = {row["locationid"] for row in rows}
    counts = Counter(row["measureid"] for row in rows)
    print(f"Saved {len(rows)} rows for {len(counties)} counties to {OUTPUT_PATH.name}")
    print("Rows by measure:", dict(sorted(counts.items())))


if __name__ == "__main__":
    main()
