"""
Transform phase:
  1. Group rows by category.
  2. For each category, call LLM to extract structured insights (with retry).
"""
from pathlib import Path

from openai import OpenAI, APIError, APITimeoutError, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config import (
    API_KEYS, CATEGORIES, LLM_ENDPOINTS, LLM_PROVIDER,
)

# ── LLM client factory ────────────────────────────────────────────────────────

def _get_client() -> tuple[OpenAI, str]:
    base_url, model = LLM_ENDPOINTS[LLM_PROVIDER]
    api_key = API_KEYS[LLM_PROVIDER]
    if not api_key:
        raise EnvironmentError(
            f"API key for provider '{LLM_PROVIDER}' is not set. "
            "Add it to .env and rerun."
        )
    return OpenAI(api_key=api_key, base_url=base_url), model

def _load_prompt(name: str) -> str:
    return (Path(__file__).parent / "prompts" / name).read_text(encoding="utf-8")

# ── Retry-wrapped LLM call ────────────────────────────────────────────────────

@retry(
    retry=retry_if_exception_type((APIError, APITimeoutError, RateLimitError)),
    wait=wait_exponential(multiplier=1, min=2, max=60),  # 2s → 4s → 8s … ≤ 60s
    stop=stop_after_attempt(4),
    reraise=True,  # raise on final failure so run.py can skip this category
)
def _call_llm(client: OpenAI, model: str, messages: list[dict], **kwargs) -> str:
    response = client.chat.completions.create(
        model=model, messages=messages, **kwargs
    )
    return response.choices[0].message.content

# ── Per-category insight extraction ──────────────────────────────────────────

def extract_insights_for_category(category_key: str, responses: list[str]) -> str:
    client, model = _get_client()
    template = _load_prompt("insight_extraction.txt")
    combined = "\n---\n".join(responses[:80])  # cap to stay within context limit
    user_prompt = template.format(category=category_key, responses=combined)

    return _call_llm(
        client, model,
        messages=[
            {"role": "system", "content": "你是一位专业的留学信息整理助手，擅长从学生问卷中提炼有价值的建议。"},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.3,
    )

# ── Orchestrator ──────────────────────────────────────────────────────────────

def transform(rows: list[dict]) -> dict[str, str]:
    """Returns category_summaries: {category_key: markdown_string}"""
    by_category: dict[str, list[str]] = {k: [] for k in CATEGORIES}
    uncategorized: list[str] = []

    for row in rows:
        cat  = str(row.get("category", "")).strip()
        text = str(row.get("response", "")).strip()
        if not text:
            continue
        if cat in by_category:
            by_category[cat].append(text)
        else:
            uncategorized.append(text)

    if uncategorized:
        print(f"[INFO] {len(uncategorized)} rows had unrecognized category; skipped.")

    category_summaries: dict[str, str] = {}
    for cat_key, responses in by_category.items():
        if not responses:
            print(f"[INFO] No responses for '{cat_key}', skipping LLM call.")
            continue
        print(f"[TRANSFORM] Extracting insights for '{cat_key}' ({len(responses)} responses)…")
        try:
            category_summaries[cat_key] = extract_insights_for_category(cat_key, responses)
        except Exception as exc:
            print(f"[ERROR] '{cat_key}' failed after retries: {exc}. Skipping.")

    return category_summaries
