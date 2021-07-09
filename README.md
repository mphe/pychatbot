# Chatbot
A plugin based, extendable chatbot written in Python 3.

## Install

Requires Python 3.8+.

```shell
# Install required dependencies
sudo pip install -r requirements.txt
```

## Quick Start

Run the bot using `run.sh`.
At least one of `-p/--profile` or `-a/--api` has to be specified.

A profile is a configuration file located in the platform specific default
directory, e.g. `~/.config` on Linux, or `%appdata%` on windows, containing Bot
and API specific configuration, e.g. login credentials.
If the given profile does not exist, it will be created, however you also need to specify the API in this case.

Usually, in order to connect to chat protocols, you will need an account and/or a bot token to log in,
hence, specifying only an API using `-a/--api`, will most likely fail due to missing login credentials.

Currently supported chat protocols are:

* Discord
* Telegram
* ~~Tox~~

Here is an example of how to create a Discord bot.

```sh
# 1) Create a new profile with Discord API
# Will fail afterwards due to missing login credentials
./run.sh -p discordbot -a discord

# 2) Go to "~/.config/pychatbot/discordbot" and edit the "api.json" file to add the bot token.

# 3) Run the bot
./run.sh -p discordbot
```

Type `run.sh -h` for more information.



## Compatibility

* Requires Python 3.8+
* Only tested on Linux, but should theoretically work on other platforms, too.
