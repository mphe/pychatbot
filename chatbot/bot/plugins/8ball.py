# -*- coding: utf-8 -*-

import random
from chatbot.bot.subsystem.plugin import BasePlugin
from chatbot.bot.subsystem import command
from chatbot.compat import *

random.seed()

class Plugin(BasePlugin):
    def __init__(self, oldme, bot):
        self._bot = bot
        self._bot.register_command("missing_8ball", self._question,
                                   argc=0, flags=command.CMDFLAG_MISSING)
        self._answers = []
        self.reload()

    def reload(self):
        self._answers = self._bot.get_configmgr().load_update("8ball", {
            "answers": [ "Yes!", "No!", "Maybe.", ],
        })["answers"]

    def quit(self):
        self._bot.unregister_command("missing_8ball")

    def _question(self, msg, argv):
        if not argv[-1].endswith("?"):
            raise command.CommandError(command.COMMAND_ERR_NOTFOUND)
        msg.reply(random.choice(self._answers))
