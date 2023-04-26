# -*- coding: utf-8 -*-

import json
from datetime import datetime
from typing import List, Dict, Any
import logging
from gw2api import GuildWars2Client
from chatbot.bot import BotPlugin
from chatbot import api, util


class Plugin(BotPlugin):
    def __init__(self, bot):
        super().__init__(bot)
        self._notifier = util.Notifier(self.bot.api)
        self._timer = util.async_timer.AsyncRepeatingTimer()
        self._info_providers: List[InfoProvider] = []
        self.register_command("gw2", self._gw2, argc=0)

    async def _on_ready(self) -> None:
        await super()._on_ready()
        await self._notifier.load(self.cfg["chats"])
        self._info_providers = [
            MysticForgerInfo(),
            GemPriceInfo(self.cfg["gem_threshold"])
        ]
        self._update_timer()

    async def quit(self):
        await super().quit()
        self._timer.stop()

    async def _gw2(self, msg: api.ChatMessage, argv: List[str]) -> None:
        """Syntax: gw2 [notify]

        Print useful Guild Wars 2 information.
        If "notify" is specified, enable/disable automatic notifications for this chat.
        """
        if len(argv) > 1 and argv[1] == "notify":
            await self._gw2_notify(msg, argv)
            return

        await msg.reply(await self._compile_info_list(False))

    async def _gw2_notify(self, msg: api.ChatMessage, _argv: List[str]) -> None:
        if self._notifier.toggle_chat(msg.chat):
            await msg.reply("GW2 notifications enabled")
        else:
            await msg.reply("GW2 notifications disabled")

        self._update_timer()
        self.cfg["chats"] = self._notifier.save()
        self.cfg.write()

    async def _compile_info_list(self, is_notification: bool) -> str:
        for i in self._info_providers:
            await i.update()

        if is_notification:
            text = [ i.get_notification_text() for i in self._info_providers if i.should_notify() ]
        else:
            text = [ i.get_status_text() for i in self._info_providers ]

        # If there are multiple messages, use bullet points
        if len(text) > 1:
            text = [ f"- {i}" for i in text ]

        return "\n".join(text)

    def _update_timer(self) -> None:
        if self._notifier.size() == 0:
            self._timer.stop()
        else:
            self._timer.start(self._timer_func, 24 * 60 * 60, datetime.now().replace(hour=12, minute=0, second=0))

    async def _timer_func(self) -> None:
        if text := await self._compile_info_list(True):
            await self._notifier.notify(text)

    @staticmethod
    def get_default_config():
        return {
            "chats": [],
            "gem_threshold": 32.0,
        }


class InfoProvider:
    async def update(self) -> None:
        raise NotImplementedError

    def should_notify(self) -> bool:
        raise NotImplementedError

    def get_notification_text(self) -> str:
        raise NotImplementedError

    def get_status_text(self) -> str:
        raise NotImplementedError


class MysticForgerInfo(InfoProvider):
    def __init__(self) -> None:
        self._is_mystic_forger: bool = False

    async def update(self) -> None:
        self._is_mystic_forger = await self.is_daily_coin()

    def should_notify(self) -> bool:
        return self._is_mystic_forger

    def get_notification_text(self) -> str:
        return self.get_status_text()

    def get_status_text(self) -> str:
        if self._is_mystic_forger:
            return "Today is Daily Mystic Forger"
        return "Today is not Daily Mystic Forger"

    @staticmethod
    async def is_daily_coin() -> bool:
        DAILY_MYSTIC_FORGER_ID = 500

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


class GemPriceInfo(InfoProvider):
    def __init__(self, notify_threshold: float) -> None:
        self._gold_for_100_gems: float = 0.0
        self._threshold: float = notify_threshold

    async def update(self) -> None:
        self._gold_for_100_gems = await self.get_coins_for_100_gems() / 10000

    def should_notify(self) -> bool:
        return self._gold_for_100_gems < self._threshold

    def get_notification_text(self) -> str:
        return self.get_status_text()

    def get_status_text(self) -> str:
        return f"Gem price is {self._gold_for_100_gems:.2f}G per 100 Gems"

    @staticmethod
    async def get_coins_for_100_gems() -> int:
        data: Dict = json.loads(await util.async_urlopen("https://api.guildwars2.com/v2/commerce/exchange/coins?quantity=1000000"))
        coins_per_gem = int(data["coins_per_gem"])
        return coins_per_gem * 100
