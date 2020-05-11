# -*- coding: utf-8 -*-

import appdirs
import logging
import os
from typing import List, Iterable
import chatbot
from chatbot import api
from chatbot.util import merge_dicts
from chatbot.util.config import ConfigManager, Config
from .subsystem import APIEventDispatcher
from .subsystem.command import CommandError, CommandHandler
from .subsystem.plugin import PluginManager


CONFIG_DIR = appdirs.user_config_dir("pychatbot")


class ExitCode:
    """Exit codes returned by Bot.run()"""
    Normal = 0
    Error = 1
    Restart = 42  # Use a higher value so it stands out from usual exitcodes


class Bot:
    def __init__(self, profiledir=""):
        self._exit = ExitCode.Normal
        self._config = None  # type: Config
        self._api = None  # type: api.APIBase
        self._dispatcher = None  # type: APIEventDispatcher
        self._cmdhandler = None  # type: CommandHandler
        self._pluginmgr = None  # type: PluginManager

        if profiledir:
            self._cfgmgr = ConfigManager(profiledir)
            logging.info("Using custom profile directory: %s", profiledir)
        else:
            self._cfgmgr = ConfigManager(CONFIG_DIR)
            logging.info("Using default profile directory: %s", CONFIG_DIR)

    async def close(self, code=ExitCode.Normal) -> None:
        """Gives the signal to stop with the given exit code."""
        logging.info("Shutting down...")
        await self._api.close()
        self._exit = code

    def init(self, profile="", apiname="", namespace="", api_kwargs: dict = None) -> None:
        """Run initialization or throw Exception if something fails.

        Args:
            profile: A profile name to load.
            apiname: An API to load.
            api_kwargs: Dictionary of API options passed to the API object.

        If neither `profile` nor `apiname` is specified, the initialization fails.
        """
        # NOTE: init() is a separate function and not included in run()
        # so that it's possible to register some custom handlers before
        # starting the main loop.
        # See echobot test.
        try:
            self._init(profile, apiname, namespace, api_kwargs)
        except Exception as e:
            logging.exception(e)
            logging.error("Failed to initialize.")
            raise

    async def run(self) -> int:
        """Run the main loop, including cleanup afterwards.

        Returns an exit code. See `ExitCode` class.
        """
        logging.info("Running API...")
        try:
            await self._api.run()
        finally:
            logging.info("Exiting...")
            self._cleanup()

        logging.info("Exited with code %s", str(self._exit))
        return self._exit

    def is_admin(self, userid: str) -> bool:
        return userid in self.get_admins()

    def get_admins(self) -> List[str]:
        assert self._config["admins"] == self._cmdhandler._admins
        return self._config["admins"]

    def get_api(self) -> api.APIBase:
        """Returns the API object."""
        return self._api

    def get_configmgr(self) -> ConfigManager:
        return self._cfgmgr

    # Wrappers
    # TODO: Consider using some hacks to set the docstrings to the wrapped
    #       functions' docstring.

    def register_event_handler(self, event: str, callback, nice=0):
        """Register an event handler and return a handle to it.

        To unregister call handle.unregister().
        See bot.subsystem.APIEventDispatcher for further information.
        """
        return self._dispatcher.register(event, callback, nice)

    def mount_plugin(self, name: str) -> None:
        self._pluginmgr.mount_plugin(name, self)

    def unmount_plugin(self, name: str) -> None:
        self._pluginmgr.unmount_plugin(name)

    def reload_plugin(self, name: str) -> None:
        self._pluginmgr.reload_plugin(name)

    def iter_plugins(self) -> Iterable["chatbot.bot.BotPlugin"]:
        return self._pluginmgr.iter_plugins()

    def register_command(self, name, callback, argc=1, flags=0) -> None:
        """Register a command.

        See bot.subsystem.command.CommandHandler for further information.
        """
        self._cmdhandler.register(name, callback, argc, flags)

    def unregister_command(self, *names) -> None:
        """Unregister one or more commands.

        See bot.subsystem.command.CommandHandler for further information.
        """
        for i in names:
            self._cmdhandler.unregister(i)

    # Callbacks
    async def _on_ready(self) -> None:
        displayname = self._config["display_name"]
        if displayname:
            logging.info("Setting display name to: %s", displayname)
            await self._api.set_display_name(displayname)

        logging.info(str(self._api))
        user = await self._api.get_user()
        logging.info("User handle: %s", user.id())
        logging.info("Display name: %s", user.display_name())
        logging.info("Ready!")

    async def _handle_command(self, msg) -> None:
        try:
            if not await self._cmdhandler.execute(msg) and self._config["echo"]:
                await msg.get_chat().send_message("Echo: " + msg.get_text())
        except Exception as e:
            if not isinstance(e, CommandError):
                self._handle_plugin_exc("", e)
            await msg.get_chat().send_message("Error: " + str(e))

    @staticmethod
    async def _autoaccept(request) -> None:
        await request.accept()
        logging.info("Accepted friend request from \"%s\" (%s)",
                     request.get_author().display_name(),
                     request.get_author().id())

    @staticmethod
    async def _autojoin(invite) -> None:
        await invite.accept()
        logging.info("Accepted group invite from \"%s\" (%s)",
                     invite.get_author().display_name(),
                     invite.get_author().id())

    @staticmethod
    async def _autoleave(chat, _user) -> None:
        if chat.size() == 1:
            logging.info("Leaving group after last user left (%s)", chat.id())
            await chat.leave()

    # Utility functions
    def _load_config(self, profile="", apiname="", namespace="", api_kwargs: dict = None) -> None:
        if not apiname and not profile:
            raise ValueError("No API and no profile specified")

        cfg = self._cfgmgr.get_config(profile)
        cfg.load(self._get_default_config())

        # Apply custom settings and overwrite existing
        if namespace:
            cfg["namespace"] = namespace

        if apiname:
            cfg["api"] = apiname
        elif not cfg["api"]:
            raise ValueError("No API specified")

        if api_kwargs:
            merge_dicts(cfg["api_config"], api_kwargs, True)

        # Save if new profile
        if profile and not cfg.exists():
            # Add API specific defaults
            merge_dicts(cfg["api_config"],
                        api.get_api_class(cfg["api"]).get_default_options())
            cfg.write()

        if cfg["namespace"]:
            self._cfgmgr.set_searchpath(
                os.path.join(self._cfgmgr.get_searchpath(), cfg["namespace"]))
            logging.info("Using custom config directory: %s", cfg["namespace"])

        self._config = cfg

    def _init(self, profile="", apiname="", namespace="", api_kwargs: dict = None) -> None:
        logging.info("Initializing...")
        logging.info("Loading configs")
        self._load_config(profile, apiname, namespace, api_kwargs)

        self._cmdhandler = CommandHandler(self._config["prefix"], self._config["admins"])
        self._pluginmgr = PluginManager(
            os.path.dirname(chatbot.bot.plugins.__file__),
            whitelist=self._config["plugins"]["whitelist"],
            blacklist=self._config["plugins"]["blacklist"])

        logging.info("Preparing API...")
        self._api = api.create_api_object(
            self._config["api"], **self._config["api_config"])

        self._dispatcher = APIEventDispatcher(self._api, self._handle_event_exc)
        self._dispatcher.register(api.APIEvents.Message, self._handle_command)
        self._dispatcher.register(api.APIEvents.Ready, self._on_ready)

        if self._config["autoaccept_friend"]:
            self._dispatcher.register(api.APIEvents.FriendRequest, self._autoaccept)
        if self._config["autoaccept_invite"]:
            self._dispatcher.register(api.APIEvents.GroupInvite, self._autojoin)
        if self._config["autoleave"]:
            self._dispatcher.register(api.APIEvents.GroupMemberLeave, self._autoleave)

        logging.info("Mounting plugins...")
        self._pluginmgr.mount_all(self._handle_plugin_exc, self)

        logging.info("Done")

    def _cleanup(self) -> None:
        """Performs actual cleanup after exiting the main loop."""
        logging.info("Umounting plugins...")
        self._pluginmgr.unmount_all(self._handle_plugin_exc)

        logging.info("Unregistering commands...")
        self._cmdhandler.clear()

        logging.info("Unregistering event handlers...")
        self._dispatcher.clear()

    @staticmethod
    def _handle_plugin_exc(name, exc) -> bool:
        logging.exception(exc)
        logging.debug("Plugin: %s", name)
        return True

    @staticmethod
    def _handle_event_exc(event, exc, *args, **kwargs) -> bool:
        logging.exception(exc)
        logging.debug("Event: %s\nargs: %s\nkwargs: %s", event, args, kwargs)
        return True

    @staticmethod
    def _get_default_config():
        return {
            "api": "",
            "api_config": {
                "stub": False,
            },
            "plugins": {
                "whitelist": [],
                "blacklist": [
                    "groupbot",
                ],
            },
            "namespace": "",
            "prefix": [ "!bot", "@bot", "!" ],
            "admins": [],
            "display_name": "Bot",
            "echo": False,
            "autoaccept_friend": True,
            "autoaccept_invite": True,
            "autoleave": False,
        }
