# baymaxBot

A bot for the messaging service Discord written in Python that simulates users using recurrent neural networks implemented using TensorFlow.

## Getting Started

If you have a Discord server, you can invite the bot using [this invite link.](https://discordapp.com/oauth2/authorize?client_id=563436071950614546&scope=bot). This is the recommended course of action. If you want to run the bot on your own Linux server, here are the instructions.

### Prerequisites

Aside from the Python packages listed in `requirements.txt`, you will need:
```
Python >= 3.5
```
[Downloading Python](https://wiki.python.org/moin/BeginnersGuide/Download)

### Installing

First, clone the repository.
```
git clone git@github.com:vluk/baymaxBot.git
```
Next, go into the directory.
```
cd baymaxBot
```
Next, download all the necessary Python packages.
```
pip3 install -r requirements.txt
```
Make a `config.ini` file in the root directory and put a [Discord bot token.](https://discordapp.com/developers/docs/intro).
Example:
```
[tokens]
DISCORD_TOKEN_0: [your token here]
```
The bot should now be ready.

### Usage

To run the bot, just type in the root directory
```
python3 bot.py
```

Invite the bot to a [server](https://github.com/jagrosh/MusicBot/wiki/Adding-Your-Bot-To-Your-Server), then type in ?help for a list of the functions the bot has.
