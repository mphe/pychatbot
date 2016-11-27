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


# Special commands
# The registered command is called when an entered command does not exist
COMMAND_MISSING = "__missing"


# Return values for callbacks
COMMAND_SUCCESS         = 0 # Success, no error
COMMAND_ERR             = 1 # Unspecified error
COMMAND_ERR_ARGC        = 2 # Wrong argument count
COMMAND_ERR_PERM        = 3 # Missing permissions
COMMAND_ERR_SYNTAX      = 4 # Syntax error
COMMAND_ERR_NOTFOUND    = 5 # Continue as if the command didn't exist
                            # (useful in COMMAND_MISSING callbacks)

class CommandError(Exception):
    _err_strings = {
        COMMAND_SUCCESS         : "Success",
        COMMAND_ERR             : "An error occurred",
        COMMAND_ERR_ARGC        : "Wrong number of arguments",
        COMMAND_ERR_PERM        : "Permission denied",
        COMMAND_ERR_SYNTAX      : "Syntax error",
        COMMAND_ERR_NOTFOUND    : "Command not found"
    }

    def __init__(self, code, command):
        super(CommandError, self).__init__(CommandError._err_strings[code])
        self.code = code
        self.command = command

    def __repr__(self):
        return "CommandError({}, {})".format(repr(self.code), repr(self.command))


class Command(object):
    def __init__(self, callback, argc, flags):
        self.callback = callback
        self.argc = argc
        self.flags = flags

    def __call__(self, *args, **kwargs):
        ret = self.callback(*args, **kwargs)
        return COMMAND_SUCCESS if ret is None else ret


class CommandHandler(object):
    def __init__(self, prefix=[ "!" ], admins=[]):
        self._prefix = prefix
        self._admins = admins
        self._cmds = {}
        # self._evhandle = None
        self.register("help", self._help, argc=0)
        self.register("list", self._list, argc=0)

    def register(self, name, callback, argc=1, flags=0):
        """Register a chat command.
        
        The callback must be of the format:
            (api.ChatMessage, list[str]) -> int/None
        or
            (api.ChatMessage, *args) -> int/None

        The first argument is the message object issuing the command.
        The second argument is the list of arguments that were passed to
        the command (the first element is the name of the command itself).

        There are 2 ways of letting a command fail: raising an exception or
        returning an error code.

        Aside from normal exceptions, there is a CommandError exception
        that can be raised to indicate a command specific error.
        It needs an error code and the name of the command to be constructed,
        e.g.: raise CommandError(COMMAND_ERR_PERM, "mycommand").

        Returning an error code basically leads to the same outcome.
        If an error code (except COMMAND_SUCCESS) is returned, an exception
        like above will be raised with this specific error code.
        Returning nothing (None) is equal to returning COMMAND_SUCCESS.

        Possible values are:
            COMMAND_SUCCESS       -  Success, no error
            COMMAND_ERR           -  Unspecified error
            COMMAND_ERR_ARGC      -  Wrong argument count
            COMMAND_ERR_PERM      -  Missing permissions
            COMMAND_ERR_SYNTAX    -  Syntax error
            COMMAND_ERR_NOTFOUND  -  Continue as if the command didn't exist

        There is one special command called COMMAND_MISSING, which is called
        when a command was not found.

        Every command can have certain flags that can be or'ed together,
        e.g.: CMDFLAG_ADMIN | CMDFLAG_EXPAND

        Available flags are:
            CMDFLAG_ADMIN   -  The command is only available to admins
            CMDFLAG_EXPAND  -  Use the second callback format where the
                               arguments to the command are passed as
                               individual arguments to the callback.
            CMDFLAG_ALIAS   -  Not yet implemented.
        """
        if self._cmds.has_key(name):
            logging.warn("Overwriting existing command: " + name)
        self._cmds[name] = Command(callback, argc, flags)

    def unregister(self, name):
        if self._cmds.has_key(name):
            del self._cmds[name]
        else:
            logging.warn("Trying to unregister non-existing command: " + name)

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
            cmd = None
            if self._cmds.has_key(argv[0]):
                cmd = self._cmds[argv[0]]
            elif self._cmds.has_key(COMMAND_MISSING):
                cmd = self._cmds[COMMAND_MISSING]

            ret = self._exec_command(msg, cmd, argv)

            if ret != COMMAND_SUCCESS:
                raise CommandError(ret, argv[0])

    def _exec_command(self, msg, cmd, argv):
        if not cmd:
            return COMMAND_ERR_NOTFOUND

        if cmd.flags & CMDFLAG_ADMIN:
            if msg.get_author().handle() not in self._admins:
                return COMMAND_ERR_PERM

        if len(argv) <= cmd.argc:
            return COMMAND_ERR_ARGC

        if cmd.flags & CMDFLAG_EXPAND:
            return cmd(msg, *argv)
        else:
            return cmd(msg, argv)


    # Commands
    def _help(self, msg, argv):
        """Syntax: help [command]

        Shows the documentation of the given command.
        Use ´commands list´ to display a list of all available commands.
        """

        if len(argv) == 1:
            argv.append(argv[0]) # Show own help

        if not self._cmds.has_key(argv[1]):
            return COMMAND_ERR_NOTFOUND

        doc = self._cmds[argv[1]].callback.__doc__
        msg.get_chat().send_message(doc if doc else "No documentation found.")

    def _list(self, msg, argv):
        """Syntax: list

        List available commands.
        """
        msg.get_chat().send_message(", ".join(
            [ i for i in self._cmds.keys() if not i.startswith("__") ]))
