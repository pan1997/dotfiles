"""
Based on https://github.com/pedroscaff/swaywsr.git
"""

import asyncio
from i3ipc.aio import Connection
from i3ipc.aio import Con
from i3ipc import WindowEvent, WorkspaceEvent, Event, WorkspaceReply
import functools
import logging

from typing import List, Dict


class Configuration(object):
    separator: str = "  "
    aliases: Dict[str, str] = {}
    icons: Dict[str, str] = {
        "ulauncher": "",
        "TelegramDesktop": "",
        "firefox": "",
        "Alacritty": "",
        "kitty": "",
        "Slack": "",
        "Chromium": "",
        "zoom": "",
        "jetbrains-pycharm-ce": "",
        "jetbrains-idea-ce": "",
        "jetbrains-clion": "",
        "jetbrains-toolbox": "",
        "org.qbittorrent.qBittorrent": "",
        "org.gnome.Nautilus": "",
        "vlc": "嗢",
        "gnome-control-center": "",
        "eog": "",
    }
    remove_duplicates = True  # Remove duplicates in the same workspace
    show_names: bool = False
    ignored_workspaces: List[str] = ["__i3_scratch"]
    log: logging.Logger = logging.Logger(name="wsr")


def get_class(window: Con, configuration: Configuration) -> str:
    configuration.log.debug(f"fetching class of {window.name}")
    name = window.app_id
    if not name:
        name = window.window_class
    if name:
        display_name = configuration.aliases.get(name, name)
        icon = configuration.icons.get(name)
        if icon:
            if configuration.show_names:
                return f'{icon} {display_name}'
            else:
                return icon
        else:
            return name
    raise Exception(f"Unable to process {window.name}")


def get_classes(workspace: Con, configuration: Configuration) -> List[str]:
    assert workspace.type == "workspace"
    leaves = workspace.leaves()
    result = [get_class(window, configuration) for window in leaves]
    if configuration.remove_duplicates:
        result = list(dict.fromkeys(result))
    return result


def get_workspaces(tree: Con) -> List[Con]:
    result = [node for node in tree.descendants() if node.type == "workspace"]
    return result


async def update_workspace_names(connection: Connection, configuration: Configuration) -> None:
    tree = await connection.get_tree()
    for workspace in get_workspaces(tree):
        configuration.log.debug(f"workspace: {workspace.name}")
        if workspace.name not in configuration.ignored_workspaces:
            classes = configuration.separator.join(get_classes(workspace, configuration))
            old_name = workspace.name

            # keep the first word as is to avoid loosing workspace number
            name_prefix = old_name.split(' ')[0]
            if not name_prefix.isdigit():
                name_prefix = ""
            new_name = f"{name_prefix}{configuration.separator}{classes}" if len(classes) > 0 else name_prefix
            if old_name != new_name:
                command = f'rename workspace "{old_name}" to "{new_name}"'
                configuration.log.info(command)
                reply = await connection.command(command)
                configuration.log.info(f"reply: {[f'{r.success} {r.error}' for r in reply]}")


def handle_window_event(
        configuration: Configuration,
        connection: Connection,
        event: WindowEvent,
) -> None:
    if event.change in ["new", "close", "move"]:
        asyncio.ensure_future(update_workspace_names(connection, configuration))


def handle_workspace_event(
        configuration: Configuration,
        connection: Connection,
        event: WorkspaceEvent,
) -> None:
    if event.change in ["focus", "empty"]:
        asyncio.ensure_future(update_workspace_names(connection, configuration))


async def setup_window_renaming(connection: Connection, configuration: Configuration) -> None:
    await update_workspace_names(connection, configuration)
    connection.on(Event.WINDOW, functools.partial(handle_window_event, configuration))
    connection.on(Event.WORKSPACE, functools.partial(handle_workspace_event, configuration))
