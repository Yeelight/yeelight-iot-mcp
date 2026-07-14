import importlib
import os
import sys
import unittest
from contextlib import contextmanager
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


ENV_NAMES = [
    "YEELIGHT_IOT_MCP_RUNTIME_ENV",
    "YEELIGHT_IOT_MCP_NACOS_ENABLED",
    "YEELIGHT_IOT_MCP_BIND_HOST",
    "YEELIGHT_IOT_MCP_PORT",
    "YEELIGHT_IOT_MCP_PATH",
    "IOT_MCP_RUNTIME_ENV",
    "IOT_MCP_NACOS_ENABLE",
    "IOT_MCP_BIND_HOST",
    "IOT_MCP_PORT",
    "IOT_MCP_PATH",
    "APP_MCP_RUNTIME_ENV",
    "APP_MCP_NACOS_ENABLE",
    "APP_MCP_BIND_HOST",
    "APP_MCP_PORT",
    "APP_MCP_PATH",
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
        for name in ENV_NAMES:
            if original[name] is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = original[name]


def load_main(env):
    with isolated_mcp_env(env):
        for name in list(sys.modules):
            if (
                name == "main"
                or name == "config.config"
                or name == "register.register"
                or name.startswith("config.")
                or name.startswith("register.")
            ):
                sys.modules.pop(name)
        return importlib.import_module("main")


class CloudMainTest(unittest.TestCase):
    def test_fastmcp_uses_local_bind_host_in_test_runtime(self):
        main = load_main({
            "IOT_MCP_RUNTIME_ENV": "test",
            "IOT_MCP_NACOS_ENABLE": "false",
        })

        self.assertEqual(main.mcp.settings.host, "127.0.0.1")
        self.assertEqual(main.mcp.settings.port, 9000)
        transport_security = getattr(main.mcp.settings, "transport_security", None)
        if transport_security is not None:
            self.assertTrue(transport_security.enable_dns_rebinding_protection)
            self.assertIn("127.0.0.1:*", transport_security.allowed_hosts)

    def test_fastmcp_uses_public_bind_host_in_prod_runtime(self):
        main = load_main({
            "IOT_MCP_RUNTIME_ENV": "prod",
            "IOT_MCP_NACOS_ENABLE": "false",
        })

        self.assertEqual(main.mcp.settings.host, "0.0.0.0")
        self.assertEqual(main.mcp.settings.port, 9000)
        self.assertIsNone(getattr(main.mcp.settings, "transport_security", None))

    def test_fastmcp_bind_host_override_keeps_local_host_protection(self):
        main = load_main({
            "IOT_MCP_RUNTIME_ENV": "prod",
            "IOT_MCP_NACOS_ENABLE": "false",
            "IOT_MCP_BIND_HOST": "127.0.0.1",
            "IOT_MCP_PORT": "19000",
        })

        self.assertEqual(main.mcp.settings.host, "127.0.0.1")
        self.assertEqual(main.mcp.settings.port, 19000)
        transport_security = getattr(main.mcp.settings, "transport_security", None)
        if transport_security is not None:
            self.assertTrue(transport_security.enable_dns_rebinding_protection)


if __name__ == "__main__":
    unittest.main()
