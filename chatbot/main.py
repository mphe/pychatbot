#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import logging
import argparse
import chatbot.bot


def main():
    parser = argparse.ArgumentParser(
        description="Run the bot using a given profile and/or a given API.",
        epilog="At least one of -p/--profile or -a/--api has to be specified."
    )
    parser.add_argument("-p", "--profile",    help="Profile name", default="")
    parser.add_argument("-a", "--api",        help="API name",     default="")
    parser.add_argument("-d", "--profiledir", help="Profile directory (bot config). If not specified, the platform specific default directory is used.")
    parser.add_argument("-c", "--configdir",  help="Config directory (plugin configs). If not specified, the profile directory is used..")
    parser.add_argument("-v", "--verbose",    help="Show debug output",
                        action="store_true")
    args = parser.parse_args()

    if not args.profile and not args.api:
        parser.error("An API and/or a profile has to specified.")
        return 1

    logging.basicConfig(level=logging.DEBUG,
                        filemode="a", filename="chatbot.log",
                        format="%(levelname)s: %(message)s")

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logging.root.addHandler(handler)

    logging.debug("------------------------ MAIN ------------------------")

    bot = chatbot.bot.Bot(args.profiledir)

    try:
        bot.init(profile=args.profile, apiname=args.api, configdir=args.configdir)
        return asyncio.run(bot.run())
    except (KeyboardInterrupt, SystemExit) as e:
        logging.info(e)
    except Exception as e:
        logging.exception(e)
        return chatbot.bot.ExitCode.Error


if __name__ == "__main__":
    sys.exit(main())
