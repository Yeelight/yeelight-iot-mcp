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
| Multi-region authorization and request-scoped home selection | [Yeelight Metadata MCP](https://github.com/Yeelight/yeelight-metadata-mcp), optionally configured with [Yeelight AI CLI](https://github.com/Yeelight/yeelight-cli) |
| An existing integration that depends on `control_node` or `execute_scene` | Keep using Yeelight IoT MCP |
| Focused direct control, live state, or scene execution not yet covered by Metadata MCP | Use Metadata MCP as the primary entry and add Yeelight IoT MCP only when needed |

## Yeelight AI Capability Matrix

These projects form a complementary stack. Choose the entry point that matches
how you integrate with Yeelight; they can also be combined.

| Project | Role and capabilities | Best for | GitHub |
| --- | --- | --- | --- |
| Yeelight Home | Recommended local semantic Runtime with one structured `invoke --stdin` boundary for queries, control, scenes, automations, lighting design, diagnostics, product knowledge, and generated apps. | Agent hosts, local automation, and applications that need a stable and policy-aware smart-home execution layer. | [Yeelight/yeelight-home](https://github.com/Yeelight/yeelight-home) |
| Yeelight Smart Home Skills | Official Agent Skills: Smart Home turns natural language into safe Runtime operations; PRO App Builder generates focused local apps from proven Runtime capabilities. | Agent hosts that need conversational smart-home workflows or app generation. | [Yeelight/yeelight-smart-home-skills](https://github.com/Yeelight/yeelight-smart-home-skills) |
| Yeelight AI CLI | Unified terminal workspace and MCP client for Cloud, Metadata, and LAN services, with local profiles, safe shortcuts, diagnostics, scripting, and AI client configuration. | People, scripts, and CI that want one general MCP and automation entry point. | [Yeelight/yeelight-cli](https://github.com/Yeelight/yeelight-cli) |
| Yeelight Metadata MCP | Recommended cloud MCP entry for new integrations, with guarded workflows for homes, rooms, devices, groups, panels, scenes, automations, favorites, maintenance, accounts, multi-region authorization, and request-scoped home selection. | New MCP integrations and AI clients that need broad discovery, inspection, and management workflows. | [Yeelight/yeelight-metadata-mcp](https://github.com/Yeelight/yeelight-metadata-mcp) |
| Yeelight IoT MCP | Focused companion MCP for direct topology and live-state access, device control, and scene execution not yet fully covered by Metadata MCP. | Existing integrations or clients that specifically need `control_node`, `execute_scene`, or focused live control. | [Yeelight/yeelight-iot-mcp](https://github.com/Yeelight/yeelight-iot-mcp) |

Yeelight Home also provides system credential storage, local QR login, secret-redacted diagnostics, preview and validation, caller confirmation and Runtime policy/readback behavior, local memory and recommendation support, operation lessons, and machine-readable intent schema/explanations. Cross-platform binaries are distributed through GitHub Releases, npm, and supported package managers.

Typical paths: smart-home agents and generated apps -> Skills -> Yeelight Home; terminal users and scripts -> Yeelight AI CLI; new MCP integrations -> Metadata MCP; add IoT MCP only for focused direct control or scene execution that Metadata MCP does not yet cover.

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

### Strongly recommended: authorize with Yeelight AI CLI

```bash
npm install --global yeelight-ai
yeelight-ai login --qr
```

Install [Yeelight AI CLI](https://github.com/Yeelight/yeelight-cli) first. In
Yeelight Pro APP, tap Home's top-right `+`, choose **MCP Authorization**, and
scan the terminal QR code exactly as shown in the CLI README's Figure 1. The CLI
sends the saved Profile as MCP headers. Manual token configuration is an
advanced compatibility path; never paste a token into an AI chat, prompt, log,
issue, or repository.

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

The local MCP URL is `http://127.0.0.1:9000/mcp`. Local deployment still uses
the same Yeelight cloud credentials and APIs; it is not an offline gateway.
When no Authorization header is present, local/test loopback deployment can
read the Cloud Profile saved by `yeelight-ai login --qr`. Remote or public
deployments cannot read a user's local file and still require request headers.
Nacos registration is disabled by default in the public project and can be
enabled explicitly through environment variables.

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
