# -*- coding: utf-8 -*-

from collections import namedtuple
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Set, Tuple
import logging
import parsedatetime
from chatbot import api, bot, util
from queue import PriorityQueue

# isoformat should be the first item, to ensure correct sorting order
Reminder = namedtuple("Reminder", [ "isoformat", "chatid", "userid", "msg", ])


class Plugin(bot.BotPlugin):
    def __init__(self, oldme: "Plugin", bot: bot.Bot):
        self._parsers = []  # type: List[parsedatetime.Calendar]
        self._timer = None  # type: asyncio.Task
        self._reminders = PriorityQueue()

        super(Plugin, self).__init__(oldme, bot)

        self.register_command("remindme", self._remindme)

    def reload(self):
        super(Plugin, self).reload()

        langs = self.cfg["langs"]

        if len(langs) == 0:
            logging.warning("%s: No languages specified -> using default.", self.name)
            self._parsers = [ parsedatetime.Calendar() ]
        else:
            self._parsers = [ parsedatetime.Calendar(parsedatetime.Constants(i)) for i in langs ]

        for i in self.cfg["timers"]:
            self._reminders.put(Reminder(*i))
        self._restart_timer()

    def quit(self):
        self._stop_timer()
        super(Plugin, self).quit()

    async def _remindme(self, msg: api.ChatMessage, argv: List[str]):
        """Syntax: remindme <date/time> [text]

        Schedule a timer for the given date/time and send a message when the time has passed.
        <time> can be any human readable date/time string, e.g. "tomorrow", "5m", "22.7.2022", "1h 5m 30s", "15:30", etc.

        Extra text not containing any time information is ignored and can be used as message.

        Example: !remindme 5m 5 minutes have passed
        """
        text = " ".join(argv[1:])

        for i in self._parsers:
            logging.debug("Trying parser %s", i.ptc.localeID)
            struct, result = i.parse(text)
            if result != 0:
                break

        if result == 0:
            await msg.reply("Failed to parse date/time.")
            return

        date = datetime(*struct[:6])
        self._schedule(Reminder(date.isoformat(), msg.chat.id, msg.author.id, msg.text))
        await msg.reply("Reminding you on {}".format(date))

    def _schedule(self, reminder: Reminder):
        self.cfg["timers"].append(reminder)  # is seemlessly serializable
        self.cfg.write()

        self._reminders.put(reminder)
        logging.debug("Scheduled %s", reminder.isoformat)
        self._restart_timer()

    def _stop_timer(self):
        if self._timer and not self._timer.done():
            self._timer.cancel()
            logging.debug("Reminder task stopped")
        self._timer = None

    def _restart_timer(self):
        self._stop_timer()
        self._timer = asyncio.create_task(self._timer_callback())
        logging.debug("Reminder task started")

    def _get_next_timer(self) -> Tuple[float, Reminder]:
        """Returns tuple of seconds to wait and corresponding Reminder, or None."""
        if self._reminders.empty():
            return None, None

        reminder: Reminder = self._reminders.queue[0]
        delta = (datetime.fromisoformat(reminder.isoformat) - datetime.today()).total_seconds()
        return delta, reminder

    async def _timer_callback(self):
        while True:
            delta, reminder = self._get_next_timer()

            if reminder is None:
                break

            if delta <= 0:
                logging.debug("Reminder delta time <= 0 -> executing immediately")
                await self._exec_reminder(reminder)
                continue

            logging.debug("Updated timer: Next reminder in %s seconds", delta)
            await asyncio.sleep(delta)
            await self._exec_reminder(reminder)

        logging.debug("Reminder task finished, no more timers.")

    async def _exec_reminder(self, reminder: Reminder):
        logging.debug("Executing reminder: %s", reminder)

        # Wait until API is ready, since this could run directly after startup
        await util.wait_until_api_ready(self.bot.api)

        chat = await self.bot.api.find_chat(reminder.chatid)
        user = await self.bot.api.find_user(reminder.userid)

        if chat is None:
            logging.error("Failed to retrieve chat %s", reminder.chatid)
        if user is None:
            logging.error("Failed to retrieve user %s", reminder.userid)

        if chat:
            userping = "@Unknown" if user is None else user.mention
            await chat.send_message("{}\n{}: {}".format(
                util.string_prepend("> ", reminder.msg), userping, self.cfg["message"]))

        self._pop_reminder(reminder)

    def _pop_reminder(self, reminder: Reminder):
        self._reminders.get()
        self.cfg["timers"] = list(self._reminders.queue)
        self.cfg.write()
        logging.debug("Reminder removed: %s", reminder)

    @staticmethod
    def get_default_config():
        return {
            "message": "Reminding you!",
            "langs": [
                "en_US",
                "de_DE",
            ],
            "timers": [],  # type: List[Reminder]
        }
