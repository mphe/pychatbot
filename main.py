#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import chatbot

def main():
    if len(sys.argv) == 1:
        print("Usage: main.py <api>")
        return

    while True:
        bot = chatbot.bot.Bot(sys.argv[1])
        bot.init()
        err = bot.run()
        if err == chatbot.bot.ExitCode.Restart:
            reload(chatbot.bot)
            continue
        return err

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
