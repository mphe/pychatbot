#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import appdirs
from chatbot.util import config
import chatbot
from typing import List

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
    """A helper class to access config files in a simple, centralized way.

    It does not manage, load, or create any files or directories automatically.
    """
    def __init__(self, dir_path: str):
        self._manager = config.ConfigManager(dir_path)
        self._log_path = self._manager.get_file(LOGFILE_NAME)
        self._old_log_path = self._manager.get_file(LOGFILE_NAME_OLD)

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

    def is_profile(self) -> bool:
        """Returns true when the directory appears to be a profile directory."""
        return os.path.isdir(self.get_path()) and self.get_bot_config().exists() and self.get_api_config().exists()

    def get_path(self) -> str:
        return self._manager.get_searchpath()

    def create(self, api_name: str) -> None:
        """Create required files and directories for this profile.

        Raises an exception if something fails.
        """
        if not api_name:
            raise ValueError("No API specified")
        if not os.path.isdir(self.get_path()):
            raise ValueError("Not a directory: " + self.get_path())

        os.makedirs(self.get_path(), exist_ok=True)
        os.makedirs(self._manager.get_file(PLUGIN_DIR), exist_ok=True)

        self.get_api_config().load(chatbot.api.get_api_class(api_name).get_default_options(), validate=True, write=True)
        botcfg = self.get_bot_config()
        botcfg["api"] = api_name
        botcfg.write()
        botcfg.load(chatbot.bot.Bot.get_default_config(), validate=True, write=True)

    def log_rotate(self):
        if os.path.isfile(self.get_old_log_path()):
            os.remove(self.get_old_log_path())
        if os.path.isfile(self.get_log_path()):
            os.rename(self.get_log_path(), self.get_old_log_path())


class BotProfileManager:
    def __init__(self, config_path: str = CONFIG_DIR):
        self._config_path = config_path

    def load_or_create(self, profile_name: str, api_name: str = "") -> BotProfile:
        """Load or (re-)create a bot profile with default config files."""
        profile = self._get_profile(profile_name)
        if not profile.is_profile():
            profile.create(api_name)
        return profile

    def get_profiles(self) -> List[str]:
        return [ i for i in os.listdir(self._config_path) if self._get_profile(i).is_profile() ]

    def _get_profile(self, profile_name: str) -> BotProfile:
        return BotProfile(os.path.join(self._config_path, profile_name))
