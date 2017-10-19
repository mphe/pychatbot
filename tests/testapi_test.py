#!/usr/bin/env python
# -*- coding: utf-8 -*-

from context import *
from chatbot.compat import *
import time


def print_message(msg, prefix):
    logging.info("{} message in {}:\n\t {}".format(
        prefix,
        str(msg.get_chat()),
        str(msg)
    ))


class Test(object):
    def __init__(self):
        self._msg = None # stores the received message
        self._api = None
        self._sent = False

    def _on_receive(self, msg):
        print_message(msg, "Received")
        self._msg = msg
        msg.get_chat().send_message("Reply")

    def _on_sent(self, msg):
        print_message(msg, "Sent")
        self._api.close()
        self._sent = True

    def run(self):
        logging.info("Creating API object")
        self._api = api.create_api_object("test", message="custom message text",
                                          interactive=False)
        logging.info(str(self._api))

        self._api.register_event_handler(api.APIEvents.Message, self._on_receive)
        self._api.register_event_handler(api.APIEvents.MessageSent, self._on_sent)

        logging.info("Running...")
        self._api.run()
        self._api.quit()

        assert self._sent

        self._api.unregister_event_handler(api.APIEvents.Message)
        self._api.unregister_event_handler(api.APIEvents.MessageSent)

        logging.info("Done")

Test().run()
