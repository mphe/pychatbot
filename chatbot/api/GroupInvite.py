# -*- coding: utf-8 -*-

from chatbot import api  # Needed for typehints. pylint: disable=unused-import


class GroupInvite:
    """Represents a group invite."""

    def get_author(self) -> "api.User":
        """Returns a User object of the sender."""
        raise NotImplementedError

    async def accept(self) -> None:
        raise NotImplementedError

    async def decline(self) -> None:
        raise NotImplementedError
