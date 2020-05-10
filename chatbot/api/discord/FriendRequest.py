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

    def get_author(self):
        return User(self._client, self._request.user)

    def get_text(self):
        return ""

    async def accept(self):
        errstring = "Can't accept friend requests because it was blacklisted from the API.\nDoing so will not work but invalidate the account, thus requiring to revalidate the email address."
        logging.error(errstring)
        await (await self.get_author().get_chat()).send_message(errstring)
        await self.decline()
        # await self._request.accept()

    async def decline(self):
        await self._request.delete()
