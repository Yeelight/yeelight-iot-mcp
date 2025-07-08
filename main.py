from mcp.server.fastmcp import FastMCP
from service.mcp_service import register_tools
from middleware.auth import AuthMiddleware
from config.config import settings
import uvicorn

mcp = FastMCP(settings.MCP_SERVER_NAME, stateless_http=settings.STATELESS_HTTP, path=settings.MCP_PATH)
register_tools(mcp)
streamable_http_app = mcp.streamable_http_app()
streamable_http_app.add_middleware(AuthMiddleware)

# development launch
if __name__ == "__main__":
    uvicorn.run(streamable_http_app, host="0.0.0.0", port=9000)