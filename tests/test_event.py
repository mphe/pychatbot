#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial
import unittest
from unittest.mock import AsyncMock
from context import util


class Test(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ev = util.event.Event()

    async def test_handlers(self):
        event_func = AsyncMock()
        h = self.ev.register(event_func)
        await self.ev.trigger()
        event_func.assert_called_once()

        h.unregister()
        event_func.reset_mock()
        await self.ev.trigger()
        event_func.assert_not_called()

    async def test_clear(self):
        event_func = AsyncMock()
        self.ev.register(event_func)
        self.ev.register(event_func)
        self.ev.clear()

        await self.ev.trigger()
        event_func.assert_not_called()

    async def test_order(self):
        order = []

        async def event_func(order_value: int):
            order.append(order_value)

        event_prios = (util.event.EVENT_NORMAL, util.event.EVENT_POST_POST, util.event.EVENT_POST, util.event.EVENT_PRE, util.event.EVENT_PRE_PRE)
        for prio in event_prios:
            self.ev.register(partial(event_func, prio), prio)

        await self.ev.trigger()
        self.assertEqual(len(order), len(event_prios))

        for i in range(len(order) - 1):
            self.assertLess(order[i], order[i + 1])


if __name__ == "__main__":
    unittest.main()
