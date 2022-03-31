#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from chatbot import api
from typing import List, Set


class Notifier:
    """Utility class that stores a list of chats and broadcasts messages to all of them."""
    def __init__(self, apiobj: api.APIBase):
        self._api = apiobj
        self._chats: Set[api.Chat] = set()

    def add_chat(self, chat: api.Chat) -> None:
        self._chats.add(chat)

    def remove_chat(self, chat: api.Chat) -> None:
        self._chats.remove(chat)

    def toggle_chat(self, chat: api.Chat) -> bool:
        """Removes the chat from the list if it is in it, otherwise adds it.

        Returns True if the chat was added, otherwise False."""
        if chat in self._chats:
            self.remove_chat(chat)
            return False
        self.add_chat(chat)
        return True

    def save(self) -> List[str]:
        return [ chat.id for chat in self._chats ]

    async def load(self, ids: List[str]) -> None:
        self._chats = { await self._api.find_chat(chatid) for chatid in ids }

    async def notify(self, message: str) -> None:
        for chat in self._chats:
            await chat.send_message(message)

    def size(self) -> int:
        return len(self._chats)
