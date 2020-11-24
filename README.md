# Chatbot
A plugin based, extendable chatbot written in Python.

## Requirements

Requires Python 3.8.

Install dependencies:
```shell
# pip install -r requirements.txt
```

Install optional dependencies needed by plugins and APIs:
```shell
# pip install -r requirements_optional.txt
```

Additionally you will need python bindings for the chat protocols you want to use.

* **Discord:**
    ```
    # pip install discord.py==1.3.3
    ```
* **Tox:** No longer supported

## Usage

Run the bot using `run.sh`.

Type `run.sh -h` for more information.

## Compatibility

* Requires Python 3.8
* Only tested on Linux, but should theoretically work on other platforms, too.
