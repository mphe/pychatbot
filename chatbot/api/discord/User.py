# -*- coding: utf-8 -*-

import logging
import discord as discordapi
from chatbot import api
from .Chat import create_chat
from typing import Union


class User(api.User):
    def __init__(self, client, user: Union[discordapi.User, discordapi.ClientUser, discordapi.Member]):
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

    # extra
    @property
    def username(self) -> str:
        return str(self._user)

    async def get_chat(self):
        if isinstance(self._user, discordapi.ClientUser):
            logging.warning("Trying to create a chat with oneself")
            return None
        if not self._user.dm_channel:
            await self._user.create_dm()  # type: ignore[misc]
        return create_chat(self._client, self._user.dm_channel)
