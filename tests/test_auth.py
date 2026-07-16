import asyncio
import base64
import json
from pathlib import Path
import sys


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config.yeelight_ai import CloudProfile
from middleware.auth import AuthMiddleware


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

    def forbidden_profile():
        raise AssertionError("Header 模式不应读取本机 Profile")

    monkeypatch.setattr("middleware.auth.load_cloud_profile", forbidden_profile)
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


def test_local_loopback_falls_back_to_complete_cli_profile(monkeypatch):
    middleware = configured_middleware(monkeypatch, runtime_env="local", bind_host="127.0.0.1")
    token = fake_jwt({"region": "EU", "client_id": "profile-client"})
    monkeypatch.setattr("middleware.auth.load_cloud_profile", lambda: CloudProfile(
        name="default",
        authorization=token,
        house_id="profile-house",
        region="cn",
    ))
    middleware.check_token_valid = lambda *args: async_true()
    middleware.resolve_first_house = lambda *args: async_value("unexpected")

    async def call_next(request):
        return request.state.cloud_context

    context = asyncio.run(middleware.dispatch(Request(), call_next))

    assert context.credential_source == "yeelight-ai"
    assert context.region == "eu"
    assert context.house_id == "profile-house"
    assert context.client_id == "profile-client"


def test_public_binding_without_authorization_does_not_read_profile(monkeypatch):
    middleware = configured_middleware(monkeypatch, runtime_env="prod", bind_host="0.0.0.0")
    monkeypatch.setattr(
        "middleware.auth.load_cloud_profile",
        lambda: (_ for _ in ()).throw(AssertionError("公网模式不应读取本机 Profile")),
    )

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
