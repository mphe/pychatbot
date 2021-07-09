#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import asyncio
import logging
from context import api, bot, print_message


async def on_friend_request(req: api.FriendRequest):
    logging.info("Received friend request from %s", req.author.id)
    await req.accept()
    logging.info("Accepted.")


async def on_message(msg: api.ChatMessage):
    print_message(msg, "Received")
    await msg.chat.send_message(msg.text)


async def on_ready():
    logging.info("Type !exit or !quit to exit.")


async def main():
    profilemgr = bot.BotProfileManager(os.path.dirname(__file__))
    profile = profilemgr.load_or_create("test_profile", "test")
    profile.log_rotate()

    b = bot.Bot(profile)
    await b.init()
    b.register_event_handler(api.APIEvents.FriendRequest, on_friend_request)
    b.register_event_handler(api.APIEvents.Message, on_message)
    b.register_event_handler(api.APIEvents.Ready, on_ready)

    async def exitcmd(_msg, _argv):
        await b.close()

    b.register_command("exit", exitcmd, argc=0)
    b.register_command("quit", exitcmd, argc=0)

    await b.run()


if __name__ == "__main__":
    asyncio.run(main())
