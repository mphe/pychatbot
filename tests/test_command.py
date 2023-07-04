#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from context import create_test_api
from chatbot.bot.subsystem import command
from chatbot.bot.subsystem.command import CommandFlag
from chatbot.api.test import TestAPI


class Test(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self._echostring = ""
        self._api = create_test_api({})
        self._chat = TestAPI.TestChat(self._api)
        self.cmd = command.CommandHandler(prefix=[ "!", "@bot" ], admins=[ "root" ])

    async def test_fail(self):
        async def cmd_fail(_msg, _argv):
            return 2 / 0

        self.cmd.register("fail", cmd_fail, argc=0)

        with self.assertRaises(ZeroDivisionError):
            await self._run_command("!fail")

    async def test_permission(self):
        async def cmd_admin(_msg, _argv):
            pass

        self.cmd.register("admin", cmd_admin, argc=0, flags=CommandFlag.Admin)

        with self.assertRaises(command.CommandPermError):
            await self._run_command("@bot admin")

        try:
            await self._run_command("@bot admin", "root")
        except command.CommandPermError:
            self.fail("There should not be a permission error")

    async def test_invoke(self):
        async def cmd_echo(_msg, argv):
            self._echostring = " ".join(argv[1:])

        self.cmd.register("echo", cmd_echo)
        await self._run_command("!echo foo bar asdf")
        self.assertEqual(self._echostring, "foo bar asdf")

    async def test_invoke_expand(self):
        async def cmd_expand(_msg, _arg1, arg2):
            self._echostring = arg2

        self.cmd.register("expand", cmd_expand, argc=2, flags=CommandFlag.Expand)
        await self._run_command("! expand foo bar bla blub")
        self.assertEqual(self._echostring, "bar")

    async def test_not_invoke(self):
        async def test_cmd(_msg, _argv):
            self._echostring = "foo"

        self.cmd.register("test", test_cmd, argc=0)

        # These should not be executed
        await self._run_command("test")
        self.assertEqual(self._echostring, "")

        with self.assertRaises(command.CommandNotFoundError):
            await self._run_command("!missing_command")

    async def test_repeat(self):
        async def test_cmd(_msg, _argv):
            self._echostring += "A"

        self.cmd.register("test", test_cmd, argc=0)

        await self._run_command("!test")
        self.assertEqual(self._echostring, "A")
        await self._run_command("!!")
        self.assertEqual(self._echostring, "AA")

        with self.assertRaises(command.CommandNotFoundError):
            await self._run_command("!missing_command")

    async def test_missing_handlers(self):
        async def cmd_missing(_msg, _a, _b, _c):
            self._echostring += "A"

        async def cmd_missing2(_msg, _argv):
            self._echostring += "B"

        async def cmd_missing_continue(_msg, _argv):
            self._echostring += "C"
            raise command.CommandNotFoundError()

        self.cmd.register("missing_handler1", cmd_missing, argc=3, flags=CommandFlag.Expand | CommandFlag.Missing)
        self.cmd.register("missing_handler2", cmd_missing_continue, argc=2, flags=CommandFlag.Missing)
        self.cmd.register("missing_handler3", cmd_missing2, argc=0, flags=CommandFlag.Missing)

        # Should execute cmd_missing2 because cmd_missing and cmd_missing_continue expect 3 and 2 arguments
        await self._run_command("!missing foo")
        self.assertEqual(self._echostring, "B")

        # Should execute cmd_missing
        self._echostring = ""
        await self._run_command("!missing foo bar foobar")
        self.assertEqual(self._echostring, "A")

        # Should execute cmd_missing_continue and then cmd_missing2
        self._echostring = ""
        await self._run_command("!missing foo bar")
        self.assertEqual(self._echostring, "CB")

    async def _run_command(self, cmdstring, author="user"):
        msg = TestAPI.TestingMessage(TestAPI.User(author, "", None), cmdstring, self._chat)
        await self.cmd.execute(msg)


if __name__ == "__main__":
    unittest.main()
