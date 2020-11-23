# -*- coding: utf-8 -*-

import telethon
from chatbot import api
from .Chat import Chat
from . import Telegram  # needed for type hints, pylint: disable=unused-import


class User(api.User):
    @staticmethod
    async def create(teleapi: "Telegram.TelegramAPI", target_user) -> "User":
        return User(teleapi, await teleapi._client.get_entity(target_user))

    def __init__(self, teleapi: "Telegram.TelegramAPI", user: telethon.tl.types.User):
        self._api = teleapi
        self._user = user

    @property
    def id(self) -> str:
        return str(self._user.id)

    @property
    def display_name(self) -> str:
        names = ( i for i in (self._user.first_name, self._user.last_name) if i is not None )
        return " ".join(names)

    @property
    def mention(self) -> str:
        # if self._user.username:
        #     return f"@{self._user.username}"
        return f"[@{self.display_name}](tg://user?id={self.id})"

    async def get_chat(self) -> Chat:
        return await Chat.create(self._api, self._user)
