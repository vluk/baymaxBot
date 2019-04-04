import discord
from discord.ext import commands

import aiohttp
import urllib
from dateutil import parser
import datetime
import random

class Dictionary(commands.Cog):
    def __init__(self, bot, session):
        self.bot = bot
        self.session = session

    async def get_define(self, term):
        response = {}
        async with self.session.get("https://googledictionaryapi.eu-gb.mybluemix.net/?define=" + term) as resp:
            json_response = await resp.json()
            response = json_response
        embed = discord.Embed(
            title = "{0}".format(response["word"]),
            description = "{0}".format(""),
            url = "https://www.google.com/search?q=define%20" + urllib.parse.quote(term, safe=""),
            timestamp = datetime.datetime.now(),
            colour = [0x4285F4, 0xDB4437, 0xF4B400, 0x0F9D58][int(random.random() * 4)]
        )
        embed.set_author(
            name="Google",
            url="https://www.google.com",
            icon_url="http://www.stickpng.com/assets/images/5a951939c4ffc33e8c148af2.png"
        )
        for part in response["meaning"]:
            enum_defs = enumerate(response["meaning"][part], 1)
            list_defs = ["{0}. {1}\n*\"{2}\"*".format(i[0], i[1]["definition"], i[1]["example"])
                if "example" in i[1] else "{0}. {1}\n".format(i[0], i[1]["definition"]) for i in enum_defs]
            defs = "\n".join(list_defs)
            embed.add_field(name="*{0}*".format(part), value=defs)
        return embed

    async def get_udefine(self, term):
        dict_def = {}
        url = "https://api.urbandictionary.com/v0/define?term={0}".format(urllib.parse.quote(term, safe=""))
        async with self.session.get(url) as resp:
            dict_def = await resp.json()
        full_definition = ""

        if len(dict_def["list"]) == 0:
            await bot.say("`None found!`")
            return
        definition = (dict_def["list"][0]["definition"])
        example = (dict_def["list"][0]["example"])

        definition = definition.replace("\\", "\\\\")
        definition = definition.replace("*", "\\*")
        definition = definition.replace("_", "\\_")
        definition = definition.replace("~", "\\~")
        definition = definition.replace("[", "")
        definition = definition.replace("]", "")

        example = example.replace("\\", "\\\\")
        example = example.replace("*", "")
        example = example.replace("_", "\\_")
        example = example.replace("~", "\\~")
        example = example.replace("[", "")
        example = example.replace("]", "")

        full_definition += definition
        full_definition += "\n\n"
        full_definition += "*" + example.strip() + "*"


        if (len(full_definition) + len(term) < 2000):
            embed = discord.Embed(
                color = 0xFF8C00,
                title = dict_def["list"][0]["word"],
                description = full_definition,
                url = dict_def["list"][0]["permalink"],
                timestamp = parser.parse(dict_def["list"][0]["written_on"])
            )
            embed.set_author(
                name = "Urban Dictionary",
                icon_url = "http://www.packal.org/sites/default/files/public/styles/icon_large/public/workflow-files/florianurban/icon/icon.png?itok=sMaOFyEA",
                url = "https://www.urbandictionary.com/"
            )

            embed.set_footer(
                text = "Submitted by " + dict_def["list"][0]["author"]
            )

            return embed
        else:
            embed = discord.Embed(
                color = 0xFF8C00,
                title = dict_def["list"][0]["word"],
                description = full_definition[:1990] + "[...]",
                url = dict_def["list"][0]["permalink"],
                timestamp = parser.parse(dict_def["list"][0]["written_on"])
            )
            embed.set_author(
                name = "Urban Dictionary",
                icon_url = "http://www.packal.org/sites/default/files/public/styles/icon_large/public/workflow-files/florianurban/icon/icon.png?itok=sMaOFyEA",
                url = "https://www.urbandictionary.com/"
            )

            embed.set_footer(
                text = "Submitted by " + dict_def["list"][0]["author"]
            )

            return embed

    @commands.command(aliases=["d"])
    async def define(self, ctx, *, term : str):
        def_embed = await self.get_define(term)
        await ctx.send(embed=def_embed)

    @commands.command(aliases=["ud"])
    async def udefine(self, ctx, *, term : str):
        def_embed = await self.get_udefine(term)
        await ctx.send(embed=def_embed)
