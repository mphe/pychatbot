# -*- coding: utf-8 -*-

from chatbot import api  # Needed for typehints. pylint: disable=unused-import


class FriendRequest:
    """Represents a friend request."""

    def get_author(self) -> "api.User":
        """Returns a User object of the sender."""
        raise NotImplementedError

    def get_text(self) -> str:
        """Returns the message sent with the friend request."""
        return ""

    async def accept(self) -> None:
        raise NotImplementedError

    async def decline(self) -> None:
        raise NotImplementedError
