import base64
import json
from pathlib import Path
import sys


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from utils.auth import extract_token_claims, resolve_upstream_client_id


def fake_jwt(payload):
    def encode(value):
        raw = json.dumps(value, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    return f"{encode({'alg': 'none'})}.{encode(payload)}.signature"


def test_extract_token_claims_supports_bearer_region_and_client_id():
    claims = extract_token_claims(
        f"Bearer {fake_jwt({'region': 'CN', 'client_id': 'iot-platform'})}"
    )

    assert claims.region == "cn"
    assert claims.client_id == "iot-platform"


def test_extract_token_claims_never_exposes_unrelated_payload():
    claims = extract_token_claims(fake_jwt({"region": "SG", "username": "private"}))

    assert claims.region == "sg"
    assert claims.client_id is None
    assert not hasattr(claims, "username")


def test_extract_token_claims_tolerates_invalid_tokens_and_claims():
    assert extract_token_claims("opaque-token").region is None
    assert extract_token_claims("broken.payload.signature").client_id is None
    claims = extract_token_claims(fake_jwt({"region": {}, "client_id": "x" * 300}))
    assert claims.region is None
    assert claims.client_id is None


def test_upstream_client_id_prefers_jwt_and_uses_region_defaults():
    assert resolve_upstream_client_id("jwt-client", "cn") == "jwt-client"
    assert resolve_upstream_client_id(None, "dev") == "dev"
    for region in ("cn", "sg", "us", "eu"):
        assert resolve_upstream_client_id(None, region) == "iot-app"
