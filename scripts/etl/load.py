"""
Load phase — append-merge enriched rows to experiences.json.
"""
import json
from datetime import date
from pathlib import Path

from config import EXPERIENCES_JSON_PATH


def write_experiences_json(enriched_rows: list[dict]) -> None:
    """Append new rows to experiences.json, deduplicating by id."""
    existing: list[dict] = []
    existing_ids: set[str] = set()

    if EXPERIENCES_JSON_PATH.exists():
        try:
            data = json.loads(EXPERIENCES_JSON_PATH.read_text(encoding="utf-8"))
            existing = data.get("experiences", [])
            existing_ids = {e["id"] for e in existing}
        except Exception:
            print("[LOAD] Warning: could not parse existing experiences.json; starting fresh.")

    new_count = 0
    for row in enriched_rows:
        if row["id"] not in existing_ids:
            existing.append(row)
            existing_ids.add(row["id"])
            new_count += 1

    payload = {
        "experiences": existing,
        "meta": {
            "last_updated": date.today().isoformat(),
            "total":        len(existing),
        },
    }

    EXPERIENCES_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXPERIENCES_JSON_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[LOAD] +{new_count} new entries. Total: {payload['meta']['total']} → {EXPERIENCES_JSON_PATH}")
