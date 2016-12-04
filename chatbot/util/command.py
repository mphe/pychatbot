# -*- coding: utf-8 -*-

import logging
import shlex


# Command flags
# Require admin privileges to run this command
CMDFLAG_ADMIN = 1

# Expand the arguments list rather passing it as list to the callback 
CMDFLAG_EXPAND = 2

# Not an actual command but an alias to an already existing one
# TODO: Implement this
CMDFLAG_ALIAS = 4

# The registered command is called when an entered command does not exist
CMDFLAG_MISSING = 8


# Return values for callbacks
COMMAND_ERR             = 1 # Unspecified error
COMMAND_ERR_ARGC        = 2 # Wrong argument count
COMMAND_ERR_PERM        = 3 # Missing permissions
COMMAND_ERR_SYNTAX      = 4 # Syntax error
COMMAND_ERR_NOTFOUND    = 5 # Continue as if the command didn't exist
                            # (useful in CMDFLAG_MISSING callbacks)

class CommandError(Exception):
    """Represents a command specific error.

    The constructor takes an error code and optionally the name of
    the command and/or a custom error message, e.g.:
        raise CommandError(COMMAND_ERR_PERM, command="mycommand")
        raise CommandError(COMMAND_ERR, msg="Custom error message")
        raise CommandError(COMMAND_ERR_SYNTAX).

    If no message is supplied, the default message for this error code
    is used.

    Possible error codes are:
        COMMAND_ERR           -  Unspecified error
        COMMAND_ERR_ARGC      -  Wrong argument count
        COMMAND_ERR_PERM      -  Missing permissions
        COMMAND_ERR_SYNTAX    -  Syntax error
        COMMAND_ERR_NOTFOUND  -  Command not found
    """
    _err_strings = {
        COMMAND_ERR             : "An error occurred",
        COMMAND_ERR_ARGC        : "Wrong number of arguments",
        COMMAND_ERR_PERM        : "Permission denied",
        COMMAND_ERR_SYNTAX      : "Syntax error",
        COMMAND_ERR_NOTFOUND    : "Command not found"
    }

    def __init__(self, code, command="", msg=""):
        msg = msg if msg else CommandError._err_strings[code]
        super(CommandError, self).__init__(msg)
        self.code = code
        self.command = command

    def __repr__(self):
        return "CommandError({}, command={}, msg={})".format(
            repr(self.code), repr(self.command), repr(self.args[0]))


class Command(object):
    def __init__(self, callback, argc, flags):
        self.callback = callback
        self.argc = argc
        self.flags = flags

    def __call__(self, *args, **kwargs):
        self.callback(*args, **kwargs)


class CommandHandler(object):
    def __init__(self, prefix=[ "!" ], admins=[]):
        self._prefix = prefix
        self._admins = admins
        self._cmds = {}
        self._missing_cmds = {}
        self.register("help", self._help, argc=0)
        self.register("list", self._list, argc=0)

    def register(self, name, callback, argc=1, flags=0):
        """Register a chat command.
        
        name:       The name of the command. If a command with the same name
                    already exists, it will be overwritten.
        callback:   A callback function.
        argc:       The minimum amount of arguments needed for this command.
                    If there are less, a CommandError(COMMAND_ERR_ARGC)
                    exception is raised.
        flags:      A list of flags or'ed together.

        The callback must be of the format (return values are ignored):
            (api.ChatMessage, list[str]) -> Any
        or
            (api.ChatMessage, *args) -> Any

        The first argument is the message object issuing the command.
        The second argument is a list of arguments that were passed to
        the command (the first element is the name of the command itself).

        The second callback format can be used by specifying the
        CMDFLAG_EXPAND flag. This way, the arguments to the command are
        passed as individual arguments rather than as an array.
        If there are more arguments given than the command expects
        (-> argc parameter), only the expected amount of arguments is
        forwarded. Every additional argument will be discarded.
        Note that the function will still receive argc+1 number of arguments.
        The first one is the name of the command itself.

        Every command can have certain flags that can be or'ed together,
        e.g.: CMDFLAG_ADMIN | CMDFLAG_EXPAND

        Available flags are:
            CMDFLAG_ADMIN   -  The command is only available to admins.
            CMDFLAG_EXPAND  -  Use the second callback format where the
                               arguments to the command are passed as
                               individual arguments to the callback.
            CMDFLAG_ALIAS   -  Not yet implemented.
            CMDFLAG_MISSING -  These commands are called consecutively
                               (NOT in order of registration) as long as a
                               command was not found or couldn't be executed
                               because of wrong argument count.

        Aside from normal exceptions, there is a CommandError exception
        that can be thrown to let the command fail.
        See the CommandError docs on how to use it.

        Throwing a COMMAND_ERR_NOTFOUND error will make the execution
        continue as if the command was not found. This is especially useful
        in command-missing-handlers (CMDFLAG_MISSING).

        Throwing COMMAND_ERR_ARGC inside a missing handler will skip this
        handler and jump to the next one. So, effectively it does the same
        as throwing COMMAND_ERR_NOTFOUND.

        When a CommandError was raised inside the command callback, it will
        be catched by the CommandHandler, edited to include the command's
        name, and then re-raised. This way one doesn't have to bother with
        passing the command name manually.
        """
        group = self._missing_cmds if flags & CMDFLAG_MISSING else self._cmds
        if group.has_key(name):
            logging.warn("Overwriting existing command: " + name)
        group[name] = Command(callback, argc, flags)

    def unregister(self, name):
        if self._cmds.has_key(name):
            del self._cmds[name]
        elif self._missing_cmds.has_key(name):
            del self._missing_cmds[name]
        else:
            logging.warn("Trying to unregister non-existing command: " + name)

    def clear(self):
        """Remove all (except builtin) commands."""
        self._cmds.clear()
        self._missing_cmds.clear()
        self.register("help", self._help, argc=0)
        self.register("list", self._list, argc=0)

    def execute(self, msg):
        """Execute a command from a message."""
        argv = []

        command = msg.get_text()
        # Check if the message is a command and fill argv with its arguments.
        for i in self._prefix:
            if command.startswith(i):
                # Abort if the command is another prefix
                if not command[len(i):].strip().startswith(i.strip()):
                    argv = shlex.split(command[len(i):])
                break

        if argv:
            if self._cmds.has_key(argv[0]):
                try:
                    self._exec_command(msg, self._cmds[argv[0]], argv)
                    return
                except CommandError as e:
                    if e.code != COMMAND_ERR_NOTFOUND:
                        e.command = argv[0]
                        raise

            # Missing handlers
            # It's important to make a copy of the list to avoid
            # "dictionary changed size while iterating" errors
            for i in list(v for v in self._missing_cmds.itervalues()):
                try:
                    self._exec_command(msg, i, argv)
                    return
                except CommandError as e:
                    if e.code not in (COMMAND_ERR_NOTFOUND, COMMAND_ERR_ARGC):
                        e.command = argv[0]
                        raise

            raise CommandError(COMMAND_ERR_NOTFOUND, argv[0])

    def _exec_command(self, msg, cmd, argv):
        if not cmd:
            raise CommandError(COMMAND_ERR_NOTFOUND)

        if cmd.flags & CMDFLAG_ADMIN:
            if msg.get_author().handle() not in self._admins:
                raise CommandError(COMMAND_ERR_PERM)

        if len(argv) <= cmd.argc:
            raise CommandError(COMMAND_ERR_ARGC)

        if cmd.flags & CMDFLAG_EXPAND:
            cmd.callback(msg, *argv[:cmd.argc + 1])
        else:
            cmd.callback(msg, argv)


    # Commands
    def _help(self, msg, argv):
        """Syntax: help [command]

        Shows the documentation of the given command.
        Use ´commands list´ to display a list of all available commands.
        """

        if len(argv) == 1:
            argv.append(argv[0]) # Show own help

        if not self._cmds.has_key(argv[1]):
            # Use COMMAND_ERR rather than COMMAND_ERR_NOTFOUND to avoid
            # calling not-found-handlers.
            raise CommandError(COMMAND_ERR, msg="Command not found")

        doc = self._cmds[argv[1]].callback.__doc__
        msg.get_chat().send_message(doc if doc else "No documentation found.")

    def _list(self, msg, argv):
        """Syntax: list

        List available commands.
        """
        msg.get_chat().send_message(", ".join(self._cmds.keys()))
