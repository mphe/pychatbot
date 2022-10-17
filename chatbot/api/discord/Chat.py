# -*- coding: utf-8 -*-

import discord as discordapi
from chatbot import api
from typing import Union, cast


def create_chat(client, channel):
    if isinstance(channel, discordapi.TextChannel):
        return GuildChat(client, channel)
    if isinstance(channel, discordapi.DMChannel):
        return PrivateChat(client, channel)
    if isinstance(channel, discordapi.GroupChannel):
        return PrivateGroup(client, channel)
    return None


class DiscordChat():
    """Base-class for Discord chats."""
    def __init__(self, client: api.APIBase, chat: Union[discordapi.TextChannel, discordapi.DMChannel, discordapi.GroupChannel]):
        assert chat is not None
        assert client is not None

        self._client = client
        self._chat = chat

    @property
    def id(self) -> str:
        return str(self._chat.id)

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
        super().__init__(client, channel)
        self._guild = channel.guild

    async def leave(self):
        if self._guild.owner == self._guild.me:
            await self._guild.delete()
        else:
            await self._guild.leave()

    async def invite(self, user):
        invite = await cast(discordapi.TextChannel, self._chat).create_invite()
        await user._user.send(content=invite.url)

    @property
    def size(self):
        return self._guild.member_count


class PrivateGroup(DiscordChat, api.GroupChat):
    async def leave(self):
        await cast(discordapi.GroupChannel, self._chat).leave()

    async def invite(self, _user):
        # This seems to be not available anymore
        raise NotImplementedError

    @property
    def size(self):
        return len(cast(discordapi.GroupChannel, self._chat).recipients) + 1
