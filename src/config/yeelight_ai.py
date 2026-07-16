from dataclasses import dataclass
import ipaddress
import json
import os
from pathlib import Path
import sys
from typing import Mapping

from config.region import normalize_region


class ProfileError(ValueError):
    pass


@dataclass(frozen=True)
class CloudProfile:
    name: str
    authorization: str
    house_id: str | None
    region: str


def get_config_path(
    env: Mapping[str, str] | None = None,
    *,
    platform: str | None = None,
    home: Path | None = None,
) -> Path:
    values = env if env is not None else os.environ
    explicit_dir = values.get("YEELIGHT_AI_CONFIG_DIR")
    if explicit_dir:
        return Path(explicit_dir).expanduser() / "config.json"

    platform_name = platform or sys.platform
    home_dir = home or Path.home()
    if platform_name == "win32":
        app_data = Path(values.get("APPDATA", home_dir / "AppData/Roaming"))
        return app_data / "yeelight-ai/config.json"
    return home_dir / ".config/yeelight-ai/config.json"


def load_cloud_profile(env: Mapping[str, str] | None = None) -> CloudProfile:
    config_path = get_config_path(env)
    if not config_path.is_file():
        raise ProfileError(
            f"未找到 yeelight-ai 配置：{config_path}。请先运行 yeelight-ai login --qr。"
        )
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProfileError(
            f"yeelight-ai 配置无法解析：{config_path}。请重新运行 yeelight-ai login --qr。"
        ) from error
    if not isinstance(data, dict):
        raise ProfileError(f"yeelight-ai 配置格式无效：{config_path}。")

    mcp = data.get("mcp") if isinstance(data.get("mcp"), dict) else {}
    cloud = mcp.get("cloud") if isinstance(mcp.get("cloud"), dict) else {}
    profile_name = str(cloud.get("authProfile") or "default").strip() or "default"
    auth = data.get("auth") if isinstance(data.get("auth"), dict) else {}
    profiles = auth.get("profiles") if isinstance(auth.get("profiles"), dict) else {}
    profile = profiles.get(profile_name)
    if not isinstance(profile, dict):
        raise ProfileError(
            f"yeelight-ai Cloud Profile 不存在：{profile_name}。请重新运行 yeelight-ai login --qr。"
        )

    authorization = str(profile.get("authorization") or "").strip()
    if not authorization:
        raise ProfileError(
            f"yeelight-ai Cloud Profile 缺少 Authorization：{profile_name}。请重新扫码登录。"
        )
    if str(profile.get("bizType", "0")).strip() == "1":
        raise ProfileError(
            "当前 yeelight-ai Profile 是商照项目，不能用于 Pro IoT MCP。请使用 Yeelight Pro APP 重新扫码。"
        )

    house_value = profile.get("houseId")
    house_id = str(house_value).strip() if house_value is not None else ""
    return CloudProfile(
        name=profile_name,
        authorization=authorization,
        house_id=house_id or None,
        region=normalize_region(profile.get("region")),
    )


def is_local_profile_allowed(runtime_env: str, bind_host: str) -> bool:
    if str(runtime_env or "").strip().lower() not in {"local", "test"}:
        return False
    host = str(bind_host or "").strip().lower()
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False
