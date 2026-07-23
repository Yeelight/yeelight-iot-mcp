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
> **New to Yeelight MCP? Use one Yeelight MCP setup instead of installing this repository separately.**
>
> The setup configures this live-state/control service and
> [Yeelight Metadata MCP](https://github.com/Yeelight/yeelight-metadata-mcp)
> together. This repository remains the developer reference for its specialized
> server, endpoint, and tools.
>
> Follow the [official English Yeelight MCP tutorial](https://ai-tutorials.yeelight.com/en/guides/yeelight-mcp/) for the complete beginner path, or open the [Simplified Chinese tutorial](https://ai-tutorials.yeelight.com/zh/guides/yeelight-mcp/).

## Yeelight Cloud MCP Suite

This repository is the focused-control part of the official Yeelight cloud MCP
suite. Ordinary users receive both independently deployed services as one
capability group through the same setup:

| Server | Role in the suite | Core capabilities |
| --- | --- | --- |
| **[Metadata MCP](https://github.com/Yeelight/yeelight-metadata-mcp)** | Home understanding and guarded management. | Broad discovery and guarded management workflows, multi-region authorization, and request-scoped home selection. |
| [IoT MCP](https://github.com/Yeelight/yeelight-iot-mcp) | Live state and focused control. | Direct topology and live-state access, `control_node`, and `execute_scene`. |

**Recommended composition:** run one Yeelight MCP setup so both services are
available without a second install or scan.

### Which MCP should I use?

| What you need | Recommended entry point |
| --- | --- |
| First Yeelight MCP integration | Configure the complete Yeelight MCP suite with `yeelight-home setup --mode mcp --mcp-source cloud` |
| Homes, rooms, devices, groups, panels, scenes, automations, favorites, maintenance, or account workflows | [Yeelight Metadata MCP](https://github.com/Yeelight/yeelight-metadata-mcp) |
| Multi-region authorization and request-scoped home selection | [Yeelight Metadata MCP](https://github.com/Yeelight/yeelight-metadata-mcp), optionally configured with [Yeelight Home](https://github.com/Yeelight/yeelight-home) |
| An existing integration that depends on `control_node` or `execute_scene` | Keep using Yeelight IoT MCP |
| Develop or troubleshoot focused direct control, live state, or scene execution | Use this repository's server and tool documentation |

## Place In Yeelight AI

`yeelight-home` provides the recommended installation, QR sign-in, and client-configuration flow. Ordinary users should prefer the complete `yeelight-smart-home` Skill; MCP-only clients run one cloud setup for the complete Yeelight MCP suite. The cloud services then execute independently of the local Runtime.

In plain language: ordinary users do not install this server separately. It is
included by the unified setup and remains independently addressable for existing
or specialized integrations. It is not a dependency of Yeelight Home or either Skill.

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
