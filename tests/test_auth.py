import asyncio
import base64
import json
from pathlib import Path
import sys


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from middleware.auth import AuthMiddleware
from service.request_context import CredentialBundle


class Headers(dict):
    def get(self, key, default=None):
        lowered = key.lower()
        for name, value in self.items():
            if name.lower() == lowered:
                return value
        return default


class State:
    pass


class Request:
    def __init__(self, headers=None):
        self.headers = Headers(headers or {})
        self.state = State()


def fake_jwt(payload):
    def encode(value):
        raw = json.dumps(value, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    return f"{encode({'alg': 'none'})}.{encode(payload)}.signature"


def configured_middleware(monkeypatch, *, runtime_env="prod", bind_host="0.0.0.0"):
    middleware = object.__new__(AuthMiddleware)
    monkeypatch.setattr("middleware.auth.settings.RUNTIME_ENV", runtime_env)
    monkeypatch.setattr("middleware.auth.settings.BIND_HOST", bind_host)
    monkeypatch.setattr("middleware.auth.settings.DEFAULT_REGION", "cn")
    monkeypatch.setattr("middleware.auth.settings.API_BASE_URL", "https://api.yeelight.com")
    return middleware


def test_first_pro_house_uses_post_and_pro_business_type(monkeypatch):
    calls = []

    class Response:
        @staticmethod
        def json():
            return {"code": "200", "data": [{"houseId": "first-pro-house"}]}

    class AsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, *args, **kwargs):
            raise AssertionError("Pro 家庭发现必须使用 POST")

        async def post(self, url, *, headers, json):
            calls.append({"url": url, "headers": headers, "json": json})
            return Response()

    monkeypatch.setattr(
        "middleware.auth.httpx.AsyncClient",
        lambda **kwargs: AsyncClient(),
    )
    middleware = configured_middleware(monkeypatch)

    house_id = asyncio.run(middleware.resolve_first_house(
        "Bearer token",
        "https://api.yeelight.com",
    ))

    assert house_id == "first-pro-house"
    assert calls == [{
        "url": "https://api.yeelight.com/apis/iot/v1/house/r/list",
        "headers": {"authorization": "Bearer token", "bizType": "0"},
        "json": {},
    }]


def test_header_bundle_uses_jwt_region_client_id_and_first_pro_house(monkeypatch):
    middleware = configured_middleware(monkeypatch)
    calls = []

    async def valid(authorization, api_base_url):
        calls.append(("validate", authorization, api_base_url))
        return True

    async def first_house(authorization, api_base_url):
        calls.append(("house", authorization, api_base_url))
        return "first-house"

    middleware.check_token_valid = valid
    middleware.resolve_first_house = first_house

    async def call_next(request):
        return request.state.cloud_context

    token = fake_jwt({"region": "EU", "client_id": "jwt-client"})
    context = asyncio.run(middleware.dispatch(
        Request({"Authorization": token, "Client-Id": "untrusted-client"}),
        call_next,
    ))

    assert context.region == "eu"
    assert context.api_base_url == "https://api-de.yeelight.com"
    assert context.house_id == "first-house"
    assert context.client_id == "jwt-client"
    assert context.credential_source == "header"
    assert calls == [
        ("validate", f"Bearer {token}", "https://api-de.yeelight.com"),
        ("house", f"Bearer {token}", "https://api-de.yeelight.com"),
    ]


def test_explicit_header_bundle_does_not_read_or_mix_local_profile(monkeypatch):
    middleware = configured_middleware(monkeypatch, runtime_env="local", bind_host="127.0.0.1")
    middleware.check_token_valid = lambda *args: async_true()
    middleware.resolve_first_house = lambda *args: async_value("unexpected")

    async def call_next(request):
        return request.state.cloud_context

    token = fake_jwt({"region": "US", "client_id": "jwt-client"})
    context = asyncio.run(middleware.dispatch(Request({
        "Authorization": token,
        "Yeelight-Region": "sg",
        "House-Id": "header-house",
    }), call_next))

    assert context.region == "sg"
    assert context.house_id == "header-house"


def test_explicit_test_credential_provider_can_supply_isolated_bundle(monkeypatch):
    middleware = configured_middleware(monkeypatch, runtime_env="local", bind_host="127.0.0.1")
    token = fake_jwt({"region": "EU", "client_id": "profile-client"})
    middleware.credential_provider = lambda _request: CredentialBundle(
        authorization=token,
        house_id="profile-house",
        region="cn",
        source="test-injection",
    )
    middleware.check_token_valid = lambda *args: async_true()
    middleware.resolve_first_house = lambda *args: async_value("unexpected")

    async def call_next(request):
        return request.state.cloud_context

    context = asyncio.run(middleware.dispatch(Request(), call_next))

    assert context.credential_source == "test-injection"
    assert context.region == "cn"
    assert context.house_id == "profile-house"
    assert context.client_id == "profile-client"


def test_public_binding_without_authorization_does_not_read_profile(monkeypatch):
    middleware = configured_middleware(monkeypatch, runtime_env="prod", bind_host="0.0.0.0")

    async def call_next(request):
        raise AssertionError("缺少认证不应继续")

    response = asyncio.run(middleware.dispatch(Request(), call_next))

    assert response.status_code == 401


def test_local_loopback_without_header_or_injection_is_rejected(monkeypatch):
    middleware = configured_middleware(monkeypatch, runtime_env="local", bind_host="127.0.0.1")

    async def call_next(request):
        raise AssertionError("缺少认证不应继续")

    response = asyncio.run(middleware.dispatch(Request(), call_next))

    assert response.status_code == 401


def test_unknown_explicit_region_is_rejected_before_validation(monkeypatch):
    middleware = configured_middleware(monkeypatch)
    called = False

    async def valid(*args):
        nonlocal called
        called = True
        return True

    middleware.check_token_valid = valid

    async def call_next(request):
        raise AssertionError("未知 Region 不应继续")

    response = asyncio.run(middleware.dispatch(Request({
        "Authorization": "opaque-token",
        "Yeelight-Region": "mars",
    }), call_next))

    assert response.status_code == 400
    assert called is False


def test_valid_opaque_token_uses_region_default_client_id(monkeypatch):
    middleware = configured_middleware(monkeypatch)
    middleware.check_token_valid = lambda *args: async_true()
    middleware.resolve_first_house = lambda *args: async_value("unexpected")

    async def call_next(request):
        return request.state.cloud_context

    context = asyncio.run(middleware.dispatch(Request({
        "Authorization": "opaque-token",
        "Yeelight-Region": "us",
        "House-Id": "house-us",
    }), call_next))

    assert context.client_id == "iot-app"


async def async_true():
    return True


async def async_value(value):
    return value
