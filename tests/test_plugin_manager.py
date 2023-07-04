#!/usr/bin/env python
# -*- coding: utf-8 -*-

from context import bot
import logging
import unittest


def handle_exception(name: str, _e: Exception):
    if name == "failingplugin":
        logging.info("\"failingplugin\" failed to load (as expected)")
        return True
    return False


class Test(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.pm = bot.subsystem.async_plugin.PluginManager("./plugins")

    async def asyncTearDown(self):
        await self.pm.unmount_all(None)
        del self.pm

    async def test_mount(self):
        await self.pm.mount_plugin("testplugin", 42)
        self.assertTrue(self.pm.plugin_exists("testplugin"))

        await self.pm.unmount_plugin("testplugin")
        self.assertFalse(self.pm.plugin_exists("testplugin"))

    async def test_mount_all(self):
        await self.pm.mount_all(handle_exception, 42)
        self.assertTrue(self.pm.plugin_exists("testplugin"))
        self.assertFalse(self.pm.plugin_exists("failingplugin"))

        await self.pm.unmount_all(handle_exception)
        self.assertFalse(self.pm.plugin_exists("testplugin"))
        self.assertFalse(self.pm.plugin_exists("failingplugin"))


if __name__ == "__main__":
    unittest.main()
