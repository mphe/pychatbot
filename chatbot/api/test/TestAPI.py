# -*- coding: utf-8 -*-

import asyncio
import logging
from chatbot import api


class TestAPI(api.APIBase):
    def __init__(self, api_id, stub, opts):
        super(TestAPI, self).__init__(api_id, stub)
        # Fires a message received event every second
        self._timer: asyncio.Task = None
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
                text = input("Enter message: ").strip()
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

    def version(self):
        return "42.0"

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

    def get_text(self):
        return self._text

    def get_author(self):
        return self._author

    def get_chat(self):
        return self._chat

    def get_type(self):
        return self._type

    def is_editable(self):
        return False


class TestChat(api.Chat):
    _id_counter = 0

    def __init__(self, apiobj):
        super(TestChat, self).__init__()
        self._api = apiobj
        self._id = TestChat._id_counter
        TestChat._id_counter += 1

    def id(self):
        return self._id

    async def send_message(self, text, msgtype=api.MessageType.Normal):
        msg = TestingMessage(await self._api.get_user(), text, self, msgtype)
        logging.info(str(msg))
        await self._api._trigger(api.APIEvents.MessageSent, msg)

    async def send_action(self, text):
        await self.send_message(text, api.MessageType.Action)

    def type(self):
        return api.ChatType.Normal

    def is_anonymous(self):
        return False


class User(api.GenericUser):
    pass
