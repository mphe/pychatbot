# -*- coding: utf-8 -*-

from typing import Dict
import asyncio
from functools import partial
from chatbot.util.event import Event


class APIEventDispatcher:
    """Provides a dispatch system to allow multiple handlers per API event."""

    def __init__(self, apiobj, exc_handler=None):
        """Constructor

        apiobj is an API objects instance.
        exc_handler is an optional callback with the signature
            (event, Exception, *args, **kwargs) -> bool
        that will be called when an exception occurs during event execution.
        The first argument is the event and second is the Exception object.
        Any arguments passed to the event appear as *args or **kwargs.
        The return value indicates whether to treat the exception as caught
        or re-raise it: True -> caught, False -> re-raise.
        If exception_handler is None, exceptions will be re-raised
        immediately.
        """
        self._events: Dict[str, Event] = {}
        self._api = apiobj
        self._exc_handler = exc_handler

    def register(self, event, callback, nice=0):
        """Register an event handler and return a Handle to it.

        See util.event.Event.register for further information.
        """
        ev = self._events.get(event, None)
        if ev is None:
            ev = self._setup_dispatch(event)
        return ev.register(callback, nice)

    @staticmethod
    def unregister(handle):
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
            event, asyncio.coroutine(partial(self._dispatch_event, event)))
        ev = self._events[event] = Event()
        return ev

    async def _dispatch_event(self, event, *args, **kwargs):
        """Generic function to dispatch an event to all registered callbacks."""
        ev = self._events.get(event, None)
        if ev is None:
            return

        if len(ev) > 0:
            try:
                await ev.trigger(*args, **kwargs)
            except Exception as e:
                if self._exc_handler:
                    if not self._exc_handler(event, e, *args, **kwargs):
                        raise
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
            await self._api._trigger(event, *args, **kwargs)
