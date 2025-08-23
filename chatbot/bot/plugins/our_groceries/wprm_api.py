import re
from . import datamodel, parsetools
from chatbot.util import utils
from bs4 import Tag, BeautifulSoup
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
        self._soup: BeautifulSoup

    async def supports_url(self) -> bool:
        if MATCH_PRINT_URL.match(self._url):
            return True
        return await self._extract_tags()

    async def fetch_recipe(self) -> Optional[datamodel.Recipe]:  # pylint: disable=too-many-locals
        if not await self._extract_tags():
            return None

        # Since wordpress pages can have all sorts of languages, try to detect it
        use_us_float_format = self._soup.html.get("lang", "").lower() == "en"

        num_servings = int(self._wprm_recipe.find(class_="wprm-recipe-servings").get_text())

        ingredients_container: Optional[Tag] = self._wprm_recipe.find(class_="wprm-recipe-ingredients-container")
        ingredients: List[datamodel.Ingredient] = []

        ing: Tag
        for ing in ingredients_container.find_all(class_="wprm-recipe-ingredient"):
            notes_tag: Optional[Tag] = ing.find(class_="wprm-recipe-ingredient-notes")
            unit_tag: Optional[Tag] = ing.find(class_="wprm-recipe-ingredient-unit")
            amount_tag: Optional[Tag] = ing.find(class_="wprm-recipe-ingredient-amount")
            name: str = ing.find(class_="wprm-recipe-ingredient-name").get_text().strip()

            name = utils.string_capitalize(name)
            ingredient_notes: str = notes_tag.get_text().strip() if notes_tag else ""
            unit: str = unit_tag.get_text().strip() if unit_tag else ""

            if amount_tag:
                amount_text = amount_tag.get_text().strip()
                try:
                    amount = parsetools.normalize_str_to_float(amount_text, use_us_float_format)
                except ValueError:
                    # If the amount is not a valid number, e.g. "1 to 2", just use 1 and append the string to the unit
                    amount = 1
                    unit = utils.string_join_non_empty(" ", (amount_text, unit))
            else:
                amount = 0.0

            if ingredient_notes:
                name = f"{name} ({ingredient_notes})"

            ingredients.append(datamodel.Ingredient(name, amount, unit))

        instructions_container: Optional[Tag] = self._wprm_recipe.find(class_="wprm-recipe-instructions-container")
        instructions: List[str] = []

        if instructions_container:
            instr: Tag
            for instr in instructions_container.find_all(class_="wprm-recipe-instruction-text"):
                text = instr.get_text(separator=" ", strip=True)
                text = parsetools.reduce_excessive_whitespace(text)
                instructions.append(text)

        recipe_notes: List[str] = []
        note: Tag
        for note in self._wprm_recipe.find_all(class_="wprm-recipe-notes"):
            recipe_notes.append(note.get_text().strip())

        title: str = self._wprm_recipe.find(class_="wprm-recipe-name").get_text().strip()

        return datamodel.Recipe(title, self._url, num_servings, ingredients, instructions, recipe_notes)

    async def _extract_tags(self) -> bool:
        """Serves as a kind of init function. Fetches the page content and extract relevant tags. Results are cached."""
        if not self._extracted:
            self._soup = await self._fetch_url_as_soup()
            self._wprm_recipe = self._soup.find(class_="wprm-recipe-container")

            if not self._wprm_recipe:
                self._wprm_recipe = self._soup.find(class_="wprm-recipe")

            self._extracted = True

        return self._wprm_recipe is not None
