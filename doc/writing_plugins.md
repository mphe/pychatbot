# Writing Plugins
## Basic structure

Create a new file "myplugin.py" and add this snippet:

```python
# -*- coding: utf-8 -*-

from typing import List
from chatbot import bot, api


class Plugin(bot.BotPlugin):
    def __init__(self, oldme: "Plugin", bot: bot.Bot):
        super(Plugin, self).__init__(oldme, bot)

    def quit(self):
        # Custom cleanup here
        super(Plugin, self).quit()
```

This is the basic structure of a plugin.
Note that your plugin class must be called "Plugin", otherwise it can't be loaded.
The `bot` parameter in `__init__` is a reference to the Bot instance loading this plugin.
`oldme` is either `None` or the previous instance of your plugin, if it was reloaded, and can be used to move data over to the new instance.

The `BotPlugin` base class provides a bunch of functions for registering/unregistering commands, loading configs, and hooking/unhooking event handlers.

To get the Bot instance, the plugin name, and the config, there are respective properties: `bot`, `name`, and `cfg`.


## Adding commands

The `BotPlugin` class provides wrappers for registering commands or hooking events and unregisters them automatically when the plugin is unloaded.

Here's how it looks like:

```
def __init__(self, oldme: "Plugin", bot: bot.Bot):
    super(Plugin, self).__init__(oldme, bot)
    self.register_command("echo", self._echo)

async def _echo(self, msg: api.ChatMessage, argv: List[str]):
    await msg.reply(" ".join(argv[1:]))
```

Note that command callbacks must be coroutines.



### Documentation
Every command should have a docstring in the following format:
```
Syntax: mycommand <arg1> [arg2] [arg3]

Description.
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

def __init__(self, oldme: "Plugin", bot: bot.Bot):
    super(Plugin, self).__init__(oldme, bot)
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

def __init__(self, oldme: "Plugin", bot: bot.Bot):
    super(Plugin, self).__init__(oldme, bot)
    self.register_event_handler(api.APIEvents.Message, self._on_message)

async def _on_message(self, msg: api.ChatMessage):
    if msg.text == "handled":
        return event.EVENT_HANDLED
```


## Loading and storing configs

`BotPlugin` automatically loads the respective config file when instantiated. It also provides a `reload` function that (re-)loads the config file.
The config object can be accessed using the `BotPlugin.cfg` property.
All configs are stored as json files.

The `get_default_config` function should return the default config dict.
Note that it must be a `@staticmethod`, otherwise it won't work.
If not manually handled otherwise, the default dict gets recursively merged into the loaded config to ensure all keys are present.

Example:
```python
import logging

def __init__(self, oldme: "Plugin", bot: bot.Bot):
    super(Plugin, self).__init__(oldme, bot)

    logging.info(self.cfg["some_option"])

@staticmethod
def get_default_config():
    return {
        "some_option": 42,
        "more_options": "foobar",
        "some_array": [ "Hello World", "This is a test" ],
    }
```
