import chefkoch
from bs4 import BeautifulSoup, Tag
from typing import List, Optional
from . import parsetools, datamodel
from .datamodel import Ingredient


class ChefkochFetcher(datamodel.RecipeFetcher):
    async def supports_url(self) -> bool:
        return self._url_match_domain("chefkoch.de")

    async def fetch_recipe(self) -> Optional[datamodel.Recipe]:
        url = self._url.split("?", maxsplit=1)[0]  # Remove URL arguments, including amount of servings to get "clean" numbers.
        recipe = chefkoch.Recipe(url)
        num_servings = int(recipe._Recipe__info_dict["recipeYield"])  # pylint: disable=no-member

        return datamodel.Recipe(recipe.title, url, num_servings, parse_ingredients(recipe), make_instructions_uniform(recipe))


def make_instructions_uniform(recipe: chefkoch.Recipe) -> List[str]:
    if isinstance(recipe.instructions, str):
        return [ recipe.instructions ]
    if isinstance(recipe.instructions, list):
        return recipe.instructions
    return []


def parse_ingredients(recipe: chefkoch.Recipe) -> List[Ingredient]:
    entries = extract_ingredients_and_amounts(recipe)
    ingredients: List[Ingredient] = []

    for amount_unit, ingredient in zip(entries[::2], entries[1::2]):
        amount_float, unit = parsetools.parse_amount_and_unit(amount_unit, False)
        ingredients.append(Ingredient(ingredient, amount_float, unit))

    return ingredients


def extract_ingredients_and_amounts(recipe: chefkoch.Recipe) -> List[str]:
    soup: BeautifulSoup = recipe._Recipe__soup  # pylint: disable=no-member
    ingredients_table: Tag = soup.find(attrs={ "class": "ingredients" })
    entries: List[str] = []

    # Transform all HTML elements to text and strip excessive whitespace
    tag: Tag
    for tag in ingredients_table.find_all("td"):
        text: str = tag.get_text()
        text = text.strip()
        text = parsetools.reduce_excessive_whitespace(text)
        entries.append(text)

    return entries
