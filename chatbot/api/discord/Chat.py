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

    @property
    def id(self):
        return self._chat.id

    @property
    def is_id_unique(self):
        return True

    @property
    def is_anonymous(self):
        return False

    async def send_message(self, text):
        await self._chat.send(content=text)

    async def send_action(self, text):
        await self.send_message("*{} {}*".format(
            (await self._client.get_user()).display_name, text))


class PrivateChat(DiscordChat, api.Chat):
    pass


class GuildChat(DiscordChat, api.GroupChat):
    def __init__(self, client, channel):
        super(GuildChat, self).__init__(client, channel)
        self._guild = channel.guild

    async def leave(self):
        if self._guild.owner == self._guild.me:
            await self._guild.delete()
        else:
            await self._guild.leave()

    async def invite(self, user):
        invite = await self._chat.create_invite()
        await user._user.send(content=invite.url)

    @property
    def size(self):
        return self._guild.member_count


class PrivateGroup(DiscordChat, api.GroupChat):
    async def leave(self):
        await self._chat.leave()

    async def invite(self, user):
        await self._chat.add_recipients(user)

    @property
    def size(self):
        return len(self._chat.recipients) + 1
