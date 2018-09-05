# -*- coding: utf-8 -*-

from chatbot.compat import *
import discord as discordapi
import chatbot.api as api
import logging


def create_chat(client, channel):
    if type(channel) is discordapi.abc.GuildChannel:
        return GroupChat(client, channel)
    elif type(channel) is discordapi.DMChannel:
        return PrivateChat(client, channel)
    else:
        return PrivateGroup(client, channel)


class DiscordChat(object):
    def __init__(self, client, chat):
        self._client = client
        self._chat = chat

    def id(self):
        return self._chat.id

    def send_message(self, text):
        self._client.run_task(self._chat.send(content=text))

    def send_action(self, text):
        self.send_message("*{} {}*".format(self._client.get_user().display_name(), text))

    def is_anonymous(self):
        return False


class PrivateChat(DiscordChat, api.Chat): pass


class GuildChat(DiscordChat, api.GroupChat):
    def __init__(self, client, channel):
        super(GuildChat, self).__init__(client, channel)
        self._left = False
        self._guild = channel.guild

    def leave(self):
        self._left = True
        if self._guild.owner == self._guild.me:
            self._client.run_task(self._guild.delete())
        else:
            self._client.run_task(self._guild.leave())

    def invite(self, user):
        invite = self._client.run_task(self._chat.create_invite())
        self._client.run_task(user._user.send(content=invite.url))

    def size(self):
        return 0 if self._left else self._guild.member_count


class PrivateGroup(DiscordChat, api.GroupChat):
    def __init__(self, client, channel):
        super(PrivateGroup, self).__init__(client, channel)
        self._left = False

    def leave(self):
        self._left = True
        self._client.run_task(self._chat.leave())

    def invite(self, user):
        self._client.run_task(self._chat.add_recipients(user))

    def size(self):
        return 0 if self._left else len(self._chat.recipients)
