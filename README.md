# Yeelight IoT MCP

[简体中文](README.zh-CN.md)

Yeelight IoT MCP is the official Model Context Protocol server for Yeelight Pro
homes. It lets MCP clients discover homes, areas, rooms, devices, groups, and
scenes, read current capabilities, prepare safe device controls, and execute
confirmed controls or scenes.

## Yeelight AI Capability Matrix

These projects form a complementary stack. Choose the entry point that matches
how you integrate with Yeelight; they can also be combined.

| Project | Role and capabilities | Best for | GitHub |
| --- | --- | --- | --- |
| Yeelight Home | Recommended local semantic Runtime with one structured `invoke --stdin` boundary for queries, control, scenes, automations, lighting design, diagnostics, product knowledge, and generated apps. | Agent hosts, local automation, and applications that need a stable and policy-aware smart-home execution layer. | [Yeelight/yeelight-home](https://github.com/Yeelight/yeelight-home) |
| Yeelight Smart Home Skills | Official Agent Skills: Smart Home turns natural language into safe Runtime operations; PRO App Builder generates focused local apps from proven Runtime capabilities. | Agent hosts that need conversational smart-home workflows or app generation. | [Yeelight/yeelight-smart-home-skills](https://github.com/Yeelight/yeelight-smart-home-skills) |
| Yeelight AI CLI | Unified terminal workspace and MCP client for Cloud, Metadata, and LAN services, with local profiles, safe shortcuts, diagnostics, scripting, and AI client configuration. | People, scripts, and CI that want one general MCP and automation entry point. | [Yeelight/yeelight-cli](https://github.com/Yeelight/yeelight-cli) |
| Yeelight IoT MCP | Hosted or self-hosted Streamable HTTP MCP server for topology, live state, device control, and scene execution. | MCP clients that need direct IoT discovery and control. | [Yeelight/yeelight-iot-mcp](https://github.com/Yeelight/yeelight-iot-mcp) |
| Yeelight Metadata MCP | Hosted or self-hosted Streamable HTTP MCP server for guarded home, room, group, panel, scene, automation, favorite, and account metadata workflows. | MCP clients that need metadata inspection and management. | [Yeelight/yeelight-metadata-mcp](https://github.com/Yeelight/yeelight-metadata-mcp) |

Yeelight Home also provides system credential storage, local QR login, secret-redacted diagnostics, preview and validation, caller confirmation and Runtime policy/readback behavior, local memory and recommendation support, operation lessons, and machine-readable intent schema/explanations. Cross-platform binaries are distributed through GitHub Releases, npm, and supported package managers.

Typical paths: smart-home agents and generated apps -> Skills -> Yeelight Home; terminal users and scripts -> Yeelight AI CLI; MCP clients -> IoT MCP and/or Metadata MCP.

## Capabilities

- Streamable HTTP MCP transport.
- Official hosted endpoint or self-hosted source deployment.
- Eight tools for topology discovery, device control, and scene execution.
- Cursor pagination for area, room, device, group, and scene lists.
- Dry-run by default for device control and scene execution.
- Redacted control plans and explicit side-effect confirmation.

## Requirements

- Python 3.10 or later for local deployment.
- `uv` for the documented local workflow.
- A Yeelight authorization token, client ID, and house ID.

See the [Yeelight Open Platform documentation](https://open-console.yeelight.com/open-platform-docs-en.html)
for credential provisioning. Store credentials in the MCP client's secret
storage. Do not commit them or paste them into logs, prompts, or issue reports.

## Hosted Service

Use the official Streamable HTTP endpoint:

```text
https://api.yeelight.com/apis/mcp_server/v1/mcp
```

Required request headers:

```text
Authorization: <YOUR_AUTHORIZATION>
Client-Id: <YOUR_CLIENT_ID>
House-Id: <YOUR_HOUSE_ID>
```

The server accepts a raw token or a value prefixed with `Bearer` and normalizes
it before forwarding requests.

## Local Development

```bash
git clone https://github.com/Yeelight/yeelight-iot-mcp.git
cd yeelight-iot-mcp

uv sync --extra test
YEELIGHT_IOT_MCP_NACOS_ENABLED=false \
PYTHONPATH=src \
uv run uvicorn main:streamable_http_app --host 127.0.0.1 --port 9000
```

The local MCP URL is `http://127.0.0.1:9000/mcp`. Local deployment still uses
the same Yeelight cloud credentials and APIs; it is not an offline gateway.
Nacos registration is disabled by default in the public project and can be
enabled explicitly through environment variables.

## MCP Client Configuration

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

Restart the MCP client after changing its configuration, then verify that
`tools/list` returns the Yeelight tools.

## Tools

| Tool | Purpose | Side effect |
| --- | --- | --- |
| `get_currnet_house_info` | Read the selected house. The misspelling is retained for compatibility. | Read only |
| `get_areas` | List areas with cursor pagination. | Read only |
| `get_rooms` | List rooms with cursor pagination. | Read only |
| `get_devices` | List all devices or filter by room. | Read only |
| `get_groups` | List all groups or filter by room. | Read only |
| `get_scenes` | List scenes with cursor pagination. | Read only |
| `control_node` | Preview or execute a node property command. | Dry-run by default |
| `execute_scene` | Preview or execute a scene. | Dry-run by default |

For request examples and operating rules, read the [usage guide](guides/usage.md).
For client and deployment details, read the [integration guide](guides/integration.md).

## Safety Model

`control_node` and `execute_scene` default to `dryRun=true`. A live operation
requires both `dryRun=false` and `confirmSideEffect=true`. Callers should:

1. Resolve names to current IDs using read tools.
2. Inspect the target's supported properties and operators.
3. Generate and review a dry-run plan.
4. Obtain user confirmation in the calling application.
5. Execute once and query the resulting state when possible.

The control property `rs` is blocked by the current safety policy. Do not retry
failed writes or scene executions blindly.

## Configuration

Common environment variables for local deployments:

| Variable | Default | Purpose |
| --- | --- | --- |
| `YEELIGHT_IOT_MCP_API_BASE_URL` | `https://api.yeelight.com` | Yeelight API origin |
| `YEELIGHT_IOT_MCP_BIND_HOST` | `127.0.0.1` | Local bind address |
| `YEELIGHT_IOT_MCP_PATH` | `/mcp` | Streamable HTTP path |
| `YEELIGHT_IOT_MCP_HTTP_TIMEOUT` | `15` | Upstream timeout in seconds |
| `YEELIGHT_IOT_MCP_FETCH_NODES_MAX_SIZE` | `300` | Maximum list page size |
| `YEELIGHT_IOT_MCP_NACOS_ENABLED` | `false` | Enable optional service registration |
| `YEELIGHT_IOT_MCP_LOG_DIR` | `./logs/yeelight-online-iot-mcp-server` | Log directory |

## Test

```bash
uv run --no-project --with-editable '.[test]' python -m pytest -q
```

Tests cover authorization normalization, pagination, property normalization,
redacted plans, dry-run defaults, confirmation guards, and configuration
overrides. They do not call the live Yeelight cloud.

## License

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
