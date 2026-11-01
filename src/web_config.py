"""Configuration sanitizing and Web API helpers for the config view."""

from __future__ import annotations

from typing import Any

from astrbot.api import logger

TEMPLATE_KEY = "model"


def ensure_template_keys(config: dict[str, Any]) -> bool:
    """Stamp the template key on every model entry.

    The declarative settings page rejects template_list entries without
    one, so stamping keeps both config pages in sync.

    Args:
        config: The plugin configuration mapping.

    Returns:
        True when the config was modified and needs persisting.
    """
    changed = False
    for item in config.get("models") or []:
        if isinstance(item, dict) and item.get("__template_key") != TEMPLATE_KEY:
            item["__template_key"] = TEMPLATE_KEY
            changed = True
    return changed


def sanitize_models(value: Any) -> list[dict[str, Any]]:
    """Normalize the submitted model list into strict entries.

    Args:
        value: Raw models value from a web request body.

    Returns:
        The sanitized list of ``{alias, provider_id, enabled}`` dicts.
    """
    if not isinstance(value, list):
        return []
    entries: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        provider_id = str(item.get("provider_id") or "").strip()
        if not provider_id:
            continue
        entries.append(
            {
                "alias": str(item.get("alias") or "").strip(),
                "provider_id": provider_id,
                "enabled": bool(item.get("enabled", True)),
                "__template_key": TEMPLATE_KEY,
            }
        )
    return entries


def sanitize_output_mode(value: Any, allowed: tuple[str, ...], default: str) -> str:
    """Clamp an output-mode choice to the allowed set.

    Args:
        value: The raw config value.
        allowed: The accepted mode strings.
        default: The fallback when the value is not accepted.

    Returns:
        A mode string from ``allowed``.
    """
    mode = str(value or "").strip().lower()
    return mode if mode in allowed else default


def sanitize_uids(value: Any) -> list[str]:
    """Normalize the submitted UID whitelist into strict entries.

    Accepts a list of strings or a newline/comma separated string, matching
    both the declarative page and the config view payloads.

    Args:
        value: Raw allowed_uids value from a request body.

    Returns:
        The sanitized list of non-empty UID strings.
    """
    if isinstance(value, str):
        items: list[Any] = value.replace(",", "\n").splitlines()
    elif isinstance(value, list):
        items = value
    else:
        return []
    uids: list[str] = []
    for item in items:
        uid = str(item or "").strip()
        if uid:
            uids.append(uid)
    return uids


def log_config_update(username: str | None) -> None:
    """Log a config update for auditing.

    Args:
        username: The dashboard account that saved the configuration.
    """
    logger.info(
        "astrbot_plugin_group_model_selection: 配置已由 %s 更新",
        username or "unknown",
    )
