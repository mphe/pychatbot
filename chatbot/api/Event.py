# -*- coding: utf-8 -*-


class Event(object):
    def __init__(self):
        self._handlers = []

    def add_handler(self, callback):
        """Adds a callback that will be called when the event is triggered."""
        self._handlers.append(callback)

    def del_handler(self, callback):
        """Remove a previously registered callback."""
        self._handlers.remove(callback)

    def clear(self):
        self._handlers = []

    def trigger(self, *args):
        """Calls every registered event handler with the given arguments."""
        for i in self._handlers:
            i(*args)

    def __len__(self):
        return len(self._handlers)
