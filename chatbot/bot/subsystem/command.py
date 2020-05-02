# -*- coding: utf-8 -*-

import asyncio
import enum
import logging
import shlex
from typing import Callable, List
from collections import namedtuple
from chatbot.api import MessageType, ChatMessage


CommandHandle = namedtuple("CommandHandle", [ "callback", "argc", "flags" ])


class CommandFlag(enum.IntFlag):
    """Require admin privileges to run this command."""
    Admin = 1

    """Expand the arguments list rather passing it as list to the callback."""
    Expand = 2

    """Not an actual command but an alias to an already existing one.
    Not yet implemented.
    """
    # TODO: Implement this
    Alias = 4

    """The registered command is called when an entered command does not exist.
    These commands are called consecutively (NOT in order of registration)
    until a command executes successfully.
    """
    Missing = 8


class CommandError(Exception):
    def __init__(self, msg="An error occurred.", command=""):
        super(CommandError, self).__init__(msg)
        self.command = command


class CommandNotFoundError(CommandError):
    def __init__(self, command=""):
        super(CommandNotFoundError, self).__init__("Command not found.", command)


class CommandSyntaxError(CommandError):
    def __init__(self, msg="", command=""):
        msg = "Syntax error: {}.".format(msg) if msg else "Syntax error."
        super(CommandSyntaxError, self).__init__(msg, command)


class CommandArgcError(CommandSyntaxError):
    def __init__(self, command=""):
        super(CommandArgcError, self).__init__("Wrong number of arguments.", command)


class CommandPermError(CommandError):
    def __init__(self, command=""):
        super(CommandPermError, self).__init__("Permission denied.", command)


class CommandHandler:
    def __init__(self, prefix=("!",), admins=()):
        """Takes a list of command prefixes and admins."""
        self._prefix = prefix
        self._admins = admins
        self._cmds = {}
        self._missing_cmds = {}
        self.register("help", self._help, argc=0)
        self.register("list", self._list, argc=0)

    def register(self, name: str,
                 callback: Callable[[ChatMessage, List[str]], None],
                 argc=1, flags=0):
        """Register a chat command.

        Args:
            name: The name of the command. If a command with the same name
                  already exists, it will be overwritten.
            callback: A coroutine callback function.
            argc: The minimum amount of arguments needed for this command.
                  If there are less, a CommandArgcError is raised.
            flags: A list of flags or'ed together. See also `CommandFlag`.

        The callback must have one of the following signatures
        (return values are ignored):
            (api.ChatMessage, list[str]) -> None
        or
            (api.ChatMessage, *args) -> None

        The first argument is the message object issuing the command.
        The second argument is a list of arguments that were passed to
        the command (the first element is the name of the command itself).

        The second callback format can be used by specifying the
        `CommandFlag.Expand` flag. This way, the arguments to the command are
        passed as individual arguments rather than as array.
        If there are more arguments given than the command expects
        (-> argc parameter), only the expected amount of arguments are
        forwarded. Every additional argument will be discarded.
        Note that the function will _not_ receive the name of the command as
        first argument.

        Aside from normal exceptions, there are several CommandError exceptions
        that can be thrown to let the command fail.

        Throwing CommandNotFoundError will make the execution continue as if
        the command was not found. This is especially useful in
        command-missing-handlers (CommandFlag.Missing).

        Throwing CommandNotFoundError or CommandArgcError inside a
        command-missing-handler will skip this handler and jump to the next one.

        When a CommandError was raised inside the command callback, it will
        be catched by the CommandHandler, edited to include the command's
        name, and then re-raised. This way one doesn't have to bother with
        passing the command name manually.
        """
        assert asyncio.iscoroutinefunction(callback), "Callback must be a coroutine"
        group = self._missing_cmds if flags & CommandFlag.Missing else self._cmds
        if name in group:
            logging.warning("Overwriting existing command: %s", name)
        group[name] = CommandHandle(callback, argc, flags)
        logging.debug("Registered command: %s", name)

    def unregister(self, name):
        try:
            self._cmds.pop(name)
        except KeyError:
            try:
                self._missing_cmds.pop(name)
            except KeyError:
                logging.warning("Trying to unregister non-existing command: %s", name)
                return
        logging.debug("Unregistered command: %s", name)

    def clear(self):
        """Remove all (except builtin) commands."""
        logging.debug("Clearning all commands")
        self._cmds.clear()
        self._missing_cmds.clear()
        self.register("help", self._help, argc=0)
        self.register("list", self._list, argc=0)

    async def execute(self, msg: ChatMessage):
        """Execute a command from a message.

        Returns True if the message was a command, otherwise False.
        Exceptions may be raised and have to be handled by the calling scope.
        """
        if msg.get_type() != MessageType.Normal:
            return False

        argv = []
        text = msg.get_text()

        # Check if the message is a command and fill argv with its arguments.
        for i in self._prefix:
            if text.startswith(i):
                # Abort if the command is another prefix
                if not text[len(i):].strip().startswith(i.strip()):
                    argv = shlex.split(text[len(i):])
                break

        if not argv:
            return False

        command = self._cmds.get(argv[0], None)
        if command:
            try:
                await self._exec_command(msg, command, argv)
                return True
            except CommandNotFoundError:
                pass
            except CommandError as e:
                e.command = argv[0]
                raise

        # Missing handlers
        # It's important to make a copy of the list to avoid
        # "dictionary changed size while iterating" errors
        for i in list(v for v in self._missing_cmds.values()):
            try:
                await self._exec_command(msg, i, argv)
                return True
            except (CommandNotFoundError, CommandArgcError):
                pass
            except CommandError as e:
                e.command = argv[0]
                raise

        raise CommandNotFoundError(command=argv[0])

    async def _exec_command(self, msg: ChatMessage, cmd: CommandHandle, argv: List[str]):
        if not cmd:
            raise CommandNotFoundError

        if cmd.flags & CommandFlag.Admin:
            if msg.get_author().id() not in self._admins:
                raise CommandPermError

        if len(argv) <= cmd.argc:
            raise CommandArgcError

        if cmd.flags & CommandFlag.Expand:
            await cmd.callback(msg, *argv[1:cmd.argc + 1])
        else:
            await cmd.callback(msg, argv)

    # Commands
    async def _help(self, msg: ChatMessage, argv: List[str]):
        """Syntax: help [command]

        Shows the documentation of the given command.
        Use `list` to display a list of all available commands.

        Arguments in <angular brackets> are required, those in
        [square brackets] are optional. | means "or", A|B means "A or B".
        Arguments followed by 3 dots (...) stand for 0 or more arguments.
        Wrapping arguments in "quotation marks" allows strings to have spaces.
        References to other commands are noted in `backticks`.
        """
        helpcmd = argv[0] if len(argv) == 1 else argv[1]
        cmd = self._cmds.get(helpcmd, None)

        if not cmd:
            # Use CommandError rather than CommandNotFoundError to avoid
            # calling not-found-handlers.
            raise CommandError("There is no such command.")

        doc = cmd.callback.__doc__
        await msg.get_chat().send_message(doc if doc else "No documentation found.")

    async def _list(self, msg, _argv):
        """Syntax: list

        List available commands.
        """
        await msg.reply("User commands: {}\n\nAdmin commands: {}".format(
            ", ".join([ k for k, v in self._cmds.items() if not (v.flags & CommandFlag.Admin) ]),
            ", ".join([ k for k, v in self._cmds.items() if v.flags & CommandFlag.Admin ])
        ))
