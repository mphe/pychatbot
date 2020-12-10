# -*- coding: utf-8 -*-

from dataclasses import dataclass
import textwrap
import asyncio
import enum
import logging
import shlex
from typing import Callable, List, Iterable, Dict, Tuple
from chatbot.api import MessageType, ChatMessage


@dataclass
class CommandHandle:
    callback: Callable
    argc: int
    flags: int
    types: Tuple


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
    def __init__(self, msg="An error occurred", command=""):
        super().__init__(msg)
        self.command = command


class CommandNotFoundError(CommandError):
    def __init__(self, command=""):
        super().__init__("Command not found", command)


class CommandSyntaxError(CommandError):
    def __init__(self, msg="", command=""):
        msg = "Syntax error: {}".format(msg) if msg else "Syntax error"
        super().__init__(msg, command)


class CommandArgcError(CommandSyntaxError):
    def __init__(self, command=""):
        super().__init__("Wrong number of arguments", command)


class CommandPermError(CommandError):
    def __init__(self, command=""):
        super().__init__("Permission denied", command)


class CommandHistory:
    def __init__(self, max_entries: int):
        self._max_entries = max_entries
        self._entries: Dict[Tuple[str, str], List[ChatMessage]] = {}

    def add(self, msg: ChatMessage):
        history = self.get_for_message(msg)
        history.append(msg)

        # Remove first element if overflowing
        if len(history) > self._max_entries:
            history.pop(0)

    def get_for_message(self, msg: ChatMessage) -> List[ChatMessage]:
        """Wrapper around get()."""
        return self.get(msg.author.id, msg.chat.id)

    def get(self, userid: str, chatid: str) -> List[ChatMessage]:
        """Returns a mutable list of recent commands of a given user in a given chat, with more recent entries last."""
        # setdefault() returns the existing value at key or creates and returns it
        return self._entries.setdefault((userid, chatid), [])


def get_argument_as_type(argument: str, type_):
    """Try to cast `argument` to the given type or raise CommandSyntaxError."""
    try:
        return type_(argument)
    except Exception as e:
        if type_ is int:
            basetext = "Argument is not an integral number"
        elif type_ is float:
            basetext = "Argument is not a number"
        else:
            basetext = "Argument is not of type {}".format(type_.__name__)

        raise CommandSyntaxError("{}: {}".format(basetext, argument)) from e


def get_argument(argv: List[str], index: int, default=None, type=None):  # pylint: disable=redefined-builtin
    """Get the nth argument or default, optionally casted to type or raise CommandSyntaxError."""
    if index >= len(argv) or not argv[index]:
        return default
    if type is not None:
        return get_argument_as_type(argv[index], type)
    return argv[index]


class CommandHandler:
    def __init__(self, prefix=("!",), admins=()):
        """Takes a list of command prefixes and admins."""
        self._prefix = prefix
        self._repeat_cmd = "!!"
        self._admins = admins
        self._history = CommandHistory(1)  # Last command should be enough
        self._cmds: Dict[str, CommandHandle] = {}
        self._missing_cmds: Dict[str, CommandHandle] = {}
        self.register("help", self._help, argc=0)
        self.register("list", self._list, argc=0)

    @property
    def admins(self) -> Iterable[str]:
        return self._admins

    def register(self, name: str, callback: Callable, argc=1, flags=0, types=()):
        """Register a chat command.

        Args:
            name: The name of the command. If a command with the same name
                  already exists, it will be overwritten.
            callback: A coroutine callback function.
            argc: The minimum amount of arguments needed for this command.
                  If there are less, a CommandArgcError is raised.
            flags: A list of flags or'ed together. See also `CommandFlag`.
            types: A tuple of types to automatically cast arguments to or error.

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
        group[name] = CommandHandle(callback, argc, flags, types)
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

    async def execute(self, msg: ChatMessage) -> bool:
        """Execute a command from a message.

        Returns True if the message was a command, otherwise False.
        Exceptions may be raised and have to be handled in the calling scope.
        """
        if msg.type != MessageType.Normal:
            return False

        text = msg.text.strip()

        if self._repeat_cmd and text == self._repeat_cmd:
            history = self._history.get_for_message(msg)
            if not history:
                raise CommandError("No previous commands", command=self._repeat_cmd)
            await self.execute(history[-1])
            return True

        argv: List[str] = []

        # Check if the message is a command and fill argv with its arguments.
        for i in self._prefix:
            if text.startswith(i):
                # Abort if the command is another prefix
                if not text[len(i):].strip().startswith(i.strip()):
                    argv = shlex.split(text[len(i):])
                break

        if not argv:
            return False

        # It is a command, so add to history
        self._history.add(msg)

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
        for i in list(self._missing_cmds.values()):
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
            if msg.author.id not in self._admins:
                raise CommandPermError

        if len(argv) <= cmd.argc:
            raise CommandArgcError

        if cmd.types:
            for i, (arg, t) in enumerate(zip(argv[1:], cmd.types), 1):
                argv[i] = get_argument_as_type(arg, t)

        if cmd.flags & CommandFlag.Expand:
            await cmd.callback(msg, *argv[1:cmd.argc + 1])
        else:
            await cmd.callback(msg, argv)

    # Commands
    async def _help(self, msg: ChatMessage, argv: List[str]):
        """Syntax: help [command]

        Shows the documentation of the given command.
        Use `list` to display a list of all available commands.
        Use `!!` to repeat your last command in this channel.

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

        doc: str = cmd.callback.__doc__
        if doc:
            firstline = doc.find("\n")
            if firstline != -1:
                doc = doc[:firstline] + textwrap.dedent(doc[firstline:])

            # TODO: add a supports_markdown() function to api.Chat
            # if doc.startswith("Syntax:"):
            #     doc.replace("Syntax:", "**Syntax:**", 1)
        else:
            doc = "No documentation found."
        await msg.reply(doc)

    async def _list(self, msg, _argv):
        """Syntax: list

        List available commands.
        """
        await msg.reply("User commands: {}\n\nAdmin commands: {}".format(
            ", ".join([ k for k, v in self._cmds.items() if not (v.flags & CommandFlag.Admin) ]),
            ", ".join([ k for k, v in self._cmds.items() if v.flags & CommandFlag.Admin ])
        ))
