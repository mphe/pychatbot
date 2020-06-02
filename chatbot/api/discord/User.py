# -*- coding: utf-8 -*-

import discord as discordapi
import chatbot.api as api
from .Chat import create_chat


class User(api.User):
    def __init__(self, client, user: discordapi.User):
        self._user = user
        self._client = client

    @property
    def id(self) -> str:
        return str(self._user.id)

    @property
    def display_name(self) -> str:
        return self._user.display_name

    @property
    def mention(self) -> str:
        return self._user.mention

    async def get_chat(self):
        channel = self._user.dm_channel
        if not channel:
            await self._user.create_dm()
            channel = self._user.dm_channel

        return create_chat(self._client, channel)

    # extra
    @property
    def username(self) -> str:
        return str(self._user)
