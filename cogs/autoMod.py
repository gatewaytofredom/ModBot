import discord
import json
import os
import editdistance
from flashtext import KeywordProcessor
from discord.ext import commands

class autoMod(commands.Cog):
    def __init__(self, bot):
        self.blacklsited_keyword_processor = KeywordProcessor()
        self.valid_keyword_processor = KeywordProcessor()
        self.black_list = []
        self.valid_words = []

        # Load the blacklisted words.
        with open('data/wordblacklist.json') as wordlist:
            self.black_list = json.load(wordlist)
        
            for word in self.black_list:
                self.blacklsited_keyword_processor.add_keyword(word)

        # Load the non vulgar english words.
        with open('data/valid_words.json') as valid_words:
            self.valid_words = json.load(valid_words)

            for word in self.valid_words:
                self.valid_keyword_processor.add_keyword(word)

        # Clear both lists after use to reduce memory usage after use.
        # self.black_list = []
        # self.valid_words = []

        self.bot = bot

    @commands.command()
    async def reload(self,ctx):
        self.black_list = []
        self.valid_words = []

        # Load the blacklisted words.
        with open('data/wordblacklist.json') as wordlist:
            self.black_list = json.load(wordlist)
        
            for word in self.black_list:
                self.blacklsited_keyword_processor.add_keyword(word)

        # Load the non vulgar english words.
        with open('data/valid_words.json') as valid_words:
            self.valid_words = json.load(valid_words)

            for word in self.valid_words:
                self.valid_keyword_processor.add_keyword(word)

    @commands.Cog.listener()
    async def on_message(self, ctx):

        # Ignores other bots.
        if ctx.author.bot:
            return

        word_found = False

        keywords_found = self.blacklsited_keyword_processor.extract_keywords(ctx.content.lower())
        temp_valid_word = self.valid_keyword_processor.extract_keywords(ctx.content.lower())

        if len(keywords_found) > 0:
            f = open("logfile.txt", "a")
            f.write(f"Detected {keywords_found} in {ctx.author}: {ctx.content} \n")
            f.close()

            # await ctx.delete()
            pass
        
        # Check against every blacklisted word in the users message.
        for word in self.black_list:

            # Skip current blacklisted word if it has more characters than the users message.
            if len(word) > len(ctx.content):
                continue
            
            try:

                # Iterate for the total length of the users message.
                for index in range(0,len(ctx.content)):

                    # Set substring to the length of the blacklisted word we are matching against.
                    substring = ctx.content[index:len(word) + index].lower()

                    # checks the substring contains a real word.
                    # Breaks here to prevent a false positive.
                    if len(temp_valid_word) > 0:
                        word_found = True
                        break

                    # Checks if substrings length is that of the word were checking against.
                    # Break here to prevent a false positive.
                    if not (len(substring) == len(word)) or len(substring) <= 2:
                        break

                    # Determine total characters the substring has different compared to the blacklisted word.
                    edit_distance = editdistance.eval(word,substring)

                    # Checks how many letters substring deviates from the blacklisted word compared to a threshold.
                    if edit_distance <= 2:
                        f = open("logfile.txt", "a")
                        f.write(f"{substring} matched {word} in {ctx.author}: {ctx.content} with edit distence of {edit_distance}. \n Breaking Out of Loop. \n")
                        f.close()
                        # await ctx.delete()
                        word_found = True
                        break

            except Exception as e:
                print(f"!exception! \n {e}")
            
            # Exits the loop if a blacklisted word is detected.
            if word_found:
                break
            
def setup(bot):
    bot.add_cog(autoMod(bot))