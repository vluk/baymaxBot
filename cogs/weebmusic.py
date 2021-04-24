import discord
from discord.ext import commands

import asyncio
import random
import youtube_dl

from collections import deque

import re
from bs4 import BeautifulSoup

import functools

ANILIST_API = 'https://graphql.anilist.co'
ANILIST_QUERY = '''query GetAnimeList($name: String) {MediaListCollection(userName: $name, type: ANIME) {
    lists {
        entries{
            media{
                idMal
                seasonYear
                title {
                    romaji
                    english
                }
                synonyms
                coverImage {
                    extraLarge
                }
            }
        }
    }
}}'''

wiki = "https://www.reddit.com/r/AnimeThemes/wiki/"

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLError(Exception):
    pass

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def create_source(cls, search: str, loop: asyncio.BaseEventLoop = None, stream=False):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))

        return cls(discord.FFmpegPCMAudio(info['url'], **ffmpeg_options), data=info)

class WeebGame():
    def __init__(self, guild_id):
        self.guild_id = guild_id

        self.lists = {}
        self.length = 0

        self.scores = {}
        self.players = {}
        self.total = 0
        self.rounds = 0

    def get_length(self):
        total = set()
        for i in self.lists:
            ids = [anime["media"]["idMal"] for anime in self.lists[i]]
            total.update(ids)
        return len(total)

    def add_list(self, name, data):
        self.lists[name] = data
        self.length = self.get_length()
        return self.current_lists()

    def remove_list(self, name):
        if not name in self.lists:
            raise Exception()
        del self.lists[name]
        return self.current_lists()

    def current_lists(self):
        current_lists = list(self.lists.keys())
        if len(current_lists) == 0:
            current_lists = ["empty :("]
        embed = discord.Embed(
            title = "Anime Music Game - Current Lists",
            description = "\n".join(current_lists),
            color = 0xe475ea
        )
        return embed

    def random_anime(self):
        anime_list = random.choice(list(self.lists.values()))
        anime = random.choice(anime_list)["media"]
        idMal = anime["idMal"]
        year = anime["seasonYear"]
        cover = anime["coverImage"]["extraLarge"]
        name = anime["title"]["romaji"]
        english = anime["title"]["english"]
        synonyms = anime["synonyms"]
        synonyms.append(english)

        print(name, year, synonyms)

        return anime, idMal, year, cover, name, synonyms

    def score_string(self):
        combined = [(self.scores[i], self.players[i].display_name) for i in self.scores]
        ordered = list(reversed(sorted(combined)))
        formatted = [f"**{i[1]}** has {i[0]} points" for i in ordered]
        joined = "\n".join(formatted)

        if len(joined) == 0:
            return "none :("
        return joined

    def increment_score(self, user : discord.Member, name, title, thumbnail):
        if not user.id in self.scores:
            self.scores[user.id] = 0
            self.players[user.id] = user

        self.scores[user.id] += 5

        self.total += 1
        self.rounds += 1

        player = self.players[user.id]

        # make an embed
        embed = discord.Embed(
            title = "Anime Music Game",
            description = f'That was __{title}__ from *{name}*',
            color = player.color
        )
        embed.set_thumbnail(url = thumbnail)
        embed.set_author(name = f"{player.display_name} guessed it!", icon_url = player.avatar_url)
        embed.add_field(name = "Scores", value = self.score_string())
        return embed

    def failure(self, name, title, thumbnail):
        self.rounds += 1
        embed = discord.Embed(
            title = "Anime Music Game",
            description = f'That was __{title}__ from *{name}*',
            color = 0xcc0000
        )
        embed.set_thumbnail(url = thumbnail)
        embed.set_author(name = "no one got it this round :(")
        embed.add_field(name = "Scores", value = self.score_string())
        return embed

    def end_embed(self):
        embed = discord.Embed(
            title = "Anime Music Game",
            description = (f'That was {5*self.total} points across {self.rounds} rounds ' +
                            '({:.2f}% accuracy)'.format(100*self.total/self.rounds)),
            color = 0x98d685
        )
        embed.add_field(name = "Scores", value = self.score_string())
        return embed

    def listen_embed(self, name, title, thumbnail):
        embed = discord.Embed(
            title = "Anime Music",
            description = f'This is __{title}__ from *{name}*',
            color = 0xc0c0c0
        )
        embed.set_image(url = thumbnail)
        return embed

class WeebMusic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wiki_cache = {}
        self.games = {}
        self.pasts = [deque(), set()]

    async def random_title(self, idMal, year, name):
        # scrape reddit
        if year == None:
            raise Exception()

        if year < 2000:
            year = str(year)[2] + "0s"

        if not year in self.wiki_cache:
            async with self.bot.session.get(wiki + str(year)) as resp:
                soup = BeautifulSoup(await resp.text(), "html.parser")
            self.wiki_cache[year] = soup

        soup = self.wiki_cache[year]

        link = "https://myanimelist.net/anime/{}/".format(idMal)
        matches = soup.select('h3 a[href="{}"]'.format(link))

        if len(matches) == 0:
            print("no matches")
            raise Exception()

        elem = matches[0]
        table = elem.parent.find_next("tbody")

        first_col = [i.find("td").string for i in table.find_all("tr")]
        choices = list(filter(lambda x: x and not x.isspace(), first_col))

        title = random.choice(choices)
        clean_title = title.replace("\"", "")
        full_title = f"{name} {clean_title}"
        return full_title

    async def get_random(self, guild_id):
        # i really need this to return something eventually, but theres a lot of points of failure
        # rather than try to handle all of them, i just retry when something fails
        try:
            # choose from lists
            anime, idMal, year, cover, name, synonyms = self.games[guild_id].random_anime()

            title = await self.random_title(idMal, year, name)

            # avoid repeats
            while len(self.pasts[0]) >= self.games[guild_id].length:
                self.pasts[1].remove(self.pasts[0].pop())
            if title in self.pasts[1]:
                print("repeat")
                raise Exception()
            else:
                self.pasts[0].appendleft(title)
                self.pasts[1].add(title)

            print(title)

            # construct player
            player = await YTDLSource.create_source(title, loop=self.bot.loop, stream=True)

            return (name, cover, title, player, synonyms)
        except Exception as e:
            print(e)
            if guild_id in self.games:
                return await self.get_random(guild_id)

    def longest_common_subsequence(self, A, B):
        x = len(A)
        y = len(B)
        z = 0

        L = [[0 for j in range(y)] for i in range(x)]

        for i in range(x):
            for j in range(y):
                if A[i] == B[j]:
                    if i == 0 or j == 0:
                        L[i][j] = 1
                    else:
                        L[i][j] = L[i - 1][j - 1] + 1
                    if L[i][j] > z:
                        z = L[i][j]
        return z

    def guess_match(self, source, target):
        if source == None or target == None:
            return False

        def clean_string(s):
            return re.sub(r"[\W_]+", " ", s.lower()).split(" ")

        source_list = clean_string(source)
        target_list = clean_string(target)

        if source == target:
            return True

        if source_list[0] in target_list and len(source_list[0]) >= 6:
            return True

        # source_list is a sublist of target_list of at least length 2
        lcs = self.longest_common_subsequence(source_list, target_list)
        if len(source_list) == lcs and lcs >= 2:
            return True

        return False

    async def handle_controls(self, ctx, event, message, game):
        await message.add_reaction('▶️')

        def check(reaction, user):
            return (reaction.message.id == message.id
                and str(reaction.emoji) == '▶️'
                and user.id in game.players
            )

        def skip_check(reaction, user):
            return (reaction.message.id == message.id
                and str(reaction.emoji) == '⏭'
                and user.id in game.players
            )

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=5.0, check=check)
            await message.add_reaction('⏭')
            skip_task = self.bot.wait_for('reaction_add', check=skip_check)
            # wait for song end or skip react, whichever comes first
            _, pending = await asyncio.wait([event.wait(), skip_task],
                                            return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()

        except asyncio.TimeoutError:
            pass

    async def game_step(self, ctx, song, game):
        (name, cover, title, player, synonyms) = song

        event = asyncio.Event()

        # stop before play lets previous song play until next song, eliminating awk gap
        ctx.voice_client.stop()
        ctx.voice_client.play(player, after=lambda e: event.set())

        print("playing")

        def check(m):
            return (m.channel.id == ctx.channel.id and
                (self.guess_match(m.content, name) or
                    any([self.guess_match(m.content, i) for i in synonyms]))
            )

        try:
            message = await self.bot.wait_for('message', timeout=30.0, check=check)
            embed = self.games[ctx.guild.id].increment_score(message.author, name, title, cover)
            m = await ctx.send(embed = embed)
            # handle if someone presses continue
            await self.handle_controls(ctx, event, m, game)

        except asyncio.TimeoutError:
            embed = self.games[ctx.guild.id].failure(name, title, cover)
            await ctx.send(embed=embed)

    async def game_loop(self, ctx, game):

        song = await self.get_random(ctx.guild.id)
        while game.guild_id in self.games:
            try:
                await self.game_step(ctx, song, game)
                song = await self.get_random(ctx.guild.id)
            except Exception as e:
                print(e)
                song = await self.get_random(ctx.guild.id)

    @commands.group(aliases=["am"], invoke_without_command=True)
    async def animu(self, ctx):
        embed = discord.Embed(
            title = "Anime Music Game",
            description = " ".join([
                "Test your weeb level against fellow weebs!",
                "Join a voice channel, add at least one anime list using `?am add_list [anilist username]`, "
                "and start the game using `?am play`.",
                "\n\nWhen you recognize what anime you think it's from, simply type out your guess.",
                "You get 5 points for every correct guess, and there's no penalty for guessing.",
                "\n\nOnce you guess correctly, you can use ▶️ to continue playing the song",
                "or ⏭ to skip to the next one.",
                "The next song will start automatically in 5 seconds.",
                "\n\nIf you ever want to stop the game, just type out `?am stop`",
                "and the game will tally up your score.",
                "\n\nHave fun!"
            ]),
            color = 0xe475ea
        )

        embed.set_footer(text=f"i am not liable for any time lost playing this game (image credits to @deeeskye)")
        embed.set_image(url="https://i.pinimg.com/originals/34/b2/2e/34b22e8d6c9be0f9d5f09b0295d65747.jpg")
        await ctx.send(embed=embed)

    @animu.command()
    async def play(self, ctx):
        if not ctx.guild.id in self.games:
            await ctx.send("no lists, can't start!")
            return

        if ctx.author.voice == None:
            await ctx.send("hmm, r u sure ur in a voice channel?")
            return

        channel = ctx.author.voice.channel

        try:
            await channel.connect()
        except discord.errors.ClientException as e:
            await ctx.send("woops! can't do that...")
            print(e)
            return

        embed = discord.Embed(
            title = "Anime Music Game",
            description = "Starting!",
            color = 0xe475ea
        )
        await ctx.send(embed=embed)

        await self.game_loop(ctx, self.games[ctx.guild.id])

    @animu.command()
    async def remove_list(self, ctx, name):
        try:
            embed = self.games[ctx.guild.id].remove_list(name)
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)
            await ctx.send("failed")

    @animu.command()
    async def add_list(self, ctx, name):
        async with self.bot.session.post(ANILIST_API, json={
                'query': ANILIST_QUERY,
                'variables': {
                    'name': name
                }
        }) as response:
                if response.status != 200:
                    await ctx.send("failed")
                    print(response)
                else:
                    data = (await response.json())["data"]["MediaListCollection"]["lists"]
                    if not ctx.guild.id in self.games:
                        self.games[ctx.guild.id] = WeebGame(ctx.guild.id)
                    embed = self.games[ctx.guild.id].add_list(name, data[0]["entries"])
                    await ctx.send(embed=embed)

    @animu.command()
    async def stop(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        await voice.disconnect()
        await ctx.send(embed=self.games[ctx.guild.id].end_embed())
        del self.games[ctx.guild.id]

def setup(bot):
    bot.add_cog(WeebMusic(bot))
