# -*- coding: utf-8 -*-

import chatbot.api as api
import User


class FriendRequest(api.FriendRequest):
    def __init__(self, tox, pubkey, msg):
        self._author = User.User(pubkey, "Unknown")
        self._msg = msg
        self._tox = tox

    def get_author(self):
        return self._author

    def get_text(self):
        return self._msg

    def accept(self):
        self._tox.tox_friend_add_norequest(self._key)

    def decline(self):
        # Simply ignore the request to decline it
        pass
