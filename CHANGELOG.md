# Changelog

## [v1.0.6] - 2026-11-08

### 信息

- 当前版本仅提升版本号，若已安装 v1.0.5 则无需更新

## [v1.0.5] - 2026-11-08

### 修复

- 可视化配置页「会话模型」标签修改首选模型后保存按钮不出现：该输入框此前未接入脏状态跟踪；且会话行原本是标签页本地状态，全局「保存配置」不会应用它们。现在所有会话修改（新建 / 删除条目、修改首选模型、恢复默认）统一接入侧栏「保存配置」流——修改后出现保存按钮，点击保存时逐行应用变更的会话，提示中显示应用条数；「重新加载 / 取消编辑」同步刷新会话列表。
- 可视化配置页「会话模型」标签删除条目后保存无效：删除的行不参与全局保存流，存储中的会话偏好未被清除，重新加载后又出现。现在保存时会对比上次保存快照，对被删除的条目自动清除其会话模型设置；「取消编辑 / 重新加载」恢复基线语义同步修正。

### 新增

- 可视化配置页三个标签页的交互增强：
  - 「可用模型设置」支持通过条目上的 ↑ / ↓ 按钮调整顺序（调整后点侧栏「保存配置」生效）。
  - 「管理员白名单」新增「选择用户」对话框，可从 AstrBot 已知的发送者中搜索并勾选 UID，仍保留手动输入。
  - 「会话模型」新增「选择」对话框，可从 AstrBot 已知的会话中挑选 UMO 自动填入，仍保留手动输入。
- 配置页新增两个数据端点：`/umos`（已知会话枚举）与 `/senders`（发送者搜索 / 按 ID 回查），数据源自 AstrBot 会话与别名表。

### 变更

- `main.py` 拆分为薄入口（127 行）：Web API 处理器迁至 `src/web_apis.py`（`WebApiMixin`），聊天命令处理器迁至 `src/chat_commands.py`（`CommandMixin`）；带装饰器的消息入口 `on_message` 保留在主模块以满足 AstrBot 的 handler 注册机制。

## [v1.0.4] - 2026-11-06

### 修复

- 模型快照存储位置迁移至标准插件数据目录 `data/plugin_data/`。

## [v1.0.3] - 2026-11-05

### 新增

- 可用模型条目自动分配 UUID（`models[].uuid`），旧版配置首次加载时自动补齐，作为条目身份标识。
- 模型条目变更后自动同步会话：移除某条目时，使用该模型的会话自动恢复默认模型；修改别名时会话绑定的输入记录同步更新；修改提供商 ID 时会话自动迁移到新模型（迁移失败则恢复默认）。声明式配置页保存与手动编辑配置文件后重载插件均会触发。
- 可视化配置页保存后提示同步的会话数量。

### 变更

- 插件日志去掉正文中手写的插件名前缀，统一由 AstrBot 标准日志机制自动附加 `[插件名]` 标签。

### 修复

- 可视化配置页「重新加载」现在重新读取磁盘配置文件（此前返回内存副本）。

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

[v1.0.6]: https://github.com/XKPU/astrbot_plugin_group_model_selection/compare/v1.0.5...v1.0.6
[v1.0.5]: https://github.com/XKPU/astrbot_plugin_group_model_selection/compare/v1.0.4...v1.0.5
[v1.0.4]: https://github.com/XKPU/astrbot_plugin_group_model_selection/compare/v1.0.3...v1.0.4
[v1.0.3]: https://github.com/XKPU/astrbot_plugin_group_model_selection/compare/v1.0.2...v1.0.3
[v1.0.2]: https://github.com/XKPU/astrbot_plugin_group_model_selection/compare/v1.0.1...v1.0.2
[v1.0.1]: https://github.com/XKPU/astrbot_plugin_group_model_selection/compare/v1.0.0...v1.0.1
[v1.0.0]: https://github.com/XKPU/astrbot_plugin_group_model_selection/compare/cbf9c01c7a8fa547e5a44ac470a47b9d43ebb408...v1.0.0
