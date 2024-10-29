#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import context  # pylint: disable=unused-import
from our_groceries import chefkoch_api
from our_groceries.chefkoch_api import ExtendedIngredient


class ChefkochTest(unittest.TestCase):
    def test_fetch_url(self):
        base_url = "https://www.chefkoch.de/rezepte/1844061298739441/Mozzarella-Haehnchen-in-Basilikum-Sahnesauce.html"
        expected_num_servings = 1  # Recipe default is 4

        tests = {
            base_url,
            base_url + "?",
            base_url + "?&",
            base_url + "?portionen=4",  # Test replacement
            base_url + "?portionen=4&portionen=825",  # Test replacement
            base_url + "?somearg=asdf",  # Test append
            base_url + "?somearg=asdf&",  # Test append
        }

        for i in tests:
            r = chefkoch_api.ExtendedRecipe(i, expected_num_servings)
            self.assertEqual(r.num_servings, expected_num_servings, "url = " + r.url)

    def test_parse_discrete_amount(self):
        tests = {
            "1 EL":         (1, "1 EL"),
            "1 TL":         (1, "1 TL"),
            "100g":         (1, "100g"),
            "100 g":        (1, "100 g"),
            "100 kg":       (1, "100 kg"),
            "100 ml":       (1, "100 ml"),
            "100 l":        (1, "100 l"),
            "100 L":        (1, "100 L"),
            "5,05 l":       (1, "5,05 l"),
            "5,05asdf":     (1, "5,05asdf"),
            "5  ,5":        (1, "5  ,5"),
            "5  ,   5":     (1, "5  ,   5"),
            "5,   5":       (1, "5,   5"),
            "n. B.":        (1, "n. B."),
            "etwas":        (1, "etwas"),
            "":             (1, ""),
            "  ":           (1, "  "),
            "1 ½":          (1, "1 ½"),
            "1 ½ kleine":   (1, "1 ½ kleine"),
            "½":            (1, "½"),
            "½ kleine":     (1, "½ kleine"),
            "2 TL, gestr.": (1, "2 TL, gestr."),
            "3 kleine":     (3, "kleine"),
            "3":            (3, ""),
            "3 ":           (3, ""),
            "2 Prise(n)":   (2, "Prise(n)"),
            "4 Stiel/e":    (4, "Stiel/e"),
            "2, kleine":    (2, "kleine"),
            "2 , kleine":   (2, "kleine"),
            "2,kleine":     (2, "kleine"),
        }

        for input_str, expected in tests.items():
            result = chefkoch_api.ExtendedRecipe._parse_discrete_amount(input_str)
            self.assertTupleEqual(result, expected, f"for input '{input_str}'")

    def test_ingredients(self):
        url = "https://www.chefkoch.de/rezepte/1844061298739441/Mozzarella-Haehnchen-in-Basilikum-Sahnesauce.html"
        r = chefkoch_api.ExtendedRecipe(url, 4)

        self.assertEqual(r.title, "Mozzarella-Hähnchen in Basilikum-Sahnesauce")

        expected_ingredients = [
            ExtendedIngredient("Hühnerbrustfilet(s)", "", 4),
            ExtendedIngredient("Salz und Pfeffer", ""),
            ExtendedIngredient("Öl", "1 EL"),
            ExtendedIngredient("Cocktailtomaten", "250 g"),
            ExtendedIngredient("Basilikum", "½ Topf"),
            ExtendedIngredient("Sahne", "200 g"),
            ExtendedIngredient("Sahneschmelzkäse", "100 g"),
            ExtendedIngredient("Fett für die Form", ""),
            ExtendedIngredient("Mozzarella", "125 g"),
            ExtendedIngredient("Parmesan, optional", "n. B."),
            ExtendedIngredient("Kräuterbutter, optional", "1 EL"),
        ]

        self.assertListEqual(r.extended_ingredients, expected_ingredients)


if __name__ == "__main__":
    unittest.main()
