# -*- coding: utf-8 -*-

import os
import imp
import logging
from chatbot.util import mkdir_p
from chatbot.compat import *


class Plugin(object):
    """Base class for plugins."""

    def init(self, oldme, *argv, **kwargs):
        """Will be called to initialize the plugin after it was loaded.
        
        If the plugin was remounted, then oldme is the old instance of this
        plugin. Otherwise None. This is useful to exchange data from the old
        instance to the new one before it gets deleted.
        """
        raise NotImplementedError

    def reload(self):
        """Reload the plugin's config."""
        raise NotImplementedError

    def quit(self):
        """Will be called when a plugin is unmounted."""
        raise NotImplementedError


class PluginHandle(object):
    def __init__(self):
        self.plugin = None
        self.module = None


class PluginManager(object):
    def __init__(self, searchpath):
        """searchpath is the directory where plugins are stored."""
        self._searchpath = searchpath
        self._plugins = {}
        mkdir_p(searchpath)

    def mount_plugin(self, name, *argv, **kwargs):
        """(Re-)Mount a plugin from the searchpath.
        
        name is the plugin's name without the .py extension.
        Additional arguments that will be passed to the plugin's init()
        function can be specified.

        The function searches for a file "<searchpath>/<name>.py", imports
        the module using imp.load_source() and creates an instance
        of module.Plugin. Therefore the plugin class needs to be named
        "Plugin", otherwise it can't be loaded.

        If an exception occurs during the loading process, the plugin is
        guaranteed to be removed from the system.
        """
        if name in self._plugins:
            handle = self._plugins[name]
            self.unmount_plugin(name)
        else:
            handle = PluginHandle()

        self._load_module(handle, name)
        self._init_plugin(handle, *argv, **kwargs)
        self._plugins[name] = handle
        logging.info("Plugin (re-)mounted: " + name)

    def unmount_plugin(self, name):
        """Unmount a plugin.
        
        The plugin is guaranteed to be removed, even if an exception occurs.
        Exceptions will be re-raised.
        """
        if not name in self._plugins:
            logging.warn("Trying to unmount non-mounted plugin: " + name)
        else:
            try:
                self._plugins[name].plugin.quit()
            finally:
                del self._plugins[name]
                logging.info("Plugin unmounted: " + name)

    def mount_all(self, exception_handler, *argv, **kwargs):
        """Mount all plugins in the search path.
        
        exception_handler is a callback with the signature
            (str, Exception) -> bool
        that is called when an exception occurs during plugin loading.
        The first argument is the plugin's name and second is the
        Exception object.
        The return value indicates whether to treat the exception as caught
        or re-raise it: True -> caught, False -> re-raise.
        If exception_handler is None, exceptions will be re-raised
        immediately.
        No matter if the exception was caught or re-raised, the responsible
        plugin will be skipped.
        """
        for i in os.listdir(self._searchpath):
            if not os.path.isdir(i) and i.endswith(".py"):
                name = i[:-3]
                try:
                    self.mount_plugin(name, *argv, **kwargs)
                except Exception as e:
                    if exception_handler and exception_handler(name, e):
                        continue
                    raise

    def unmount_all(self, exception_handler):
        """Unmount all plugins.

        See mount_all() on how to use exception_handler.
        """
        # Create a copy so the source dict doesn't change while iterating
        for i in [ n for n in self._plugins ]:
            try:
                self.unmount_plugin(i)
            except Exception as e:
                if exception_handler:
                    exception_handler(i, e)
                else:
                    raise

    def reload_plugin(self, name):
        """Reload a plugin's config.
        
        This is only used for config reloading, for remounting use
        mount_plugin().
        """
        if not name in self._plugins:
            logging.warn("Trying to reload non-mounted plugin: " + name)
        else:
            self._plugins[name].plugin.reload()
            logging.info("Plugin reloaded: " + name)

    def iter_plugins(self):
        """Iterate through mounted plugins.

        Yields a tuple (name, plugin), where name is a string and plugin
        the plugin object.
        """
        for k,v in self._plugins.iteritems():
            yield (k, v.plugin)

    def plugin_exists(self, name):
        return name in self._plugins

    def _load_module(self, handle, name):
        """(Re-)Loads a module from the plugin search path."""
        fname = "{}/{}.py".format(self._searchpath, name)
        try:
            handle.module = imp.load_source(name, fname)
        except:
            handle.module = None
            raise
        logging.debug("Module loaded: " + fname)

    def _init_plugin(self, handle, *argv, **kwargs):
        try:
            oldinst = handle.plugin
            handle.plugin = handle.module.Plugin()
            handle.plugin.init(oldinst, *argv, **kwargs)
        except:
            handle.plugin = None
            raise
