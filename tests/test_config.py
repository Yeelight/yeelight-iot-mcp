import importlib
import os
from unittest.mock import patch


def test_environment_overrides_internal_service_defaults():
    import config.config as config

    overrides = {
        "YEELIGHT_IOT_MCP_API_BASE_URL": "https://api.example.test",
        "YEELIGHT_IOT_MCP_BIND_HOST": "0.0.0.0",
        "YEELIGHT_IOT_MCP_NACOS_ENABLED": "false",
        "YEELIGHT_IOT_MCP_NACOS_SERVER": "",
        "YEELIGHT_IOT_MCP_NACOS_WEIGHT": "invalid",
    }
    with patch.dict(os.environ, overrides):
        reloaded = importlib.reload(config)
        assert reloaded.settings.API_BASE_URL == "https://api.example.test"
        assert reloaded.settings.BIND_HOST == "0.0.0.0"
        assert reloaded.settings.NACOS_CONFIG["enable"] is False
        assert reloaded.settings.NACOS_CONFIG["server"] == ""
        assert reloaded.settings.NACOS_CONFIG["weight"] == 1.0

    importlib.reload(config)
