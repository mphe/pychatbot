# -*- coding: utf-8 -*-

import chatbot.api as api
from threading import Timer


class TestAPI(api.APIBase):
    def __init__(self, message="", **kwargs):
        super(TestAPI, self).__init__()
        # Fires a message received event every second
        self._timer = None
        self._msg = message if message else self.get_default_options()["message"]
        self._chat = TestChat(self)

    def attach(self):
        self._start_timer()

    def detach(self):
        self._timer.cancel()

    def version(self):
        return "42.0"

    def api_name(self):
        return "Test API"

    def username(self):
        return "testuser"

    @staticmethod
    def get_default_options():
        return {
            "message": "Test message"
        }

    def _timer_func(self):
        self._start_timer()
        msg = TestingMessage("TestAPI", self._msg, self._chat)
        self._trigger(api.APIEvents.Message, msg)

    def _start_timer(self):
        self._timer = Timer(1, self._timer_func)
        self._timer.start()



class TestingMessage(api.ChatMessage):
    def __init__(self, author, text, chat):
        self._text = text
        self._author = author
        self._chat = chat

    def get_text(self):
        return self._text

    def get_author(self):
        return self._author

    def get_chat(self):
        return self._chat

    def is_editable():
        return False


class TestChat(api.Chat):
    _id_counter = 0

    def __init__(self, api):
        super(TestChat, self).__init__()
        self._api = api
        self._id = TestChat._id_counter
        TestChat._id_counter += 1

    def id(self):
        return self._id

    def send_message(self, text):
        msg = TestingMessage(self._api.username(), text, self)
        self._api._trigger(api.APIEvents.MessageSent, msg)

    def type(self):
        return api.ChatType.Normal
