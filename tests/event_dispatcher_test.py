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
    logging.info("Received friend request from " + req.author_handle())
    req.accept()
    logging.info("Accepted.")

def on_message(msg):
    print_message(msg, "Received")
    msg.get_chat().send_message(msg.get_text())


class Test(object):
    def __init__(self):
        self.running = True
        self.apiobj = None
        self.dispatcher = None

    def command_handler(self, msg):
        if msg.get_text().startswith("!"):
            cmd = msg.get_text()[1:]
            logging.info("User entered command: " + cmd)

            if cmd == "exit":
                self.running = False
            elif cmd == "silent":
                self.dispatcher.unregister_event_handler(api.APIEvents.Message,
                                                         on_message)
            elif cmd == "unsilent":
                self.dispatcher.register_event_handler(api.APIEvents.Message,
                                                       on_message)

    def run(self):
        self.apiobj = api.create_api_object("tox", savefile="profile.tox")
        self.dispatcher = util.APIEventDispatcher(self.apiobj)
        self.dispatcher.register_event_handler(api.APIEvents.FriendRequest,
                                               on_friend_request)
        self.dispatcher.register_event_handler(api.APIEvents.Message,
                                               on_message)
        self.dispatcher.register_event_handler(api.APIEvents.Message,
                                               self.command_handler)

        self.apiobj.attach()
        logging.info("Attached")

        try:
            while self.running:
                self.apiobj.iterate()
        except (KeyboardInterrupt, SystemExit) as e:
            pass
        finally:
            logging.info("Shuttin down...")
            self.apiobj.detach()


if __name__ == "__main__":
    Test().run()
