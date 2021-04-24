import discord
from discord.ext import commands

import re
import random
import json

from os import listdir
from os.path import isfile, join

class Personality(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("lollipops.json", "r") as json_file:
            self.lollipops = json.load(json_file)
        self.lollipop_path = "lollipops/"
        self.images = [f for f in listdir(self.lollipop_path) if isfile(join(self.lollipop_path, f))]

    def dump(self):
        with open("lollipops.json", "w") as json_file:
            json.dump(self.lollipops, json_file, indent=4)

    @commands.command()
    async def fistbump(self, ctx):
        await ctx.send("https://gfycat.com/gifs/detail/snarlingdetailedeyas")

    @commands.command()
    async def baymax(self, ctx):
        linkList = [
            "https://cdn.discordapp.com/attachments/471571845200478228/503802851550691338/maxresdefault.png",
            "https://giphy.com/gifs/disney-big-hero-6-baymax-hiro-Lb3vIJjaSIQWA", "https://gfycat.com/gifs/detail/KindlyDeficientChameleon", "https://giphy.com/gifs/baymax-CQw94V8AMa556",
            "https://media.giphy.com/media/zmGpTQY8TQ2d2/giphy.gif",
            "https://media1.tenor.com/images/8d391924fac3bb2f4bf36bd910c8fb11/tenor.gif?itemid=7375013",
            "https://media1.tenor.com/images/2294960dff7049d2a3666cc65c00ecd3/tenor.gif?itemid=4086977",
            "https://media0.giphy.com/media/ma5AFexgkVBny/giphy.gif"
        ]
        link = linkList[int(random.random() * len(linkList))]
        print(int(random.random() * len(linkList)))
        await ctx.send(link)

    @commands.command(aliases=["hello", "heyo"])
    async def hi(self, ctx):
        await ctx.send("hello. i am baymax, your personal healthcare companion.")

    async def ow_processor(self, message):
        ow = re.search("\\b_*(0|o|O|\\(\\)|\\{\\}|\\[\\])+(w|W)+\\b", message.content)
        if (ow != None and message.author.id != self.bot.user.id):
            emoji_strings = ["b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10"]
            emojis = [discord.utils.get(self.bot.emojis, name=emoji_string) for emoji_string in emoji_strings]
            msg = await message.channel.send("hello, i am baymax, your personal healthcare companion. i heard a sound of distress. from a scale of 1 to 10, how would you rate your pain?")
            for emoji in emojis:
                await msg.add_reaction(emoji)
            def check(reaction, user):
                return reaction.message.id == msg.id and user.id == message.author.id
            reaction, user = await self.bot.wait_for("reaction_add", check=check)
            number = emojis.index(reaction.emoji) + 1
            if number > 1:
                if not str(message.author.id) in self.lollipops:
                    self.lollipops[str(message.author.id)] = 0
                await message.channel.send("here, have {0} lollipops to help you cope with the pain.".format(str(number)))
                self.lollipops[str(message.author.id)] += number
                self.dump()
            else:
                await message.channel.send("thats good to hear. have a lollipop anyways for good luck")

    @commands.command()
    async def nom(self, ctx):
        person = str(ctx.message.author.id)
        if not person in self.lollipops or self.lollipops[person] == 0:
            await ctx.send("you don't have any lollipops :(")
            return
        self.lollipops[person] -= 1
        self.dump()
        number = self.lollipops[person]
        if number == 0:
            del self.lollipops[person]

        with open(self.lollipop_path + random.choice(self.images), "rb") as image:
            await ctx.send(f"nom! you have {number} lollipops left", file = discord.File(image))

    async def satisfaction_processor(self, message):
        if "satisfied with my care" in message.content and await self.bot.is_owner(message.author):
            await message.channel.send("goodbye.")
            await self.bot.logout()

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.ow_processor(message)
        await self.satisfaction_processor(message)

