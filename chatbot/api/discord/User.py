# -*- coding: utf-8 -*-

from chatbot.compat import *
import discord as discordapi
import chatbot.api as api
from .Chat import create_chat
import logging
import time


class User(api.User):
    def __init__(self, client, user):
        self._user = user
        self._client = client

    def handle(self):
        return str(self._user.id)

    def display_name(self):
        return self._user.display_name

    def get_chat(self):
        channel = self._user.dm_channel
        if not channel:
            self._client.run_task(self._user.create_dm())
            channel = self._user.dm_channel

        if not channel:
            logging.warn("Can't get private channel because of the asyncio implementation")

        return create_chat(self._client, channel)

    #extra
    def username(self):
        return str(self._user)
