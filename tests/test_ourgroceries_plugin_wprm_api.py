#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import context  # pylint: disable=unused-import
from our_groceries import wprm_api, datamodel
from our_groceries.datamodel import Ingredient


class WPRMTest(unittest.IsolatedAsyncioTestCase):
    async def test_match_url(self):
        urls = [
            "https://www.gaumenfreundin.de/kartoffelsalat-mit-bruehe-schwaebisch/",
            "https://www.gaumenfreundin.de/wprm_print/29259",
            "https://veggie-einhorn.de/vegane-kaese-lauch-suppe-mit-kartoffeln/",
            "https://veggie-einhorn.de/wprm_print/vegane-kaese-lauch-suppe-mit-kartoffeln",
        ]

        for url in urls:
            with self.subTest(url):
                fetcher = wprm_api.WPRMFetcher(url)
                self.assertTrue(await fetcher.supports_url())

    async def test_not_match_url(self):
        urls = [
            "https://google.de",
            "https://www.chefkoch.de/rezepte/1844061298739441/Mozzarella-Haehnchen-in-Basilikum-Sahnesauce.html",
        ]

        for url in urls:
            with self.subTest(url):
                fetcher = wprm_api.WPRMFetcher(url)
                self.assertFalse(await fetcher.supports_url())

    async def test_fetch_recipe(self):
        urls = [
            "https://www.gaumenfreundin.de/kartoffelsalat-mit-bruehe-schwaebisch/",
            "https://www.gaumenfreundin.de/wprm_print/29259",
        ]

        expected = datamodel.Recipe(
            "Kartoffelsalat mit Brühe und Senf",
            "REPLACE WITH URL",
            4,  # 4 is the default
            [
                Ingredient("Kartoffeln", 1, "kg"),
                Ingredient("Zwiebeln", 2, ""),
                Ingredient("Fleischbrühe", 300, "ml"),
                Ingredient("Weißweinessig", 4, "EL"),
                Ingredient("Senf", 1, "EL"),
                Ingredient("Zucker", 1, "TL"),
                Ingredient("Rapsöl", 4, "EL"),
                Ingredient("Schnittlauch", 1, "Bund"),
            ],
            [
                "Kartoffeln mit der Schale in reichlich Salzwasser für ca. 20 Minuten gar kochen. Abgießen und ausdampfen lassen. Dann noch warm pellen und in dünne Scheiben schneiden.",
                "Zwiebeln fein würfeln. Dann etwas Öl in einem Topf erhitzen und die Zwiebeln andünsten. Fleischbrühe zugeben und aufkochen. Dann vom Herd nehmen und Essig, Senf, Salz, Pfeffer und Zucker einrühren.",
                "Die Kartoffeln mit der heißen Brühe mischen. Zugedeckt für mindestens 1 Stunde ziehen lassen, dann das Öl unterheben.",
                "Den Salat mit Salz und Pfeffer abschmecken und mit gehacktem Schnittlauch garnieren.",
            ]
        )

        for url in urls:
            with self.subTest(url):
                fetcher = wprm_api.WPRMFetcher(url)
                recipe: datamodel.Recipe = await fetcher.fetch_recipe()

                expected.url = url
                self.assertEqual(expected, recipe)


if __name__ == "__main__":
    unittest.main()
