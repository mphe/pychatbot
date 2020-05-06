#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import asyncio
import logging
from context import api, bot, print_message


async def on_friend_request(req):
    logging.info("Received friend request from %s", req.get_author().id())
    await req.accept()
    logging.info("Accepted.")


async def on_message(msg):
    print_message(msg, "Received")
    await msg.get_chat().send_message(msg.get_text())


async def on_ready():
    logging.info("Type !exit or !quit to exit.")


def main():
    b = bot.Bot(os.path.join(os.path.dirname(__file__), "test_profile"))
    b.init(apiname="test")
    b.register_event_handler(api.APIEvents.FriendRequest, on_friend_request)
    b.register_event_handler(api.APIEvents.Message, on_message)
    b.register_event_handler(api.APIEvents.Ready, on_ready)

    async def exitcmd(_msg, _argv):
        await b.close()

    b.register_command("exit", exitcmd, argc=0)
    b.register_command("quit", exitcmd, argc=0)

    asyncio.run(b.run())


if __name__ == "__main__":
    main()
