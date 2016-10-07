#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from context import *
import time


def print_message(msg, prefix):
    logging.info("{} message in {}:\n\t {}".format(
        prefix,
        str(msg.get_chat()),
        str(msg)
    ))


class Test(object):
    def __init__(self):
        self._running = True
        self._api = None
        self._msg = None # stores the received message

    def _on_receive(self, msg):
        print_message(msg, "Received")
        self._msg = msg
        msg.get_chat().send_message("Reply")

    def _on_sent(self, msg):
        # Check chat requirements
        if self._msg.get_chat() is not msg.get_chat():
            raise Exception("Messages are not from the same chat object")

        print_message(msg, "Sent")
        self._running = False

    def run(self):
        logging.info("Creating API object")
        self._api = api.create_api_object("test", message="custom message text")
        logging.info(str(self._api))

        self._api.register_event_handler(api.APIEvents.Message,
                                         self._on_receive)
        self._api.register_event_handler(api.APIEvents.MessageSent,
                                         self._on_sent)

        logging.info("Attaching...")
        self._api.attach()

        while self._running:
            logging.info("Waiting for test message...")
            self._api.iterate()

        self._api.unregister_event_handler(api.APIEvents.Message)
        self._api.unregister_event_handler(api.APIEvents.MessageSent)

        logging.info("Detaching...")
        self._api.detach()
        logging.info("Done")

Test().run()
