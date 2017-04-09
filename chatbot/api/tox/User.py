# -*- coding: utf-8 -*-


def create_user(tox, friend_number):
    """Creates a User object from a friend number.
    
    If friend_number is -1, the logged in user is used.
    """
    if friend_number == -1:
        return User(tox.tox_self_get_address(),
                    tox.tox_self_get_name())
    else:
        return User(tox.tox_friend_get_public_key(friend_number),
                    tox.tox_friend_get_name(friend_number))


class User(object):
    def __init__(self, toxid, name):
        self._toxid = toxid
        self._name = name

    def handle(self):
        """Returns the user's Tox ID"""
        return self._toxid

    def display_name(self):
        return self._name
