"""Score counties using the six measures in places_raw_long.csv.

Run: python3 compute_scores.py
Output: county_priority_scores.csv

Each measure is converted to a z-score across the complete counties:
    z = (county value - county average) / population standard deviation
The three burden z-scores are averaged; the three access z-scores are
averaged after reversing measures where a higher value means better access.
The two averages are added with equal weight. Scores are relative to the
counties in this input file, so they are not percentages or clinical risks.
"""

import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean, pstdev


PROJECT_DIR = Path(__file__).resolve().parent
INPUT_PATH = PROJECT_DIR / "places_raw_long.csv"
OUTPUT_PATH = PROJECT_DIR / "county_priority_scores.csv"
BURDEN = ("DIABETES", "OBESITY", "BPHIGH")
ACCESS = ("ACCESS2", "CHECKUP", "CHOLSCREEN")
MEASURES = BURDEN + ACCESS


def main():
    # Pivot the long CSV: one dictionary per county, with measure IDs as keys.
    # Keep locationid as text so its leading zero, if any, is preserved.
    counties = defaultdict(dict)
    years = set()
    with INPUT_PATH.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            years.add(row["year"])
            county_id = row["locationid"]
            measure = row["measureid"]
            if measure not in MEASURES:
                continue
            if measure in counties[county_id]:
                raise ValueError(f"Duplicate {measure} for county {county_id}")
            counties[county_id][measure] = float(row["data_value"]) if row["data_value"] else None
            counties[county_id]["locationname"] = row["locationname"]
            counties[county_id]["stateabbr"] = row["stateabbr"]

    if len(years) != 1:
        raise ValueError(f"Expected one year of data for scoring; found {sorted(years)}")
    year = years.pop()

    # A county needs all six values to receive a comparable composite score.
    # Missing counties are excluded before calculating averages and deviations.
    complete = {
        county_id: row for county_id, row in counties.items()
        if all(row.get(measure) is not None for measure in MEASURES)
    }
    print(f"Counties found: {len(counties)}; complete: {len(complete)}")
    if not complete:
        raise ValueError("No counties have all six measures")

    # Measures have different ranges. A z-score puts each one on the same
    # scale: 0 is the county average and +1 is one standard deviation above it.
    # Use the same complete counties for every measure's mean and deviation.
    zscores = {}
    for measure in MEASURES:
        values = [row[measure] for row in complete.values()]
        center, spread = mean(values), pstdev(values)
        if spread == 0:
            raise ValueError(f"Cannot standardize {measure}: all values are equal")
        zscores[measure] = {
            county_id: (row[measure] - center) / spread
            for county_id, row in complete.items()
        }

    results = []
    for county_id, row in complete.items():
        # Higher diabetes, obesity, and blood pressure prevalence increases
        # the burden index. Each measure contributes one third of this index.
        burden = mean(zscores[measure][county_id] for measure in BURDEN)

        # More uninsured adults (ACCESS2) increases the access gap.
        # More routine checkups or cholesterol screening implies better access,
        # so multiply those two z-scores by -1 before averaging.
        access_gap = mean((1 if measure == "ACCESS2" else -1) * zscores[measure][county_id]
                          for measure in ACCESS)
        # Equal weight for burden and access gap; higher means higher relative
        # need among the counties scored in this run.
        results.append({
            "year": year,
            "locationid": county_id,
            "locationname": row["locationname"],
            "stateabbr": row["stateabbr"],
            **{measure: row[measure] for measure in MEASURES},
            "burden_index": round(burden, 6),
            "access_gap_index": round(access_gap, 6),
            "need_priority_score": round(burden + access_gap, 6),
        })

    # Put the highest-priority counties first in the exported CSV.
    results.sort(key=lambda row: row["need_priority_score"], reverse=True)
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(results[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)

    print(f"Saved {len(results)} counties to {OUTPUT_PATH.name}")
    for rank, row in enumerate(results[:10], start=1):
        print(f"{rank:2}. {row['locationname']}, {row['stateabbr']}: {row['need_priority_score']:.3f}")


if __name__ == "__main__":
    main()
