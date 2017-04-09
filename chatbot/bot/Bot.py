# -*- coding: utf-8 -*-

import traceback
import logging
from chatbot import api
from chatbot.util import event, command, plugin
from chatbot.compat import *


class ExitCode(object):
    """Exit codes returned by Bot.run()"""
    Normal = 0
    Error = 1
    Restart = 2


class Bot(object):
    def __init__(self, apiname, stub=False, **kwargs):
        self._running = False
        self._exit = ExitCode.Normal

        self._api = api.create_api_object(apiname, stub, **kwargs)
        self._dispatcher = event.APIEventDispatcher(self._api)
        self._cmdhandler = command.CommandHandler(
            prefix=["!bot","@bot", "!"])
        self._pluginmgr = plugin.PluginManager("plugins")
        self._events = {}

    def init(self):
        """Initialize (attach API, register event handlers, ...)."""
        try:
            logging.info("Initializing...")
            logging.info("{} version {}".format(self._api.api_name(),
                                                self._api.version()))
            logging.info("User handle: " + self._api.get_user().handle())

            logging.info("Attaching API...")
            self._api.attach()

            logging.info("Mounting plugins...")
            self._pluginmgr.mount_all(self._handle_plugin_exc, self)

            logging.info("Done.")
        except:
            logging.error("Failed to initialize.")
            raise

    def quit(self, code=ExitCode.Normal):
        """Gives the signal to stop with the given exit code."""
        logging.info("Shutting down...")
        self._running = False
        self._exit = code

    def run(self):
        """Starts the main loop."""
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

    # Events
    def register_event_handler(self, event, callback, nice=event.EVENT_NORMAL):
        """Register an event handler and return a handle to it.
        
        To unregister call handle.unregister().
        See util.event.APIEventDispatcher for further information.
        """
        return self._dispatcher.register(event, callback, nice)

    # Commands
    def register_command(self, name, callback, argc=1, flags=0):
        """Register a command.

        See util.command.CommandHandler for further information.
        """
        self._cmdhandler.register(name, callback, argc, flags)

    def unregister_command(self, name):
        """Unregister a command.

        See util.command.CommandHandler for further information.
        """
        self._cmdhandler.unregister(name)


    # Utility functions
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
