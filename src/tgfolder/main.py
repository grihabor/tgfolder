import asyncio
import json
import os
import pathlib
from typing import Optional, List

import click
from telethon import TelegramClient
from pydantic.dataclasses import dataclass
from telethon.tl.functions import messages
from telethon.tl import types
from telethon.sessions import SQLiteSession


@click.group()
def main():
    pass


@main.command(name="list")
@click.option("-c", "--config", default=None)
def command_list(config: Optional[str]):
    asyncio.run(async_command_list(config))


def get_workdir() -> str:
    return os.path.join(os.environ["HOME"], ".tgfolder")


async def async_command_list(config: Optional[str]):
    if config is None:
        config = os.path.join(get_workdir(), "config.json")
    cfg = load_config(config)
    session = await new_session(os.path.join(get_workdir(), "session"))
    client = TelegramClient(session, api_id=cfg.api_id, api_hash=cfg.api_hash)
    client = await client.start(phone=cfg.phone)
    dialog_filters: List[types.DialogFilter] = await client(
        messages.GetDialogFiltersRequest()
    )
    click.echo(json.dumps([item.title for item in dialog_filters], ensure_ascii=False))


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


if __name__ == "__main__":
    main()
