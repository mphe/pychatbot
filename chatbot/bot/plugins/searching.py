# -*- coding: utf-8 -*-

from chatbot.bot.subsystem.plugin import BasePlugin
from chatbot.compat import *


class Plugin(BasePlugin):
    urls = {
        "duden":     "https://www.duden.de/suchen/dudenonline/{}",
        "wikipedia": "https://en.wikipedia.org/wiki/Special:Search?search={}",
        "google":    "https://www.google.com/search?q={}",
        "youtube":   "https://www.youtube.com/results?search_query={}",
        "bisafans":  "https://www.bisafans.de/suchbisa.php?q={}",
        "translate": "https://translate.google.com/#{}"
    }

    def __init__(self, oldme, bot):
        self._bot = bot
        for i in Plugin.urls:
            if i != "translate":
                self._bot.register_command(i, self._search)
        self._bot.register_command("translate", self._translate, argc=3)

    def reload(self):
        pass

    def quit(self):
        for i in Plugin.urls:
            self._bot.unregister_command(i)

    @staticmethod
    def _generate_url(url, argv):
        return Plugin.urls[url].format("%20".join(argv))

    def _search(self, msg, argv):
        """Syntax: site <search string> [search string 2]...
        
        Generate a search link for a specific website.
        site is a placeholder for the command name and can be any of the
        following: google, wikipedia, youtube, duden, bisafans.
        """
        msg.reply(self._generate_url(argv[0], argv[1:]))

    def _translate(self, msg, argv):
        """Syntax: translate <src> <dest> <text>

        Translate <text> from one language to another using Google Translator.
        <src> is the original language, <dst> the new language.
        """
        argv[3] = "{}/{}/{}".format(argv[1], argv[2], argv[3])
        msg.reply(self._generate_url(argv[0], argv[3:]))
