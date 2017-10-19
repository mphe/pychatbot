# -*- coding: utf-8 -*-

import logging
import time
from threading import Timer
from chatbot import api
from chatbot.compat import *


class TestAPI(api.APIBase):
    def __init__(self, api_id, stub, opts):
        super(TestAPI, self).__init__(api_id, stub)
        # Fires a message received event every second
        self._timer = None
        self._interactive = opts["interactive"]
        self._msg = opts["message"]
        self._chat = TestChat(self)
        self._user = User("testuser", "Test User")
        self._otheruser = User("testfriend", "You")
        self._running = False

    def run(self):
        if not self._interactive:
            self._start_timer()
        self._running = True

        while self._running:
            if self._interactive:
                text = input("Enter message: ").strip()
                if text:
                    if text.startswith("/me "):
                        self.trigger_receive(text[4:], api.MessageType.Action)
                    else:
                        self.trigger_receive(text)
            else:
                time.sleep(1)

    def quit(self):
        self._timer = None

    def close(self):
        if not self._interactive:
            self._timer.cancel()
        self._running = False

    def version(self):
        return "42.0"

    def api_name(self):
        return "Test API"

    def get_user(self):
        return self._user

    def set_display_name(self, name):
        self._user._name = name

    @staticmethod
    def get_default_options():
        return {
            "message": "Test message",
            "interactive": True
        }

    # Testing functions
    def trigger_receive(self, text, msgtype=api.MessageType.Normal):
        msg = TestingMessage(self._otheruser, text, self._chat, msgtype)
        logging.info(str(msg))
        self._trigger(api.APIEvents.Message, msg)

    def trigger_sent(self, text):
        self._chat.send_message(text)

    def _timer_func(self):
        self._start_timer()
        self.trigger_receive(self._msg)

    def _start_timer(self):
        self._timer = Timer(1, self._timer_func)
        self._timer.start()


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

    def __init__(self, api):
        super(TestChat, self).__init__()
        self._api = api
        self._id = TestChat._id_counter
        TestChat._id_counter += 1

    def id(self):
        return self._id

    def send_message(self, text, msgtype=api.MessageType.Normal):
        msg = TestingMessage(self._api.get_user(), text, self, msgtype)
        logging.info(str(msg))
        self._api._trigger(api.APIEvents.MessageSent, msg)

    def send_action(self, text):
        self.send_message(text, api.MessageType.Action)

    def type(self):
        return api.ChatType.Normal

    def is_anonymous(self):
        return False


class User(api.User):
    def __init__(self, handle, name):
        self._handle = handle
        self._name = name

    def handle(self):
        return self._handle

    def display_name(self):
        return self._name
