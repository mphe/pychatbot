# -*- coding: utf-8 -*-


class Event(object):
    def __init__(self):
        self._handlers = []

    def add_handler(self, callback):
        """Adds a callback that will be called when the event is triggered."""
        self._handlers.append(callback)

    def del_handler(self, callback):
        """Remove a previously registered callback."""
        try:
            self._handlers.remove(callback)
        except ValueError:
            pass

    def trigger(self, *args):
        """Calls every registered event handler with the given arguments."""
        for i in self._handlers:
            i(*args)
