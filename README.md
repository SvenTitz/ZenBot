I created this bot from a Template. Credit to https://github.com/kkrypt0nn/Python-Discord-Bot-Template

## Disclaimer
I have no idea what I'm doing in python and this is a hobby project. Please don't judge me too hard.

## Set it up for yourself
If you want to run a local test version of this bot you'll have to prepare a few things.
1. Create a the Discord Bot Account [here](https://discord.com/developers/applications)
2. Generate a Clash of Clans API key [here](https://developer.clashofclans.com/#/)
3. Set up a Google Developer Service Account as discribed [here](https://docs.gspread.org/en/v5.7.1/oauth2.html)

After that you can clone the project. Once you've done that, you'll have to:
1. copy the "config.example.json" file and rename it to "config.json". Afterwards fill in the information.
2. run ` python -m pip install -r requirements.txt ` to install all required packages
3. run ` python bot.py ` to start the bot

## About the code
Like I said, I copied a [template](https://github.com/kkrypt0nn/Python-Discord-Bot-Template) for a python discord bot, so the only things I've added are the Clash of Clans related commands. If you want to learn more about how the bot itself works, check out the templates github page. I am only slowly figuring it out myself.

Quick rundown of the structure:
- `bot.py` is the main class, where the base bot is set up. I did nothing here.
- Commands are added via [cogs](https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html). and located in the /cogs folder.
  - the tempalte came with a lot of exemplary commands that I've mostly moved to /cogs/unused
- /services contains the clash api service and the spreadsheet api service, which are doing most of the work currently.
  -  [gspread](https://docs.gspread.org/en/v5.7.1/) is used for interacting with google spreadsheets.
  -  Plain old http request are used for the Clash API. Those are wrapped in the `/clients/coc_api.py` file.


## Questeions?
Feel free to contact me on discrod ".cuba" (I have one of the new usernames without #1234 already)
