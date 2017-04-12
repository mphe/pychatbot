# -*- coding: utf-8 -*-

from context import *
import logging

class Plugin(bot.subsystem.plugin.BasePlugin):
    def __init__(self, oldme, x):
        logging.info("Received parameter x=" + str(x))

    def reload(self):
        logging.info("testplugin.reload")

    def quit(self):
        logging.info("testplugin.quit")


