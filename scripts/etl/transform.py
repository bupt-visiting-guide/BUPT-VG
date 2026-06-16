"""
Transform phase — semantic chunking via LLM.
Each survey response expands to 0-3 independent chunk records, one per dimension.
"""
import json
import logging
import re
from pathlib import Path

from openai import OpenAI, APIError, APITimeoutError, RateLimitError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from config import API_KEYS, LLM_ENDPOINTS, LLM_PROVIDER

logger = logging.getLogger(__name__)

_NAN_STRINGS = frozenset({"nan", "none", "null", ""})
_VALID_CATS = frozenset({"pre-departure", "academics", "life-and-mindset"})


def _clean_str(value) -> str | None:
    """Convert a value to stripped string, returning None for pandas NaN and blank values."""
    s = str(value).strip() if value is not None else ""
    return None if s.lower() in _NAN_STRINGS else s


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


@retry(
    retry=retry_if_exception_type((APIError, APITimeoutError, RateLimitError)),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    stop=stop_after_attempt(4),
    reraise=True,
)
def _call_llm(client: OpenAI, model: str, messages: list[dict]) -> str:
    response = client.chat.completions.create(model=model, messages=messages, temperature=0.2)
    return response.choices[0].message.content


def _parse_json_array(raw: str) -> list[dict]:
    """Strip markdown fences and parse JSON array; returns [] on failure."""
    text = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.MULTILINE)
    text = re.sub(r"\s*```$", "", text.strip(), flags=re.MULTILINE)
    try:
        result = json.loads(text)
        return result if isinstance(result, list) else []
    except json.JSONDecodeError:
        logger.warning("\033[33m[TRANSFORM-WARN]\033[0m JSON parse failed; skipping row.")
        return []


def _extract_chunks_for_row(client: OpenAI, model: str, row: dict, idx: int) -> list[dict]:
    """Call LLM for a single row; return 0–3 validated chunk dicts."""
    template = _load_prompt("row_extraction.txt")
    prompt = template.format(
        idx=idx,
        response=str(row.get("response", "")).strip(),
    )
    raw = _call_llm(
        client, model,
        messages=[
            {"role": "system", "content": "你是一位结构化数据提取专家，只输出要求的 JSON。"},
            {"role": "user",   "content": prompt},
        ],
    )
    chunks = _parse_json_array(raw)
    return [c for c in chunks if c.get("category") in _VALID_CATS]


def extract_row_metadata(rows: list[dict]) -> list[dict]:
    """Semantic chunking: each row expands to 0–3 records, one per dimension."""
    from config import row_id
    records: list[dict] = []
    total = len(rows)
    client, model = _get_client()

    for idx, row in enumerate(rows):
        text = str(row.get("response", "")).strip()
        print(f"[TRANSFORM] Row {idx + 1}/{total}…")
        try:
            chunks = _extract_chunks_for_row(client, model, row, idx)
        except Exception as exc:
            print(f"[TRANSFORM] Row {idx + 1} failed: {exc}; skipped.")
            chunks = []

        for chunk in chunks:
            category = chunk.get("category", "")
            records.append({
                "id":            row_id(text, category),
                "original_text": text,
                "category":      category,
                "summary":       (chunk.get("summary") or "")[:50],
                "exact_quote":   (chunk.get("exact_quote") or "")[:500],
                "tags":          chunk.get("tags") or [],
                "major":         chunk.get("major") if category == "academics" else None,
                "alias":         _clean_str(row.get("alias")),
                "source_file":   str(row.get("source_file", "")),
            })

    print(f"[TRANSFORM] {total} rows → {len(records)} chunk records.")
    return records
