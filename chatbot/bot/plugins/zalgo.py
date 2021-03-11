# -*- coding: utf-8 -*-

from typing import List, Tuple
from chatbot.bot import BotPlugin
from chatbot import util, api
import random


class Plugin(BotPlugin):
    def __init__(self, oldme, bot):
        super().__init__(oldme, bot)
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
    u'\u030d', u'\u030e', u'\u0304', u'\u0305',
    u'\u033f', u'\u0311', u'\u0306', u'\u0310',
    u'\u0352', u'\u0357', u'\u0351', u'\u0307',
    u'\u0308', u'\u030a', u'\u0342', u'\u0343',
    u'\u0344', u'\u034a', u'\u034b', u'\u034c',
    u'\u0303', u'\u0302', u'\u030c', u'\u0350',
    u'\u0300', u'\u0301', u'\u030b', u'\u030f',
    u'\u0312', u'\u0313', u'\u0314', u'\u033d',
    u'\u0309', u'\u0363', u'\u0364', u'\u0365',
    u'\u0366', u'\u0367', u'\u0368', u'\u0369',
    u'\u036a', u'\u036b', u'\u036c', u'\u036d',
    u'\u036e', u'\u036f', u'\u033e', u'\u035b',
    u'\u0346', u'\u031a'
)

ZALGO_DOWN = (
    u'\u0316', u'\u0317', u'\u0318', u'\u0319',
    u'\u031c', u'\u031d', u'\u031e', u'\u031f',
    u'\u0320', u'\u0324', u'\u0325', u'\u0326',
    u'\u0329', u'\u032a', u'\u032b', u'\u032c',
    u'\u032d', u'\u032e', u'\u032f', u'\u0330',
    u'\u0331', u'\u0332', u'\u0333', u'\u0339',
    u'\u033a', u'\u033b', u'\u033c', u'\u0345',
    u'\u0347', u'\u0348', u'\u0349', u'\u034d',
    u'\u034e', u'\u0353', u'\u0354', u'\u0355',
    u'\u0356', u'\u0359', u'\u035a', u'\u0323'
)

ZALGO_MID = (
    u'\u0315', u'\u031b', u'\u0340', u'\u0341',
    u'\u0358', u'\u0321', u'\u0322', u'\u0327',
    u'\u0328', u'\u0334', u'\u0335', u'\u0336',
    u'\u034f', u'\u035c', u'\u035d', u'\u035e',
    u'\u035f', u'\u0360', u'\u0362', u'\u0338',
    u'\u0337', u'\u0361', u'\u0489'
)


def _zalgo_get_random_seq(size, zalgoset):
    for _ in range(size):
        yield zalgoset[random.randint(0, len(zalgoset) - 1)]


def create_zalgo(text, strength, sets=(ZALGO_UP, ZALGO_MID, ZALGO_DOWN)):
    # Create for each character in <text> a random sequence of zalgo chars using the given zalgo sets
    zchars = ["".join([c for z in sets for c in _zalgo_get_random_seq(strength, z)]) for i in range(len(text))]

    # zip() through text and zchars and join() them together to get the zalgo text
    return "".join([j for i in zip(text, zchars) for j in i])
