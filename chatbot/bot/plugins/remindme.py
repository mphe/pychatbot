# -*- coding: utf-8 -*-

import time
import asyncio
from datetime import datetime
from typing import List, Tuple, NamedTuple
import logging
import parsedatetime
from chatbot import api, bot, util
from queue import PriorityQueue


# DON'T CHANGE ATTRIBUTE ORDER!
# Changing order will break serialization.
# isoformat should be the first item, to ensure correct sorting order.
class Reminder(NamedTuple):
    isoformat: str
    chatid: str
    userid: str
    msg: str


def time_get_utc() -> int:
    return int(time.localtime().tm_gmtoff / 3600)


class Plugin(bot.BotPlugin):
    def __init__(self, bot_: bot.Bot):
        super().__init__(bot_)
        self._parsers: List[parsedatetime.Calendar] = []
        self._timer: asyncio.Task = None
        self._reminders: PriorityQueue[Reminder] = PriorityQueue()

        self.register_command("remindme", self._remindme)
        self.register_command("reminders", self._print_reminders, argc=0)

    async def reload(self):
        await super().reload()

        langs = self.cfg["langs"]

        if len(langs) == 0:
            logging.warning("%s: No languages specified -> using default.", self.name)
            self._parsers = [ parsedatetime.Calendar() ]
        else:
            self._parsers = [ parsedatetime.Calendar(parsedatetime.Constants(i, usePyICU=False)) for i in langs ]

        for i in self.cfg["timers"]:
            self._reminders.put(Reminder(*i))
        self._restart_timer()

    async def quit(self):
        self._stop_timer()
        await super().quit()

    async def _print_reminders(self, msg: api.ChatMessage, argv: List[str]):
        """Syntax: reminders [all]

        Lists all active reminders for the current user in the current chat.
        If `all` is given, or when in private chat with the bot, all reminders from all chats are listed.
        """
        chat = await msg.author.get_chat()
        listall = bot.command.get_argument(argv, 1, "") == "all" \
            or chat.id == msg.chat.id
        num_other_reminders = 0
        output: List[str] = []

        r: Reminder
        for r in self._reminders.queue:
            if r.userid == msg.author.id:
                if listall or r.chatid == msg.chat.id:
                    date = datetime.fromisoformat(r.isoformat)
                    num_reminders = len(output) + 1
                    output.append(f"{num_reminders}) {date} (UTC+{time_get_utc()})\n> {r.msg}")
                else:
                    num_other_reminders += 1

        if output:
            # Add newline after reminders, if there are other reminders
            if num_other_reminders:
                output.append("")
        else:
            if not num_other_reminders:
                output.append("You have no active reminders.")
            else:
                output.append("You have no active reminders in this chat.")

        if num_other_reminders > 0:
            output.append(f"You have {num_other_reminders} more reminder(s) in other chats.")

        await msg.reply("\n".join(output))

    async def _remindme(self, msg: api.ChatMessage, argv: List[str]):
        """Syntax: remindme <date/time> [# text]

        Schedule a timer for the given date/time and send a message when the time has passed.
        <time> can be any human readable date/time string, e.g. "tomorrow", "5m", "22.7.2022", "1h 5m 30s", "15:30", etc.

        NOTE: Be aware that all dates/times are relative to the bot's system timezone.

        Extra text not containing any time information is ignored and can be used as message.
        To separate extra text from time information, in case it would be interpreted as such, use "#" as separator.

        **Examples:**
        `!remindme 5m some reminder text`
            Sets a timer to 5 minutes.
            "some reminder text" will be ignored since it does not contain any time information.

        `!remindme 7.7. # tomorrow important date`
            Sets a timer to 7. July of current year.
            A "#" is required here because otherwise "tomorrow" would be interpreted as date.
        """
        text = " ".join(argv[1:])
        comment_idx = text.find("#")

        if comment_idx != -1:
            text = text[:comment_idx]

        for i in self._parsers:
            logging.debug("Trying parser %s", i.ptc.localeID)
            struct, result = i.parse(text)

            if result != 0:
                date = datetime(*struct[:6])
                self._schedule(Reminder(date.isoformat(), msg.chat.id, msg.author.id, msg.text))
                await msg.reply(f"Reminding you on {date} (UTC+{time_get_utc()})")
                return

        await msg.reply("Failed to parse date/time.")

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
            "timers": [],
        }
