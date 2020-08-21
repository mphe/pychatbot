# -*- coding: utf-8 -*-

import re
from chatbot.bot import BotPlugin
from chatbot import api


class Plugin(BotPlugin):
    def __init__(self, oldme, bot):
        super(Plugin, self).__init__(oldme, bot)
        self.register_command("tags", self._list, argc=0)
        self.register_event_handler(api.APIEvents.Message, self._on_message)

    # This plugin actually needs a custom reload function so that the default
    # example entry gets overwritten if the user wants to.
    def reload(self):
        self.cfg.load(self.get_default_config(), validate=False, create=True)

    @staticmethod
    def get_default_config():
        return { "lenny": "( ͡° ͜ʖ ͡°)" }

    async def _list(self, msg: api.ChatMessage, _argv):
        """Syntax: tags

        Shows the list of available tags.
        Tags are mapped to specific text and can be used in messages by
        wrapping them in [square brackets].
        If supported by the chat protocol, all tags will be substituted within
        the original message. Otherwise they are sent in a separate message
        in order of appearance.
        """
        if len(self.cfg) == 0:
            await msg.reply("No tags defined")
        else:
            await msg.reply("\n".join([ "[{}]: {}".format(k, v) for k, v in self.cfg.data.items() ]))

    async def _on_message(self, msg: api.ChatMessage):
        tmp = msg.text
        if msg.is_editable:
            for k, v in self.cfg.data.items():
                tmp = tmp.replace("[{}]".format(k), "[ {} ]".format(v))
            if tmp != msg.text:
                await msg.edit(tmp)
        else:
            tags = []
            for i in re.finditer(r"\[(\S+?)\]", tmp):
                if i and i.group(1) in self.cfg.data:
                    tags.append(i.group(1))
            if tags:
                await msg.reply("\n".join([ self.cfg[t] for t in tags ]))
