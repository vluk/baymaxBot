import discord
from discord.ext import commands
import tensorflow as tf
from tensorflow import keras
import numpy as np
import random
from utils.model import Model

nicknames = {
     150731311001239553: 'nick',
     275000974345764865: 'gabe',
     116350814439604230: 'maya',
     219642803943112705: 'jonny',
     280559507401211904: 'aaron',
     320659306745954304: 'vernon',
     583118520058118155: 'lilly',
     320731556672962560: 'kevin moy',
     312418351844425731: 'kev',
     305840135734558742: 'mackenzie',
     264568793068470278: 'alex',
     257216991788531712: 'Jason',
     320705791575326720: 'gabby',
     206988376006459393: 'jacob',
     332350596826791937: 'jake',
     361789541494947851: 'arul',
     220825807856074752: 'isaac',
     219962518506831872: 'sean',
     326220254835638272: 'emily',
     321808457583951872: 'anika',
     322886373134696478: 'alyssa',
     361383914813784066: 'charlotte',
     327203089067147286: 'albert',
     314563015380828160: 'joe',
     461298305838874624: 'jenny',
     210959959905665026: 'balex',
     201459841426915329: 'darren',
     216995907894378496: 'daniel',
     320735343739535362: 'owen',
     321112185633898497: 'alice',
     322193711352119297: 'emma',
     151074267205730304: 'rafi',
     222864996265099264: 'hailey',
     164199386820247552: 'colin',
     321131053114982400: "rachel"
}

people = {0: 'stormyskies', 1: 'seaweedgrapes', 2: 'Random17', 3: 'calymsis', 4: 'axylon', 5: 'HeresJohnny', 6: 'Cutie', 7: 'MysteryPig', 8: 'TheJoviets', 9: 'Marvin', 10: 'NA - starethebear', 11: 'NotRelatedToANazi', 12: 'JonnyBot', 13: 'jennythebot', 14: 'stillblue', 15: 'Kron', 16: 'Electrostatic Mikei', 17: 'danielp', 18: 'GabbyTirsell', 19: 'Anipon'}

letters = {' ': 0, 'e': 1, 't': 2, 'o': 3, 'a': 4, 'i': 5, 'n': 6, 's': 7, 'h': 8, 'r': 9, 'l': 10, 'd': 11, 'm': 12, 'u': 13, 'c': 14, 'y': 15, '0': 16, 'p': 17, 'g': 18, 'w': 19, 'f': 20, 'b': 21, '﷽': 22, 'k': 23, '1': 24, '2': 25, '4': 26, 'v': 27, '.': 28, '3': 29, '9': 30, '5': 31, '8': 32, '/': 33, '6': 34, '7': 35, "'": 36, '?': 37, '\n': 38, 'I': 39, '!': 40, ',': 41, 'j': 42, '-': 43, ':': 44, 'A': 45, 'x': 46, 'T': 47, '`': 48, '>': 49, 'O': 50, '<': 51, '_': 52, 'S': 53, 'E': 54, 'H': 55, '*': 56, '@': 57, 'N': 58, 'W': 59, 'q': 60, 'C': 61, 'Y': 62, 'L': 63, 'M': 64, 'R': 65, ')': 66, '(': 67, 'D': 68, 'z': 69, '~': 70, '"': 71, 'G': 72, 'P': 73, 'U': 74, '+': 75, 'B': 76, 'F': 77, '\\': 78, 'K': 79, '|': 80, 'J': 81, '$': 82, '#': 83, '\u200b': 84, 'V': 85, '^': 86, '=': 87, '⚫': 88, '{': 89, '\xad': 90, ';': 91, 'X': 92, '[': 93, ']': 94, '}': 95, '%': 96, '°': 97, 'Q': 98, '☭': 99}

numbersToPeople = {100: 'stormyskies', 101: 'racheljiang', 102: 'Random17', 103: 'calymsis', 104: 'axylon', 105: 'HeresJohnny', 106: 'MysteryPig', 107: 'TheJoviets', 108: 'NA - starethebear', 109: 'NotRelatedToANazi', 110: 'stillblue', 111: 'Kron', 112: 'Electrostatic Mikei', 113: 'danielp', 114: 'GabbyTirsell', 115: 'Anipon'}

lettersToNumbers = {' ': 0, 'e': 1, 't': 2, 'o': 3, 'a': 4, 'i': 5, 'n': 6, 's': 7, 'h': 8, 'r': 9, 'l': 10, 'd': 11, 'm': 12, 'u': 13, 'c': 14, 'y': 15, '0': 16, 'p': 17, 'g': 18, 'w': 19, 'f': 20, 'b': 21, '﷽': 22, 'k': 23, '1': 24, '2': 25, '4': 26, 'v': 27, '.': 28, '3': 29, '9': 30, '5': 31, '8': 32, '/': 33, '6': 34, '7': 35, "'": 36, '?': 37, '\n': 38, 'I': 39, '!': 40, ',': 41, 'j': 42, '-': 43, ':': 44, 'A': 45, 'x': 46, 'T': 47, '`': 48, '>': 49, 'O': 50, '<': 51, '_': 52, 'S': 53, 'E': 54, 'H': 55, '*': 56, '@': 57, 'N': 58, 'W': 59, 'q': 60, 'C': 61, 'Y': 62, 'L': 63, 'M': 64, 'R': 65, ')': 66, '(': 67, 'D': 68, 'z': 69, '~': 70, '"': 71, 'G': 72, 'P': 73, 'U': 74, '+': 75, 'B': 76, 'F': 77, '\\': 78, 'K': 79, '|': 80, 'J': 81, '$': 82, '#': 83, '\u200b': 84, 'V': 85, '^': 86, '=': 87, '⚫': 88, '{': 89, '\xad': 90, ';': 91, 'X': 92, '[': 93, ']': 94, '}': 95, '%': 96, '°': 97, 'Q': 98, '☭': 99}

peopleToNumbers = {numbersToPeople[i] : i for i in numbersToPeople}
numbersToLetters = {lettersToNumbers[i] : i for i in lettersToNumbers}

vocab_size = 116
embedding_dim = 64
units = 256

class Neural(commands.Cog):
    def __init__(self, bot):
        predict_model = keras.models.load_model("models/878328592.h5")
        predict_model.compile(
            optimizer="adam",
            loss = "sparse_categorical_crossentropy",
            metrics = ["accuracy"]
        )

        sim_model = Model(vocab_size, embedding_dim, units)
        sim_dir = "models/checkpoints"
        checkpoint = tf.train.Checkpoint(model=sim_model)
        checkpoint.restore(tf.train.latest_checkpoint(sim_dir))

        self.bot = bot
        self.predict_model = predict_model
        self.sim_model = sim_model
        self.temp = 0.65

    @commands.command()
    async def heat(self, ctx, heat : float):
        self.temp = heat
        await ctx.send("temp set to {0}".format(str(heat)))

    @commands.command()
    async def temp(self, ctx):
        await ctx.send("temp currently at {0}".format(str(self.temp)))

    @commands.command(aliases=["sim"])
    async def simulate(self, ctx, user : discord.Member):
        if not user.name in peopleToNumbers:
            await ctx.send("person not found!")
            return
        person = peopleToNumbers[user.name]
        messages = []
        count = 0
        async for message in ctx.history(limit = 256):
            if message.id != ctx.message.id and not ctx.message.content.startswith("%"):
                count += 1
                count += len(message.content)
                if count > 255:
                    break
                messages.insert(0, message)

        input_eval = []

        for message in messages:
            if message.author.name in peopleToNumbers:
                input_eval.append(peopleToNumbers[message.author.name])
                for letter in message.content:
                    if letter in lettersToNumbers:
                        input_eval.append(lettersToNumbers[letter])
        input_eval.append(person)
        input_eval = tf.expand_dims(input_eval, 0)
        text_generated = []
        for i in range(256):
            predictions = self.sim_model(input_eval)
            predictions = tf.squeeze(predictions, 0)
            predictions = predictions / self.temp
            predicted_id = tf.random.categorical(predictions, num_samples=1)[-1, 0].numpy()
            input_eval = tf.expand_dims([predicted_id], 0)
            numbered = predicted_id
            if numbered >= 100:
                break
            text_generated.append(numbersToLetters[numbered])
        embed = discord.Embed(
            description = "".join(text_generated),
            color = user.colour
        )
        embed.set_author(name=user.display_name, icon_url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def whom(self, ctx, *, message : str):
        nice_list = np.asarray([[letters[message[i]] if i < len(message) else 100 for i in range(128)]])
        probabilities = self.predict_model.predict(nice_list).tolist()[0]
        people_probs = list(reversed(sorted([(probabilities[i], people[i]) for i in people])))[:3]
        nice_string = "```Python\n"
        for i in people_probs:
            nice_string += "{0:<20}{1:.4f}%\n".format(i[1], 100 * i[0])
        nice_string += "```"
        await ctx.send(nice_string)
