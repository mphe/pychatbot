# -*- coding: utf-8 -*-

from .Event import Event
from .APIEvents import *
import importlib
import logging
import time


def create_api_object(apiname):
    """Loads the API module <apiname> and returns an API object."""
    m = importlib.import_module("." + apiname, "chatbot.api")
    logging.info("Loaded API " + str(m))
    return m.API()


class APIBase(object):
    """Base class for API objects.

    See also the \"test\" API for an example.
    
    When creating an API, the class should be derived from APIBase.
    The custom API class must have the name \"API\"
    For example:
    api
    |- skype
    |- tox
    |- irc
    |  |
    |  |- __init__.py
    |  |- ircapi.py

    If ircapi.py contains the class IRCAPI, which is the, as the name says, the
    API to access IRC.
    IRCAPI should be derived from APIBase.
    To work properly, IRCAPI must be imported in __init__,py and renamed to
    \"API\", e.g. by using
        from ircapi import IRCAPI as API
    or by directly renaming IRCAPI to API.
    """

    def __init__(self):
        self._events = {}

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
        raise NotImplementedError

    def register_event_handler(self, event, callback):
        """Add an event handler to the given event.
        
        Available events can be found in the APIEvents class.
        The actual API implementation might offer additional events.
        """
        if not self._events.has_key(event):
            self._events[event] = Event()
        return self._events[event].add_handler(callback)
        logging.debug("Added event handler for {}-Event".format(event))

    def unregister_event_handler(self, event, callback):
        """Remove an event handler from the given event.
        
        See also register_event_handler().
        """
        self._events[event].del_handler(callback)
        logging.debug("Removed event handler for {}-Event".format(event))

    def _trigger(self, event, *args):
        """Triggers the given event with the given arguments.
        
        Should be used instead of accessing self._events directly.
        """
        if self._events.has_key(event) and len(self._events[event]) > 0:
            self._events[event].trigger(*args)
        else:
            logging.debug("Unhandled event: " + str(event))

    def __str__(self):
        return "API: {}, version {}".format(self.api_name(), self.version())
