# -*- coding: utf-8 -*-

from collections import namedtuple
from chatbot.bot.subsystem.plugin import BasePlugin
from chatbot.compat import *


ChatHandle = namedtuple("ChatHandle", [ "password", "chat" ])

class Plugin(BasePlugin):
    def __init__(self, oldme, bot):
        self._bot = bot
        self._bot.register_command("join", self._join)
        self._bot.register_command("join!", self._forcejoin)
        self._bot.register_command("groups", self._listgroups, argc=0)
        self._chats = {}

        if oldme:
            self._chats = oldme._chats
            self._filter()

    def reload(self):
        pass

    def quit(self):
        self._bot.unregister_command("join", "join!", "groups")

    def _filter(self):
        # Filter empty chats
        self._chats = { k: v for k,v in self._chats.items() if v.chat.size() > 0 }

    def _listgroups(self, msg, argv):
        """Syntax: groups
        
        List available groups.
        """
        def iterchats():
            for k,v in self._chats.items():
                yield k + " [password protected]" if v.password else k

        self._filter()
        if not self._chats:
            msg.reply("No groups exist at the moment.")
        else:
            msg.reply("The following groups exist:\n" + "\t\n".join(iterchats()))

    def _forcejoin(self, msg, argv):
        """Syntax: join! <groupname> [password]
        
        Same as `join` but creates the group if it doesn't exist.
        See `join` for further information.
        """
        self._join(msg, argv)

    def _join(self, msg, argv):
        """Syntax: join[!] <groupname> [password]

        Join a groupchat. If `join!` is used, it will be created if it doesn't
        exist.
        The groupname is an identifier for this group, _not_ the group title.
        Specifying a password when creating a new group, requires others to
        provide the password when joining.
        """
        if msg.get_chat().is_anonymous():
            msg.reply("This command is not available in anonymous chats. Please try the private chat.")
            return

        password = argv[2] if len(argv) > 2 else ""

        if argv[1] not in self._chats or self._chats[argv[1]].chat.size() == 0:
            if argv[0] == "join!":
                chat = self._bot.get_API().create_group([msg.get_author()])
                self._chats[argv[1]] = ChatHandle(password, chat)
            else:
                msg.reply("This chat doesn't exist yet, use `join!` to create it.")
        else:
            chat = self._chats[argv[1]]
            if not chat.password or password == chat.password:
                chat.chat.invite(msg.get_author())
            else:
                msg.reply("Wrong password.")