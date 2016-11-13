#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import logging
from context import *


def print_message(msg, prefix):
    logging.info("{} message in {}:\n\t {}".format(
        prefix,
        str(msg.get_chat()),
        str(msg)
    ))


def on_friend_request(req):
    logging.info("Received friend request from " + req.get_author().handle())
    req.accept()
    logging.info("Accepted.")

def on_message(msg):
    print_message(msg, "Received")
    msg.get_chat().send_message(msg.get_text())


def main():
    b = bot.Bot("tox", savefile="profile.tox")
    b.init()
    b.register_event_handler(api.APIEvents.FriendRequest, on_friend_request)
    b.register_event_handler(api.APIEvents.Message, on_message)
    b.run()


if __name__ == "__main__":
    main()
