# -*- coding: utf-8 -*-

import logging
import chatbot.api as api
import discord as discordapi
from .User import User


class FriendRequest(api.FriendRequest):
    def __init__(self, client, request):
        self._request = request # type: discordapi.Relationship
        self._client = client
        assert self._request.type == discordapi.RelationshipType.incoming_request

    def get_author(self):
        return User(self._client, self._request.user)

    def get_text(self):
        return ""

    def accept(self):
        logging.error("Can't accept invites because it was blacklisted from the API.\nDoing so will not work but invalidate the account, thus requiring to revalidate the email address")
        # self._client.run_task(self._request.accept())

    def decline(self):
        self._client.run_task(self._request.delete())
