# -*- coding: utf-8 -*-

from .subsystem.plugin import BasePlugin
from chatbot.util import event
from chatbot.bot import command, Bot
from inspect import getfile
import os


class BotPlugin(BasePlugin):
    def __init__(self, oldme, bot):
        super(BotPlugin, self).__init__(oldme, bot)
        self.__name = os.path.splitext(os.path.basename(getfile(self.__class__)))[0]  # type: str
        self.__bot = bot  # type: Bot
        self.__commands = []  # keeps track of registered commands to unregister them automatically
        self.__handles = []  # keeps track of registered event handlers
        self._cfg = {}  # holds config, protected to allow custom loading
        self.reload()

    def reload(self):
        self._cfg = self.bot().get_configmgr().load(self.name(), self.get_default_config(), create=True)

    def save_config(self):
        self._cfg = self.bot().get_configmgr().write(self.name(), self.cfg())

    def quit(self):
        self.bot().unregister_command(*self.__commands)
        for i in self.__handles:
            i.unregister()

    @staticmethod
    def get_default_config():
        """Returns a dictionary with options and their default values for this plugin."""
        return {}

    def bot(self):
        return self.__bot

    def name(self):
        return self.__name

    def cfg(self):
        return self._cfg

    def register_command(self, name, callback, argc=1, flags=0):
        """Wrapper around Bot.register_command"""
        self.bot().register_command(name, callback, argc, flags)
        self.__commands.append(name)

    def register_admin_command(self, name, callback, argc=1, flags=0):
        """Same as register_command() but with CMDFLAG_ADMIN flag set."""
        self.register_command(name, callback, argc, flags | command.CMDFLAG_ADMIN)

    def register_event_handler(self, evname, callback, nice=event.EVENT_NORMAL):
        """Wrapper around Bot.register_event_handler"""
        self.__handles.append(
            self.bot().register_event_handler(evname, callback, nice))
