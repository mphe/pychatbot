import os
import sys
import logging

sys.path.insert(0, os.path.abspath('..'))

from chatbot import *

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(message)s")

if len(sys.argv) > 1 and sys.argv[1] == "--test":
    logging.disable(logging.CRITICAL)
