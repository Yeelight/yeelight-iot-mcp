from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CredentialBundle:
    authorization: str
    region: str | None
    house_id: str | None
    source: str


@dataclass(frozen=True)
class CloudContext:
    authorization: str
    region: str
    api_base_url: str
    house_id: str
    client_id: str | None
    credential_source: str


def build_upstream_headers(context: CloudContext) -> dict[str, str]:
    headers = {"authorization": context.authorization}
    if context.client_id:
        headers["clientId"] = context.client_id
    return headers


def first_pro_house_id(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    if "code" in payload and str(payload.get("code")) != "200":
        return None
    if payload.get("success") is False:
        return None

    data = payload.get("data")
    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict):
        rows = next(
            (
                data[key]
                for key in ("rows", "list", "houses", "houseList", "data")
                if isinstance(data.get(key), list)
            ),
            [],
        )
    else:
        rows = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        value = row.get("houseId")
        if value is None:
            value = row.get("id")
        if value is None:
            value = row.get("value")
        text = str(value).strip() if value is not None else ""
        if text:
            return text
    return None
