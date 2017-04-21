# Writing Plugins
## Basic structure

Create a new file "myplugin.py" and add this snippet:

```python
# -*- coding: utf-8 -*-

from chatbot.bot.subsystem.plugin import BasePlugin
from chatbot.compat import *


class Plugin(BasePlugin):
    def __init__(self, oldme, bot):
        self._bot = bot

    def reload(self):
        # Reload configs here
        pass

    def quit(self):
        # Do cleanup
        pass
```

This is the basic structure of a plugin.
Note that your plugin class must be called "Plugin", otherwise it can't be loaded.
The `bot` parameter in `__init__` is a reference to the Bot instance that loaded this plugin.
`oldme` is either `None` or the previous instance of your plugin, after it was reloaded. It can be used to move data over to the new instance.
For further information on what these functions do, you can read the docstrings of `chatbot.bot.subsystem.plugin.Plugin`.

## Adding commands

The Bot class provides wrappers for common functions like adding commands or hooking events. You can read the usage instructions in the respective docstrings.

Here's how it looks like:

```
def __init__(self, oldme, bot):
    self._bot = bot
    self._bot.register_command("echo", self._echo)

def quit(self):
    self._bot.unregister_command("echo")

def _echo(self, msg, argv):
    msg.reply(" ".join(argv[1:]))
```

It's important to unregister all commands in `quit()`, otherwise they will stay
in memory even after the plugin was unloaded.

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

Here's an example (shortened):

```python
from chatbot.bot.subsystem import command

def __init__(self, oldme, bot):
    self._bot.register_command("missing_test", self._handler,
                               argc=0, flags=command.CMDFLAG_MISSING)

def quit(self):
    self._bot.unregister_command("missing_test")

def _handler(self, msg, argv):
    if argv[0] != "handled":
        raise command.CommandError(command.COMMAND_ERR_NOTFOUND)
```

If a missing-handler returns nothing, it's assumed, that it handled the input and no further handlers should be called.
Raising COMMAND_ERR_NOTFOUND or COMMAND_ERR_ARGC indicate that the command was not handled and the next handle should be executed.




## Hooking events

To register an event handler, the Bot class provides a function `register_event_handler()`. It takes 2 arguments: the first one is the event ID defined in `api.APIEvents` and the second is the callback. The callback signature for the respective events can be found in the `api.APIEvents` *module*. Optionally you can also pass a third parameter that indicates the priority of your handler. Small values are called first, high values later. For readability there are some predefined priorities: `event.EVENT_PRE`, `event.EVENT_NORMAL`, and `event.EVENT_POST`.
To stop the event execution, e.g. when your handler handled the event and no further handlers should be called, you can return `event.EVENT_HANDLED`.

For example, this will hook the "message received" event:
```python
TODO

```

Again, it's important to unregister all event handlers in `quit()`.

## Loading and storing configs

Bot holds a config manager objects that can be retrieved using the `get_configmgr()` function. For further information on how to use it, see its docstrings at `chatbot.bot.subsystem.ConfigManager`.

Adding config support in a plugin is fairly easy. Here is how it's done:

```python
def __init__(self, oldme, bot):
    self._bot = bot
    self._bot.register_command("say", self._say, argc=0)
    self._config = {}
    self.reload()

def reload(self):
    self._config = self._bot.get_configmgr().load_update("sayplugin", {
        "answers": [ "Hello World", "This is a test" ],
        "moreoptions": True,
        "evenmoreoptions": 5,
    })

def _say(self, msg, argv):
    msg.reply(random.choice(self._config["answers"]))
```

The config manager will load/store configs in json format. It will automatically translate the given filename ("sayplugin") to the respective path on the filesystem. When a default config is given (second parameter), it will also merge any non-existing keys into the loaded config.
Using `load_update()` or `load(write=True)` will update the file by rewriting it. This is useful to keep the config file up-to-date when new keys are added. As far as useful, this should be preferred over normal loading.
