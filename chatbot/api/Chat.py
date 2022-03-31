# -*- coding: utf-8 -*-

from enum import IntEnum
from .Identifiable import Identifiable


class ChatType(IntEnum):
    """An enum defining group types."""
    Normal, Group = range(2)


class Chat(Identifiable):
    """Represents a chat of any type (normal and groupchats).

    If normal chats and groupchats have different functionality, use this
    as baseclass.

    Every chat must have a unique ID that is persistent across the session.
    It can be persistent across multiple sessions but doesn't have to.
    """

    @property
    def id(self) -> str:
        """Returns the chat's unique ID.

        Similar to User.id().

        This _must_ always be a string, no matter what the underlying API uses
        internally.
        """
        raise NotImplementedError

    @property
    def is_id_unique(self) -> bool:
        """Returns whether the chat's ID is globally unique."""
        raise NotImplementedError

    @property
    def type(self) -> ChatType:
        """Returns the chat type. See ChatType for available types."""
        return ChatType.Normal

    @property
    def size(self) -> int:
        """Returns the number of chat members (including the current user).

        In a normal chat this is 2. Groupchats should override this.

        If the user is not part of this chat or leave()ed, the size is
        undefined behavior.
        """
        return 2

    @property
    def is_anonymous(self) -> bool:
        """Returns whether or not this is an anonymous chat.

        In anonymous groups you can't access other chat member's handles.
        That means users in an anonymous chat can't be uniquely identified.
        """
        raise NotImplementedError

    async def send_message(self, _text: str) -> None:
        """Sends a message with the given text to this chatroom."""
        raise NotImplementedError

    async def send_action(self, _text: str) -> None:
        """Sends an action (/me ...) with the given text to this chatroom."""
        raise NotImplementedError

    def __len__(self):
        return self.size

    def __str__(self):
        if self.type == ChatType.Normal:
            return "Chat {}".format(self.id)
        return "Groupchat {}".format(self.id)


class GroupChat(Chat):
    """Represents a group chat.

    Basically the same as a normal chat but with some extra functions.
    """
    @property
    def type(self) -> ChatType:
        return ChatType.Group

    async def leave(self) -> None:
        """Leave a group chat.

        After calling leave(), the size() function should return 0.
        """
        raise NotImplementedError

    async def invite(self, _user) -> None:
        """Invite the given User to the groupchat."""
        raise NotImplementedError

    @property
    def size(self) -> int:
        """Returns the number of chat members (including the current user).

        In a normal chat this is 2. Groupchats should override this.
        After calling leave(), the size() function should return 0.
        """
        raise NotImplementedError
