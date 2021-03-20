# -*- coding: utf-8 -*-

from chatbot import api  # Needed for typehints. pylint: disable=unused-import


class MetaAPIEvents(type):
    def __iter__(self):
        return ( v for k, v in APIEvents.__dict__.items() if not k.startswith("_") )


class APIEvents(metaclass=MetaAPIEvents):
    """An enum of API events."""
    Ready            = "Ready"
    Message          = "MessageReceived"
    MessageSent      = "MessageSent"
    FriendRequest    = "FriendRequest"
    GroupInvite      = "GroupInvite"
    GroupMemberJoin  = "GroupMemberJoin"
    GroupMemberLeave = "GroupMemberLeave"


# The following functions are solely for documentation.

async def on_ready():
    """Triggered when the API is initialized and ready to be used"""


async def on_message_received(_msg: "api.ChatMessage"):
    """Triggered when receiving a message.

    Args:
        msg: A ChatMessage object
    """


async def on_message_sent(_msg: "api.ChatMessage"):
    """Triggered when a message was sent.

    Args:
        msg: A ChatMessage object
    """


async def on_friend_request_received(_request: "api.FriendRequest"):
    """Triggered when receiving a friend request.

    Args:
        request: A FriendRequest object
    """


async def on_group_invite(_invite: "api.GroupInvite"):
    """Triggered when receiving a groupchat invite.

    Args:
        invite: A GroupInvite object
    """


async def on_group_member_join(_chat: "api.Chat", _user: "api.User"):
    """Triggered when a user joins a groupchat.

    Args:
        chat: A Chat object representing the groupchat
        user: A User object of the joined user
    """


async def on_group_member_leave(_chat: "api.Chat", _user: "api.User"):
    """Triggered when a user leaves a groupchat.

    Args:
        chat: A Chat object representing the groupchat
        user: A User object of the left user
    """
