# -*- coding: utf-8 -*-

import random
from chatbot.bot import BotPlugin, command
from urllib import request
from xml.etree import ElementTree
from chatbot import api, util
from typing import List


class Plugin(BotPlugin):
    def __init__(self, oldme, bot):
        super(Plugin, self).__init__(oldme, bot)

        self.register_command("shitpost", self._shitpost, argc=0)

    async def _shitpost(self, msg: api.ChatMessage, argv: List[str]):
        """Syntax: shitpost [random] [count]

        Get the most recent shitpost or a random one if "random" is given as first argument.
        `count` is optional determines how many posts to fetch (max. 50 by default).
        Please mind anit-spam limits when using high count values, bots are affected, too.
        """
        count = 1
        rand = False

        if len(argv) > 1 and argv[1] == "random":
            rand = True
            argv = util.list_shifted(argv)

        if len(argv) > 1:
            try:
                count = int(argv[1])
                if count <= 0:
                    raise ValueError
                count = min(count, self.cfg["max_posts"])
            except ValueError:
                raise command.CommandSyntaxError("`count` is not a valid number.")

        urls = await get_shitpost_urls(count, rand)

        # Split in multiple messages, because Discord only previews 5 URLs per message.
        for chunk in util.iter_chunks(urls, self.cfg["split_messages"]):
            await msg.reply("\n".join(chunk))

    @staticmethod
    def get_default_config():
        return {
            "split_messages": 1,  # Split in messages of N URLs
            "max_posts": 50,
        }


async def get_shitpost_urls(num: int, rand: bool) -> List[str]:
    def cb(rand: bool) -> List[str]:
        start = random.randint(0, get_num_posts() - 1) if rand else 0
        posts = query_tumblr_posts(num, start)
        return extract_urls(posts)

    return await util.run_in_thread(cb, rand)


def get_num_posts() -> int:
    xml = query_tumblr_posts(0)
    return int(xml.getroot().find("posts").get("total"))


def extract_urls(posts: ElementTree.ElementTree) -> List[str]:
    return [ i.find("photo-url").text for i in posts.getroot().find("posts") ]


def query_tumblr_posts(num=1, start=0) -> ElementTree.ElementTree:
    """Query for tumblr posts, by default top post."""
    requesturl = "https://shitpostbot5k.tumblr.com/api/read?type=photo&num={}&start={}".format(num, start)
    return ElementTree.parse(request.urlopen(requesturl))
