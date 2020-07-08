import discord
import sqlite3

from discord.ext import commands


# def automodInitiator():
#     conn = sqlite3.connect('./data/guildSettings.db')
#     c = conn.cursor()
#     sql = "SELECT * FROM modbot_guild_settings"
#     c.execute(sql)
#     result = c.fetchall()
#     conn.close()
#     return result


guild_id = None
blacklist_enabled = None
deepStringEnabled = None
blacklist = None


logfile = {}
conn = sqlite3.connect('./data/guildSettings.db')
c = conn.cursor()


def initNewServer(guild_id):

    initModBotSettingsSQL = '''INSERT INTO modbot_guild_settings(
            guild_id,enable_blacklist,enable_deepStringMatch,
            blacklist) VALUES(?,?,?,?)'''

    c.execute(initModBotSettingsSQL,
              (int(guild_id), "False", "False", "Default"))

    conn.commit()


def getAllModbotSettings():
    sql = "SELECT * FROM modbot_guild_settings"
    c.execute(sql)
    return c.fetchall()


def getModbotServerSettings(guild_id):
    sql = "SELECT * FROM modbot_guild_settings WHERE guild_id = ?"
    c.execute(sql, (int(guild_id),))
    return c.fetchall()


def enable_blacklist(ctx):

    print(ctx.guild.id)

    if ctx.author.id == ctx.guild.owner.id:
        sql = '''UPDATE modbot_guild_settings
                SET enable_blacklist = "True"
                WHERE guild_id = ?
                '''
        data = (int(ctx.guild.id),)

        c.execute(sql, data)
        conn.commit()


def disable_blacklist(ctx):

    if ctx.author.id == ctx.guild.owner.id:
        sql = '''UPDATE modbot_guild_settings
                SET enable_blacklist = "False"
                WHERE guild_id = ?'''
        c.execute(sql, (ctx.guild.id,))
        conn.commit()


def enable_deepStringMatch(ctx):
    if ctx.author.id == ctx.guild.owner.id:
        sql = '''UPDATE modbot_guild_settings
                SET enable_deepStringMatch = "True"
                WHERE guild_id = ?
                '''
        data = (int(ctx.guild.id),)

        c.execute(sql, data)
        conn.commit()


def disable_deepStringMatch(ctx):
    if ctx.author.id == ctx.guild.owner.id:
        sql = '''UPDATE modbot_guild_settings
                SET enable_deepStringMatch = "False"
                WHERE guild_id = ?
                '''
        data = (int(ctx.guild.id),)

        c.execute(sql, data)
        conn.commit()
