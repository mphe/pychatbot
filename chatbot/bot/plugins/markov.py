# -*- coding: utf-8 -*-

from dataclasses import dataclass
import logging
import os
import markovify
from chatbot.bot import BotPlugin, command
from chatbot import api
from typing import List, Dict

DEFAULT_MAX_TRIES = 500
DEFAULT_STATE_SIZE = 2
DEFAULT_NEWLINE = True
DEFAULT_MAX_OVERLAP_RATIO = markovify.text.DEFAULT_MAX_OVERLAP_RATIO

MAX_SENTENCE_COUNT = 50


@dataclass
class MarkovModel:
    model: markovify.Text
    max_tries: int
    max_overlap: float

    def make_sentence(self, *args, **kwargs) -> str:
        return self.model.make_sentence(
            *args, tries=self.max_tries, max_overlap_ratio=self.max_overlap, **kwargs)


class Plugin(BotPlugin):
    def __init__(self, bot):
        super().__init__(bot)
        self._models: Dict[str, MarkovModel] = {}
        self.register_command("markov", self._markov, argc=0)

    # This plugin needs a custom reload function so that the default
    # example entry gets overwritten if the user wants to.
    async def reload(self):
        self.cfg.load(self.get_default_config(), validate=False, create=True)

        for name, settings in self.cfg.data.items():
            name              = name.strip().lower()
            filename          = settings.get("filename", "")
            state_size        = settings.get("state_size", DEFAULT_STATE_SIZE)
            max_tries         = settings.get("max_tries", DEFAULT_MAX_TRIES)
            max_overlap       = settings.get("max_overlap", DEFAULT_MAX_OVERLAP_RATIO)
            newline_separator = settings.get("newline_separator", DEFAULT_NEWLINE)

            if not name:
                logging.error("Empty markov model name")
                continue

            if name in self._models:
                logging.warning("Model with that name already loaded: %s -> Skipped", name)
                continue

            if not filename or not os.path.isfile(filename):
                logging.error("File does not exist: %s", filename)
                continue

            try:
                with open(filename) as f:
                    text = f.read()

                if newline_separator:
                    model = markovify.NewlineText(text, state_size=state_size)
                else:
                    model = markovify.Text(text, state_size=state_size)

            except Exception:
                logging.exception("Failed to generate markov model: %s", name)
                continue

            self._models[name] = MarkovModel(model, max_tries, max_overlap)
            logging.info("Added model: %s", name)

    async def _markov(self, msg: api.ChatMessage, argv: List[str]):
        """Syntax: markov <model> [count]

        Generate `count` random sentences using the given markov model.
        For a list of available models run `markov` without any arguments.
        """
        if len(argv) <= 1:
            await msg.reply("Available models: " + ", ".join(self._models))
            return

        count = command.get_argument(argv, 2, 1, int)
        count = min(max(1, count), MAX_SENTENCE_COUNT)

        model: MarkovModel = self._models.get(argv[1].lower(), None)
        if not model:
            raise command.CommandError("The model does not exist")

        sentences = []
        name = argv[1].capitalize()

        for _ in range(count):
            text = model.make_sentence() or model.make_sentence(test_output=False)
            if text:  # shouldn't be necessary but just to be sure
                sentences.append("{}: {}".format(name, text))

        if sentences:
            await msg.reply("\n".join(sentences))
        else:
            raise command.CommandError("Failed to generate a random sentence, try again")

    @staticmethod
    def get_default_config():
        return {
            "profile_name": {
                "filename": "path_to_file.txt",
                "newline_separator": DEFAULT_NEWLINE,
                "state_size": DEFAULT_STATE_SIZE,
                "max_tries": DEFAULT_MAX_TRIES,
                "max_overlap_ratio": DEFAULT_MAX_OVERLAP_RATIO,
            }
        }
