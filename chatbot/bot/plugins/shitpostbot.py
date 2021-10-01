# -*- coding: utf-8 -*-

import random
from chatbot.bot import BotPlugin, command
from urllib import request
from xml.etree import ElementTree
from chatbot import api, util
from typing import List, Set
import logging
import asyncio


class Plugin(BotPlugin):
    def __init__(self, oldme, bot):
        self._autochats: Set[str] = set()
        self._timer: asyncio.Task = None

        super().__init__(oldme, bot)

        self.register_command("shitpost", self._shitpost, argc=0)
        self.register_command("autoshitpost", self._auto_shitpost, argc=0)

    def reload(self):
        super().reload()
        self._autochats = set(self.cfg["autochats"])
        self._start_timer()

    def quit(self):
        self._stop_timer()
        super().quit()

    async def _shitpost(self, msg: api.ChatMessage, argv: List[str]):
        """Syntax: shitpost [random] [count]

        Get the most recent shitpost or a random one if "random" is given as first argument.
        `count` is optional determines how many posts to fetch (max. 50 by default).
        Please mind anit-spam limits when using high count values, bots are affected, too.
        """
        rand = len(argv) > 1 and argv[1] == "random"
        count = min(command.get_argument(argv, 1 if not rand else 2, 1, int), self.cfg["max_posts"])
        await self._send_shitpost(msg.chat, count, rand)

    async def _auto_shitpost(self, msg: api.ChatMessage, _argv: List[str]):
        """Syntax: autoshitpost

        Toggle automatically posting the most recent shitpost to the current chat every 30 minutes.
        """
        chatid = msg.chat.id

        try:
            self._autochats.remove(chatid)
            if not self._autochats:
                self._stop_timer()
            await msg.reply("Auto-Shitposting deactivated!")
        except KeyError:
            self._autochats.add(chatid)
            self._start_timer()
            await msg.reply("Auto-Shitposting activated!")

        # Update config
        self.cfg["autochats"] = list(self._autochats)
        self.cfg.write()

    async def _timer_callback(self):
        last_url = ""

        while True:
            await asyncio.sleep(30 * 60)

            # Fetch URL and check if it is not the same as before
            urls = await get_shitpost_urls(1, False)

            if urls[0] != last_url:
                last_url = urls[0]
                for chatid in self._autochats:
                    if chat := await self.bot.api.find_chat(chatid):
                        await self._send_urls(chat, urls)

    async def _send_shitpost(self, chat: api.Chat, count: int, rand: bool):
        urls = await get_shitpost_urls(count, rand)
        self._send_urls(chat, urls)

    async def _send_urls(self, chat: api.Chat, urls: List[str]):
        """Split in multiple messages, because Discord only previews 5 URLs per message, Telegram only 1,  etc."""
        for chunk in util.iter_chunks(urls, self._get_split_messages()):
            await chat.send_message("\n".join(chunk))

    def _start_timer(self):
        if not self._timer:
            self._timer = asyncio.create_task(self._timer_callback())
            logging.debug("Auto-Shitpost task started")

    def _stop_timer(self):
        if self._timer and not self._timer.done():
            self._timer.cancel()
            logging.debug("Auto-Shitpost task stopped")
        self._timer = None

    def _get_split_messages(self) -> int:
        urls = self.cfg["urls_per_message"]
        if urls <= 0:
            if self.bot.api.api_id == "discord":
                return 5
            return 1
        return urls

    @staticmethod
    def get_default_config():
        return {
            "urls_per_message": 0,  # Split in messages of N URLs, 0 for auto
            "max_posts": 50,
            "autochats": [],
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
