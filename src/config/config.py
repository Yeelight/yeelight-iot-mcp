import os


_SERVICE_NAME = "yeelight-online-iot-mcp-server"
_DEFAULT_API_BASE_URL = "https://api.yeelight.com"

try:
    from config.internal_defaults import INTERNAL_LOGGER_CONFIG, INTERNAL_NACOS_CONFIG
except ImportError:
    INTERNAL_LOGGER_CONFIG = {}
    INTERNAL_NACOS_CONFIG = {}


def _env(names, default=None):
    for name in names:
        value = os.getenv(name)
        if value is not None:
            return value
    return default


def _env_bool(names, default):
    value = _env(names)
    if value is None:
        return bool(default)
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(names, default):
    value = _env(names)
    if value is None:
        return int(default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _env_float(names, default):
    value = _env(names)
    if value is None:
        return float(default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


_RUNTIME_ENV = str(
    _env(
        [
            "YEELIGHT_IOT_MCP_RUNTIME_ENV",
            "IOT_MCP_RUNTIME_ENV",
            "APP_MCP_RUNTIME_ENV",
        ],
        "prod",
    )
).lower()


def default_bind_host():
    if _RUNTIME_ENV in {"local", "test"}:
        return "127.0.0.1"
    return "0.0.0.0"


_DEFAULT_NACOS_SERVICE_NAME = (
    INTERNAL_NACOS_CONFIG.get("service-name", f"{_SERVICE_NAME}-prod")
    if _RUNTIME_ENV == "prod"
    else f"{_SERVICE_NAME}-dev"
)
_DEFAULT_NACOS_ENABLED = (
    False
    if _RUNTIME_ENV in {"local", "test"}
    else bool(INTERNAL_NACOS_CONFIG.get("enable", False))
)
_DEFAULT_PORT = INTERNAL_NACOS_CONFIG.get("port", 9000)


class Config:
    MCP_SERVER_NAME = _env(
        [
            "YEELIGHT_IOT_MCP_SERVER_NAME",
            "IOT_MCP_SERVER_NAME",
            "APP_MCP_SERVER_NAME",
        ],
        "Yeelight IoT MCP Server",
    )
    SERVICE_NAME = _SERVICE_NAME
    RUNTIME_ENV = _RUNTIME_ENV
    API_BASE_URL = _env(
        [
            "YEELIGHT_IOT_MCP_API_BASE_URL",
            "IOT_MCP_API_BASE_URL",
            "APP_MCP_API_BASE_URL",
        ],
        _DEFAULT_API_BASE_URL,
    ).rstrip("/")
    HTTP_TIMEOUT = _env_int(
        [
            "YEELIGHT_IOT_MCP_HTTP_TIMEOUT",
            "IOT_MCP_HTTP_TIMEOUT",
            "APP_MCP_HTTP_TIMEOUT",
        ],
        15,
    )
    MCP_PATH = _env(
        ["YEELIGHT_IOT_MCP_PATH", "IOT_MCP_PATH", "APP_MCP_PATH"],
        "/mcp",
    )
    STATELESS_HTTP = _env_bool(
        ["YEELIGHT_IOT_MCP_STATELESS_HTTP", "IOT_MCP_STATELESS_HTTP"],
        True,
    )
    AUTHORIZATION_HEADER_KEY = "Authorization"
    HOUSE_ID_HEADER_KEY = "House-Id"
    CLIENT_ID_HEADER_KEY = "Client-Id"
    FETCH_NODES_MAX_SIZE = _env_int(
        [
            "YEELIGHT_IOT_MCP_FETCH_NODES_MAX_SIZE",
            "IOT_MCP_FETCH_NODES_MAX_SIZE",
            "APP_MCP_FETCH_NODES_MAX_SIZE",
        ],
        300,
    )
    BIND_HOST = _env(
        [
            "YEELIGHT_IOT_MCP_BIND_HOST",
            "IOT_MCP_BIND_HOST",
            "APP_MCP_BIND_HOST",
        ],
        default_bind_host(),
    )
    PORT = _env_int(
        ["YEELIGHT_IOT_MCP_PORT", "IOT_MCP_PORT", "APP_MCP_PORT"],
        _DEFAULT_PORT,
    )

    NACOS_CONFIG = {
        "enable": _env_bool(
            [
                "YEELIGHT_IOT_MCP_NACOS_ENABLED",
                "YEELIGHT_IOT_MCP_NACOS_ENABLE",
                "IOT_MCP_NACOS_ENABLE",
                "APP_MCP_NACOS_ENABLE",
            ],
            _DEFAULT_NACOS_ENABLED,
        ),
        "server": _env(
            [
                "YEELIGHT_IOT_MCP_NACOS_SERVER",
                "IOT_MCP_NACOS_SERVER",
                "APP_MCP_NACOS_SERVER",
            ],
            INTERNAL_NACOS_CONFIG.get("server", ""),
        ),
        "namespace": _env(
            [
                "YEELIGHT_IOT_MCP_NACOS_NAMESPACE",
                "IOT_MCP_NACOS_NAMESPACE",
                "APP_MCP_NACOS_NAMESPACE",
            ],
            INTERNAL_NACOS_CONFIG.get("namespace", "public"),
        ),
        "service-name": _env(
            [
                "YEELIGHT_IOT_MCP_NACOS_SERVICE_NAME",
                "IOT_MCP_NACOS_SERVICE_NAME",
                "APP_MCP_NACOS_SERVICE_NAME",
            ],
            _DEFAULT_NACOS_SERVICE_NAME,
        ),
        "port": _env_int(
            [
                "YEELIGHT_IOT_MCP_NACOS_PORT",
                "IOT_MCP_NACOS_PORT",
                "APP_MCP_NACOS_PORT",
                "YEELIGHT_IOT_MCP_PORT",
                "IOT_MCP_PORT",
                "APP_MCP_PORT",
            ],
            _DEFAULT_PORT,
        ),
        "weight": _env_float(
            [
                "YEELIGHT_IOT_MCP_NACOS_WEIGHT",
                "IOT_MCP_NACOS_WEIGHT",
                "APP_MCP_NACOS_WEIGHT",
            ],
            INTERNAL_NACOS_CONFIG.get("weight", 1.0),
        ),
        "cluster-name": _env(
            [
                "YEELIGHT_IOT_MCP_NACOS_CLUSTER",
                "IOT_MCP_NACOS_CLUSTER",
                "APP_MCP_NACOS_CLUSTER",
            ],
            INTERNAL_NACOS_CONFIG.get("cluster-name", "DEFAULT"),
        ),
        "heartbeat-interval": _env_int(
            [
                "YEELIGHT_IOT_MCP_NACOS_HEARTBEAT_INTERVAL",
                "IOT_MCP_NACOS_HEARTBEAT_INTERVAL",
                "APP_MCP_NACOS_HEARTBEAT_INTERVAL",
            ],
            INTERNAL_NACOS_CONFIG.get("heartbeat-interval", 5),
        ),
    }
    LOGGER_CONFIG = {
        "logger-name": _env(
            [
                "YEELIGHT_IOT_MCP_LOGGER_NAME",
                "IOT_MCP_LOGGER_NAME",
                "APP_MCP_LOGGER_NAME",
            ],
            INTERNAL_LOGGER_CONFIG.get("logger-name", _SERVICE_NAME),
        ),
        "file-path": _env(
            [
                "YEELIGHT_IOT_MCP_LOG_DIR",
                "IOT_MCP_LOG_DIR",
                "APP_MCP_LOG_DIR",
            ],
            INTERNAL_LOGGER_CONFIG.get("file-path", f"./logs/{_SERVICE_NAME}"),
        ),
        "file-name": _env(
            [
                "YEELIGHT_IOT_MCP_LOG_FILE",
                "IOT_MCP_LOG_FILE",
                "APP_MCP_LOG_FILE",
            ],
            INTERNAL_LOGGER_CONFIG.get("file-name", f"{_SERVICE_NAME}.log"),
        ),
    }


settings = Config()
