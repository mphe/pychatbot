#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from context import chatbot
api = chatbot.api
import logging
import time

class Test(object):
    def __init__(self):
        self._running = True
        self._test = None

    def _on_receive(self, msg):
        self._running = False
        logging.info("Received message:\n\t" + str(msg))

    def run(self):
        logging.info("Creating api object")
        self._test = api.create_api_object("test")
        logging.info(str(self._test))
        self._test.register_event_handler(api.APIEvents.Received, self._on_receive)

        logging.info("Attaching...")
        self._test.attach()

        while self._running:
            logging.info("Waiting for test message...")
            self._test.iterate()

        self._test.unregister_event_handler(api.APIEvents.Received, self._on_receive)
        logging.info("Detaching...")
        self._test.detach()
        logging.info("Done")


logging.basicConfig(level=logging.DEBUG)
Test().run()
