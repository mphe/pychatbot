import os
import sys
import logging
from typing import Dict, Any, cast

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import chatbot  # noqa
from chatbot.api.test import API as TestAPI  # noqa

# For convenience in test cases
from chatbot import api, util, bot  # noqa  # pylint: disable=unused-import

# Import these so test cases can import them directly from here
# from chatbot import api, bot, util  # pylint: disable=unused-import

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(message)s")

if len(sys.argv) > 1 and sys.argv[1] == "--test":
    logging.disable(logging.CRITICAL)


def print_message(msg: chatbot.api.ChatMessage, prefix):
    logging.info("%s message in %s:\n\t %s", prefix, str(msg.chat), str(msg))


def create_test_api(options: Dict[str, Any]) -> TestAPI:
    return cast(TestAPI, chatbot.api.create_api_object("test", options))
