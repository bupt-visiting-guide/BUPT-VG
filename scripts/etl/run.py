#!/usr/bin/env python3
"""
BUPT Visiting Guide — ETL Pipeline
Usage:  python scripts/etl/run.py

Reads CSVs from data/raw/, calls LLM API (DeepSeek by default),
writes Markdown summaries + keywords.json.

Set DEEPSEEK_API_KEY (or KIMI_API_KEY) in .env before running.
"""
import sys
from pathlib import Path

# Allow sibling imports without installing the package.
sys.path.insert(0, str(Path(__file__).parent))

import jsonschema
from extract import read_all_csvs
from load import write_category_md, write_keywords_json
from transform import transform


def main() -> None:
    print("=== BUPT Visiting Guide ETL Pipeline ===\n")

    print("[1/3] Extracting data from CSV files…")
    rows = read_all_csvs()
    print(f"      {len(rows)} total responses loaded.\n")

    print("[2/3] Transforming: calling LLM and counting keywords…")
    category_summaries, keyword_counts = transform(rows)
    print(
        f"      {len(category_summaries)} categories processed, "
        f"{len(keyword_counts)} keywords counted.\n"
    )

    print("[3/3] Loading: writing Markdown files and keywords.json…")
    write_category_md(category_summaries)
    try:
        write_keywords_json(keyword_counts)
    except jsonschema.ValidationError as exc:
        print(f"[ERROR] keywords.json failed schema validation — existing file kept.\n{exc.message}")
        sys.exit(1)

    print("\nDone. Review generated files, then: git add docs/ && git push")


if __name__ == "__main__":
    main()
