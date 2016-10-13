# -*- coding: utf-8 -*-

from functools import partial
import Event


class APIEventDispatcher(object):
    """Provides a dispatch functionality to allow multiple handlers per API event."""

    def __init__(self, apiobj):
        self._events = {}
        self._api = apiobj

    def register_event_handler(self, event, callback):
        if not self._events.has_key(event):
            self._setup_dispatch(event, partial(self._dispatch_event, event))
        return self._events[event].add_handler(callback)

    def unregister_event_handler(self, event, callback):
        self._events[event].del_handler(callback)

    def clear(self):
        for i in self._events.iterkeys():
            self._api.unregister_event_handler(i)
        self._events = {}


    # Utility functions
    def _setup_dispatch(self, event, callback):
        self._api.register_event_handler(event, callback)
        self._events[event] = Event.Event()

    def _dispatch_event(self, event, *args, **kwargs):
        """Generic function to dispatch an event to all registered callbacks."""
        if len(self._events[event]) > 0:
            self._events[event].trigger(*args, **kwargs)
        else:
            # Unregister if no callbacks left, so that debug stub messages
            # on unhandled events still come through.
            # This needs to happen here because unregister_event_handler can be
            # bypassed by unregistering using the EventHandle returned by the
            # register function.
            del self._events[event]
            self._api.unregister_event_handler(event)
            # Trigger without anything registered (as it should have been)
            self._api._trigger(event, *args, **kwargs)

