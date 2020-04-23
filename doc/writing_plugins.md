# Writing Plugins
## Basic structure

Create a new file "myplugin.py" and add this snippet:

```python
# -*- coding: utf-8 -*-

from chatbot.bot import BotPlugin


class Plugin(BotPlugin):
    def __init__(self, oldme, bot):
        super(Plugin, self).__init__(oldme, bot)
```

This is the basic structure of a plugin.
Note that your plugin class must be called "Plugin", otherwise it can't be loaded.
The `bot` parameter in `__init__` is a reference to the Bot instance that loaded this plugin.
`oldme` is either `None` or the previous instance of your plugin, after it was reloaded. It can be used to move data over to the new instance.

The `BotPlugin` base class provides a bunch of functions for registering/unregistering commands, loading configs, and hooking/unhooking event handlers.

To get the Bot instance, the plugin name, and the config dict there are respective functions: `bot()`, `name()`, and `cfg()`.


## Adding commands

The `BotPlugin` class provides wrappers for common functions like adding commands or hooking events. You can read the usage instructions in the respective docstrings.

Here's how it looks like:

```
def __init__(self, oldme, bot):
    super(Plugin, self).__init__(oldme, bot)
    self.register_command("echo", self._echo)

def _echo(self, msg, argv):
    msg.reply(" ".join(argv[1:]))
```

The base class keeps track of registered commands and unregisters them automatically when the plugin is unloaded.

### Documentation
Every command should have a docstring in the following format:
```
Syntax: mycommand <arg1> [arg2] [arg3]

Description.
```

The builtin `help` command can then read the docstring and print it to the user.
For the above example it would look like this:

```python
def _echo(self, msg, argv):
    """Syntax: echo <text> [moretext]...

    Prints the given text in the chat.
    """
    msg.reply(" ".join(argv[1:]))
```

### Command-missing handlers

In case a user entered a non-existing command, there can be special command-missing handlers that will be called in such a case.

To declare a command as missing-handler, simply set the CMDFLAG_MISSING flag.
Unregistering is the same as for normal commands, therefore you should prefix your missing-handlers with a special prefix to avoid possible ambiguity.
Even though a missng-handler is registered with a name, it can't be called explicitely.

Here's an example:

```python
from chatbot.bot.subsystem import command

def __init__(self, oldme, bot):
    super(Plugin, self).__init__(oldme, bot)
    self.register_command("missing_test", self._handler,
                          argc=0, flags=command.CMDFLAG_MISSING)

def _handler(self, msg, argv):
    if argv[0] != "handled":
        raise command.CommandError(command.COMMAND_ERR_NOTFOUND)
```

If a missing-handler returns nothing, it's assumed, that it handled the input and no further handlers should be called.
Raising COMMAND_ERR_NOTFOUND or COMMAND_ERR_ARGC indicate that the command was not handled and the next handle should be executed.



## Hooking events

To register an event handler, the `BotPlugin` class provides a wrapper function `register_event_handler()`. It takes 2 arguments: the first one is the event ID defined in `api.APIEvents` and the second is the callback. The callback signature for the respective events can be found in the `api.APIEvents` \*module\*. Optionally you can also pass a third parameter that indicates the priority of your handler. Small values are called first, high values later. For readability there are some predefined priorities: `event.EVENT_PRE`, `event.EVENT_NORMAL`, and `event.EVENT_POST`.
To stop the event execution, e.g. when your handler handled the event and no further handlers should be called, you can return `event.EVENT_HANDLED`.

For example, this will hook the "message received" event:
```python
from chatbot.bot import BotPlugin
from chatbot.api import APIEvents
from chatbot.util import event

class Plugin(BotPlugin):
    def __init__(self, oldme, bot):
        super(Plugin, self).__init__(oldme, bot)
        self.register_event_handler(APIEvents.Message, self._on_message)

    def _on_message(self, msg):
        if msg.get_text() == "handled":
            return event.EVENT_HANDLED
```

The `BotPlugin` will automatically unregister the event hook when the plugin is unloaded.


## Loading and storing configs

`BotPlugin`  will automatically load the respective config file when instantiated. It also provides a `reload` function that (re-)loads the config file.

All it needs is a static method `get_default_config` that returns the default config values.
Note that it must be a `@staticmethod`, otherwise it won't work.

Example:
```python
class Plugin(BotPlugin):
    def __init__(self, oldme, bot):
        super(Plugin, self).__init__(oldme, bot)

    @staticmethod
    def get_default_config():
        return {
            "some_option": 42,
            "more_options": "foobar",
            "some_array": [ "Hello World", "This is a test" ],
        }
```
The `get_default_config` method is optional and only needed if the plugin makes use of config files.
It can be safely removed if no config is required.


`Bot` holds a config manager object that can be retrieved using the `get_configmgr()` function. For further information on how to use it, see its docstrings at `chatbot.bot.subsystem.ConfigManager`.

The config manager will load/store configs in json format. It will automatically translate the given filename to the respective path on the filesystem. When a default config is given, it will also merge any non-existing keys into the loaded config.
Using `load_update()` or `load(write=True)` will update the file by rewriting it. This is useful to keep the config file up-to-date when new keys are added.

Usually it is not necessary to query configs manually, only if the plugin requires a special way of loading its config. `BotPlugin` internally uses respective config manager functions with the plugin's module name as filename to load and store config files.
