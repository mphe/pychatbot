import sys
import logging
from typing import Dict, Any, cast
from pathlib import Path

project_root = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(project_root))  # To import the chatbot module
sys.path.insert(0, str(project_root / "chatbot" / "bot" / "plugins"))  # To import plugins

import chatbot  # noqa
from chatbot.api.test import API as TestAPI  # noqa

# For convenience in test cases
from chatbot import api, util, bot  # noqa  # pylint: disable=unused-import

# Import these so test cases can import them directly from here
# from chatbot import api, bot, util  # pylint: disable=unused-import

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")


def print_message(msg: chatbot.api.ChatMessage, prefix):
    logging.info("%s message in %s:\n\t %s", prefix, str(msg.chat), str(msg))


def create_test_api(options: Dict[str, Any]) -> TestAPI:
    return cast(TestAPI, chatbot.api.create_api_object("test", options))
