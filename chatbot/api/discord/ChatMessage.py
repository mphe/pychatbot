# -*- coding: utf-8 -*-

from chatbot.compat import *
import discord as discordapi
import chatbot.api as api
from .Chat import ServerChannel
from .User import User

class Message(api.ChatMessage):
    def __init__(self, client, msg, editable=False):
        self._msg = msg
        self._editable = editable

        if self._msg.server:
            self._chat = ServerChannel(client, self._msg.channel)
        else:
            raise NotImplementedError

    def get_author(self):
        return User(self._msg.author)

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
