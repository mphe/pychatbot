#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import logging
import argparse
import chatbot.bot


async def main():
    parser = argparse.ArgumentParser(
        description="""
Run the bot using a given profile and/or a given API.
At least one of -p/--profile or -a/--api has to be specified.

A profile is a configuration file located in the platform specific default
directory, e.g. "~/.config" on Linux, or %appdata% on windows, containing Bot
and API specific configuration, e.g. login credentials.
If the given profile does not exist, it will be created, however you also need to specify the API in this case.

Usually, in order to connect to chat protocols, you will need an account and/or a bot token to log in,
hence, specifying only an API using -a/--api, will most likely fail due to missing login credentials.
        """
    )
    parser.add_argument("-p", "--profile",       help="Profile name", default="")
    parser.add_argument("-a", "--api",           help="API name",     default="")
    parser.add_argument("-l", "--list-profiles", help="List available profiles", action="store_true")
    parser.add_argument("-v", "--verbose",       help="Show debug output", action="store_true")
    args = parser.parse_args()

    if args.list_profiles:
        print("Available profiles:", ", ".join(chatbot.bot.BotProfileManager().get_profiles()))
        return 0

    if not args.profile and not args.api:
        parser.error("An API and/or a profile has to specified.")
        return 1

    profilemgr = chatbot.bot.BotProfileManager()
    profile = profilemgr.load_or_create(args.profile, args.api)
    profile.log_rotate()

    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s",
                        filemode="a", filename=profile.get_log_path())

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logging.root.addHandler(handler)

    logging.debug("------------------------ MAIN ------------------------")

    bot = chatbot.bot.Bot(profile)

    try:
        await bot.init()
        return await bot.run()
    except (KeyboardInterrupt, SystemExit) as e:
        logging.info(e)
    except Exception as e:
        logging.exception(e)
        return chatbot.bot.ExitCode.Error


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
