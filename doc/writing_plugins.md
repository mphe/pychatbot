# Writing Plugins

## Searchpath

The default plugin searchpath is `chatbot/bot/plugins/`.
The filenames act as a unique identifier to identify each plugin.
Only directories and `.py` files are considered. All files starting with a `.` or `_` are ignored.

A plugin can be contained in a singular `.py` file or in a package.
When provided as package, a directory must be created containing an `__init__.py` file.

The plugin's main entry-point is a class named `Plugin` which must be defined in the plugin's `.py` or `__init__.py` file and inherit from `bot.BotPlugin`.

## Basic structure

Create a new file "myplugin.py" and add this snippet:

```python
# -*- coding: utf-8 -*-

from typing import List
from chatbot import bot, api
from .subsystem.async_plugin import BasePlugin


class Plugin(bot.BotPlugin):
    def __init__(self, bot: bot.Bot):
        super().__init__(bot)

    async def init(self, old_instance) -> bool:
        # Initialization _before_ loading configs
        return await super().init()

    async def reload(self) -> None:
        await super().reload()
        # Initialization _after_ loading configs

    async def _on_ready(self) -> None:
        await super()._on_ready()
        # Called after the API became ready or, if it already is, after reload() finished.

    async def quit(self) -> None:
        # Cleanup
        await super().quit()
```

This is the basic structure of a plugin, however, you will only need to overwrite `__init__()` and `reload()` in most cases.
Note that your plugin class must be called "Plugin", otherwise it can't be loaded.
The `bot` parameter in `__init__` is a reference to the Bot instance loading this plugin.
`old_instance` in `init()` is either `None` or the previous instance of your plugin if it was reloaded. It can be used to move data over to the new instance.

The `BotPlugin` base class provides a bunch of functions for registering/unregistering commands, loading configs, and hooking/unhooking event handlers.

To get the Bot instance, the plugin name, and the config, there are respective properties: `bot`, `name`, and `cfg`.


## Adding commands

The `BotPlugin` class provides wrappers for registering commands or hooking events and unregisters them automatically when the plugin is unloaded.

Here's how it looks like:

```python
def __init__(self, bot: bot.Bot):
    super().__init__(bot)
    self.register_command("echo", self._echo)

async def _echo(self, msg: api.ChatMessage, argv: List[str]):
    await msg.reply(" ".join(argv[1:]))
```

Note that command callbacks must be coroutines.



### Documentation

Every command should have a docstring in the following format:
```python
"""Syntax: mycommand <arg1> [arg2] [arg3]

Description.
"""
```

The builtin `help` command reads the docstring and prints it to the user.
For the above example it would look like this:

```python
async def _echo(self, msg: api.ChatMessage, argv: List[str]):
    """Syntax: echo <text> [moretext]...

    Prints the given text in the chat.
    """
    await msg.reply(" ".join(argv[1:]))
```

### Command-missing handlers

Command-missing handlers are special commands that are called when a user entered a non-existing command.

To register a command-missing handler, simply set the `CommandFlag.Missing` flag.
Even though a missng-handler is registered with a name, it can't be called explicitely.
Make sure to give missing-handlers a unique name to avoid ambiguity, as they're still treated as commands.

Here's an example:

```python
from chatbot.bot.subsystem import command

def __init__(self, bot: bot.Bot):
    super().__init__(bot)
    self.register_command("missing_test", self._handler,
                          argc=0, flags=command.CommandFlag.Missing)

async def _handler(self, msg: api.ChatMessage, argv: List[str]):
    if argv[0] != "handled":
        raise command.CommandNotFoundError
```

If a missing-handler returns nothing, it's assumed, that it handled the input and no further handlers should be called.
Raising `CommandNotFoundError` or `CommandArgcError` indicates the command was not handled and the next handler should be executed.



## Hooking events

`BotPlugin` provides a wrapper function `register_event_handler()` and automatically unregisters the event hook when the plugin is unloaded.
`register_event_handler()` takes 2 arguments: the event ID defined in `api.APIEvents` and a callback.
The callback signature for the respective events can be found in the `api.APIEvents` module. Note that callbacks must be coroutines.
Optionally you can also pass a third parameter that indicates the priority of your handler. Small values are called first, high values later. For readability there are some predefined priorities: `event.EVENT_PRE`, `event.EVENT_NORMAL`, and `event.EVENT_POST`.
To stop the event execution, e.g. when your handler handled the event and no further handlers should be called, you can return `event.EVENT_HANDLED`.


For example, this will hook the "message received" event:
```python
from chatbot.util import event

def __init__(self, bot: bot.Bot):
    super().__init__(bot)
    self.register_event_handler(api.APIEvents.Message, self._on_message)

async def _on_message(self, msg: api.ChatMessage):
    if msg.text == "handled":
        return event.EVENT_HANDLED
```


## Loading and storing configs

`BotPlugin` provides a `reload()` function that (re-)loads the respective config file when called.
It is called automatically in `init()` (not `__init__()`) when the plugin is initialized.
Hence, if you need to perform initialization based on config entries, you should do that by overriding `reload()`.

The config object can be accessed using the `cfg` property.
All configs are stored as json files.

The `get_default_config` function should return the default config dict.
Note that it must be a `@staticmethod`, otherwise it won't work.
If not manually handled otherwise, the default dict gets recursively merged into the loaded config to ensure all keys are present.

Example:
```python
import logging

async def reload(self) -> None:
    await super().reload()
    logging.info(self.cfg["some_option"])

@staticmethod
def get_default_config():
    return {
        "some_option": 42,
        "more_options": "foobar",
        "some_array": [ "Hello World", "This is a test" ],
    }
```
