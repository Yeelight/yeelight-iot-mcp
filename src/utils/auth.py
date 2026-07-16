import base64
from dataclasses import dataclass
import json


@dataclass(frozen=True)
class TokenClaims:
    region: str | None = None
    client_id: str | None = None


def normalize_authorization_header(value: str | None) -> str:
    token = str(value or "").strip()
    while token.lower().startswith("bearer "):
        token = token[7:].strip()
    return f"Bearer {token}" if token else ""


def extract_token_claims(value: str | None) -> TokenClaims:
    token = normalize_authorization_header(value).removeprefix("Bearer ")
    parts = token.split(".")
    if len(parts) != 3:
        return TokenClaims()
    try:
        padding = "=" * (-len(parts[1]) % 4)
        raw = base64.urlsafe_b64decode(f"{parts[1]}{padding}")
        payload = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return TokenClaims()
    if not isinstance(payload, dict):
        return TokenClaims()
    region = _claim_text(payload.get("region"), 32)
    client_id = _claim_text(payload.get("client_id"), 255)
    return TokenClaims(
        region=region.lower() if region else None,
        client_id=client_id,
    )


def resolve_upstream_client_id(client_id: str | None, region: str) -> str:
    explicit = _claim_text(client_id, 255)
    if explicit:
        return explicit
    return "dev" if str(region).strip().lower() == "dev" else "iot-app"


def _claim_text(value, max_length: int) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text or len(text) > max_length:
        return None
    return text
