# Requires python3
# -*- coding: utf-8 -*-

import os
import logging
import time
from threading import Timer
from pytoxcore import ToxCore
from chatbot import api
from chatbot.compat import *
from . import FriendRequest, Message, Chat, User

class ToxAPI(api.APIBase, ToxCore):
    def __init__(self, api_id, stub, **kwargs):
        self._bootstrap_timer = None
        self._opts = self.get_default_options()
        self._chats = {}
        self._queue = {}    # Stores unsent messages

        # Merge passed arguments with default options
        for i in kwargs:
            self._opts[i] = kwargs[i]

        if os.path.isfile(self._opts["savefile"]):
            self._opts["savedata_type"] = ToxCore.TOX_SAVEDATA_TYPE_TOX_SAVE
            with open(self._opts["savefile"], "rb") as f:
                self._opts["savedata_data"] = f.read()

        api.APIBase.__init__(self, api_id, stub)
        ToxCore.__init__(self, self._opts)

        self._user = User.create_user(self, -1)

        self.tox_add_tcp_relay(self._opts["bootstrap_host"],
                               self._opts["bootstrap_port"],
                               self._opts["bootstrap_key"])

    def attach(self):
        self._bootstrap_timer = None
        if self.tox_self_get_connection_status() == ToxCore.TOX_CONNECTION_NONE:
            logging.info("(Re-)Connecting to bootstrap node...")
            self.tox_bootstrap(self._opts["bootstrap_host"],
                               self._opts["bootstrap_port"],
                               self._opts["bootstrap_key"])

    def detach(self):
        # NOTE: the object needs to be reinstantiated to be able to attach again.
        if self._bootstrap_timer is not None:
            self._bootstrap_timer.cancel()
        self._save()
        self.tox_kill()

    def iterate(self):
        if self.tox_self_get_connection_status() == ToxCore.TOX_CONNECTION_NONE:
            self._reattach()

        self.tox_iterate()
        time.sleep(self.tox_iteration_interval() / 1000.0)

    def version(self):
        # For some reason this is always 0.0.0
        return "{}.{}.{}".format(self.tox_version_major(),
                                 self.tox_version_minor(),
                                 self.tox_version_patch())

    def api_name(self):
        return "Tox"

    def get_user(self):
        return self._user

    def set_display_name(self, name):
        self.tox_self_set_name(name)

    @staticmethod
    def get_default_options():
        # Bootstrap nodes: https://wiki.tox.chat/users/nodes
        # The default bootstrap node is hosted in Germany.
        opts = ToxCore.tox_options_default()
        opts["savefile"] = ""
        # opts["savedata_type"] = ToxCore.TOX_SAVEDATA_TYPE_TOX_SAVE
        opts["bootstrap_host"] = "130.133.110.14"
        opts["bootstrap_port"] = 33445
        opts["bootstrap_key"] = "461FA3776EF0FA655F1A05477DF1B3B614F7D6B124F7DB1DD4FE3C08B03B640F"
        return opts


    # Utility functions
    def _reattach(self):
        """Called to reconnect after the connection to the DHT node is lost.
        
        It waits 10 seconds before reconnecting because the connection state
        "may frequently change for short amounts of time."
        """
        if self._bootstrap_timer is None:
            self._bootstrap_timer = Timer(10, self.attach)
            self._bootstrap_timer.start()

    def _find_chat(self, chat_id):
        if not chat_id in self._chats:
            self._chats[chat_id] = Chat.Chat(chat_id, self)
        return self._chats[chat_id]

    def _send_message(self, text, friend_number):
        for i in range(0, len(text), ToxCore.TOX_MAX_MESSAGE_LENGTH):
            segment = text[i:i + ToxCore.TOX_MAX_MESSAGE_LENGTH]
            id = self.tox_friend_send_message(
                friend_number,
                ToxCore.TOX_MESSAGE_TYPE_NORMAL,
                segment
            )
            self._queue[id] = Message.Message(self._user,
                                      segment,
                                      self._find_chat(friend_number))

    def _save(self):
        if self._opts["savefile"]:
            tmpfile = self._opts["savefile"] + ".tmp"
            with open(tmpfile, "wb") as f:
                f.write(self.tox_get_savedata())
            os.rename(tmpfile, self._opts["savefile"])
            logging.debug("Profile saved.")

    # Tox events
    def tox_friend_request_cb(self, pubkey, msg):
        req = FriendRequest.FriendRequest(self, pubkey, msg)
        self._trigger(api.APIEvents.FriendRequest, req)

        # Let's save, just in case
        self._save()

    def tox_friend_message_cb(self, friend_number, text):
        msg = Message.Message(User.create_user(self, friend_number),
                      text,
                      self._find_chat(friend_number))
        self._trigger(api.APIEvents.Message, msg)

    def tox_friend_read_receipt_cb(self, friend_number, message_id):
        self._trigger(api.APIEvents.MessageSent, self._queue[message_id])
        del self._queue[message_id]
