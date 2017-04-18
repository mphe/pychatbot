# -*- coding: utf-8 -*-

from pytoxcore import ToxCore
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
        return len(self._peers)

    def leave(self):
        self._tox.tox_conference_delete(self._id)
        self._tox._purge_conference(self._id)


    def _find_peer(self, num):
        if not num in self._peers:
            self._peers[num] = GroupPeer(self._id, num)
        return self._peers[num]

    def _message_received(self, peer_number, msgtype, text):
        if self._tox.tox_conference_peer_number_is_ours(self._id, peer_number):
            return
        self._tox._trigger(api.APIEvents.Message, Message(
            self._find_peer(peer_number), text, self, translate_type_tox(msgtype)))

    def _namelist_change(self, peer_number, change):
        peer = self._find_peer(peer_number)
        if change == ToxCore.TOX_CONFERENCE_STATE_CHANGE_PEER_NAME_CHANGE:
            # initial name change -> join
            if peer.update_name(self._tox.tox_conference_peer_get_name(self._id, peer_number)):
                self._tox._trigger(api.APIEvents.GroupMemberJoin, self, peer)
        elif change == ToxCore.TOX_CONFERENCE_STATE_CHANGE_PEER_EXIT:
            del self._peers[peer_number]
            self._tox._trigger(api.APIEvents.GroupMemberLeave, self, peer)
