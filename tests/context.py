import os
import sys
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from chatbot import *

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(message)s")

if len(sys.argv) > 1 and sys.argv[1] == "--test":
    logging.disable(logging.CRITICAL)


def print_message(msg, prefix):
    logging.info("%s message in %s:\n\t %s", prefix, str(msg.get_chat()), str(msg))
