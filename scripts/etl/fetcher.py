"""
Netlify Forms fetcher: pull submissions and download attachments.

Usage (standalone):
    python fetcher.py --form-id <id> --token <token>

Integration with run.py (future):
    rows_netlify = fetch_and_parse_submissions(FORM_ID, NETLIFY_TOKEN)
    clear_attachment_cache()
    rows = read_all_csvs() + rows_netlify
"""
import logging
import os
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

# Relative to project root — added to .gitignore to prevent temp files from
# being committed.
_CACHE_DIR = Path(__file__).resolve().parents[2] / ".vitepress" / "cache" / "attachments"

# ── Cache management ──────────────────────────────────────────────────────────

def clear_attachment_cache() -> None:
    """Delete all files in the attachment cache directory.  Silent if not found."""
    if not _CACHE_DIR.exists():
        return
    shutil.rmtree(_CACHE_DIR)
    logger.info("[FETCHER] Attachment cache cleared: %s", _CACHE_DIR)


def _ensure_cache_dir() -> Path:
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return _CACHE_DIR

# ── Netlify API helpers ───────────────────────────────────────────────────────

def fetch_submissions(form_id: str, token: str) -> list[dict]:
    """Fetch all submissions for a Netlify Forms form.

    Returns the raw list of submission dicts from the Netlify API.
    Raises on HTTP error (caller is responsible for catching).
    """
    import requests

    url = f"https://api.netlify.com/api/v1/forms/{form_id}/submissions"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def download_attachment(url: str, submission_id: str, filename: str) -> Path:
    """Download a single attachment to the cache directory.

    Returns the local Path to the downloaded file.
    The local filename is prefixed with submission_id to avoid collisions.
    """
    import requests

    safe_name = f"{submission_id}_{Path(filename).name}"
    dest = _ensure_cache_dir() / safe_name

    if dest.exists():
        logger.info("[FETCHER] Cache hit, skipping download: %s", safe_name)
        return dest

    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        dest.write_bytes(resp.content)
        logger.info("[FETCHER] Downloaded %s → %s", filename, dest.name)
    except Exception as exc:
        logger.warning(
            "\033[33m[FETCHER-WARN]\033[0m Failed to download %s: %s", filename, exc
        )
        raise

    return dest

# ── High-level integration helper ────────────────────────────────────────────

def fetch_and_parse_submissions(form_id: str, token: str) -> list[dict]:
    """Fetch Netlify submissions, parse attachments via parser.py, and return
    a list of dicts in the same format as read_all_csvs() (response, category).

    Call clear_attachment_cache() after this function returns to clean up
    the temporary downloaded files.
    """
    from parser import parse_bytes
    from extract import CATEGORY_LABEL_MAP, classify_category
    _VALID_CATS = set(CATEGORY_LABEL_MAP.values())

    submissions = fetch_submissions(form_id, token)
    rows: list[dict] = []

    for sub in submissions:
        data = sub.get("data", {})
        sub_id = sub.get("id", "unknown")

        text_parts: list[str] = []

        content_text = str(data.get("content") or "").strip()
        if content_text:
            text_parts.append(content_text)

        for field in sub.get("ordered_human_fields", []):
            if field.get("name") == "attachment" and field.get("value"):
                att_url = field["value"]
                att_name = field.get("title") or "attachment"
                try:
                    local_path = download_attachment(att_url, sub_id, att_name)
                    text_parts.append(parse_bytes(local_path.read_bytes(), att_name))
                except Exception:
                    text_parts.append("[FILE_CORRUPTED: 文件损坏或格式错误]")

        combined = "\n".join(text_parts).strip()
        if combined:
            raw_cat = str(data.get("category", "")).strip()
            cat = CATEGORY_LABEL_MAP.get(raw_cat, raw_cat)
            if cat not in _VALID_CATS:
                cat = classify_category(combined) or ""
            rows.append({
                "response":    combined,
                "category":    cat,
                "alias":       str(data.get("alias") or "").strip() or None,
                "source_file": f"netlify:{sub_id}",
            })

    logger.info("[FETCHER] Processed %d Netlify submission(s).", len(rows))
    return rows
