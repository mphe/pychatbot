# -*- coding: utf-8 -*-

from chatbot.compat import *
import discord as discordapi
import chatbot.api as api
from .Chat import create_chat
from .User import User

class Message(api.ChatMessage):
    def __init__(self, client, msg, editable=False):
        self._msg = msg
        self._editable = editable
        self._chat = create_chat(client, msg.channel)
        self._user = User(client, msg.author)

    def get_author(self):
        return self._user

    def get_chat(self):
        return self._chat

    def get_text(self):
        return self._msg.content

    def get_type(self):
        if self._msg.type == discordapi.MessageType.default:
            return api.MessageType.Normal
        return api.MessageType.System

    def is_editable(self):
        return self._editable
