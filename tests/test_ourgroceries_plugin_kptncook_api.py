#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import context  # pylint: disable=unused-import
from our_groceries import kptncook_api, datamodel
from our_groceries.datamodel import Ingredient
from ourgroceries_plugin_api_base import CommonTestCases


class Test(CommonTestCases.APITestBase):
    def setUp(self):
        self.fetcher = kptncook_api.Fetcher
        self.matching_urls = [
            "https://mobile.kptncook.com/recipe/pinterest/Kartoffel-Pilz-Eintopf/78245a13?lang=de"
            "https://mobile.kptncook.com/recipe/pinterest/Kartoffel-Pilz-Eintopf/78245a13?lang=en"
        ]
        self.non_matching_urls = []
        self.recipe_urls = [ "https://mobile.kptncook.com/recipe/pinterest/Kartoffel-Pilz-Eintopf/78245a13?lang=de", ]
        self.expected_recipes = [
            datamodel.Recipe(
                "Kartoffel-Pilz-Eintopf",
                "placeholder",
                2,
                [
                    Ingredient("Schalotte", 1, ""),
                    Ingredient("Thymian, frisch", 4, "Zweig(e)"),
                    Ingredient("Kartoffeln", 400, "g"),
                    Ingredient("braune Champignons", 400, "g"),
                    Ingredient("Schlagsahne", 100, "ml"),
                    Ingredient("Petersilie, frisch", 10, "g"),
                    Ingredient("Pfeffer", 0, ""),
                    Ingredient("Lorbeerblätter", 0, ""),
                    Ingredient("Butter", 0, ""),
                    Ingredient("Weizenmehl, Typ 405", 0, ""),
                    Ingredient("Gemüsebrühe", 0, ""),
                    Ingredient("Salz", 0, ""),
                    Ingredient("Knoblauch", 0, ""),
                ],
                []
            )
        ]


if __name__ == "__main__":
    unittest.main()
