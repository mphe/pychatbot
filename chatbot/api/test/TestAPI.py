# -*- coding: utf-8 -*-

import time
import chatbot.api as api
from threading import Timer


class TestAPI(api.APIBase):
    def __init__(self, api_id, stub, message="", interactive=False, **kwargs):
        super(TestAPI, self).__init__(api_id, stub)
        # Fires a message received event every second
        self._timer = None
        self._interactive = interactive
        self._msg = message if message else self.get_default_options()["message"]
        self._chat = TestChat(self)

    def attach(self):
        if not self._interactive:
            self._start_timer()

    def detach(self):
        if not self._interactive:
            self._timer.cancel()

    def iterate(self):
        if self._interactive:
            text = raw_input("Enter message: ").strip()
            if text:
                self._recv_message(text)
        else:
            time.sleep(1)


    def version(self):
        return "42.0"

    def api_name(self):
        return "Test API"

    def user_handle(self):
        return "testuser"

    @staticmethod
    def get_default_options():
        return {
            "message": "Test message",
            "interactive": False
        }

    def _recv_message(self, text):
        msg = TestingMessage("TestAPI", text, self._chat)
        self._trigger(api.APIEvents.Message, msg)

    def _timer_func(self):
        self._start_timer()
        self._recv_message(self._msg)

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

    def author_handle(self):
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
        msg = TestingMessage(self._api.user_handle(), text, self)
        self._api._trigger(api.APIEvents.MessageSent, msg)

    def type(self):
        return api.ChatType.Normal
