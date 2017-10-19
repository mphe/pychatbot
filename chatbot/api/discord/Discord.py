# -*- coding: utf-8 -*-
# Requires python3

import logging
import discord as discordapi
from chatbot import api
from chatbot.compat import *
from .User import User
from .ChatMessage import Message


class DiscordAPI(api.APIBase):
    def __init__(self, api_id, stub, opts):
        super(DiscordAPI, self).__init__(api_id, stub)
        self._opts = opts
        self._discord = DiscordClient(self)

    def run(self):
        self._discord.run(self._opts["token"])

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
        return User(self._discord.user)

    def set_display_name(self, name):
        # TODO: maybe use nicknames instead, because usernames can only be
        # changed once an hour apparently
        try:
            self._discord.run_task(self._discord.edit_profile(username=str(name)))
        except:
            logging.error("Couldn't set username (usernames can only be changed once an hour)")

    def create_group(self, users=[]):
        server = self.run_task(self._discord.create_server("New Server"))
        chat = ServerChannel(self, server.default_channel)
        for i in users:
            chat.invite(i)
        return chat

    @staticmethod
    def get_default_options():
        return {
            "token": "",
        }

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
            logging.info("Invite link: " + self._api.get_invite_link())
            self._api._trigger(api.APIEvents.Ready)

    async def on_message(self, msg):
        if msg.type == discordapi.MessageType.default:
            if msg.author == self.user:
                self._api._trigger(api.APIEvents.MessageSent, Message(self._api, msg, True))
            else:
                self._api._trigger(api.APIEvents.Message, Message(self._api, msg, False))

    async def on_member_join(self, member):
        self._api._trigger(api.APIEvents.GroupMemberJoin, User(member))

    async def on_member_remove(self, member):
        self._api._trigger(api.APIEvents.GroupMemberLeave, User(member))

    # private channel
    async def on_group_join(self, channel, user):
        self._api._trigger(api.APIEvents.GroupMemberJoin, User(member))

    async def on_group_remove(self, channel, user):
        self._api._trigger(api.APIEvents.GroupMemberLeave, User(member))
