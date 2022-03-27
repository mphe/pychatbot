# -*- coding: utf-8 -*-

from chatbot.bot import BotPlugin, command
import random


class Plugin(BotPlugin):
    def __init__(self, bot):
        super().__init__(bot)
        self.register_command("missing_8ball", self._question, argc=0, flags=command.CommandFlag.Missing)

    @staticmethod
    def get_default_config():
        return {
            "answers": [
                "Yes!",
                "No!",
                "Maybe...",
                "Definitely!",
                "Absolutely not!",
                "I have a really hard time making decisions..."
            ]
        }

    async def _question(self, msg, argv):
        if not argv[-1].endswith("?"):
            raise command.CommandNotFoundError
        await msg.reply(random.choice(self.cfg["answers"]))
