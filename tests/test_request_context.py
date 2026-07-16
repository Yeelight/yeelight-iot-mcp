from pathlib import Path
import sys


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from service.request_context import (
    CloudContext,
    build_upstream_headers,
    first_pro_house_id,
)


def cloud_context(client_id="iot-platform"):
    return CloudContext(
        authorization="Bearer token",
        region="eu",
        api_base_url="https://api-de.yeelight.com",
        house_id="house-1",
        client_id=client_id,
        credential_source="header",
    )


def test_upstream_headers_use_authorization_and_derived_client_id():
    assert build_upstream_headers(cloud_context()) == {
        "authorization": "Bearer token",
        "clientId": "iot-platform",
    }


def test_upstream_headers_allow_validated_opaque_tokens_without_client_id():
    assert build_upstream_headers(cloud_context(None)) == {
        "authorization": "Bearer token",
    }


def test_first_pro_house_supports_array_and_rows_payloads():
    assert first_pro_house_id({"code": "200", "data": [{"houseId": 1001}]}) == "1001"
    assert first_pro_house_id({"success": True, "data": {"rows": [{"id": "house-2"}]}}) == "house-2"


def test_first_pro_house_rejects_failed_or_empty_payloads():
    assert first_pro_house_id({"code": "500", "data": [{"houseId": "wrong"}]}) is None
    assert first_pro_house_id({"code": "200", "data": []}) is None
    assert first_pro_house_id({"code": "200", "data": {"rows": [{}]}}) is None
