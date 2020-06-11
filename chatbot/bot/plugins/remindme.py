# -*- coding: utf-8 -*-

import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Set, Tuple, NamedTuple
import logging
import parsedatetime
import pytz
from chatbot import api, bot, util
from queue import PriorityQueue


# Even though it is more like a normal class, it is still useful to treat this
# as tuple, because:
# - `date` (as first item) allows comparison and correct sorting order
# - data is immutable
class Reminder(NamedTuple):
    date: datetime
    chatid: str
    userid: str
    msg: str

    @staticmethod
    def from_json(self, node: List) -> "Reminder":
        return Reminder(datetime.fromisoformat(node[0]), *node[1:])

    def to_json_tuple(self):
        return (self.date.isoformat(), *self[1:])

    def get_remaining_seconds(self, timezone) -> float:
        return (self.date - datetime.now(timezone)).total_seconds()


class Plugin(bot.BotPlugin):
    def __init__(self, oldme: "Plugin", bot: bot.Bot):
        self._parsers = []  # type: List[parsedatetime.Calendar]
        self._timer = None  # type: asyncio.Task
        self._timezone = None  # type: pytz.BaseTzInfo
        self._reminders = PriorityQueue()  # type: PriorityQueue[Reminder]

        super(Plugin, self).__init__(oldme, bot)

        self.register_command("remindme", self._remindme)

    def reload(self):
        super(Plugin, self).reload()

        try:
            self._timezone = pytz.timezone(self.cfg["timezone"])
        except pytz.UnknownTimeZoneError as e:
            # Log exception if given timezone is not empty
            if e.args[0]:
                logging.exception(e)
            logging.warning("Using system timezone")
            self._timezone = None

        langs = self.cfg["langs"]

        if len(langs) == 0:
            logging.warning("%s: No languages specified -> using default.", self.name)
            self._parsers = [ parsedatetime.Calendar() ]
        else:
            self._parsers = [ parsedatetime.Calendar(parsedatetime.Constants(i)) for i in langs ]

        for i in self.cfg["timers"]:
            self._schedule(Reminder.from_json(i), only_queue=True)
        self._restart_timer()

    def quit(self):
        self._stop_timer()
        super(Plugin, self).quit()

    async def _remindme(self, msg: api.ChatMessage, argv: List[str]):
        """Syntax: remindme <date/time> [text]

        Schedule a timer for the given date/time and send a message when the time has passed.
        <time> can be any human readable date/time string, e.g. "tomorrow", "5m", "22.7.2022", "1h 5m 30s", "15:30", etc.

        Extra text not containing any time information is ignored and can be used as message.

        NOTE: Be aware that all dates/times are relative to the bot's timezone.

        Example: !remindme 5m 5 minutes have passed
        """
        text = " ".join(argv[1:])

        for i in self._parsers:
            logging.debug("Trying parser %s", i.ptc.localeID)
            date, result = i.parseDT(text, tzinfo=self._timezone)

            if result != 0:
                break

        if result == 0:
            await msg.reply("Failed to parse date/time.")
            return

        self._schedule(Reminder(date, msg.chat.id, msg.author.id, msg.text))
        await msg.reply("Reminding you on {} (UTC+{})".format(
            date, int(date.utcoffset().total_seconds() / 3600)))

    def _schedule(self, reminder: Reminder, only_queue: bool = False):
        self._reminders.put(reminder)
        logging.debug("Scheduled %s", reminder.date)

        if not only_queue:
            self.cfg["timers"].append(reminder.to_json_tuple())
            self.cfg.write()

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
        delta = reminder.get_remaining_seconds(self._timezone)
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
        self.cfg["timers"] = [ i.to_json_tuple() for i in self._reminders.queue ]
        self.cfg.write()
        logging.debug("Reminder removed: %s", reminder)

    @staticmethod
    def get_default_config():
        return {
            "timezone": "",  # Empty for system default. See pytz.all_timezones.
            "message": "Reminding you!",
            "langs": [
                "en_US",
                "de_DE",
            ],
            "timers": [],  # type: List[Reminder]
        }
