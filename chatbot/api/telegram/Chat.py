# -*- coding: utf-8 -*-

from chatbot import api
from . import Telegram  # Needed for type hints, pylint: disable=unused-import


class Chat(api.Chat):
    @staticmethod
    async def create(teleapi: "Telegram.TelegramAPI", target) -> "Chat":
        return Chat(teleapi, await teleapi._client.get_peer_id(target))

    def __init__(self, teleapi: "Telegram.TelegramAPI", id_: int):
        self._api = teleapi
        self._id = id_

    @property
    def id(self) -> str:
        return str(self._id)

    @property
    def is_id_unique(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    async def send_message(self, text: str) -> None:
        await self._api._send_message(self._id, text)

    async def send_action(self, text: str) -> None:
        name = (await self._api.get_user()).display_name
        await self.send_message(f"__{name} {text}__")


class GroupChat(Chat, api.GroupChat):
    async def leave(self) -> None:
        """Leave a group chat.

        After calling leave(), the size() function should return 0.
        """
        raise NotImplementedError

    async def invite(self, user) -> None:
        """Invite the given User to the groupchat."""
        raise NotImplementedError

    @property
    def size(self) -> int:
        """Returns the number of chat members (including the current user).

        In a normal chat this is 2. Groupchats should override this.
        After calling leave(), the size() function should return 0.
        """
        raise NotImplementedError
