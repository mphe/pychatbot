# -*- coding: utf-8 -*-

import traceback
import logging
import shlex
from collections import namedtuple
from .. import api


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

# Error messages
COMMAND_ERROR_STRINGS = {
    COMMAND_SUCCESS         : "Success",
    COMMAND_ERR             : "An error occurred",
    COMMAND_ERR_ARGC        : "Wrong number of arguments",
    COMMAND_ERR_PERM        : "Permission denied",
    COMMAND_ERR_SYNTAX      : "Syntax error",
    COMMAND_ERR_NOTFOUND    : "Command not found"
}

class Command(object):
    def __init__(self, callback, argc, flags):
        self.callback = callback
        self.argc = argc
        self.flags = flags

    def __call__(self, *args, **kwargs):
        ret = self.callback(*args, **kwargs)
        return COMMAND_SUCCESS if ret is None else ret


class CommandHandler(object):
    def __init__(self, nofail=True, prefix=[ "!bot ", "!", "@bot " ], admins=[]):
        self._prefix = prefix
        self._admins = admins
        self._cmds = {}
        self._evhandle = None
        self._nofail = nofail

    def attach(self, dispatcher):
        if not self._evhandle:
            self._evhandle = dispatcher.register(api.APIEvents.Message,
                                                 self._on_msg_receive)
            self.register("help", self._help, argc=0)
            self.register("list", self._list, argc=0)

    def detach(self):
        if self._evhandle:
            self._evhandle.unregister()
            self._evhandle = None

    def register(self, name, callback, argc=1, flags=0):
        """Register a chat command.
        
        The callback must be in the format:
            (api.ChatMessage, list[str]) -> int/None
        or
            (api.ChatMessage, *args) -> int/None

        The first argument to the callback is the message object issuing
        the command. The second argument is a list of arguments to the
        command (the first element is the name of the command itself).

        The return value indicates if the command was successful or failed.
        Possible values are:
            COMMAND_SUCCESS       -  Success, no error
            COMMAND_ERR           -  Unspecified error
            COMMAND_ERR_ARGC      -  Wrong argument count
            COMMAND_ERR_PERM      -  Missing permissions
            COMMAND_ERR_SYNTAX    -  Syntax error
            COMMAND_ERR_NOTFOUND  -  Continue as if the command didn't exist

        Returning nothing (None) is equal to returning COMMAND_SUCCESS.

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

    def _on_msg_receive(self, msg):
        argv = []

        # Check if the message is a command and fill argv with its arguments.
        for i in self._prefix:
            if msg.get_text().startswith(i):
                argv = shlex.split(msg.get_text()[len(i):])
                # Abort if no command supplied or when the command is another
                # prefix.
                if not argv or argv[0].startswith(i.strip()):
                    return
                break

        if not argv:
            return

        cmd = None
        if self._cmds.has_key(argv[0]):
            cmd = self._cmds[argv[0]]
        elif self._cmds.has_key(COMMAND_MISSING):
            cmd = self._cmds[COMMAND_MISSING]

        ret = self._exec_command(cmd, msg, argv)

        if ret != COMMAND_SUCCESS:
            msg.get_chat().send_message( "Error: " + COMMAND_ERROR_STRINGS[ret])

    def _exec_command(self, cmd, msg, argv):
        if not cmd:
            return COMMAND_ERR_NOTFOUND

        if cmd.flags & CMDFLAG_ADMIN:
            if msg.author_handle() not in self._admins:
                return COMMAND_ERR_PERM

        if len(argv) <= cmd.argc:
            return COMMAND_ERR_ARGC

        try:
            if cmd.flags & CMDFLAG_EXPAND:
                return cmd(msg, *argv)
            else:
                return cmd(msg, argv)
        except Exception as e:
            if self._nofail:
                logging.error(traceback.format_exc())
                msg.get_chat().send_message("Error: " + str(e))
                # Hide the exception, it has already been logged
                return COMMAND_SUCCESS
            else:
                raise


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
