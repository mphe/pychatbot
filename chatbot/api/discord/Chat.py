# -*- coding: utf-8 -*-

import discord as discordapi
import chatbot.api as api
from typing import Union


def create_chat(client, channel):
    if isinstance(channel, discordapi.abc.GuildChannel):
        return GuildChat(client, channel)
    if isinstance(channel, discordapi.DMChannel):
        return PrivateChat(client, channel)
    if isinstance(channel, discordapi.GroupChannel):
        return PrivateGroup(client, channel)
    return None


class DiscordChat:
    """Base-class for Discord chats."""
    def __init__(self, client: api.APIBase, chat: Union[discordapi.abc.GuildChannel, discordapi.abc.PrivateChannel]):
        assert chat is not None
        assert client is not None

        self._client = client
        self._chat = chat

    def id(self):
        return self._chat.id

    def is_id_unique(self):
        return True

    async def send_message(self, text):
        await self._chat.send(content=text)

    async def send_action(self, text):
        await self.send_message("*{} {}*".format(
            (await self._client.get_user()).display_name(), text))

    def is_anonymous(self):
        return False


class PrivateChat(DiscordChat, api.Chat):
    pass


class GuildChat(DiscordChat, api.GroupChat):
    def __init__(self, client, channel):
        super(GuildChat, self).__init__(client, channel)
        self._left = False
        self._guild = channel.guild

    async def leave(self):
        self._left = True
        if self._guild.owner == self._guild.me:
            await self._guild.delete()
        else:
            await self._guild.leave()

    async def invite(self, user):
        invite = await self._chat.create_invite()
        await user._user.send(content=invite.url)

    def size(self):
        return 0 if self._left else self._guild.member_count


class PrivateGroup(DiscordChat, api.GroupChat):
    def __init__(self, client, channel):
        super(PrivateGroup, self).__init__(client, channel)
        self._left = False

    async def leave(self):
        self._left = True
        await self._chat.leave()

    async def invite(self, user):
        await self._chat.add_recipients(user)

    def size(self):
        return 0 if self._left else len(self._chat.recipients) + 1
