#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
from context import api
from chatbot.bot.subsystem import command
from chatbot.bot.subsystem.command import CommandFlag


class Test:
    def __init__(self):
        self._echostring = ""

        self.cmd = command.CommandHandler(prefix=[ "!", "@bot" ],
                                          admins=[ "root" ])
        self.cmd.register("echo", self._cmd_echo)
        self.cmd.register("fail", self._cmd_fail, argc=0)
        self.cmd.register("expand", self._cmd_expand, argc=2,
                          flags=CommandFlag.Expand)
        self.cmd.register("admin", self._cmd_admin, argc=0,
                          flags=CommandFlag.Admin)
        self.cmd.register("missing_handler1", self._cmd_missing, argc=3,
                          flags=CommandFlag.Expand | CommandFlag.Missing)
        self.cmd.register("missing_handler2", self._cmd_missing2, argc=0,
                          flags=CommandFlag.Missing)

        # Import the module. We don't need the API object.
        api.create_api_object("test", interactive=False)

    async def run(self):
        try:
            await self.run_command("!fail")
        except ZeroDivisionError:
            pass

        try:
            await self.run_command("@bot admin")
        except command.CommandPermError:
            pass

        await self.run_command("@bot admin", "root")

        await self.run_command("! expand foo bar bla blub")
        assert self._echostring == "bar"

        # These should not even be executed
        await self.run_command("!!fail")
        await self.run_command("fail")

        await self.run_command("!echo foo bar asdf")
        assert self._echostring == "foo bar asdf"

        # Should skip _cmd_missing because it expects 3 arguments, and
        # execute _cmd_missing2 instead.
        await self.run_command("!missing foo bar")

        try:
            await self.run_command("!missing foo bar foobar")
        except command.CommandSyntaxError as e:
            assert e.args[0].find("Custom syntax error") != -1

        logging.info("Done")

    async def run_command(self, cmdstring, author="user"):
        msg = api.test.TestAPI.TestingMessage(
            api.test.TestAPI.User(author, ""), cmdstring, None)
        await self.cmd.execute(msg)

    async def _cmd_echo(self, msg, argv):
        self._echostring = " ".join(argv[1:])

    @staticmethod
    async def _cmd_fail(msg, argv):
        return 2 / 0

    async def _cmd_expand(self, msg, arg1, arg2):
        self._echostring = arg2

    @staticmethod
    async def _cmd_admin(msg, argv):
        pass

    @staticmethod
    async def _cmd_missing(msg, a, b, c):
        raise command.CommandSyntaxError("Custom syntax error")

    @staticmethod
    async def _cmd_missing2(msg, argv):
        pass


if __name__ == "__main__":
    asyncio.run(Test().run())
