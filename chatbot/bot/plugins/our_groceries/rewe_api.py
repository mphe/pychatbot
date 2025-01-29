from . import datamodel, parsetools
from bs4 import Tag
from typing import Optional, List


class ReweFetcher(datamodel.RecipeFetcher):
    async def supports_url(self) -> bool:
        return self._url_match_domain("www.rewe.de")

    async def fetch_recipe(self) -> Optional[datamodel.Recipe]:
        # NOTE: Many of these soup filters are prone to break, but there are no better hints to consistently find those items.
        soup = await self._fetch_url_as_soup()

        title = soup.find("h1").get_text().strip()
        num_servings = int(soup.find("span", {"x-text": "currentServings"}).get_text())

        ingredient_container: List[Tag] = soup.find_all(class_="ingredient_list_item")
        ingredients: List[datamodel.Ingredient] = []

        for item in ingredient_container:
            name: str = item.find("div", class_="ld-rds items-start").get_text(" ", strip=True)
            amount_and_unit: str = item.find("div", class_="formattedAmountDiv").get_text()
            amount, unit = parsetools.parse_amount_and_unit(amount_and_unit, True)
            ingredients.append(datamodel.Ingredient(name, amount, unit))

        instructions_container: List[Tag] = soup.find_all(class_="step-ingredients")
        instructions: List[str] = []

        for step in instructions_container:
            instruction: Tag = step.find("div", class_="ld-rds mt-4 self-stretch text-sm leading-5 md:text-base lg:mt-6 lg:leading-6")
            instructions.append(instruction.get_text().strip())

        return datamodel.Recipe(title, self._url, num_servings, ingredients, instructions)
