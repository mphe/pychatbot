# -*- coding: utf-8 -*-

import asyncio
import logging
import discord as discordapi
from chatbot import api
from .User import User
from .ChatMessage import Message
from .Chat import create_chat


class DiscordAPI(api.APIBase):
    def __init__(self, api_id, stub, opts):
        super().__init__(api_id, stub)
        self._opts = opts
        self._discord = None  # type: DiscordClient

    @property
    def version(self) -> str:
        return "{}.{}.{}-{}".format(*discordapi.version_info)

    @property
    def api_name(self) -> str:
        return "Discord"

    @property
    def is_ready(self) -> bool:
        return self._discord is not None and self._discord.is_ready()

    async def start(self) -> None:
        if not self._discord:
            self._discord = DiscordClient(self, loop=asyncio.get_running_loop())
        await self._discord.start(self._opts["token"])

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
        if user is None and self._discord.user.bot:
            user = await self._discord.fetch_user(int(userid))
        if user is None:
            logging.warning("Could not find user with ID %s.\nYou probably don't share any groups and/or don't use a bot account.\nAlso make sure the API is ready.", userid)
            return None
        return User(self, user)

    async def find_chat(self, chatid: str):
        chat = self._discord.get_channel(int(chatid))
        if chat is None:
            chat = await self._discord.fetch_channel(int(chatid))
        if chat is None:
            logging.warning("Could not find chat with ID %s.\nYou probably don't have access to this group and/or don't use a bot account.\nAlso make sure the API is ready.", chatid)
            return None
        return create_chat(self, chat)

    @staticmethod
    def get_default_options():
        return {
            "token": "",
        }

    # extra stuff
    async def create_server(self, _users=()):
        raise NotImplementedError

    async def create_dmgroup(self, _users=()):
        raise NotImplementedError

    def get_invite_link(self):
        return "https://discordapp.com/api/oauth2/authorize?client_id={}&scope=bot&permissions=0".format(str(self._discord.user.id))


# Inheriting discordapi.Client in DiscordAPI would cause overlaps in certain
# functions (like close()).
class DiscordClient(discordapi.Client):
    def __init__(self, apiobj, *args, **kwargs):
        intents = discordapi.Intents.default()
        intents.message_content = True  # pylint: disable=assigning-non-slot
        intents.messages = True  # pylint: disable=assigning-non-slot
        intents.members = True  # pylint: disable=assigning-non-slot
        super().__init__(*args, intents=intents, **kwargs)
        self._firstready = True
        self._api = apiobj

    async def close(self):
        if not self.is_closed():
            logging.info("Closing discord connection")
            await super().close()
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
        self._api._trigger(api.APIEvents.Ready)

    async def on_message(self, msg: discordapi.Message):
        if msg.type == discordapi.MessageType.default:
            if msg.author == self.user:
                self._api._trigger(api.APIEvents.MessageSent, Message(self._api, msg, True))
            else:
                # msg.ack() is not available for bot accounts and no longer supported by the non-bot API.
                self._api._trigger(api.APIEvents.Message, Message(self._api, msg, False))

    async def on_member_join(self, member):
        self._api._trigger(api.APIEvents.GroupMemberJoin, User(self._api, member))

    async def on_member_remove(self, member):
        self._api._trigger(api.APIEvents.GroupMemberLeave, User(self._api, member))

    # private channel
    async def on_group_join(self, _channel, member):
        self._api._trigger(api.APIEvents.GroupMemberJoin, User(self._api, member))

    async def on_group_remove(self, _channel, member):
        self._api._trigger(api.APIEvents.GroupMemberLeave, User(self._api, member))
