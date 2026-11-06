"""Configuration sanitizing and Web API helpers for the config view."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from astrbot.api import logger

TEMPLATE_KEY = "model"
MODEL_SNAPSHOT_NAME = ".model_snapshot.json"
PLUGIN_NAME = "astrbot_plugin_group_model_selection"


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


def ensure_model_uuids(config: dict[str, Any]) -> bool:
    """Assign a UUID to every model entry missing one (legacy compatibility).

    Args:
        config: The plugin configuration mapping.

    Returns:
        True when the config was modified and needs persisting.
    """
    changed = False
    for item in config.get("models") or []:
        if isinstance(item, dict) and not str(item.get("uuid") or "").strip():
            item["uuid"] = uuid.uuid4().hex
            changed = True
    return changed


def sanitize_models(
    value: Any, template_key: str = TEMPLATE_KEY
) -> list[dict[str, Any]]:
    """Normalize the submitted model list into strict entries.

    Existing UUIDs are kept so an entry keeps its identity across alias
    or provider edits; new or legacy entries without one get a fresh UUID.

    Args:
        value: Raw models value from a web request body.
        template_key: The template key stamped on each entry.

    Returns:
        The sanitized list of ``{uuid, alias, provider_id, enabled, public}``
        dicts.
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
                "uuid": str(item.get("uuid") or "").strip() or uuid.uuid4().hex,
                "alias": str(item.get("alias") or "").strip(),
                "provider_id": provider_id,
                "enabled": bool(item.get("enabled", True)),
                "public": bool(item.get("public", False)),
                "__template_key": template_key,
            }
        )
    return entries


def entries_snapshot(models: Any) -> dict[str, dict[str, str]]:
    """Map model UUID to alias and provider_id for change detection.

    Args:
        models: The raw models list; entries without a UUID are skipped.

    Returns:
        A ``{uuid: {"alias": ..., "provider_id": ...}}`` mapping.
    """
    snapshot: dict[str, dict[str, str]] = {}
    for item in models or []:
        if not isinstance(item, dict):
            continue
        entry_uuid = str(item.get("uuid") or "").strip()
        if not entry_uuid:
            continue
        snapshot[entry_uuid] = {
            "alias": str(item.get("alias") or "").strip(),
            "provider_id": str(item.get("provider_id") or "").strip(),
        }
    return snapshot


def _snapshot_path() -> Path:
    """Return the snapshot file path under the plugin data directory.

    Uses ``StarTools.get_data_dir`` (data/plugin_data/<plugin_name>) so
    persisted state survives plugin reinstalls and stays auditable.
    """
    from astrbot.api.star import StarTools

    return StarTools.get_data_dir(PLUGIN_NAME) / MODEL_SNAPSHOT_NAME


def load_model_snapshot() -> dict[str, dict[str, str]] | None:
    """Load the persisted model identity snapshot.

    Returns:
        The saved snapshot mapping, or ``None`` when absent or unreadable
        (treated as the first run).
    """
    path = _snapshot_path()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        logger.warning("读取模型快照失败，将按首次运行处理: %s", exc)
        return None
    return data if isinstance(data, dict) else None


def save_model_snapshot(snapshot: dict[str, dict[str, str]]) -> None:
    """Persist the model identity snapshot in the plugin data directory.

    Args:
        snapshot: The ``{uuid: {alias, provider_id}}`` mapping to store.
    """
    path = _snapshot_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except OSError as exc:
        logger.error("写入模型快照失败: %s", exc)


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
    logger.info("配置已由 %s 更新", username or "unknown")
