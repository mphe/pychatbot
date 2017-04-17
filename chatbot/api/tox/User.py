# -*- coding: utf-8 -*-

import chatbot.api as api


class SelfUser(api.User):
    """Represents the logged in user."""
    def __init__(self, tox):
        self._tox = tox

    def handle(self):
        return self._tox.tox_self_get_address()

    def display_name(self):
        return self._tox.tox_self_get_name()


class Friend(api.User):
    """Represents a friend."""
    def __init__(self, tox, friend_number):
        self._tox = tox
        self._number = friend_number

    def handle(self):
        return self._tox.tox_friend_get_public_key(self._number)

    def display_name(self):
        return self._tox.tox_friend_get_name(self._number)

    # Special
    def number(self):
        return self._number


# Names need to be cached, so they are available when users leave the chat
class GroupPeer(api.User):
    """Represents a group peer."""
    def __init__(self, conf_number, peer_number):
        self._handle = str(conf_number) + str(peer_number)
        self._name = None

    def handle(self):
        return self._handle

    def display_name(self):
        return self._name

    # Special
    def update_name(self, name):
        """Returns true if this was the initial rename after a joining"""
        init = self._name is None
        self._name = name
        return init

