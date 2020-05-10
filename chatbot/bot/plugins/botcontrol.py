# -*- coding: utf-8 -*-

from chatbot.bot import BotPlugin, ExitCode, command


class Plugin(BotPlugin):
    def __init__(self, oldme, bot):
        super(Plugin, self).__init__(oldme, bot)
        self.register_admin_command("quit", self._quit, argc=0)
        self.register_admin_command("restart", self._restart, argc=0)
        self.register_admin_command("plugins", self._plugins, argc=2)
        self.register_command("listplugins", self._listplugins, argc=0)

    async def _listplugins(self, msg, _argv):
        """Syntax: listplugins

        List mounted plugins.
        """
        await msg.reply(", ".join([ k for k, v in self.bot.iter_plugins() ]))

    async def _plugins(self, msg, argv):
        """Syntax: plugins <mount|unmount|reload> <plugin name>

        Mount/remount, unmount, or reload a plugin.
        Mounting an already mounted plugin remounts it.
        """
        f = {
            "reload":  (self.bot.reload_plugin,  "Plugin reloaded"),
            "mount":   (self.bot.mount_plugin,   "Plugin (re)mounted"),
            "unmount": (self.bot.unmount_plugin, "Plugin unmounted"),
        }
        if argv[1] in f:
            f[argv[1]][0](argv[2])
            await msg.reply(f[argv[1]][1])
        else:
            raise command.CommandSyntaxError

    async def _quit(self, msg, argv):
        """Syntax: quit [exit code]

        Shutdown bot (with the given exit code).
        """
        await msg.reply("Shutting down...")
        await self.bot.close(ExitCode.Normal if len(argv) == 1 else int(argv[1]))

    async def _restart(self, msg, _argv):
        """Syntax: restart

        Restart bot.
        """
        await msg.reply("Restarting...")
        await self.bot.close(ExitCode.Restart)
