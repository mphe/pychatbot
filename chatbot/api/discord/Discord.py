# -*- coding: utf-8 -*-
# Requires python3
# Requires discord.py

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
        self._discord = DiscordClient(self)


    def run(self):
        self._discord.run(self._opts["token"], bot=self._opts["bot"])

    def quit(self):
        if not self._discord.is_closed:
            self.run_task(self._discord.quit())

    def close(self):
        self.run_task(self._discord.close())

    def version(self):
        return "{}.{}.{}-{}".format(*discordapi.version_info)

    def api_name(self):
        return "Discord"

    def get_user(self):
        return User(self, self._discord.user)

    def set_display_name(self, name):
        if (name == self.get_user().display_name()):
            return

        try:
            # TODO: maybe use nicknames instead, because usernames can only be
            # changed once an hour apparently
            self.run_task(self._discord.user.edit(username=str(name)))
        except HTTPException:
            logging.error("Couldn't set username (usernames can only be changed once an hour)")

    # TODO: needs testing
    def create_group(self, users=[]):
        if self._discord.user.bot or len(users) >= 10 or len(users) < 2:
            return self.create_server(users)
        else:
            return self.create_dmgroup(users)

    def find_user(self, userid):
        user = self._discord.get_user(userid)
        return User(self, user) if user else None

    def find_chat(self, chatid):
        return create_chat(self, self._discord.get_channel(chatid))


    @staticmethod
    def get_default_options():
        return {
            "token": "",
            "bot": True
        }


    # extra stuff
    def create_server(self, users=[]):
        raise NotImplementedError
        # TODO: needs testing
        # server = self.run_task(self._discord.create_guild("New Server"))
        # chat = create_chat(self, server.text_channels[0])
        # for i in users:
        #     chat.invite(i)
        # return chat

    def create_dmgroup(self, users=[]):
        raise NotImplementedError
        # TODO: needs testing
        # assert len(users) >= 2 and len(users) < 10
        # return create_chat(self, self.run_task(
        #     self._discord.user.create_group(*[ i._user for i in users ])))


    def get_invite_link(self):
        return "https://discordapp.com/api/oauth2/authorize?client_id={}&scope=bot&permissions=0".format(str(self._discord.user.id))

    def run_task(self, call):
        """Shortcut for calling coroutines from non-coroutines"""
        self._discord.loop.create_task(call)



# Inheriting discordapi.Client in DiscordAPI would cause overlaps in certain
# functions (like close()).

class DiscordClient(discordapi.Client):
    def __init__(self, apiobj):
        super(DiscordClient, self).__init__()
        self._firstready = True
        self._api = apiobj

    def quit(self):
        self.logout()
        self._firstready = True


    # Events
    async def on_ready(self):
        logging.info("(Re-)Connected to Discord.")
        if self._firstready:
            self._firstready = False
            if self.user.bot:
                logging.info("Invite link: " + self._api.get_invite_link())
            else:
                logging.info("Username: " + self._api.get_user().username())
            self._api._trigger(api.APIEvents.Ready)

            for i in self.user.relationships:
                await self.on_relationship_add(i)

    async def on_message(self, msg):
        if not self.user.bot:
            self._api.run_task(msg.ack())
        if msg.type == discordapi.MessageType.default:
            if msg.author == self.user:
                self._api._trigger(api.APIEvents.MessageSent, Message(self._api, msg, True))
            else:
                # Preload private chat because it can't be created in a non-async
                # function because the result isn't returned instantly.
                if self.user.bot or msg.author.is_friend():
                    await msg.author.create_dm()

                self._api._trigger(api.APIEvents.Message, Message(self._api, msg, False))
                # api.testing.test_message(Message(self._api, msg, False), self._api)

    async def on_relationship_add(self, relationship):
        if relationship.type == discordapi.RelationshipType.incoming_request:
            self._api._trigger(api.APIEvents.FriendRequest, FriendRequest(self._api, relationship))

    async def on_member_join(self, member):
        self._api._trigger(api.APIEvents.GroupMemberJoin, User(self._api, member))

    async def on_member_remove(self, member):
        self._api._trigger(api.APIEvents.GroupMemberLeave, User(self._api, member))

    # private channel
    async def on_group_join(self, channel, member):
        self._api._trigger(api.APIEvents.GroupMemberJoin, User(self._api, member))

    async def on_group_remove(self, channel, member):
        self._api._trigger(api.APIEvents.GroupMemberLeave, User(self._api, member))
