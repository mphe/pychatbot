# -*- coding: utf-8 -*-

from context import *
import logging

class Plugin(bot.subsystem.async_plugin.BasePlugin):
    def __init__(self, x):
        logging.info("Received parameter x=" + str(x))

    async def init(self, _old_instance):
        logging.info("testplugin.init")

    async def quit(self):
        logging.info("testplugin.quit")
