def normalize_authorization_header(value: str) -> str:
    token = (value or "").strip()
    while token.lower().startswith("bearer "):
        token = token[7:].strip()
    return f"Bearer {token}" if token else ""
