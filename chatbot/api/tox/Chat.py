# -*- coding: utf-8 -*-

import chatbot.api as api
from pytoxcore import ToxCore


class Chat(api.Chat):
    def __init__(self, friend_number, tox):
        self._id = friend_number
        self._tox = tox

    def id(self):
        return self._id

    def send_message(self, text):
        self._tox._send_message(text, self._id)

    def type(self):
        return api.ChatType.Normal
