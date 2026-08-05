"""Quote service layer - manages quote persistence and retrieval."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from backend.config import DATA_DIR


# Simple JSON-based storage for MVP (could be replaced with SQLAlchemy)
QUOTES_FILE = DATA_DIR / "quotes.json"


def _ensure_data_dir():
    """Ensure data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not QUOTES_FILE.exists():
        QUOTES_FILE.write_text("[]", encoding="utf-8")


def _load_quotes() -> list[dict]:
    """Load all quotes from storage."""
    _ensure_data_dir()
    content = QUOTES_FILE.read_text(encoding="utf-8")
    return json.loads(content) if content.strip() else []


def _save_quotes(quotes: list[dict]):
    """Save quotes to storage."""
    _ensure_data_dir()
    QUOTES_FILE.write_text(json.dumps(quotes, indent=2, default=str), encoding="utf-8")


def create_quote_record(client_id: str, raw_text: str) -> dict:
    """Create a new quote record."""
    quote = {
        "id": str(uuid.uuid4()),
        "client_id": client_id,
        "raw_text": raw_text,
        "status": "processing",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "extracted_data": None,
        "validation_result": None,
        "quotation": None,
        "approval": None,
        "draft": None,
        "history": [],
    }
    quotes = _load_quotes()
    quotes.append(quote)
    _save_quotes(quotes)
    return quote


def update_quote(quote_id: str, updates: dict) -> Optional[dict]:
    """Update a quote record."""
    quotes = _load_quotes()
    for i, q in enumerate(quotes):
        if q["id"] == quote_id:
            quotes[i].update(updates)
            quotes[i]["updated_at"] = datetime.now(timezone.utc).isoformat()
            _save_quotes(quotes)
            return quotes[i]
    return None


def add_history_event(quote_id: str, event: str, details: Optional[dict] = None):
    """Add an event to the quote's audit trail."""
    quotes = _load_quotes()
    for i, q in enumerate(quotes):
        if q["id"] == quote_id:
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": event,
                "details": details,
            }
            quotes[i].setdefault("history", []).append(entry)
            quotes[i]["updated_at"] = datetime.now(timezone.utc).isoformat()
            _save_quotes(quotes)
            return
    return None


async def get_all_quotes() -> list[dict]:
    """Get all quotes (summary view)."""
    quotes = _load_quotes()
    # Return summary without heavy fields
    return [
        {
            "id": q["id"],
            "client_id": q["client_id"],
            "status": q["status"],
            "created_at": q["created_at"],
            "updated_at": q["updated_at"],
            "raw_text": q["raw_text"][:100] + "..." if len(q.get("raw_text", "")) > 100 else q.get("raw_text", ""),
        }
        for q in sorted(quotes, key=lambda x: x["created_at"], reverse=True)
    ]


async def get_quote_by_id(quote_id: str) -> Optional[dict]:
    """Get full quote details by ID."""
    quotes = _load_quotes()
    for q in quotes:
        if q["id"] == quote_id:
            return q
    return None


async def get_quote_history(quote_id: str) -> Optional[list]:
    """Get audit trail for a quote."""
    quotes = _load_quotes()
    for q in quotes:
        if q["id"] == quote_id:
            return q.get("history", [])
    return None
