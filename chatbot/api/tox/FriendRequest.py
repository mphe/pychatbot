# -*- coding: utf-8 -*-

import chatbot.api as api
from . import User


class FriendRequest(api.FriendRequest):
    def __init__(self, tox, pubkey, msg):
        self._author = api.GenericUser(pubkey)
        self._msg = msg
        self._tox = tox

    def get_author(self):
        return self._author

    def get_text(self):
        return self._msg

    def accept(self):
        self._tox.tox_friend_add_norequest(self._author.handle())

    def decline(self):
        # Simply ignore the request to decline it
        pass
