"""Command parsing for the model selection chat commands."""

from __future__ import annotations

from typing import Any

DEFAULT_PREFIX = "/"
DEFAULT_COMMAND_NAME = "msto"
DEFAULT_SID_COMMAND_NAME = "mstosid"
DEFAULT_LIST_COMMAND_NAME = "mstolist"
DEFAULT_CURR_COMMAND_NAME = "mstom"


def _pair(
    config: Any, prefix_key: str, name_key: str, default_name: str
) -> tuple[str, str]:
    """Read a prefix/name pair from the config with defaults applied.

    Args:
        config: The plugin configuration mapping.
        prefix_key: Config key holding the command prefix.
        name_key: Config key holding the command name.
        default_name: Fallback command name.

    Returns:
        The ``(prefix, command)`` tuple, command lowercased.
    """
    prefix = str(config.get(prefix_key) or "").strip() or DEFAULT_PREFIX
    command = str(config.get(name_key) or "").strip() or default_name
    return prefix, command.lower()


def command_settings(config: Any) -> dict[str, str]:
    """Read the command switches from the plugin configuration.

    Args:
        config: The plugin configuration mapping.

    Returns:
        A dict with ``prefix``/``command`` plus the ``sid_``/``list_``/
        ``curr_`` prefixed pairs (all lowercase command names).
    """
    prefix = str(config.get("command_prefix") or "").strip() or DEFAULT_PREFIX
    command = str(config.get("command_name") or "").strip() or DEFAULT_COMMAND_NAME
    sid_prefix, sid_command = _pair(
        config, "sid_command_prefix", "sid_command_name", DEFAULT_SID_COMMAND_NAME
    )
    list_prefix, list_command = _pair(
        config, "list_command_prefix", "list_command_name", DEFAULT_LIST_COMMAND_NAME
    )
    curr_prefix, curr_command = _pair(
        config, "curr_command_prefix", "curr_command_name", DEFAULT_CURR_COMMAND_NAME
    )
    # Keep clear of the builtin /sid command when using the default prefix.
    if sid_prefix == DEFAULT_PREFIX and sid_command == "sid":
        sid_command = DEFAULT_SID_COMMAND_NAME
    return {
        "prefix": prefix,
        "command": command.lower(),
        "sid_prefix": sid_prefix,
        "sid_command": sid_command,
        "list_prefix": list_prefix,
        "list_command": list_command,
        "curr_prefix": curr_prefix,
        "curr_command": curr_command,
    }


def parse_command(
    text: str,
    settings: dict[str, str],
    woken: bool,
) -> dict[str, Any] | None:
    """Parse a chat message into a main-command invocation.

    The wake stage may already have stripped the server wake prefix, so both
    the raw form (``/msto glm-5.2``) and the woken form (``msto glm-5.2``)
    are accepted here.

    Args:
        text: The raw message text.
        settings: The dict returned by :func:`command_settings`.
        woken: Whether the message passed the @-or-wake check.

    Returns:
        ``{"args": str}`` when the message targets the main command,
        otherwise ``None``. The message starting with the command is treated
        as an invocation regardless of the wake state.
    """
    raw = (text or "").strip()
    if not raw:
        return None
    prefix = settings["prefix"]
    command = settings["command"]
    head = (prefix + command).lower()

    body = None
    if raw.lower().startswith(head):
        rest = raw[len(prefix) + len(command) :]
        # Require a boundary so "/mstolist" does not match "/msto".
        if rest == "" or rest[0].isspace():
            body = rest.strip()
    elif woken:
        parts = raw.split(None, 1)
        if parts and parts[0].lower() == command:
            body = parts[1].strip() if len(parts) > 1 else ""
    if body is None:
        return None
    return {"args": body}


def parse_exact_command(
    text: str,
    prefix: str,
    command: str,
    woken: bool,
) -> bool:
    """Check whether the message invokes a no-argument command.

    Args:
        text: The raw message text.
        prefix: The command prefix, e.g. ``/``.
        command: The command name, e.g. ``mstosid``.
        woken: Whether the message passed the @-or-wake check.

    Returns:
        True when the message is exactly the command (no arguments).
    """
    raw = (text or "").strip()
    if not raw:
        return False
    if raw.lower() == (prefix + command).lower():
        return True
    return bool(woken and raw.lower() == command)
