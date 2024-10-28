# -*- coding: utf-8 -*-

from chatbot import api  # Needed for typehints. pylint: disable=unused-import


class Request:
    """Base-class for requests like group invites or friend requests."""

    @property
    def author(self) -> "api.User":
        """Returns a User object of the sender."""
        raise NotImplementedError

    @property
    def text(self) -> str:
        """Returns the message sent with the request."""
        raise NotImplementedError

    async def accept(self) -> None:
        raise NotImplementedError

    async def decline(self) -> None:
        raise NotImplementedError

    def __str__(self):
        return f"{self.__class__.__name__} by user '{self.author}': {self.text}"


class GroupInvite(Request):  # pylint: disable=abstract-method
    """Represents a group invite."""

    @property
    def text(self) -> str:
        return ""


class FriendRequest(Request):  # pylint: disable=abstract-method
    """Represents a friend request."""
