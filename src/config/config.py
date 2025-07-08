class Config:
    MCP_SERVER_NAME = "Yeelight IoT Mcp Server Server"
    API_BASE_URL = "https://api.yeelight.com"
    HTTP_TIMEOUT = 15
    MCP_PATH = "/mcp"
    STATELESS_HTTP=True
    # AUTHORIZATION_HEADER_KEY="Authorization"
    AUTHORIZATION_HEADER_KEY="access_token"
    FETCH_NODES_MAX_SIZE=300

settings = Config()
