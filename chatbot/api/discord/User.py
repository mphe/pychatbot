# -*- coding: utf-8 -*-

import discord as discordapi
import chatbot.api as api
from .Chat import create_chat


class User(api.User):
    def __init__(self, client, user: discordapi.User):
        self._user = user
        self._client = client

    def id(self):
        return self._user.id

    def display_name(self):
        return self._user.display_name

    async def get_chat(self):
        channel = self._user.dm_channel
        if not channel:
            await self._user.create_dm()
            channel = self._user.dm_channel

        return create_chat(self._client, channel)

    # extra
    def username(self):
        return str(self._user)
