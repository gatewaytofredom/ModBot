import discord
import json
import os
import editdistance
import time
from flashtext import KeywordProcessor
from discord.ext import commands
#from profanity_check import predict, predict_prob

class autoMod(commands.Cog):
    def __init__(self, bot):
        self.total_messages = 0
        self.substring_deleted_messages = 0
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

        self.bot = bot

    @commands.command()
    async def reload(self,ctx):

        print(f"sender id:{ctx.author.id}\n bot owner id:212318242247671808\n")

        if ctx.author.id != 212318242247671808:

            return

        for word in self.black_list:
            self.blacklsited_keyword_processor.remove_keyword(word)

        for word in self.valid_words:
            self.valid_keyword_processor.remove_keyword(word)

        self.black_list = []
        self.white_list = []

        try:
            # Load the blacklisted words.
            with open('data/wordblacklist.json') as wordlist:
                self.black_list = json.load(wordlist)
        
                for word in self.black_list:
                    self.blacklsited_keyword_processor.add_keyword(word)
        except Exception as e:
            print(e)
        
        try:
            # Load the non vulgar english words.
            with open('data/valid_words.json') as valid_words:
                self.white_list = json.load(valid_words)

                for word in self.white_list:
                    self.valid_keyword_processor.add_keyword(word)
        except Exception as e:
            print(e)

        print("Keywords updated!")

    def directStringMatch(self,keywords_found,message,ctx):
        if len(keywords_found) > 0:
            print(f"Detected {keywords_found} in: {message} \n")
            # f = open("logfile.txt", "a",encoding="utf-8")
            # f.write(f"Direct Match: Detected {keywords_found} in: {message} \n")
            # f.close()              
            return True

    def substringMatch(self,users_message,ctx):

        list_of_words = ctx.content.split(" ")
        word_found = False

        for space_split_word in list_of_words:

            space_split_valid_words = self.valid_keyword_processor.extract_keywords(space_split_word.lower())

            if len(space_split_valid_words) > 0:
                # print(f"{space_split_valid_words} is a valid word.")
                continue         

            for blacklisted_word in self.black_list:

                # Skip current blacklisted word if it has more characters than the users message.
                if len(blacklisted_word) > len(space_split_word):
                    continue

                try:
                    # Iterate for the total length of the users message.
                    for i in range(0,len(space_split_word) - len(blacklisted_word) + 1) :
                        # print(f"index:{i} of { len(space_split_word) - len(blacklisted_word) } ")

                        # Set substring to the length of the blacklisted word we are matching against.
                        substring = space_split_word[i:len(blacklisted_word) + i].lower()
                        # print(f"{substring} of {space_split_word}")

                        # Checks if substrings length is that of the word were checking against.
                        # Break here to prevent a false positive.
                        if not len(substring) > 3:
                            break

                        # Determine total characters the substring has different compared to the blacklisted word.
                        edit_distance = editdistance.eval(blacklisted_word,substring)

                        # Checks how many letters substring deviates from the blacklisted word compared to a threshold.
                        if ((edit_distance <=1 and len(substring) <= 6) or (edit_distance <= 2 and len(substring) > 6)):


                            substring_valid_words = self.valid_keyword_processor.extract_keywords(substring.lower())
                             
                            if len(substring_valid_words) > 0:
                                print(f"{substring} found to be valid because {substring_valid_words} is a valid word.")
                                word_found = True
                                break

                            self.substring_deleted_messages += 1

                            print(f"{substring} matched {blacklisted_word} in: {ctx.content} with edit distance of {edit_distance}.\n")
                            f = open("logfile.txt", "a",encoding="utf-8")
                            f.write(f"substring deletions:{self.substring_deleted_messages} \ntotal messages {self.total_messages} \n{substring} matched {blacklisted_word} in: {ctx.content} with edit distance of {edit_distance}. \n")
                            f.close()

                            
                            return True

                except Exception as e:
                    print(f"!exception! \n {e}")
                    break
                
                # Exits the loop if a blacklisted word is detected.
                if word_found:
                    break
   
    @commands.Cog.listener()
    async def on_message(self, ctx):

        users_message = ctx.content.lower()

        # Ignores other bots.
        if ctx.author.bot:
            return

        self.total_messages += 1

        print(f"\n{ctx.content}")

        start_time = time.time()

        word_found = False

        keywords_found = self.blacklsited_keyword_processor.extract_keywords(users_message)
        white_listed_words = self.valid_keyword_processor.extract_keywords(users_message)

        if(self.directStringMatch(keywords_found,users_message,ctx)):
            if ctx.guild.id == 376932355434217473:
                await ctx.delete()
            word_found = True
        
        if not word_found:
            if(self.substringMatch(users_message,ctx)):
                if ctx.guild.id == 376932355434217473:
                    await ctx.delete()

        end_time = time.time()

        print(f"time taken: {end_time - start_time}")             
            
def setup(bot):
    bot.add_cog(autoMod(bot))