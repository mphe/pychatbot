# -*- coding: utf-8 -*-


class User(object):
    def handle(self):
        """Returns the user handle.
        
        The return value depends on the chat system.
        For example, in Skype it would return the username, in Tox it would
        return the user's Tox ID, etc.
        In anonymous groups the handle may have random values.
        """
        raise NotImplementedError

    def display_name(self):
        """Returns the name of the user.
        
        Unlike handle() this function returns the "pretty" name, that
        most (not all) chat systems offer.
        """
        raise NotImplementedError

    def get_chat(self):
        """Returns a Chat object representing the chat with this user."""
        raise NotImplementedError

    def __str__(self):
        return "{} ({})".format(self.display_name(), self.handle())


class GenericUser(User):
    """Generic user with a handle and a name."""

    def __init__(self, handle, name="Unknown"):
        self._handle = handle
        self._name = name

    def handle(self):
        return self._handle

    def display_name(self):
        return self._name
