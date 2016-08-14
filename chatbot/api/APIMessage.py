# -*- coding: utf-8 -*-


class ChatMessage(object):
    def get_text(self):
        raise NotImplementedError

    def get_author(self):
        raise NotImplementedError

    def is_editable():
        raise NotImplementedError

    def edit(self, newstr):
        raise NotImplementedError

    def __str__(self):
        return "{}: {}".format(self.get_author(), self.get_text())
