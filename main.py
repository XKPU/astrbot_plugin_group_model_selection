"""Group model selection plugin for AstrBot."""

from __future__ import annotations

import json

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register
from astrbot.api.web import request as web_request

from .src import commands as command_utils
from .src import provider_ops, web_config

PLUGIN_NAME = "astrbot_plugin_group_model_selection"


@register(
    "astrbot_plugin_group_model_selection",
    "K_PU",
    "通过 /msto 按别名或模型 ID 设置会话首选模型",
    "1.0.5",
)
class GroupModelSelectionPlugin(Star):
    """Per-session model selection via chat commands and a config view."""

    def __init__(self, context: Context, config: AstrBotConfig | None = None):
        super().__init__(context)
        self.config = config
        self._skip_session_sync_once = False

    def _version(self) -> str:
        """Return the plugin version from the star registry."""
        meta = self.context.get_registered_star(PLUGIN_NAME)
        return str(meta.version) if meta and meta.version else ""

    async def initialize(self) -> None:
        """Prepare the plugin: register web APIs and stamp template keys."""
        self._register_web_apis()
        if self.config is not None:
            changed = web_config.ensure_template_keys(self.config)
            if web_config.ensure_model_uuids(self.config):
                changed = True
            if changed:
                self.config.save_config()
            await self._sync_sessions_on_load()

    async def _sync_sessions_on_load(self) -> None:
        """Detect model list changes made outside the config view.

        Compares the persisted identity snapshot with the current model
        list (covering declarative-page saves and manual file edits, both
        followed by a plugin reload), syncs affected sessions, then saves
        the new snapshot.
        """
        snapshot = web_config.load_model_snapshot()
        models = self.config.get("models") or []
        new_snapshot = web_config.entries_snapshot(models)
        try:
            if snapshot is None:
                web_config.save_model_snapshot(new_snapshot)
                return
            if snapshot == new_snapshot:
                return
            if self._skip_session_sync_once:
                self._skip_session_sync_once = False
                web_config.save_model_snapshot(new_snapshot)
                return
            from astrbot.core import sp

            changes = await provider_ops.sync_sessions_after_change(
                self.context, snapshot, new_snapshot, sp
            )
            for change in changes:
                logger.info("模型变更同步会话: %s", change)
            web_config.save_model_snapshot(new_snapshot)
        except Exception as exc:
            logger.error("模型变更同步会话失败: %s", exc)

    def _register_web_apis(self) -> None:
        """Register the config view endpoints (idempotent across reloads)."""
        route = f"/{PLUGIN_NAME}/config"
        self.context.register_web_api(
            route,
            self._web_get_config,
            ["GET"],
            "获取会话模型插件配置",
        )
        self.context.register_web_api(
            route,
            self._web_save_config,
            ["POST"],
            "保存会话模型插件配置",
        )
        self.context.register_web_api(
            f"/{PLUGIN_NAME}/providers",
            self._web_list_providers,
            ["GET"],
            "列出 AstrBot 已配置的提供商（模型）",
        )
        self.context.register_web_api(
            f"/{PLUGIN_NAME}/umos",
            self._web_list_umos,
            ["GET"],
            "列出已知会话（用于会话选择器）",
        )
        self.context.register_web_api(
            f"/{PLUGIN_NAME}/senders",
            self._web_search_senders,
            ["GET"],
            "搜索发送者（用于用户选择器）",
        )
        self.context.register_web_api(
            f"/{PLUGIN_NAME}/sessions",
            self._web_list_sessions,
            ["GET"],
            "列出已设置首选模型的会话",
        )
        self.context.register_web_api(
            f"/{PLUGIN_NAME}/version",
            self._web_get_version,
            ["GET"],
            "获取插件版本",
        )
        self.context.register_web_api(
            f"/{PLUGIN_NAME}/session-model",
            self._web_session_model,
            ["GET"],
            "查询当前会话模型",
        )
        self.context.register_web_api(
            f"/{PLUGIN_NAME}/session-model",
            self._web_set_session_model,
            ["POST"],
            "设置会话首选模型",
        )

    async def _web_get_config(self) -> dict:
        """Return the plugin configuration read fresh from disk.

        The config file is the source of truth (the declarative settings
        page and manual edits write it directly), so the view reload must
        re-read it instead of serving the in-memory copy.
        """
        disk_config: dict | None = None
        config_path = getattr(self.config, "config_path", None)
        if config_path:
            try:
                with open(config_path, encoding="utf-8-sig") as handle:
                    loaded = json.load(handle)
                if isinstance(loaded, dict):
                    disk_config = loaded
            except (OSError, ValueError) as exc:
                logger.warning("读取配置文件失败，回退内存配置: %s", exc)
        if disk_config is None:
            disk_config = dict(self.config)
        return {"status": "ok", "data": {"config": disk_config}}

    async def _web_save_config(self) -> dict:
        """Apply the submitted configuration and persist it.

        Returns:
            A status dict for the dashboard response envelope.
        """
        try:
            body = await web_request.json(default=None)
        except Exception:
            body = None
        config = body.get("config") if isinstance(body, dict) else None
        if not isinstance(config, dict):
            return {"status": "error", "message": "缺少 config 对象。", "data": {}}

        next_config = dict(self.config)
        next_config["enable_main_command"] = bool(
            config.get("enable_main_command", True)
        )
        next_config["command_prefix"] = (
            str(config.get("command_prefix") or "").strip() or "/"
        )
        next_config["command_name"] = (
            str(config.get("command_name") or "").strip() or "msto"
        )
        next_config["sid_command_prefix"] = (
            str(config.get("sid_command_prefix") or "").strip() or "/"
        )
        next_config["sid_command_name"] = (
            str(config.get("sid_command_name") or "").strip() or "mstosid"
        )
        next_config["enable_sid_command"] = bool(config.get("enable_sid_command"))
        next_config["enable_list_command"] = bool(config.get("enable_list_command"))
        next_config["list_command_prefix"] = (
            str(config.get("list_command_prefix") or "").strip() or "/"
        )
        next_config["list_command_name"] = (
            str(config.get("list_command_name") or "").strip() or "mstolist"
        )
        next_config["list_output_mode"] = web_config.sanitize_output_mode(
            config.get("list_output_mode"), ("alias", "id", "both"), "alias"
        )
        next_config["enable_curr_command"] = bool(config.get("enable_curr_command"))
        next_config["curr_command_prefix"] = (
            str(config.get("curr_command_prefix") or "").strip() or "/"
        )
        next_config["curr_command_name"] = (
            str(config.get("curr_command_name") or "").strip() or "mstom"
        )
        next_config["curr_output_mode"] = web_config.sanitize_output_mode(
            config.get("curr_output_mode"),
            ("as_set", "alias", "id", "both"),
            "as_set",
        )
        next_config["allowed_uids"] = web_config.sanitize_uids(
            config.get("allowed_uids")
        )
        next_config["models"] = web_config.sanitize_models(config.get("models"))

        old_snapshot = web_config.entries_snapshot((self.config or {}).get("models"))
        new_snapshot = web_config.entries_snapshot(next_config["models"])

        self.config.update(next_config)
        self.config.save_config()
        web_config.log_config_update(web_request.username)
        self._skip_session_sync_once = True
        await self.initialize()
        session_changes: list[str] = []
        try:
            from astrbot.core import sp

            session_changes = await provider_ops.sync_sessions_after_change(
                self.context, old_snapshot, new_snapshot, sp
            )
        except Exception as exc:
            logger.error("保存后同步会话失败: %s", exc)
        web_config.save_model_snapshot(new_snapshot)
        return {
            "status": "ok",
            "data": {"config": dict(self.config), "session_changes": session_changes},
        }

    async def _web_list_providers(self) -> dict:
        """List the models configured in AstrBot for the config view."""
        providers = []
        for provider in self.context.get_all_providers():
            try:
                meta = provider.meta()
            except Exception:
                continue
            providers.append(
                {
                    "id": str(meta.id or ""),
                    "model": str(meta.model or ""),
                }
            )
        return {"status": "ok", "data": {"providers": providers}}

    async def _web_list_umos(self) -> dict:
        """List known sessions for the session picker.

        Mirrors the dashboard session selector: sessions are sourced from
        the sender/alias tables, latest activity first.
        """
        db = self.context.get_db()
        try:
            records = await db.get_umo_senders(search="", limit=100)
        except Exception as exc:
            logger.error("枚举已知会话失败: %s", exc)
            return {"status": "error", "message": "读取会话列表失败。", "data": {}}
        umos: dict[str, dict] = {}
        for sender, alias in records:
            umo = str(getattr(sender, "umo", "") or "")
            if not umo or umo in umos:
                continue
            auto_name = str(getattr(alias, "auto_name", "") or "")
            user_alias = str(getattr(alias, "user_alias", "") or "")
            umos[umo] = {
                "umo": umo,
                "platform": umo.split(":", 1)[0],
                "sender_id": str(getattr(sender, "sender_id", "") or ""),
                "sender_name": str(getattr(sender, "sender_name", "") or ""),
                "auto_name": auto_name,
                "user_alias": user_alias,
                "display_name": user_alias or auto_name or umo,
            }
        return {"status": "ok", "data": {"umos": list(umos.values())}}

    async def _web_search_senders(self) -> dict:
        """Search senders for the user picker.

        Query parameters:
            search: Fuzzy keyword matched against sender and alias names.
            limit: Max rows (1-100).
            sender_ids: Repeatable; resolves names for the given IDs.
        """
        query = web_request.query
        search = str(query.get("search", "") or "").strip()
        raw_limit = query.get("limit", 50, int) or 50
        limit = max(1, min(raw_limit, 100))
        sender_ids = query.getlist("sender_ids") + query.getlist("sender_ids[]")
        sender_ids = [str(item) for item in sender_ids if str(item).strip()]
        try:
            db = self.context.get_db()
            records = await db.get_umo_senders(
                search=search,
                limit=limit,
                sender_ids=sender_ids or None,
            )
        except Exception as exc:
            logger.error("搜索发送者失败: %s", exc)
            return {"status": "error", "message": "读取用户列表失败。", "data": {}}
        senders = []
        for sender, alias in records:
            umo = str(getattr(sender, "umo", "") or "")
            senders.append(
                {
                    "sender_id": str(getattr(sender, "sender_id", "") or ""),
                    "sender_name": str(getattr(sender, "sender_name", "") or ""),
                    "platform": umo.split(":", 1)[0] if umo else "",
                }
            )
        return {"status": "ok", "data": {"senders": senders}}

    async def _web_list_sessions(self) -> dict:
        """List every session that currently has a preferred model set."""
        try:
            from astrbot.core import sp

            preferences = await sp.range_get_async(
                "umo", None, provider_ops.PROVIDER_PREF_KEY
            )
        except Exception as exc:
            logger.error("枚举会话失败: %s", exc)
            return {"status": "error", "message": "读取会话列表失败。", "data": {}}
        sessions = []
        for pref in preferences:
            umo = str(getattr(pref, "scope_id", "") or "")
            if umo:
                sessions.append(umo)
        return {"status": "ok", "data": {"sessions": sorted(sessions)}}

    async def _web_get_version(self) -> dict:
        """Return the plugin version for the config view footer."""
        return {"status": "ok", "data": {"version": self._version()}}

    async def _web_session_model(self) -> dict:
        """Report the effective model of the requested session.

        Query parameters:
            umo: The unified message origin to inspect.
        """
        umo = str(web_request.query.get("umo", "") or "").strip()
        if not umo:
            return {"status": "error", "message": "缺少 umo 参数。", "data": {}}
        try:
            info = await provider_ops.session_model_info(self.context, umo, self.config)
        except Exception as exc:
            return {"status": "error", "message": str(exc), "data": {}}
        return {"status": "ok", "data": {"umo": umo, "info": info}}

    async def _web_set_session_model(self) -> dict:
        """Set or clear the preferred model of the requested session.

        Body:
            umo: The unified message origin to update.
            token: The alias or model ID typed, empty to reset.
        """
        try:
            body = await web_request.json(default=None)
        except Exception:
            body = None
        if not isinstance(body, dict):
            return {"status": "error", "message": "缺少请求体。", "data": {}}
        umo = str(body.get("umo") or "").strip()
        if not umo:
            return {"status": "error", "message": "缺少 umo 参数。", "data": {}}
        token = str(body.get("token") or "").strip()
        try:
            if not token:
                await provider_ops.reset_provider(self.context, umo)
            else:
                entry = provider_ops.resolve_model(self.config or {}, token)
                if not entry:
                    return {
                        "status": "error",
                        "message": f"未找到模型或别名：{token}",
                        "data": {},
                    }
                await provider_ops.switch_provider(
                    self.context, umo, entry["provider_id"], token
                )
        except Exception as exc:
            logger.error(
                "会话 %s 设置 %s 失败: %s",
                umo,
                token,
                exc,
            )
            return {"status": "error", "message": "设置错误", "data": {}}
        return {"status": "ok", "data": {}}

    def _settings(self) -> dict[str, str]:
        """Return the effective command settings."""
        return command_utils.command_settings(self.config or {})

    def _allowed_uids(self) -> list[str]:
        """Return the normalized UID whitelist."""
        return web_config.sanitize_uids(
            self.config.get("allowed_uids") if self.config else []
        )

    def _uid_allowed(self, event: AstrMessageEvent) -> bool:
        """Check the sender against the UID whitelist.

        Args:
            event: The incoming message event.

        Returns:
            True when the sender's UID is whitelisted.
        """
        allowed = self._allowed_uids()
        if not allowed:
            return False
        return str(event.get_sender_id() or "") in allowed

    async def _reply(self, event: AstrMessageEvent, text: str) -> None:
        """Send a plain-text reply and stop event propagation.

        Send failures are logged and swallowed: some OneBot adapters raise
        ActionFailed on self-echo timeout even though the message was
        delivered.
        """
        event.stop_event()
        try:
            await event.send(event.plain_result(text))
        except Exception as exc:
            logger.warning(
                "回复发送失败（消息可能已送达）: %s",
                exc,
            )

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_message(self, event: AstrMessageEvent, *args, **kwargs):
        """Handle chat messages, matching the /msto, /mstosid, /mstolist and /mstom commands.

        Args:
            event: The incoming message event.
        """
        settings = self._settings()
        woken = bool(event.is_at_or_wake_command)
        try:
            if command_utils.parse_exact_command(
                event.message_str,
                settings["sid_prefix"],
                settings["sid_command"],
                woken,
            ):
                if self.config and self.config.get("enable_sid_command"):
                    await self._handle_sid_command(event)
                return
            if command_utils.parse_exact_command(
                event.message_str,
                settings["list_prefix"],
                settings["list_command"],
                woken,
            ):
                if self.config and self.config.get("enable_list_command"):
                    await self._handle_list_command(event)
                return
            if command_utils.parse_exact_command(
                event.message_str,
                settings["curr_prefix"],
                settings["curr_command"],
                woken,
            ):
                if self.config and self.config.get("enable_curr_command"):
                    await self._handle_curr_command(event)
                return
            parsed = command_utils.parse_command(event.message_str, settings, woken)
            if parsed is None:
                return
            if not (self.config and self.config.get("enable_main_command", True)):
                return
            is_admin = self._uid_allowed(event)
            if not is_admin and not provider_ops.public_entries(self.config or {}):
                await self._reply(event, "本用户无权使用该命令。")
                return
            await self._run_model_command(event, parsed["args"], is_admin)
        except Exception as exc:
            logger.exception("处理失败: %s", exc)
            if woken:
                await self._reply(event, "命令处理失败，请稍后重试。")

    async def _handle_sid_command(self, event: AstrMessageEvent) -> None:
        """Reply with the session identifiers mirroring /sid."""
        umo = event.unified_msg_origin
        session = event.session
        bot_id = session.platform_id if session else ""
        message_type = session.message_type.value if session else ""
        session_id = session.session_id if session else ""
        group_id = event.get_group_id()
        lines = [
            f"UMO: 「{umo}」",
            f"UID: 「{event.get_sender_id()}」",
            "*Use UID to set whitelist (白名单请填 UID)。",
            "",
            "Your session information:",
            f"Bot ID: 「{bot_id}」",
            f"Message Type: 「{message_type}」",
            f"Session ID: 「{session_id}」",
        ]
        if group_id:
            lines.append(f"Group ID: 「{group_id}」")
        await self._reply(event, "\n".join(lines))

    async def _handle_list_command(self, event: AstrMessageEvent) -> None:
        """Reply with the model list visible to the requesting user."""
        mode = str((self.config or {}).get("list_output_mode") or "alias")
        entries = provider_ops.model_entries(self.config or {})
        if not self._uid_allowed(event):
            public = provider_ops.public_entries(self.config or {})
            if public:
                entries = public
        lines = []
        for entry in entries:
            rendered = provider_ops.format_model_output(
                {"alias": entry["alias"], "provider_id": entry["provider_id"]},
                mode,
            )
            if rendered:
                lines.append(rendered)
        await self._reply(event, "\n".join(lines) if lines else "尚未配置可用模型。")

    async def _handle_curr_command(self, event: AstrMessageEvent) -> None:
        """Reply with the model this session is currently using."""
        mode = str((self.config or {}).get("curr_output_mode") or "as_set")
        try:
            info = await provider_ops.session_model_info(
                self.context, event.unified_msg_origin, self.config
            )
        except Exception as exc:
            logger.error(
                "查询当前模型失败(umo=%s): %s",
                event.unified_msg_origin,
                exc,
            )
            await self._reply(event, "查询错误")
            return
        rendered = provider_ops.format_model_output(info, mode)
        await self._reply(
            event,
            f"当前会话模型：{rendered}" if rendered else "当前会话模型：默认配置",
        )

    async def _run_model_command(
        self,
        event: AstrMessageEvent,
        args: str,
        is_admin: bool = True,
    ) -> None:
        """Switch, reset, or report the session's preferred model.

        Non-admin users resolve tokens against entries flagged
        ``public`` only; admins resolve against the whole list.
        """
        umo = event.unified_msg_origin
        token = args.split(None, 1)[0] if args.split() else ""
        if not token:
            await provider_ops.reset_provider(self.context, umo)
            await self._reply(event, "当前会话模型已恢复为默认配置。")
            return
        key = "models" if is_admin else "public"
        entry = provider_ops.resolve_model(self.config or {}, token, key)
        if entry is None and is_admin:
            entry = provider_ops.resolve_model(self.config or {}, token, "public")
        if entry is None:
            await self._reply(event, f"未找到模型或别名：{token}")
            return
        try:
            await provider_ops.switch_provider(self.context, umo, entry["provider_id"])
        except Exception as exc:
            logger.error(
                "切换到 %s(umo=%s) 失败: %s",
                entry["provider_id"],
                umo,
                exc,
            )
            await self._reply(event, "设置错误")
            return
        await self._reply(event, f"当前会话模型更改为：{token}")

    async def terminate(self):
        """Release resources on unload."""
        return None
