# -*- coding: utf-8 -*-

from chatbot.compat import *
from . import ChatType
import traceback
import os

COLOR_OK = "\033[92m"
COLOR_WARNING = "\033[93m"
COLOR_FAIL = "\033[91m"
COLOR_ENDC = "\033[0m"
COLOR_BOLD = "\033[1m"

SUCCESS = (0, "Success", COLOR_OK)
NOTIMPL = (1, "Not implemented", COLOR_WARNING)
ERROR = (2, "Error", COLOR_FAIL)

def colorize(s, *argv):
    if os.name == "posix":
        return "{}{}{}".format("".join(argv), s, COLOR_ENDC)
    return s

def print_header(s):
    print("\n" + colorize(s, COLOR_BOLD))

def test_function(func, *argv, **kwargs):
    state = SUCCESS
    ret = ""

    try:
        ret = " -> " + repr(func(*argv, **kwargs))
    except NotImplementedError:
        state = NOTIMPL
    except:
        state = ERROR
        print(traceback.format_exc())

    result = colorize(state[1], COLOR_BOLD, state[2])
    s = "{}: {}\t{}".format(result, func.__name__, ret)
    print(s)

    return state == SUCCESS

def test_builtins(o):
    test_function(o.__str__)
    test_function(o.__repr__)

def Test(name):
    def decorator(func):
        def wrapper(*argv, **kwargs):
            print_header("Testing " + name)
            test_builtins(argv[0])
            func(*argv, **kwargs)
        return wrapper
    return decorator


@Test("Chat")
def test_chat(chat, api=None):
    test_function(chat.id)
    test_function(chat.is_id_unique)
    test_function(chat.send_message, "test message")
    test_function(chat.send_action, "test action")
    test_function(chat.type)
    test_function(chat.size)

    if test_function(chat.id) and api:
        if test_function(api.find_chat, chat.id()):
            test_chat(api.find_chat(chat.id()))

@Test("User")
def test_user(user, api=None):
    test_function(user.display_name)
    handle = test_function(user.handle)
    chat = test_function(user.get_chat)

    if handle and api:
        if test_function(api.find_user, user.handle()):
            test_user(api.find_user(user.handle()))

    if chat:
        test_chat(user.get_chat(), api)

@Test("Message")
def test_message(msg, api=None):
    test_function(msg.get_text)
    test_function(msg.get_type)
    test_function(msg.is_editable)
    test_function(msg.edit, "test edit")
    test_function(msg.reply, "test reply")
    author = test_function(msg.get_author)
    chat = test_function(msg.get_chat)

    if author:
        test_user(msg.get_author(), api)
    if chat:
        test_chat(msg.get_chat(), api)


