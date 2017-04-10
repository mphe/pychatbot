#!/usr/bin/env python
# -*- coding: utf-8 -*-

from context import logging, api
from chatbot.util import event
from chatbot.bot.subsystem import APIEventDispatcher
from chatbot.compat import *


def print_message(msg, prefix):
    logging.info("{} message in {}:\n\t {}".format(
        prefix,
        str(msg.get_chat()),
        str(msg)
    ))


class Test(object):
    def __init__(self):
        self._counter = 0

    def _on_receive_pre(self, msg):
        print_message(msg, "Received Pre")
        self._counter += 1

    def _on_receive(self, msg):
        print_message(msg, "Received")
        assert self._counter == 1
        self._counter += 1
        msg.get_chat().send_message("Reply")

    def _on_sent(self, msg):
        print_message(msg, "Sent")
        assert self._counter == 2

    def run(self):
        logging.info("Creating API object")
        apiobj = api.create_api_object("test", message="custom message text",
                                       interactive=False)
        dispatcher = APIEventDispatcher(apiobj)
        logging.info(str(apiobj))

        h1 = dispatcher.register(api.APIEvents.Message, self._on_receive_pre, event.EVENT_PRE)
        h2 = dispatcher.register(api.APIEvents.Message, self._on_receive)
        h3 = dispatcher.register(api.APIEvents.MessageSent, self._on_sent)

        apiobj.trigger_receive("foobar")
        h1.unregister()
        h2.unregister()
        apiobj.trigger_receive("foobar II")
        h3.unregister()
        self._counter = 0
        apiobj.trigger_sent("sent")

        dispatcher.clear()
        logging.info("Done")

Test().run()
