#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import context  # pylint: disable=unused-import
from our_groceries import rewe_api, datamodel
from our_groceries.datamodel import Ingredient
from ourgroceries_plugin_api_base import CommonTestCases


class ReweTest(CommonTestCases.APITestBase):
    def setUp(self):
        self.fetcher = rewe_api.ReweFetcher
        self.matching_urls = [ "https://www.rewe.de/rezepte/maronen-pilz-ragout/", ]
        self.non_matching_urls = [
            "https://google.de",
            "https://rewe.de/rezepte/maronen-pilz-ragout/",
        ]
        self.recipe_urls = [ "https://www.rewe.de/rezepte/maronen-pilz-ragout/", ]
        self.expected_recipes = [
            datamodel.Recipe(
                "Maronen-Pilz-Ragout",
                "PLACEHOLDER",
                4,
                [
                    Ingredient("Maronen (gekocht)", 400, "g"),
                    Ingredient("Kräuterseitlinge", 200, "g"),
                    Ingredient("Champignons (braun)", 200, "g"),
                    Ingredient("Zwiebel", 1, ""),
                    Ingredient("Knoblauch", 1, "Zehe(n)"),
                    Ingredient("Butterschmalz", 2, "EL"),
                    Ingredient("Weißwein", 50, "ml"),
                    Ingredient("Portwein", 2, "EL"),
                    Ingredient("Gemüsebrühe", 150, "ml"),
                    Ingredient("Schlagsahne", 150, "g"),
                    Ingredient("Soßenbinder (hell)", 2, "EL"),
                    Ingredient("Salz", 0, ""),
                    Ingredient("Pfeffer", 0, ""),
                    Ingredient("Schnittlauch", 15, "g"),
                ],
                [
                    "Maronen halbieren. Pilze mit einer Pilzbürste säubern und in mundgerechte Stücke schneiden (die etwa die gleiche Größe wie die ganzen Maronen haben). Zwiebel und Knoblauch schälen und fein hacken.",
                    "Die Pilze in einer großen Pfanne portionsweise in Butterschmalz kräftig anbraten, herausnehmen und Beiseite stellen. In dem restlichen Fett Zwiebeln und Knoblauch andünsten, mit Weißwein und Portwein ablöschen und etwas einkochen lassen.",
                    "Maronen und Pilze mit in die Pfanne geben. Gemüsebrühe, Sahne und Soßenbinder einrühren, kurz aufkochen lassen und bei mittlerer Hitze etwa 10 Minuten schmoren lassen. Mit Salz und Pfeffer abschmecken.",
                    "Den Schnittlauch waschen und in feine Röllchen schneiden, dann die Pilzpfanne damit garnieren.",
                ]
            ),
        ]


if __name__ == "__main__":
    unittest.main()
