# -*- coding: utf-8 -*-


class FriendRequest(object):
    """Represents a friend request."""
    def __init__(self):
        pass

    def get_username(self):
        """Returns the sender's username."""
        raise NotImplementedError

    def get_text(self):
        """Returns the message sent with the friend request."""
        return ""

    def accept(self):
        raise NotImplementedError

    def decline(self):
        raise NotImplementedError
