import discord
import json
import os
import editdistance
from flashtext import KeywordProcessor
from discord.ext import commands


class autoMod(commands.Cog):
    def __init__(self, bot):
        self.keyword_processor = KeywordProcessor()
        self.valid_keyword_processor = KeywordProcessor()
        self.blacklist = []
        self.valid_words = []

        with open('data/wordblacklist.json') as wordlist:
            self.blacklist = json.load(wordlist)
        
            for word in self.blacklist:
                self.keyword_processor.add_keyword(word)

        with open('data/valid_words.json') as valid_words:
            self.valid_words = json.load(valid_words)

            for word in self.valid_words:
                self.valid_keyword_processor.add_keyword(word)

        self.bot = bot
        self.word_black_list = self.blacklist

    @commands.command()
    async def reload(self,ctx):
        with open('data/wordblacklist.json') as wordlist:
            TEMPaaaa = json.load(wordlist)
            self.blacklist = TEMPaaaa

    @commands.Cog.listener()
    async def on_message(self, ctx):

        if message.author.bot:
            return
            
        word_found = False
        # print(f"{ctx.author} said {ctx.content}")

        keywords_found = self.keyword_processor.extract_keywords(ctx.content.lower())
        temp_valid_word = self.valid_keyword_processor.extract_keywords(ctx.content.lower())

        if len(keywords_found) > 0:
            print(f"found {keywords_found} in {ctx.content}")
            await ctx.delete()
            pass
        
        for word in self.word_black_list:

            if word_found:
                word_found = False
                break

            if len(word) > len(ctx.content):
                continue
            
            try:
                for index in range(0,len(ctx.content)):

                    substring = ctx.content[index:len(word) + index].lower()

                    # print(f"Substring = {substring}")
                    
                    # print(f"temp valid word = {temp_valid_word}")

                    if len(temp_valid_word) > 0:
                        # print(f"Valid word {substring} found. \n Breaking Out of Loop.")
                        word_found = True
                        break

                    #Checks if substrings legth is that of the word were checking against.
                    if not (len(substring) == len(word)) or len(substring) <= 2:
                        # print(f"{substring} length of {len(substring)} \n")
                        break

                    edit_distance = editdistance.eval(word,substring)

                    if edit_distance <= 2:
                        
                        await ctx.delete()
                        print(f"{substring} matched {word} in {ctx.content} with edit distence of {edit_distance}. \n Breaking Out of Loop.")
                        word_found = True
                        break
           
            except Exception as e:
                print(f"!excetion! \n {e}")
            

def setup(bot):
    bot.add_cog(autoMod(bot))