# -*- coding: utf-8 -*-


class ChatMessage(object):
    def get_text(self):
        raise NotImplementedError

    def get_author(self):
        """Returns a User object of the sender."""
        raise NotImplementedError

    def get_chat(self):
        """Return a Chat object representing the chat this message was sent in."""
        raise NotImplementedError

    def is_editable(self):
        raise NotImplementedError

    def edit(self, newstr):
        raise NotImplementedError

    def reply(self, text):
        """Same as ChatMessage.get_chat().send_message(text)."""
        self.get_chat().send_message(text)

    def __str__(self):
        return "{}: {}".format(self.get_author().display_name(),
                               self.get_text())
