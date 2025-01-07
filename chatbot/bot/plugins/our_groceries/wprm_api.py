import re
from . import datamodel, parsetools
from bs4 import Tag
from typing import Optional, List


MATCH_PRINT_URL = re.compile(r".*/wprm_print/.*", re.IGNORECASE)


# NOTE: Theoretically, WordPress provides a JSON API and WPRM provides an endpoint to query recipe
# data as JSON.
# See https://help.bootstrapped.ventures/article/85-wordpress-rest-api.
# However, this functionality might be disabled, so we can't rely on it.


class WPRMFetcher(datamodel.RecipeFetcher):
    def __init__(self, url: str):
        super().__init__(url)
        self._wprm_recipe: Optional[Tag]
        self._extracted = False

    async def supports_url(self) -> bool:
        if MATCH_PRINT_URL.match(self._url):
            return True
        return await self._extract_tags()

    async def fetch_recipe(self) -> Optional[datamodel.Recipe]:
        if not await self._extract_tags():
            return None

        num_servings = int(self._wprm_recipe.find(class_="wprm-recipe-servings").get_text())

        ingredients_container: Optional[Tag] = self._wprm_recipe.find(class_="wprm-recipe-ingredients-container")
        ingredients: List[datamodel.Ingredient] = []

        ing: Tag
        for ing in ingredients_container.find_all(class_="wprm-recipe-ingredient"):
            name: str = ing.find(class_="wprm-recipe-ingredient-name").get_text()

            unit_tag: Optional[Tag] = ing.find(class_="wprm-recipe-ingredient-unit")
            unit: str = unit_tag.get_text() if unit_tag else ""

            amount_tag: Optional[Tag] = ing.find(class_="wprm-recipe-ingredient-amount")
            amount = float(amount_tag.get_text()) if amount_tag else 0.0

            ingredients.append(datamodel.Ingredient(name, amount, unit))

        instructions_container: Optional[Tag] = self._wprm_recipe.find(class_="wprm-recipe-instructions-container")
        instructions: List[str] = []

        if instructions_container:
            instr: Tag
            for instr in instructions_container.find_all(class_="wprm-recipe-instruction"):
                text = instr.get_text(separator=" ", strip=True)
                text = parsetools.reduce_excessive_whitespace(text)
                instructions.append(text)

        title: str = self._wprm_recipe.find(class_="wprm-recipe-name").get_text()

        return datamodel.Recipe(title, self._url, num_servings, ingredients, instructions)

    async def _extract_tags(self) -> bool:
        """Serves as a kind of init function. Fetches the page content and extract relevant tags. Results are cached."""
        if not self._extracted:
            soup = await self._fetch_url_as_soup()
            self._wprm_recipe = soup.find(class_="wprm-recipe")
            self._extracted = True

        return self._wprm_recipe is not None
