# -*- coding: utf-8 -*-

import time
import asyncio
import logging
from chatbot import api, util


class TestAPI(api.APIBase):
    def __init__(self, api_id, stub, opts):
        super().__init__(api_id, stub)
        # Fires a message received event every second
        self._timer = None  # type: asyncio.Task
        self._input_task = None  # type: asyncio.Task
        self._interactive = opts["interactive"]
        self._msg = opts["message"]
        self._chat = TestChat(self)
        self._user = User("testuser", "Test User")
        self._otheruser = User("testfriend", "You")
        self._running = False

    async def start(self):
        if not self._interactive:
            self._timer = asyncio.create_task(self._timer_func())
        self._running = True
        await self._trigger(api.APIEvents.Ready)

        while self._running:
            if self._interactive:
                def input_cb():
                    time.sleep(0.1)  # Simple fix text overlapping
                    return input("Enter message: ").strip()

                # Run input() in a thread to prevent blocking
                if self._input_task is None or self._input_task.done():
                    self._input_task = asyncio.create_task(util.run_in_thread(input_cb))
                    try:
                        text = await self._input_task
                    except asyncio.CancelledError:
                        pass

                if text:
                    if text.startswith("/me "):
                        await self.trigger_receive(text[4:], api.MessageType.Action)
                    else:
                        await self.trigger_receive(text)
            else:
                await asyncio.sleep(1)

    async def cleanup(self) -> None:
        pass

    async def close(self):
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        self._running = False
        if self._input_task and not self._input_task.done():
            self._input_task.cancel()

    @property
    def version(self):
        return "42.0"

    @property
    def api_name(self):
        return "Test API"

    async def get_user(self):
        return self._user

    async def set_display_name(self, name):
        self._user._name = name

    @staticmethod
    def get_default_options():
        return {
            "message": "Test message",
            "interactive": True
        }

    # Testing functions
    async def trigger_receive(self, text, msgtype=api.MessageType.Normal):
        msg = TestingMessage(self._otheruser, text, self._chat, msgtype)
        logging.info(str(msg))
        await self._trigger(api.APIEvents.Message, msg)

    async def trigger_sent(self, text):
        await self._chat.send_message(text)

    async def _timer_func(self):
        while True:
            await asyncio.sleep(1)
            await self.trigger_receive(self._msg)


class TestingMessage(api.ChatMessage):
    def __init__(self, author, text, chat, msgtype=api.MessageType.Normal):
        self._text = text
        self._author = author
        self._chat = chat
        self._type = msgtype

    @property
    def text(self):
        return self._text

    @property
    def author(self):
        return self._author

    @property
    def chat(self):
        return self._chat

    @property
    def type(self):
        return self._type

    @property
    def is_editable(self):
        return False


class TestChat(api.Chat):
    _id_counter = 0

    def __init__(self, apiobj):
        super().__init__()
        self._api = apiobj
        self._id = TestChat._id_counter
        TestChat._id_counter += 1

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return api.ChatType.Normal

    @property
    def is_anonymous(self):
        return False

    async def send_message(self, text, msgtype=api.MessageType.Normal):
        msg = TestingMessage(await self._api.get_user(), text, self, msgtype)
        logging.info(str(msg))
        await self._api._trigger(api.APIEvents.MessageSent, msg)

    async def send_action(self, text):
        await self.send_message(text, api.MessageType.Action)


class User(api.GenericUser):
    pass
