# -*- coding: utf-8 -*-

import asyncio
import re
import math
import random
from multiprocessing import Array, Process
from chatbot import util, api, bot

RE_ROLL = re.compile(r"(\d*)\s*d\s*(\d+)")


class Plugin(bot.BotPlugin):
    def __init__(self, bot_):
        super().__init__(bot_)
        self.register_command("clear", self._clear, argc=0)
        self.register_command("calc", self._calc)
        self.register_command("hex", self._hex)
        self.register_command("binary", self._binary)
        self.register_command("choose", self._choose)
        self.register_command("random", self._random)
        self.register_command("blockspam", self._blockspam, argc=2)
        self.register_command("stretch", self._stretch, argc=2)
        self.register_command("slap", self._slap)
        self.register_command("explode", self._explode, argc=0)
        self.register_command("lenny", self._lenny, argc=0)
        self.register_command("roll", self._roll, argc=1)

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
            result.value = str(eval(expr, { "__builtins__": None }, mathlist)).encode("utf-8")  # pylint: disable=eval-used
        except Exception as e:
            result.value = ("Error: " + str(e))[:256].encode("utf-8")

    async def _calc(self, msg: api.ChatMessage, argv):
        """Syntax: calc <expression>

        Evaluates the given mathematical expression.
        The expression must only contain the following characters:
        a-z A-Z 0-9 . + - * / ( ) or whitespace.
        """
        expr = " ".join(argv[1:])
        if not re.match(r"^[ a-zA-Z0-9\.\+\-\*/\(\)]*$", expr):
            raise bot.command.CommandSyntaxError("Expression contains invalid characters")

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
    async def _hex(msg: api.ChatMessage, argv):
        """Syntax: hex <text>

        Convert a given text to hexadecimal.
        If supported by the chat protocol it will replace the user's message.
        """
        text = " ".join([hex(ord(i))[2:].upper() for i in " ".join(argv[1:])])
        await util.edit_or_reply(msg, text)

    @staticmethod
    async def _binary(msg: api.ChatMessage, argv):
        """Syntax: binary <text>

        Convert a given text to binary.
        If supported by the chat protocol it will replace the user's message.
        """
        text = " ".join([bin(ord(i))[2:] for i in " ".join(argv[1:])])
        await util.edit_or_reply(msg, text)

    @staticmethod
    async def _choose(msg: api.ChatMessage, argv):
        """Syntax: choose <option1> [option2] [option3] ...

        Randomly choose one of the given options.
        """
        await msg.reply(random.choice(argv[1:]))

    @staticmethod
    async def _random(msg: api.ChatMessage, argv):
        """Syntax: random <a> [b]

        Randomly choose a number between 0 and <a> or, if b is given, <a> and <b>.
        Both end points are included.
        """
        a = bot.command.get_argument(argv, 1, type=int)
        b = bot.command.get_argument(argv, 2, default=0, type=int)
        await msg.reply(str(random.randint(min(a, b), max(a, b))))

    @staticmethod
    async def _blockspam(msg: api.ChatMessage, argv):
        """Syntax: blockspam <text> <amount>

        Create a block of text by repeating it for a specific amount of times.
        If supported by the chat protocol it will replace the user's message.
        """
        await util.edit_or_reply(msg, int(argv[2]) * argv[1])

    @staticmethod
    async def _stretch(msg: api.ChatMessage, argv):
        """Syntax: stretch <text> <strength> [offset]

        Repeats every character in <text> after position [offset] <strength> times.
        If supported by the chat protocol it will replace the user's message.
        """
        off = int(argv[3]) if len(argv) > 3 else 0
        strength = int(argv[2])
        out = argv[1][:off] + "".join([strength * i for i in argv[1][off:]])
        await util.edit_or_reply(msg, out)

    @staticmethod
    async def _slap(msg: api.ChatMessage, argv):
        """Syntax: slap <user> [something]

        Slap a user with something. By default: a fish.
        """
        if len(argv) > 2:
            await msg.chat.send_action("slaps " + " ".join(argv[1:]))
        else:
            await msg.chat.send_action("slaps {} with a fish".format(argv[1]))

    @staticmethod
    async def _explode(msg, _argv):
        await msg.chat.send_action("explodes\nRespawn in...\n5")
        for i in range(4, 0, -1):
            await asyncio.sleep(1)
            await msg.reply(str(i))
        await asyncio.sleep(1)
        await msg.chat.send_action("is back")

    @staticmethod
    async def _lenny(msg, _argv):
        await msg.reply("( ͡° ͜ʖ ͡°)")

    @staticmethod
    async def _roll(msg: api.ChatMessage, argv):
        """Syntax: roll [x]d<N>
                   roll [x] d <N>

        Roll an N-sided dice x times. Whitespace is ignored.
        Example:
            `!roll 2d6`: Roll two 8-sided dices.
            `!roll d20`: Roll one 20-sided dice.
            `!roll 3 d8`: Roll three 8-sided dices.
            `!roll 5 d 6`: Roll five 6-sided dices.
        """
        text = "".join(argv[1:])
        match = RE_ROLL.match(text)
        if not match:
            raise bot.command.CommandSyntaxError("Invalid roll command")

        dice = int(match.group(2))
        num = int(match.group(1) or 1)
        values = [ random.randint(1, dice) for _ in range(num) ]

        if num > 1:
            await msg.reply("{} = {}".format(" + ".join(map(str, values)), sum(values)))
        else:
            await msg.reply(str(values[0]))
