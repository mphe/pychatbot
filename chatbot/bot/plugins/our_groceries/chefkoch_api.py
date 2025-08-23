from bs4 import BeautifulSoup, Tag
from typing import List, Optional, Dict, Any
from . import parsetools, datamodel, chefkoch
from .datamodel import Ingredient


class ChefkochFetcher(datamodel.RecipeFetcher):
    async def supports_url(self) -> bool:
        return self._url_match_domain("chefkoch.de")

    async def fetch_recipe(self) -> Optional[datamodel.Recipe]:
        url = self._url.split("?", maxsplit=1)[0]  # Remove URL arguments, including amount of servings to get "clean" numbers.
        soup = await self._fetch_url_as_soup(url)
        recipe = chefkoch.Recipe(url, bs=soup)
        num_servings = int(recipe.info_dict["recipeYield"])
        # import json
        # print(json.dumps(recipe.info_dict, indent=4))

        return datamodel.Recipe(recipe.title, url, num_servings, parse_ingredients(soup), parse_instructions(recipe))


def parse_instructions(recipe: chefkoch.Recipe) -> List[str]:
    instructions = []

    if isinstance(recipe.instructions, str):
        return [ recipe.instructions ]

    section: Dict[str, Any]
    for section in recipe.instructions:
        i: Dict[str, Any]
        for i in section["itemListElement"]:
            instructions.append(i.get("text").strip())

    return instructions


def parse_ingredients(soup: BeautifulSoup) -> List[Ingredient]:
    # Extract ingredients from HTML because amount+unit and name are separated there, unlike in the JSON.
    # Some pages are using a new HTML format, some still use the old format.
    ingredients = parse_old_ingredient_format(soup)

    if ingredients is None:
        ingredients = parse_new_ingredient_format(soup)

    return ingredients


def parse_old_ingredient_format(soup: BeautifulSoup) -> Optional[List[Ingredient]]:
    root: Optional[Tag] = soup.find(class_="ingredients")

    if root is None:
        return None

    ingredients: List[Ingredient] = []

    tag: Tag
    for tag in root.find_all("tr"):
        tds = tag.find_all("td")
        assert len(tds) >= 2, "Unexpected ingredient entry"

        amount_float, unit = parsetools.parse_amount_and_unit(tds[0].get_text(), True)
        name = tds[1].get_text().strip()
        name = parsetools.reduce_excessive_whitespace(name)

        ingredients.append(Ingredient(name, amount_float, unit))

    return ingredients


def parse_new_ingredient_format(soup: BeautifulSoup) -> List[Ingredient]:
    ingredients: List[Ingredient] = []

    tag: Tag
    for tag in soup.find_all(class_="ds-ingredients-table__tr"):
        tds = tag.find_all("td")
        assert len(tds) >= 2, "Unexpected ingredient entry"

        amount_float, unit = parsetools.parse_amount_and_unit(tds[0].get_text(), True)

        name_tag: Tag = tds[1].find(class_="ds-ingredients-table__ingredient-name")
        hint_tag: Tag = tds[1].find(class_="ds-ingredients-table__ingredient-properties")

        name_str = name_tag.get_text().strip()

        if hint_tag is None:
            text = name_str
        else:
            hint_str: str = hint_tag.get_text().strip()
            text = f"{name_str}, {hint_str}"

        text = parsetools.reduce_excessive_whitespace(text)

        ingredients.append(Ingredient(text, amount_float, unit))

    return ingredients
