# 支持

插件的一般说明见 [README.md](README.md)。

## 目录

- [提问之前](#提问之前)
- [报告缺陷与建议](#报告缺陷与建议)
- [不在支持范围内](#不在支持范围内)
- [安全](#安全)
- [参与贡献](#参与贡献)
- [许可](#许可)

## 提问之前

下面覆盖最常见的问题。

### 1. 发送 `/msto <模型 ID>` 提示"本用户无权使用该命令"

`/msto` 仅对管理员白名单（UID）内的用户开放；白名单外用户只有在有勾选「允许非管理员选择」的模型条目时才能使用主命令。请：

1. 在私信中发送 `/sid`（或启用会话查询命令后发送 `/mstosid`），获取输出中的 `UID`（发送者 ID）值；
2. 打开插件配置页 →「管理员白名单」，点击「+ 新建条目」，将步骤 1 中获取的 UID 填入并保存（也可在「插件配置」的声明式配置中直接编辑 `allowed_uids` 列表）；
3. 若只想让该用户切换部分模型，可改在「可用模型设置」中勾选对应条目的「允许非管理员选择」，该用户即可用主命令切换这些模型。

### 2. 发送 `/msto <模型 ID>` 提示"未找到模型或别名"

请检查：

1. 打开插件配置页 →「可用模型设置」，确认该模型已在列表中且处于「启用」状态；
2. 非管理员用户还请确认该条目已勾选「允许非管理员选择」（未勾选任何条目时非管理员与管理员可见范围相同）；
3. 如果使用的是别名，确认配置中为该模型设置了对应的别名；
4. 别名与模型 ID 均不区分大小写，但必须完全匹配（不含多余空格）。

### 3. 修改或删除模型条目后，已设置的会话会怎样

插件为每个模型条目自动分配 UUID 作为身份标识（旧版配置在插件加载时自动补齐）：

- **删除条目**：正在使用该模型的会话自动清除独立配置，恢复 AstrBot 默认模型；
- **修改别名**：会话绑定的输入记录同步更新，`/mstom` 的「跟随设置时」输出显示新别名；
- **修改模型 ID**：会话自动迁移到新模型；迁移失败（如新 ID 不存在）时会话恢复默认模型。

同步在声明式配置页保存或手动编辑配置文件后重载插件时自动进行；可视化配置页保存后会提示同步的会话数量。

## 报告缺陷与建议

缺陷报告、功能建议与使用疑问，请提交到 GitHub Issues：

[https://github.com/XKPU/astrbot_plugin_group_model_selection/issues](https://github.com/XKPU/astrbot_plugin_group_model_selection/issues)

### 一份有用的缺陷报告通常包含

1. **你做了什么** —— 导致问题的操作步骤。
2. **预期结果** 与 **实际结果**。
3. **环境** —— AstrBot 版本、插件版本、Python 版本、操作系统。
4. **AstrBot 日志** —— 请裁剪出错的那一步，最好为 Debug 日志等级下。

> **请勿附带含有个人数据的日志或配置文件。**

## 不在支持范围内

- **非 AstrBot 标准环境。** 本插件基于 AstrBot 的 Provider 与 Session 机制开发，脱离 AstrBot 框架无法运行。
- **UID 无法唯一标识用户的平台。** 插件依赖平台返回的 UID（发送者 ID）做白名单判断，若你的平台 UID 可被伪造或无法定位单一用户，请关闭主命令（`enable_main_command` 设为 `false`），仅使用可视化配置页面管理会话模型。

## 安全

发现安全问题请**不要**开公开 issue。可通过以下渠道私下报告：

- GitHub 安全公告：[https://github.com/XKPU/astrbot_plugin_group_model_selection/security/advisories/new](https://github.com/XKPU/astrbot_plugin_group_model_selection/security/advisories/new)
- 邮箱：`csaxongmail@gmail.com` 或 `u-eptm@u-eptm.top`

更详细的内容见 [SECURITY.md](SECURITY.md)。

## 参与贡献

欢迎提交 Pull Request 或参与 Issue 讨论。

提交前请确保：

- 代码通过 Ruff 格式化。
- 代码功能通过测试。

**未完成或未经测试的提交**同样欢迎，请在提交时说明其状态。

## 许可

本项目基于 **GNU Affero General Public License v3.0 (AGPL-3.0)** 发布。

```
astrbot_plugin_group_model_selection - 会话模型选择
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