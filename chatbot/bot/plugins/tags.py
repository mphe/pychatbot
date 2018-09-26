# -*- coding: utf-8 -*-

import re
from chatbot.bot import BotPlugin
from chatbot.api import APIEvents
from chatbot.compat import *


class Plugin(BotPlugin):
    def __init__(self, oldme, bot):
        super(Plugin, self).__init__(oldme, bot)
        self.register_command("tags", self._list, argc=0)
        self.register_event_handler(APIEvents.Message, self._on_message)

    # This plugin actually needs a custom reload function so that the default
    # example entry gets overwritten.
    def reload(self):
        self._cfg = self.bot().get_configmgr().load(
            self.name(), self.get_default_config(), validate=False, create=True)

    @staticmethod
    def get_default_config():
        return { "tagname": "<url>" }

    def _list(self, msg, argv):
        """Syntax: tags
        
        Shows a list of available tags.
        Tags are mapped to specific URLs and can be used in messages by
        wrapping them in [square brackets].
        If supported by the chat protocol, all tags will be substituted within
        the original message. Otherwise they are sent in a separate message
        in order of appearance.
        """
        if len(self.cfg()) == 0:
            msg.reply("No tags defined")
        else:
            msg.reply("\n".join([ "[{}]: {}".format(k, v) for k,v in self.cfg().items() ]))

    def _on_message(self, msg):
        tmp = msg.get_text()
        if msg.is_editable():
            for k,v in self.cfg().items():
                tmp = tmp.replace("[{}]".format(k), "[ {} ]".format(v))
            if tmp != msg.get_text():
                msg.edit(tmp)
        else:
            tags = []
            for i in re.finditer("\[(\S+?)\]", tmp):
                if i and i.group(1) in self.cfg():
                    tags.append(i.group(1))
            if tags:
                msg.reply("\n".join([ "[ {} ]".format(self.cfg()[t]) for t in tags ]))
