"""
Extract phase: read all CSV files from data/raw/ and anonymize PII before
passing data downstream to the LLM transform phase.
"""
import re
import pandas as pd
from config import RAW_DATA_DIR

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

        df["source_file"] = csv_path.name
        # Map Chinese category labels to internal English keys
        if "category" in df.columns:
            df["category"] = df["category"].map(CATEGORY_LABEL_MAP).fillna(df["category"])
        # Anonymize in place before any downstream processing
        df["response"] = df["response"].fillna("").astype(str).apply(anonymize)
        rows.extend(df.to_dict(orient="records"))

    print(f"[EXTRACT] Loaded {len(rows)} rows from {len(csv_files)} file(s), PII anonymized.")
    return rows
