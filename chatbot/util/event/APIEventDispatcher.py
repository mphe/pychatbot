# -*- coding: utf-8 -*-


from functools import partial
from ..event import *
from chatbot.compat import *


class APIEventDispatcher(object):
    """Provides a dispatch system to allow multiple handlers per API event."""

    def __init__(self, apiobj):
        self._events = {}
        self._api = apiobj

    def register(self, event, callback, nice=EVENT_NORMAL):
        """Register an event handler and return a Handle to it.

        See util.event.Event.register for further information.
        """
        if not event in self._events:
            self._setup_dispatch(event)
        return self._events[event].register(callback, nice)

    def unregister(self, handle):
        """Unregister an event handler using its handle.

        Same as handle.unregister().
        See util.event.Event.unregister for further information.
        """
        handle.unregister()

    def clear(self):
        for i in self._events:
            self._api.unregister_event_handler(i)
        self._events = {}


    # Utility functions
    def _setup_dispatch(self, event):
        self._api.register_event_handler(
            event, partial(self._dispatch_event, event))
        self._events[event] = Event()

    def _dispatch_event(self, event, *args, **kwargs):
        """Generic function to dispatch an event to all registered callbacks."""
        ev = self._events[event]
        if len(ev) > 0:
            ev.trigger(*args, **kwargs)
        else:
            # Unregister if there are no callbacks left, so that debug stub
            # messages on unhandled events still come through.
            # This needs to happen here because unregister() can be bypassed
            # by unregistering using the EventHandle returned by the
            # register function.
            # TODO: Consider generating stub messages on higher software
            #       layers (e.g. here) and not by the API.
            del self._events[event]
            self._api.unregister_event_handler(event)
            # Trigger without anything registered (as it should have been)
            self._api._trigger(event, *args, **kwargs)
