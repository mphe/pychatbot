# -*- coding: utf-8 -*-

import asyncio
from sortedcontainers import SortedList

# Return values for callbacks to determine if event execution should be
# continued or stopped.
EVENT_CONTINUE = 0  # continue
EVENT_HANDLED  = 1  # stop

# Predefined nice-values, not necessary but makes things cleaner
EVENT_PRE    = -1000
EVENT_NORMAL = 0
EVENT_POST   = 1000


class Handle:
    def __init__(self, event, callback, nice):
        self._event = event
        self._callback = callback
        self._remove = False
        self._nice = nice

    def unregister(self):
        if not self._remove:
            self._remove = True
            self._event._dirty += 1
            # Avoid preventing garbage collection
            self._callback = None
            self._event = None

    def __del__(self):
        self.unregister()

    def __call__(self, *args, **kwargs):
        return self._callback(*args, **kwargs)

    def __bool__(self):
        return not self._remove

    def __str__(self):
        return repr(self._callback)

    def __repr__(self):
        return "Handle({}, {}, {})".format(
            repr(self._event), repr(self._callback), repr(self._nice))


class Event:
    """Contains a list of callbacks and calls them when the event is trigger()ed.

    It's safe to remove/unregister a callback during the trigger() loop
    (unregistering a callback inside a callback).

    Callbacks can return a value to determine whether the event execution
    should be continued or stopped. This might be useful when certain events
    should only be handled by specific event handlers.
    Returning nothing or EVENT_CONTINUE will continue executing the remaining
    handlers. EVENT_HANDLED will stop the execution.

    To guarantee that every handler will be called, regardless of return
    values, use the trigger_all() function.
    """

    def __init__(self):
        self._handlers = SortedList(key=lambda x: x._nice)
        self._waiting = []  # Callbacks waiting to get inserted
        self._dirty = 0     # counts how many handlers need to be removed
        self._running = False   # Whether or not trigger() is currently executed

    def register(self, callback, nice=EVENT_NORMAL):
        """Adds a callback that will be called when the event is triggered.

        Returns a handle that can be used to unregister.

        `callback` must be a coroutine.
        `nice` determines the priority. Lower priorities are called first,
        higher ones later. For simplicity and readability there are some
        predefined constants for common priorities:
            EVENT_PRE    = -1000
            EVENT_NORMAL = 0
            EVENT_POST   = 1000
        If `nice` is not specified, EVENT_NORMAL is used.

        The callback may return EVENT_HANDLED to abort the event
        execution early. (See also class docstring)
        """
        assert asyncio.iscoroutinefunction(callback), "Callback must be a coroutine"

        hnd = Handle(self, callback, nice)
        if not self._running:
            self._handlers.add(hnd)
        else:
            # Event handlers that have been registered inside another
            # callback must not be called inside the same trigger()-loop
            # (e.g. reloading could cause an infinite loop).
            # Therefore they need to be buffered.
            self._waiting.append(hnd)
        return hnd

    @staticmethod
    def unregister(handle):
        """Removes a previously registered callback.

        Same as calling Handle.unregister() directly.
        """
        # To prevent interference with the loop inside trigger(), the
        # callback won't be removed immediately (but also won't be called
        # anymore). The actual removal is done at the end of every trigger()
        # call.
        # The len() function will report a size not including inactive handlers.
        handle.unregister()

    def clear(self):
        """Remove all event handlers."""
        for i in self._handlers:
            i.unregister()

    async def trigger(self, *args, **kwargs):
        """Calls every registered event handler with the given arguments.

        The loop will stop if EVENT_HANDLED is returned by a callback or an
        Exception is thrown. In case of an exception, it won't be handled.
        """
        self._running = True
        for i in self._handlers:
            if i and await i(*args, **kwargs) == EVENT_HANDLED:
                break
        self._running = False
        self._update()

    def trigger_all(self, *args, **kwargs):
        """The same as trigger() but calls every handler, regardless of return values."""
        self._running = True
        for i in self._handlers:
            if i:
                i(*args, **kwargs)
        self._running = False
        self._update()

    def _update(self):
        if not self._running:
            # Remove every handler that was marked for removal.
            if self._dirty > 0:
                self._handlers = SortedList(
                    [ i for i in self._handlers if i ], key=lambda x: x._nice)
                self._waiting = [ i for i in self._waiting if i ]
                self._dirty = 0

            # Insert pending callbacks
            if len(self._waiting) > 0:
                self._handlers.update(self._waiting)
                self._waiting = []

    def __len__(self):
        return len(self._handlers) + len(self._waiting) - self._dirty
