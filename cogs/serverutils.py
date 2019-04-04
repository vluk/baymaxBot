import discord
from discord.ext import commands

import re

class ServerUtils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_string_carots(self, content):
        if content == discord.Embed.Empty:
            return 0
        reg_num_match = re.search("\\d+\\^", content)
        num_count = 0
        if reg_num_match != None:
            num_count = int(content[reg_num_match.span()[0]:reg_num_match.span()[1]-1])
            if num_count > 2000:
                num_count = 0
        reg_con_match = re.search("(\\^)+", content)
        con_count = 0
        if reg_con_match != None:
            con_count = reg_con_match.span()[1] - reg_con_match.span()[0]
        return max(num_count, con_count)

    async def get_message_carots(self, message):
        embed_carots = 0
        if len(message.embeds) > 0:
            embed_carots = await self.get_string_carots(message.embeds[0].description)
        content_carots = await self.get_string_carots(message.content)
        return max(embed_carots, content_carots)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:  
            pass
        nextContent = ""
        limit = await self.get_message_carots(message) + 1
        current = 1
        async for new_message in message.channel.history(limit = 2000):
            last = new_message
            if limit <= current:
                limit += await self.get_message_carots(new_message)
                if limit <= current:
                    break
            current += 1
        description = last.clean_content
        if (len(last.clean_content) == 0
            and len(last.embeds) > 0
            and last.embeds[0].description != discord.Embed.Empty):
            description += last.embeds[0].description
        embed = discord.Embed(
            description = description,
            timestamp = last.created_at,
            color = last.author.colour
        )
        if len(last.embeds) > 0 and last.embeds[0].type == "image":
            embed.set_image(url=last.embeds[0].thumbnail.url)
        elif len(last.attachments) > 0:
            embed.set_image(url=last.attachments[0].url)
        url = "https://discordapp.com/channels/{0}/{1}/{2}".format(last.guild.id, last.channel.id, last.id)
        embed.set_author(name=last.author.display_name, url = url, icon_url = last.author.avatar_url)
        if current > 3:
            await message.channel.send(embed=embed)
