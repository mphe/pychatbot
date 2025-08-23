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
            "https://www.malteskitchen.de/gnocchi-mit-crunchy-cashew-pesto/",
        ]
        self.non_matching_urls = [
            "https://google.de",
            "https://www.chefkoch.de/rezepte/1844061298739441/Mozzarella-Haehnchen-in-Basilikum-Sahnesauce.html",
        ]
        self.recipe_urls = [
            "https://www.gaumenfreundin.de/kartoffelsalat-mit-bruehe-schwaebisch/",
            "https://www.gaumenfreundin.de/wprm_print/29259",
            "https://emmikochteinfach.de/wprm_print/zucchini-pfanne-mit-hackfleisch",  # This one contains "1/2" as amount and ingredient notes
            "https://www.malteskitchen.de/gnocchi-mit-crunchy-cashew-pesto/",  # Has slightly different html structure and additional notes
            "https://veggie-einhorn.de/wprm_print/vegane-kaese-lauch-suppe-mit-hack",  # "1 bis 2" as amount, many weird notes
        ]

        recipe = datamodel.Recipe(
            "Kartoffelsalat mit Brühe, Omas bestes Rezept!",
            "",
            4,
            [
                Ingredient("Kartoffeln (festkochend)", 1, "kg"),
                Ingredient("Zwiebeln", 2, ""),
                Ingredient("Fleischbrühe", 300, "ml"),
                Ingredient("Weißweinessig", 4, "EL"),
                Ingredient("Senf", 1, "EL"),
                Ingredient("Zucker", 1, "TL"),
                Ingredient("Rapsöl (oder Sonnenblumenöl)", 4, "EL"),
                Ingredient("Schnittlauch", 1, "Bund"),
                Ingredient("Salz und Pfeffer", 0.0, ""),
            ],
            [
                "Kartoffeln mit der Schale in reichlich Salzwasser für 20 Minuten gar kochen. Dann abgießen und ausdampfen lassen. Kartoffeln noch warm pellen und in dünne Scheiben schneiden.",
                "Zwiebeln fein würfeln. Dann etwas Öl in einem Topf erhitzen und die Zwiebeln andünsten. Fleischbrühe zugeben und aufkochen. Den Topf vom Herd nehmen und Weißweinessig, Senf, Salz, Pfeffer und Zucker einrühren.",
                "Die Kartoffeln mit der heißen Brühe mischen. Den Salat zugedeckt für mindestens 1 Stunde ziehen lassen und zwischendurch ab und zu umrühren. Nach der Ziehzeit das Öl unterheben. Das macht den Kartoffelsalat schön schlonzig.",
                "Kartoffelsalat mit gehacktem Schnittlauch garnieren.",
            ]
        )

        self.expected_recipes = [
            recipe,
            recipe,
            datamodel.Recipe(
                "Zucchini Pfanne mit Hackfleisch",
                "",
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
                    Ingredient("Schwarzer Pfeffer", 0, ""),
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
                ],
                [
                    # Unsure how the special char got into the webpage text
                    "Hast Du das Rezept einmal ausprobiert? Wie findest Du es? Ich freue mich immer über Lob, freundliche Kritik oder Deine Tipps und Erfahrungen. Lass uns sehr gerne über die untenstehende Kommentarfunktion im Austausch bleiben.\xa0Das würde mich sehr freuen.",
                ]
            ),
            datamodel.Recipe(
                "Gebratene Gnocchi mit Cashew-Pesto | knusprig & lecker",
                "",
                4,
                [
                    Ingredient("Getrocknete Tomaten", 150, "g"),
                    Ingredient("Chiliflocken (oder frische Chili)", 0.5, "TL"),
                    Ingredient("Knoblauchzehe", 1, ""),
                    Ingredient("Parmesan", 60, "g"),
                    Ingredient("Cashewskerne", 80, "g"),
                    Ingredient("Gutes Olivenöl (nach gewünschter Konsistenz)", 150, "ml"),
                    Ingredient("Meersalz", 0, ""),
                    Ingredient("Gnocchi", 500, "g"),
                    Ingredient("Butter", 2, "EL"),
                    Ingredient("Basilikumblätter (gehackt)", 0, ""),
                ],
                [
                    "Die Zutaten für das Pesto in die Küchenmaschine geben und zu Pesto verarbeiten. Das fertige Pesto eventuell mit Salz abschmecken. Das hängt davon ab, wie salzig der Parmesan und die Nüsse sind.",
                    "Die Gnocchi in reichlich Wasser gar kochen, mit der Schaumkelle rausnehmen und kurz beiseite stellen. Eine Pfanne auf mittlerer Hitze aufsetzen, die Butter hineingeben und schmelzen lassen.",
                    "Die Gnocchi in die Pfanne geben und in der Butter braten, bis sie Farbe angenommen haben.",
                    "Alternativ die Gnocchi direkt aus der Packung in die Pfanne geben und in Butter richtig knusprig braten.",
                    "Vom Herd nehmen und 3-4 EL Pesto in die Pfanne geben und gut durchschwenken.",
                    "Mit dem gehackten Basilikum bestreuen und servieren.",
                ],
                [
                    "Vom Pesto wird wahrscheinlich noch etwas übrig bleiben. Es hält sich mit Öl bedeckt im Kühlschrank sicherlich 7 Tage.",
                ]
            ),
            datamodel.Recipe(
                "Vegane Käse-Lauch-Suppe mit Hack",
                "",
                4,
                [
                    Ingredient("Lauch (500 g bis 650 g)", 1, "1 bis 2 Stangen"),
                    Ingredient("Knoblauch", 2, "Zehen"),
                    Ingredient("Kartoffeln (Ungeschält gewogen. Festkochend oder vorwiegend festkochend.)", 400, "g"),
                    Ingredient("Vegane Butter", 60, "g"),
                    Ingredient("Veganes Hackfleisch (180 g bis 250 g)", 1, "Packung"),
                    Ingredient("Speisestärke (10 g)", 1, "EL"),
                    Ingredient("Vegane Kochsahne oder Cuisine (250 ml. Z.B. Soja Cuisine oder Hafer Cuisine.)", 250, "g"),
                    Ingredient("Veganer Frischkäse (natur oder veganer Kräuterfrischkäse)", 100, "g"),
                    Ingredient("Wasser (800 ml)", 800, "g"),
                    Ingredient("Gemüsebrühe Pulver (22,5 g)", 1.5, "EL"),
                    Ingredient("Mittelscharfer Senf (Mittelscharf. 15 g)", 1, "EL"),
                    Ingredient("Hefeflocken", 40, "g"),
                    Ingredient("Muskat (gemahlen)", 1, "kleine Prise"),
                    Ingredient("Salz und Pfeffer", 0, ""),
                ],
                [
                    "400 g Kartoffeln schälen. Du brauchst ca. 300 g bis 320 g geschälte Kartoffeln. Die Kartoffeln in kleine Würfelchen schneiden.",
                    "1 bis 2 Stangen Lauch längs halbieren.",
                    "Die Lauchhälften nochmal längs zwei oder dreimal einschneiden. Dann quer in feine Streifen schneiden. Du brauchst ca. 500 g bis 650 g Lauchstreifen.",
                    "Die Lauchstreifen in einen Durchschlag (Seiher) geben. Unter fließendem Wasser sehr gut waschen. Dann abtropfen lassen.",
                    "(Du kannst den Lauch auch erst waschen und dann klein schneiden.)",
                    "2 Knoblauchzehen schälen und durch eine Knoblauchpresse pressen.",
                    "60 g vegane Butter in einem Topf erhitzen.",
                    "180 g bis 250 g veganes Hack darin 4 bis 5 Minuten anbraten.",
                    "Zufügen: Die Lauchstreifen Den gepressten Knoblauch",
                    "4 Minuten mit anbraten.",
                    "1 EL Speisestärke ( 10 g) zufügen und alles gut verrühren.",
                    "Zufügen: 800 g Wasser (= 800 ml) 1,5 EL Gemüsebrühe Pulver ( 22,5 g) Die Kartoffelwürfelchen",
                    "Zum Kochen bringen. (Mit Deckel)",
                    "Dann 20 Minuten bei kleiner bis mittlerer Hitze köcheln lassen. (Mit Deckel) Ab und zu umrühren.",
                    "Zufügen: 250 g vegane Kochsahne (= 250 ml) 100 g veganer Frischkäse 40 g Hefeflocken 1 EL mittelscharfer Senf ( 15 g) 1 kleine Prise gemahlene Muskatnuss Schwarzer Pfeffer Bei Bedarf Salz",
                    "Sehr gut umrühren, damit sich der vegane Frischkäse gut auflöst.",
                    "Dazu passt Baguette.",
                ],
            ),
        ]


if __name__ == "__main__":
    unittest.main()
