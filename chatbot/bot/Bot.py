# -*- coding: utf-8 -*-

from .. import api
import time
import logging


class ExitCode(object):
    """Exit codes returned by Bot.run()"""
    Normal = 0
    Error = 1
    Restart = 2


class Bot(object):
    def __init__(self, apiname, **kwargs):
        self._api = api.create_api_object(apiname, **kwargs)
        self._handlers = []
        self._running = False
        self._exit = ExitCode.Normal

    def init(self):
        """Initialize (attach API, register event handlers, ...)."""
        try:
            logging.info("Initializing...")
            logging.info("Registering event handlers...")
            self._api.register_event_handler(api.APIEvents.Message,
                                             self._on_msg_receive)
            self._api.register_event_handler(api.APIEvents.FriendRequest,
                                             self._on_friend_request)

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
        try:
            while self._running:
                self._api.iterate()
        except (KeyboardInterrupt, SystemExit):
            self.quit()
        except:
            self.quit(ExitCode.Error)
            raise
        finally:
            self._cleanup()
            logging.info("Exited with code " + str(self._exit))
            return self._exit

    def _cleanup(self):
        """Performs actual cleanup, like detaching the API."""
        logging.info("Detaching API...")
        self._api.detach()

        logging.info("Unregistering event handlers...")
        for i in self._handlers:
            i.unregister()

    def _on_msg_receive(self, msg):
        logging.info("Message received")

    def _on_friend_request(self, req):
        logging.info("Friend request received from " + req.get_username())
