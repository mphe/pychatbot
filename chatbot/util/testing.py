# -*- coding: utf-8 -*-

import asyncio
import logging
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
    logging.info("\n%s", colorize(s, COLOR_BOLD))


async def test_function(func, *argv, **kwargs):
    state = SUCCESS
    ret = ""

    try:
        if asyncio.iscoroutinefunction(func):
            ret = " -> " + repr(await func(*argv, **kwargs))
        else:
            ret = " -> " + repr(func(*argv, **kwargs))
    except NotImplementedError:
        state = NOTIMPL
    except Exception as e:
        state = ERROR
        logging.exception(e)

    result = colorize(state[1], COLOR_BOLD, state[2])
    s = "{}: {}\t{}".format(result, func.__name__, ret)
    logging.info(s)

    return state == SUCCESS


async def test_builtins(o):
    await test_function(o.__str__)
    await test_function(o.__repr__)


def test(name):
    def decorator(func):
        async def wrapper(*argv, **kwargs):
            print_header("Testing " + name)
            test_builtins(argv[0])
            await func(*argv, **kwargs)
        return wrapper
    return decorator


@test("Chat")
async def test_chat(chat, api=None):
    await test_function(chat.id)
    await test_function(chat.is_id_unique)
    await test_function(chat.send_message, "test message")
    await test_function(chat.send_action, "test action")
    await test_function(chat.type)
    await test_function(chat.size)

    if await test_function(chat.id) and api:
        if await test_function(api.find_chat, chat.id()):
            await test_chat(await api.find_chat(chat.id()))


@test("User")
async def test_user(user, api=None):
    await test_function(user.display_name)
    handle = await test_function(user.handle)
    chat = await test_function(user.get_chat)

    if handle and api:
        if await test_function(api.find_user, user.handle()):
            await test_user(await api.find_user(user.handle()))

    if chat:
        await test_chat(await user.get_chat(), api)


@test("Message")
async def test_message(msg, api=None):
    await test_function(msg.get_text)
    await test_function(msg.get_type)
    await test_function(msg.is_editable)
    await test_function(msg.edit, "test edit")
    await test_function(msg.reply, "test reply")
    author = await test_function(msg.get_author)
    chat = await test_function(msg.get_chat)

    if author:
        await test_user(msg.get_author(), api)
    if chat:
        await test_chat(msg.get_chat(), api)
