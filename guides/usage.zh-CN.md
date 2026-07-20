# 使用指南

[English](usage.md) | [README](../README.zh-CN.md) | [集成指南](integration.zh-CN.md)

仓库入口：[GitHub](https://github.com/Yeelight/yeelight-iot-mcp) 是规范源；无法
访问 GitHub 时可使用只读的 [Gitee](https://gitee.com/yeelight/yeelight-iot-mcp)
或 [GitCode](https://gitcode.com/Yeelight/yeelight-iot-mcp) 国内镜像，
[GitLab.com](https://gitlab.com/Yeelight/yeelight-iot-mcp) 是全球备用源。

认证时强烈建议先安装 [Yeelight Home](https://github.com/Yeelight/yeelight-home)，运行
`yeelight-home auth login --qr`，然后在 Yeelight Pro APP 首页点击右上角 `+` ->
**MCP 授权** 扫描终端二维码。手动 Token 配置仅作为高级兼容方式。

不同 MCP 客户端的工具调用 envelope 可能不同。下面的 JSON 是对应工具的
arguments 对象。

## 读取当前家庭

调用 `get_currnet_house_info`，无需参数：

```json
{}
```

历史拼写 `currnet` 已成为公开工具名，为向前兼容会继续保留。

## 列出拓扑

调用 `get_areas`、`get_rooms` 或 `get_scenes`：

```json
{
  "limit": 100
}
```

返回 `nextCursor` 时，把它传给下一次调用：

```json
{
  "cursor": "2",
  "limit": 100
}
```

调用 `get_devices` 或 `get_groups` 时，不传 `roomId` 表示整个家庭，也可以按
房间筛选：

```json
{
  "roomId": "<ROOM_ID>",
  "limit": 100
}
```

控制前必须先把名称解析为当前 ID，不要沿用其它家庭或旧缓存中的 ID。

## 预览设备控制

调用 `control_node`。默认 `dryRun=true`，只返回脱敏计划，不调用真实控制 API：

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
    "reason": "把选中的灯调整到 60% 亮度"
  }
}
```

节点类型是 `1=房间`、`2=设备`、`3=区域`、`4=设备组`、`5=家庭`。常见属性
包括：`p` 开关、`l` 亮度、`c` 十进制 RGB 颜色、`ct` 色温、`tp` 窗帘目标
开合度。实际调用必须以目标返回的属性 schema 和 operator 为准。

## 执行已确认的设备控制

审查计划并取得确认后，重新发送同一请求并修改两个门禁字段：

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
    "reason": "用户已确认打开选中的灯"
  }
}
```

成功执行返回 `code=EXECUTED`。缺少确认会返回
`CONFIRM_SIDE_EFFECT_REQUIRED`。当前策略会阻止属性 `rs`。

## 预览与执行情景

以 dry-run 调用 `execute_scene`：

```json
{
  "request": {
    "sceneId": "<SCENE_ID>",
    "reason": "预览选中的情景"
  }
}
```

确认后执行：

```json
{
  "request": {
    "sceneId": "<SCENE_ID>",
    "dryRun": false,
    "confirmSideEffect": true,
    "reason": "用户已确认执行选中的情景"
  }
}
```

## 运行规则

- Authorization 和 House ID 属于传输上下文，不要放进工具参数或日志；用户不需要
  配置 Client ID。
- 需要完整拓扑时必须跟随分页。
- 使用服务端返回的 ID、属性类型、范围、枚举值和 operator。
- 所有写入和情景执行都先预览。
- 真实执行前由调用方取得用户确认。
- API 支持时执行后回读状态。
- 副作用调用失败后不要盲目重试。
