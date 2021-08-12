# -*- coding: utf-8 -*-

import logging
import chatbot.api as api
import discord as discordapi
from .User import User


class FriendRequest(api.FriendRequest):
    def __init__(self, client, request: discordapi.Relationship):
        self._request = request
        self._client = client
        assert self._request.type == discordapi.RelationshipType.incoming_request

    @property
    def author(self):
        return User(self._client, self._request.user)

    @property
    def text(self):
        return ""

    async def accept(self):
        await self.decline()

    async def decline(self):
        # Not available for bot accounts and no longer supported by the non-bot API.
        errstring = "Friend requests are not availabe for bot accounts and are no longer supported by the non-bot API."
        logging.error(errstring)
        await (await self.author.get_chat()).send_message(errstring)
