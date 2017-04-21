# Chatbot
A plugin based, extendable chatbot written in Python.

## Requirements
The following python modules are required and can be installed using pip:

```shell
pip install appdirs sortedcontainers
```

Additionally you will need the python bindings for the chat protocols you want to use.<br>
Currently only Tox is supported.

**Tox:** pytoxcore ([this fork](https://github.com/mphe/pytoxcore))


## Compatibility

Fully compatible with Python 3.<br>
Theoretically compatible with Python 2, but only partially tested.

Only tested on Linux, but should theoretically work on other platforms, too.


## Todo
* Add more documentation
* Support more chat protocols
* Internal:
    * Keep the last loaded version of a plugin if reloading fails
    * Create a PluginError exception
