import logging
from dataclasses import dataclass
from typing import List, Optional
from . import parsetools
import math
import locale
from chatbot import util
from bs4 import BeautifulSoup

# Only includes sensible fractions, e.g. not 7/8, 3/8, 1/7, etc.
REVERSE_FRACTION_TRANSLATION = (
    ("½", 0.5),
    ("¼", 0.25),
    ("¾", 0.75),
    ("⅓", 0.3333333333333333),
    ("⅔", 0.6666666666666666),
)


def find_unicode_fraction(frac: float) -> str:
    for char, value in REVERSE_FRACTION_TRANSLATION:
        if math.isclose(frac, value):
            return char
    return ""


@dataclass
class Ingredient:
    name: str
    amount: float
    unit: str

    def __post_init__(self):
        # Passing an int might happen accidentally, so we silently fix it.
        self.amount = float(self.amount)

    def get_discrete_amount(self) -> Optional[int]:
        """Returns the discrete amount or None if not applicable.

        Some grocery apps support specifying an integer amount for a list item, e.g. 5 tomatoes.
        This is usually unapplicable if the amount in the recipe is a fractional number or a weight/volume unit,
        e.g. "200 g", "1.5 l", "3 ½ onions", "4 EL oil", "3 TL oil", or "3.5 tomatoes".
        """
        return parsetools.try_get_discrete_amount(self.amount, self.unit)

    def format_amount(self, locale_name: str = "") -> str:
        """Formats the amount in a nice human-readable way using rounding, number separation and unicode fractions."""

        if locale_name:
            old_locale = locale.getlocale(locale.LC_NUMERIC)

            try:
                locale.setlocale(locale.LC_NUMERIC, locale_name)
            except locale.Error:
                logging.error("Failed to set locale: %s", locale_name)

        try:
            if self.amount.is_integer() or self.unit.lower() in ("g", "ml"):
                return locale.format_string("%d", int(self.amount), True)

            int_amount = int(self.amount)
            unicode_frac = find_unicode_fraction(self.amount - int_amount)

            if unicode_frac:
                if int_amount == 0:
                    return unicode_frac

                int_format = locale.format_string("%d", int_amount, True)
                return f"{int_format} {unicode_frac}"

            return locale.format_string("%.2f", round(self.amount, 2), True).rstrip("0")

        finally:
            if locale_name:
                locale.setlocale(locale.LC_NUMERIC, old_locale)


@dataclass
class Recipe:
    title: str
    url: str
    num_servings: int
    ingredients: List[Ingredient]
    instructions: List[str]

    def set_num_servings(self, num_servings: int) -> None:
        if num_servings == self.num_servings:
            return

        factor = num_servings / self.num_servings

        for ingredient in self.ingredients:
            ingredient.amount *= factor

        self.num_servings = num_servings


class RecipeFetcher:
    def __init__(self, url: str):
        self._url: str = url

    async def fetch_recipe(self) -> Optional[Recipe]:
        raise NotImplementedError

    async def supports_url(self) -> bool:
        raise NotImplementedError

    def _url_match_domain(self, domain: str) -> bool:
        """Helper for supports_url(). Performs a case-insensitive check if the given domain is used in the URL.

        The given domain must not include a trailing '/'.
        Example:
            _url_match_domain("chefkoch.de")
        """
        return (domain.lower() + "/") in self._url.lower()

    async def _fetch_url_as_soup(self, url: str = "") -> BeautifulSoup:
        """Asynchronously fetches the URL content and returns a corresponding BeautifulSoup object.

        Uses the given URL if not empty, otherwise the constructor URL.
        """
        url = url if url else self._url
        content: str = await util.async_http_get_str(url)
        soup = BeautifulSoup(content, "html.parser")
        return soup
