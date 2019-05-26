# -*- coding: utf-8 -*-

import asyncio
import re
import math
import random
from time import sleep
from multiprocessing import Process, Array
from chatbot.bot import BotPlugin, command, Bot
from chatbot import util
from chatbot.compat import *

class Plugin(BotPlugin):
    def __init__(self, oldme, bot):
        super(Plugin, self).__init__(oldme, bot)
        self.register_command("clear", self._clear, argc=0)
        self.register_command("calc", self._calc)
        self.register_command("hex", self._hex)
        self.register_command("binary", self._binary)
        self.register_command("choose", self._choose)
        self.register_command("random", self._random)
        self.register_command("blockspam", self._blockspam, argc=2)
        self.register_command("stretch", self._stretch, argc=2)
        self.register_command("slap", self._slap)
        self.register_command("schlag", self._slap_german)
        self.register_command("explode", self._explode, argc=0)
        self.register_command("lenny", self._lenny, argc=0)

    def _clear(self, msg, argv):
        """Syntax: clear

        Clear the screen.
        """
        msg.reply("-" + "\n" * 50 + "-")

    def _calc(self, msg, argv):
        """Syntax: calc <expression>

        Evaluates the given mathematical expression.
        The expression must only contain the following characters:
        a-z A-Z 0-9 . + - * / ( ) or whitespace.
        """
        expr = " ".join(argv[1:])
        if not re.match(r"^[ a-zA-Z0-9\.\+\-\*/\(\)]*$", expr):
            raise command.CommandError(
                command.COMMAND_ERR_SYNTAX, 'Expression contains invalid characters')

        result = Array("c", 256)
        p = Process(target=self._async_eval, args=(result, expr))
        p.start()
        p.join(3)
        if p.is_alive():
            p.terminate()
            p.join()
            msg.reply("Expression took too long to evaluate.")
        else:
            msg.reply(result.value.decode("utf-8"))

    @staticmethod
    def _async_eval(result, expr):
        mathlist = { k: math.__dict__[k] for k in math.__dict__ if not k.startswith("_") }
        try:
            result.value = str(eval(expr, { "__builtins__": None }, mathlist)).encode("utf-8")
        except Exception as e:
            result.value = ("Error: " + str(e))[:256].encode("utf-8")

    def _hex(self, msg, argv):
        """Syntax: hex <text>

        Convert a given text to hexadecimal.
        If supported by the chat protocol it will replace the user's message.
        """
        text = " ".join([hex(ord(i))[2:].upper() for i in " ".join(argv[1:])])
        util.edit_or_reply(msg, text)

    def _binary(self, msg, argv):
        """Syntax: binary <text>

        Convert a given text to binary.
        If supported by the chat protocol it will replace the user's message.
        """
        text = " ".join([bin(ord(i))[2:] for i in " ".join(argv[1:])])
        util.edit_or_reply(msg, text)

    def _choose(self, msg, argv):
        """Syntax: choose <option1> [option2] [option3] ...

        Randomly choose one of the given options.
        """
        msg.reply(random.choice(argv[1:]))

    def _random(self, msg, argv):
        """Syntax: random <a> [b]

        Randomly choose a number between 0 and <a> or, if b is given, <a> and <b>.
        Both end points are included.
        """
        if len(argv) == 2:
            msg.reply(str(random.randint(0, int(argv[1]))))
        else:
            msg.reply(str(random.randint(int(argv[1]), int(argv[2]))))

    def _blockspam(self, msg, argv):
        """Syntax: blockspam <text> <amount>

        Create a block of text by repeating it for a specific amount of times.
        If supported by the chat protocol it will replace the user's message.
        """
        util.edit_or_reply(msg, int(argv[2]) * argv[1])

    def _stretch(self, msg, argv):
        """Syntax: stretch <text> <strength> [offset]

        Repeats every character in <text> after position [offset] <strength> times.
        If supported by the chat protocol it will replace the user's message.
        """
        off = int(argv[3]) if len(argv) > 3 else 0
        strength = int(argv[2])
        out = argv[1][:off] + "".join([strength * i for i in argv[1][off:]])
        util.edit_or_reply(msg, out)

    def _slap(self, msg, argv):
        if len(argv) > 2:
            msg.get_chat().send_action("slaps " + " ".join(argv[1:]))
        else:
            msg.get_chat().send_action("slaps {} with a fish".format(argv[1]))

    def _slap_german(self, msg, argv):
        if len(argv) > 2:
            msg.get_chat().send_action("schlägt " + " ".join(argv[1:]))
        else:
            msg.get_chat().send_action("schlägt {} mit einem Fisch".format(argv[1]))

    def _explode(self, msg, argv):
        async def _async_explode(chat):
            for i in range(5, 0, -1):
                chat.send_message(str(i))
                await asyncio.sleep(1)
            chat.send_action("is back")

        def _thread_explode(chat):
            for i in range(5, 0, -1):
                chat.send_message(str(i))
                time.sleep(1)
            chat.send_action("is back")

        msg.get_chat().send_action("explodes\nRespawn in...")
        if self.bot().get_API().api_id() == "discord":
            asyncio.get_event_loop().create_task(_async_explode(msg.get_chat()))
        else:
            # TODO: separate thread?
            _thread_explode(msg.get_chat())

    def _lenny(self, msg, argv):
        msg.get_chat().send_message("( ͡° ͜ʖ ͡°)");
