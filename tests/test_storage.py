#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any
import os
from context import util
import unittest

TEST_STORAGE_FILE = "test_storage.json"
USER_ID = "userid"
CHAT_ID = "chatid"

VALUE_USER_CHAT = 100
VALUE_CHAT = 200
VALUE_USER = 300
VALUE_GLOBAL = 400


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.tearDown()  # Ensure there is no leftover config
        self.storage = util.Storage(util.config.Config(TEST_STORAGE_FILE))

    def tearDown(self):
        if os.path.isfile(TEST_STORAGE_FILE):
            os.remove(TEST_STORAGE_FILE)

    def _test_scope_set_get(self, scope: util.StorageScope, value: Any) -> None:
        scope.set("test", value)
        self.assertEqual(scope.get("test"), value, f"Should be {value}")

    def _test_fallback(self, user: str, chat: str, value: Any):
        retrieved = self.storage.scope(user, chat).get_with_fallback("test")
        self.assertEqual(value, retrieved, f"Should be {value} with user {user}, chat {chat}")

    # set/get
    def test_chat_user(self):
        scope = self.storage.scope(USER_ID, CHAT_ID)
        self._test_scope_set_get(scope, VALUE_USER_CHAT)

    def test_chat(self):
        scope = self.storage.scope(None, CHAT_ID)
        self._test_scope_set_get(scope, VALUE_CHAT)

    def test_user(self):
        scope = self.storage.scope(USER_ID, None)
        self._test_scope_set_get(scope, VALUE_USER)

    def test_global(self):
        scope = self.storage.scope(None, None)
        self._test_scope_set_get(scope, VALUE_GLOBAL)

    # set/get with fallbacks
    def test_fallback_global(self):
        self.storage.scope(None, None).set("test", VALUE_GLOBAL)
        self._test_fallback(USER_ID, CHAT_ID, VALUE_GLOBAL)
        self._test_fallback(USER_ID, None, VALUE_GLOBAL)
        self._test_fallback(None, CHAT_ID, VALUE_GLOBAL)
        self._test_fallback(None, None, VALUE_GLOBAL)

    def test_fallback_user(self):
        self.storage.scope(USER_ID, None).set("test", VALUE_USER)
        self._test_fallback(USER_ID, CHAT_ID, VALUE_USER)
        self._test_fallback(USER_ID, None, VALUE_USER)
        self._test_fallback(None, CHAT_ID, None)
        self._test_fallback(None, None, None)

    def test_fallback_chat(self):
        self.storage.scope(None, CHAT_ID).set("test", VALUE_CHAT)
        self._test_fallback(USER_ID, CHAT_ID, VALUE_CHAT)
        self._test_fallback(None, CHAT_ID, VALUE_CHAT)
        self._test_fallback(USER_ID, None, None)
        self._test_fallback(None, None, None)

    def test_fallback_user_chat(self):
        self.storage.scope(USER_ID, CHAT_ID).set("test", VALUE_USER_CHAT)
        self._test_fallback(USER_ID, CHAT_ID, VALUE_USER_CHAT)
        self._test_fallback(None, CHAT_ID, None)
        self._test_fallback(USER_ID, None, None)
        self._test_fallback(None, None, None)

    def test_erase(self):
        scope = self.storage.scope(USER_ID, CHAT_ID)
        scope.set("test", VALUE_USER_CHAT)
        scope.erase("test")
        self.assertIsNone(scope.get("test"))

    def test_erase_non_existing(self):
        # This should simply do nothing
        self.storage.erase("non_existing_key", USER_ID, CHAT_ID)

    def test_write(self):
        scope = self.storage.scope(USER_ID, CHAT_ID)
        scope.set("test", VALUE_USER_CHAT)
        self.storage.write()
        self.storage.load()
        self.assertEqual(scope.get("test"), VALUE_USER_CHAT)


if __name__ == '__main__':
    unittest.main()
