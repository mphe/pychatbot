# -*- coding: utf-8 -*-

from typing import List
from .subsystem.async_plugin import BasePlugin
import chatbot  # Used for type hints, pylint: disable=unused-import
from chatbot.util import event, config, Storage
from chatbot.bot import command
from inspect import getfile
import os


class BotPlugin(BasePlugin):
    def __init__(self, bot: "chatbot.bot.Bot"):
        super().__init__()
        self.__name: str = os.path.splitext(os.path.basename(getfile(self.__class__)))[0]
        self.__bot: "chatbot.bot.Bot" = bot
        self.__cfg = bot.profile.get_plugin_config(self.name)
        self.__storage = bot.profile.get_plugin_storage(self.name)

        # Keep track of registered commands and event handlers to unregister them automatically
        self.__commands: List[str] = []
        self.__handles: List[event.Handle] = []

        self.bot.register_event_handler(chatbot.api.APIEvents.Ready, self._on_ready)

    async def init(self, _old_instance: BasePlugin) -> bool:
        await self.reload()

        if self.bot.api.is_ready:
            await self._on_ready()
        return True

    async def _on_ready(self) -> None:
        """Called when the API becomes ready or, if it already is, after reload() finished."""

    async def reload(self):
        """Reloads the plugin configuration. Called by BotPlugin.init() automatically."""
        self.cfg.load(self.get_default_config(), create=True)
        self.storage.load()

    def save_config(self):
        self.cfg.write()
        self.storage.write()

    async def quit(self):
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

    @property
    def storage(self) -> Storage:
        return self.__storage

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
