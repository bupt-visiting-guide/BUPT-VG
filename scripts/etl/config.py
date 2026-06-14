"""
Central configuration — all paths and API settings flow through here.
Non-technical maintainers: only this file and .env need to change.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
DOCS_DIR     = PROJECT_ROOT / "docs"
OUTPUT_JSON  = DOCS_DIR / "public" / "data" / "keywords.json"

# Category key → output directory. Keys must match sidebar sections in config.mts.
CATEGORIES: dict[str, Path] = {
    "pre-departure":    DOCS_DIR / "pre-departure",
    "academics":        DOCS_DIR / "academics",
    "life-and-mindset": DOCS_DIR / "life-and-mindset",
}

# ── LLM provider ─────────────────────────────────────────────────────────────
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek")  # deepseek | kimi | openai

LLM_ENDPOINTS: dict[str, tuple[str, str]] = {
    "deepseek": ("https://api.deepseek.com",        "deepseek-chat"),
    "kimi":     ("https://api.moonshot.cn/v1",      "moonshot-v1-8k"),
    "openai":   ("https://api.openai.com/v1",       "gpt-4o-mini"),
}

API_KEYS: dict[str, str] = {
    "deepseek": os.getenv("DEEPSEEK_API_KEY", ""),
    "kimi":     os.getenv("KIMI_API_KEY", ""),
    "openai":   os.getenv("OPENAI_API_KEY", ""),
}

# ── Seed keywords ─────────────────────────────────────────────────────────────
SEED_KEYWORDS: list[str] = [
    "微电子", "绩点", "实验室", "导师", "签证",
    "住宿", "文化冲击", "选课", "论文", "奖学金",
    "交流项目", "语言关", "实习", "宿舍", "同学",
]
