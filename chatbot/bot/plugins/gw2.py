# -*- coding: utf-8 -*-

from datetime import datetime
from chatbot.bot import BotPlugin
from chatbot import api, util
from typing import List, Dict, Any
from gw2api import GuildWars2Client
import logging

MAX_IDS = 200
DAILY_MYSTIC_FORGER_ID = 500


class Plugin(BotPlugin):
    def __init__(self, bot):
        super().__init__(bot)
        self._notifier = util.Notifier(self.bot.api)
        self._timer = util.async_timer.AsyncRepeatingTimer()
        self.register_command("gw2", self._gw2, argc=0)

    async def _on_ready(self) -> None:
        await super()._on_ready()
        await self._notifier.load(self.cfg["chats"])
        self._update_timer()

    async def quit(self):
        await super().quit()
        self._timer.stop()

    async def _gw2(self, msg: api.ChatMessage, argv: List[str]) -> None:
        """Syntax: gw2 [notify]

        Print information about useful Guild Wars 2 dailys.
        If "notify" is specified, enable/disable automatic notifications for this chat.
        """
        if len(argv) > 1 and argv[1] == "notify":
            await self._gw2_notify(msg, argv)
            return

        if await is_daily_coin():
            await msg.reply("Today is Daily Mystic Forger!")
        else:
            await msg.reply("Today is not Daily Mystic Forger :(")

    async def _gw2_notify(self, msg: api.ChatMessage, _argv: List[str]) -> None:
        if self._notifier.toggle_chat(msg.chat):
            await msg.reply("GW2 notifications enabled")
        else:
            await msg.reply("GW2 notifications disabled")

        self._update_timer()
        self.cfg["chats"] = self._notifier.save()
        self.cfg.write()

    def _update_timer(self):
        if self._notifier.size() == 0:
            self._timer.stop()
        else:
            self._timer.start(self._timer_func, 24 * 60 * 60, datetime.now().replace(hour=12, minute=0, second=0))

    async def _timer_func(self) -> None:
        if await is_daily_coin():
            await self._notifier.notify("Today is Daily Mystic Forger!")

    @staticmethod
    def get_default_config():
        return {
            "chats": [],
        }


async def is_daily_coin() -> bool:
    def check_daily_coin() -> bool:
        client = GuildWars2Client()
        assert client.achievements.get(id=DAILY_MYSTIC_FORGER_ID)["name"] == "Daily Mystic Forger"  # type: ignore # pylint: disable=no-member

        logging.debug("Retrieving GW2 dailys...")
        dailys: Dict[str, List[Dict[str, Any]]] = client.achievementsdaily.get()  # type: ignore # pylint: disable=no-member
        flat_dailies = ( i for ach_list in dailys.values() for i in ach_list )

        for i in flat_dailies:
            if i["id"] == DAILY_MYSTIC_FORGER_ID:
                return True
        return False

    return await util.run_in_thread(check_daily_coin)
