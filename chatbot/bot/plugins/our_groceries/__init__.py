import re
from typing import List, Tuple, Callable, Awaitable
from chatbot import api, bot
from chatbot.bot.subsystem.command import CommandError, CommandSyntaxError
from ourgroceries import OurGroceries, InvalidLoginException
from . import chefkoch_api

import secrets
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


DEFAULT_NUM_SERVINGS = 4
STORAGE_AUTH_KEY = "ourgroceries_login"
MAX_RECIPE_NAME_RETRIES = 10


class Plugin(bot.BotPlugin):
    def __init__(self, bot_: bot.Bot):
        super().__init__(bot_)

        self.register_command("ourgroceries", self._ourgroceries, argc=1)

        self.SUPPORTED_PAGES: List[Tuple[re.Pattern, Callable[[OurGroceries, str, int], Awaitable[None]]]] = [
            (re.compile(r".*chefkoch.de/.*", re.IGNORECASE), create_recipe_from_chefkoch),
        ]

    async def _ourgroceries(self, msg: api.ChatMessage, argv: List[str]) -> None:
        """Syntax: ourgroceries login <username> <password>
                   ourgroceries logout
                   ourgroceries <url> [number of servings]

        Provides an interface to automatically add recipes to OurGroceries from a given URL.
        Supported web pages are:
            - chefkoch.de

        If the given URL matches a supported page, it fetches the title, ingredients and instructions and creates a corresponding recipe in OurGroceries.
        If no amount of servings is specified, it defaults to 4.

        Before recipes can be added, login credentials to the OurGroceries account must be supplied using the "login" subcommand.
        After successful login, access is allowed from all chats, not just the current one.
        Other users do not have access, only yourself.

        To remove the credentials, use the "logout" subcommand.

        Examples:
            `!ourgroceries login myaccount 12345`
                Provides the login credentials for OurGroceries.

            `!ourgroceries https://www.chefkoch.de/rezepte/1844061298739441/Mozzarella-Haehnchen-in-Basilikum-Sahnesauce.html`
                Creates a new recipe for 4 servings from the web page.

            `!ourgroceries https://www.chefkoch.de/rezepte/1844061298739441/Mozzarella-Haehnchen-in-Basilikum-Sahnesauce.html 2`
                Creates a new recipe for 2 servings from the web page.
        """
        subcommand = bot.command.get_argument(argv, 1, "")

        if subcommand == "login":
            await self._login(msg, argv)
        elif subcommand == "logout":
            await self._logout(msg)
        else:
            await self._add_recipe(msg, argv)

    async def _login(self, msg: api.ChatMessage, argv: List[str]) -> None:
        username: str = bot.command.get_argument(argv, 2, "")
        password: str = bot.command.get_argument(argv, 3, "")

        if not username or not password:
            raise CommandSyntaxError("Both, username and password, must be specified")

        try:
            og = OurGroceries(username, password)
            await og.login()
        except InvalidLoginException as e:
            raise CommandError("Credentials incorrect") from e
        except:
            raise

        self._store_credentials(msg, username, password)
        await msg.reply("Login successful.\nYou may now delete your login command message to remove the cleartext credentials from the chat log.")

    async def _logout(self, msg: api.ChatMessage) -> None:
        self.storage.erase(STORAGE_AUTH_KEY, msg.author, None)
        self.storage.erase(STORAGE_AUTH_KEY, msg.author, msg.chat)
        self.storage.write()
        await msg.reply("Credentials successfully deleted.")

    async def _add_recipe(self, msg: api.ChatMessage, argv: List[str]) -> None:
        url: str = bot.command.get_argument(argv, 1, "")
        num_servings: int = bot.command.get_argument(argv, 2, DEFAULT_NUM_SERVINGS, int)

        for pattern, callback in self.SUPPORTED_PAGES:
            if pattern.match(url):
                og = self._get_credentials(msg)
                await msg.reply("Processing...")
                await callback(og, url, num_servings)
                await msg.reply("Recipe successfully added")
                return

        raise CommandError("The given URL is not supported")

    def _get_credentials(self, msg: api.ChatMessage) -> OurGroceries:
        encrypted = self.storage.get_with_fallback(STORAGE_AUTH_KEY, msg.author, msg.chat)

        if not encrypted:
            raise CommandError("No login credentials found.\nUse `ourgroceries login` to store your credentials.")

        decrypted = password_decrypt(encrypted, msg.author.id)
        username, password = decrypted.split("\n", 1)
        return OurGroceries(username, password)

    def _store_credentials(self, msg: api.ChatMessage, username: str, password: str) -> None:
        # Unfortunately, OurGroceries does not provide API Tokens, so the full credentials need to
        # be saved. Thereotically, the auth-cookie could be stored instead, but since it can't be
        # revoked manually by the user, it doesn't grant any more benefits than storing credentials.

        # Add some security-through-obscurity so that the credentials don't appear in cleartext in the config files.
        encrypted = password_encrypt(f"{username}\n{password}", msg.author.id).decode()

        self.storage.set(STORAGE_AUTH_KEY, encrypted, msg.author, None)
        self.storage.write()

    @staticmethod
    def get_default_config():
        return {}


def _derive_key(password: str, salt: bytes, iterations: int) -> bytes:
    """Derive a secret key from a given password and salt"""
    kdf = PBKDF2HMAC(hashes.SHA256(), 32, salt, iterations)
    return b64e(kdf.derive(password.encode()))


def password_encrypt(message: str, password: str) -> bytes:
    FERNET_ITERATIONS = 480000

    salt = secrets.token_bytes(16)
    key = _derive_key(password, salt, FERNET_ITERATIONS)
    return b64e(
        b'%b%b%b' % (
            salt,
            FERNET_ITERATIONS.to_bytes(4, 'big'),
            b64d(Fernet(key).encrypt(message.encode())),
        )
    )


def password_decrypt(token: bytes, password: str) -> str:
    decoded = b64d(token)
    salt, iter_, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
    iterations = int.from_bytes(iter_, 'big')
    key = _derive_key(password, salt, iterations)
    return Fernet(key).decrypt(token).decode()


def ingredient_to_og_item(ingredient: str, discrete_amount: int, unit_and_amount: str) -> Tuple[str, str, str]:
    if discrete_amount > 1:
        # Discrete amounts are handled simply by appending them in braces to the ingredient name
        return (f"{unit_and_amount} {ingredient} ({discrete_amount})", "", "")
    return (ingredient, "", unit_and_amount)


async def create_recipe_from_chefkoch(og: OurGroceries, chefkoch_url: str, num_servings: int) -> None:
    recipe = chefkoch_api.ExtendedRecipe(chefkoch_url, num_servings)

    if not recipe:
        raise CommandError("Failed to fetch recipe from chefkoch.de")

    for i in range(1, MAX_RECIPE_NAME_RETRIES):
        list_id = await og.create_recipe(recipe.title if i <= 1 else f"{recipe.title} ({i})")

        if list_id is not None:
            break

    if list_id is None:
        raise CommandError(f"There are already {MAX_RECIPE_NAME_RETRIES} OurGroceries recipes with the same name.")

    items = [ ingredient_to_og_item(i.ingredient, i.discrete_amount, i.amount_and_unit) for i in recipe.extended_ingredients ]
    await og.add_items_to_list(list_id, items)

    instructions = ""

    if isinstance(recipe.instructions, str):
        instructions = recipe.instructions
    elif isinstance(recipe.instructions, list):
        instructions = "\n\n".join(recipe.instructions)

    await og.set_list_notes(list_id, f"{recipe.url}\n\nFür {num_servings} Portionen.\n\n{instructions}")
