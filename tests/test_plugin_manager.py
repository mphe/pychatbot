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
        await self._mount_and_unmount_plugin("testplugin", 42)

    async def test_mount_package(self):
        await self._mount_and_unmount_plugin("plugin_package")

    async def test_mount_ignored(self):
        # These are ignored by mount_all() but can be mounted manually.
        await self._mount_and_unmount_plugin("_ignored_plugin")
        await self._mount_and_unmount_plugin(".ignored_plugin")

    async def test_mount_all(self):
        await self.pm.mount_all(handle_exception, 42)
        self.assertTrue(self.pm.plugin_exists("testplugin"))
        self.assertTrue(self.pm.plugin_exists("plugin_package"))
        self.assertFalse(self.pm.plugin_exists("failingplugin"))
        self.assertFalse(self.pm.plugin_exists(".ignored_plugin"))
        self.assertFalse(self.pm.plugin_exists("_ignored_plugin"))
        self.assertFalse(self.pm.plugin_exists("asdfasdfasfd"))

        await self.pm.unmount_all(handle_exception)
        self.assertFalse(self.pm.plugin_exists("testplugin"))
        self.assertFalse(self.pm.plugin_exists("plugin_package"))
        self.assertFalse(self.pm.plugin_exists("failingplugin"))

    async def _mount_and_unmount_plugin(self, name: str, *args):
        await self.pm.mount_plugin(name, *args)
        plugin = self.pm.get_plugin(name)
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.name, name)
        self.assertTrue(self.pm.plugin_exists(name))

        await self.pm.unmount_plugin(name)
        self.assertFalse(self.pm.plugin_exists(name))
        self.assertIsNone(self.pm.get_plugin(name))


if __name__ == "__main__":
    unittest.main()
