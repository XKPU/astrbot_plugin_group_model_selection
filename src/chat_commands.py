"""Chat command handling mixed into the plugin class."""

from __future__ import annotations

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent

from . import commands as command_utils
from . import provider_ops, web_config


class CommandMixin:
    """Plain (undecorated) handlers behind the on_message dispatcher."""

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
