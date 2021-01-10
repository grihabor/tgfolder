import asyncio
from typing import Optional

import click
from tgfolder.lib import async_command_user_list, async_command_list

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


@include_peers_group.command(name="list")
@config_path_option
@click.option("-t", "--title", required=True)
def command_user_list(config: Optional[str], title):
    asyncio.run(async_command_user_list(config, target_title=title))


def main():
    main_group()


if __name__ == "__main__":
    main()
