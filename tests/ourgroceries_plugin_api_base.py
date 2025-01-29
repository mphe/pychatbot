#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import context  # pylint: disable=unused-import
from our_groceries import datamodel
from typing import List, Callable
from dataclasses import asdict


DEFAULT_NON_MATCHING_URLS = [
    "https://google.de",
    "https://www.asdfasdf.de/asfdjaksfj?ab=1234&asf=342da",
]


# Wrapping APITestBase in another class implicitly skips test execution for the base class itself.
class CommonTestCases:
    class APITestBase(unittest.IsolatedAsyncioTestCase):
        def __init__(self, *args):
            super().__init__(*args)
            self.fetcher: Callable[[str], datamodel.RecipeFetcher]
            self.matching_urls: List[str] = []
            self.non_matching_urls: List[str] = []
            self.recipe_urls: List[str]
            self.expected_recipes: List[datamodel.Recipe]

        async def test_match_url(self):
            for url in self.matching_urls:
                with self.subTest(url):
                    fetcher = self.fetcher(url)
                    self.assertTrue(await fetcher.supports_url())

        async def test_not_match_url(self):
            for url in self.non_matching_urls + DEFAULT_NON_MATCHING_URLS:
                with self.subTest(url):
                    fetcher = self.fetcher(url)
                    self.assertFalse(await fetcher.supports_url())

        async def test_fetch_recipe(self):
            self.maxDiff = None
            for url, expected in zip(self.recipe_urls, self.expected_recipes):
                with self.subTest(url):
                    fetcher = self.fetcher(url)
                    recipe: datamodel.Recipe = await fetcher.fetch_recipe()

                    expected.url = url

                    # Use dict comparison because it better displays the differences
                    self.assertEqual(asdict(expected), asdict(recipe))
