# -*- coding: utf-8 -*-

import asyncio
import logging
from chatbot import api  # Needed for typehints. pylint: disable=unused-import
from typing import Iterable, Optional


class APIBase:
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

    @property
    def api_id(self) -> str:
        """Returns the API's unique module name.

        This can be used to check if a certain API is used.
        API implementations must not override this method!
        """
        return self._api_id

    @property
    def version(self) -> str:
        """Return API version as string."""
        raise NotImplementedError

    @property
    def api_name(self) -> str:
        """Returns the name of the API.

        Note: for a unique identifier use api_id() instead.
        """
        raise NotImplementedError

    async def run(self) -> None:
        """Run the main loop, including initialization and cleanup afterwards.

        Wrapper around `start()` and `cleanup()` that ensures cleanup
        afterwards if an exception occurs.
        """
        try:
            await self.start()
        except (KeyboardInterrupt, SystemExit) as e:
            logging.info(e)
            await self.close()
        finally:
            await self.cleanup()

    async def start(self) -> None:
        """Initialize and run the main loop."""
        raise NotImplementedError

    async def cleanup(self) -> None:
        """Cleanup and free resources."""
        raise NotImplementedError

    async def close(self) -> None:
        """Signal to stop the main loop."""
        raise NotImplementedError

    async def get_user(self) -> "api.User":
        """Returns a User object of the currently logged in user."""
        raise NotImplementedError

    async def set_display_name(self, name) -> None:
        """Set the logged in user's display name."""
        raise NotImplementedError

    async def create_group(self, users: Iterable["api.User"]) -> "api.Chat":
        """Create a new groupchat with the given `api.User`s.

        Returns a Chat object representing the group.
        """
        raise NotImplementedError

    async def find_user(self, userid: str) -> "api.User":
        """Returns a User object for the user with the given ID.

        As mentioned in api.User, the given ID should be a string.
        Therefore, if the underlying API uses a different type, you must
        manually convert it here.
        """
        raise NotImplementedError

    async def find_chat(self, chatid: str) -> "api.Chat":
        """Returns a Chat object for the chat with the given ID.

        As mentioned in api.Chat, the given ID should be a string.
        Therefore, if the underlying API uses a different type, you must
        manually convert it here.
        """
        raise NotImplementedError

    @staticmethod
    def get_default_options() -> dict:
        """Return a dictionary with options and their default values for this API."""
        return {}

    def register_event_handler(self, event, callback) -> None:
        """Set an event handler for the given event.

        `callback` must be a coroutine.

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
            assert asyncio.iscoroutinefunction(callback), "Callback must be a coroutine"
            self._events[event] = callback

    def unregister_event_handler(self, event) -> None:
        """Remove the event handler from the given event.

        See also register_event_handler().
        """
        self.register_event_handler(event, None)

    async def _trigger(self, event, *args, **kwargs) -> Optional[asyncio.Task]:
        """Triggers the given event with the given arguments.

        Runs the associated callback as a new asyncio task and returns the
        Task object. Returns None, if no callback registered.

        Should be used instead of accessing self._events directly.
        """
        ev = self._events.get(event, None)
        if ev is not None:
            return asyncio.create_task(ev(*args, **kwargs))
        if self._stub:
            logging.debug("Unhandled event: %s", str(event))
        return None

    def __str__(self):
        return "API: {}, version {}".format(self.api_name, self.version)
