import discord
from discord.ext import commands
from cogs.administration import Administration
from cogs.utility import Utility
from cogs.serverutils import ServerUtils
from cogs.personality import Personality

import configparser

prefix = '%'
help_command = commands.DefaultHelpCommand(dm_help=True)
bot = commands.Bot(command_prefix=prefix, help_command = help_command)

async def setup():
    bot.add_cog(Administration(bot))
    bot.add_cog(Utility(bot))
    bot.add_cog(ServerUtils(bot))
    bot.add_cog(Personality(bot))

@bot.event
async def on_ready():
    await setup()
    print("okay three two one lets jam")

config = configparser.ConfigParser()
config.read('config.ini')
bot.run(config.get('tokens', 'DISCORD_TOKEN_0'))
