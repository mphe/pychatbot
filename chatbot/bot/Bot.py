# -*- coding: utf-8 -*-

import logging
import os
from typing import Iterable, Tuple, cast
import chatbot
from chatbot import api
from chatbot.util import config
from .subsystem import APIEventDispatcher, command
from .subsystem.async_plugin import PluginManager
from . import BotProfile


class ExitCode:
    """Exit codes returned by Bot.run()"""
    Normal = 0
    Error = 1
    Restart = 42  # Use a higher value so it stands out from usual exitcodes
    RestartGitPull = 50  # ^


class Bot:
    def __init__(self, profile: BotProfile):
        self._exit = ExitCode.Normal
        self._profile = profile
        self._config: config.Config = None
        self._api: api.APIBase = None
        self._dispatcher: APIEventDispatcher = None
        self._cmdhandler: command.CommandHandler = None
        self._pluginmgr: PluginManager = None

    async def close(self, code=ExitCode.Normal) -> None:
        """Gives the signal to stop with the given exit code."""
        logging.info("Received exit code %s, closing API...", code)
        self._exit = code
        await self._api.close()

    async def init(self) -> None:
        """Run initialization or re-raise Exceptions if something fails."""
        # NOTE: This is a coroutine, because plugins might rely on an asyncio event
        # loop already running.
        #
        # NOTE: init() is a separate function and not included in run()
        # so that it's possible to register some custom handlers before
        # starting the main loop.
        # See echobot test.
        try:
            await self._init()
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
            # At this point, the main loop already exited, hence another
            # api.close() call is not necessary and only leads to more exceptions.
            # Also, for some reason it is not possible to catch KeyboardInterrupt,
            # probably due to some asyncio reasons.
            logging.info("Exiting...")
            await self._cleanup()

        logging.info("Exited with code %s", str(self._exit))
        return self._exit

    def is_admin(self, user: api.User) -> bool:
        return user.id in self.admins

    @property
    def admins(self) -> Iterable[str]:
        """Get user IDs of admins."""
        return self._cmdhandler._admins

    @property
    def api(self) -> api.APIBase:
        """Returns the API object."""
        return self._api

    @property
    def profile(self) -> BotProfile:
        return self._profile

    # Wrappers
    # TODO: Consider using some hacks to set the docstrings to the wrapped
    #       functions' docstring.

    def register_event_handler(self, event: str, callback, nice=0):
        """Register an event handler and return a handle to it.

        To unregister call handle.unregister().
        See bot.subsystem.APIEventDispatcher for further information.
        """
        return self._dispatcher.register(event, callback, nice)

    async def mount_plugin(self, name: str) -> None:
        await self._pluginmgr.mount_plugin(name, self)

    async def unmount_plugin(self, name: str) -> None:
        await self._pluginmgr.unmount_plugin(name)

    def iter_plugins(self) -> Iterable[Tuple[str, "chatbot.bot.BotPlugin"]]:
        return cast(Iterable[Tuple[str, "chatbot.bot.BotPlugin"]], self._pluginmgr.iter_plugins())

    def register_command(self, *args, **kwargs) -> None:
        """Register a command.

        See bot.subsystem.command.CommandHandler for further information.
        """
        self._cmdhandler.register(*args, **kwargs)

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
        logging.info("User handle: %s", user.id)
        logging.info("Display name: %s", user.display_name)
        logging.info("Ready!")

    async def _handle_command(self, msg: chatbot.api.ChatMessage) -> None:
        try:
            if not await self._cmdhandler.execute(msg) and self._config["echo"]:
                await msg.reply("Echo: " + msg.text)
        except command.CommandSyntaxError as e:
            await msg.reply("Error: {}.\nSee `help {}` for usage instructions.".format(e, e.command))
        except command.CommandNotFoundError as e:
            await msg.reply("Error: {}.\nType `list` for a list of available commands.".format(e))
        except Exception as e:
            if not isinstance(e, command.CommandError):
                self._handle_plugin_exc("", e)
            await msg.reply("Error: {}.".format(e))

    @staticmethod
    async def _autoaccept(request: chatbot.api.FriendRequest) -> None:
        await request.accept()
        logging.info("Accepted friend request from \"%s\" (%s)",
                     request.author.display_name,
                     request.author.id)

    @staticmethod
    async def _autojoin(invite: chatbot.api.GroupInvite) -> None:
        await invite.accept()
        logging.info("Accepted group invite from \"%s\" (%s)",
                     invite.author.display_name,
                     invite.author.id)

    @staticmethod
    async def _autoleave(chat: chatbot.api.GroupChat, _user: chatbot.api.User) -> None:
        if chat.size == 1:
            logging.info("Leaving group after last user left (%s)", chat.id)
            await chat.leave()

    # Utility functions
    async def _init(self) -> None:
        logging.info("Initializing...")
        logging.info("Loading configs")

        self._config = self._profile.get_bot_config()
        self._config.load(self.get_default_config())

        self._cmdhandler = command.CommandHandler(
            prefix=self._config["prefix"],
            admins=self._config["admins"],
            history_size=int(self._config["cmd_history_size"]))

        self._pluginmgr = PluginManager(
            os.path.dirname(chatbot.bot.plugins.__file__),
            whitelist=self._config["plugin_whitelist"],
            blacklist=self._config["plugin_blacklist"])

        logging.info("Preparing API...")
        apicfg = self._profile.get_api_config().load()
        self._api = api.create_api_object(self._config["api"], apicfg.data)

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
        await self._pluginmgr.mount_all(self._handle_plugin_exc, self)

        logging.info("Done")

    async def _cleanup(self) -> None:
        """Performs actual cleanup after exiting the main loop."""
        logging.info("Umounting plugins...")
        await self._pluginmgr.unmount_all(self._handle_plugin_exc)

        logging.info("Unregistering commands...")
        self._cmdhandler.clear()

        logging.info("Unregistering event handlers...")
        self._dispatcher.clear()

    @staticmethod
    def _handle_plugin_exc(name, exc) -> bool:
        logging.error("Exception in plugin: %s", name)
        logging.exception(exc)
        return True

    @staticmethod
    def _handle_event_exc(event: str, exc: Exception) -> bool:
        logging.error("Exception in event: %s", event)
        logging.exception(exc)
        return True

    @staticmethod
    def get_default_config():
        return {
            "api": "",  # This key is also used in BotProfileManager
            "plugin_whitelist": [],
            "plugin_blacklist": [ "gw2" ],
            "prefix": [ "!bot", "@bot", "!" ],
            "admins": [],
            "display_name": "Bot",
            "echo": False,
            "autoaccept_friend": True,
            "autoaccept_invite": True,
            "autoleave": False,
            "cmd_history_size": 5,
        }
