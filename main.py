from mcp.server.fastmcp import FastMCP
from service.mcp_service import register_tools
from middleware.auth import AuthMiddleware
from config.config import settings
from inspect import signature
import uvicorn
from register.register import get_nacos_registration


def create_mcp_server() -> FastMCP:
    init_params = signature(FastMCP).parameters
    kwargs = {"stateless_http": settings.STATELESS_HTTP}
    if "streamable_http_path" in init_params:
        kwargs["streamable_http_path"] = settings.MCP_PATH
    else:
        kwargs["path"] = settings.MCP_PATH
    return FastMCP(settings.MCP_SERVER_NAME, **kwargs)


mcp = create_mcp_server()
register_tools(mcp)

get_nacos_registration().register_instance()

streamable_http_app = mcp.streamable_http_app()
streamable_http_app.add_middleware(AuthMiddleware)


# development launch
if __name__ == "__main__":
    uvicorn.run(streamable_http_app, host=settings.BIND_HOST, port=9000)
