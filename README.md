# astrbot_plugin_group_model_selection

[![GitHub release](https://img.shields.io/github/v/release/XKPU/astrbot_plugin_group_model_selection?logo=github)](https://github.com/XKPU/astrbot_plugin_group_model_selection)
[![License](https://img.shields.io/badge/license-AGPL--3.0-green?logo=data:image/svg+xml;base64,PHN2ZyB0PSIxNzg2ODczMTA1MjgwIiBjbGFzcz0iaWNvbiIgdmlld0JveD0iMCAwIDEwMjQgMTAyNCIgdmVyc2lvbj0iMS4xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHAtaWQ9IjY2MzEiIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIj48cGF0aCBkPSJNNTEyIDE2QzIzOC4wNjYgMTYgMTYgMjM4LjA2NiAxNiA1MTJzMjIyLjA2NiA0OTYgNDk2IDQ5NiA0OTYtMjIyLjA2NiA0OTYtNDk2Uzc4NS45MzQgMTYgNTEyIDE2eiBtMCA4OTZjLTIyMS4wNjQgMC00MDAtMTc4LjkwMi00MDAtNDAwIDAtMjIxLjA2MiAxNzguOTAyLTQwMCA0MDAtNDAwIDIyMS4wNjQgMCA0MDAgMTc4LjkwMiA0MDAgNDAwIDAgMjIxLjA2NC0xNzguOTAyIDQwMC00MDAgNDAweiBtMjE0LjcwMi0yMDIuMTI4Yy0xOS4yMjggMTkuNDI0LTkxLjA2IDgyLjc5Mi0yMDguMTMgODIuNzkyLTE2NC44NiAwLTI4MC45NjgtMTIyLjg1LTI4MC45NjgtMjgzLjEzNCAwLTE1OC4zMDQgMTIwLjU1LTI3OC44MDIgMjc5LjUyNC0yNzguODAyIDExMS4wNjIgMCAxNzcuNDc2IDUzLjI0IDE5NS4xODYgNjkuNTU4YTIzLjkzIDIzLjkzIDAgMCAxIDMuODcyIDMwLjY0NGwtMzYuMzEgNTYuMjI2Yy03LjY4MiAxMS45LTIzLjkzMiAxNC41NjQtMzQuOTk4IDUuODQyLTE3LjE5LTEzLjU1Mi02My42MjgtNDUuMDc2LTEyMy40MTYtNDUuMDc2LTk2LjYwNiAwLTE1NS44MzIgNzAuNjYtMTU1LjgzMiAxNjAuMTY0IDAgODMuMTc4IDUzLjc3NiAxNjcuMzg0IDE1Ni41NTQgMTY3LjM4NCA2NS4zMTQgMCAxMDMuNjg2LTM4LjA3OCAxMzEuNDUyLTU0LjQ1IDEwLjU0LTkuNzE0IDI3LjE5Mi04LjA3OCAzNS42NCAzLjQ3NmwzOS43MyA1NC4zNGEyMy44OTQgMjMuODk0IDAgMCAxLTIuMzA0IDMxLjAzNnoiIGZpbGw9IiNmZmZmZmYiIHAtaWQ9IjY2MzIiPjwvcGF0aD48L3N2Zz4=)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-AstrBot-purple?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48cGF0aCBkPSJNMzUgMjBRMzcgNDIgNjUgNTJRMzcgNjIgMzUgODRRMzMgNjIgNSA1MlEzMyA0MiAzNSAyMFoiIGZpbGw9IiM0Mjc4YjgiLz48cGF0aCBkPSJNNzUgMTJRNzYgMjMgODggMjdRNzYgMzEgNzUgNDJRNzQgMzEgNjIgMjdRNzQgMjMgNzUgMTJaIiBmaWxsPSIjNDI3OGI4Ii8+PC9zdmc+)](https://github.com/AstrBotDevs/AstrBot)
[![Author](https://custom-icon-badges.demolab.com/badge/author-K__PU-orange?logo=k_pu)](https://github.com/XKPU)

设置首选模型，支持别名、管理员白名单（UID）、模型列表与当前模型查询命令，并提供独立的可视化配置页面（含会话模型管理）。

> [!WARNING]
> 插件依赖于平台返回的 UID（发送者 ID）做白名单判断，某些平台的 UID（发送者 ID）可能被伪造或无法判断单一用户，在此类平台上请关闭主命令（enable_main_command），采用可视化配置页面管理。

## 目录

- [功能](#功能)
- [快速开始](#快速开始)
- [聊天命令](#聊天命令)
- [配置项](#配置项)
- [权限说明](#权限说明)
- [可视化配置](#可视化配置)
- [代码结构](#代码结构)
- [实现说明](#实现说明)
- [许可证](#许可证)

## 功能

| 功能 | 说明 |
| --- | --- |
| `/msto <别名或模型ID>` | 将当前会话的首选模型切换为指定模型，会话未设置时使用 AstrBot 自身配置的首选模型 |
| `/msto`（无参数） | 清除当前会话的独立模型配置，回退 AstrBot 默认模型 |
| `/mstolist` | 查看当前配置的可用模型列表（可选开启） |
| `/mstom` | 查看当前会话模型（可选启用） |
| `/mstosid` | 输出本会话 UMO（会话 ID）与 UID（发送者 ID）等信息（可选启用，不受管理员白名单限制） |

可视化配置页面（插件详情 → 配置页）与声明式配置页面（插件配置）双入口，数据同源。配置页「会话模型」标签可直接为任意会话查看 / 设置 / 清除首选模型，行为与 `/msto` 完全等价。

## 快速开始

1. 将本目录放入 AstrBot 的 `data/plugins/` 下并重载插件。
2. 打开插件的可视化配置页：
   - **命令设置**：自定义命令前缀（默认 `/`）与各命令名（默认 `msto` / `mstosid` / `mstolist` / `mstom`），按需启用会话查询、列表、当前模型命令。
   - **管理员白名单**：逐条添加允许使用主命令的用户 UID（发送者 ID）（`/sid` 输出的 `UID` 行），支持增加 / 删除条目；**列表为空时任何人都无法使用主命令**。
   - **可用模型设置**：从 AstrBot 已配置的模型中单独挑选允许切换的条目并设置别名。此处配置与 AstrBot 自身的模型配置相互独立。勾选条目上的「允许非管理员选择」后，管理员白名单外的用户也能用主命令切换该条目。
   - **会话模型**：列表自动读取已设置首选模型的会话，可逐条查看 / 设置 / 清除；点击「+ 新建条目」填入 UMO（会话 ID）即可直接设置，行为与 `/msto` 一致。
3. 让目标用户在群聊中发送 `/sid`（或启用 `/mstosid` 后发送会话查询命令），把输出中的 UID（发送者 ID）填入管理员白名单并保存。
4. 发送 `/msto <别名或模型ID>` 即可切换。

## 聊天命令

除可在配置中自定义外，命令由插件自行解析，不经过 AstrBot 的命令过滤器与 LLM 管线。

| 命令 | 说明 |
| --- | --- |
| `/msto <别名或模型ID>` | 切换当前会话的首选模型；别名优先匹配，均不区分大小写 |
| `/msto` | 清除当前会话的独立模型配置，回退 AstrBot 默认模型 |
| `/mstolist` | 查看可用模型列表（需启用）；非管理员仅看到勾选了「允许非管理员选择」的条目（未勾选任何条目时看到完整列表） |
| `/mstom` | 查看当前会话模型（需启用） |
| `/mstosid` | 输出本会话 UMO（会话 ID）与 UID（发送者 ID）等信息（需启用；不受管理员白名单限制） |

所有命令的命令前缀与命令名均可在配置中自定义；例如把命令名改为 `模型` 后，命令即变为 `/模型 glm-5.2`。会话查询命令（/mstosid）有独立的命令前缀与命令名，命令前缀为 `/` 时命令名不能改为 `sid`（与内置 `/sid` 冲突，自动回退 `mstosid`）。

## 配置项

| 键 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `enable_main_command` | bool | `true` | 是否启用主命令；关闭后仅可在配置页设置会话模型 |
| `command_prefix` | string | `/` | 聊天命令前缀，留空回退 `/` |
| `command_name` | string | `msto` | 主命令名 |
| `sid_command_prefix` | string | `/` | 会话查询命令前缀；命令前缀为 `/` 时命令名不能为 `sid`（自动回退 `mstosid`） |
| `sid_command_name` | string | `mstosid` | 会话查询命令名 |
| `enable_sid_command` | bool | `false` | 是否启用会话查询命令 |
| `list_command_prefix` | string | `/` | 模型列表命令前缀 |
| `list_command_name` | string | `mstolist` | 模型列表命令名 |
| `list_output_mode` | string | `alias` | 列表输出方式：`alias` 仅别名 / `id` 仅 ID / `both` 别名 + ID |
| `enable_list_command` | bool | `false` | 是否启用模型列表命令 |
| `curr_command_prefix` | string | `/` | 当前模型命令前缀 |
| `curr_command_name` | string | `mstom` | 当前模型命令名 |
| `curr_output_mode` | string | `as_set` | 当前模型输出方式：`as_set` 跟随设置时 / `alias` / `id` / `both` |
| `enable_curr_command` | bool | `false` | 是否启用当前模型命令 |
| `allowed_uids` | list | `[]` | 允许使用主命令的用户 UID 列表（发送者 ID），空列表表示无人可用 |
| `models` | template_list | `[]` | 可用模型条目：`alias`（别名，可空）、`provider_id`（模型 ID（提供商 ID），必填）、`enabled`（启用开关）、`public`（允许非管理员选择） |

## 权限说明

- `/msto` 仅对管理员白名单（UID，`allowed_uids`）内的用户可用，与所在会话无关；白名单外用户在使用了勾选「允许非管理员选择」（`models[].public`）条目的配置下也可用主命令，但只能切换到勾选的条目（无参 `/msto` 清除不受限）。`/mstolist`、`/mstom`、`/mstosid` 不受管理员白名单限制。`enable_main_command` 关闭时主命令不响应，会话模型仅能在配置页设置（适用于 UID（发送者 ID）无法唯一标记或可能被伪造的平台）。
- 配置页「会话模型」标签的查看 / 设置操作同样不受管理员白名单限制（面板本身已有登录保护）。

## 可视化配置

在管理面板的插件详情中点击「打开视图」进入 `views/config/` 页面，支持：

- 命令前缀与命令名的自定义、各子命令独立开关
- 管理员白名单（UID）的增删管理
- 可用模型的挑选、别名设置、启用开关与「允许非管理员选择」勾选
- 已设置首选模型的会话列表查看、设置与清除
- 所有配置通过 Web API 读写，效果与手动编辑配置文件一致

右侧导航支持快速跳转，并跟随面板语言与主题。

## 代码结构

```
main.py            # 插件入口：注册、Web API、事件监听与命令分发
src/
  commands.py      # 聊天命令解析与匹配
  provider_ops.py  # 模型条目管理、别名解析与会话偏好切换
  web_config.py    # 配置校验、模板键补写与日志记录
views/
  config/          # 可视化配置视图（HTML + 前端资源）
vue/               # Vue 源码与构建产物
```

## 实现说明

- 命令不走 AstrBot 的指令注册，而是通过事件监听手动匹配，因此不会与内置 `/provider` 等指令冲突。
- 切换模型调用 AstrBot 的 `provider_manager.set_provider(..., umo=会话 UMO（会话 ID）)`，仅影响当前会话的后续对话。
- 「跟随设置时」输出依赖切换时记录的原始输入（与会话偏好一同存储）；清除模型设置时一并移除。

## 许可证

本项目基于 **GNU Affero General Public License v3.0 (AGPL-3.0)** 发布。

```
astrbot_plugin_group_model_selection - 群聊模型选择
Copyright (C) 2025 K_PU

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```