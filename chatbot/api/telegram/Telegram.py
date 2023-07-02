# -*- coding: utf-8 -*-

import telethon
from telethon.tl.functions.account import UpdateProfileRequest
import logging
from chatbot import api
from typing import Iterable
from .User import User
from .Chat import Chat
from .ChatMessage import ChatMessage

# NOTE:
# =====
# To allow receiving NewMessage events in groups, you must disable group
# privacy for your bot using @BotFather.
# 1. /start
# 2. /mybots
# 3. (select a bot)
# 4. Bot Settings
# 5. Group Privacy
# 6. Turn off


class TelegramAPI(api.APIBase):
    def __init__(self, api_id, stub, opts: dict):
        super().__init__(api_id, stub)
        self._opts = opts
        self._client: telethon.TelegramClient = None
        self._me: User = None

    @property
    def version(self) -> str:
        return telethon.version.__version__

    @property
    def api_name(self) -> str:
        return "Telegram"

    @property
    def is_ready(self) -> bool:
        return self._client and self._client.is_connected()

    async def start(self) -> None:
        logging.info("NOTE: To receive NewMessage events in groups, you must disable group privacy for your bot using @BotFather.")

        self._client = telethon.TelegramClient(session=self._opts["session_file"],
                                               api_id=self._opts["api_id"],
                                               api_hash=self._opts["api_hash"])
        self._client.add_event_handler(self._on_receive, telethon.events.NewMessage)
        self._client.add_event_handler(self._on_chat_action, telethon.events.ChatAction)

        await self._client.start(bot_token=self._opts["bot_token"])

        if not self._client.is_connected():
            logging.error("Failed to connect")
            return

        # Cache this, so it can be accessed in non async methods when needed, e.g. Message.is_editable.
        me = await self._client.get_me()
        self._me = User(self, me)
        logging.info("Logged in as %s %s (%s, %s)", me.first_name, me.last_name, me.username, me.id)
        await self._on_ready()

        async with self._client:
            await self._client.run_until_disconnected()

    async def cleanup(self) -> None:
        pass

    async def close(self) -> None:
        logging.info("Logging out...")
        await self._client.log_out()
        await self._client.disconnect()

    async def get_user(self) -> User:
        return self._me

    async def set_display_name(self, name) -> None:
        if (await self.get_user()).display_name != name:
            await self._client(UpdateProfileRequest(first_name=name, last_name=""))

    async def create_group(self, users: Iterable["api.User"]) -> "api.Chat":
        """Create a new groupchat with the given `api.User`s.

        Returns a Chat object representing the group.
        """
        raise NotImplementedError

    async def find_user(self, userid: str) -> "api.User":
        return await User.create(self, int(userid))

    async def find_chat(self, chatid: str) -> "api.Chat":
        return await Chat.create(self, int(chatid))

    async def _send_message(self, target, message: str) -> telethon.types.Message:
        """Wrapper around client.send_message.

        This is needed because the Telegram API does not seem to trigger
        "message sent" events when using a bot account, so we need to do it
        on our own.
        """
        msg = await self._client.send_message(target, message)
        await self._on_sent(msg)
        return msg

    @staticmethod
    def get_default_options() -> dict:
        return {
            "api_id": 0,
            "api_hash": "",
            "bot_token": "",
            "session_file": None,
        }

    # Events
    async def _on_ready(self):
        self._trigger(api.APIEvents.Ready)

    async def _on_receive(self, event: telethon.events.NewMessage.Event):
        msg: telethon.tl.custom.Message = event.message
        # await msg.mark_read()  # Not needed for bot accounts
        # logging.info("received %s", msg.stringify())

        if not msg.out:
            apimsg = await ChatMessage.create(self, msg)
            self._trigger(api.APIEvents.Message, apimsg)
        else:
            await self._on_sent(msg)

    async def _on_sent(self, msg: telethon.tl.custom.Message):
        # logging.info("sent %s", msg.stringify())
        apimsg = await ChatMessage.create(self, msg)
        self._trigger(api.APIEvents.MessageSent, apimsg)

    async def _on_chat_action(self, event: telethon.events.ChatAction.Event):
        if event.user_ids:
            for userid in event.user_ids:
                user = await User.create(self, userid)

                if event.user_added or event.user_joined:
                    self._trigger(api.APIEvents.GroupMemberJoin, user)
                elif event.user_kicked or event.user_left:
                    self._trigger(api.APIEvents.GroupMemberLeave, user)
