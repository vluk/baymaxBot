import discord
from discord.ext import commands
import random

import asyncio

cards = ["villager", "werewolf", "minion", "mason", "seer", "robber", "troublemaker", "drunk", "insomniac", "tanner", "hunter"]
aesthetics = {
    "werewolf" : {
        "color" : 0x25d0ff,
        "thumbnail" : "https://cdn.discordapp.com/attachments/323535193073778689/716453639782137876/unknown.png"
    }
}

class Game:
    def __init__(self, host, join_message):
        self.state = "preparing"
        self.players = [1, 2, 3]
        self.host = host
        self.join_message = join_message
        self.initial_roles = []
        self.current_roles = []
        self.votes = {}

    def fetch_player(self, arg):
        try:
            for player in self.players:
                if not isinstance(player, int):
                    if player.id == int(arg):
                        return self.players.index(player)
        except ValueError:
            pass
        arg = str(arg)
        for player in self.players:
            if not isinstance(player, int):
                if player.name.lower() == arg.lower():
                    return self.players.index(player)
        for player in self.players:
            if not isinstance(player, int):
                if player.nick != None and player.nick.lower() == arg.lower():
                    return self.players.index(player)
        return -1

    def get_refreshed_embed(self):
        embed = self.join_message.embeds[0]
        embed.clear_fields()
        players = ", ".join(self.get_player_list()) if len(self.players) > 3 else "None"
        embed.add_field(name="Players:", value = players)
        roles = ", ".join([cards[i] for i in self.initial_roles]) if len(self.initial_roles) > 0 else "None"
        embed.add_field(name="Roles:", value = roles)
        return embed

    def get_player_list(self):
        return [i.display_name for i in self.players if not isinstance(i, int)]

    def get_debrief(self):
        return [(self.players[i].display_name, cards[self.current_roles[i]]) for i in range(len(self.current_roles)) if not isinstance(self.players[i], int)]

    def simulate(self, instructions):
        for i in instructions:
            for j in i:
                swap = self.current_roles[j[0]]
                self.current_roles[j[0]] = self.current_roles[j[1]]
                self.current_roles[j[1]] = swap

class Werewolf(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}

    async def do_villager():
        pass

    async def do_werewolf(self, user, game):
        werewolves = []
        for i in range(len(game.players)):
            if not isinstance(game.players[i], int) and game.initial_roles[i] == 1:
                werewolves.append(game.players[i])

        if len(werewolves) == 1:

            embed = discord.Embed(
                title = "You are a werewolf!",
                description = " ".join([
                    "You are a werewolf, the very embodiment of evil itself.",
                    "As a werewolf, your goal is to stay alive by deceiving the other players.",
                    "If all of the werewolves manage to stay alive, then their team wins.",
                    "Since it looks like you're the only werewolf, you get to look at a card from the center.",
                    "Click on one of the reactions on this message to reveal a card."
                ]),
                color = aesthetics["werewolf"]["color"]
            )

            embed.set_thumbnail(url=aesthetics["werewolf"]["thumbnail"])

            embed.add_field(
                name="Werewolves",
                value = "Just you!"
            )

            message = await user.send(embed=embed)

            key = {"1️⃣" : 1, "2️⃣" : 2, "3️⃣" : 3}

            for i in key:
                await message.add_reaction(i)

            def check(r, u):
                return u.id == user.id and r.message.id == message.id and str(r.emoji) in key

            reaction, user = await self.bot.wait_for("reaction_add", check=check)

            selection = key[str(reaction.emoji)]

            revealed = cards[game.initial_roles[game.players.index(selection)]].capitalize()

            embed.add_field(
                name="Revealed Card",
                value=revealed,
            )

            await message.edit(embed=embed)

        elif len(werewolves) > 1:

            embed = discord.Embed(
                title = "You are a werewolf!",
                description = " ".join([
                    "As a werewolf, your goal is to stay alive by deceiving the other players.",
                    "If all of the werewolves manage to stay alive, then their team wins."
                ]),
                color = aesthetics["werewolf"]["color"]
            )

            embed.set_thumbnail(url=aesthetics["werewolf"]["thumbnail"])

            embed.add_field(
                name="Werewolves:",
                value = ", ".join([werewolf.display_name for werewolf in werewolves])
            )

            await user.send(embed=embed)

        return []

    async def do_minion(self, user, game):
        werewolves = []
        for i in range(len(game.players)):
            if not isinstance(game.players[i], int) and game.initial_roles[i] == 1:
                werewolves.append(game.players[i])

        if len(werewolves) == 0:

            embed = discord.Embed(
                title = "You are a minion!",
                description = " ".join([
                    "You are a dastardly minion, only barely tolerated by the werewolves.",
                    "Try to draw the fire of the other players, or divert suspicion towards one of the villagers.",
                    "If all of the werewolves manage to stay alive, then you win.",
                ])
            )

            embed.add_field(
                name="Werewolves:",
                value = "None"
            )

            await user.send(embed=embed)

        else:

            embed = discord.Embed(
                title = "You are a minion!",
                description = " ".join([
                    "You are a minion, dashing but with a heart of coal.",
                    "Try to draw the fire of the other players, or divert suspicion towards one of the villagers.",
                    "If all of the werewolves manage to stay alive, then you win.",
                ])
            )


            embed.add_field(
                name="Werewolves:",
                value = ", ".join([werewolf.display_name for werewolf in werewolves])
            )

            await user.send(embed=embed)

        return []

    async def do_mason(self, user, game):
        masons = []
        for i in range(len(game.players)):
            if not isinstance(game.players[i], int) and game.initial_roles[i] == 3:
                masons.append(game.players[i])

        embed = discord.Embed(
            title = "You are a mason!",
            description = " ".join([
                "Your sublime bond with your partner is unbreakable.",
                "Leverage your maybe-platonic love to narrow down the suspects.",
                "If you manage to kill a werewolf, then you win.",
            ])
        )

        embed.add_field(
            name="Masons",
            value = ", ".join([mason.display_name for mason in masons])
        )

        message = await user.send(embed=embed)

        return []

    async def do_seer(self, user, game):
        embed = discord.Embed(
            title = "You are a seer!",
            description = " ".join([
                "You are one with the very fabric of reality itself.",
                "Use your eldritch knowledge to gain insights into the game.",
                "If you manage to kill a werewolf, then you win.",
                "You can either look at either another player's card or two cards in the center. "
                "React with either 🇵 or 🇨 to choose."
            ])
        )

        message = await user.send(embed=embed)

        key = {"🇵" : "player", "🇨" : "center"}

        for i in key:
            await message.add_reaction(i)

        def check(r, u):
            return u.id == user.id and r.message.id == message.id and str(r.emoji) in key

        reaction, user = await self.bot.wait_for("reaction_add", check=check)

        selection = key[str(reaction.emoji)]

        if selection == "player":
            await user.send("Choose which player, using either their full username or nickname.")

            def user_check(m):
                if m.author.id != self.bot.user.id:
                    if m.channel.id == user.dm_channel.id:
                        if game.fetch_player(m.content) != -1:
                            self.bot.loop.create_task(m.add_reaction("✅"))
                            return True
                        else:
                            self.bot.loop.create_task(m.add_reaction("❌"))
                            return False

            player = game.fetch_player((await self.bot.wait_for("message", check=user_check)).content)
            await user.send(cards[game.initial_roles[player]])

        elif selection == "center":
            await user.send("Choose which two using two numbers (1, 2, 3) seperated with a space.")

            def card_check(m):
                if m.channel.id != user.dm_channel.id:
                    return False
                split = m.content.split()
                if len(split) != 2:
                    self.bot.loop.create_task(m.add_reaction("❌"))
                    return False
                try:
                    valid = int(split[0]) in [1, 2, 3] and int(split[1]) in [1, 2, 3] and split[0] != split[1]
                    if valid:
                        self.bot.loop.create_task(m.add_reaction("✅"))
                        return True
                    self.bot.loop.create_task(m.add_reaction("❌"))
                    return False
                except ValueError:
                    self.bot.loop.create_task(m.add_reaction("❌"))
                    return False

            centers = [int(i) for i in (await self.bot.wait_for("message", check=card_check)).content.split()]

            await user.send(cards[game.initial_roles[game.players.index(centers[0])]])
            await user.send(cards[game.initial_roles[game.players.index(centers[1])]])

        await user.send("You're good to go!")

        return []

    async def do_robber(self, user, game):
        embed = discord.Embed(
            title = "You are a robber!",
            description = " ".join([
                "Your morals are flexible, and so is your identity.",
                "Choose another player to swap your card with.",
                "Whoever ends up with your card will be on the villager team.",
                "(Send a message containing their full username or nickname.)"
            ])
        )

        message = await user.send(embed=embed)

        initial = game.fetch_player(user.id)

        def check(m):
            if m.channel.id == user.dm_channel.id:
                if (game.fetch_player(m.content) != -1
                    and game.fetch_player(m.content) != initial):
                    self.bot.loop.create_task(m.add_reaction("✅"))
                    return True
                else:
                    self.bot.loop.create_task(m.add_reaction("❌"))
                    return False

        target = game.fetch_player((await self.bot.wait_for("message", check=check)).content)

        await user.send("you are now the " + cards[game.initial_roles[target]])

        await user.send("You're good to go!")

        return [(initial, target)]

    async def do_troublemaker(self, user, game):
        await user.send("choose two players to swap (seperate messages)")

        initial = game.fetch_player(user.id)

        first = None

        def check(m):
            if m.channel.id == user.dm_channel.id:
                if (game.fetch_player(m.content) != -1
                    and game.fetch_player(m.content) != first
                    and game.fetch_player(m.content) != initial):
                    self.bot.loop.create_task(m.add_reaction("✅"))
                    return True
                else:
                    self.bot.loop.create_task(m.add_reaction("❌"))
                    return False

        first_message = await self.bot.wait_for("message", check=check)

        first = game.fetch_player(first_message.content)

        second_message = await self.bot.wait_for("message", check=check)

        second = game.fetch_player(second_message.content)

        await user.send("You're good to go!")

        return [(first, second)]

    async def do_drunk(self, user, game):

        embed = discord.Embed(
            title = "You are a drunk!",
            description = " ".join([
                "You like the happy juice a biiiit more than is probably healthy.",
                "Choose a card in the center to swap with."
            ])
        )

        message = await user.send(embed=embed)

        key = {"1️⃣" : 1, "2️⃣" : 2, "3️⃣" : 3}

        for i in key:
            await message.add_reaction(i)

        def check(r, u):
            return u.id == user.id and r.message.id == message.id and str(r.emoji) in key

        reaction, user = await self.bot.wait_for("reaction_add", check=check)

        selection = key[str(reaction.emoji)]

        current = game.fetch_player(user.id)

        middle = game.players.index(key[str(reaction.emoji)])

        await user.send("You're good to go!")

        return [(current, middle)]

    async def do_insomniac(self, user, game):

        current = game.fetch_player(user.id)

        await user.send(cards[game.current_roles[current]])

    @commands.group(aliases=["ww"], invoke_without_command=True)
    async def werewolf(self, ctx):
        host = ctx.message.author
        embed = discord.Embed(
            title = "Werewolf",
            description = " ".join([
                "A classic social deduction game where two sides face off against each other: the **Villagers** and **Werewolves**.",
                "Uncover who the werewolves are, or use deception to stay hidden until the end.",
                "But be careful: if you kill the Tanner, then both teams lose.",
                "\n\n**Instructions:**\n",
                "**React to this message with 🐺** to join the game, "
                "then **add cards** using `%ww add` followed by a list of the roles you want to add, seperated by spaces.",
                "For example, you might do something like this to add multiple roles:",
                "`%ww add werewolf minion seer tanner troublemaker mason mason`.",
                "Additionally, you can get the order of the roles using %ww roleOrder."
            ]),
            color = 0x7289da
        )

        embed.set_footer(text=f"{host.display_name} is the host", icon_url=host.avatar_url)
        embed.add_field(name="Players", value="None")
        embed.add_field(name="Roles", value="None")


        if not ctx.channel.id in self.games:
            message = await ctx.send(embed=embed)
            await message.add_reaction("🐺")
            self.games[ctx.channel.id] = Game(ctx.message.author, message)
        else:
            await ctx.send("There's already a game running here!")

    @werewolf.command()
    async def join(self, ctx):
        game = None
        if not ctx.channel.id in self.games:
             self.games[ctx.channel.id] = Game()
        game = self.games[ctx.channel.id]
        if game.state == "preparing":
            if game.fetch_player(ctx.message.author.id) == -1:
                game.players.append(ctx.message.author)
                await ctx.send("yeah sure")
            else:
                await ctx.send("already in the game")
        else:
            await ctx.send("nah you cant join in the middle of a round")

    @werewolf.command(aliases=["addcard"])
    async def add(self, ctx, *, names):
        if not ctx.channel.id in self.games:
            await ctx.send("theres no game here dummy")
            return
        game = self.games[ctx.channel.id]
        if game.host.id != ctx.message.author.id:
            await ctx.send("Only the host can add roles.")
            return
        if all([name.lower() in cards for name in names.split()]) and game.state == "preparing":
            for name in names.split():
                game.initial_roles.append(cards.index(name.lower()))
            await game.join_message.edit(embed=game.get_refreshed_embed())

    @werewolf.command()
    async def set(self, ctx, *, names):
        if not ctx.channel.id in self.games:
            await ctx.send("theres no game here dummy")
            return
        game = self.games[ctx.channel.id]
        if game.host.id != ctx.message.author.id:
            await ctx.send("Only the host can add roles.")
            return
        game.initial_roles = []
        if all([name.lower() in cards for name in names.split()]) and game.state == "preparing":
            for name in names.split():
                game.initial_roles.append(cards.index(name.lower()))
            await game.join_message.edit(embed=game.get_refreshed_embed())

    @werewolf.command(aliase=["removecard"])
    async def remove(self, ctx, name):
        if not ctx.channel.id in self.games:
            await ctx.send("theres no game here dummy")
            return
        game = self.games[ctx.channel.id]
        if game.host.id != ctx.message.author.id:
            await ctx.send("Only the host can add roles.")
        game = self.games[ctx.channel.id]
        if game.state == "preparing" and cards.index(name.lower()) in game.initial_roles:
            game.initial_roles.remove(cards.index(name.lower()))
            await game.join_message.edit(embed=game.get_refreshed_embed())

    @werewolf.command()
    async def vote(self, ctx, *, accused : str):
        if not ctx.channel.id in self.games:
            await ctx.send("theres no game here dummy")
            return
        game = self.games[ctx.channel.id]
        if game.state != "voting":
            await ctx.send("cant vote yet")
            return

        author = ctx.message.author

        if game.fetch_player(author.id) != -1:
            if game.fetch_player(accused) != -1:
                game.votes[author.id] = game.players[game.fetch_player(accused)].id
                if len(game.votes) == len(game.players) - 3:
                    tally = {}
                    for i in game.votes:
                        if not game.votes[i] in tally:
                            tally[game.votes[i]] = 0
                        tally[game.votes[i]] += 1
                    top = sorted([(tally[i], i) for i in tally])
                    if len(top) > 1 and top[-1][0] == top[-2][0]:
                        await ctx.send("no decisive winner")
                    else:
                        killed_id = top[-1][1]

                        index = game.fetch_player(killed_id)

                        killed = game.players[index]

                        await ctx.send("killing " + killed.mention)
                        if cards[game.current_roles[index]] == "hunter":
                            def user_check(m):
                                if m.channel.id == ctx.message.channel.id:
                                    if game.fetch_player(m.content) != -1:
                                        self.bot.loop.create_task(m.add_reaction("✅"))
                                        return True
                                    else:
                                        self.bot.loop.create_task(m.add_reaction("❌"))
                                        return False

                            player = game.fetch_player((await self.bot.wait_for("message", check=user_check)).content)

                        await ctx.send(killed.display_name + " was " + cards[game.current_roles[index]])

                        paired_roles = [" was ".join(i) for i in game.get_debrief()]

                        await ctx.send(", ".join(paired_roles))

                        del self.games[ctx.channel.id]
                else:
                    await ctx.send("vote registered")
            else:
                await ctx.send("cant find")
        else:
            await ctx.send("you're not playing")

    @werewolf.command()
    async def roleOrder(self, ctx):
        await ctx.send(", ".join(cards))

    @werewolf.command()
    async def start(self, ctx):
        if not ctx.channel.id in self.games:
            await ctx.send("theres no game here dummy")
            return

        game = self.games[ctx.channel.id]

        if game.host.id != ctx.message.author.id:
            await ctx.send("Only the host can start the game.")
            return

        if len(game.players) > len(game.initial_roles):
            await ctx.send("You need more roles to play!")
            return
        if len(game.players) < len(game.initial_roles):
            await ctx.send("You need less roles to play!")
            return

        game.state = "running"

        game.initial_roles = sorted(game.initial_roles)

        random.shuffle(game.players)

        game.current_roles = [i for i in game.initial_roles]

        await ctx.send("game starting")

        for i in range(len(game.players)):
            if not isinstance(game.players[i], int):
                await game.players[i].send("you're the " + cards[game.initial_roles[i]])

        tasks = []

        for i in range(len(game.initial_roles)):
            if not isinstance(game.players[i], int):
                if game.initial_roles[i] == 1:
                    tasks.append(self.do_werewolf(game.players[i], game))
                if game.initial_roles[i] == 2:
                    tasks.append(self.do_minion(game.players[i], game))
                if game.initial_roles[i] == 3:
                    tasks.append(self.do_mason(game.players[i], game))
                if game.initial_roles[i] == 4:
                    tasks.append(self.do_seer(game.players[i], game))
                if game.initial_roles[i] == 5:
                    tasks.append(self.do_robber(game.players[i], game))
                if game.initial_roles[i] == 6:
                    tasks.append(self.do_troublemaker(game.players[i], game))
                if game.initial_roles[i] == 7:
                    tasks.append(self.do_drunk(game.players[i], game))

        instructions = await asyncio.gather(*tasks)

        game.simulate(instructions)

        for i in range(len(game.players)):
            if not isinstance(game.players[i], int):
                if game.initial_roles[i] == 8:
                    await self.do_insomniac(game.players[i], game)

        await ctx.send("the night's now over, do ur stuff then do %ww vote")

        game.state = "voting"

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.id == self.bot.user.id:
            return
        message = reaction.message
        if message.channel.id in self.games and self.games[message.channel.id].state == "preparing":
            game = self.games[message.channel.id]
            if game.join_message.id == message.id:
                if game.fetch_player(user.id) == -1:
                    game.players.append(user)
                    await message.edit(embed=game.get_refreshed_embed())

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        message = reaction.message
        if message.channel.id in self.games and self.games[message.channel.id].state == "preparing":
            game = self.games[message.channel.id]
            if game.join_message.id == message.id:
                if game.fetch_player(user.id) != -1:
                    for player in range(len(game.players)):
                        if not isinstance(game.players[player], int) and game.players[player].id == user.id:
                            del game.players[player]
                            await message.edit(embed=game.get_refreshed_embed())

    @werewolf.command()
    async def cancel(self, ctx):
        if ctx.message.channel.id in self.games:
            game = self.games[ctx.channel.id]
            if game.host.id == ctx.message.author.id:
                del self.games[ctx.channel.id]
                await ctx.send("game cancelled")

def setup(bot):
    bot.add_cog(Dictionary(bot))
