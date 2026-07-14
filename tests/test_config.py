import importlib
import os
import sys
from contextlib import contextmanager
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


ENV_NAMES = [
    f"{prefix}{suffix}"
    for prefix in ("YEELIGHT_IOT_MCP_", "IOT_MCP_", "APP_MCP_")
    for suffix in (
        "RUNTIME_ENV",
        "SERVER_NAME",
        "API_BASE_URL",
        "HTTP_TIMEOUT",
        "PATH",
        "STATELESS_HTTP",
        "FETCH_NODES_MAX_SIZE",
        "BIND_HOST",
        "PORT",
        "NACOS_ENABLED",
        "NACOS_ENABLE",
        "NACOS_SERVER",
        "NACOS_NAMESPACE",
        "NACOS_SERVICE_NAME",
        "NACOS_PORT",
        "NACOS_WEIGHT",
        "NACOS_CLUSTER",
        "NACOS_HEARTBEAT_INTERVAL",
        "LOGGER_NAME",
        "LOG_DIR",
        "LOG_FILE",
    )
]


@contextmanager
def isolated_mcp_env(values=None):
    values = values or {}
    original = {name: os.environ.get(name) for name in ENV_NAMES}
    try:
        for name in ENV_NAMES:
            os.environ.pop(name, None)
        os.environ.update(values)
        yield
    finally:
        for name, value in original.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def load_config(env=None):
    with isolated_mcp_env(env):
        for name in list(sys.modules):
            if name == "config.config" or name.startswith("config."):
                sys.modules.pop(name)
        return importlib.import_module("config.config")


def test_default_runtime_uses_internal_defaults_when_available():
    config = load_config()

    assert config.settings.RUNTIME_ENV == "prod"
    assert config.settings.BIND_HOST == "0.0.0.0"
    assert config.settings.PORT == 9000
    assert config.settings.NACOS_CONFIG["enable"] is bool(
        config.INTERNAL_NACOS_CONFIG.get("enable", False)
    )
    assert config.settings.NACOS_CONFIG["server"] == config.INTERNAL_NACOS_CONFIG.get(
        "server", ""
    )


def test_dev_and_local_bind_behaviour_is_preserved():
    dev = load_config(
        {
            "IOT_MCP_RUNTIME_ENV": "dev",
            "IOT_MCP_NACOS_ENABLE": "true",
            "IOT_MCP_NACOS_SERVER": "dev-nacos.example.test:8848",
        }
    )
    assert dev.settings.RUNTIME_ENV == "dev"
    assert dev.settings.BIND_HOST == "0.0.0.0"
    assert dev.settings.NACOS_CONFIG["enable"] is True
    assert dev.settings.NACOS_CONFIG["service-name"].endswith("-dev")

    local = load_config({"IOT_MCP_RUNTIME_ENV": "local"})
    assert local.settings.RUNTIME_ENV == "local"
    assert local.settings.BIND_HOST == "127.0.0.1"
    assert local.settings.NACOS_CONFIG["enable"] is False
    assert local.settings.NACOS_CONFIG["service-name"].endswith("-dev")


def test_iot_mcp_bind_host_and_port_can_be_overridden():
    config = load_config(
        {
            "IOT_MCP_RUNTIME_ENV": "prod",
            "IOT_MCP_BIND_HOST": "127.0.0.1",
            "IOT_MCP_PORT": "19000",
        }
    )

    assert config.settings.BIND_HOST == "127.0.0.1"
    assert config.settings.PORT == 19000
    assert config.settings.NACOS_CONFIG["port"] == 19000


def test_legacy_app_mcp_environment_is_supported():
    config = load_config(
        {
            "APP_MCP_RUNTIME_ENV": "test",
            "APP_MCP_BIND_HOST": "127.0.0.2",
            "APP_MCP_PORT": "19001",
            "APP_MCP_NACOS_ENABLE": "true",
            "APP_MCP_API_BASE_URL": "https://legacy.example.test/",
        }
    )

    assert config.settings.RUNTIME_ENV == "test"
    assert config.settings.BIND_HOST == "127.0.0.2"
    assert config.settings.PORT == 19001
    assert config.settings.NACOS_CONFIG["enable"] is True
    assert config.settings.API_BASE_URL == "https://legacy.example.test"


def test_yeelight_environment_has_highest_priority():
    config = load_config(
        {
            "YEELIGHT_IOT_MCP_RUNTIME_ENV": "local",
            "IOT_MCP_RUNTIME_ENV": "dev",
            "APP_MCP_RUNTIME_ENV": "prod",
            "YEELIGHT_IOT_MCP_API_BASE_URL": "https://canonical.example.test/",
            "IOT_MCP_API_BASE_URL": "https://iot.example.test",
            "APP_MCP_API_BASE_URL": "https://legacy.example.test",
            "YEELIGHT_IOT_MCP_BIND_HOST": "127.0.0.3",
            "IOT_MCP_BIND_HOST": "127.0.0.4",
            "YEELIGHT_IOT_MCP_PORT": "19002",
            "IOT_MCP_PORT": "19003",
            "YEELIGHT_IOT_MCP_NACOS_ENABLED": "false",
            "IOT_MCP_NACOS_ENABLE": "true",
        }
    )

    assert config.settings.RUNTIME_ENV == "local"
    assert config.settings.API_BASE_URL == "https://canonical.example.test"
    assert config.settings.BIND_HOST == "127.0.0.3"
    assert config.settings.PORT == 19002
    assert config.settings.NACOS_CONFIG["port"] == 19002
    assert config.settings.NACOS_CONFIG["enable"] is False


def test_invalid_numeric_overrides_fall_back_to_service_defaults():
    config = load_config(
        {
            "YEELIGHT_IOT_MCP_HTTP_TIMEOUT": "invalid",
            "YEELIGHT_IOT_MCP_PORT": "invalid",
            "YEELIGHT_IOT_MCP_NACOS_WEIGHT": "invalid",
        }
    )

    assert config.settings.HTTP_TIMEOUT == 15
    assert config.settings.PORT == 9000
    assert config.settings.NACOS_CONFIG["port"] == 9000
    assert config.settings.NACOS_CONFIG["weight"] == 1.0
