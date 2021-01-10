import json
import os
import pathlib
from typing import Optional, List

import click
from pydantic.dataclasses import dataclass
from telethon import TelegramClient
from telethon.sessions import SQLiteSession
from telethon.tl import types
from telethon.tl.functions import messages


async def async_command_user_list(config: Optional[str], target_title: str):
    client = await new_client(config)
    dialog_filters: List[types.DialogFilter] = await client(
        messages.GetDialogFiltersRequest()
    )
    found = [f for f in dialog_filters if f.title == target_title]
    if not found:
        click.echo(f"folder not found: {target_title}", err=True)
        return

    target = found[0]
    echo_json([p.to_dict() for p in target.include_peers])


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


def echo_json(obj):
    click.echo(json.dumps(obj, ensure_ascii=False))


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
