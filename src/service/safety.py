from typing import Any, Optional

from service.model import ControlExecutionResult, ControlPlan

BOOLEAN_PROP_NAMES = {"p"}
INTEGER_PROP_NAMES = {"l", "ct", "tp", "c"}
BLOCKED_CONTROL_PROP_NAMES = {"rs", "cp", "o"}


def redact_headers(headers: dict) -> dict:
    result = dict(headers)
    if result.get("authorization"):
        result["authorization"] = "Bearer ****"
    if result.get("clientId"):
        result["clientId"] = "****"
    return result


def build_control_plan(method: str, url: str, headers: dict, body: Optional[Any] = None) -> ControlPlan:
    return ControlPlan(method=method, url=url, headers=redact_headers(headers), body=body)


def normalize_control_body(body: Optional[Any]) -> Optional[Any]:
    if not isinstance(body, dict):
        return body
    normalized = dict(body)
    params = normalized.get("params")
    if isinstance(params, list):
        normalized["params"] = [normalize_command_param(item) for item in params]
    return normalized


def find_blocked_control_prop_name(body: Optional[Any]) -> str:
    if not isinstance(body, dict):
        return ""
    params = body.get("params")
    if not isinstance(params, list):
        return ""
    for param in params:
        if not isinstance(param, dict):
            continue
        prop_name = str(param.get("propName") or "").strip()
        if prop_name in BLOCKED_CONTROL_PROP_NAMES:
            return prop_name
    return ""


def normalize_command_param(param: Any) -> Any:
    if not isinstance(param, dict):
        return param
    normalized = dict(param)
    prop_name = str(normalized.get("propName") or "")
    value = normalized.get("value")
    if prop_name in BOOLEAN_PROP_NAMES:
        normalized["value"] = normalize_boolean_value(value)
    elif prop_name in INTEGER_PROP_NAMES:
        normalized["value"] = normalize_integer_value(value)
    return normalized


def normalize_boolean_value(value: Any) -> Any:
    if isinstance(value, str):
        text = value.strip().lower()
        if text == "true":
            return True
        if text == "false":
            return False
    return value


def normalize_integer_value(value: Any) -> Any:
    if isinstance(value, str):
        text = value.strip()
        if text.isdigit():
            return int(text)
    return value


def is_success_response(response: Any) -> bool:
    if not isinstance(response, dict):
        return False
    if response.get("error"):
        return False
    if response.get("success") is False:
        return False
    code = response.get("code")
    return code in ("200", 200, None)


def require_side_effect_confirmation(dry_run: bool, confirm_side_effect: bool, plan: ControlPlan) -> ControlExecutionResult | None:
    if dry_run:
        return ControlExecutionResult(ok=True, dryRun=True, code="DRY_RUN", message="dryRun 已生成执行计划，未调用真实控制接口", plan=plan)
    if not confirm_side_effect:
        return ControlExecutionResult(
            ok=False,
            dryRun=False,
            code="CONFIRM_SIDE_EFFECT_REQUIRED",
            message="真实执行控制操作必须显式传 confirmSideEffect=true",
            plan=plan,
        )
    return None


def reject_blocked_control_property(prop_name: str, dry_run: bool, plan: ControlPlan) -> ControlExecutionResult:
    return ControlExecutionResult(
        ok=False,
        dryRun=dry_run,
        code="CONTROL_PROPERTY_NOT_ALLOWED",
        message=f"属性 {prop_name} 是只读/状态属性，不允许控制。请使用设备列表中可控制的属性。",
        plan=plan,
    )
