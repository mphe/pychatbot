# -*- coding: utf-8 -*-

from functools import partial
import Event

HOOK_PRE = 0
HOOK_NORMAL = 1
HOOK_POST = 2

class APIEventDispatcher(object):
    """Provides a dispatch system to allow multiple handlers per API event.
    
    It also provides 3 categories for each event: pre, normal, and post.
    Pre-handlers are called before normal handlers. Post-handlers are
    called after normal handlers.
    See also register().
    """

    def __init__(self, apiobj):
        self._events = {}
        self._api = apiobj

    def register(self, event, callback, htype=HOOK_NORMAL):
        """Register an event handler and returns an Event.Handle to it.

        The last parameter is optional and indicates whether to register as
        pre-, normal-, or post-hook (default is normal).
        Possible values are: HOOK_PRE, HOOK_NORMAL, HOOK_POST.
        Normal hooks are called after pre-hooks and before post-hooks.
        Inside each category the event handlers are executed in the order
        they have been registered in.
        """
        if not self._events.has_key(event):
            self._setup_dispatch(event)
        return self._events[event][htype].add_handler(callback)

    def unregister(self, event, callback, htype=HOOK_NORMAL):
        self._events[event][htype].del_handler(callback)

    def clear(self):
        for i in self._events.iterkeys():
            self._api.unregister_event_handler(i)
        self._events = {}


    # Utility functions
    def _setup_dispatch(self, event):
        self._api.register_event_handler(
            event, partial(self._dispatch_event, event))
        self._events[event] = [ Event.Event(), Event.Event(), Event.Event() ]

    def _dispatch_event(self, event, *args, **kwargs):
        """Generic function to dispatch an event to all registered callbacks."""
        empty = True
        for i in self._events[event]:
            if len(i) > 0:
                empty = False
                i.trigger(*args, **kwargs)

        # Unregister if there are no callbacks left, so that debug stub
        # messages on unhandled events still come through.
        # This needs to happen here because unregister() can be bypassed
        # by unregistering using the EventHandle returned by the
        # register function.
        # TODO: Consider generating stub messages on higher software layers
        #       (e.g. here) and not by the API.
        if empty:
            del self._events[event]
            self._api.unregister_event_handler(event)
            # Trigger without anything registered (as it should have been)
            self._api._trigger(event, *args, **kwargs)
