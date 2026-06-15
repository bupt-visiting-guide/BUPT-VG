"""
Load phase: write Markdown summaries to the docs tree.
"""
from datetime import date
from pathlib import Path

from config import CATEGORIES

_FRONTMATTER = """\
---
title: {title}
description: 由问卷数据自动生成，最后更新：{date}
---

"""

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
