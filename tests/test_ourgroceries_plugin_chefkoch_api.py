#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import context  # pylint: disable=unused-import
from our_groceries import chefkoch_api, datamodel
from our_groceries.datamodel import Ingredient
from ourgroceries_plugin_api_base import CommonTestCases


class ChefkochTest(CommonTestCases.APITestBase):
    def setUp(self):
        self.fetcher = chefkoch_api.ChefkochFetcher
        self.matching_urls = [
            "https://www.chefkoch.de/rezepte/1844061298739441/Mozzarella-Haehnchen-in-Basilikum-Sahnesauce.html",
            "https://www.chefkoch.de/rezepte/1844061298739441/Mozzarella-Haehnchen-in-Basilikum-Sahnesauce.html?portionen=4",
            "https://www.chefkoch.de/rezepte/4331861726562757/Cremesuppe-von-der-Schwarzwurzel-mit-Brezel-Speck-Croutons.html?portionen=8.01",
        ]
        self.non_matching_urls = []
        self.recipe_urls = [
            "https://www.chefkoch.de/rezepte/1844061298739441/Mozzarella-Haehnchen-in-Basilikum-Sahnesauce.html",
            "https://www.chefkoch.de/rezepte/1171381223217983/Schupfnudel-Bohnen-Pfanne.html?portionen=5",
        ]
        self.expected_recipes = [
            datamodel.Recipe(
                "Mozzarella-Hähnchen in Basilikum-Sahnesauce",
                "placeholder",
                4,
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
                    "Fleisch waschen und trocken tupfen. Mit Salz und Pfeffer würzen. Öl in einer Pfanne erhitzen. Filets darin von allen Seiten ca. 5 Min. kräftig anbraten.",
                    "Tomaten waschen und halbieren. Basilikumblätter abzupfen, waschen und fein hacken.",
                    "Sahne in einem Topf aufkochen lassen. Schmelzkäse hineinrühren und schmelzen lassen. Mit Salz und Pfeffer würzen. 2/3 vom Basilikum unterrühren.",
                    "Fleisch und Tomaten in eine gefettete Auflaufform geben. Sauce darüber gießen. Mozzarella in kleine Stückchen schneiden und auf dem Fleisch verteilen. Wer mag, kann noch geriebenen Parmesan und 1 EL Kräuterbutter in kleinen Flöckchen darauf verteilen.",
                    "Im vorgeheizten Ofen bei 200 °C Ober-/Unterhitze bzw. 175 °C Umluft ca. 30 Min. backen. Herausnehmen und mit restlichem Basilikum bestreuen.  Dazu schmecken Kroketten oder Reis.",
                ]
            ),
            datamodel.Recipe(
                "Schupfnudel-Bohnen-Pfanne",
                "URL",
                2,
                [
                    Ingredient("Schupfnudeln, aus dem Kühlregal", 500, "g"),
                    Ingredient("Kochschinken", 200, "g"),
                    Ingredient("Prinzessbohnen, TK", 250, "g"),
                    Ingredient("Fleischbrühe", 125, "ml"),
                    Ingredient("Crème fraîche, ca. 150 g", 1, "Becher"),
                    Ingredient("Schmelzkäse, z.B. Toast-Käse", 4, "Scheibe/n"),
                    Ingredient("Salz und Pfeffer", 0, "n. B."),
                    Ingredient("Olivenöl zum Braten", 0, ""),
                ],
                [
                    "Die Prinzessböhnchen ca. 5 Min. in kochendem Salzwasser blanchieren.",
                    "Den Kochschinken würfeln und mit etwas Olivenöl in der Pfanne braten. Die Schupfnudeln hinzugeben und 5 - 8 Min. mit dem Schinken braten, bis sie eine goldgelbe Farbe annehmen. Die Prinzessbohnen hinzugeben. Die Fleischbrühe dazu gießen und mit Crème fraîche nach Belieben andicken. Nach Geschmack würzen.",
                    "Als Abschluss die Schmelzkäsescheiben obendrauf legen. Warten, bis sie verlaufen, dann sofort servieren.",
                ]

            ),
        ]

    async def test_fetch_clean_url(self):
        url = "https://www.chefkoch.de/rezepte/1844061298739441/Mozzarella-Haehnchen-in-Basilikum-Sahnesauce.html?portionen=8"
        fetcher = chefkoch_api.ChefkochFetcher(url)
        recipe = await fetcher.fetch_recipe()
        self.assertEqual(recipe.num_servings, 4)  # Fetcher should ignore the URL parameter specifying 8 servings


if __name__ == "__main__":
    unittest.main()
