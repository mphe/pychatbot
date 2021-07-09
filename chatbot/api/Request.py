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

    def __str__(self, reqname="Request"):
        return "{} by user '{}': {}".format(
            reqname, self.author, self.text)


class GroupInvite(Request):  # pylint: disable=abstract-method
    """Represents a group invite."""

    @property
    def text(self) -> str:
        return ""

    def __str__(self):  # pylint: disable=signature-differs
        return super().__str__("Group-Invite")


class FriendRequest(Request):  # pylint: disable=abstract-method
    """Represents a friend request."""

    def __str__(self):  # pylint: disable=signature-differs
        return super().__str__("Friend-Request")
