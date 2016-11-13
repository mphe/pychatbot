# -*- coding: utf-8 -*-


class FriendRequest(object):
    """Represents a friend request."""

    def get_author(self):
        """Returns a User object of the sender."""
        raise NotImplementedError

    def get_text(self):
        """Returns the message sent with the friend request."""
        return ""

    def accept(self):
        raise NotImplementedError

    def decline(self):
        raise NotImplementedError
