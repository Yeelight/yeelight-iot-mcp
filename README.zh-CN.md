# Yeelight IoT MCP

[English](README.md)

Yeelight IoT MCP 是面向 Yeelight Pro 家庭的官方 Model Context Protocol
服务。MCP 客户端可以通过它发现家庭、区域、房间、设备、设备组和情景，读取
当前能力，生成安全的控制预览，并执行经过确认的设备控制或情景。

## Yeelight AI 能力矩阵

这些项目组成互补的 Yeelight AI 技术栈。可以根据接入方式选择入口，也可以组合使用。

| 项目 | 定位与核心能力 | 适用场景 | GitHub |
| --- | --- | --- | --- |
| Yeelight Home | 首选本地语义 Runtime，通过统一结构化 `invoke --stdin` 边界提供查询、控制、场景、自动化、灯光设计、诊断、产品知识和生成应用能力。 | 需要稳定、受策略保护的智能家居执行层的 Agent host、本地自动化和应用。 | [Yeelight/yeelight-home](https://github.com/Yeelight/yeelight-home) |
| Yeelight Smart Home Skills | 官方 Agent Skills：Smart Home 把自然语言转换为安全的 Runtime 操作；PRO App Builder 基于已验证能力生成专用本地应用。 | 需要智能家居对话工作流或应用生成能力的 Agent host。 | [Yeelight/yeelight-smart-home-skills](https://github.com/Yeelight/yeelight-smart-home-skills) |
| Yeelight AI CLI | 统一终端工作台和 MCP 客户端，连接 Cloud、Metadata 和 LAN 服务，提供本地 profile、安全快捷命令、诊断、脚本和 AI 客户端配置。 | 希望通过通用 MCP 与自动化命令行入口操作的用户、脚本和 CI。 | [Yeelight/yeelight-cli](https://github.com/Yeelight/yeelight-cli) |
| Yeelight IoT MCP | 官方托管或可自行部署的 Streamable HTTP MCP 服务，提供拓扑、实时状态、设备控制和场景执行。 | 需要直接发现和控制 IoT 设备的 MCP 客户端。 | [Yeelight/yeelight-iot-mcp](https://github.com/Yeelight/yeelight-iot-mcp) |
| Yeelight Metadata MCP | 官方托管或可自行部署的 Streamable HTTP MCP 服务，提供受保护的家庭、房间、组、面板、场景、自动化、收藏和账号元数据工作流。 | 需要检查和管理元数据的 MCP 客户端。 | [Yeelight/yeelight-metadata-mcp](https://github.com/Yeelight/yeelight-metadata-mcp) |

Yeelight Home 还提供系统凭据存储、本地 QR 登录、秘密脱敏诊断、预览与校验、调用方确认和 Runtime 策略/写后读取、本地记忆与推荐、实操经验，以及机器可读的 intent schema 和解释。跨平台二进制通过 GitHub Release、npm 和已支持的包管理器分发。

典型组合：智能家居 Agent 和生成应用 -> Skills -> Yeelight Home；终端用户和脚本 -> Yeelight AI CLI；MCP 客户端 -> IoT MCP 和/或 Metadata MCP。

## 主要能力

- Streamable HTTP MCP 传输。
- 支持官方托管服务和本地源码部署。
- 提供拓扑发现、设备控制和情景执行等 8 个工具。
- 区域、房间、设备、设备组和情景列表支持游标分页。
- 设备控制和情景执行默认 dry-run。
- 控制计划会脱敏，真实副作用必须显式确认。

## 环境要求

- 本地部署需要 Python 3.10 或更高版本。
- 推荐使用 `uv` 管理本地环境。
- 需要 Yeelight Authorization、Client ID 和 House ID。

凭据申请方式请参考 [Yeelight 开放平台文档](https://open-console.yeelight.com/commerical-lighting-open-platform-docs.html)。
请把凭据保存在 MCP 客户端的密钥存储中，不要提交到仓库，也不要写入日志、
提示词或 Issue。

## 官方托管服务

Streamable HTTP 地址：

```text
https://api.yeelight.com/apis/mcp_server/v1/mcp
```

请求 Header：

```text
Authorization: <YOUR_AUTHORIZATION>
Client-Id: <YOUR_CLIENT_ID>
House-Id: <YOUR_HOUSE_ID>
```

服务端接受原始 token 或带 `Bearer` 前缀的值，并会在转发前统一规范化。

## 本地开发

```bash
git clone https://github.com/Yeelight/yeelight-iot-mcp.git
cd yeelight-iot-mcp

uv sync --extra test
YEELIGHT_IOT_MCP_NACOS_ENABLED=false \
PYTHONPATH=src \
uv run uvicorn main:streamable_http_app --host 127.0.0.1 --port 9000
```

本地 MCP 地址是 `http://127.0.0.1:9000/mcp`。本地部署仍会使用同一套
Yeelight 云端凭据和 API，并不是离线网关。公共项目默认关闭 Nacos 注册，只有
显式配置环境变量后才会启用。

## MCP 客户端配置

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

修改配置后重启 MCP 客户端，并确认 `tools/list` 能返回 Yeelight 工具。

## 工具

| 工具 | 用途 | 副作用 |
| --- | --- | --- |
| `get_currnet_house_info` | 读取当前家庭；拼写保留用于向前兼容 | 只读 |
| `get_areas` | 游标分页列出区域 | 只读 |
| `get_rooms` | 游标分页列出房间 | 只读 |
| `get_devices` | 列出全部设备或按房间筛选 | 只读 |
| `get_groups` | 列出全部设备组或按房间筛选 | 只读 |
| `get_scenes` | 游标分页列出情景 | 只读 |
| `control_node` | 预览或执行节点属性控制 | 默认 dry-run |
| `execute_scene` | 预览或执行情景 | 默认 dry-run |

请求示例和运行规则见[使用指南](guides/usage.zh-CN.md)，客户端与部署配置见
[集成指南](guides/integration.zh-CN.md)。

## 安全模型

`control_node` 和 `execute_scene` 默认 `dryRun=true`。真实执行必须同时设置
`dryRun=false` 和 `confirmSideEffect=true`。调用方应当：

1. 先用只读工具把名称解析为当前真实 ID。
2. 检查目标支持的属性和 operator。
3. 生成并审查 dry-run 计划。
4. 在调用应用中取得用户确认。
5. 只执行一次，并在可能时查询结果状态。

当前安全策略会阻止控制属性 `rs`。写入或情景执行失败后不要盲目重试。

## 配置

本地部署常用环境变量：

| 变量 | 默认值 | 用途 |
| --- | --- | --- |
| `YEELIGHT_IOT_MCP_API_BASE_URL` | `https://api.yeelight.com` | Yeelight API 地址 |
| `YEELIGHT_IOT_MCP_BIND_HOST` | `127.0.0.1` | 本地监听地址 |
| `YEELIGHT_IOT_MCP_PATH` | `/mcp` | Streamable HTTP 路径 |
| `YEELIGHT_IOT_MCP_HTTP_TIMEOUT` | `15` | 上游超时秒数 |
| `YEELIGHT_IOT_MCP_FETCH_NODES_MAX_SIZE` | `300` | 列表最大分页数量 |
| `YEELIGHT_IOT_MCP_NACOS_ENABLED` | `false` | 启用可选服务注册 |
| `YEELIGHT_IOT_MCP_LOG_DIR` | `./logs/yeelight-online-iot-mcp-server` | 日志目录 |

## 测试

```bash
uv run --no-project --with-editable '.[test]' python -m pytest -q
```

测试覆盖 Authorization 规范化、分页、属性值规范化、计划脱敏、dry-run 默认值、
确认门禁和配置覆盖，不会调用真实 Yeelight 云服务。

## 许可证

Apache License 2.0，参见 [LICENSE](LICENSE) 和 [NOTICE](NOTICE)。
