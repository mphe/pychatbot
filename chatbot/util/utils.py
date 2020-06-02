# -*- coding: utf-8 -*-

import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from chatbot import api
from typing import Callable


def merge_dicts(srcdict: dict, mergedict: dict, overwrite=False):
    """Recursively merges `mergedict` into `srcdict` and returns `srcdict`.

    Makes shallow copies of `dict` and `list` values.
    """
    for k, v in mergedict.items():
        srcvalue = srcdict.get(k, None)

        if isinstance(v, dict) and isinstance(srcvalue, dict):
            merge_dicts(srcvalue, v, overwrite)
            continue

        if overwrite or srcvalue is None:
            if isinstance(v, dict):
                v = dict(v)
            elif isinstance(v, list):
                v = list(v)
            srcdict[k] = v

    return srcdict


def merge_dicts_copy(srcdict, mergedict, overwrite=False):
    """Same as _merge_dicts but returns a shallow copy instead of merging directly into srcdict."""
    return merge_dicts(dict(srcdict), mergedict, overwrite)


def string_prepend(prefix: str, string: str):
    """Prepends each line in `string` with `prefix`."""
    sub = "\n" + prefix
    return prefix + string.replace("\n", sub)


async def edit_or_reply(msg: api.ChatMessage, text: str):
    if msg.is_editable:
        await msg.edit(text)
    else:
        await msg.reply(text)


async def wait_until_api_ready(api: api.APIBase):
    if not api.is_ready:
        logging.debug("Waiting for API to become ready...")
        await wait_until_true(lambda: api.is_ready)


async def run_in_thread(callback, *args):
    """Spawn a new thread, run a callback in it, and wait until it returns.

    Returns what the callback returns.
    """
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=1) as pool:
        return await loop.run_in_executor(pool, callback, *args)


async def wait_until_true(callback: Callable, *args, **kwargs):
    """Wait (in 1s intervals) until `callback` returns true.

    `callback` can be a normal function or a coroutine.
    """
    while True:
        if asyncio.iscoroutine(callback):
            if await callback(*args, **kwargs):
                break
        else:
            if callback(*args, **kwargs):
                break
        await asyncio.sleep(1)
