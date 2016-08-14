# -*- coding: utf-8 -*-

import logging


class APIEvents(object):
    """An enum of API events."""
    Message         = "MessageReceived"
    MessageSent     = "MessageSent"
    Filetrans       = "FiletransferReceived"


# The following functions are solely for documentation.

def on_message_received(msg):
    """Triggered when receiving a message.
    
    Parameters:
        msg:            A message object
    """
    pass

def on_message_sent(msg):
    """Triggered when a message was sent.
    
    Parameters:
        msg:            A message object
    """
    pass

def on_filetransfer_received(filetrans):
    """Triggered when receiving a message.
    
    Parameters:
        filetrans:            A filetransfer object
    """
    pass
