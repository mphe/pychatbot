# -*- coding: utf-8 -*-

import time
import logging
from functools import partial
from .. import api
from ..util import event, command


class ExitCode(object):
    """Exit codes returned by Bot.run()"""
    Normal = 0
    Error = 1
    Restart = 2


class Bot(object):
    def __init__(self, apiname, stub=False, **kwargs):
        self._api = api.create_api_object(apiname, stub, **kwargs)
        self._dispatcher = event.APIEventDispatcher(self._api)
        self._cmdhandler = command.CommandHandler()
        self._cmdhandler.attach(self._dispatcher)
        self._running = False
        self._exit = ExitCode.Normal

    def init(self):
        """Initialize (attach API, register event handlers, ...)."""
        try:
            logging.info("Initializing...")
            logging.info("{} version {}".format(self._api.api_name(),
                                                self._api.version()))
            logging.info("User handle: " + self._api.user_handle())

            logging.info("Attaching API...")
            self._api.attach()
            logging.info("Done.")
        except:
            logging.error("Failed to initialize.")
            raise

    def quit(self, code=ExitCode.Normal):
        """Gives the signal to stop with the given exit code."""
        self._running = False
        self._exit = code
        logging.info("Shutting down...")

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
    def register_event_handler(self, event, callback, htype=event.HOOK_NORMAL):
        """Register an event handler and returns an Event.Handle to it.
        
        See util.event.APIEventDispatcher for further information.
        """
        return self._dispatcher.register(event, callback, htype)

    def unregister_event_handler(self, event, callback, htype=event.HOOK_NORMAL):
        """Unregister an event handler.

        See util.event.APIEventDispatcher for further information.
        """
        self._dispatcher.unregister(event, callback, htype)

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
        logging.info("Unregistering event handlers...")
        self._cmdhandler.detach()
        self._dispatcher.clear()

        logging.info("Detaching API...")
        self._api.detach()
