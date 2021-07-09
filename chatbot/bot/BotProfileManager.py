#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import appdirs
from chatbot.util import config
import chatbot

# Profile directory structure
#
# - configpath/ (e.g. ~/.config/pychatbot)
#   |- profileA/
#      |- bot.json
#      |- api.json
#      |- chatbot.log
#      |- plugins/
#         |- pluginA.json
#         |- pluginB.json
#         |- ...
#   |- profileB/
#      |- ...

CONFIG_DIR = appdirs.user_config_dir("pychatbot")
PLUGIN_DIR = "plugins"
BOT_CONFIG_NAME = "bot.json"
API_CONFIG_NAME = "api.json"
LOGFILE_NAME = "chatbot.log"
LOGFILE_NAME_OLD = "chatbot.old.log"


# TODO: Cache Config objects?
class BotProfile:
    """A helper class to access config files.

    It does not manage or load these configs, it just provides means to access
    them in a simple, centralized way.
    """
    def __init__(self, dir_path: str):
        self._manager = config.ConfigManager(dir_path)
        self._log_path = os.path.join(self._manager.get_searchpath(), LOGFILE_NAME)
        self._old_log_path = os.path.join(self._manager.get_searchpath(), LOGFILE_NAME_OLD)

    def get_plugin_config(self, plugin_name: str) -> config.Config:
        return self._manager.get_config(os.path.join(PLUGIN_DIR, plugin_name))

    def get_bot_config(self) -> config.Config:
        return self._manager.get_config(BOT_CONFIG_NAME)

    def get_api_config(self) -> config.Config:
        return self._manager.get_config(API_CONFIG_NAME)

    def get_log_path(self) -> str:
        return self._log_path

    def get_old_log_path(self) -> str:
        return self._old_log_path

    def log_rotate(self):
        if os.path.isfile(self.get_old_log_path()):
            os.remove(self.get_old_log_path())
        if os.path.isfile(self.get_log_path()):
            os.rename(self.get_log_path(), self.get_old_log_path())


class BotProfileManager:
    def __init__(self, config_path: str = CONFIG_DIR):
        self._config_path = config_path

    def create_profile(self, profile_name: str, api_name: str) -> BotProfile:
        """(Re-)Create a bot profile and with default config files."""
        return self._create_profile(self._get_profile_dir(profile_name), api_name)

    def load_or_create(self, profile_name: str, api_name: str = "") -> BotProfile:
        profile_dir = self._get_profile_dir(profile_name)
        if os.path.isdir(profile_dir):
            return BotProfile(profile_dir)
        return self._create_profile(profile_dir, api_name)

    @staticmethod
    def _create_profile(path: str, api_name: str) -> BotProfile:
        if not path:
            raise ValueError("No profile name specified")
        if not api_name:
            raise ValueError("No API specified")

        os.makedirs(path, exist_ok=True)
        os.makedirs(os.path.join(path, PLUGIN_DIR), exist_ok=True)

        profile = BotProfile(path)
        profile.get_api_config().load(chatbot.api.get_api_class(api_name).get_default_options(), validate=True, write=True)
        botcfg = profile.get_bot_config()
        botcfg["api"] = api_name
        botcfg.write()
        botcfg.load(chatbot.bot.Bot.get_default_config(), validate=True, write=True)

        return profile

    def _get_profile_dir(self, profile_name: str) -> str:
        return os.path.join(self._config_path, profile_name)
