import os


_SERVICE_NAME = "yeelight-online-iot-mcp-server"

try:
    from config.internal_defaults import INTERNAL_LOGGER_CONFIG, INTERNAL_NACOS_CONFIG
except ImportError:
    INTERNAL_LOGGER_CONFIG = {}
    INTERNAL_NACOS_CONFIG = {}


def _env(name, default):
    value = os.getenv(name)
    return default if value is None else value


def _env_bool(name, default):
    value = os.getenv(name)
    if value is None:
        return bool(default)
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name, default):
    value = os.getenv(name)
    if value is None:
        return int(default)
    try:
        return int(value)
    except ValueError:
        return int(default)


def _env_float(name, default):
    value = os.getenv(name)
    if value is None:
        return float(default)
    try:
        return float(value)
    except ValueError:
        return float(default)


class Config:
    MCP_SERVER_NAME = _env("YEELIGHT_IOT_MCP_SERVER_NAME", "Yeelight IoT MCP Server")
    SERVICE_NAME = _SERVICE_NAME
    API_BASE_URL = _env("YEELIGHT_IOT_MCP_API_BASE_URL", "https://api.yeelight.com")
    HTTP_TIMEOUT = _env_int("YEELIGHT_IOT_MCP_HTTP_TIMEOUT", 15)
    MCP_PATH = _env("YEELIGHT_IOT_MCP_PATH", "/mcp")
    STATELESS_HTTP = _env_bool("YEELIGHT_IOT_MCP_STATELESS_HTTP", True)
    AUTHORIZATION_HEADER_KEY = "Authorization"
    HOUSE_ID_HEADER_KEY = "House-Id"
    CLIENT_ID_HEADER_KEY = "Client-Id"
    FETCH_NODES_MAX_SIZE = _env_int("YEELIGHT_IOT_MCP_FETCH_NODES_MAX_SIZE", 300)
    BIND_HOST = _env("YEELIGHT_IOT_MCP_BIND_HOST", "127.0.0.1")

    NACOS_CONFIG = {
        "enable": _env_bool("YEELIGHT_IOT_MCP_NACOS_ENABLED", INTERNAL_NACOS_CONFIG.get("enable", False)),
        "server": _env("YEELIGHT_IOT_MCP_NACOS_SERVER", INTERNAL_NACOS_CONFIG.get("server", "")),
        "namespace": _env("YEELIGHT_IOT_MCP_NACOS_NAMESPACE", INTERNAL_NACOS_CONFIG.get("namespace", "public")),
        "service-name": _env("YEELIGHT_IOT_MCP_NACOS_SERVICE_NAME", INTERNAL_NACOS_CONFIG.get("service-name", _SERVICE_NAME)),
        "port": _env_int("YEELIGHT_IOT_MCP_NACOS_PORT", INTERNAL_NACOS_CONFIG.get("port", 9000)),
        "weight": _env_float("YEELIGHT_IOT_MCP_NACOS_WEIGHT", INTERNAL_NACOS_CONFIG.get("weight", 1.0)),
        "cluster-name": _env("YEELIGHT_IOT_MCP_NACOS_CLUSTER", INTERNAL_NACOS_CONFIG.get("cluster-name", "DEFAULT")),
        "heartbeat-interval": _env_int("YEELIGHT_IOT_MCP_NACOS_HEARTBEAT_INTERVAL", INTERNAL_NACOS_CONFIG.get("heartbeat-interval", 5)),
    }
    LOGGER_CONFIG = {
        "logger-name": _env("YEELIGHT_IOT_MCP_LOGGER_NAME", INTERNAL_LOGGER_CONFIG.get("logger-name", _SERVICE_NAME)),
        "file-path": _env("YEELIGHT_IOT_MCP_LOG_DIR", INTERNAL_LOGGER_CONFIG.get("file-path", f"./logs/{_SERVICE_NAME}")),
        "file-name": _env("YEELIGHT_IOT_MCP_LOG_FILE", INTERNAL_LOGGER_CONFIG.get("file-name", f"{_SERVICE_NAME}.log")),
    }


settings = Config()
