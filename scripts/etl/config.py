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

EXPERIENCES_JSON_PATH = DOCS_DIR / "public" / "data" / "experiences.json"

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

