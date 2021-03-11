# -*- coding: utf-8 -*-

from chatbot.bot import BotPlugin


class Plugin(BotPlugin):
    urls = {
        "duden":     "https://www.duden.de/suchen/dudenonline/{}",
        "wikipedia": "https://en.wikipedia.org/wiki/Special:Search?search={}",
        "google":    "https://www.google.com/search?q={}",
        "youtube":   "https://www.youtube.com/results?search_query={}",
        "bisafans":  "https://www.bisafans.de/suchbisa.php?q={}",
        "translate": "https://translate.google.com/#{}"
    }

    def __init__(self, oldme, bot):
        super().__init__(oldme, bot)
        for i in Plugin.urls:
            if i != "translate":
                self.register_command(i, self._search)
        self.register_command("translate", self._translate, argc=3)

    @staticmethod
    def _generate_url(url, argv):
        return Plugin.urls[url].format("%20".join(argv))

    async def _search(self, msg, argv):
        """Syntax: site <search string> [search string 2]...

        Generate a search link for a specific website.
        site is a placeholder for the command name and can be any of the
        following: google, wikipedia, youtube, duden, bisafans.
        """
        await msg.reply(self._generate_url(argv[0], argv[1:]))

    async def _translate(self, msg, argv):
        """Syntax: translate <src> <dest> <text>

        Translate <text> from one language to another using Google Translator.
        <src> is the original language, <dst> the new language.
        """
        argv[3] = "{}/{}/{}".format(argv[1], argv[2], argv[3])
        await msg.reply(self._generate_url(argv[0], argv[3:]))
