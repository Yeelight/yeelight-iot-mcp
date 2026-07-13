from typing import Any, Optional


def resolve_page(cursor: Optional[str], limit: Optional[int], default_page_size: int, max_page_size: int) -> tuple[int, int]:
    page_no = _parse_positive_int(cursor, 1)
    page_size = _parse_positive_int(limit, default_page_size)
    return page_no, min(page_size, max_page_size)


def append_next_cursor(data: dict[str, Any]) -> dict[str, Any]:
    payload = dict(data or {})
    total = _parse_positive_int(payload.get("total"), 0)
    page_no = _parse_positive_int(payload.get("pageNum"), 1)
    page_size = _parse_positive_int(payload.get("pageSize"), 0)
    payload["nextCursor"] = str(page_no + 1) if page_size > 0 and page_no * page_size < total else None
    return payload


def _parse_positive_int(value: Any, fallback: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return fallback
    return parsed if parsed > 0 else fallback
