# -*- coding: utf-8 -*-

import asyncio
import logging
import os

# Black        0;30     Dark Gray     1;30
# Red          0;31     Light Red     1;31
# Green        0;32     Light Green   1;32
# Brown/Orange 0;33     Yellow        1;33
# Blue         0;34     Light Blue    1;34
# Purple       0;35     Light Purple  1;35
# Cyan         0;36     Light Cyan    1;36
# Light Gray   0;37     White         1;37

COLOR_OK = "\033[32m"
COLOR_WARNING = "\033[33m"
COLOR_FAIL = "\033[31m"
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
    logging.info("%s", colorize(s, COLOR_BOLD))


async def test_function(func, *argv, **kwargs):
    state = SUCCESS

    try:
        if asyncio.iscoroutinefunction(func):
            ret = await func(*argv, **kwargs)
        else:
            ret = func(*argv, **kwargs)
    except NotImplementedError:
        state = NOTIMPL
    except Exception as e:
        state = ERROR
        logging.exception(e)

    logging.info("%s: %s -> %s",
                 colorize(state[1], COLOR_BOLD, state[2]),
                 func.__name__, repr(ret))

    return ret


async def test_builtins(o):
    await test_function(o.__str__)
    await test_function(o.__repr__)


def test(name):
    def decorator(func):
        async def wrapper(*argv, **kwargs):
            print_header("Testing " + name)
            await test_builtins(argv[0])
            await func(*argv, **kwargs)
            logging.info(colorize(COLOR_BOLD, "Testing ", name, " finished!"))
        return wrapper
    return decorator


@test("Chat")
async def test_chat(chat, api=None):
    await test_function(chat.id)
    await test_function(chat.is_id_unique)
    await test_function(chat.type)
    await test_function(chat.size)
    await test_function(chat.send_message, "test message")
    await test_function(chat.send_action, "test action")

    if await test_function(chat.id) and api:
        if await test_function(api.find_chat, chat.id()):
            await test_chat(await api.find_chat(chat.id()))


@test("User")
async def test_user(user, api=None):
    await test_function(user.display_name)
    userid = await test_function(user.id)
    chat = await test_function(user.get_chat)

    if userid and api:
        founduser = await test_function(api.find_user, userid)
        if founduser:
            await test_user(founduser)

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
