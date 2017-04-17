# -*- coding: utf-8 -*-


class GroupInvite(object):
    """Represents a group invite."""

    def get_author(self):
        """Returns a User object of the sender."""
        raise NotImplementedError

    def accept(self):
        raise NotImplementedError

    def decline(self):
        raise NotImplementedError
