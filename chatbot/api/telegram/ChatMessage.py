# -*- coding: utf-8 -*-

import telethon
from telethon.tl.custom.message import Message as TelegramMessage
from chatbot import api
from . import Telegram  # pylint: disable=unused-import
from .User import User
from .Chat import Chat


class ChatMessage(api.ChatMessage):
    @staticmethod
    async def create(teleapi: "Telegram.TelegramAPI", telemsg: TelegramMessage) -> "ChatMessage":
        # Sometimes the sender_id is None for outgoing messages
        if telemsg.out and telemsg.sender_id is None:
            user = await teleapi.get_user()
        else:
            user = await User.create(teleapi, telemsg.sender_id)

        return ChatMessage(
            teleapi, telemsg, await Chat.create(teleapi, telemsg.chat_id), user, None)

        # For some reason this fails with "ValueError: You must pass either a channel or a chat"
        # await teleapi._client.get_permissions(chat, teleapi._me._user))

    def __init__(self, teleapi: "Telegram.TelegramAPI",
                 telemsg: TelegramMessage,
                 chat: Chat, author: User,
                 _permissions: telethon.tl.custom.ParticipantPermissions):
        self._api = teleapi
        self._msg = telemsg
        self._chat = chat
        self._author = author
        # self._permissions = permissions

    @property
    def text(self) -> str:
        return self._msg.text

    @property
    def author(self) -> "api.User":
        return self._author

    @property
    def chat(self) -> "api.Chat":
        return self._chat

    @property
    def type(self) -> api.MessageType:
        if self._msg.action_entities is None:
            return api.MessageType.Normal
        return api.MessageType.System

    @property
    def is_editable(self) -> bool:
        # TODO: Fix permission query
        # return self.author.id == self._api._me.id or self._permissions.edit_messages
        return self.author.id == self._api._me.id

    async def edit(self, newstr: str) -> None:
        await self._msg.edit(newstr)
