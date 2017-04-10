# -*- coding: utf-8 -*-

import traceback
import logging
from chatbot import api
from chatbot.api import APIEvents
from chatbot.util import event, merge_dicts
from .subsystem import APIEventDispatcher, command, plugin, ConfigManager
from chatbot.compat import *


class ExitCode(object):
    """Exit codes returned by Bot.run()"""
    Normal = 0
    Error = 1
    Restart = 2


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


    # Wrappers
    # TODO: Consider using some hacks to set the docstrings to the wrapped
    #       functions' docstring.

    # Plugins
    def mount_plugin(self, name):
        self._pluginmgr.mount_plugin(name, self)

    def unmount_plugin(self, name):
        self._pluginmgr.unmount_plugin(name)

    def reload_plugin(self, name):
        self._pluginmgr.reload_plugin(name)

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

    def unregister_command(self, name):
        """Unregister a command.

        See bot.subsystem.command.CommandHandler for further information.
        """
        self._cmdhandler.unregister(name)


    # Callbacks
    def _echo(self, msg):
        msg.get_chat().send_message("Echo: " + msg.get_text())

    def _autoaccept(self, request):
        request.accept()


    # Utility functions
    def _load_config(self, profile="", apiname="", **kwargs):
        if not apiname and not profile:
            raise ValueError("No API and no profile specified")

        # Load default or existing config
        cfg = self._get_default_config()
        if profile:
            cfg = self._cfgmgr.load(profile, cfg)

        # Apply custom settings and overwrite existing
        if apiname:
            cfg["api"] = apiname
        elif not cfg["api"]:
            raise ValueError("No API specified")

        merge_dicts(cfg["api_config"],
                    api.get_api_class(cfg["api"]).get_default_options())
        if kwargs:
            merge_dicts(cfg["api_config"], kwargs, True)

        # Create the profile if it doesn't exist yet
        if profile:
            self._cfgmgr.create(profile, cfg)
        return cfg

    def _init(self, profile="", apiname="", **kwargs):
        logging.info("Initializing...")
        logging.info("Loading configs")
        self._config = self._load_config(profile, apiname, **kwargs)

        self._cmdhandler = command.CommandHandler(self._config["prefix"])
        self._pluginmgr = plugin.PluginManager(self._config["plugin_path"])

        logging.info("Mounting plugins...")
        self._pluginmgr.mount_all(self._handle_plugin_exc, self)

        logging.info("Loading API...")
        self._api = api.create_api_object(self._config["api"],
                                          **self._config["api_config"])
        self._dispatcher = APIEventDispatcher(self._api)

        if self._config["echo"]:
            self._dispatcher.register(APIEvents.Message, self._echo)
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
        logging.info("Unregistering commands...")
        self._cmdhandler.clear()

        logging.info("Unregistering event handlers...")
        self._dispatcher.clear()

        logging.info("Umounting plugins...")
        self._pluginmgr.unmount_all(self._handle_plugin_exc)

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
            "plugin_path": "plugins",
            "prefix": [ "!bot","@bot", "!" ],
            "display_name": "Bot",
            "echo": True,
            "autoaccept_friend": True,
        }

