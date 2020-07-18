import discord
import sqlite3

from discord.ext import commands


logfile = {}
conn = sqlite3.connect("./data/blacklists.db")
c = conn.cursor()


def initNewServer(guild_id):
    sql = """INSERT INTO blacklists(guild_id,'')"""
    c.execute(sql, (guild_id, ''))
    print("initialized blacklist DB entry for {}".format(guild_id))


def getAllBlacklists():
    sql = "SELECT * FROM blacklists"
    c.execute(sql)
    return c.fetchall()


def getBlacklist(guild_id):
    sql = "SELECT * FROM blacklists WHERE guild_id = ?"
    c.execute(sql, (int(guild_id),))
    return c.fetchall()


def setBlacklist(guild_id, csv):
    sql = """INSERT INTO blacklists(guild_id, blacklist_csv)"""


def deleteServer(guild_id):
    sql = "DELETE FROM blacklists WHERE guild_id = id"
    c.execute(sql, (guild_id,))
    print(f"Deleted server entry {guild_id}")
