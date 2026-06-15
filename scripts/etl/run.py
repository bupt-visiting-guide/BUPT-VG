#!/usr/bin/env python3
"""
BUPT Visiting Guide — ETL Pipeline
Usage:  python scripts/etl/run.py

Reads CSVs from data/raw/, calls LLM API (DeepSeek by default),
writes Markdown summaries to docs/<category>/generated-insights.md.

Set DEEPSEEK_API_KEY (or KIMI_API_KEY) in .env before running.
"""
import sys
from pathlib import Path

# Allow sibling imports without installing the package.
sys.path.insert(0, str(Path(__file__).parent))

from extract import read_all_csvs
from load import write_category_md
from transform import transform


def main() -> None:
    print("=== BUPT Visiting Guide ETL Pipeline ===\n")

    print("[1/3] Extracting data from CSV files…")
    rows = read_all_csvs()
    print(f"      {len(rows)} total responses loaded.\n")

    print("[2/3] Transforming: calling LLM to extract insights…")
    category_summaries = transform(rows)
    print(f"      {len(category_summaries)} categories processed.\n")

    print("[3/3] Loading: writing Markdown files…")
    write_category_md(category_summaries)

    print("\nDone. Review generated files, then: git add docs/ && git push")


if __name__ == "__main__":
    main()
