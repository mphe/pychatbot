# -*- coding: utf-8 -*-

import asyncio
from concurrent.futures import ThreadPoolExecutor
from chatbot import api


def merge_dicts(srcdict, mergedict, overwrite=False):
    """Merges mergedict into srcdict and returns srcdict."""
    if overwrite:
        for k, v in mergedict.items():
            srcdict[k] = v
    else:
        diff = set(mergedict) - set(srcdict)
        for i in diff:
            srcdict[i] = mergedict[i]
    return srcdict


def merge_dicts_copy(srcdict, mergedict, overwrite=False):
    """Same as _merge_dicts but returns a shallow copy instead of merging directly into srcdict."""
    ndict = dict(srcdict)
    merge_dicts(ndict, mergedict, overwrite)
    return ndict


async def edit_or_reply(msg: api.ChatMessage, text: str):
    if msg.is_editable():
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
