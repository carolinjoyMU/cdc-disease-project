"""Load county_priority_scores.csv into a local SQLite database.

Run: python3 load_scores_sqlite.py
Output: county_health.db
"""

import csv
import sqlite3
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
CSV_PATH = PROJECT_DIR / "county_priority_scores.csv"
DB_PATH = PROJECT_DIR / "county_health.db"
MEASURES = ("DIABETES", "OBESITY", "BPHIGH", "ACCESS2", "CHECKUP", "CHOLSCREEN")


def main():
    with CSV_PATH.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))

    if not rows:
        raise ValueError("The scores CSV has no county rows")

    # One row per county and year. Keep FIPS locationid as text.
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS county_scores (
                year INTEGER NOT NULL,
                locationid TEXT NOT NULL,
                locationname TEXT NOT NULL,
                stateabbr TEXT NOT NULL,
                diabetes REAL NOT NULL,
                obesity REAL NOT NULL,
                bphigh REAL NOT NULL,
                access2 REAL NOT NULL,
                checkup REAL NOT NULL,
                cholscreen REAL NOT NULL,
                burden_index REAL NOT NULL,
                access_gap_index REAL NOT NULL,
                need_priority_score REAL NOT NULL,
                PRIMARY KEY (year, locationid)
            )
        """)
        years = sorted({int(row["year"]) for row in rows})
        # Re-running the loader replaces just the years in this CSV.
        connection.executemany("DELETE FROM county_scores WHERE year = ?", [(year,) for year in years])
        connection.executemany("""
            INSERT INTO county_scores VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (
                int(row["year"]), row["locationid"], row["locationname"], row["stateabbr"],
                *(float(row[measure]) for measure in MEASURES),
                float(row["burden_index"]), float(row["access_gap_index"]),
                float(row["need_priority_score"]),
            )
            for row in rows
        ])

    print(f"Loaded {len(rows)} county scores for {years} into {DB_PATH.name}")


if __name__ == "__main__":
    main()
