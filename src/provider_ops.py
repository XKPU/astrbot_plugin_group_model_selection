"""Model registry and provider switching for the group model selection."""

from __future__ import annotations

from typing import Any

from astrbot.api import logger
from astrbot.core.provider.entities import ProviderType

PROVIDER_PREF_KEY = "provider_perf_chat_completion"
LAST_INPUT_KEY = "group_model_selection_last_input"


def model_entries(config: Any, key: str = "models") -> list[dict[str, Any]]:
    """Return the enabled model entries configured for the command.

    Args:
        config: The plugin configuration mapping.
        key: The config key holding the template list ("models").
            When ``public`` is True only entries flagged for non-admin
            use are returned.

    Returns:
        The list of enabled, non-empty model entries with their aliases.
    """
    entries: list[dict[str, Any]] = []
    for item in config.get(key) or []:
        if not isinstance(item, dict) or not item.get("enabled", True):
            continue
        provider_id = str(item.get("provider_id") or "").strip()
        if not provider_id:
            continue
        entries.append(
            {
                "provider_id": provider_id,
                "alias": str(item.get("alias") or "").strip(),
            }
        )
    return entries


def public_entries(config: Any) -> list[dict[str, Any]]:
    """Return the enabled entries flagged as selectable by non-admins.

    Args:
        config: The plugin configuration mapping.

    Returns:
        The subset of enabled model entries with ``public`` enabled.
    """
    entries: list[dict[str, Any]] = []
    for item in config.get("models") or []:
        if not isinstance(item, dict) or not item.get("enabled", True):
            continue
        if not item.get("public", False):
            continue
        provider_id = str(item.get("provider_id") or "").strip()
        if not provider_id:
            continue
        entries.append(
            {
                "provider_id": provider_id,
                "alias": str(item.get("alias") or "").strip(),
            }
        )
    return entries


def resolve_model(
    config: Any,
    token: str,
    key: str = "models",
) -> dict[str, Any] | None:
    """Resolve a command token to a configured model entry.

    Alias matches win over provider-id matches; both are case-insensitive.

    Args:
        config: The plugin configuration mapping.
        token: The alias or provider ID typed after the command.
        key: The config key holding the template list to match against.
            ``"public"`` matches only entries flagged for non-admin use.

    Returns:
        The matched entry, or ``None`` when nothing matches.
    """
    wanted = str(token or "").strip().lower()
    if not wanted:
        return None
    entries = public_entries(config) if key == "public" else model_entries(config, key)
    for entry in entries:
        if entry["alias"] and entry["alias"].lower() == wanted:
            return entry
    for entry in entries:
        if entry["provider_id"].lower() == wanted:
            return entry
    return None


async def switch_provider(
    context: Any, umo: str, provider_id: str, token: str = ""
) -> str:
    """Switch the session preference to the given provider.

    Args:
        context: The plugin context.
        umo: The unified message origin of the session.
        provider_id: The target provider (model) ID.
        token: The alias or ID the user typed, remembered for the
            ``as_set`` output mode.

    Returns:
        The ``provider_id`` of the provider now in effect.

    Raises:
        ValueError: If the provider ID does not exist.
    """
    await context.provider_manager.set_provider(
        provider_id=provider_id,
        provider_type=ProviderType.CHAT_COMPLETION,
        umo=umo,
    )
    if token:
        from astrbot.core import sp

        await sp.session_put(umo, LAST_INPUT_KEY, token)
    return provider_id


async def reset_provider(context: Any, umo: str) -> None:
    """Remove the session preference so AstrBot's default applies again.

    Args:
        context: The plugin context.
        umo: The unified message origin of the session.
    """
    from astrbot.core import sp

    await sp.session_remove(umo, PROVIDER_PREF_KEY)
    await sp.session_remove(umo, LAST_INPUT_KEY)


async def sync_sessions_after_change(
    context: Any,
    old_snapshot: dict[str, dict[str, str]],
    new_snapshot: dict[str, dict[str, str]],
    sp: Any,
) -> list[str]:
    """Adjust sessions whose preferred model was removed or edited.

    Args:
        context: The plugin context, used to switch providers.
        old_snapshot: ``{uuid: {alias, provider_id}}`` saved before the change.
        new_snapshot: The same mapping after the change.
        sp: Shared preferences object (required, injectable for tests).

    Returns:
        Human-readable descriptions of the sessions that were adjusted.
    """
    if not old_snapshot or not sp:
        return []
    try:
        prefs = await sp.range_get_async("umo", None, PROVIDER_PREF_KEY)
    except Exception:
        logger.error("sync_sessions_after_change: 枚举会话偏好失败")
        return []

    changes: list[str] = []
    for pref in prefs:
        umo = getattr(pref, "scope_id", None)
        if not umo:
            continue
        action = await _sync_single_session(
            context, sp, umo, old_snapshot, new_snapshot
        )
        if action:
            changes.append(f"{umo}: {action}")
    return changes


async def _sync_single_session(
    context: Any,
    sp: Any,
    umo: str,
    old_snapshot: dict[str, dict[str, str]],
    new_snapshot: dict[str, dict[str, str]],
) -> str | None:
    """Rebind, migrate, or reset one session; returns a description or None."""
    token = await sp.session_get(umo, LAST_INPUT_KEY, None)
    owner = _find_owner_uuid(token, old_snapshot)

    if owner is None:
        current_id = await sp.session_get(umo, PROVIDER_PREF_KEY, None)
        if not current_id:
            return None
        owners = [
            uuid
            for uuid, entry in old_snapshot.items()
            if entry.get("provider_id") == current_id
        ]
        owner = owners[0] if len(owners) == 1 else None
        if owner is None:
            return None

    if owner not in new_snapshot:
        await sp.session_remove(umo, PROVIDER_PREF_KEY)
        await sp.session_remove(umo, LAST_INPUT_KEY)
        return "会话使用的模型已被移除，已恢复默认模型"

    new_entry = new_snapshot[owner]
    old_entry = old_snapshot[owner]
    alias_changed = new_entry["alias"] != old_entry["alias"]
    provider_changed = new_entry["provider_id"] != old_entry["provider_id"]

    if alias_changed:
        if new_entry["alias"]:
            await sp.session_put(umo, LAST_INPUT_KEY, new_entry["alias"])
        else:
            await sp.session_remove(umo, LAST_INPUT_KEY)

    if provider_changed:
        try:
            await context.provider_manager.set_provider(
                provider_id=new_entry["provider_id"],
                provider_type=ProviderType.CHAT_COMPLETION,
                umo=umo,
            )
        except Exception:
            logger.error("sync_sessions_after_change: 迁移会话 %s 失败", umo)
            await sp.session_remove(umo, PROVIDER_PREF_KEY)
            await sp.session_remove(umo, LAST_INPUT_KEY)
            return "会话迁移至新模型失败，已恢复默认模型"
        return "会话已迁移至修改后的模型"

    return "会话绑定的别名已同步" if alias_changed else None


def _find_owner_uuid(
    token: Any,
    old_snapshot: dict[str, dict[str, str]],
) -> str | None:
    """Resolve which model entry a session was bound to before the change."""
    if token:
        lowered = str(token).lower()
        for uuid, entry in old_snapshot.items():
            if entry.get("alias", "").lower() == lowered:
                return uuid
        for uuid, entry in old_snapshot.items():
            if entry.get("provider_id") == token:
                return uuid
    return None


async def session_model_info(context: Any, umo: str, config: Any) -> dict[str, Any]:
    """Collect what the session is currently using for chat completions.

    Args:
        context: The plugin context.
        umo: The unified message origin of the session.
        config: The plugin configuration mapping, used to map the
            effective provider back to its alias.

    Returns:
        A dict with ``provider_id`` (effective provider or ``None``),
        ``as_set`` (the token typed when it was set, or ``None``), and
        ``alias`` (the configured alias for the effective provider, or
        empty when unknown or unset).
    """
    from astrbot.core import sp

    provider = await context.get_using_provider_async(umo=umo)
    provider_id = None
    if provider is not None:
        try:
            provider_id = str(provider.meta().id or "")
        except Exception:
            provider_id = None
    as_set = await sp.session_get(umo, LAST_INPUT_KEY, None)
    alias = ""
    if provider_id:
        for entry in model_entries(config):
            if entry["provider_id"].lower() == provider_id.lower():
                alias = entry["alias"]
                break
    return {"provider_id": provider_id, "as_set": as_set, "alias": alias}


def format_model_output(info: dict[str, Any], mode: str) -> str:
    """Format a model reference according to the configured output mode.

    Args:
        info: A dict with ``provider_id``, ``as_set`` and ``alias`` keys
            (as produced by :func:`session_model_info`), or a plain
            ``{"alias": ..., "provider_id": ...}`` entry.
        mode: One of ``as_set``, ``alias``, ``id`` or ``both``.

    Returns:
        The human-readable model reference; empty when nothing applies.
    """
    alias = str(info.get("alias") or "")
    provider_id = str(info.get("provider_id") or "")
    as_set = str(info.get("as_set") or "")
    if mode == "as_set":
        return as_set or alias or provider_id
    if mode == "alias":
        return alias or provider_id
    if mode == "id":
        return provider_id
    if mode == "both":
        if alias and provider_id and alias.lower() != provider_id.lower():
            return f"{alias}（{provider_id}）"
        return alias or provider_id
    return alias or provider_id
