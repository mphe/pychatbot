# -*- coding: utf-8 -*-

import asyncio
import re
import math
import random
from multiprocessing import Array, Process
from chatbot.bot import BotPlugin, command
from chatbot import util


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

    @staticmethod
    async def _clear(msg, _argv):
        """Syntax: clear

        Clear the screen.
        """
        await msg.reply("-" + "\n" * 50 + "-")

    @staticmethod
    def _async_eval_proc(result, expr):
        mathlist = { k: math.__dict__[k] for k in math.__dict__ if not k.startswith("_") }
        try:
            result.value = str(eval(expr, { "__builtins__": None }, mathlist)).encode("utf-8")
        except Exception as e:
            result.value = ("Error: " + str(e))[:256].encode("utf-8")

    async def _calc(self, msg, argv):
        """Syntax: calc <expression>

        Evaluates the given mathematical expression.
        The expression must only contain the following characters:
        a-z A-Z 0-9 . + - * / ( ) or whitespace.
        """
        expr = " ".join(argv[1:])
        if not re.match(r"^[ a-zA-Z0-9\.\+\-\*/\(\)]*$", expr):
            raise command.CommandSyntaxError("Expression contains invalid characters")

        def _async_calc_thread(expr):
            result = Array("c", 256)
            p = Process(target=self._async_eval_proc, args=(result, expr))
            p.start()
            p.join(3)
            if p.is_alive():
                p.terminate()
                p.join()
                return "Expression took too long to evaluate."
            return result.value.decode("utf-8")

        # Start a new thread and from there run a new process for calculation.
        # We need to do this, because a ProcessPoolExecutor can't be killed
        # apparently. Instead it hangs and blocks execution if trying to
        # shutdown() or asyncio.wait_for().
        result = await util.run_in_thread(_async_calc_thread, expr)
        await msg.reply(result)

    @staticmethod
    async def _hex(msg, argv):
        """Syntax: hex <text>

        Convert a given text to hexadecimal.
        If supported by the chat protocol it will replace the user's message.
        """
        text = " ".join([hex(ord(i))[2:].upper() for i in " ".join(argv[1:])])
        await util.edit_or_reply(msg, text)

    @staticmethod
    async def _binary(msg, argv):
        """Syntax: binary <text>

        Convert a given text to binary.
        If supported by the chat protocol it will replace the user's message.
        """
        text = " ".join([bin(ord(i))[2:] for i in " ".join(argv[1:])])
        await util.edit_or_reply(msg, text)

    @staticmethod
    async def _choose(msg, argv):
        """Syntax: choose <option1> [option2] [option3] ...

        Randomly choose one of the given options.
        """
        await msg.reply(random.choice(argv[1:]))

    @staticmethod
    async def _random(msg, argv):
        """Syntax: random <a> [b]

        Randomly choose a number between 0 and <a> or, if b is given, <a> and <b>.
        Both end points are included.
        """
        if len(argv) == 2:
            await msg.reply(str(random.randint(0, int(argv[1]))))
        else:
            await msg.reply(str(random.randint(int(argv[1]), int(argv[2]))))

    @staticmethod
    async def _blockspam(msg, argv):
        """Syntax: blockspam <text> <amount>

        Create a block of text by repeating it for a specific amount of times.
        If supported by the chat protocol it will replace the user's message.
        """
        await util.edit_or_reply(msg, int(argv[2]) * argv[1])

    @staticmethod
    async def _stretch(msg, argv):
        """Syntax: stretch <text> <strength> [offset]

        Repeats every character in <text> after position [offset] <strength> times.
        If supported by the chat protocol it will replace the user's message.
        """
        off = int(argv[3]) if len(argv) > 3 else 0
        strength = int(argv[2])
        out = argv[1][:off] + "".join([strength * i for i in argv[1][off:]])
        await util.edit_or_reply(msg, out)

    @staticmethod
    async def _slap(msg, argv):
        if len(argv) > 2:
            await msg.get_chat().send_action("slaps " + " ".join(argv[1:]))
        else:
            await msg.get_chat().send_action("slaps {} with a fish".format(argv[1]))

    @staticmethod
    async def _slap_german(msg, argv):
        if len(argv) > 2:
            await msg.get_chat().send_action("schlägt " + " ".join(argv[1:]))
        else:
            await msg.get_chat().send_action("schlägt {} mit einem Fisch".format(argv[1]))

    async def _explode(self, msg, _argv):
        await msg.get_chat().send_action("explodes\nRespawn in...")
        for i in range(5, 0, -1):
            await msg.reply(str(i))
            await asyncio.sleep(1)
        msg.get_chat().send_action("is back")

    @staticmethod
    async def _lenny(msg, _argv):
        await msg.reply("( ͡° ͜ʖ ͡°)")
