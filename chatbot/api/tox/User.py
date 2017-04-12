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
