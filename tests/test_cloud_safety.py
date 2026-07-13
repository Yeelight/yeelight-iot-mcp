from pathlib import Path
import sys
import unittest


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from service.model import Command, CommandParam, ControlNodeRequest
from service.pagination import append_next_cursor, resolve_page
from service.safety import build_control_plan, find_blocked_control_prop_name, is_success_response, normalize_control_body, reject_blocked_control_property, require_side_effect_confirmation
from utils.auth import normalize_authorization_header


class CloudSafetyTest(unittest.TestCase):
    def test_normalize_authorization_header_accepts_raw_and_bearer_token(self):
        self.assertEqual(normalize_authorization_header("token"), "Bearer token")
        self.assertEqual(normalize_authorization_header("Bearer token"), "Bearer token")
        self.assertEqual(normalize_authorization_header("Bearer Bearer token"), "Bearer token")

    def test_control_node_request_defaults_to_dry_run(self):
        request = ControlNodeRequest(
            nodeId=1,
            nodeType=2,
            command=Command(command="set", params=[CommandParam(propName="p", value=True)]),
        )

        self.assertTrue(request.dryRun)
        self.assertFalse(request.confirmSideEffect)

    def test_control_body_normalizes_string_values_by_prop_name(self):
        body = normalize_control_body({
            "command": "set",
            "params": [
                {"propName": "p", "value": "false"},
                {"propName": "l", "value": "80"},
                {"propName": "ct", "value": "4000"},
                {"propName": "name", "value": "80"},
            ],
        })

        self.assertIs(body["params"][0]["value"], False)
        self.assertEqual(body["params"][1]["value"], 80)
        self.assertEqual(body["params"][2]["value"], 4000)
        self.assertEqual(body["params"][3]["value"], "80")

    def test_blocked_control_property_is_rejected(self):
        body = {
            "command": "set",
            "params": [
                {"propName": "rs", "value": "opening"},
                {"propName": "tp", "value": "80"},
            ],
        }
        plan = build_control_plan("POST", "https://api.example/control", {"authorization": "Bearer token"}, body)

        prop_name = find_blocked_control_prop_name(body)
        result = reject_blocked_control_property(prop_name, True, plan)

        self.assertEqual(prop_name, "rs")
        self.assertFalse(result.ok)
        self.assertTrue(result.dryRun)
        self.assertEqual(result.code, "CONTROL_PROPERTY_NOT_ALLOWED")

    def test_dry_run_returns_plan_without_real_execution(self):
        plan = build_control_plan(
            "POST",
            "https://api.example/control",
            {"authorization": "Bearer token", "clientId": "client"},
            {"ok": True},
        )

        result = require_side_effect_confirmation(True, False, plan)

        self.assertTrue(result.ok)
        self.assertTrue(result.dryRun)
        self.assertEqual(result.code, "DRY_RUN")
        self.assertEqual(result.plan.headers["authorization"], "Bearer ****")

    def test_real_execution_requires_confirm_side_effect(self):
        plan = build_control_plan("POST", "https://api.example/control", {"authorization": "Bearer token", "clientId": "client"})

        result = require_side_effect_confirmation(False, False, plan)

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "CONFIRM_SIDE_EFFECT_REQUIRED")

    def test_confirmed_real_execution_passes_guard(self):
        plan = build_control_plan("POST", "https://api.example/control", {"authorization": "Bearer token", "clientId": "client"})

        self.assertIsNone(require_side_effect_confirmation(False, True, plan))

    def test_success_response_requires_success_code(self):
        self.assertTrue(is_success_response({"code": "200", "success": True}))
        self.assertFalse(is_success_response({"code": "500", "success": False, "msg": "失败"}))
        self.assertFalse(is_success_response({"error": "network failed"}))

    def test_pagination_resolves_page_and_next_cursor(self):
        self.assertEqual(resolve_page("2", 20, 300, 300), (2, 20))
        self.assertEqual(resolve_page(None, None, 300, 300), (1, 300))
        self.assertEqual(resolve_page("bad", 999, 300, 300), (1, 300))
        self.assertEqual(append_next_cursor({"total": 21, "pageNum": 1, "pageSize": 20, "rows": []})["nextCursor"], "2")
        self.assertIsNone(append_next_cursor({"total": 21, "pageNum": 2, "pageSize": 20, "rows": []})["nextCursor"])


if __name__ == "__main__":
    unittest.main()
