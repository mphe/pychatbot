# -*- coding: utf-8 -*-

from APIEvents import *
import logging
import time


class APIBase(object):
    """Base class for API objects.

    See also the \"test\" API for an example.

    When creating an API, the class should be derived from APIBase.
    The custom API class must have the name \"API\".
    For example:
    api
    |- skype
    |- tox
    |- irc
    |  |
    |  |- __init__.py
    |  |- ircapi.py

    ircapi.py contains the class IRCAPI that is derived from APIBase.
    To work properly, IRCAPI must be imported in __init__,py and renamed to
    \"API\", e.g. by using
        from ircapi import IRCAPI as API
    or by directly renaming IRCAPI to API.
    """

    def __init__(self, api_id, stub=True):
        """Must be called by API implementations.
        
        The arguments for this function are usually passed to the
        create_api_object() function and should _not_ be altered.
        The API should simply forward these values to this constructor.

        api_id contains a unique string to identify this API (usually the
        module name).
        stub determines whether to print stub messages on unhandled events.
        """
        self._events = {}
        self._api_id = api_id
        self._stub = stub

    def attach(self):
        raise NotImplementedError

    def detach(self):
        raise NotImplementedError

    def iterate(self):
        """The main loop.
        
        Will sleep for 1 second by default.
        It will be called like
        while True:
            apiobj.iterate()
        """
        time.sleep(1)

    def version(self):
        raise NotImplementedError

    def api_name(self):
        """Returns the name of the API.
        
        Note: for a unique identifier use api_id() instead."""
        raise NotImplementedError

    def api_id(self):
        """Returns the API's unique module name.
        
        This can be used to check if a certain API is used.
        API implementations must not override this method!
        """
        return self._api_id

    def get_user():
        """Returns a User object of the currently logged in user"""
        raise NotImplementedError

    @staticmethod
    def get_default_options():
        """Return a dictionary with options and their default values for this API."""
        return {}

    def register_event_handler(self, event, callback):
        """Add an event handler to the given event.
        
        Only one callback can be registered per event. If you need more, you
        have to write your own dispatch functionality.
        To unregister an event simply pass None as callback or use
        unregister_event_handler, which is a simple wrapper around this.
        
        A list of available events can be found in the APIEvents class.
        The actual API implementation might offer additional events.
        """
        if callback is None:
            del self._events[event]
        else:
            self._events[event] = callback

    def unregister_event_handler(self, event):
        """Remove the event handler from the given event.
        
        See also register_event_handler().
        """
        self.register_event_handler(event, None)

    def _trigger(self, event, *args, **kwargs):
        """Triggers the given event with the given arguments.
        
        Should be used instead of accessing self._events directly.
        """
        if self._events.has_key(event):
            self._events[event](*args, **kwargs)
        elif self._stub:
            logging.debug("Unhandled event: " + str(event))

    def __str__(self):
        return "API: {}, version {}".format(self.api_name(), self.version())
