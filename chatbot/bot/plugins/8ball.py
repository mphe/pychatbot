# -*- coding: utf-8 -*-

from chatbot.bot import BotPlugin
from chatbot.bot import command
import random


class Plugin(BotPlugin):
    def __init__(self, oldme, bot):
        super(Plugin, self).__init__(oldme, bot)
        self.register_command("missing_8ball", self._question, argc=0, flags=command.CMDFLAG_MISSING)

    @staticmethod
    def get_default_config():
        return { "answers": [ "Yes!", "No!", "Maybe.", ] }

    def _question(self, msg, argv):
        if not argv[-1].endswith("?"):
            raise command.CommandError(command.COMMAND_ERR_NOTFOUND)
        msg.reply(random.choice(self.cfg()["answers"]))
