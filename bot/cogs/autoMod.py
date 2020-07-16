import discord
import json
import requests
import wordlistloader as bl
import sqlite3


from helperFunctions import modbotDBinterface
from flashtext import KeywordProcessor
from discord.ext import commands


class autoMod(commands.Cog):
    def __init__(self, bot):

        self.logfile = {}
        self.bot = bot

        self.modbotCache = {}

        self.populateCache()

        self.DEFAULT_KEYWORD_PROCESSOR = KeywordProcessor()
        for word in bl.loadDefaultBlacklist():
            self.DEFAULT_KEYWORD_PROCESSOR.add_keyword(word)

    # Append to dictionary cache in form (id : (enable_blacklist,enable_deepStringMatch,selected_blacklist_name ))

    def populateCache(self):
        for entry in modbotDBinterface.getAllModbotSettings():
            self.modbotCache[entry[0]] = (entry[1], entry[2], entry[3])

            for item in self.modbotCache.keys():
                print(f'{item}: {self.modbotCache[item]}')

    def updateDB(self, ctx):
        modbotDBinterface.initNewServer(ctx.guild.id)
        entry = modbotDBinterface.getModbotServerSettings(ctx.guild.id)[0]

        print(entry)

        self.modbotCache[entry[0]] = (entry[1], entry[2], entry[3])

        for item in self.modbotCache.keys():
            print(f'{item}: {self.modbotCache[item]}')

    @ commands.command()
    async def reload(self, ctx):

        print(f"sender id:{ctx.author.id}\n bot owner id:212318242247671808\n")

        if ctx.author.id != 212318242247671808:
            return

        populateCache()

    @commands.command()
    async def enable_deepStringMatch(self, ctx):
        modbotDBinterface.enable_deepStringMatch(ctx)

        self.modbotCache[ctx.guild.id] = (
            self.modbotCache[ctx.guild.id][0], "True", self.modbotCache[ctx.guild.id][2])

    @commands.command()
    async def disable_deepStringMatch(self, ctx):
        modbotDBinterface.disable_deepStringMatch(ctx)

        self.modbotCache[ctx.guild.id] = (
            self.modbotCache[ctx.guild.id][0], "False", self.modbotCache[ctx.guild.id][2])

    @commands.command()
    async def enable_blacklist(self, ctx):
        modbotDBinterface.enable_blacklist(ctx)

        self.modbotCache[ctx.guild.id] = (
            "True", self.modbotCache[ctx.guild.id][1], self.modbotCache[ctx.guild.id][2])

    @commands.command()
    async def disable_blacklist(self, ctx):
        modbotDBinterface.disable_blacklist(ctx)

        self.modbotCache[ctx.guild.id] = (
            "False", self.modbotCache[ctx.guild.id][1], self.modbotCache[ctx.guild.id][2])

    def directStringMatch(self, ctx):
        if len(self.DEFAULT_KEYWORD_PROCESSOR.extract_keywords(ctx.content)) > 0:
            return True
        else:
            return False

    def deepStringMatch(self, ctx):
        r = requests.get(
            f'http://127.0.0.1:5000/mod-bot/api/v1.0/deep-check/"{ctx.content}"')
        print(r.text)
        if "true" in r.text:
            return True
        else:
            return False

    @ commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot:
            return

        if ctx.guild.id not in self.modbotCache:
            print("Guild not in database")
            self.updateDB(ctx)
            return

        # if blacklist disabled stop
        if self.modbotCache[ctx.guild.id][0] == 'False':
            return

        if self.directStringMatch(ctx):
            print(f'Direct string match for message: {ctx.content}')
            await ctx.delete()
        elif (self.modbotCache[ctx.guild.id][1] == 'True') and (self.deepStringMatch(ctx)):
            print(f'Deep string match for message: {ctx.content}')
            await ctx.delete()

    @ commands.Cog.listener()
    async def on_guild_join(self, guild):
        modbotDBinterface.initNewServer(guild.id)


def setup(bot):
    bot.add_cog(autoMod(bot))
