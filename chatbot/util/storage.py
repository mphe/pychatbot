#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, Optional, Union
from chatbot.api import User, Chat
from chatbot.util import config

ChatReference = Union[Chat, str, None]
UserReference = Union[User, str, None]


class Storage:
    def __init__(self, cfg: config.Config) -> None:
        self._cfg = cfg

    def get(self, key: str, user: UserReference, chat: ChatReference) -> Optional[Any]:
        return self._cfg.data.get(self._build_storage_key(key, user, chat))

    def get_with_fallback(self, key: str, user: UserReference, chat: ChatReference) -> Optional[Any]:
        """Return the value of key. If the key does not exist in the specified scope, it falls back to chat-scope, then user-scope, then global-scope."""
        # First try requested scope
        data = self.get(key, user, chat)
        if data:
            return data

        # Global scope, there is nothing more to fall back
        if not user and not chat:
            return None

        # If requested user+chat scope, first try chat, then fallback to user storage
        if user and chat:
            data = self.get(key, None, chat)
            if data:
                return data

            data = self.get(key, user, None)
            if data:
                return data

        # If nothing found, use global storage or return None
        data = self.get(key, None, None)
        return data

    def set(self, key: str, value: Any, user: UserReference, chat: ChatReference) -> None:
        self._cfg[self._build_storage_key(key, user, chat)] = value

    def erase(self, key: str, user: UserReference, chat: ChatReference) -> None:
        """Removes the given entry from storage. Does nothing when the key does not exist."""
        key = self._build_storage_key(key, user, chat)

        if key in self._cfg:
            del self._cfg[key]

    def load(self):
        """Reload storage file. See also config.Config.load()."""
        self._cfg.load()

    def write(self):
        """Write to file. See also config.Config.write()."""
        self._cfg.write()

    def scope(self, user: UserReference, chat: ChatReference) -> "StorageScope":
        return StorageScope(self, user, chat)

    @staticmethod
    def _build_storage_key(key: str, user: UserReference, chat: ChatReference) -> str:
        userid: Optional[str] = user.id if isinstance(user, User) else user
        chatid: Optional[str] = chat.id if isinstance(chat, Chat) else chat

        if userid and chatid:
            prefix = f"uc-{userid}-{chatid}"
        elif userid and not chatid:
            prefix = f"u-{userid}"
        elif not userid and chatid:
            prefix = f"c-{chatid}"
        else:
            prefix = "g-"

        return f"{prefix}-{key}"


class StorageScope:
    def __init__(self, storage: Storage, user: UserReference, chat: ChatReference):
        self._storage: Storage = storage
        self._user = user
        self._chat = chat

    def get(self, key: str) -> Optional[Any]:
        return self._storage.get(key, self._user, self._chat)

    def get_with_fallback(self, key: str) -> Optional[Any]:
        return self._storage.get_with_fallback(key, self._user, self._chat)

    def set(self, key: str, value: Any) -> None:
        return self._storage.set(key, value, self._user, self._chat)

    def erase(self, key: str) -> None:
        return self._storage.erase(key, self._user, self._chat)

    def __getitem__(self, key) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        self.erase(key)
