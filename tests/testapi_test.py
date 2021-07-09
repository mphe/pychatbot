#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from context import api, print_message
import logging


class Test:
    def __init__(self):
        self._msg = None  # stores the received message
        self._api = None  # api.APIBase
        self._sent = False

    async def _on_receive(self, msg: api.ChatMessage):
        print_message(msg, "Received")
        self._msg = msg
        await msg.chat.send_message("Reply")

    async def _on_sent(self, msg: api.ChatMessage):
        print_message(msg, "Sent")
        await self._api.close()
        self._sent = True

    def run(self):
        logging.info("Creating API object")
        self._api = api.create_api_object("test", {
            "message": "custom message text",
            "interactive": False
        })
        logging.info(str(self._api))

        self._api.register_event_handler(api.APIEvents.Message, self._on_receive)
        self._api.register_event_handler(api.APIEvents.MessageSent, self._on_sent)

        logging.info("Running...")

        asyncio.run(self._api.run())

        assert self._sent

        self._api.unregister_event_handler(api.APIEvents.Message)
        self._api.unregister_event_handler(api.APIEvents.MessageSent)

        logging.info("Done")


Test().run()
