# -*- coding: utf-8 -*-

from chatbot.compat import *
import discord as discordapi
import chatbot.api as api


class User(api.User):
    def __init__(self, user):
        self._user = user

    def handle(self):
        return "{}#{}".format(self._user.name, str(self._user.discriminator))

    def display_name(self):
        return self._user.display_name
