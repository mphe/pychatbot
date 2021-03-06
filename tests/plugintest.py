#!/usr/bin/env python
# -*- coding: utf-8 -*-

from context import *
import logging


def handle_exception(name, e):
    if name == "failingplugin":
        logging.info("\"failingplugin\" failed to load (as expected)")
        return True
    else:
        return False


pm = bot.subsystem.plugin.PluginManager("./plugins")
pm.mount_plugin("testplugin", 42)
pm.reload_plugin("testplugin")
pm.unmount_plugin("testplugin")
pm.mount_all(handle_exception, 42)
pm.unmount_all(handle_exception)
