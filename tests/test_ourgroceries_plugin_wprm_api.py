#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import context  # pylint: disable=unused-import
from our_groceries import wprm_api, datamodel
from our_groceries.datamodel import Ingredient
from ourgroceries_plugin_api_base import CommonTestCases


class WPRMTest(CommonTestCases.APITestBase):
    def setUp(self):
        self.fetcher = wprm_api.WPRMFetcher
        self.matching_urls = [
            "https://www.gaumenfreundin.de/kartoffelsalat-mit-bruehe-schwaebisch/",
            "https://www.gaumenfreundin.de/wprm_print/29259",
            "https://veggie-einhorn.de/vegane-kaese-lauch-suppe-mit-kartoffeln/",
            "https://veggie-einhorn.de/wprm_print/vegane-kaese-lauch-suppe-mit-kartoffeln",
        ]
        self.non_matching_urls = [
            "https://google.de",
            "https://www.chefkoch.de/rezepte/1844061298739441/Mozzarella-Haehnchen-in-Basilikum-Sahnesauce.html",
        ]
        self.recipe_urls = [
            "https://www.gaumenfreundin.de/kartoffelsalat-mit-bruehe-schwaebisch/",
            "https://www.gaumenfreundin.de/wprm_print/29259",
            "https://emmikochteinfach.de/wprm_print/zucchini-pfanne-mit-hackfleisch",  # This one contains "1/2" as amount and ingredient notes
        ]

        recipe = datamodel.Recipe(
            "Kartoffelsalat mit Brühe und Senf",
            "PLACEHOLDER",
            4,
            [
                Ingredient("Kartoffeln (festkochend)", 1, "kg"),
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

        self.expected_recipes = [
            recipe,
            recipe,
            datamodel.Recipe(
                "Zucchini Pfanne mit Hackfleisch",
                "PLACEHOLDER",
                4,
                [
                    Ingredient("Zucchini (mittelgroß)", 600, "g"),
                    Ingredient("Hackfleisch (halb und halb)", 600, "g"),
                    Ingredient("Kirschtomaten", 200, "g"),
                    Ingredient("Zwiebeln", 100, "g"),
                    Ingredient("Bacon in Scheiben", 100, "g"),
                    Ingredient("Erdnüsse (gesalzen)", 100, "g"),
                    Ingredient("Knoblauchzehe", 2, ""),
                    Ingredient("Speisestärke", 4, "EL"),
                    Ingredient("Tomatenmark", 2, "EL"),
                    Ingredient("Olivenöl", 5, "EL"),
                    Ingredient("Oregano, getrocknet", 2, "TL"),
                    Ingredient("Zucker", 0.5, "TL"),
                    Ingredient("schwarzer Pfeffer", 0, ""),
                    Ingredient("Salz", 0, ""),
                ],
                [
                    "HINWEIS: Glaube mir, dieser Arbeitsschritt lohnt sich, damit die Zucchini einen leichten Biss und Röstaromen bekommen und schön goldgelb aussehen: Die 600 g Zucchini wäschst Du und schneidest die Strünke ab. Dann in ca. 1 cm dicke Scheiben schneiden. Auf ein Schneidebrett legst Du Küchenpapier und streust gleichmäßig 2 EL Speisestärke mit Hilfe eines feinen Siebs darauf. Die Zucchini-Scheiben verteilst Du auf dem Küchenpapier, drückst sie mit den Händen leicht fest, damit sie auf der Unterseite etwas von der Speisestärke aufnehmen. Von oben bestreust Du sie mit ca. 1,5 TL Salz – das wird sie entwässern.",
                    "Die 100 g Zwiebel schälst Du und schneidest sie in feine Ringe, die 2 Knoblauchzehen schälst Du und schneidest sie in feine Würfel. Die 100 g Baconscheiben schneidest Du in ca. 5 mm feine Streifen. Die 200 g Kirschtomaten wäschst Du und halbierst sie.",
                    "Nun trocknest Du die Zucchini-Scheiben mit Küchenpapier ab, und streust 2 EL Speisestärke ebenfalls mit Hilfe des Siebs darüber. Mit den Handflächen gut festdrücken.",
                    "In einer großen, beschichteten Pfanne erhitzt Du 2 EL Olivenöl und lässt darin die Zucchini-Scheiben in zwei Chargen von beiden Seiten goldgelb braten, sie sollten idealerweise nicht übereinander liegen damit sie schön goldgelb werden. Aus der Pfanne nehmen und beiseite stellen. TIPP: Schneller geht es, wenn Du zwei Pfannen für diesen Schritt im Einsatz hast.",
                    "Dann erhitzt Du nochmals 3 EL Olivenöl in einer großen (derselben) Pfanne und lässt darin die geschnittene Zwiebel, den Bacon und 600 g Hackfleisch für ca. 3 Minuten auf hoher Temperatur anbraten. Mit je einer Prise Salz und schwarzem Pfeffer würzen. Dabei zerkleinerst Du das Hackfleisch grob mit zwei Kochlöffeln.",
                    "Im Anschluss gibst Du die Knoblauchwürfel, 2 EL Tomatenmark und die Kirschtomaten dazu und lässt alles für weitere 5 Minuten weiter braten. Dabei mit 1/2 TL Zucker würzen.",
                    "Zum Schluss hebst Du die Zucchini-Scheiben, 100 g gesalzene Erdnüsse und 2 TL Oregano unter und lässt es kurz heiß werden.",
                    "Die bunte Zucchini Pfanne mit Hackfleisch kann direkt serviert werden. Gekochter Reis, Nudeln oder Baguette passt prima dazu.",
                    "Ich wünsche Dir mit meinem Zucchini Pfanne Rezept viele Freude und einen guten Appetit.",
                ]
            )
        ]


if __name__ == "__main__":
    unittest.main()
