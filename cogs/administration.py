import discord
import pandas
import random
import inspect
import json
import subprocess
import pandas
from discord.ext import commands
class Administration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def bot_exec(self, ctx, str_code):
        """Takes a series of semicolon seperated statements and evaluates them."""
        results = []
        memory = []
        codes = str_code.strip('` ').split(";")
        python = '```py\n{}\n```'
        env = {
            'self' : self,
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'server': ctx.guild,
            'channel': ctx.message.channel,
            'author': ctx.author,
            'results' : results,
            'memory' : memory,
            'codes' : codes
        }

        env.update(globals())

        # handle multi-statement debugs
        for code in codes:
            try:
                result = eval(code, env)
                # async if necessary
                if inspect.isawaitable(result):
                    result = await result
                results.append(result)
                await ctx.send(str(python.format(result)))
            except Exception as e:
                await ctx.send(python.format(type(e).__name__ + ': ' + str(e)))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def debug(self, ctx, *, str_code : str):
        """Takes evaluates a series of statements."""
        await self.bot_exec(ctx, str_code)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def say(self, ctx, *, msg : str):
        """Has the bot send a message."""
        await ctx.message.delete()
        await ctx.send(msg)

def setup(bot):
    bot.add_cog(Administration(bot))
