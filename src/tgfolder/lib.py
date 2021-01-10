import asyncio
import json
import os
import pathlib
from typing import Optional, List, Any, Dict, Set

import click
from pydantic.dataclasses import dataclass
from telethon import TelegramClient
from telethon.sessions import SQLiteSession
from telethon.tl import types
from telethon.tl.functions import messages, contacts


async def async_command_include_peers_group_add(
    config: Optional[str], folder_title: str, chat_ids: List[int], dry_run: bool
):
    client = await new_client(config)
    dialog_filter = await get_dialog_filter(client, folder_title)
    if dialog_filter is None:
        raise RuntimeError(f"Folder not found: {folder_title}")

    chats_we_want = set(chat_ids)
    chats_already_included = set(
        get_entity_ids(dialog_filter.include_peers)
        + get_entity_ids(dialog_filter.pinned_peers)
    )
    chats_to_add = chats_we_want - chats_already_included

    await client.get_dialogs(ignore_pinned=False)
    entities = await asyncio.gather(
        *[client.get_entity(chat_id) for chat_id in chats_to_add]
    )

    chats = filter_chats(entities)
    channels = filter_channels(entities)

    assert len(channels) + len(chats) == len(
        entities
    ), f"{len(channels)} + {len(chats)} != {len(entities)}"

    echo_json(chats_to_list(chats))
    echo_json(channels_to_list(channels))
    if dry_run:
        return

    peer_chats = [types.InputPeerChat(c.id) for c in chats]
    peer_channels = [types.InputPeerChannel(c.id, c.access_hash) for c in channels]
    dialog_filter.include_peers = (
        dialog_filter.include_peers + peer_chats + peer_channels
    )
    request = messages.UpdateDialogFilterRequest(dialog_filter.id, dialog_filter)
    result = await client(request)
    click.echo(
        f'Added {len(entities)} entries to folder "{folder_title}": {result}', err=True
    )


def filter_chats(entities):
    return [e for e in entities if isinstance(e, types.Chat)]


def filter_channels(entities):
    return [e for e in entities if isinstance(e, types.Channel)]


def filter_users(entities):
    return [e for e in entities if isinstance(e, types.User)]


def chats_to_list(chats: List[types.Chat]) -> List[Dict[str, Any]]:
    return [{"type": "chat", "id": e.id, "title": e.title} for e in chats]


def channels_to_list(channels: List[types.Channel]) -> List[Dict[str, Any]]:
    return [{"type": "channel", "id": e.id, "title": e.title} for e in channels]


def users_to_list(users: List[types.User]) -> List[Dict[str, Any]]:
    return [{"type": "user", "id": e.id, "username": e.username} for e in users]


def get_entity_ids(peers: List[types.TypeInputPeer]) -> List[int]:
    entity_ids = [get_entity_id(peer) for peer in peers]
    result = [entity_id for entity_id in entity_ids if entity_id is not None]
    assert len(peers) == len(result), f"{len(peers)} != {len(result)}"
    return result


def get_entity_id(e: types.TypeInputPeer) -> Optional[int]:
    if isinstance(e, types.InputPeerChat):
        return e.chat_id
    if isinstance(e, (types.InputPeerUser, types.InputPeerUserFromMessage)):
        return e.user_id
    if isinstance(e, (types.InputPeerChannel, types.InputPeerChannelFromMessage)):
        return e.channel_id
    return None


async def async_command_common_chat_list(config: Optional[str], user_ids: List[int]):
    client = await new_client(config)

    async def get_common_chats(user_id: int) -> Set[int]:
        result = await client(
            messages.GetCommonChatsRequest(user_id, max_id=2147483647, limit=100)
        )
        chats: List[types.Chat] = result.chats
        return set(chat.id for chat in chats)

    chat_batches: List[Set[int]] = await asyncio.gather(
        *[get_common_chats(user_id) for user_id in user_ids]
    )
    chat_ids = set()
    for batch in chat_batches:
        chat_ids.update(batch)

    entities = await asyncio.gather(*[client.get_entity(peer) for peer in chat_ids])
    chats = filter_chats(entities)
    channels = filter_channels(entities)
    users = filter_users(entities)

    echo_json(chats_to_list(chats))
    echo_json(channels_to_list(channels))
    echo_json(users_to_list(users))


async def get_dialog_filter(client, title: str) -> Optional[types.DialogFilter]:
    dialog_filters: List[types.DialogFilter] = await client(
        messages.GetDialogFiltersRequest()
    )
    found = [f for f in dialog_filters if f.title == title]
    if not found:
        return

    return found[0]


async def async_command_user_list(config: Optional[str], folder_title: str):
    client = await new_client(config)
    dialog_filter = await get_dialog_filter(client, folder_title)
    if dialog_filter is None:
        click.echo(f"folder not found: {folder_title}", err=True)
        return

    entities = await asyncio.gather(
        *[
            client.get_entity(peer)
            for peer in dialog_filter.include_peers + dialog_filter.pinned_peers
        ]
    )
    chats = filter_chats(entities)
    channels = filter_channels(entities)
    users = filter_users(entities)

    echo_json(chats_to_list(chats))
    echo_json(channels_to_list(channels))
    echo_json(users_to_list(users))


async def new_client(config: Optional[str]):
    workdir = os.path.join(os.environ["HOME"], ".tgfolder")
    if config is None:
        config = os.path.join(workdir, "config.json")
    cfg = load_config(config)
    session = await new_session(os.path.join(workdir, "session"))
    client = TelegramClient(session, api_id=cfg.api_id, api_hash=cfg.api_hash)
    client = await client.start(phone=cfg.phone)
    return client


async def async_command_list(config: Optional[str]):
    client = await new_client(config)
    dialog_filters: List[types.DialogFilter] = await client(
        messages.GetDialogFiltersRequest()
    )
    titles = [item.title for item in dialog_filters]
    echo_json(titles)


def echo_json(arr: List[Any]):
    if len(arr) == 0:
        return
    click.echo("\n".join(json.dumps(s, ensure_ascii=False) for s in arr))


async def new_session(path: str) -> SQLiteSession:
    p = pathlib.Path(path)
    if not p.parent.exists():
        p.parent.mkdir(0o755, parents=True)
    return SQLiteSession(path)


@dataclass
class Config:
    api_id: int
    api_hash: str
    phone: str


def load_config(path: str) -> Config:
    with open(path) as f:
        content = json.load(f)

    return Config(**content)
