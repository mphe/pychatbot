# -*- coding: utf-8 -*-

from chatbot.compat import *
from chatbot.bot import BotPlugin, ExitCode, command


class Plugin(BotPlugin):
    def __init__(self, oldme, bot):
        super(Plugin, self).__init__(oldme, bot)
        self.register_admin_command("quit", self._quit, argc=0)
        self.register_admin_command("restart", self._restart, argc=0)
        self.register_admin_command("reload", self._reload, argc=0)
        self.register_admin_command("plugins", self._plugins, argc=2)
        self.register_command("listplugins", self._listplugins, argc=0)

    def _listplugins(self, msg, argv):
        """Syntax: listplugins

        List mounted plugins.
        """
        msg.reply(", ".join([ k for k, v in self.bot().iter_plugins() ]))

    def _plugins(self, msg, argv):
        """Syntax: plugins <mount|unmount|reload> <plugin name>

        Mount/remount, unmount, or reload a plugin.
        Mounting an already mounted plugin remounts it.
        """
        f = {
            "reload":  (self.bot().reload_plugin,  "Plugin reloaded"),
            "mount":   (self.bot().mount_plugin,   "Plugin (re)mounted"),
            "unmount": (self.bot().unmount_plugin, "Plugin unmounted"),
        }
        if argv[1] in f:
            f[argv[1]][0](argv[2])
            msg.reply(f[argv[1]][1])
        else:
            raise command.CommandError(command.COMMAND_ERR_SYNTAX, command=argv[0])

    def _reload(self, msg, argv):
        """Syntax: reload

        Reload bot's configuration file.
        """
        self.bot().reload()
        msg.reply("Configuration reloaded")

    def _quit(self, msg, argv):
        """Syntax: quit [exit code]

        Shutdown bot (with the given exit code).
        """
        msg.reply("Shutting down...")
        self.bot().quit(ExitCode.Normal if len(argv) == 1 else int(argv[1]))

    def _restart(self, msg, argv):
        """Syntax: restart

        Restart bot.
        """
        msg.reply("Restarting...")
        self.bot().quit(ExitCode.Restart)
