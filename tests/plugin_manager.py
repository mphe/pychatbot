#!/usr/bin/env python
# -*- coding: utf-8 -*-

from context import *
import logging
import asyncio


def handle_exception(name: str, _e: Exception):
    if name == "failingplugin":
        logging.info("\"failingplugin\" failed to load (as expected)")
        return True
    return False


async def main() -> None:
    pm = bot.subsystem.async_plugin.PluginManager("./plugins")

    await pm.mount_plugin("testplugin", 42)
    assert pm.plugin_exists("testplugin")

    await pm.unmount_plugin("testplugin")
    assert not pm.plugin_exists("testplugin")

    await pm.mount_all(handle_exception, 42)
    assert pm.plugin_exists("testplugin")
    assert not pm.plugin_exists("failingplugin")

    await pm.unmount_all(handle_exception)
    assert not pm.plugin_exists("testplugin")
    assert not pm.plugin_exists("failingplugin")


if __name__ == "__main__":
    asyncio.run(main())
