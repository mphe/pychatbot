# -*- coding: utf-8 -*-

import os
import imp
import logging
from typing import Callable, Dict, Iterable, Tuple
from dataclasses import dataclass

ExceptionCallback = Callable[[str, Exception], bool]


class BasePlugin:
    """Base class for plugins."""

    async def init(self, _old_instance: "BasePlugin") -> bool:
        """Initialize the plugin.

        If the plugin was remounted, then `old_instance` is the old instance of
        this plugin, otherwise None. This is useful to exchange data from the
        old instance to the new one before it gets deleted.
        """
        raise NotImplementedError

    async def quit(self):
        """Will be called when a plugin is unmounted."""
        raise NotImplementedError


@dataclass
class PluginHandle:
    plugin: BasePlugin = None
    module: object = None

    def __bool__(self) -> bool:
        return self.plugin is not None and self.module is not None


# @dataclass
# class PluginHandle:
#     def __init__(self):
#         self._plugin: BasePlugin = None
#         self._module: object = None
#
#     def get_plugin(self) -> BasePlugin:
#         return self._plugin
#
#     def get_module(self) -> object:
#         return self._module
#
#     def load
#
#     def __bool__(self) -> bool:
#         return self._plugin is not None and self._module is not None


class PluginManager:
    def __init__(self, searchpath, whitelist: Iterable[str] = None, blacklist: Iterable[str] = None):
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
        self.blacklist = set(blacklist if blacklist else [])
        self.whitelist = set(whitelist if whitelist else [])
        self._plugins: Dict[str, PluginHandle] = {}
        os.makedirs(searchpath, exist_ok=True)

    async def mount_plugin(self, name: str, *args, **kwargs):
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
        oldplugin = None

        if old_handle := self._plugins.get(name, None):
            oldplugin = old_handle.plugin
            await self.unmount_plugin(name)

        new_handle = self._load_plugin(name, *args, **kwargs)
        await new_handle.plugin.init(oldplugin)
        self._plugins[name] = new_handle
        logging.info("Plugin (re-)mounted: %s", name)

    async def unmount_plugin(self, name: str):
        """Unmount a plugin.

        The plugin is guaranteed to be removed, even if an exception occurs.
        Exceptions will be re-raised.
        """
        handle = self._plugins.get(name, None)

        if handle is None:
            logging.warning("Trying to unmount non-mounted plugin: %s", name)
        else:
            try:
                await handle.plugin.quit()
            finally:
                del self._plugins[name]
                logging.info("Plugin unmounted: %s", name)

    async def mount_all(self, exception_handler: ExceptionCallback, *args, **kwargs):
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
                    await self.mount_plugin(name, *args, **kwargs)
                except Exception as e:
                    if exception_handler and exception_handler(name, e):
                        continue
                    raise

    async def unmount_all(self, exception_handler: ExceptionCallback):
        """Unmount all plugins.

        See mount_all() on how to use exception_handler.
        """
        # Create a copy so the source dict doesn't change while iterating
        for i in list(self._plugins):
            try:
                await self.unmount_plugin(i)
            except Exception as e:
                if exception_handler and exception_handler(i, e):
                    continue
                raise

    def iter_plugins(self) -> Iterable[Tuple[str, BasePlugin]]:
        """Iterate through mounted plugins.

        Yields a tuple (name, plugin), where name is a string and plugin
        the plugin object.
        """
        for k, v in self._plugins.items():
            yield (k, v.plugin)

    def plugin_exists(self, name: str):
        return name in self._plugins

    def _load_plugin(self, name: str, *args, **kwargs) -> PluginHandle:
        """Loads a module from the plugin search path and instantiates it."""
        fname = f"{self._searchpath}/{name}.py"

        logging.debug("Loading module: %s", fname)
        module = imp.load_source(name, fname)

        logging.debug("Creating plugin instance: %s", name)
        plugin = module.Plugin(*args, **kwargs)

        return PluginHandle(plugin, module)
