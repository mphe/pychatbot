# -*- coding: utf-8 -*-

from enum import IntEnum
from chatbot import api  # Needed for typehints. pylint: disable=unused-import


class MessageType(IntEnum):
    Normal, Action, System = range(3)


class ChatMessage:
    @property
    def text(self) -> str:
        raise NotImplementedError

    @property
    def author(self) -> "api.User":
        """Returns a User object of the sender."""
        raise NotImplementedError

    @property
    def chat(self) -> "api.Chat":
        """Returns a Chat object representing the chat this message was sent in."""
        raise NotImplementedError

    @property
    def type(self) -> MessageType:
        """Returns the message type."""
        raise NotImplementedError

    @property
    def is_editable(self) -> bool:
        raise NotImplementedError

    async def edit(self, newstr: str) -> None:
        raise NotImplementedError

    async def reply(self, text: str) -> None:
        """Same as ChatMessage.chat.send_message(text)."""
        await self.chat.send_message(text)

    def __str__(self) -> str:
        f = "{}: {}" if self.type == MessageType.Normal else "*** {} {} ***"
        return f.format(self.author, self.text)
