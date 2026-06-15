"""
Extract phase: read all CSV files from data/raw/ and anonymize PII before
passing data downstream to the LLM transform phase.
"""
import json
import re
from pathlib import Path

import pandas as pd
from config import RAW_DATA_DIR

# Shared attachment download cache (same location as fetcher.py).
_ATTACH_CACHE = Path(__file__).resolve().parents[2] / ".vitepress" / "cache" / "attachments"

# Map questionnaire export column headers to internal field names.
# Extend this dict to handle different export formats.
COLUMN_ALIASES: dict[str, str] = {
    "分类":     "category",
    "回答内容": "response",
    "问题":     "question",
    "content":  "response",   # Netlify Forms export (ExperienceForm.vue)
}

# Map Chinese category labels (used by Netlify Forms / questionnaire exports)
# to internal English category keys expected by transform.py.
CATEGORY_LABEL_MAP: dict[str, str] = {
    "行前准备":   "pre-departure",
    "学业与科研": "academics",
    "生活与心态": "life-and-mindset",
}

# Keyword-based category classifier for rows without a category label
# (e.g. bulk-mode submissions from Netlify Forms).
_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "pre-departure":    ["行李", "机票", "火车票", "住宿", "宿舍", "材料", "打包", "体检", "航班"],
    "academics":        ["课程", "选课", "学分", "考试", "考核", "导师", "实验室", "论文", "绩点", "科研", "实习", "考研", "保研", "竞赛"],
    "life-and-mindset": ["生活", "饮食", "交通", "社交", "心态", "心理", "文化", "孤独", "压力", "焦虑", "思乡", "适应"],
}

# ── PII anonymization ─────────────────────────────────────────────────────────
#姓名难以通用识别，依赖 LLM prompt 层兜底（prompt 要求模型不还原任何姓名）。
_PII_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r'\b\d{8,12}\b'),         '[学号]'),  # 8–12 位纯数字
    (re.compile(r'1[3-9]\d{9}'),          '[手机]'),  # 大陆手机号
    (re.compile(r'[\w.+-]+@[\w-]+\.\w+'), '[邮箱]'),  # 邮箱地址
]

def anonymize(text: str) -> str:
    for pattern, placeholder in _PII_PATTERNS:
        text = pattern.sub(placeholder, text)
    return text

def classify_category(text: str) -> str | None:
    """Guess the internal category key from text content using keyword matching."""
    if not text:
        return None
    best_cat, best_score = None, 0
    for cat, keywords in _CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score, best_cat = score, cat
    return best_cat if best_score > 0 else None

# ── Attachment helpers ────────────────────────────────────────────────────────

def _download_and_parse_csv_attachment(att_json: str) -> str:
    """Parse a Netlify CSV attachment field (JSON string), download the file,
    and return extracted text.  Returns empty string on any failure."""
    try:
        att = json.loads(att_json)
        url = att.get("url", "")
        filename = att.get("filename", "attachment")
    except (json.JSONDecodeError, AttributeError, TypeError):
        return ""

    if not url:
        return ""

    import requests
    from parser import parse_file

    _ATTACH_CACHE.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^\w.\-]", "_", filename)
    dest = _ATTACH_CACHE / safe_name

    if not dest.exists():
        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
        except Exception as exc:
            print(f"\033[33m[EXTRACT-WARN]\033[0m Failed to download {filename}: {exc}")
            return ""

    return parse_file(dest)


# ── Main extract function ─────────────────────────────────────────────────────

def read_all_csvs() -> list[dict]:
    """Return a flat list of anonymized response dicts from every CSV in RAW_DATA_DIR."""
    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {RAW_DATA_DIR}. "
            "Place questionnaire exports there and rerun."
        )

    rows: list[dict] = []
    for csv_path in csv_files:
        df = pd.read_csv(csv_path, encoding="utf-8-sig")  # handles Excel BOM
        df = df.rename(columns=COLUMN_ALIASES)

        if "response" not in df.columns:
            raise ValueError(
                f"{csv_path.name} has no 'response' / '回答内容' column. "
                "Check COLUMN_ALIASES in extract.py."
            )

        # Merge bulk-mode raw_content into response when structured content is empty
        if "raw_content" in df.columns:
            df["response"] = df["response"].fillna("").astype(str)
            raw_filled = df["raw_content"].fillna("").astype(str)
            resp_empty = df["response"].str.strip().eq("")
            df.loc[resp_empty, "response"] = raw_filled[resp_empty]
            merged_count = resp_empty.sum()
            if merged_count:
                print(f"[EXTRACT] Merged raw_content → response for {merged_count} row(s).")

        # Handle Netlify CSV attachment column (JSON-encoded file info with URL).
        # Download and parse the file whenever response is still empty.
        if "attachment" in df.columns:
            df["response"] = df["response"].fillna("").astype(str)
            needs_parse = df["response"].str.strip().eq("") & df["attachment"].fillna("").str.strip().ne("")
            if needs_parse.any():
                print(f"[EXTRACT] Downloading and parsing {needs_parse.sum()} attachment(s) from {csv_path.name}…")
                parsed = df.loc[needs_parse, "attachment"].apply(
                    lambda s: _download_and_parse_csv_attachment(str(s))
                )
                df.loc[needs_parse, "response"] = parsed

        df["source_file"] = csv_path.name
        # Map Chinese category labels to internal English keys
        if "category" in df.columns:
            cat_str = df["category"].astype(str)
            mapped = cat_str.map(CATEGORY_LABEL_MAP)
            df["category"] = mapped.where(mapped.notna(), cat_str)
        # For rows where category is still unknown, try keyword classification
        valid_cats = set(CATEGORY_LABEL_MAP.values())
        unknown_mask = ~df["category"].fillna("").isin(valid_cats)
        if unknown_mask.any():
            rescued = df.loc[unknown_mask, "response"].apply(classify_category)
            df["category"] = df["category"].astype(object)
            df.loc[unknown_mask, "category"] = rescued
            n_rescued = rescued.notna().sum()
            if n_rescued:
                print(f"[EXTRACT] Keyword-classified category for {n_rescued} row(s).")
        # Anonymize in place before any downstream processing
        df["response"] = df["response"].fillna("").astype(str).apply(anonymize)
        # Drop rows whose response is a parser placeholder (parse failures that
        # returned e.g. [DOCX_UNSUPPORTED] or [FILE_CORRUPTED]).
        _PLACEHOLDER_RE = re.compile(r"^\[[A-Z]+_(?:UNSUPPORTED|CORRUPTED)")
        def _is_placeholder(s: str) -> bool:
            return bool(_PLACEHOLDER_RE.match(str(s).strip()))
        placeholder_mask = df["response"].apply(_is_placeholder)
        if placeholder_mask.any():
            print(f"[EXTRACT] Dropped {placeholder_mask.sum()} placeholder row(s) from {csv_path.name}.")
            df = df[~placeholder_mask]

        # Drop rows with no usable content (bot submissions, empty uploads, etc.)
        before = len(df)
        df = df[df["response"].str.strip().ne("")]
        dropped = before - len(df)
        if dropped:
            print(f"[EXTRACT] Dropped {dropped} empty row(s) from {csv_path.name}.")
        rows.extend(df.to_dict(orient="records"))

    print(f"[EXTRACT] Loaded {len(rows)} rows from {len(csv_files)} file(s), PII anonymized.")
    return rows
