# Adding new APIs

To add support for a new chat API, you have to create a new module in `chatbot.api` that implements all necessary API base classes.

## Setup

Go into `chatbot/api/` and create a new folder for your API.<br>
In this example a new API called "coolapi" will be created. Therefore we create a new folder called "coolapi".

## Main class

The main API class should be derived from `chatbot.api.APIBase` and implement all necessary functions. It provides the entry point for your API.

This is a simple example of the basic structure of your main class:

```python
from chatbot import api

class CoolAPI(api.APIBase):
    def __init__(self, api_id, stub, opts):
        super(CoolAPI, self).__init__(api_id, stub)
        self._opts = opts

    @staticmethod
    def get_default_options():
        return {
            "cool_option": 42,
        }
```

It is important to call the `APIBase` constructor with the supplied arguments `api_id` and `stub`.<br>
The third parameter `opts` are the options passed to your API. They are based on `get_default_options()` with user supplied options merged into it.

If `get_default_options()` is not implemented, the default one will be used, which returns an empty dictionary.
Also note that `get_default_options()` **must** be static.

The remaining functions, properties, and classes are pretty much self explanatory and have docstrings explaining their purpose and requirements (see `APIBase`).<br>
Functions/Properties that have to be implemented will raise `NotImplementedError` by default.<br>

### Make it accessible
There is now a file `CoolAPI.py` in `chatbot.api.coolapi` that contains the main class.<br>

`api.create_api_object()` will look for a class named `API`, hence you need to include your main class in your package as `API`.

To do that, create another file `__init__.py` and add the following line:

```python
from .CoolAPI import CoolAPI as API
```

## Events

TODO
