#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import context  # pylint: disable=unused-import
from our_groceries import datamodel, parsetools, ingredient_to_og_item, generate_og_notes
from our_groceries.datamodel import Ingredient


class OurGroceriesTest(unittest.TestCase):
    def test_split_amount_and_unit_general(self):
        tests = (
            ("n. B.",          ("", "n. B.")),
            ("etwas",          ("", "etwas")),
            ("",               ("", "")),
            ("  ",             ("", "")),
            ("1 ½",            ("1 ½", "")),
            ("1½",             ("1½", "")),
            ("1 ½ kleine",     ("1 ½", "kleine")),
            ("½",              ("½", "")),
            ("½ kleine",       ("½", "kleine")),
            ("2 TL, gestr.",   ("2", "TL, gestr.")),
            ("3 kleine",       ("3", "kleine")),
            ("3",              ("3", "")),
            ("3 ",             ("3", "")),
            (" 3 ",            ("3", "")),
            ("2 Prise(n)",     ("2", "Prise(n)")),
            ("4 Stiel/e",      ("4", "Stiel/e")),
            ("2 Pkt.",         ("2", "Pkt.")),
            ("5  ,5",          ("5", ",5")),
            ("5  ,   5",       ("5", ",   5")),
            ("5,   5",         ("5", ",   5")),
            ("5  .5",          ("5", ".5")),
            ("5  .   5",       ("5", ".   5")),
            ("5.   5",         ("5", ".   5")),
        )

        for input_str, expected in tests:
            with self.subTest(input_str):
                result = parsetools._split_amount_and_unit(input_str, use_us_float_format=True)
                self.assertTupleEqual(result, expected)

                result = parsetools._split_amount_and_unit(input_str, use_us_float_format=False)
                self.assertTupleEqual(result, expected)

    def test_split_amount_and_unit_country_formats(self):
        # (input, expected de, expected us)
        tests = (
            ("5,05 l",           ("5,05", "l"),              ("5", ",05 l")),
            ("5,05asdf",         ("5,05", "asdf"),           ("5", ",05asdf")),
            ("5.05 l",           ("5", ".05 l"),             ("5.05", "l")),
            ("5.05asdf",         ("5", ".05asdf"),           ("5.05", "asdf")),
            (".05 something",    ("", ".05 something"),      (".05", "something")),
            (",05 something",    (",05", "something"),       ("", ",05 something")),
            ("5. something",     ("5", ". something"),       ("5", ". something")),
            ("1.000,05 kg",      ("1.000,05", "kg"),         ("1.000", ",05 kg")),
            ("1.000.000 kg",     ("1.000.000", "kg"),        ("1.000", ".000 kg")),
            ("1.000.000,5 kg",   ("1.000.000,5", "kg"),      ("1.000", ".000,5 kg")),
            ("1,000,000 kg",     ("1,000", ",000 kg"),       ("1,000,000", "kg")),
            ("1,000.05 kg",      ("1,000", ".05 kg"),        ("1,000.05", "kg")),
            ("2,5 TL, gestr.",   ("2,5", "TL, gestr."),      ("2", ",5 TL, gestr.")),
            ("2.5 TL, gestr.",   ("2", ".5 TL, gestr."),     ("2.5", "TL, gestr.")),
            ("1.000.000 ½ kg",   ("1.000.000 ½", "kg"),      ("1.000", ".000 ½ kg")),
            ("1.000.000,5 ½ kg", ("1.000.000,5", "½ kg"),    ("1.000", ".000,5 ½ kg")),
            ("1,000,000 ½ kg",   ("1,000", ",000 ½ kg"),     ("1,000,000 ½", "kg")),
            ("1,000,000.5 ½ kg", ("1,000", ",000.5 ½ kg"),   ("1,000,000.5", "½ kg")),
        )

        for input_str, expected_de, expected_us in tests:
            with self.subTest(input=input_str, format="non-US format"):
                result = parsetools._split_amount_and_unit(input_str, use_us_float_format=False)
                self.assertTupleEqual(result, expected_de)

            with self.subTest(input=input_str, format="US format"):
                result = parsetools._split_amount_and_unit(input_str, use_us_float_format=True)
                self.assertTupleEqual(result, expected_us)

    def test_normalize_str_to_float(self):
        # (non-us input, expected)
        tests = (
            ("5",           5),
            ("5,05",        5.05),
            (",05",         .05),
            ("5,",          5.0),

            ("5½",          5.5),
            ("5 ½",          5.5),
            ("½",          0.5),

            ("5 1/2",       5.5),
            ("1 1 / 2", 1.5),
            ("1 3/ 4",  1.75),
            ("1/4",     0.25),
            ("  1/4  ", 0.25),

            ("1.000,05",    1000.05),
            ("1.000.000",   1000000.0),
            ("1.000.000,5", 1000000.5),
            ("1.000.000 ½", 1000000.5),
            ("1.000.000 1/2", 1000000.5),
        )

        for input_str, expected in tests:
            with self.subTest(input=input_str):
                us_input_str = parsetools.non_us_to_us_number(input_str)
                self.assertEqual(parsetools.normalize_str_to_float(input_str, False), expected, "(non-US format)")
                self.assertEqual(parsetools.normalize_str_to_float(us_input_str, True), expected, "(US format)")

        # Test all available unicode fraction chars
        for input_str, expected in parsetools.FRACTION_TRANSLATION.items():
            with self.subTest(input=input_str, expected=expected):
                result = parsetools.normalize_str_to_float(input_str, True)
                self.assertAlmostEqual(result, expected)

    def test_reduce_excessive_whitespace(self):
        output = parsetools.reduce_excessive_whitespace("   a  .    b , c \t   de\t ?  ")
        self.assertEqual(output, "a. b, c de?")

    def test_non_us_to_us_number(self):
        self.assertEqual(parsetools.non_us_to_us_number("1.000.000,5"), "1,000,000.5")

    def test_amount_is_float(self):
        self.assertTrue(isinstance(datamodel.Ingredient("", 1, "g").amount, float))
        self.assertTrue(isinstance(datamodel.Ingredient("", 100, "g").amount, float))
        self.assertTrue(isinstance(datamodel.Ingredient("", 1.1, "g").amount, float))
        self.assertTrue(isinstance(datamodel.Ingredient("", 1.0, "g").amount, float))

    def test_pretty_amount(self):
        self.assertEqual("1", datamodel.Ingredient("", 1, "g").format_amount())
        self.assertEqual("1", datamodel.Ingredient("", 1.0, "g").format_amount())
        self.assertEqual("1", datamodel.Ingredient("", 1.5, "g").format_amount())
        self.assertEqual("1", datamodel.Ingredient("", 1.5, "ml").format_amount())
        self.assertEqual("1 ½", datamodel.Ingredient("", 1.5, "kg").format_amount())
        self.assertEqual("1 ½", datamodel.Ingredient("", 1.5, "something").format_amount())
        self.assertEqual("1 ⅓", datamodel.Ingredient("", 1.3333333333333, "kg").format_amount())
        self.assertEqual("1 ⅔", datamodel.Ingredient("", 1.6666666666666, "kg").format_amount())
        self.assertEqual("1000 ½", datamodel.Ingredient("", 1000.5, "kg").format_amount())

        # NOTE: Following tests require the en_US.utf8 locale to be installed on the system.
        self.assertEqual("1.2", datamodel.Ingredient("", 1.2, "kg").format_amount("en_US.utf8"))
        self.assertEqual("1,000.2", datamodel.Ingredient("", 1000.2, "kg").format_amount("en_US.utf8"))
        self.assertEqual("1,000", datamodel.Ingredient("", 1000.0, "kg").format_amount("en_US.utf8"))

        # NOTE: Following tests require the de_DE.utf8 locale to be installed on the system.
        self.assertEqual("1,2", datamodel.Ingredient("", 1.2, "kg").format_amount("de_DE.utf8"))
        self.assertEqual("1.000,2", datamodel.Ingredient("", 1000.2, "kg").format_amount("de_DE.utf8"))
        self.assertEqual("1.000", datamodel.Ingredient("", 1000.0, "kg").format_amount("de_DE.utf8"))

        for char, value in datamodel.REVERSE_FRACTION_TRANSLATION:
            self.assertEqual(char, datamodel.Ingredient("", value, "kg").format_amount())

    def test_servings(self):
        recipe = datamodel.Recipe(
            "Kartoffelsalat mit Brühe und Senf",
            "url placeholder",
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

        recipe.set_num_servings(8)

        self.assertEqual(recipe.num_servings, 8)
        self.assertEqual(recipe.ingredients, [
            Ingredient("Kartoffeln", 2, "kg"),
            Ingredient("Zwiebeln", 4, ""),
            Ingredient("Fleischbrühe", 600, "ml"),
            Ingredient("Weißweinessig", 8, "EL"),
            Ingredient("Senf", 2, "EL"),
            Ingredient("Zucker", 2, "TL"),
            Ingredient("Rapsöl", 8, "EL"),
            Ingredient("Schnittlauch", 2, "Bund"),
        ])

    def test_ingredient_discrete_amount(self):
        ingredient = Ingredient("tomatoes", 1, "")
        self.assertEqual(ingredient.get_discrete_amount(), 1)

        ingredient = Ingredient("tomatoes", 1, "small")
        self.assertEqual(ingredient.get_discrete_amount(), 1)

        ingredient = Ingredient("tomatoes", 2.0, "")
        self.assertEqual(ingredient.get_discrete_amount(), 2)

        ingredient = Ingredient("tomatoes", 2.5, "")
        self.assertIsNone(ingredient.get_discrete_amount())

        ingredient = Ingredient("salt", 0, "n. B.")
        self.assertEqual(ingredient.get_discrete_amount(), 0)

        for unit in parsetools.NON_DISCRETE_UNITS:
            self.assertIsNone(Ingredient("name", 1, unit).get_discrete_amount())

    def test_ingredient_to_og_item(self):
        # NOTE: test_pretty_amount() covers more cases.
        tests = [
            (Ingredient("Tomatoes", 1, ""), ("Tomatoes", "", "")),
            (Ingredient("Tomatoes", 3, ""), ("Tomatoes (3)", "", "")),
            (Ingredient("Tomatoes", 3, "small"), ("Small Tomatoes (3)", "", "")),
            (Ingredient("Salt", 0, "some"), ("Some Salt", "", "")),
            (Ingredient("Salt", 0, ""), ("Salt", "", "")),
            (Ingredient("Butter", 500, "g"), ("Butter", "", "500 g")),
            (Ingredient("Butter", 500.234, "g"), ("Butter", "", "500 g")),
            (Ingredient("Butter", 500.234, "kg"), ("Butter", "", "500.23 kg")),
            (Ingredient("Onions", 3.5, ""), ("Onions", "", "3 ½")),
        ]

        for ingr, expected in tests:
            self.assertEqual(ingredient_to_og_item(ingr), expected)

    def test_generate_og_notes(self):
        ingredients = [
            Ingredient("Ingredient A", 1, "kg"),
            Ingredient("Ingredient B", 300, "ml"),
            Ingredient("Salt", 0, ""),
        ]

        instructions = [
            "instruction1",
            "instruction2",
            "instruction3",
        ]

        notes = [
            "note1",
            "note2",
        ]

        recipes = [
            datamodel.Recipe("Recipe Title", "url", 4, ingredients, instructions, notes),
            datamodel.Recipe("Recipe Title", "url", 4, ingredients, [], notes),
            datamodel.Recipe("Recipe Title", "url", 4, ingredients, instructions),
        ]
        expected = [
            "url\n\nServes 4.\n\nInstructions:\n\n1) instruction1\n2) instruction2\n3) instruction3\n\nNotes:\n\n- note1\n- note2",
            "url\n\nServes 4.\n\nNotes:\n\n- note1\n- note2",
            "url\n\nServes 4.\n\nInstructions:\n\n1) instruction1\n2) instruction2\n3) instruction3",
        ]

        for recipe, exp in zip(recipes, expected):
            self.assertEqual(generate_og_notes(recipe, "Serves {}.", "Instructions", "Notes"), exp)


if __name__ == "__main__":
    unittest.main()
