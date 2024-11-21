#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import context  # pylint: disable=unused-import
from our_groceries import chefkoch_api, datamodel
from our_groceries.datamodel import Ingredient


class ChefkochTest(unittest.IsolatedAsyncioTestCase):
    async def test_match_url(self):
        urls = [
            "https://www.chefkoch.de/rezepte/1844061298739441/Mozzarella-Haehnchen-in-Basilikum-Sahnesauce.html",
            "https://www.chefkoch.de/rezepte/1844061298739441/Mozzarella-Haehnchen-in-Basilikum-Sahnesauce.html?portionen=4",
            "https://www.chefkoch.de/rezepte/4331861726562757/Cremesuppe-von-der-Schwarzwurzel-mit-Brezel-Speck-Croutons.html?portionen=8.01",
        ]

        for url in urls:
            with self.subTest(url):
                fetcher = chefkoch_api.ChefkochFetcher(url)
                self.assertTrue(await fetcher.supports_url())

    async def test_not_match_url(self):
        urls = [
            "https://google.de",
            "https://www.gaumenfreundin.de/kartoffelsalat-mit-bruehe-schwaebisch/",
        ]

        for url in urls:
            with self.subTest(url):
                fetcher = chefkoch_api.ChefkochFetcher(url)
                self.assertFalse(await fetcher.supports_url())

    async def test_fetch_clean_url(self):
        url = "https://www.chefkoch.de/rezepte/1844061298739441/Mozzarella-Haehnchen-in-Basilikum-Sahnesauce.html?portionen=8"
        fetcher = chefkoch_api.ChefkochFetcher(url)
        recipe = await fetcher.fetch_recipe()

        self.assertEqual(recipe.num_servings, 4)  # Fetcher should ignore the URL parameter specifying 8 servings

    async def test_fetch_recipe(self):
        url = "https://www.chefkoch.de/rezepte/1844061298739441/Mozzarella-Haehnchen-in-Basilikum-Sahnesauce.html"

        expected = datamodel.Recipe(
            "Mozzarella-Hähnchen in Basilikum-Sahnesauce",
            url,
            4,  # 4 is the default
            [
                Ingredient("Hühnerbrustfilet(s)", 4, ""),
                Ingredient("Salz und Pfeffer", 0, ""),
                Ingredient("Öl", 1, "EL"),
                Ingredient("Cocktailtomaten", 250, "g"),
                Ingredient("Basilikum", 0.5, "Topf"),
                Ingredient("Sahne", 200, "g"),
                Ingredient("Sahneschmelzkäse", 100, "g"),
                Ingredient("Fett für die Form", 0, ""),
                Ingredient("Mozzarella", 125, "g"),
                Ingredient("Parmesan, optional", 0, "n. B."),
                Ingredient("Kräuterbutter, optional", 1, "EL"),
            ],
            [
                "Fleisch waschen und trocken tupfen. Mit Salz und Pfeffer würzen. Öl in einer Pfanne erhitzen. Filets darin von allen Seiten ca. 5 Min. kräftig anbraten. "
                "\n\nTomaten waschen und halbieren. Basilikumblätter abzupfen, waschen und fein hacken."
                "\n\nSahne in einem Topf aufkochen lassen. Schmelzkäse hineinrühren und schmelzen lassen. Mit Salz und Pfeffer würzen. 2/3 vom Basilikum unterrühren. "
                "\n\nFleisch und Tomaten in eine gefettete Auflaufform geben. Sauce darüber gießen. Mozzarella in kleine Stückchen schneiden und auf dem Fleisch verteilen. Wer mag, kann noch geriebenen Parmesan und 1 EL Kräuterbutter in kleinen Flöckchen darauf verteilen. "
                "\n\nIm vorgeheizten Ofen bei 200 °C Ober-/Unterhitze bzw. 175 °C Umluft ca. 30 Min. backen. Herausnehmen und mit restlichem Basilikum bestreuen. "
                "\n\nDazu schmecken Kroketten oder Reis.",
            ]
        )

        fetcher = chefkoch_api.ChefkochFetcher(url)
        recipe: datamodel.Recipe = await fetcher.fetch_recipe()

        self.assertEqual(expected, recipe)


if __name__ == "__main__":
    unittest.main()
