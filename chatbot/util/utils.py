# -*- coding: utf-8 -*-


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


def edit_or_reply(msg, text):
    if msg.is_editable():
        msg.edit(text)
    else:
        msg.reply(text)
