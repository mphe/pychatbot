import re
from . import datamodel, parsetools
from bs4 import Tag
from typing import Optional, List


MATCH_NUM_SERVINGS = re.compile(r".*\s+(\d+)\s+.*", re.DOTALL)


class Fetcher(datamodel.RecipeFetcher):
    async def supports_url(self) -> bool:
        return self._url_match_domain("mobile.kptncook.com") \
            or self._url_match_domain("share.kptncook.com")

    async def fetch_recipe(self) -> Optional[datamodel.Recipe]:
        soup = await self._fetch_url_as_soup()

        title: str = soup.find(class_="kptn-recipetitle").get_text().strip()
        num_servings_str: str = soup.find(class_="kptn-person-count").get_text()
        num_servings = int(MATCH_NUM_SERVINGS.match(num_servings_str).group(1))

        measure_tags: List[Tag] = soup.find_all(class_="kptn-ingredient-measure")
        ingredient_tags: List[Tag] = soup.find_all(class_="kptn-ingredient")
        ingredients: List[datamodel.Ingredient] = []

        # Ingredients with measures are sorted first
        for measure_tag, ingredient_tag in zip(measure_tags, ingredient_tags):
            measure_str: str = measure_tag.get_text()
            ingredient_str: str = ingredient_tag.get_text().strip()
            amount, unit = parsetools.parse_amount_and_unit(measure_str, True)  # I don't think it uses floats at all, only unicode fractions.
            ingredients.append(datamodel.Ingredient(ingredient_str, amount, unit))

        # Afterwards all ingredients without measures
        for ingredient_tag in ingredient_tags[len(measure_tags):]:
            ingredient_str = ingredient_tag.get_text().strip()
            ingredients.append(datamodel.Ingredient(ingredient_str, 0, ""))

        # Instructions are only available in the KptnCook App
        instructions: List[str] = []

        return datamodel.Recipe(title, self._url, num_servings, ingredients, instructions)
