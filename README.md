# Yeelight IoT MCP

[简体中文](README.zh-CN.md)

## Official Repository And Mirrors

[GitHub](https://github.com/Yeelight/yeelight-iot-mcp) is the canonical source
for issues, contributions, CI, and releases. Read-only mirrors are available on
[Gitee](https://gitee.com/yeelight/yeelight-iot-mcp) and
[GitCode](https://gitcode.com/Yeelight/yeelight-iot-mcp) for users who cannot
reach GitHub reliably, with
[GitLab.com](https://gitlab.com/Yeelight/yeelight-iot-mcp) as an additional
global fallback. Clone from any reachable source, but report issues and
contribute changes on GitHub.

> [!IMPORTANT]
> **New to Yeelight MCP? Start with [Yeelight Metadata MCP](https://github.com/Yeelight/yeelight-metadata-mcp), not this repository.**
>
> Metadata MCP is the recommended primary cloud MCP for new integrations. Use
> IoT MCP only when you specifically need its focused direct device control,
> current live state, or scene execution capabilities, or add it as a companion
> to Metadata MCP for those cases.

## Yeelight Cloud MCP Suite

This repository is the focused-control part of the official Yeelight cloud MCP
suite. The suite is designed to be used as one capability group with
[Yeelight Metadata MCP](https://github.com/Yeelight/yeelight-metadata-mcp) as
the primary entry:

| Server | Role in the suite | Core capabilities |
| --- | --- | --- |
| **[Metadata MCP](https://github.com/Yeelight/yeelight-metadata-mcp) (primary)** | Default entry point and coordination layer for new integrations. | Broad discovery and guarded management workflows, multi-region authorization, and request-scoped home selection. |
| [IoT MCP](https://github.com/Yeelight/yeelight-iot-mcp) (companion) | Focused direct-control extension for the primary Metadata MCP integration. | Direct topology and live-state access, `control_node`, and `execute_scene`. |

**Recommended composition:** configure Metadata MCP first, then add IoT MCP to
the same AI client only when its focused tools are required.

### Which MCP should I use?

| What you need | Recommended entry point |
| --- | --- |
| First Yeelight MCP integration | [Yeelight Metadata MCP](https://github.com/Yeelight/yeelight-metadata-mcp) |
| Homes, rooms, devices, groups, panels, scenes, automations, favorites, maintenance, or account workflows | [Yeelight Metadata MCP](https://github.com/Yeelight/yeelight-metadata-mcp) |
| Multi-region authorization and request-scoped home selection | [Yeelight Metadata MCP](https://github.com/Yeelight/yeelight-metadata-mcp), optionally configured with [Yeelight Home](https://github.com/Yeelight/yeelight-home) |
| An existing integration that depends on `control_node` or `execute_scene` | Keep using Yeelight IoT MCP |
| Focused direct control, live state, or scene execution not yet covered by Metadata MCP | Use Metadata MCP as the primary entry and add Yeelight IoT MCP only when needed |

## Place In Yeelight AI

`yeelight-home` is the only installation, QR sign-in, and client-configuration entry. Ordinary users should prefer the complete `yeelight-smart-home` Skill, while new lightweight MCP integrations start with Metadata MCP. This service is a focused companion for existing `control_node`, `execute_scene`, and specific live-control compatibility needs.

In plain language: do not add this server just because it exists. Add it only
after Metadata MCP when your AI genuinely needs one of the focused live-control
tools listed below. It is not a dependency of Yeelight Home or either Skill.

## Existing and specialized IoT MCP integrations

Yeelight IoT MCP is the official focused Model Context Protocol server for
Yeelight Pro homes. It lets MCP clients discover homes, areas, rooms, devices,
groups, and scenes, read current capabilities, prepare safe device controls,
and execute confirmed controls or scenes. The following documentation remains
the supported reference for existing and specialized integrations.

For the suite overview and recommended default setup, return to
[Yeelight Metadata MCP](https://github.com/Yeelight/yeelight-metadata-mcp).

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
- A Yeelight Authorization token. Region and House ID are optional.

### Recommended: let Yeelight Home complete sign-in and configuration

```bash
npm install --global yeelight-home
yeelight-home setup --lang en-US --mode mcp --agent cursor --mcp-source cloud --yes
```

The command displays a QR code. In Yeelight Pro app Home, tap the top-right `+`, choose **MCP Authorization**, and scan it. One Pro home is selected automatically; multiple homes are presented by name. Cloud mode configures Metadata and IoT MCP together through local credential proxies, without copying Authorization into the AI client's configuration. Manual token configuration remains an advanced compatibility path.

## Hosted Service

Use the official Streamable HTTP endpoint:

```text
https://api.yeelight.com/apis/mcp_server/v1/mcp
```

Required request header:

```text
Authorization: <YOUR_AUTHORIZATION>
```

Optional headers are `Yeelight-Region` and `House-Id`. The server accepts a raw
token or a value prefixed with `Bearer`. When Region is omitted, a JWT Region
claim selects the official endpoint before the complete token is validated.
When House ID is omitted, the server selects the first Pro home in that Region.
Users never configure a Client ID; IoT upstream calls derive it from the
validated JWT when required, falling back to `dev` in the development Region
and `iot-app` in `cn`, `sg`, `us`, or `eu`.

## Local Development

```bash
git clone https://github.com/Yeelight/yeelight-iot-mcp.git
cd yeelight-iot-mcp

uv sync --extra test
YEELIGHT_IOT_MCP_RUNTIME_ENV=local \
YEELIGHT_IOT_MCP_NACOS_ENABLED=false \
PYTHONPATH=src \
uv run uvicorn main:streamable_http_app --host 127.0.0.1 --port 9000
```

The local MCP URL is `http://127.0.0.1:9000/mcp`. Local deployment still uses Yeelight cloud APIs; it is not an offline gateway. Every request must provide an explicit Authorization header regardless of bind address or runtime environment. The service never reads an operator's CLI Profile; tests may use an explicit isolated credential provider. Nacos registration is disabled by default in the public project and can be enabled explicitly through environment variables.

## MCP Client Configuration

```json
{
  "mcpServers": {
    "yeelight-iot": {
      "url": "https://api.yeelight.com/apis/mcp_server/v1/mcp",
      "headers": {
        "Authorization": "<YOUR_AUTHORIZATION>"
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
| `YEELIGHT_IOT_MCP_DEFAULT_REGION` | `cn` | Fallback Region for opaque tokens |
| `YEELIGHT_IOT_MCP_BIND_HOST` | `127.0.0.1` in local/test | Bind address; production defaults to `0.0.0.0` |
| `YEELIGHT_IOT_MCP_PATH` | `/mcp` | Streamable HTTP path |
| `YEELIGHT_IOT_MCP_HTTP_TIMEOUT` | `15` | Upstream timeout in seconds |
| `YEELIGHT_IOT_MCP_FETCH_NODES_MAX_SIZE` | `300` | Maximum list page size |
| `YEELIGHT_IOT_MCP_NACOS_ENABLED` | `false` | Enable optional service registration |
| `YEELIGHT_IOT_MCP_LOG_DIR` | `./logs/yeelight-online-iot-mcp-server` | Log directory |

## Test

```bash
uv run --extra test pytest -q
```

Tests cover JWT claim handling, multi-Region routing, local Profile isolation,
Pro home fallback, authorization normalization, pagination, redacted plans,
dry-run defaults, confirmation guards, and configuration overrides. They do not
call the live Yeelight cloud.

## License

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
