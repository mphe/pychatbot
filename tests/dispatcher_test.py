#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
from context import api, print_message
from chatbot.util import event
from chatbot.bot.subsystem import APIEventDispatcher


class Test:
    def __init__(self):
        self._counter = 0

    async def _on_receive_pre(self, msg: api.ChatMessage):
        print_message(msg, "Received Pre")
        self._counter += 1

    async def _on_receive(self, msg: api.ChatMessage):
        print_message(msg, "Received")
        assert self._counter == 1
        self._counter += 1
        await msg.chat.send_message("Reply")

    async def _on_sent(self, msg: api.ChatMessage):
        print_message(msg, "Sent")
        assert self._counter == 2

    async def run(self):
        logging.info("Creating API object")
        apiobj = api.create_api_object("test", message="custom message text",
                                       interactive=False)
        dispatcher = APIEventDispatcher(apiobj)
        logging.info(str(apiobj))

        h1 = dispatcher.register(api.APIEvents.Message, self._on_receive_pre, event.EVENT_PRE)
        h2 = dispatcher.register(api.APIEvents.Message, self._on_receive)
        h3 = dispatcher.register(api.APIEvents.MessageSent, self._on_sent)

        await apiobj.trigger_receive("foobar")  # type: ignore
        h1.unregister()
        h2.unregister()
        await apiobj.trigger_receive("foobar II")  # type: ignore
        h3.unregister()
        self._counter = 0
        await apiobj.trigger_sent("sent")  # type: ignore

        dispatcher.clear()
        logging.info("Done")


asyncio.run(Test().run())
