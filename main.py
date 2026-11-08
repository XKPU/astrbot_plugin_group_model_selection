"""Plugin entry: lifecycle management plus the chat command dispatcher."""

from __future__ import annotations

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

from .src import commands as command_utils
from .src import provider_ops, web_config
from .src.chat_commands import CommandMixin
from .src.web_apis import WebApiMixin

PLUGIN_NAME = "astrbot_plugin_group_model_selection"


@register(
    "astrbot_plugin_group_model_selection",
    "K_PU",
    "通过 /msto 按别名或模型 ID 设置会话首选模型",
    "1.0.5",
)
class GroupModelSelectionPlugin(WebApiMixin, CommandMixin, Star):
    """Per-session model selection via chat commands and a config view."""

    def __init__(self, context: Context, config: AstrBotConfig | None = None):
        super().__init__(context)
        self.config = config
        self._skip_session_sync_once = False

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

    async def terminate(self):
        """Release resources on unload."""
        return None
