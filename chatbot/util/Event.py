# -*- coding: utf-8 -*-

# TODO: use weakrefs

# Return values for callbacks to determine if event execution should be
# continued or stopped.
EVENT_CONTINUE = 0  # continue
EVENT_HANDLED = 1   # stop


class Handle(object):
    def __init__(self, event, callback):
        self._event = event
        self._callback = callback
        self._remove = False

    def unregister(self):
        if not self._remove:
            self._remove = True
            self._event._dirty += 1

    def __call__(self, *args, **kwargs):
        if not self._remove:
            self._callback(*args, **kwargs)

    def __nonzero__(self):
        return not self._remove

    def __repr__(self):
        return "Handle({}, {})".format(repr(self._event),
                                       repr(self._callback))


class Event(object):
    """Contains a list of callbacks and calls them when the event is trigger()ed.
    
    It's safe to remove/unregister a callback during the trigger() loop
    (unregistering a callback inside the callback).

    Callbacks can return a value to determine whether the event execution
    should be continued or stopped. This might be useful when certain events
    should only be handled by specific event handlers. 
    Returning nothing or EVENT_CONTINUE will continue executing the remaining
    handlers. EVENT_HANDLED will stop the execution.

    To guarantee that every handler will be called, regardless of return
    values, use the trigger_all() function.
    """

    def __init__(self):
        self._handlers = []
        self._dirty = 0     # counts how many handlers need to be removed

    def add_handler(self, callback):
        """Adds a callback that will be called when the event is triggered.
        
        Returns a handle that can be used to unregister.

        The callback function can return EVENT_HANDLED to abort the event
        execution early.
        See also the class docstring.
        """
        self._handlers.append(Handle(self, callback))
        return self._handlers[-1]

    def del_handler(self, callback):
        """Removes a previously registered callback.
        
        The same behaviour can also be achieved by storing the handle
        returned from add_handler() and calling its unregister() method.
        Since there's no need to search for the entry, this method is
        faster than using del_handler().

        To prevent interference with the loop inside trigger() the callback
        won't be removed immediately (but also won't be called anymore).
        The actual removal is done at the end of every trigger() call or
        by running clean().
        The len() function will report a size not including inactive
        handlers.
        """
        next(i for i in self._handlers if i and i._callback == callback).unregister()

    def clear(self):
        """Remove all event handlers."""
        self._handlers = []
        self._dirty = 0

    def clean(self):
        """Remove every handler that was marked for removal.

        MUST NOT BE CALLED INSIDE trigger()
        See del_handler() for further information.
        """
        if self._dirty > 0:
            self._handlers = filter(lambda i: i, self._handlers)
            self._dirty = 0

    def trigger(self, *args, **kwargs):
        """Calls every registered event handler with the given arguments.
        
        The loop will stop if EVENT_HANDLED is returned by a callback or an
        Exception is thrown.
        """
        # Event handlers that have been registered during this loop must not
        # be called (e.g. reloading could cause an infinite loop).
        # Therefore we need to store the length of the handler list and
        # access the individual callbacks by index.
        for i in range(len(self._handlers)):
            if self._handlers[i]:
                if self._handlers[i](*args, **kwargs) == EVENT_HANDLED:
                    break
        self.clean()

    def trigger_all(self, *args, **kwargs):
        """The same as trigger() but calls every handler, regardless of return values."""
        for i in range(len(self._handlers)):
            if self._handlers[i]:
                self._handlers[i](*args, **kwargs)
        self.clean()

    def __len__(self):
        return len(self._handlers) - self._dirty
