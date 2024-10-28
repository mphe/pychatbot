# -*- coding: utf-8 -*-

from chatbot.bot.subsystem.async_plugin import BasePlugin


# Create error on purpose by not implementing any methods
class Plugin(BasePlugin):  # pylint: disable=abstract-method
    pass
