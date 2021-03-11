# -*- coding: utf-8 -*-

from typing import List
from .subsystem.plugin import BasePlugin
import chatbot  # Used for type hints, pylint: disable=unused-import
from chatbot.util import event, config
from chatbot.bot import command
from inspect import getfile
import os


class BotPlugin(BasePlugin):
    def __init__(self, oldme, bot: "chatbot.bot.Bot"):
        super().__init__(oldme, bot)
        self.__name: str = os.path.splitext(os.path.basename(getfile(self.__class__)))[0]
        self.__bot: "chatbot.bot.Bot" = bot
        self.__cfg = bot.config_manager.get_config(self.name)

        # Keep track of registered commands and event handlers to unregister them automatically
        self.__commands: List[str] = []
        self.__handles: List[event.Handle] = []

        self.reload()

    def reload(self):
        self.cfg.load(self.get_default_config(), create=True)

    def save_config(self):
        self.cfg.write()

    def quit(self):
        self.bot.unregister_command(*self.__commands)
        for i in self.__handles:
            i.unregister()

    @staticmethod
    def get_default_config():
        """Returns a dictionary with options and their default values for this plugin."""
        return {}

    @property
    def bot(self) -> "chatbot.bot.Bot":
        return self.__bot

    @property
    def name(self) -> str:
        return self.__name

    @property
    def cfg(self) -> config.Config:
        return self.__cfg

    def register_command(self, name, callback, argc=1, flags=0, types=()):
        """Wrapper around Bot.register_command"""
        self.bot.register_command(name, callback, argc, flags, types)
        self.__commands.append(name)

    def register_command_expand(self, name, callback, argc=1, flags=0, types=()):
        """Wrapper around Bot.register_command with CommandFlag.Expand flag set"""
        self.register_command(name, callback, argc, flags | command.CommandFlag.Expand, types)

    def register_admin_command(self, name, callback, argc=1, flags=0, types=()):
        """Same as register_command() but with CMDFLAG_ADMIN flag set."""
        self.register_command(name, callback, argc, flags | command.CommandFlag.Admin, types)

    def register_event_handler(self, evname, callback, nice=event.EVENT_NORMAL):
        """Wrapper around Bot.register_event_handler"""
        self.__handles.append(
            self.bot.register_event_handler(evname, callback, nice))
