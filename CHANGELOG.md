# Changelog

## [v1.0.0] - 2026-11-01

### Added

- `/msto <别名或模型ID>` 为当前会话切换首选模型，别名优先匹配，不区分大小写。
- `/msto` 无参数时清除当前会话的独立模型配置，回退 AstrBot 默认模型。
- `/mstolist` 查看可用模型列表，输出方式支持仅别名、仅 ID 或别名 + ID。
- `/mstom` 查看当前会话正在使用的模型，输出方式支持跟随设置时、仅别名、仅 ID 或别名 + ID。
- `/mstosid` 输出本会话 UMO 与 UID，用于获取白名单所需的使用者 UID。
- 管理员 UID 白名单（`allowed_uids`），仅白名单内用户可使用 `/msto` 主命令。
- 可视化配置页面（Vue 3），支持命令设置、管理员设置、可用模型设置与会话模型管理。
- 声明式配置与可视化配置双入口，数据同源。
- 命令头与命令名完全可自定义，各子命令可独立开关。
- `enable_main_command` 配置项，关闭后主命令不响应，仅可通过配置页管理会话模型。
- Web API 读写配置、查询模型列表、管理会话模型偏好。

[v1.0.0]: https://github.com/XKPU/astrbot_plugin_openai_image/compare/cbf9c01c7a8fa547e5a44ac470a47b9d43ebb408...v1.0.0