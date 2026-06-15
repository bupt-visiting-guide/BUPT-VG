"""
Transform phase — per-row metadata extraction.
LLM extracts tags + major only; original_text passes through unchanged.
"""
import hashlib
import json
import logging
import re
from pathlib import Path

from openai import OpenAI, APIError, APITimeoutError, RateLimitError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from config import API_KEYS, LLM_ENDPOINTS, LLM_PROVIDER

logger = logging.getLogger(__name__)

_BATCH_SIZE = 20
_NAN_STRINGS = frozenset({"nan", "none", "null", ""})


def _clean_str(value) -> str | None:
    """Convert a value to stripped string, returning None for pandas NaN and blank values."""
    s = str(value).strip() if value is not None else ""
    return None if s.lower() in _NAN_STRINGS else s


def _row_id(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:12]


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
        logger.warning("\033[33m[TRANSFORM-WARN]\033[0m JSON parse failed; skipping batch metadata.")
        return []


def _extract_batch_metadata(batch: list[dict], start_idx: int) -> dict[int, dict]:
    """Call LLM for one batch; return {global_idx: {tags, major}} mapping."""
    client, model = _get_client()
    template = _load_prompt("row_extraction.txt")
    lines = []
    for i, row in enumerate(batch):
        lines.append(f"[{start_idx + i}]\n{row['response']}")
    prompt = template.format(
        start=start_idx,
        end=start_idx + len(batch) - 1,
        responses="\n===\n".join(lines),
    )
    raw = _call_llm(
        client, model,
        messages=[
            {"role": "system", "content": "你是一位结构化数据提取专家，只输出要求的 JSON。"},
            {"role": "user",   "content": prompt},
        ],
    )
    result: dict[int, dict] = {}
    for item in _parse_json_array(raw):
        idx = item.get("idx")
        if isinstance(idx, int):
            result[idx] = {"tags": item.get("tags", []), "major": item.get("major")}
    return result


def extract_row_metadata(rows: list[dict]) -> list[dict]:
    """Enrich each row with id, tags, major. original_text is unchanged."""
    from extract import classify_category
    _VALID_CATS = {"pre-departure", "academics", "life-and-mindset"}
    enriched: list[dict] = []
    total = len(rows)

    for batch_start in range(0, total, _BATCH_SIZE):
        batch = rows[batch_start : batch_start + _BATCH_SIZE]
        print(f"[TRANSFORM] Batch {batch_start + 1}–{batch_start + len(batch)} / {total}…")
        try:
            meta_map = _extract_batch_metadata(batch, batch_start)
        except Exception as exc:
            print(f"[TRANSFORM] Batch failed: {exc}; empty metadata used.")
            meta_map = {}

        for j, row in enumerate(batch):
            meta = meta_map.get(batch_start + j, {})
            text = str(row.get("response", "")).strip()
            tags = meta.get("tags") or []
            category = _clean_str(row.get("category")) or ""
            if category not in _VALID_CATS:
                tags_text = " ".join([str(t) for t in tags])
                if tags_text:
                    category = classify_category(tags_text) or category
            enriched.append({
                "id":            _row_id(text),
                "original_text": text,
                "category":      category,
                "tags":          tags,
                "alias":         _clean_str(row.get("alias")),
                "major":         meta.get("major"),
                "source_file":   str(row.get("source_file", "")),
            })

    print(f"[TRANSFORM] Enriched {len(enriched)} rows.")
    return enriched
