#!/usr/bin/env python
# -*- coding: utf-8 -*-

from context import *
from functools import partial
from chatbot.bot.subsystem.command import *
from chatbot.compat import *


class Test(object):
    def __init__(self):
        self._echostring = ""

        self.cmd = CommandHandler(prefix=[ "!", "@bot" ],
                                  admins=[ "root" ])
        self.cmd.register("echo", self._cmd_echo)
        self.cmd.register("fail", self._cmd_fail, argc=0)
        self.cmd.register("expand", self._cmd_expand, argc=2,
                          flags=CMDFLAG_EXPAND)
        self.cmd.register("admin", self._cmd_admin, argc=0,
                          flags=CMDFLAG_ADMIN)
        self.cmd.register("missing_handler1", self._cmd_missing, argc=3,
                          flags=CMDFLAG_EXPAND | CMDFLAG_MISSING)
        self.cmd.register("missing_handler2", self._cmd_missing2, argc=0,
                          flags=CMDFLAG_MISSING)

        # Import the module. We don't need the API object.
        api.create_api_object("test", interactive=False)

    def run(self):
        try:
            self.run_command("!fail")
        except ZeroDivisionError:
            pass

        try:
            self.run_command("@bot admin")
        except CommandError as e:
            if e.code != COMMAND_ERR_PERM:
                raise

        self.run_command("@bot admin", "root")

        self.run_command("! expand foo bar bla blub")
        assert self._echostring == "bar"

        # These should not even be executed
        self.run_command("!!fail")
        self.run_command("fail")

        self.run_command("!echo foo bar asdf")
        assert self._echostring == "foo bar asdf"

        # Should skip _cmd_missing because it expects 3 arguments, and
        # execute _cmd_missing2 instead.
        self.run_command("!missing foo bar")

        try:
            self.run_command("!missing foo bar foobar")
        except CommandError as e:
            if e.code == COMMAND_ERR_SYNTAX:
                assert e.args[0] == "Custom syntax error"
            else:
                raise

        logging.info("Done")

    def run_command(self, command, author="user"):
        msg = api.test.TestAPI.TestingMessage(
            api.test.TestAPI.User(author, ""),
            command,
            None
        )
        self.cmd.execute(msg)

    def _cmd_echo(self, msg, argv):
        self._echostring = " ".join(argv[1:])

    def _cmd_fail(self, msg, argv):
        return 2/0

    def _cmd_expand(self, msg, me, arg1, arg2):
        self._echostring = arg2

    def _cmd_admin(self, msg, argv):
        pass

    def _cmd_missing(self, msg, me, a, b, c):
        raise CommandError(COMMAND_ERR_SYNTAX, msg="Custom syntax error")

    def _cmd_missing2(self, msg, argv):
        pass


if __name__ == "__main__":
    Test().run()
