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

        return datamodel.Recipe(recipe.title, url, num_servings, parse_ingredients(recipe), parse_instructions(recipe))


def parse_instructions(recipe: chefkoch.Recipe) -> List[str]:
    instructions = []

    section: Dict[str, Any]
    for section in recipe.instructions:
        i: Dict[str, Any]
        for i in section["itemListElement"]:
            instructions.append(i.get("text").strip())

    return instructions


def parse_ingredients(recipe: chefkoch.Recipe) -> List[Ingredient]:
    soup: BeautifulSoup = recipe.soup
    ingredients: List[Ingredient] = []

    # Transform all HTML elements to text and strip excessive whitespace
    tag: Tag
    for tag in soup.find_all(class_="ds-ingredients-table__tr"):
        tds = tag.find_all(class_="ds-ingredients-table__td")
        assert len(tds) >= 2, "Unexpected ingredient entry"

        amount_unit_td = tds[0]
        name_td = tds[1]

        amount_float, unit = parsetools.parse_amount_and_unit(amount_unit_td.get_text(), True)

        name_tag: Tag = name_td.find(class_="ds-ingredients-table__ingredient-name")
        hint_tag: Tag = name_td.find(class_="ds-ingredients-table__ingredient-properties")

        name_str = name_tag.get_text().strip()

        if hint_tag is None:
            text = name_str
        else:
            hint_str: str = hint_tag.get_text().strip()
            text = f"{name_str}, {hint_str}"

        text = parsetools.reduce_excessive_whitespace(text)

        ingredients.append(Ingredient(text, amount_float, unit))

    return ingredients
