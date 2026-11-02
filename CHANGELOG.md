# Changelog

## [v1.0.2] - 2026-11-02

### 修复

- 修正在 OneBot 适配器下消息已实际送达却仍记录错误日志的问题：等待自身消息回执（waitForSelfEcho）超时未收到回执时会抛出 `ActionFailed`，该异常经 `event.send()` 传播到 `on_message` 的兜底 `except` 分支，导致即便内容已返回，日志仍记录 ERROR 级 traceback，特定情况下还会向聊天再推送一条「命令处理失败」提示。现于回复发送处捕获该异常并仅记为 warning。

## [v1.0.1] - 2026-11-02

### 新增

- 「允许非管理员选择」（`models[].public`）：在可用模型条目上勾选后，管理员白名单外的用户也能用主命令切换该条目；`/mstolist` 对非管理员只显示勾选的条目（未勾选任何条目时显示完整列表）。
- 可视化配置页「模型」标签页为每个条目新增「允许非管理员选择」开关；配置项 schema（`_conf_schema.json`）与 Web API（`web_config.sanitize_models`）同步支持 `public` 字段。

### 变更

- 统一全项目术语：「命令头」改为「命令前缀」、「群模型」改为「会话模型」、配置页与文档中「模型 ID」统一为「提供商 ID」；同步更新 README、配置 schema 提示文案、Web API 描述与命令回复文案。
- 命令回复文案由「当前群模型」改为「当前会话模型」。
- 可视化配置页视觉样式更新：采用 astrbot 原生样式并加宽内容区。

## [v1.0.0] - 2026-11-01

### 新增

- `/msto <别名或模型ID>` 为当前会话切换首选模型，别名优先匹配，不区分大小写。
- `/msto` 无参数时清除当前会话的独立模型配置，回退 AstrBot 默认模型。
- `/mstolist` 查看可用模型列表，输出方式支持仅别名、仅 ID 或别名 + ID。
- `/mstom` 查看当前会话正在使用的模型，输出方式支持跟随设置时、仅别名、仅 ID 或别名 + ID。
- `/mstosid` 输出本会话 UMO（会话 ID）与 UID（发送者 ID），用于获取管理员白名单所需的 UID。
- 管理员白名单（UID，`allowed_uids`），仅白名单内用户可使用 `/msto` 主命令。
- 可视化配置页面（Vue 3），支持命令设置、管理员设置、可用模型设置与会话模型管理。
- 声明式配置与可视化配置双入口，数据同源。
- 命令头与命令名完全可自定义，各子命令可独立开关。
- `enable_main_command` 配置项，关闭后主命令不响应，仅可通过配置页管理会话模型。
- Web API 读写配置、查询模型列表、管理会话模型偏好。

[v1.0.2]: https://github.com/XKPU/astrbot_plugin_group_model_selection/compare/v1.0.1...v1.0.2
[v1.0.1]: https://github.com/XKPU/astrbot_plugin_group_model_selection/compare/v1.0.0...v1.0.1
[v1.0.0]: https://github.com/XKPU/astrbot_plugin_group_model_selection/compare/cbf9c01c7a8fa547e5a44ac470a47b9d43ebb408...v1.0.0