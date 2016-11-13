# -*- coding: utf-8 -*-


class User(object):
    def handle(self):
        """Returns the user handle.
        
        The return value depends on the chat system.
        For example, in Skype it would return the username, in Tox it would
        return the user's Tox ID, etc.
        """
        raise NotImplementedError

    def display_name(self):
        """Returns the name of the user.
        
        Unlike handle() this function returns the "pretty" name, that
        most (not all) chat systems offer.
        """
        raise NotImplementedError

    # TODO: Consider adding this
    # def send_message(self, text):
    #     """Send a message to this user"""
    #     raise NotImplementedError
