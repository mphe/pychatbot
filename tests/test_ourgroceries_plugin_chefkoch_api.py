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
            "https://www.chefkoch.de/rezepte/1844061298739441/Mozzarella-Haehnchen-in-Basilikum-Sahnesauce.html",  # Uses the new page style
            "https://www.chefkoch.de/rezepte/1171381223217983/Schupfnudel-Bohnen-Pfanne.html?portionen=5",  # URL parameter
            "https://www.chefkoch.de/rezepte/4356081737467911/Schneller-Maultaschenauflauf-mit-Schinken-Kaese-Sahnesauce.html",  # Uses the old page style
        ]
        self.expected_recipes = [
            datamodel.Recipe(
                "Mozzarella-Hähnchen in Basilikum-Sahnesauce",
                "",
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
                "https://www.chefkoch.de/rezepte/1171381223217983/Schupfnudel-Bohnen-Pfanne.html",  # Strip URL parameter
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
            datamodel.Recipe(
                "Schneller Maultaschenauflauf mit Schinken-Käse-Sahnesauce",
                "",
                4,
                [
                    Ingredient("BÜRGER Maultaschen traditionell schwäbisch", 2, "Pck."),
                    Ingredient("Schinkenwürfel", 200, "g"),
                    Ingredient("Emmentaler, geriebener", 200, "g"),
                    Ingredient("Ei(er)", 4, ""),
                    Ingredient("Sahne", 200, "ml"),
                    Ingredient("Salz und Pfeffer", 0, ""),
                    Ingredient("Petersilie, frische, gehackt", 0, ""),
                    Ingredient("Olivenöl", 0, "etwas"),
                    Ingredient("Fett für die Form", 0, ""),
                ],
                [
                    "1. Heize den Ofen auf 180 °C Ober-/Unterhitze vor und fette eine Auflaufform leicht ein. "
                    "Schichte die Maultaschen in die vorbereitete Auflaufform. Verteile die Schinkenwürfel gleichmäßig über den Maultaschen in der Auflaufform.\n"
                    "\n"
                    "2. In einer Schüssel die Eier, Sahne, Salz und Pfeffer verquirlen, bis alles gut verrührt ist. "
                    "Die Eier-Sahne-Mischung über die Maultaschen gießen. Anschließend den Auflauf großzügig mit Emmentaler bestreuen. "
                    "Für etwa 20 - 25 Minuten in den Backofen geben. Vor dem Servieren mit gehackter Petersilie bestreuen.",
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
