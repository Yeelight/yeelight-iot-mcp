from mcp.server.fastmcp import FastMCP
from service.mcp_service import register_tools
from middleware.auth import AuthMiddleware
from config.config import settings
import uvicorn
from register.register import get_nacos_registration

try:
    from mcp.server.fastmcp.server import Settings as FastMCPSettings
except ImportError:
    FastMCPSettings = None


def create_mcp_server() -> FastMCP:
    kwargs = {
        "host": settings.BIND_HOST,
        "port": settings.PORT,
        "stateless_http": settings.STATELESS_HTTP,
    }
    setting_names = getattr(FastMCPSettings, "model_fields", {})
    if "streamable_http_path" in setting_names:
        kwargs["streamable_http_path"] = settings.MCP_PATH
    elif "path" in setting_names:
        kwargs["path"] = settings.MCP_PATH
    return FastMCP(settings.MCP_SERVER_NAME, **kwargs)


mcp = create_mcp_server()
register_tools(mcp)

get_nacos_registration().register_instance()

streamable_http_app = mcp.streamable_http_app()
streamable_http_app.add_middleware(AuthMiddleware)


if __name__ == "__main__":
    uvicorn.run(streamable_http_app, host=settings.BIND_HOST, port=settings.PORT)
