# -*- coding: utf-8 -*-

import asyncio
import logging
import discord as discordapi
from chatbot import api
from .User import User
from .FriendRequest import FriendRequest
from .ChatMessage import Message
from .Chat import create_chat


class DiscordAPI(api.APIBase):
    def __init__(self, api_id, stub, opts):
        super(DiscordAPI, self).__init__(api_id, stub)
        self._opts = opts
        self._discord = None  # type: DiscordClient

    @property
    def version(self) -> str:
        return "{}.{}.{}-{}".format(*discordapi.version_info)

    @property
    def api_name(self) -> str:
        return "Discord"

    async def start(self) -> None:
        if not self._discord:
            self._discord = DiscordClient(self, loop=asyncio.get_running_loop())

        await self._discord.start(self._opts["token"], bot=self._opts["bot"])

    async def cleanup(self) -> None:
        pass

    async def close(self) -> None:
        await self._discord.close()

    async def get_user(self) -> User:
        return User(self, self._discord.user)

    async def set_display_name(self, name) -> None:
        if name == (await self.get_user()).display_name:
            return

        try:
            # TODO: maybe use nicknames instead, because usernames can only be
            # changed once an hour apparently
            await self._discord.user.edit(username=str(name))
        except discordapi.HTTPException:
            logging.error("Couldn't set username (usernames can only be changed once an hour)")

    # TODO: needs testing
    async def create_group(self, users=()):
        if self._discord.user.bot or len(users) >= 10 or len(users) < 2:
            return await self.create_server(users)
        return await self.create_dmgroup(users)

    async def find_user(self, userid: str) -> User:
        user = self._discord.get_user(int(userid))
        if user is None:
            logging.warning("Could not find user with ID %s", userid)
            return None
        return User(self, user)

    async def find_chat(self, chatid: str):
        chat = self._discord.get_channel(int(chatid))
        if chat is None:
            logging.warning("Could not find chat with ID %s", chatid)
            return None
        return create_chat(self, chat)

    @staticmethod
    def get_default_options():
        return {
            "token": "",
            "bot": True
        }

    # extra stuff
    async def create_server(self, users=()):
        raise NotImplementedError
        # TODO: needs testing
        # server = await self._discord.create_guild("New Server")
        # chat = create_chat(self, server.text_channels[0])
        # for i in users:
        #     chat.invite(i)
        # return chat

    async def create_dmgroup(self, users=()):
        raise NotImplementedError
        # TODO: needs testing
        # assert len(users) >= 2 and len(users) < 10
        # return create_chat(
        #     self, await self._discord.user.create_group(*[ i._user for i in users ]))

    def get_invite_link(self):
        return "https://discordapp.com/api/oauth2/authorize?client_id={}&scope=bot&permissions=0".format(str(self._discord.user.id))


# Inheriting discordapi.Client in DiscordAPI would cause overlaps in certain
# functions (like close()).
class DiscordClient(discordapi.Client):
    def __init__(self, apiobj, *args, **kwargs):
        super(DiscordClient, self).__init__(*args, **kwargs)
        self._firstready = True
        self._api = apiobj

    async def close(self):
        if not self.is_closed():
            logging.info("Closing discord connection")
            await super(DiscordClient, self).close()
            self._firstready = True

    # Events
    async def on_ready(self):
        logging.info("(Re-)Connected to Discord.")
        if not self._firstready:
            return

        self._firstready = False
        if self.user.bot:
            logging.info("Invite link: %s", self._api.get_invite_link())
        else:
            logging.info("Username: %s", (await self._api.get_user()).username)
        await self._api._trigger(api.APIEvents.Ready)

        # Process pending friend requests
        for i in self.user.relationships:
            await self.on_relationship_add(i)

    async def on_message(self, msg: discordapi.Message):
        if not self.user.bot:
            await msg.ack()

        if msg.type == discordapi.MessageType.default:
            if msg.author == self.user:
                await self._api._trigger(api.APIEvents.MessageSent, Message(self._api, msg, True))
            else:
                # Preload private chat because it can't be created in a non-async
                # function because the result isn't returned instantly.
                # TODO: necessary?
                # if self.user.bot or msg.author.is_friend():
                #     await msg.author.create_dm()

                await self._api._trigger(api.APIEvents.Message, Message(self._api, msg, False))
                # await util.testing.test_message(Message(self._api, msg, False), self._api)

    async def on_relationship_add(self, relationship):
        if relationship.type == discordapi.RelationshipType.incoming_request:
            await self._api._trigger(api.APIEvents.FriendRequest, FriendRequest(self._api, relationship))

    async def on_member_join(self, member):
        await self._api._trigger(api.APIEvents.GroupMemberJoin, User(self._api, member))

    async def on_member_remove(self, member):
        await self._api._trigger(api.APIEvents.GroupMemberLeave, User(self._api, member))

    # private channel
    async def on_group_join(self, _channel, member):
        await self._api._trigger(api.APIEvents.GroupMemberJoin, User(self._api, member))

    async def on_group_remove(self, _channel, member):
        await self._api._trigger(api.APIEvents.GroupMemberLeave, User(self._api, member))
