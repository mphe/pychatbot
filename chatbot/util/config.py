# -*- coding: utf-8 -*-

import os
import errno
import json
import logging
from typing import Dict, Any
from chatbot.util import merge_dicts

JsonDict = Dict[str, Any]


class Config:
    """Provides functionality for loading, saving, and accessing json configs.

    Does not load or create any files automatically, unless explicitly
    requested in load(), write(), or create().

    Implements __len__, __setitem__, __getitem__, and __delitem__ to provide
    a simple wrapping around `dict`, e.g. Config["key"] = 4 .
    Use `Config.data` to access the json dict directly.
    """
    def __init__(self, filename: str):
        self._filename: str = filename
        self.data: JsonDict = {}

    @property
    def filename(self) -> str:
        """The config filename."""
        return self._filename

    def exists(self) -> bool:
        return os.path.exists(self.filename)

    def load(self, default: JsonDict = None, validate=True, write=False, create=False) -> "Config":
        """(Re-)Load the config file and returns itself.

        default: The default config in case the file does not exist or
                 `validate` is true.
        validate: If true, the loaded data will be compared with `default` to
                  add missing entries.
        write: Indicates whether or not the original file should be rewritten
               with the loaded config (validated/default).
               Creates missing directories as necessary.
        create: Same as `write` but only if the file didn't exist before.
        """
        logging.debug("Loading json file: %s", self.filename)
        self.data = {}
        try:
            with open(self.filename) as f:
                self.data = json.load(f)
        except IOError as e:
            if e.errno == errno.ENOENT:  # file not found
                validate = True  # Use default
                logging.debug("File not found -> using default")
            else:
                raise

        if validate and default:
            merge_dicts(self.data, default)

        if write:
            self.write()
        elif create:
            self.create()

        return self

    def create(self):
        """Write config only if the file does not yet exist, creating missing directories as necessary."""
        if not self.exists():
            self.write()

    def write(self):
        """Write config to a file, creating missing directories as necessary."""
        logging.debug("Writing json file: %s", self.filename)
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]


class ConfigManager:
    """Provides functionality for loading and saving configs as json.

    It does not create any files or directories. It provides a simple way to
    retrieve configs from a specific searchpath.
    """

    def __init__(self, searchpath: str):
        self._searchpath = "."
        self.set_searchpath(searchpath)

    def set_searchpath(self, searchpath: str):
        self._searchpath = searchpath or "."

    def get_searchpath(self) -> str:
        """Return current searchpath or '.' if empty."""
        return self._searchpath

    def get_file(self, fname: str) -> str:
        """Returns a filename relative to the searchpath."""
        return os.path.join(self._searchpath, fname)

    def get_config(self, basename: str) -> Config:
        """Returns a Config object for the respective file from searchpath.

        Only returns the object, but does not load it.
        `basename` is not a path but the base-filename, optionally with .json extension.
        """
        return Config(self.get_file(basename if basename.endswith(".json") else basename + ".json"))
