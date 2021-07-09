import importlib
import logging
from typing import Dict, Any
from .APIBase import APIBase
from .APIEvents import APIEvents
from .ChatMessage import ChatMessage, MessageType
from .User import User, GenericUser
from .Chat import GroupChat, Chat, ChatType
from .Request import Request, FriendRequest, GroupInvite


def create_api_object(apiname: str, options: Dict[str, Any] = None, stub=True) -> APIBase:
    """Loads the API module <apiname> and returns an API object.

    The stub parameter determines whether to print stub messages on
    unhandled events.

    API specific options can be defined by using kwargs.
    For example:
        test = api.create_api_object("test", { "message": "Custom message text" })

    Options supplied by kwargs are automatically merged into the API's
    default options (overwriting existing default entries).
    """
    api = get_api_class(apiname)

    # Merge arguments with default options
    opts = api.get_default_options()
    if options:
        for k, v in options.items():
            opts[k] = v

    return api(apiname, stub, opts)


def get_api_class(apiname):
    """Loads the API module <apiname> and returns the API class

    Note that this does not create an object but only returns the class.
    """
    return _import_api(apiname).API


def _import_api(apiname):
    if not apiname:
        raise ValueError("Empty API name")
    m = importlib.import_module("." + apiname, "chatbot.api")
    logging.debug("Loaded API module %s", str(m))
    return m
