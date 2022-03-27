# -*- coding: utf-8 -*-

from typing import List, Tuple
from chatbot.bot import BotPlugin
from chatbot import util, api
import random


class Plugin(BotPlugin):
    def __init__(self, bot):
        super().__init__(bot)
        self.register_command("zalgo", self._zalgo)

    @staticmethod
    async def _zalgo(msg: api.ChatMessage, argv):
        """Syntax: zalgo <text> [strength] [zalgosets]

        Create a Zalgo text.
        If supported by the chat protocol it will replace the user's message.

        <strength> must be between 0 and 15. Deafult is 5.
        [zalgosets] can be used to limit the direction of the zalgo.
            To do this, simply add the respective numbers together.
                up:     1
                middle: 2
                down:   4
            For example, if you want a zalgo in the middle and go up:
                zalgo "foobar" 5 3
        """
        strength = 5 if len(argv) == 2 else min(15, int(argv[2]))
        flags = int(argv[3]) if len(argv) > 3 else 7
        sets: List[Tuple] = []

        if flags & 1:
            sets.append(ZALGO_UP)
        if flags & 2:
            sets.append(ZALGO_MID)
        if flags & 4:
            sets.append(ZALGO_DOWN)

        out = create_zalgo(argv[1], strength, sets)
        await util.edit_or_reply(msg, out)


# Zalgo stuff
ZALGO_UP = (
    '\u030d', '\u030e', '\u0304', '\u0305',
    '\u033f', '\u0311', '\u0306', '\u0310',
    '\u0352', '\u0357', '\u0351', '\u0307',
    '\u0308', '\u030a', '\u0342', '\u0343',
    '\u0344', '\u034a', '\u034b', '\u034c',
    '\u0303', '\u0302', '\u030c', '\u0350',
    '\u0300', '\u0301', '\u030b', '\u030f',
    '\u0312', '\u0313', '\u0314', '\u033d',
    '\u0309', '\u0363', '\u0364', '\u0365',
    '\u0366', '\u0367', '\u0368', '\u0369',
    '\u036a', '\u036b', '\u036c', '\u036d',
    '\u036e', '\u036f', '\u033e', '\u035b',
    '\u0346', '\u031a'
)

ZALGO_DOWN = (
    '\u0316', '\u0317', '\u0318', '\u0319',
    '\u031c', '\u031d', '\u031e', '\u031f',
    '\u0320', '\u0324', '\u0325', '\u0326',
    '\u0329', '\u032a', '\u032b', '\u032c',
    '\u032d', '\u032e', '\u032f', '\u0330',
    '\u0331', '\u0332', '\u0333', '\u0339',
    '\u033a', '\u033b', '\u033c', '\u0345',
    '\u0347', '\u0348', '\u0349', '\u034d',
    '\u034e', '\u0353', '\u0354', '\u0355',
    '\u0356', '\u0359', '\u035a', '\u0323'
)

ZALGO_MID = (
    '\u0315', '\u031b', '\u0340', '\u0341',
    '\u0358', '\u0321', '\u0322', '\u0327',
    '\u0328', '\u0334', '\u0335', '\u0336',
    '\u034f', '\u035c', '\u035d', '\u035e',
    '\u035f', '\u0360', '\u0362', '\u0338',
    '\u0337', '\u0361', '\u0489'
)


def _zalgo_get_random_seq(size, zalgoset):
    for _ in range(size):
        yield zalgoset[random.randint(0, len(zalgoset) - 1)]


def create_zalgo(text, strength, sets=(ZALGO_UP, ZALGO_MID, ZALGO_DOWN)):
    # Create for each character in <text> a random sequence of zalgo chars using the given zalgo sets
    zchars = ["".join([c for z in sets for c in _zalgo_get_random_seq(strength, z)]) for _ in range(len(text))]

    # zip() through text and zchars and join() them together to get the zalgo text
    return "".join([j for i in zip(text, zchars) for j in i])
