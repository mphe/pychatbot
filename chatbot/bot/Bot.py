# -*- coding: utf-8 -*-

import traceback
import logging
import os
import chatbot
from chatbot import api
from chatbot.api import APIEvents
from chatbot.util import event, merge_dicts
from .subsystem import APIEventDispatcher, command, plugin, ConfigManager
from chatbot.compat import *


class ExitCode(object):
    """Exit codes returned by Bot.run()"""
    Normal = 0
    Error = 1
    Restart = 42  # Use a higher value so it stands out from usual exitcodes


class Bot(object):
    def __init__(self, configdir="config"):
        self._running = False
        self._exit = ExitCode.Normal

        self._config = {}
        self._cfgmgr = ConfigManager(configdir)
        self._api = None
        self._dispatcher = None
        self._cmdhandler = None
        self._pluginmgr = None

    def quit(self, code=ExitCode.Normal):
        """Gives the signal to stop with the given exit code."""
        logging.info("Shutting down...")
        self._running = False
        self._exit = code

    def run(self, profile="", apiname="", **kwargs):
        """Initialize and start the main loop.
        
        profile: a profile config to load
        apiname: an API to load
        kwargs: arguments passed to the API

        If neither profile nor apiname is specified, the initialization fails.
        """

        try:
            self._init(profile, apiname, **kwargs)
        except:
            logging.error("Failed to initialize.")
            raise

        self._running = True
        # TODO: handle SIGTERM
        try:
            while self._running:
                self._api.iterate()
        except (KeyboardInterrupt, SystemExit) as e:
            logging.info(repr(e))
            self.quit()
        finally:
            self._cleanup()

        logging.info("Exited with code " + str(self._exit))
        return self._exit

    def reload(self):
        raise NotImplementedError

    def is_admin(self, userhandle):
        return userhandle in self.get_admins()

    def get_admins(self):
        assert self._config["admins"] == self._cmdhandler._admins
        return self._config["admins"]


    # Wrappers
    # TODO: Consider using some hacks to set the docstrings to the wrapped
    #       functions' docstring.

    def mount_plugin(self, name):
        self._pluginmgr.mount_plugin(name, self)

    def unmount_plugin(self, name):
        self._pluginmgr.unmount_plugin(name)

    def reload_plugin(self, name):
        self._pluginmgr.reload_plugin(name)

    def iter_plugins(self):
        return self._pluginmgr.iter_plugins()


    def register_event_handler(self, event, callback, nice=event.EVENT_NORMAL):
        """Register an event handler and return a handle to it.
        
        To unregister call handle.unregister().
        See bot.subsystem.APIEventDispatcher for further information.
        """
        return self._dispatcher.register(event, callback, nice)


    def register_command(self, name, callback, argc=1, flags=0):
        """Register a command.

        See bot.subsystem.command.CommandHandler for further information.
        """
        self._cmdhandler.register(name, callback, argc, flags)
        logging.debug("Registered command: " + name)

    def register_admin_command(self, name, callback, argc=1, flags=0):
        """Same as register_command() but with CMDFLAG_ADMIN flag set."""
        self.register_command(name, callback, argc, flags | command.CMDFLAG_ADMIN)

    def unregister_command(self, *names):
        """Unregister one or more commands.

        See bot.subsystem.command.CommandHandler for further information.
        """
        for i in names:
            self._cmdhandler.unregister(i)
            logging.debug("Unregistered command: " + i)


    # Callbacks
    def _handle_command(self, msg):
        try:
            if not self._cmdhandler.execute(msg) and self._config["echo"]:
                msg.get_chat().send_message("Echo: " + msg.get_text())
        except Exception as e:
            if not isinstance(e, command.CommandError):
                self._handle_plugin_exc("", e)
            msg.get_chat().send_message("Error: " + str(e))

    def _autoaccept(self, request):
        request.accept()
        logging.info("Accepted friend request from \"{}\" ({})".format(
            request.get_author().display_name(),
            request.get_author().handle()))


    # Utility functions
    def _load_config(self, profile="", apiname="", **kwargs):
        if not apiname and not profile:
            raise ValueError("No API and no profile specified")

        newprofile = False

        # Load default or existing config
        cfg = self._get_default_config()
        if profile:
            if not self._cfgmgr.exists(profile):
                newprofile = True
            # Read config and update defaults
            cfg = self._cfgmgr.load_update(profile, cfg)

        # Apply custom settings and overwrite existing
        if apiname:
            cfg["api"] = apiname
        elif not cfg["api"]:
            raise ValueError("No API specified")

        merge_dicts(cfg["api_config"],
                    api.get_api_class(cfg["api"]).get_default_options())
        if kwargs:
            merge_dicts(cfg["api_config"], kwargs, True)

        # Update the profile (with applied settings)
        if newprofile:
            self._cfgmgr.write(profile, cfg)
        self._config = cfg

    def _init(self, profile="", apiname="", **kwargs):
        logging.info("Initializing...")
        logging.info("Loading configs")
        self._load_config(profile, apiname, **kwargs)

        self._cmdhandler = command.CommandHandler(
            self._config["prefix"], self._config["admins"])
        self._pluginmgr = plugin.PluginManager(self._config["plugin_path"])

        logging.info("Mounting plugins...")
        self._pluginmgr.mount_all(self._handle_plugin_exc, self)

        logging.info("Loading API...")
        self._api = api.create_api_object(self._config["api"],
                                          **self._config["api_config"])

        self._dispatcher = APIEventDispatcher(self._api)
        self._dispatcher.register(APIEvents.Message, self._handle_command)
        if self._config["autoaccept_friend"]:
            self._dispatcher.register(APIEvents.FriendRequest, self._autoaccept)

        logging.info("Attaching API...")
        self._api.attach()

        if self._config["display_name"]:
            self._api.set_display_name(self._config["display_name"])

        logging.info(str(self._api))
        logging.info("User handle: " + self._api.get_user().handle())
        logging.info("Display name: " + self._api.get_user().display_name())

        logging.info("Done")

    def _cleanup(self):
        """Performs actual cleanup after exiting the main loop."""
        logging.info("Umounting plugins...")
        self._pluginmgr.unmount_all(self._handle_plugin_exc)

        logging.info("Unregistering commands...")
        self._cmdhandler.clear()

        logging.info("Unregistering event handlers...")
        self._dispatcher.clear()

        logging.info("Detaching API...")
        self._api.detach()

    def _handle_plugin_exc(self, name, e):
        logging.error(traceback.format_exc())
        return True

    @staticmethod
    def _get_default_config():
        return {
            "api": "",
            "api_config": {
                "stub": False,
            },
            "plugin_path": os.path.dirname(chatbot.bot.plugins.__file__),
            "prefix": [ "!bot","@bot", "!" ],
            "admins": [],
            "display_name": "Bot",
            "echo": True,
            "autoaccept_friend": True,
        }

