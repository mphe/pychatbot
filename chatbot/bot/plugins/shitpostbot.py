# -*- coding: utf-8 -*-

import asyncio
import random
from concurrent.futures import ThreadPoolExecutor
from chatbot.bot import BotPlugin
from urllib import request
from xml.etree import ElementTree
from chatbot import api, util


class Plugin(BotPlugin):
    def __init__(self, oldme, bot):

        super(Plugin, self).__init__(oldme, bot)

        self.register_command("shitpost", self._shitpost, argc=0)

    @classmethod
    async def _shitpost(cls, msg: api.ChatMessage, argv):
        """Syntax: shitpost [random]

        Get the most recent shitpost or a random one if "random" is given as first argument.
        """
        await msg.reply(await cls._get_shitpost_url(len(argv) > 1 and argv[1] == "random"))

    @classmethod
    async def _get_shitpost_url(cls, rand: bool = False):
        def cb(rand: bool) -> str:
            start = random.randint(0, cls._get_num_posts() - 1) if rand else 0
            xml = cls._query_tumblr(1, start)
            return xml.getroot().find("posts")[0].find("photo-url").text

        return await util.run_in_thread(cb, rand)

    @classmethod
    def _get_num_posts(cls):
        xml = cls._query_tumblr(0)
        return int(xml.getroot().find("posts").get("total"))

    @staticmethod
    def _query_tumblr(num=1, start=0):
        """Query for tumblr posts, by default top post."""
        requesturl = "https://shitpostbot5k.tumblr.com/api/read?type=photo&num={}&start={}".format(num, start)
        return ElementTree.parse(request.urlopen(requesturl))
