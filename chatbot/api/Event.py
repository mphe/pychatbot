# -*- coding: utf-8 -*-


class EventHandle(object):
    def __init__(self, callback):
        self._callback = callback
        self._remove = False

    def unregister(self):
        self._remove = True

    def __nonzero__(self):
        return not self._remove

    def __repr__(self):
        return "EventHandle({})".format(repr(self._callback))


class Event(object):
    """Contains a list of callbacks and calls them when the event is trigger()ed.
    
    It's safe to remove/unregister a callback during the trigger() loop
    (unregistering a callback inside the callback).
    """

    def __init__(self):
        self._handlers = []

    def add_handler(self, callback):
        """Adds a callback that will be called when the event is triggered.
        
        Returns a handle that can be used to unregister.
        """
        self._handlers.append(EventHandle(callback))
        return self._handlers[-1]

    def del_handler(self, callback):
        """Marks a previously registered callback for removal.
        
        To prevent interference with the loop inside trigger() the function
        won't be removed immediately (it also won't be called anymore).
        At the end of trigger() the list is cleaned from everything marked
        for removal. This can also be accomplished by running clean().
        """
        next(i for i in self._handlers if i and i._callback == callback).unregister()

    def clear(self):
        self._handlers = []

    def clean(self):
        """Remove every handler that was  marked for removal.

        MUST NOT BE CALLED INSIDE trigger()
        """
        self._handlers = filter(lambda i: i, self._handlers)

    def trigger(self, *args):
        """Calls every registered event handler with the given arguments."""
        # Event handlers that have been registered during this loop must not
        # be called. Therefore we need to store the length of the handler list
        # and access the individual callbacks by index.
        for i in range(len(self._handlers)):
            if self._handlers[i]:
                self._handlers[i]._callback(*args)
        self.clean()

    def __len__(self):
        return len(self._handlers)
