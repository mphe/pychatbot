# -*- coding: utf-8 -*-

import os
import imp
import logging
from typing import List, Callable

ExceptionCallback = Callable[[str, Exception], bool]


class BasePlugin:
    """Base class for plugins."""

    def __init__(self, oldme, *argv, **kwargs):
        """Initialize plugin.

        If the plugin was remounted, then `oldme` is the old instance of this
        plugin, otherwise None. This is useful to exchange data from the old
        instance to the new one before it gets deleted.
        """

    def reload(self):
        """Reload the plugin's config."""
        raise NotImplementedError

    def quit(self):
        """Will be called when a plugin is unmounted."""
        raise NotImplementedError


class PluginHandle:
    def __init__(self):
        self.plugin = None
        self.module = None


class PluginManager:
    def __init__(self, searchpath, whitelist: List[str] = None,
                 blacklist: List[str] = None):
        """Constructor.

        Args:
            searchpath: Plugin searchpath.
            blacklist: Exclude certain plugins from autoloading.
            whitelist: Only load the specified plugins.

        If neither blacklist nor whitelist contains entries, none of them
        have effect and all plugins will be autoloaded.
        If both blacklist and whitelist contain entries, whitelist has
        precedence.
        """
        self._searchpath = searchpath
        self.blacklist = blacklist if blacklist else []
        self.whitelist = whitelist if whitelist else []
        self._plugins = {}
        os.makedirs(searchpath, exist_ok=True)

    def mount_plugin(self, name, *argv, **kwargs):
        """(Re-)Mount a plugin.

        `name` is the plugin's name without the .py extension.
        Additional arguments will be passed to the plugin's __init__()
        function.

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
        logging.info("Plugin (re-)mounted: %s", name)

    def unmount_plugin(self, name):
        """Unmount a plugin.

        The plugin is guaranteed to be removed, even if an exception occurs.
        Exceptions will be re-raised.
        """
        plugin = self._plugins.get(name, None)

        if plugin is None:
            logging.warning("Trying to unmount non-mounted plugin: %s", name)
        else:
            try:
                plugin.plugin.quit()
            finally:
                del self._plugins[name]
                logging.info("Plugin unmounted: %s", name)

    def mount_all(self, exception_handler: ExceptionCallback, *args, **kwargs):
        """Mount all plugins in searchpath while regarding black/whitelists.

        Args:
            exception_handler: Gets called if an exception occurs.
            *args: Passed to plugin's constructor
            **kwargs: Passed to plugin's constructor

        If `exception_handler` is None, exceptions will be re-raised immediately.
        The first argument to `exception_handler` is the plugin's name, the
        second is the Exception object.
        The return value indicates whether to treat the exception as
        caught: True -> caught, False -> re-raise.

        No matter if the exception was caught or re-raised, the responsible
        plugin will be skipped.
        """
        for i in os.listdir(self._searchpath):
            if not os.path.isdir(i) and i.endswith(".py")   \
                    and os.path.basename(i) != "__init__.py":
                name = i[:-3]

                if self.whitelist:
                    if name not in self.whitelist:
                        logging.debug("Plugin not whitelisted, skipping: %s", name)
                        continue
                elif self.blacklist:
                    if name in self.blacklist:
                        logging.debug("Plugin blacklisted, skipping: %s", name)
                        continue

                try:
                    self.mount_plugin(name, *args, **kwargs)
                except Exception as e:
                    if exception_handler and exception_handler(name, e):
                        continue
                    raise

    def unmount_all(self, exception_handler: ExceptionCallback):
        """Unmount all plugins.

        See mount_all() on how to use exception_handler.
        """
        # Create a copy so the source dict doesn't change while iterating
        for i in list(self._plugins):
            try:
                self.unmount_plugin(i)
            except Exception as e:
                if exception_handler and exception_handler(i, e):
                    continue
                raise

    def reload_plugin(self, name):
        """Reload a plugin's config.

        This is only used for config reloading, for remounting use
        mount_plugin().
        """
        if name not in self._plugins:
            logging.warning("Trying to reload non-mounted plugin: %s", name)
        else:
            self._plugins[name].plugin.reload()
            logging.info("Plugin reloaded: %s", name)

    def iter_plugins(self):
        """Iterate through mounted plugins.

        Yields a tuple (name, plugin), where name is a string and plugin
        the plugin object.
        """
        for k, v in self._plugins.items():
            yield (k, v.plugin)

    def plugin_exists(self, name):
        return name in self._plugins

    def _load_module(self, handle, name):
        """(Re-)Loads a module from the plugin search path."""
        fname = "{}/{}.py".format(self._searchpath, name)
        try:
            handle.module = imp.load_source(name, fname)
        except:  # noqa
            handle.module = None
            raise
        logging.debug("Module loaded: %s", fname)

    @staticmethod
    def _init_plugin(handle, *argv, **kwargs):
        try:
            oldinst = handle.plugin
            handle.plugin = handle.module.Plugin(oldinst, *argv, **kwargs)
        except:  # noqa
            handle.plugin = None
            raise
