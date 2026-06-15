#!/usr/bin/env python3
"""
BUPT Visiting Guide — ETL Pipeline
Usage:  python scripts/etl/run.py

Reads CSVs from data/raw/, calls LLM API to tag each response,
appends enriched rows to docs/public/data/experiences.json.

Set DEEPSEEK_API_KEY (or KIMI_API_KEY / OPENAI_API_KEY) in .env before running.
"""
import json
import sys
from pathlib import Path

# Allow sibling imports without installing the package.
sys.path.insert(0, str(Path(__file__).parent))

from config import EXPERIENCES_JSON_PATH, row_id
from extract import read_all_csvs
from transform import extract_row_metadata
from load import write_experiences_json


def main() -> None:
    print("=== BUPT Visiting Guide ETL Pipeline ===\n")

    print("[1/3] Extracting data from CSV files…")
    rows = read_all_csvs()
    print(f"      {len(rows)} total responses loaded.")

    # ── Pre-filter: skip rows whose id already exists in experiences.json ──
    existing_ids: set[str] = set()
    if EXPERIENCES_JSON_PATH.exists():
        try:
            data = json.loads(EXPERIENCES_JSON_PATH.read_text(encoding="utf-8"))
            existing_ids = {e["id"] for e in data.get("experiences", [])}
        except Exception:
            pass  # fresh start — no prior data

    new_rows = [r for r in rows
                if row_id(str(r.get("response", "")).strip()) not in existing_ids]
    skipped = len(rows) - len(new_rows)
    if skipped:
        print(f"      Skipped {skipped} already-processed row(s); {len(new_rows)} new.\n")
    else:
        print()

    if not new_rows:
        print("Nothing new to process. Exiting.")
        return

    print("[2/3] Transforming: calling LLM to tag each response…")
    enriched = extract_row_metadata(new_rows)
    print(f"      {len(enriched)} rows enriched.\n")

    print("[3/3] Loading: appending to experiences.json…")
    write_experiences_json(enriched)

    print("\nDone. Review experiences.json, then: git add docs/ && git push")


if __name__ == "__main__":
    main()
