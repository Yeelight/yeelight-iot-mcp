import json
from pathlib import Path
import sys

import pytest


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config.yeelight_ai import (
    ProfileError,
    get_config_path,
    is_local_profile_allowed,
    load_cloud_profile,
)


def write_config(directory: Path, data):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "config.json").write_text(json.dumps(data), encoding="utf-8")


def test_config_path_matches_cli_override_and_platform_defaults(tmp_path):
    assert get_config_path({"YEELIGHT_AI_CONFIG_DIR": str(tmp_path)}) == tmp_path / "config.json"
    assert get_config_path({}, platform="darwin", home=tmp_path) == tmp_path / ".config/yeelight-ai/config.json"
    assert get_config_path(
        {"APPDATA": str(tmp_path / "AppData/Roaming")},
        platform="win32",
        home=tmp_path,
    ) == tmp_path / "AppData/Roaming/yeelight-ai/config.json"


def test_load_cloud_profile_uses_cloud_auth_profile(tmp_path):
    write_config(tmp_path, {
        "auth": {
            "profiles": {
                "default": {"authorization": "wrong"},
                "pro-eu": {
                    "authorization": "Bearer test-token",
                    "houseId": "house-eu",
                    "region": "eu",
                    "bizType": "0",
                },
            },
        },
        "mcp": {"cloud": {"authProfile": "pro-eu"}},
    })

    profile = load_cloud_profile({"YEELIGHT_AI_CONFIG_DIR": str(tmp_path)})

    assert profile.name == "pro-eu"
    assert profile.authorization == "Bearer test-token"
    assert profile.house_id == "house-eu"
    assert profile.region == "eu"


def test_load_cloud_profile_rejects_missing_malformed_and_saas_config(tmp_path):
    with pytest.raises(ProfileError, match="未找到 yeelight-ai 配置"):
        load_cloud_profile({"YEELIGHT_AI_CONFIG_DIR": str(tmp_path)})

    (tmp_path / "config.json").write_text("not-json", encoding="utf-8")
    with pytest.raises(ProfileError, match="无法解析"):
        load_cloud_profile({"YEELIGHT_AI_CONFIG_DIR": str(tmp_path)})

    write_config(tmp_path, {
        "auth": {"profiles": {"default": {
            "authorization": "token",
            "houseId": "saas-project",
            "region": "cn",
            "bizType": "1",
        }}},
        "mcp": {"cloud": {"authProfile": "default"}},
    })
    with pytest.raises(ProfileError, match="商照"):
        load_cloud_profile({"YEELIGHT_AI_CONFIG_DIR": str(tmp_path)})


def test_local_profile_fallback_requires_local_runtime_and_loopback():
    assert is_local_profile_allowed("local", "127.0.0.1") is True
    assert is_local_profile_allowed("test", "::1") is True
    assert is_local_profile_allowed("local", "localhost") is True
    assert is_local_profile_allowed("prod", "127.0.0.1") is False
    assert is_local_profile_allowed("local", "0.0.0.0") is False
    assert is_local_profile_allowed("local", "192.168.1.10") is False
