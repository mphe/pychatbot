# -*- coding: utf-8 -*-

import logging
from pytoxcore import ToxCore, ToxCoreException
import chatbot.api as api
from .Message import Message, split_text
from .User import GroupPeer, Friend


def translate_type(msgtype):
    if msgtype == api.MessageType.Normal:
        return ToxCore.TOX_MESSAGE_TYPE_NORMAL
    else:
        return ToxCore.TOX_MESSAGE_TYPE_ACTION

def translate_type_tox(msgtype):
    if msgtype == ToxCore.TOX_MESSAGE_TYPE_NORMAL:
        return api.MessageType.Normal
    else:
        return api.MessageType.Action


class Chat(api.Chat):
    def __init__(self, friend_number, tox):
        self._tox = tox
        self._friend = Friend(self._tox, friend_number)
        self._queue = {}  # Stores messages waiting for a read-receipt

    def id(self):
        return self._friend.handle()

    def send_message(self, text, msgtype=api.MessageType.Normal):
        for seg in split_text(text):
            msgid = self._tox.tox_friend_send_message(
                self._friend.number(), translate_type(msgtype), seg)
            self._queue[msgid] = Message(self._tox.get_user(), seg, self, msgtype)

    def send_action(self, text):
        self.send_message(text, msgtype=api.MessageType.Action)

    def type(self):
        return api.ChatType.Normal

    def is_anonymous(self):
        return False


    def _read_receipt(self, msgid):
        if msgid in self._queue:
            self._tox._trigger(api.APIEvents.MessageSent, self._queue[msgid])
            del self._queue[msgid]

    def _message_received(self, msgtype, text):
        self._tox._trigger(api.APIEvents.Message, Message(
            self._friend, text, self, translate_type_tox(msgtype)))


class GroupChat(api.Chat):
    def __init__(self, conf_number, tox):
        self._id = conf_number
        self._tox = tox
        self._peers = {}

    def id(self):
        return "g" + str(self._id)

    def send_message(self, text, msgtype=api.MessageType.Normal):
        for segment in split_text(text):
            self._tox.tox_conference_send_message(
                self._id, translate_type(msgtype), segment)
            self._tox._trigger(api.APIEvents.MessageSent,
                               Message(self._tox.get_user(), segment, self, msgtype))

    def send_action(self, text):
        self.send_message(text, api.MessageType.Action)

    def type(self):
        return api.ChatType.Group

    def is_anonymous(self):
        return True

    def size(self):
        return 1 + len(self._peers) if self._id >= 0 else 0

    def leave(self):
        self._tox.tox_conference_delete(self._id)
        self._tox._purge_conference(self._id)
        self._peers.clear()
        self._id = -1

    def invite(self, user):
        self._tox.tox_conference_invite(user.number(), self._id)

    def _is_our_number(self, number):
        try:
            if self._tox.tox_conference_peer_number_is_ours(self._id, number):
                return True
        except SystemError as e:
            pass
        return False

    def _update_peers(self):
        self._peers.clear()
        logging.debug("Updating peer list")
        for i in range(self._tox.tox_conference_peer_count(self._id)):
            if self._is_our_number(i):
                continue
            name = self._tox.tox_conference_peer_get_name(self._id, i)
            self._peers[i] = GroupPeer(self._id, i, name)
            logging.debug("\t" + str(self._peers[i]))

    def _message_received(self, peer_number, msgtype, text):
        if self._is_our_number(peer_number):
            return
        self._tox._trigger(api.APIEvents.Message, Message(
            self._peers[peer_number], text, self, translate_type_tox(msgtype)))

    def _namelist_change(self, peer_number, change):
        if change == ToxCore.TOX_CONFERENCE_STATE_CHANGE_PEER_JOIN:
            return

        if change == ToxCore.TOX_CONFERENCE_STATE_CHANGE_PEER_NAME_CHANGE:
            if self._is_our_number(peer_number):
                return

            name = self._tox.tox_conference_peer_get_name(self._id, peer_number)

            # initial name change -> join
            if not peer_number in self._peers:
                peer = GroupPeer(self._id, peer_number, name)
                self._peers[peer_number] = peer
                self._tox._trigger(api.APIEvents.GroupMemberJoin, self, peer)
                logging.debug("User joined: " + str(peer))
            else:
                self._peers[peer_number]._name = name
                logging.debug("User changed name: " + str(self._peers[peer_number]))

        elif change == ToxCore.TOX_CONFERENCE_STATE_CHANGE_PEER_EXIT:
            peer = self._peers[peer_number]
            logging.debug("User left: " + str(peer))
            self._update_peers()
            self._tox._trigger(api.APIEvents.GroupMemberLeave, self, peer)
