# -*- coding: utf-8 -*-

import sys
import os
import importlib.util
import importlib.machinery
import logging
from typing import Callable, Dict, Iterable, Tuple, Any
from dataclasses import dataclass
from pathlib import Path


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
    def __init__(self, searchpath: str, whitelist: Iterable[str] = None, blacklist: Iterable[str] = None):
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
        self._searchpath = Path(searchpath)
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

        Only directories and *.py files are considered. All files starting with a '.' or '_' are ignored.
        However, they can be mounted with a direct call to mount_plugin().

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
        for i in self._searchpath.iterdir():
            # Filter hidden files
            if i.name.startswith("_") or i.name.startswith("."):
                continue

            # Filter unrelated files
            if not i.name.endswith(".py") and not i.is_dir():
                continue

            plugin_name = i.name[:-3] if i.name.endswith(".py") else i.name

            if self.whitelist:
                if plugin_name not in self.whitelist:
                    logging.debug("Plugin not whitelisted, skipping: %s", plugin_name)
                    continue
            elif self.blacklist:
                if plugin_name in self.blacklist:
                    logging.debug("Plugin blacklisted, skipping: %s", plugin_name)
                    continue

            try:
                await self.mount_plugin(plugin_name, *args, **kwargs)
            except Exception as e:
                if exception_handler and exception_handler(plugin_name, e):
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

        dir_path = self._searchpath / name
        py_path = dir_path.with_suffix(".py")

        if py_path.is_file():
            fname = py_path
        elif dir_path.is_dir():
            fname = dir_path / "__init__.py"
        else:
            raise ImportError("Plugin not found")

        logging.debug("Loading module: %s", fname)
        module = load_source(name, str(fname))

        logging.debug("Creating plugin instance: %s", name)
        plugin = module.Plugin(*args, **kwargs)

        return PluginHandle(plugin, module)


def load_source(modname: str, filename: str) -> Any:
    """Replacement for imp.load_source() for Python 3.12 compatibility. See also https://docs.python.org/3/whatsnew/3.12.html#imp."""
    loader = importlib.machinery.SourceFileLoader(modname, filename)
    spec = importlib.util.spec_from_file_location(modname, filename, loader=loader, submodule_search_locations=[])
    module = importlib.util.module_from_spec(spec)
    sys.modules[module.__name__] = module  # Register the module to cache it and to make it work with the inspect module.
    loader.exec_module(module)
    return module
