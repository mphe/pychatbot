#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial
import unittest
from context import print_message, create_test_api
from chatbot import api
import logging


class Test(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self._sent = False

    async def _on_receive(self, msg: api.ChatMessage):
        print_message(msg, "Received")
        await msg.chat.send_message("Reply")

    async def _on_sent(self, apiobj: api.APIBase, msg: api.ChatMessage):
        print_message(msg, "Sent")
        await apiobj.close()
        self._sent = True

    async def test_run(self):
        apiobj = create_test_api({
            "message": "custom message text",
            "interactive": False,
            "auto_message": True
        })
        logging.info(str(apiobj))

        apiobj.register_event_handler(api.APIEvents.Message, self._on_receive)
        apiobj.register_event_handler(api.APIEvents.MessageSent, partial(self._on_sent, apiobj))

        await apiobj.run()

        self.assertTrue(self._sent)

        apiobj.unregister_event_handler(api.APIEvents.Message)
        apiobj.unregister_event_handler(api.APIEvents.MessageSent)


if __name__ == "__main__":
    unittest.main()
