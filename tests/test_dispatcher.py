#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from functools import partial
import unittest
from unittest.mock import AsyncMock
from context import create_test_api
from chatbot import api
from chatbot.util import event
from chatbot.bot.subsystem import APIEventDispatcher


class Test(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.api = create_test_api({
            "message": "custom message text",
            "interactive": False
        })
        self.dispatcher = APIEventDispatcher(self.api)

    async def test_order(self):
        order = []

        async def event_func(_msg: api.ChatMessage, order_value: int):
            order.append(order_value)

        event_prios = (event.EVENT_NORMAL, event.EVENT_POST_POST, event.EVENT_POST, event.EVENT_PRE, event.EVENT_PRE_PRE)
        for prio in event_prios:
            self.dispatcher.register(api.APIEvents.Message, partial(event_func, order_value=prio), prio)

        self.api.trigger_receive("foobar")
        await asyncio.sleep(0.5)  # Wait a moment for the event to get handled
        self.assertEqual(len(order), len(event_prios))

        for i in range(len(order) - 1):
            self.assertLess(order[i], order[i + 1])

    async def test_handlers(self):
        event_func = AsyncMock()
        h1 = self.dispatcher.register(api.APIEvents.Message, event_func)

        self.api.trigger_receive("foobar")
        await asyncio.sleep(0.5)  # Wait a moment for the event to get handled

        event_func.assert_called_once()
        event_func.reset_mock()

        h1.unregister()
        self.api.trigger_receive("foobar")
        await asyncio.sleep(0.5)  # Wait a moment for the event to get handled
        event_func.assert_not_called()

    async def test_clear(self):
        event_func = AsyncMock()
        self.dispatcher.register(api.APIEvents.Message, event_func)
        self.dispatcher.register(api.APIEvents.Message, event_func)
        self.dispatcher.clear()

        self.api.trigger_receive("foobar")
        await asyncio.sleep(0.5)  # Wait a moment for the event to get handled
        event_func.assert_not_called()


if __name__ == "__main__":
    unittest.main()
