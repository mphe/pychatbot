# -*- coding: utf-8 -*-

import chatbot.api as api
from .User import Friend


class GroupInvite(api.GroupInvite):
    def __init__(self, tox, friend_number, cookie):
        self._tox = tox
        self._author = Friend(tox, friend_number)
        self._cookie = cookie

    def get_author(self):
        return self._author

    def accept(self):
        self._tox.tox_conference_join(self._author.number(), self._cookie)

    def decline(self):
        # Simply ignore the request to decline it
        pass
