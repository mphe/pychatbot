# -*- coding: utf-8 -*-

import re
from chatbot.bot.subsystem.plugin import BasePlugin
from chatbot.api import APIEvents
from chatbot.compat import *


class Plugin(BasePlugin):
    def __init__(self, oldme, bot):
        self._bot = bot
        self._bot.register_command("tags", self._list, argc=0)
        self._handle = bot.register_event_handler(APIEvents.Message, self._on_message)
        self._tags = {}
        self.reload()

    def reload(self):
        self._tags = self._bot.get_configmgr().load("tags", {
            "tagname": "<url>"
        }, validate=False, create=True)

    def quit(self):
        self._bot.unregister_command("tags")
        self._handle.unregister()

    def _list(self, msg, argv):
        """Syntax: tags
        
        Shows a list of available tags.
        Tags are mapped to specific URLs and can be used in messages by
        wrapping them in [square brackets].
        If supported by the chat protocol, all tags will be substituted within
        the original message. Otherwise they are sent in a separate message
        in order of appearance.
        """
        msg.reply("\n".join([ "[{}]: {}".format(k, v) for k,v in self._tags.items() ]))

    def _on_message(self, msg):
        tmp = msg.get_text()
        if msg.is_editable():
            for k,v in self._tags.items():
                tmp = tmp.replace("[{}]".format(k), "[ {} ]".format(v))
            if tmp != msg.get_text():
                msg.edit(tmp)
        else:
            tags = []
            for i in re.finditer("\[(\S+?)\]", tmp):
                if i and i.group(1) in self._tags:
                    tags.append(i.group(1))
            if tags:
                msg.reply("\n".join([ "[ {} ]".format(self._tags[t]) for t in tags ]))
