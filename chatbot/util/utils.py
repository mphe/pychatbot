# -*- coding: utf-8 -*-

import asyncio
from concurrent.futures import ThreadPoolExecutor
from chatbot import api


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


async def edit_or_reply(msg: api.ChatMessage, text: str):
    if msg.is_editable:
        await msg.edit(text)
    else:
        await msg.reply(text)


async def run_in_thread(callback, *args):
    """Spawn a new thread, run a callback in it, and wait until it returns.

    Returns what the callback returns.
    """
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=1) as pool:
        return await loop.run_in_executor(pool, callback, *args)
