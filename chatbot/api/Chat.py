# -*- coding: utf-8 -*-


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

    TODO: Consider removing the following specification.

    Messages or other objects that origin from the same chat must also
    reference the same Chat object, e.g.:

        msg1 = chat.send_message("foobar")
        msg2 = chat.send_message("foobar2")
        if msg1.get_chat() is not msg2.get_chat():
            raise Exception("Must never happen!")
    """

    def id(self):
        """Returns the chat's unique ID."""
        raise NotImplementedError

    def send_message(self, text):
        """Sends a message with the given text to this chatroom."""
        raise NotImplementedError

    def type(self):
        """Returns the chat type. See ChatType for available types."""
        raise NotImplementedError

    def __str__(self):
        if self.type() == ChatType.Normal:
            return "Chat {}".format(repr(self.id()))
        else:
            return "Groupchat {}".format(repr(self.id()))
