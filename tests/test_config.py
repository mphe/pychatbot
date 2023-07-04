#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from context import util


class Test(unittest.TestCase):
    def test_shallow_copy(self):
        array = [ 1, 2, 3 ]
        mergedict = { "a": array }

        out = util.merge_dicts({}, mergedict)

        # Ensure the array is not shared
        out["a"][0] = 42
        self.assertNotEqual(out["a"], mergedict["a"])

    def test_merge_dict_mutation(self):
        from copy import deepcopy
        d = { "a": 42 }
        merge = { "foo": "asdf" }
        backup = deepcopy(merge)

        util.merge_dicts(d, merge)
        self.assertEqual(merge, backup)

    def test_merge_empty(self):
        d = { "a": 42 }
        merged = util.merge_dicts({}, d)
        self.assertTrue(merged == d)

    def test_merge_dicts(self):
        d = {
            "a": 42,
            "sub": {
                "key": [1, 2, 3],
            }
        }
        merge = {
            "new key": "foo",
            "sub": {
                "new subkey": "foo",
            },
        }

        util.merge_dicts(d, merge)
        self._assert_dict_contains(d, merge)

    def test_merge_dicts_copy(self):
        merge_array = [ 1, 2, 3 ]
        array_original = [ 1, 2, 3 ]
        mergedict = { "a": merge_array }
        original = { "b": array_original }

        out = util.merge_dicts_copy(original, mergedict)

        self.assertEqual(out, {
            "a": merge_array,
            "b": array_original,
        })

        # Test shallow copy
        self.assertIsNot(out, original)
        self.assertIsNot(out["a"], merge_array)
        self.assertIsNot(out["b"], array_original)

    def test_merge_override(self):
        src = { "a": 42 }
        merge = { "a": 66 }
        result = util.merge_dicts_copy(src, merge, overwrite=True)
        self.assertEqual(result["a"], 66)

    def _assert_dict_contains(self, src: dict, other: dict):
        """Returns whether all items in other also exist in src and are equal."""
        for k, v in other.items():
            self.assertIn(k, src, "Key not in src")
            srcval = src[k]

            self.assertIs(type(v), type(srcval), "Different types for key")

            if isinstance(v, dict):
                self._assert_dict_contains(srcval, v)
            else:
                self.assertEqual(v, srcval, "Keys have different values")


if __name__ == "__main__":
    unittest.main()
