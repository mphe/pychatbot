# -*- coding: utf-8 -*-

from .ChatMessage import MessageType


class ChatType(object):
    """An enum defining group types."""
    Normal = "Normal"
    Group = "Group"


class Chat(object):
    """Represents a chat of any type (normal and groupchats).
    
    If normal chats and groupchats have different functionality, use this
    as baseclass.

    Every chat must have an unique ID that is persistent across the session.
    It can be persistent across multiple sessions but doesn't have to.
    The ID can be of any type (string, int, ...).
    """

    def id(self):
        """Returns the chat's unique ID."""
        raise NotImplementedError

    def send_message(self, text):
        """Sends a message with the given text to this chatroom."""
        raise NotImplementedError

    def send_action(self, text):
        """Sends an action (/me ...) with the given text to this chatroom."""
        raise NotImplementedError

    def type(self):
        """Returns the chat type. See ChatType for available types."""
        raise NotImplementedError

    def size(self):
        """Returns the number of chat members (including the current user).
        
        In a normal chat this is 2. Groupchats should override this.
        """
        return 2

    def is_anonymous(self):
        """Returns whether or not this is an anonymous chat.
        
        In anonymous groups you can't access other chat member's handles.
        That means users in an anonymous chat can't be uniquely identified.
        """
        raise NotImplementedError

    def __len__(self):
        return self.size()

    def __str__(self):
        if self.type() == ChatType.Normal:
            return "Chat {}".format(repr(self.id()))
        else:
            return "Groupchat {}".format(repr(self.id()))


class GroupChat(Chat):
    """Represents a group chat.
    
    Basically the same as a normal chat but with some extra functions.
    """
    def leave(self):
        """Leave a group chat.
        
        After calling leave(), the size() function should return 0.
        """
        raise NotImplementedError

    def invite(self, user):
        """Invite the given User to the groupchat."""
        raise NotImplementedError

    def size(self):
        """Returns the number of chat members (including the current user).
        
        In a normal chat this is 2. Groupchats should override this.
        """
        raise NotImplementedError
