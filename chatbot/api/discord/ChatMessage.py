# -*- coding: utf-8 -*-

import discord as discordapi
from chatbot import api
from .Chat import create_chat
from .User import User
import logging


class Message(api.ChatMessage):
    def __init__(self, client, msg: discordapi.Message, editable=False):
        self._msg = msg
        self._editable = editable
        self._chat = create_chat(client, msg.channel)
        self._user = User(client, msg.author)

    @property
    def author(self):
        return self._user

    @property
    def chat(self):
        return self._chat

    @property
    def text(self):
        return self._msg.content

    @property
    def type(self):
        if self._msg.type == discordapi.MessageType.default:
            return api.MessageType.Normal
        return api.MessageType.System

    @property
    def is_editable(self):
        return self._editable

    async def edit(self, newstr) -> None:
        try:
            await self._msg.edit(content=newstr)
        except (discordapi.HTTPException, discordapi.Forbidden):
            logging.error("Could not edit message: %s", self)
