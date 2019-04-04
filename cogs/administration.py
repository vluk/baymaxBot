import discord
import inspect
import subprocess
from discord.ext import commands

class Administration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def bot_exec(self, ctx, str_code):
        results = []
        memory = []
        codes = str_code.strip('` ').split(";")
        python = '```py\n{}\n```'
        env = {
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

        for code in codes:
            try:
                result = eval(code, env)
                if inspect.isawaitable(result):
                    result = await result
                results.append(result)
                await ctx.send(str(python.format(result)))
            except Exception as e:
                await ctx.send(python.format(type(e).__name__ + ': ' + str(e)))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def logout(self, ctx):
        await ctx.bot.logout()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def debug(self, ctx, *, str_code : str):
        await self.bot_exec(ctx, str_code)
