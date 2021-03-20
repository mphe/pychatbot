# -*- coding: utf-8 -*-

from asyncio import coroutine
from functools import partial
import logging
from typing import Dict
from chatbot import api, util
from chatbot.bot import BotPlugin

# TODO: !testapi should test group chats


class Plugin(BotPlugin):
    def __init__(self, oldme, bot):
        super().__init__(oldme, bot)
        self._events: Dict[str, bool] = {}  # Store which events were triggered

        self.register_admin_command("testapi", self._test, argc=0)

        for event in api.APIEvents:
            self.register_event_handler(
                event, coroutine(partial(self._handle_event, event)), util.event.EVENT_PRE_PRE)
            self._events[event] = False

    async def _test(self, msg: api.ChatMessage, _argv):
        """Syntax: testapi

        Runs code tests on this message.
        """
        # Test API calls
        await util.testing.test_message(msg, self.bot.api)

        # Print event stats
        states = (
            util.testing.colorize("Not triggered", util.testing.COLOR_FAIL, util.testing.COLOR_BOLD),
            util.testing.colorize("Triggered", util.testing.COLOR_OK, util.testing.COLOR_BOLD),
        )

        print()
        logging.info("The following events were triggered since the plugin was mounted:")

        for k, v in self._events.items():
            logging.info("%s: %s", k, states[int(v)])

    async def _handle_event(self, event: str, *_args, **_kwargs):
        self._events[event] = True
