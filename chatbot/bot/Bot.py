# -*- coding: utf-8 -*-

import time
import logging
from functools import partial
from .. import api
from .Event import Event


class ExitCode(object):
    """Exit codes returned by Bot.run()"""
    Normal = 0
    Error = 1
    Restart = 2


class Bot(object):
    def __init__(self, apiname, **kwargs):
        self._api = api.create_api_object(apiname, **kwargs)
        self._events = {}
        self._running = False
        self._exit = ExitCode.Normal

    def init(self):
        """Initialize (attach API, register event handlers, ...)."""
        try:
            logging.info("Initializing...")
            logging.info("{} version {}".format(self._api.api_name(),
                                                self._api.version()))
            logging.info("Username: " + self._api.username())

            logging.info("Registering event handlers...")
            self._api.register_event_handler(api.APIEvents.Message,
                                             self._on_msg_receive)
            self._events[api.APIEvents.Message] = Event()

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

    def _cleanup(self):
        """Performs actual cleanup after exiting the main loop."""
        logging.info("Detaching API...")
        self._api.detach()

        logging.info("Unregistering event handlers...")
        for i in self._events.iterkeys():
            self._api.unregister_event_handler(i)
        self._events = {}

    # Event functions
    def register_event_handler(self, event, callback):
        if not self._events.has_key(event):
            self._events[event] = Event()
            self._api.register_event_handler(
                    event, partial(self._dispatch_event, event))
        return self._events[event].add_handler(callback)

    def unregister_event_handler(self, event, callback):
        self._events[event].del_handler(callback)

    def _dispatch_event(self, event, *args):
        """Generic function to dispatch an event to all registered callbacks."""
        if len(self._events[event]) > 0:
            self._events[event].trigger(*args)
        else:
            # Unregister if no callbacks left, so that debug stub messages
            # on unhandled events still come through.
            # This needs to happen here because unregister_event_handler can be
            # bypassed by unregistering using the EventHandle returned by the
            # register function.
            del self._events[event]
            self._api.unregister_event_handler(event)
            # Trigger without anything registered (as it should have been)
            self._api._trigger(event, *args)

    # Events
    def _on_msg_receive(self, msg):
        self._events[api.APIEvents.Message].trigger(msg)
