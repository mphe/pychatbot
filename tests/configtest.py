#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from context import util
from pprint import pprint


def compare_dicts(srcdict: dict, mergedict: dict, sametypes=True):
    for k, v in mergedict.items():
        try:
            srcval = srcdict[k]
        except KeyError:
            logging.error("Key not in srcdict: %s", k)
            return False

        if isinstance(v, dict) and isinstance(srcval, dict):
            if not compare_dicts(srcval, v, sametypes):
                logging.error("Error in sub-dict: %s", k)
                return False
            continue

        if sametypes:
            if type(v) is not type(srcval):
                logging.error("Different types in key '%s': %s and %s", k, type(v), type(srcval))
                return False
            if v != srcval:
                logging.error("Different values in key '%s': %s and %s", k, v, srcval)
                return False
    return True


def test_merge_dicts():
    default_compare = {
        "foo": 5,
        "bar": "string",
        "list": [ 4, 5, 6 ],
        "foobar": {
            "subdictkey": 42,
            "subdictlist": [ 1, 2, 3 ],
        },
    }

    default = {
        "foo": 5,
        "bar": "string",
        "list": [ 4, 5, 6 ],
        "foobar": {
            "subdictkey": 42,
            "subdictlist": [ 1, 2, 3 ],
        },
    }
    print("default:")
    pprint(default)

    merged = util.merge_dicts({}, default)
    assert compare_dicts(merged, default)
    assert compare_dicts(default_compare, default)

    merged = {
        "bar": "string",
        "foobar": {
            "subdictlist": [ 1, 2, 3 ],
            "new subkey": "foo",
        },
        "new key": "foo",
    }
    print("merged:")
    pprint(merged)

    util.merge_dicts(merged, default)
    assert compare_dicts(default_compare, default)
    assert compare_dicts(merged, default)
    assert "new key" in merged
    assert "new subkey" in merged["foobar"]

    custom = {
        "bar": "custom text",
        "foobar": {
            "subdictlist": [ 7, 8, 9 ],
        },
    }
    print("custom:")
    pprint(custom)

    result = util.merge_dicts_copy(custom, default)
    assert compare_dicts(default_compare, default)
    assert compare_dicts(result, default, False)
    assert result["bar"] == "custom text"
    assert result["foobar"]["subdictlist"] == [ 7, 8, 9 ]

    result = util.merge_dicts_copy(custom, default, True)
    assert compare_dicts(default_compare, default)
    assert compare_dicts(result, default)


test_merge_dicts()
logging.info("Tests passed!")
