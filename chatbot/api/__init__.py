from .APIBase import APIBase
from .APIEvents import APIEvents
from .ChatMessage import ChatMessage
from .FriendRequest import FriendRequest
from .Chat import *
import importlib
import logging


def create_api_object(apiname, **kwargs):
    """Loads the API module <apiname> and returns an API object.
    
    API specific options can be defined by using kwargs.
    For example:
    test = api.create_api_object("test", message="Custom message text")
    """
    m = importlib.import_module("." + apiname, "chatbot.api")
    logging.info("Loaded API " + str(m))
    return m.API(**kwargs)
