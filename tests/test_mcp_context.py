from pathlib import Path
import sys


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from service.request_context import CloudContext
from service import mcp_service
from service.mcp_service import get_cloud_context


class State:
    def __init__(self, cloud_context):
        self.cloud_context = cloud_context


class Request:
    def __init__(self, cloud_context):
        self.state = State(cloud_context)
        self.headers = {
            "Authorization": "untrusted-header",
            "Client-Id": "untrusted-client",
            "House-Id": "untrusted-house",
        }


class Context:
    def __init__(self, cloud_context):
        request_context = type("RequestContext", (), {})()
        request_context.request = Request(cloud_context)
        self.request_context = request_context


class FakeMcp:
    def __init__(self):
        self.tools = {}

    def tool(self, *, name, description):
        def register(function):
            self.tools[name] = function
            return function

        return register


class DummyHttpClient:
    def __init__(self):
        self.calls = []

    def get(self, url, headers):
        self.calls.append({"url": url, "headers": headers})
        return {"code": "200", "data": {"id": "house-1", "name": "Home"}}


def cloud_context():
    return CloudContext(
        authorization="Bearer validated-token",
        region="eu",
        api_base_url="https://api-de.yeelight.com",
        house_id="house-1",
        client_id="jwt-client",
        credential_source="header",
    )


def test_get_cloud_context_uses_validated_request_state_not_raw_headers():
    cloud = cloud_context()

    assert get_cloud_context(Context(cloud)) is cloud


def test_house_tool_uses_region_context_and_jwt_derived_client_id(monkeypatch):
    client = DummyHttpClient()
    monkeypatch.setattr(mcp_service, "http_client", client)
    mcp = FakeMcp()
    mcp_service.register_house_tool(mcp)

    result = mcp.tools["get_currnet_house_info"](Context(cloud_context()))

    assert result.id == "house-1"
    assert client.calls == [{
        "url": "https://api-de.yeelight.com/v1/open/node/house/house-1/r/info",
        "headers": {
            "authorization": "Bearer validated-token",
            "clientId": "jwt-client",
        },
    }]
