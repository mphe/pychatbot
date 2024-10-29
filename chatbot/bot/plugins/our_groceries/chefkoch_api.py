import re
from functools import cached_property
from chefkoch import Recipe
from bs4 import BeautifulSoup, Tag
from typing import List, Tuple
from dataclasses import dataclass


FRACTION_TRANSLATION = {
    "½": ",5",
    "⅓": ",33",
    "¼": ",25",
    "⅕": ",2",
    "⅙": ",16",
    "⅐": ",14",
    "⅛": ",125",
    "⅑": ",11",
    "⅒": ",1",
    "⅔": ",66",
    "⅖": ",4",
    "¾": ",75",
    "⅗": ",6",
    "⅜": ",375",
    "⅘": ",8",
    "⅚": ",83",
    "⅝": ",625",
    "⅞": ",875",
}


MATCH_UNIT_BLACKLIST = re.compile(r"\b(g|kg|ml|l|TL|EL)\b", re.IGNORECASE)
MATCH_SPLIT_DISCRETE_NUMBER_AND_UNIT = re.compile(r"\s*(\d+)(\s*[,\.]\s*\d+)?\s*,?\s*(.+)?\s*")
MATCH_EXCESSIVE_WHITESPACE = re.compile(r"\s+")

# NOTE: Currently unused but might come in handy in future
# MATCH_UNICODE_FRACTION = "|".join(f"{re.escape(i)}" for i in FRACTION_TRANSLATION)
# MATCH_UNICODE_FRACTION_AND_NUMBER = re.compile(rf"(\d+)\s+({MATCH_UNICODE_FRACTION})")
#
#
# def fraction_sub(text: str):
#     def callback(m: re.Match[str]) -> str:
#         return m.group(1) + FRACTION_TRANSLATION[m.group(2)]
#
#     return re.sub(MATCH_UNICODE_FRACTION_AND_NUMBER, callback, text)


@dataclass
class ExtendedIngredient:
    ingredient: str
    amount_and_unit: str
    discrete_amount: int = 1


class ExtendedRecipe(Recipe):
    def __init__(self, url: str, num_servings: int):
        url = self._prepare_url(url, num_servings)
        super().__init__(url)

    @property
    def num_servings(self) -> int:
        return int(self._Recipe__info_dict["recipeYield"])  # pylint: disable=no-member

    @cached_property
    def extended_ingredients(self) -> List[ExtendedIngredient]:
        entries = self._find_ingredients_and_amounts()

        ingredients: List[ExtendedIngredient] = []

        for amount_unit, ingredient in zip(entries[::2], entries[1::2]):
            discrete_amount, unit = self._parse_discrete_amount(amount_unit)
            ingredients.append(ExtendedIngredient(ingredient, unit, discrete_amount))

        return ingredients

    @staticmethod
    def _prepare_url(url: str, num_servings: int) -> str:
        while True:
            argidx = url.find("portionen=")

            if argidx < 0:
                break

            next_argidx = url.find("&", argidx)

            if next_argidx < 0:
                url = url[:argidx]
            else:
                url = url[:argidx] + url[next_argidx + 1]

        if "?" in url:
            if not url.endswith("&"):
                separator = "&"
            else:
                separator = ""
        else:
            separator = "?"

        return f"{url}{separator}portionen={num_servings}"

    def _find_ingredients_and_amounts(self) -> List[str]:
        soup: BeautifulSoup = self._Recipe__soup  # pylint: disable=no-member
        ingredients_table: Tag = soup.find(attrs={ "class": "ingredients" })
        entries: List[str] = []

        # Transform all HTML elements to text and strip excessive whitespace
        tag: Tag
        for tag in ingredients_table.find_all("td"):
            text: str = tag.get_text()
            text = text.strip()
            text = re.sub(MATCH_EXCESSIVE_WHITESPACE, " ", text)
            entries.append(text)

        return entries

    @staticmethod
    def _parse_discrete_amount(unit_amount_str: str) -> Tuple[int, str]:
        """Parses the amount + unit part of the ingredient string for a discrete amount.

        The given string should not contain the ingredient name, only the amount and unit.

        Some grocery apps support specifying an integer amount for a list item, e.g. 5 tomatoes.
        This is usually unapplicable if the amount in the recipe is a fractional number or a weight/volume unit,
        e.g. "200g", "1.5 l", "3 ½ onions", "4 EL oil", "3 TL oil", or "3.5 tomatoes".

        This function detects whether the given string contains a discrete amount specification and
        splits it accordingly.

        Returns the discrete amount as first tuple element if applicable, otherwise 1.
        Returns the remaining string as second tuple element if a discrete amount was found, otherwise
        the original string.

        Example:
            "3 small" -> (3, "small")
            "300g" -> (1, "300g")
            "4 ½" -> (1, "4 ½")
        """

        m = MATCH_SPLIT_DISCRETE_NUMBER_AND_UNIT.match(unit_amount_str)
        default = 1, unit_amount_str

        # If not matching pattern at all or matching a fractional number, it is not discrete.
        if not m or m.group(2):
            return default

        amount = m.group(1)
        unit = m.group(3) if m.group(3) is not None else ""

        if unit:
            # Ensure there are no unicode fractions that were treated as part of the unit
            if any((i in unit for i in FRACTION_TRANSLATION)):
                return default

            # Ensure the unit is not a weight or volume unit
            if MATCH_UNIT_BLACKLIST.match(unit):
                return default

        return int(amount), unit
