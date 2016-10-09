# -*- coding: utf-8 -*-

import chatbot.api as api


class FriendRequest(api.FriendRequest):
    def __init__(self, tox, pubkey, msg):
        self._key = pubkey
        self._msg = msg
        self._tox = tox

    def get_username(self):
        """Returns the sender's public key."""
        return self._key

    def get_text(self):
        """Returns the message sent with the friend request."""
        return self._msg

    def accept(self):
        self._tox.tox_friend_add_norequest(self._key)

    def decline(self):
        # Simply ignore the request to decline it
        pass
