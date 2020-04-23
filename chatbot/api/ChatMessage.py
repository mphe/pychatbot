# -*- coding: utf-8 -*-

from chatbot import api  # Needed for typehints. pylint: disable=unused-import


class MessageType(object):
    Normal, Action, System = range(3)


class ChatMessage(object):
    def get_text(self) -> str:
        raise NotImplementedError

    def get_author(self) -> "api.User":
        """Returns a User object of the sender."""
        raise NotImplementedError

    def get_chat(self) -> "api.Chat":
        """Returns a Chat object representing the chat this message was sent in."""
        raise NotImplementedError

    def get_type(self) -> MessageType:
        """Returns the message type."""
        raise NotImplementedError

    def is_editable(self) -> bool:
        raise NotImplementedError

    def edit(self, newstr) -> None:
        raise NotImplementedError

    def reply(self, text) -> None:
        """Same as ChatMessage.get_chat().send_message(text)."""
        self.get_chat().send_message(text)

    def __str__(self) -> str:
        f = "{}: {}" if self.get_type() == MessageType.Normal else "*** {} {} ***"
        return f.format(self.get_author().display_name(), self.get_text())
