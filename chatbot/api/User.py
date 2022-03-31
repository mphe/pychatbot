# -*- coding: utf-8 -*-

from chatbot import api  # Needed for typehints. pylint: disable=unused-import
from .Identifiable import Identifiable


class User(Identifiable):
    @property
    def id(self) -> str:
        """Returns the user ID.

        The return value depends on the chat system, for example, in Discord it
        would return a snowflake ID, in Tox it would return the Tox ID, etc.
        In anonymous groups the handle may have random values.

        This _must_ always be a string, no matter what the underlying API uses
        internally.
        """
        raise NotImplementedError

    @property
    def display_name(self) -> str:
        """Returns the name of the user.

        Unlike id() this function returns the "pretty" name, that
        most (not all) chat systems offer.
        """
        raise NotImplementedError

    @property
    def mention(self) -> str:
        """Returns the corresponding string to ping the user, e.g. "@SomeUser"."""
        return "@" + self.id

    async def get_chat(self) -> "api.Chat":
        """Returns a Chat object representing the chat with this user."""
        raise NotImplementedError

    def __str__(self):
        return "{} ({})".format(self.display_name, self.id)


class GenericUser(User):
    """Generic user with an ID, name, and chat instance."""

    def __init__(self, userid: str, name: str, chat: "api.Chat"):
        self._id = userid
        self._name = name
        self._chat = chat

    @property
    def id(self) -> str:
        return self._id

    @property
    def display_name(self) -> str:
        return self._name

    async def get_chat(self) -> "api.Chat":
        return self._chat
