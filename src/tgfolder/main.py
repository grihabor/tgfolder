import asyncio
from typing import Optional, List

import click
from tgfolder.lib import (
    async_command_user_list,
    async_command_list,
    async_command_common_chat_list,
    async_command_include_peers_group_add,
)

config_path_option = click.option("-c", "--config", default=None)


@click.group()
def main_group():
    pass


@main_group.command(name="list")
@config_path_option
def command_list(config: Optional[str]):
    asyncio.run(async_command_list(config))


@main_group.group(name="include_peers")
def include_peers_group():
    pass


@include_peers_group.command(name="add")
@config_path_option
@click.option("-t", "--title", required=True)
@click.option("--dry-run/--exec", default=True)
@click.argument("chat_ids", nargs=-1, type=click.INT)
def command_include_peers_group_add(
    config: Optional[str], title: str, chat_ids: List[int], dry_run: bool
):
    asyncio.run(
        async_command_include_peers_group_add(
            config, folder_title=title, chat_ids=chat_ids, dry_run=dry_run
        )
    )


@main_group.command(name="common_chat_list")
@config_path_option
@click.argument("user_ids", nargs=-1, type=click.INT)
def command_common_chats(config: Optional[str], user_ids: List[int]):
    asyncio.run(async_command_common_chat_list(config, user_ids))


@include_peers_group.command(name="list")
@config_path_option
@click.option("-t", "--title", required=True)
def command_user_list(config: Optional[str], title):
    asyncio.run(async_command_user_list(config, folder_title=title))


def main():
    main_group()


if __name__ == "__main__":
    main()
