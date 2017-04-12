#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import argparse
import chatbot.bot

def main():
    parser = argparse.ArgumentParser(
        description="Run the bot using a given profile and/or a given API.",
        epilog="At least one of -p/--profile or -a/--api has to be specified."
    )
    parser.add_argument("-p", "--profile",   help="Profile name", default="")
    parser.add_argument("-a", "--api",       help="API name",     default="")
    parser.add_argument("-c", "--configdir", help="Config directory")
    parser.add_argument("-d", "--debug",     help="Show debug output",
                        action="store_true")
    args = parser.parse_args()

    if not args.profile and not args.api:
        parser.error("an API and/or a profile has to specified.")
        return 1

    logging.basicConfig(level=(logging.DEBUG if args.debug else logging.INFO),
                        format="%(levelname)s:%(message)s")

    if args.configdir:
        bot = chatbot.bot.Bot(args.configdir)
    else:
        bot = chatbot.bot.Bot()

    return bot.run(profile=args.profile, apiname=args.api)


if __name__ == "__main__":
    sys.exit(main())
