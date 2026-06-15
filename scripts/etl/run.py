#!/usr/bin/env python3
"""
BUPT Visiting Guide — ETL Pipeline
Usage:  python scripts/etl/run.py

Reads CSVs from data/raw/, calls LLM API to tag each response,
appends enriched rows to docs/public/data/experiences.json.

Set DEEPSEEK_API_KEY (or KIMI_API_KEY / OPENAI_API_KEY) in .env before running.
"""
import sys
from pathlib import Path

# Allow sibling imports without installing the package.
sys.path.insert(0, str(Path(__file__).parent))

from extract import read_all_csvs
from transform import extract_row_metadata
from load import write_experiences_json


def main() -> None:
    print("=== BUPT Visiting Guide ETL Pipeline ===\n")

    print("[1/3] Extracting data from CSV files…")
    rows = read_all_csvs()
    print(f"      {len(rows)} total responses loaded.\n")

    print("[2/3] Transforming: calling LLM to tag each response…")
    enriched = extract_row_metadata(rows)
    print(f"      {len(enriched)} rows enriched.\n")

    print("[3/3] Loading: appending to experiences.json…")
    write_experiences_json(enriched)

    print("\nDone. Review experiences.json, then: git add docs/ && git push")


if __name__ == "__main__":
    main()
