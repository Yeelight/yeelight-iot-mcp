# Usage Guide

[简体中文](usage.zh-CN.md) | [README](../README.md) | [Integration](integration.md)

The exact envelope used to call a tool depends on the MCP client. The JSON
objects below are the arguments for the named tool.

## Read the Current House

Call `get_currnet_house_info` with no arguments:

```json
{}
```

The historical spelling `currnet` is part of the public tool name and is kept
for compatibility.

## List Topology

Call `get_areas`, `get_rooms`, or `get_scenes`:

```json
{
  "limit": 100
}
```

If `nextCursor` is present, pass it to the next call:

```json
{
  "cursor": "2",
  "limit": 100
}
```

Call `get_devices` or `get_groups` without `roomId` for the whole house, or
filter by a room:

```json
{
  "roomId": "<ROOM_ID>",
  "limit": 100
}
```

Resolve names to current IDs before control. Do not assume IDs from a previous
home or stale cache.

## Preview a Device Control

Call `control_node`. The default `dryRun=true` returns a redacted plan and does
not call the control API:

```json
{
  "controlRequest": {
    "nodeId": 123456,
    "nodeType": 2,
    "command": {
      "command": "set",
      "params": [
        {
          "propName": "l",
          "value": 60
        }
      ]
    },
    "reason": "Set the selected light to 60 percent"
  }
}
```

Node types are `1=room`, `2=device`, `3=area`, `4=group`, and `5=house`.
Common property IDs include `p` for power, `l` for brightness, `c` for decimal
RGB color, `ct` for color temperature, and `tp` for curtain target position.
Always use the target's returned property schema and supported operators.

## Execute a Confirmed Device Control

After reviewing the plan and obtaining confirmation, resend the same request
with both flags changed:

```json
{
  "controlRequest": {
    "nodeId": 123456,
    "nodeType": 2,
    "command": {
      "command": "set",
      "params": [
        {
          "propName": "p",
          "value": true
        }
      ]
    },
    "dryRun": false,
    "confirmSideEffect": true,
    "reason": "User confirmed turning on the selected light"
  }
}
```

Successful execution returns `code=EXECUTED`. A missing confirmation returns
`CONFIRM_SIDE_EFFECT_REQUIRED`. The property `rs` is blocked by policy.

## Preview and Execute a Scene

Call `execute_scene` in dry-run mode:

```json
{
  "request": {
    "sceneId": "<SCENE_ID>",
    "reason": "Preview the selected scene"
  }
}
```

For confirmed execution:

```json
{
  "request": {
    "sceneId": "<SCENE_ID>",
    "dryRun": false,
    "confirmSideEffect": true,
    "reason": "User confirmed executing the selected scene"
  }
}
```

## Operating Rules

- Keep Authorization, Client ID, and House ID out of tool arguments and logs;
  they belong in transport headers.
- Follow pagination when a complete topology is required.
- Use returned IDs, property types, ranges, enum values, and operators.
- Preview every write and scene execution.
- Require confirmation in the caller before live execution.
- Verify resulting state when the API supports a read-back.
- Do not blindly retry failed side effects.
