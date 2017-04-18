# -*- coding: utf-8 -*-


class MessageType(object):
    Normal, Action = range(2)


class ChatMessage(object):
    def get_text(self):
        raise NotImplementedError

    def get_author(self):
        """Returns a User object of the sender."""
        raise NotImplementedError

    def get_chat(self):
        """Returns a Chat object representing the chat this message was sent in."""
        raise NotImplementedError

    def get_type(self):
        """Returns the message type."""
        raise NotImplementedError

    def is_editable(self):
        raise NotImplementedError

    def edit(self, newstr):
        raise NotImplementedError

    def reply(self, text):
        """Same as ChatMessage.get_chat().send_message(text)."""
        self.get_chat().send_message(text)

    def __str__(self):
        f = "{}: {}" if self.get_type() == MessageType.Normal else "*** {} {} ***"
        return f.format(self.get_author().display_name(), self.get_text())
