"""
Load phase: write Markdown files and keywords.json to the docs tree.
JSON Schema validation guards the write so a malformed LLM response
never corrupts the file that the frontend reads at runtime.
"""
import json
import jsonschema
from datetime import date
from pathlib import Path

from config import CATEGORIES, OUTPUT_JSON

_FRONTMATTER = """\
---
title: {title}
description: 由问卷数据自动生成，最后更新：{date}
---

"""

# ── JSON Schema: contract between ETL and KeywordBubble.vue ──────────────────

_KEYWORDS_SCHEMA: dict = {
    "type": "object",
    "required": ["generated", "keywords"],
    "properties": {
        "generated": {"type": "string"},
        "keywords": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "value"],
                "properties": {
                    "name":  {"type": "string", "minLength": 1},
                    "value": {"type": "integer", "minimum": 0},
                },
                "additionalProperties": False,
            },
        },
    },
    "additionalProperties": False,
}

# ── Writers ───────────────────────────────────────────────────────────────────

def write_category_md(category_summaries: dict[str, str]) -> None:
    """Write LLM summaries to generated-insights.md (never overwrites index.md)."""
    for cat_key, content in category_summaries.items():
        out_dir: Path = CATEGORIES[cat_key]
        out_dir.mkdir(parents=True, exist_ok=True)

        out_file = out_dir / "generated-insights.md"
        frontmatter = _FRONTMATTER.format(
            title=f"{cat_key} — 问卷洞察",
            date=date.today().isoformat(),
        )
        out_file.write_text(frontmatter + content, encoding="utf-8")
        print(f"[LOAD] Wrote {out_file.relative_to(Path.cwd())}")

def write_keywords_json(keyword_counts: dict[str, int]) -> None:
    """
    Write keyword frequencies to docs/public/data/keywords.json.
    Validates against schema before writing — on failure the existing
    file is preserved so the frontend never sees a broken response.
    """
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated": date.today().isoformat(),
        "keywords": [{"name": k, "value": v} for k, v in keyword_counts.items()],
    }

    # Raises jsonschema.ValidationError if structure is wrong; caller handles it.
    jsonschema.validate(instance=payload, schema=_KEYWORDS_SCHEMA)

    OUTPUT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[LOAD] Wrote {OUTPUT_JSON.relative_to(Path.cwd())} ({len(payload['keywords'])} keywords)")
