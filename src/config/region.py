from urllib.parse import urlsplit, urlunsplit


DEFAULT_REGION = "cn"
REGION_ORIGINS = {
    "cn": "https://api.yeelight.com",
    "sg": "https://api-sg.yeelight.com",
    "us": "https://api-us.yeelight.com",
    "eu": "https://api-de.yeelight.com",
    "dev": "http://api-dev.yeedev.com",
}
REGION_ALIASES = {
    "de": "eu",
    "local_dev": "dev",
    "local-dev": "dev",
    "cloud_region_cn": "cn",
    "cloud_region_sg": "sg",
    "cloud_region_us": "us",
    "cloud_region_eu": "eu",
}


class RegionError(ValueError):
    pass


def normalize_region(value: str | None, fallback: str = DEFAULT_REGION) -> str:
    text = str(value or fallback).strip().lower()
    region = REGION_ALIASES.get(text, text)
    if region not in REGION_ORIGINS:
        raise RegionError(f"不支持的 Region: {value}。可选: cn、sg、us、eu。")
    return region


def resolve_region(request_region: str | None, deployment_default: str | None = None) -> str:
    return normalize_region(request_region or deployment_default or DEFAULT_REGION)


def normalize_api_base_url(value: str | None) -> str:
    raw = str(value or REGION_ORIGINS[DEFAULT_REGION]).strip().rstrip("/")
    if raw.endswith("/apis/iot"):
        raw = raw[: -len("/apis/iot")]
    parsed = urlsplit(raw)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", ""))


def api_base_for_region(
    region: str,
    configured_base_url: str | None = None,
    deployment_default: str | None = None,
) -> str:
    normalized_region = normalize_region(region)
    configured = normalize_api_base_url(configured_base_url) if configured_base_url else None
    standard_origins = {normalize_api_base_url(origin) for origin in REGION_ORIGINS.values()}
    if configured is None or configured in standard_origins:
        return REGION_ORIGINS[normalized_region]

    default_region = normalize_region(deployment_default)
    if normalized_region != default_region:
        raise RegionError(
            f"自定义 API 地址固定 Region 为 {default_region}，不能处理 {normalized_region} 请求。"
        )
    return configured
