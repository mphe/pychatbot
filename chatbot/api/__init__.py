from APIBase import APIBase
from APIEvents import APIEvents
from ChatMessage import ChatMessage
from FriendRequest import FriendRequest
from User import User
from Chat import *
import importlib
import logging


def create_api_object(apiname, stub=True, **kwargs):
    """Loads the API module <apiname> and returns an API object.
    
    The stub parameter determines whether to print stub messages on
    unhandled events.

    API specific options can be defined by using kwargs.
    For example:
    test = api.create_api_object("test", message="Custom message text")
    """
    m = importlib.import_module("." + apiname, "chatbot.api")
    logging.info("Loaded API " + str(m))
    api = m.API(apiname, stub, **kwargs)
    return api
