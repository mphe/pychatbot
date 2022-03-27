# -*- coding: utf-8 -*-

from chatbot.bot import BotPlugin, ExitCode, command


class Plugin(BotPlugin):
    def __init__(self, bot):
        super().__init__(bot)
        self.register_admin_command("quit", self._quit, argc=0)
        self.register_admin_command("restart", self._restart, argc=0)
        self.register_admin_command("plugins", self._plugins, argc=2)
        self.register_admin_command("update", self._update, argc=0)
        self.register_command("listplugins", self._listplugins, argc=0)

    async def _listplugins(self, msg, _argv):
        """Syntax: listplugins

        List mounted plugins.
        """
        await msg.reply(", ".join([ k for k, _ in self.bot.iter_plugins() ]))

    async def _plugins(self, msg, argv):
        """Syntax: plugins <mount|unmount|reload> <plugin name>

        Mount/remount, unmount, or reload a plugin.
        Mounting an already mounted plugin remounts it.
        """
        plugin = argv[2]
        if argv[1] == "mount":
            await self.bot.mount_plugin(plugin)
            await msg.reply(f"Plugin {plugin} (re)mounted.")
        elif argv[1] == "unmount":
            await self.bot.unmount_plugin(plugin)
            await msg.reply(f"Plugin {plugin} unmounted.")
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

    async def _update(self, msg, _argv):
        """Syntax: update

        Run `git pull` and restart bot.
        """
        await msg.reply("Running update and restarting...")
        await self.bot.close(ExitCode.RestartGitPull)
