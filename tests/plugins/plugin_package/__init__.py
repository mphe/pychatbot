# -*- coding: utf-8 -*-

from chatbot.bot.subsystem.async_plugin import BasePlugin
import logging


class Plugin(BasePlugin):
    def __init__(self, *_args, **_kwargs):
        super().__init__()

    async def init(self, _old_instance):
        logging.info("plugin_package.init")

    async def quit(self):
        logging.info("plugin_package.quit")
