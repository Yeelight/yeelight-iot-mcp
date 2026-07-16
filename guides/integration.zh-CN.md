# 集成指南

[English](integration.md) | [README](../README.zh-CN.md) | [使用指南](usage.zh-CN.md)

仓库入口：[GitHub](https://github.com/Yeelight/yeelight-iot-mcp) 是规范源；无法
访问 GitHub 时可使用只读的 [Gitee](https://gitee.com/yeelight/yeelight-iot-mcp)
或 [GitCode](https://gitcode.com/Yeelight/yeelight-iot-mcp) 国内镜像，
[GitLab.com](https://gitlab.com/Yeelight/yeelight-iot-mcp) 是全球备用源。

本文说明如何把 MCP 客户端连接到官方托管或本地运行的 Yeelight IoT MCP。
`tools/list` 返回的 schema 是当前接口契约。

## 选择服务

| 工作负载 | 服务 |
| --- | --- |
| 实时设备发现、状态、控制和情景执行 | Yeelight IoT MCP |
| 家庭、房间、设备、设备组、面板、情景或自动化管理 | [Yeelight Metadata MCP](https://github.com/Yeelight/yeelight-metadata-mcp) |
| 网关本地发现和控制 | 本地网关暴露的 MCP 服务 |

IoT MCP 与 Metadata MCP 可以同时配置。二者使用相同的云端上下文 Header，
但工具能力不同。

## 强烈推荐扫码授权

```bash
npm install --global yeelight-ai
yeelight-ai login --qr
```

请先安装 [Yeelight AI CLI](https://github.com/Yeelight/yeelight-cli)，然后在 Yeelight
Pro APP 首页点击右上角 `+` -> **MCP 授权**，按照 CLI README 的图 1 扫描终端
二维码。手动 Token 配置仅作为高级兼容路径。

## 官方 Streamable HTTP

服务地址：

```text
https://api.yeelight.com/apis/mcp_server/v1/mcp
```

请通过客户端密钥存储提供 Authorization：

```text
Authorization: <YOUR_AUTHORIZATION>
```

`Yeelight-Region` 和 `House-Id` 可选。Region 可从 JWT 获取，House ID 缺失时选择首个
Pro 家庭。用户永远不需要填写 Client ID。IoT 上游调用优先使用验证后 JWT 的 claim；
缺失时开发 Region 使用 `dev`，公开 Region 使用 `iot-app`。

## Cursor 等客户端

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

修改配置后重启客户端，先列出工具，再调用 `get_currnet_house_info` 等只读工具
确认连接。

## Claude Desktop 与 `mcp-remote`

```json
{
  "mcpServers": {
    "yeelight-iot": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://api.yeelight.com/apis/mcp_server/v1/mcp",
        "--header", "Authorization:${AUTHORIZATION}",
        "--header", "House-Id:${HOUSE_ID}"
      ],
      "env": {
        "AUTHORIZATION": "<YOUR_AUTHORIZATION>",
        "HOUSE_ID": "<YOUR_HOUSE_ID>"
      }
    }
  }
}
```

如果客户端调整了传输或 Header 语法，以当前 `mcp-remote` 文档为准。

## 本地源码服务

```bash
uv sync --extra test

YEELIGHT_IOT_MCP_RUNTIME_ENV=local \
YEELIGHT_IOT_MCP_NACOS_ENABLED=false \
PYTHONPATH=src \
uv run uvicorn main:streamable_http_app --host 127.0.0.1 --port 9000
```

客户端 URL 配置为 `http://127.0.0.1:9000/mcp`。请求没有 Header 时，这个
local/test + loopback 服务可读取 `yeelight-ai login --qr` 保存的 Cloud Profile；
远程客户端仍通过 Header 发送 Authorization。

不要在缺少可信反向代理、网络策略、TLS 和密钥保护时监听公网地址。内置中间件
会校验 Authorization，但不是完整的公网边缘安全层。

## 集成流程

1. 连接并初始化 MCP 会话。
2. 调用 `tools/list` 读取当前 schema。
3. 用只读工具解析家庭和目标实体。
4. 需要完整列表时持续跟随 `nextCursor`，直到其为空。
5. 检查目标的属性定义和支持的 operator。
6. 使用写工具的默认 dry-run 行为生成计划。
7. 审查脱敏计划并取得用户确认。
8. 只在确认后重新发送一次，并设置 `dryRun=false`、`confirmSideEffect=true`。
9. 执行后尽可能查询当前状态。

## 故障排查

- `401`：检查 Authorization，过期时重新申请 token。
- 拓扑为空或家庭错误：检查 JWT Region，可选配置 `House-Id`，然后刷新列表工具；
  省略 House ID 时会选择首个 Pro 家庭。
- 缺少目标：先把名称解析为当前数字 node ID。
- 参数校验失败：刷新 `tools/list`，不要猜字段。
- 超时：检查地址、代理、DNS 和 `YEELIGHT_IOT_MCP_HTTP_TIMEOUT`。
- 本地 Nacos 错误：除非明确配置服务注册，否则设置
  `YEELIGHT_IOT_MCP_NACOS_ENABLED=false`。

排查客户端配置时不要打印凭据。
