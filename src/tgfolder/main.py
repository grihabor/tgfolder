import asyncio
from typing import Optional, List

import click
from tgfolder.lib import (
    async_command_user_list,
    async_command_list,
    async_command_common_chat_list,
    async_command_include_peers_group_add,
)


@click.group()
def main_group():
    pass


@main_group.command(name="list")
def command_list(config: Optional[str]):
    asyncio.run(async_command_list(config))


@main_group.group(name="include_peers")
def include_peers_group():
    pass


@include_peers_group.command(name="add")
@click.option("-t", "--title", required=True)
@click.option("--dry-run/--exec", default=True)
@click.argument("chat_ids", nargs=-1, type=click.INT)
def command_include_peers_group_add(title: str, chat_ids: List[int], dry_run: bool):
    asyncio.run(
        async_command_include_peers_group_add(
            folder_title=title, chat_ids=chat_ids, dry_run=dry_run
        )
    )


@main_group.command(name="common_chat_list")
@click.argument("user_ids", nargs=-1, type=click.INT)
def command_common_chats(user_ids: List[int]):
    asyncio.run(async_command_common_chat_list(user_ids))


@include_peers_group.command(name="list")
@click.option("-t", "--title", required=True)
def command_user_list(title: str):
    asyncio.run(async_command_user_list(folder_title=title))


def main():
    main_group()


if __name__ == "__main__":
    main()
