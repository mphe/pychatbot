# -*- coding: utf-8 -*-

from chatbot.bot.subsystem.async_plugin import BasePlugin
import logging


class Plugin(BasePlugin):
    def __init__(self, x):
        logging.info("Received parameter x=%s", str(x))

    async def init(self, _old_instance):
        logging.info("testplugin.init")

    async def quit(self):
        logging.info("testplugin.quit")
