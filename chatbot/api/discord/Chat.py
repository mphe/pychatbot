# -*- coding: utf-8 -*-

from chatbot.compat import *
import discord as discordapi
import chatbot.api as api
import logging


# Discord doesn't differentiate between normal and group chats, only between
# private channels and server channels
class ServerChannel(api.GroupChat):
    def __init__(self, client, chat):
        self._client = client
        self._isgroup = True
        self._chat = chat
        self._left = False

        # Only Channel is supported for now
        if type(chat) is discordapi.PrivateChannel:
            raise NotImplementedError

    def id(self):
        return self._chat.id

    def send_message(self, text):
        self._client.run_task(self._client._discord.send_message(self._chat, content=text))

    def send_action(self, text):
        # TODO: maybe add the name explictly
        self.send_message("*{} {}*".format(self._client.get_user().display_name(), text))

    def type(self):
        return api.ChatType.Normal

    def is_anonymous(self):
        return False

    def type(self):
        return api.ChatType.Group if self._isgroup else api.ChatType.Normal

    def leave(self):
        self._left = True
        if self._chat.server.owner == self._chat.server.me:
            self._client.run_task(self._client._discord.delete_server(self._chat.server))
        else:
            self._client.run_task(self._client._discord.leave_server(self._chat.server))

    def invite(self, user):
        invite = self._client.run_task(self._client._discord.create_invite(self._chat))
        self._client.run_task(self._client._discord.send_message(user._user, invite.url))

    def size(self):
        return self._chat.server.member_count if not self._left else 0
