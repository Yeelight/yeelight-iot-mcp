# Integration Guide

[简体中文](integration.zh-CN.md) | [README](../README.md) | [Usage](usage.md)

Repository access: [GitHub](https://github.com/Yeelight/yeelight-iot-mcp) is
canonical; use the read-only [Gitee](https://gitee.com/yeelight/yeelight-iot-mcp)
or [GitCode](https://gitcode.com/Yeelight/yeelight-iot-mcp) mirror when GitHub is
not reachable, with [GitLab.com](https://gitlab.com/Yeelight/yeelight-iot-mcp)
as a global fallback.

This guide connects an MCP client to the hosted or local Yeelight IoT MCP
server. Treat `tools/list` schemas as the current contract.

## Choose the Right Server

| Workload | Server |
| --- | --- |
| Live device discovery, state, control, and scene execution | Yeelight IoT MCP |
| Home, room, device, group, panel, scene, or automation management | [Yeelight Metadata MCP](https://github.com/Yeelight/yeelight-metadata-mcp) |
| Gateway-local discovery and control | The MCP service exposed by the local gateway |

IoT MCP and Metadata MCP can be configured together. They use the same cloud
context headers but expose different tool surfaces.

## Hosted Streamable HTTP

Use this endpoint:

```text
https://api.yeelight.com/apis/mcp_server/v1/mcp
```

Provide the following headers through the client's secret storage:

```text
Authorization: <YOUR_AUTHORIZATION>
Client-Id: <YOUR_CLIENT_ID>
House-Id: <YOUR_HOUSE_ID>
```

## Cursor and Similar Clients

```json
{
  "mcpServers": {
    "yeelight-iot": {
      "url": "https://api.yeelight.com/apis/mcp_server/v1/mcp",
      "headers": {
        "Authorization": "<YOUR_AUTHORIZATION>",
        "Client-Id": "<YOUR_CLIENT_ID>",
        "House-Id": "<YOUR_HOUSE_ID>"
      }
    }
  }
}
```

Restart the client after editing its configuration. Confirm connection by
listing tools and calling a read-only tool such as `get_currnet_house_info`.

## Claude Desktop with `mcp-remote`

```json
{
  "mcpServers": {
    "yeelight-iot": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://api.yeelight.com/apis/mcp_server/v1/mcp",
        "--header", "Authorization:${AUTHORIZATION}",
        "--header", "Client-Id:${CLIENT_ID}",
        "--header", "House-Id:${HOUSE_ID}"
      ],
      "env": {
        "AUTHORIZATION": "<YOUR_AUTHORIZATION>",
        "CLIENT_ID": "<YOUR_CLIENT_ID>",
        "HOUSE_ID": "<YOUR_HOUSE_ID>"
      }
    }
  }
}
```

Use the current `mcp-remote` documentation if the client changes its transport
or header syntax.

## Local Source Server

```bash
uv sync --extra test

YEELIGHT_IOT_MCP_NACOS_ENABLED=false \
PYTHONPATH=src \
uv run uvicorn main:streamable_http_app --host 127.0.0.1 --port 9000
```

Configure the client URL as `http://127.0.0.1:9000/mcp`. Authentication remains
required because the local server forwards requests to the Yeelight cloud.

Do not bind to a public interface without a trusted reverse proxy, network
policy, TLS, and appropriate secret handling. The built-in middleware validates
Authorization but is not a complete public edge security layer.

## Integration Workflow

1. Connect and initialize the MCP session.
2. Call `tools/list` and read current schemas.
3. Resolve the selected house and target entities with read tools.
4. Follow `nextCursor` until it is empty when a full list is required.
5. Inspect the target's property definitions and supported operators.
6. Call a write tool with its default dry-run behavior.
7. Review the redacted plan and obtain user confirmation.
8. Resend with `dryRun=false` and `confirmSideEffect=true` only once.
9. Query current state after execution when possible.

## Troubleshooting

- `401`: verify the Authorization header and provision a new token if expired.
- Empty or wrong topology: verify `House-Id` and refresh list tools.
- Missing target: resolve the name to the current numeric node ID first.
- Validation error: refresh `tools/list` instead of guessing request fields.
- Timeout: verify endpoint, proxy, DNS, and `YEELIGHT_IOT_MCP_HTTP_TIMEOUT`.
- Local Nacos errors: set `YEELIGHT_IOT_MCP_NACOS_ENABLED=false` unless service
  registration is intentionally configured.

Never print credentials while diagnosing client configuration.
