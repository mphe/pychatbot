# -*- coding: utf-8 -*-


class FriendRequest(object):
    """Represents a friend request."""

    def author_handle(self):
        """Returns the sender's user handle."""
        raise NotImplementedError

    def get_text(self):
        """Returns the message sent with the friend request."""
        return ""

    def accept(self):
        raise NotImplementedError

    def decline(self):
        raise NotImplementedError
