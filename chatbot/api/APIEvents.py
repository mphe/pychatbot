# -*- coding: utf-8 -*-


class APIEvents(object):
    """An enum of API events."""
    Message         = "MessageReceived"
    MessageSent     = "MessageSent"
    Filetrans       = "FiletransferReceived"
    FriendRequest   = "FriendRequest"


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

def on_filetransfer_received(filetrans):
    """Triggered when receiving a message.
    
    Parameters:
        filetrans:      A filetransfer object
    """
    pass

def on_friend_request_received(request):
    """Triggered when receiving a friend request.
    
    Parameters:
        request:        A FriendRequest object
    """
    pass
