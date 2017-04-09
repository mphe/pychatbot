# -*- coding: utf-8 -*-

import chatbot.api as api
from . import User


class Message(api.ChatMessage):
    def __init__(self, author, text, chat):
        self._author = author
        self._text = text
        self._chat = chat

    def get_text(self):
        return self._text

    def get_author(self):
        return self._author

    def get_chat(self):
        return self._chat

    def is_editable():
        return False
