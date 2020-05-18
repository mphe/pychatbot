# -*- coding: utf-8 -*-

from chatbot import api  # Needed for typehints. pylint: disable=unused-import


class APIEvents:
    """An enum of API events."""
    Ready            = "Ready"
    Message          = "MessageReceived"
    MessageSent      = "MessageSent"
    FriendRequest    = "FriendRequest"
    GroupInvite      = "GroupInvite"
    GroupMemberJoin  = "GroupMemberJoin"
    GroupMemberLeave = "GroupMemberLeave"


def iterevents():
    """Returns a generator to iterate over the values in APIEvents."""
    return ( v for k, v in APIEvents.__dict__.items() if not k.startswith("_") )


# The following functions are solely for documentation.

def on_ready():
    """Triggered when the API is initialized and ready to be used"""


def on_message_received(msg: "api.ChatMessage"):
    """Triggered when receiving a message.

    Args:
        msg:            A ChatMessage object
    """


def on_message_sent(msg: "api.ChatMessage"):
    """Triggered when a message was sent.

    Args:
        msg:            A ChatMessage object
    """


def on_friend_request_received(request: "api.FriendRequest"):
    """Triggered when receiving a friend request.

    Args:
        request:        A FriendRequest object
    """


def on_group_invite(invite: "api.GroupInvite"):
    """Triggered when receiving a groupchat invite.

    Args:
        invite:         A GroupInvite object
    """


def on_group_member_join(chat: "api.Chat", user: "api.User"):
    """Triggered when a user joins a groupchat.

    Args:
        chat:           A Chat object representing the groupchat
        user:           A User object of the joined user
    """


def on_group_member_leave(chat: "api.Chat", user: "api.User"):
    """Triggered when a user leaves a groupchat.

    Args:
        chat:           A Chat object representing the groupchat
        user:           A User object of the left user
    """
