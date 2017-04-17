# -*- coding: utf-8 -*-

from pytoxcore import ToxCore
import chatbot.api as api


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

    def is_editable(self):
        return False


def split_text(text):
    """Split the message in chunks of TOX_MAX_MESSAGE_LENGTH."""
    for i in range(0, len(text), ToxCore.TOX_MAX_MESSAGE_LENGTH):
        yield text[i:i + ToxCore.TOX_MAX_MESSAGE_LENGTH]
