# -*- coding: utf-8 -*-


class APIEvents(object):
    """An enum of API events."""
    Message          = "MessageReceived"
    MessageSent      = "MessageSent"
    FriendRequest    = "FriendRequest"
    GroupInvite      = "GroupInvite"
    GroupMemberJoin  = "GroupMemberJoin"
    GroupMemberLeave = "GroupMemberLeave"


def iterevents():
    """Returns a generator to iterate over the values in APIEvents."""
    return ( v for k,v in APIEvents.__dict__.iteritems() if not k.startswith("_") )


# The following functions are solely for documentation.

def on_message_received(msg):
    """Triggered when receiving a message.
    
    Parameters:
        msg:            A ChatMessage object
    """
    pass

def on_message_sent(msg):
    """Triggered when a message was sent.
    
    Parameters:
        msg:            A ChatMessage object
    """
    pass

def on_friend_request_received(request):
    """Triggered when receiving a friend request.
    
    Parameters:
        request:        A FriendRequest object
    """
    pass

def on_group_invite(invite):
    """Triggered when receiving a groupchat invite.
    
    Parameters:
        invite:         A GroupInvite object
    """
    pass

def on_group_member_join(chat, user):
    """Triggered when a user joins a groupchat.
    
    Parameters:
        chat:           A Chat object representing the groupchat
        user:           A User object of the joined user
    """
    pass

def on_group_member_leave(chat, user):
    """Triggered when a user leaves a groupchat.
    
    Parameters:
        chat:           A Chat object representing the groupchat
        user:           A User object of the left user
    """
    pass
