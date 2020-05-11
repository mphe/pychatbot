# -*- coding: utf-8 -*-

import os
import errno
import json
import logging
from chatbot.util import merge_dicts


class Config:
    """Provides functionality for loading, saving, and accessing json configs.

    Implements __len__, __setitem__, __getitem__, and __delitem__ to provide
    a simple wrapping around `dict`, e.g. Config["key"] = 4 .
    Use `Config.data` to access the json dict directly.
    """
    def __init__(self, filename):
        self._filename = filename
        self.data = {}

    @property
    def filename(self):
        """The config filename."""
        return self._filename

    def exists(self):
        return os.path.exists(self.filename)

    def load(self, default=None, validate=True, write=False, create=False):
        """(Re-)Load the config file.

        default: The default config in case the file does not exist or
                 `validate` is true.
        validate: If true, the loaded data will be compared with `default` to
                  add missing entries.
        write: Indicates whether or not the original file should be rewritten
               with the loaded config (validated/default).
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
            else:
                raise

        if validate and default:
            merge_dicts(self.data, default)

        if write:
            self.write()
        elif create:
            self.create()

    def create(self):
        """Write config only if the file does not yet exist."""
        if not self.exists():
            self.write()

    def write(self):
        """Write config to a file."""
        logging.debug("Writing json file: %s", self.filename)
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
    """Provides functionality for loading and saving configs as json."""

    def __init__(self, searchpath):
        self._searchpath = ""
        if searchpath:
            self.set_searchpath(searchpath)

    def set_searchpath(self, searchpath):
        self._searchpath = searchpath
        os.makedirs(searchpath, exist_ok=True)

    def get_searchpath(self):
        return self._searchpath

    def get_config(self, basename) -> Config:
        """Returns a Config object for the respective file from searchpath.

        Only returns the object, but does not load it.
        `basename` is not a path but the base-filename without extension.
        """
        return Config(os.path.join(self._searchpath, basename + ".json"))
