# -*- coding: utf-8 -*-

import os
import errno
import json
from chatbot.util import mkdir_p, merge_dicts


class ConfigManager(object):
    """Provides functionality for loading and saving configs as json."""

    def __init__(self, searchpath):
        self._searchpath = searchpath
        mkdir_p(searchpath)

    def set_searchpath(self, searchpath):
        self._searchpath = searchpath

    def exists(self, fname):
        return os.path.exists(self._get_fname(fname))

    # def load_create(self, fname, default=None, validate=True):
    #     return self.load(fname, default, validate, False, True)

    def load_update(self, fname, default=None, validate=True):
        return self.load(fname, default, validate, True, False)

    def load(self, fname, default=None, validate=True, write=False, create=False):
        """Load and return a config from the config folder.

        fname: the filename without extension
        default: the default config in case the file does not exist or
                 validate is true
        validate: if true, the loaded data will be compared with the
                  default to add missing entries
        write: indicates whether or not the original file should be rewritten
               with the loaded config (validated/default)
        create: same as write but only if the file didn't exist before
        """
        data = None
        try:
            with open(self._get_fname(fname), "r") as f:
                data = json.load(f)
        except IOError as e:
            if e.errno == errno.ENOENT: # file not found
                data = dict(default) if default else {}
            else:
                raise
        else:
            if validate and default:
                merge_dicts(data, default)

        if create:
            self.create(fname, data)
        elif write:
            self.write(fname, data)
        return data

    def create(self, fname, data):
        """Write config only if the file does not yet exist."""
        if not self.exists(fname):
            self.write(fname, data)

    def write(self, fname, data):
        """Write config to a file."""
        with open(self._get_fname(fname), "w") as f:
            json.dump(data, f, indent=4)

    def _get_fname(self, name):
        return "{}/{}.json".format(self._searchpath, name)

