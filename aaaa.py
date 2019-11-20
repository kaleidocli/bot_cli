import os
from io import BytesIO
import sys
import atexit
import random
import asyncio
import json
import time
from datetime import datetime

import discord
from discord.ext import commands
import discord.errors as discordErrors
from discord.ext.commands.cooldowns import BucketType

from nltk import word_tokenize
from PIL import Image
import imgurpython
import aiohttp

from cogs.configs import SConfig



config = SConfig()
TOKEN = config.TOKEN
help_dict = {}
ava_dict = {}
bulb = True

extensions = [  'jishaku',
                'cogs.misc',
                'cogs.audio',
                'cogs.pydanboo',
                'cogs.tictactoe', 
                'cogs.hen',
                'cogs.guess',
                'cogs.dbl',
                'cogs.avasoul',
                'cogs.avasoul_pack.avaHelper',
                'cogs.avasoul_pack.avaAdmin', 
                'cogs.avasoul_pack.avaTrivia', 
                'cogs.avasoul_pack.avaGuild', 
                'cogs.avasoul_pack.avaNPC', 
                'cogs.avasoul_pack.avaCombat', 
                'cogs.avasoul_pack.avaCommercial', 
                'cogs.avasoul_pack.avaSocial',
                'cogs.avasoul_pack.avaActivity',
                'cogs.avasoul_pack.avaWorkshop',
                'cogs.avasoul_pack.avaPersonal',
                'cogs.avasoul_pack.avaPersonalUtils',
                'cogs.error_handler']   # Always put error_handler at the BOTTOM!

#prefixes = {336642139381301249: 'cli ', 545945459747979265: 'cli ', 493467473870454785: 'cli '} # {Guild: [list, of, prefixes]}
# async def get_pref(bot, message):
#    if not message.guild:  # dms
#        return ">"
#    try: prefix = prefixes[message.guild.id]   # could also use a list of prefixes
#    except KeyError: prefix = '>'
#    return commands.when_mentioned_or(prefix)(bot, message)

# client = commands.Bot(command_prefix=get_pref)

# async def get_pref(bot, message):
#    return commands.when_mentioned_or(config.prefix[0])(bot, message)



# ================== INITIAL ==================

# client = commands.Bot(command_prefix=get_pref)
client = commands.Bot(command_prefix=config.prefix[0])
client.myconfig = config
client.realready = False
client.ignore_list = [422100286656479243]
client.owner_id = config.owner_id
client.owner = client.get_user(client.owner_id)
client.support_server_invite = config.support_server_invite

client.remove_command('help')

def check_id():
    def inner(ctx):
        return ctx.author.id == 214128381762076672
    return commands.check(inner)



# ================== EVENTS ==================

@client.event
async def on_ready():
    # await client.loop.run_in_executor(None, settings_plugin)
    await client.change_presence(activity=discord.Game(name='with [cli help] to start!'))
    print("|||||   THE BOT IS READY   |||||")

@client.event
async def on_guild_join(guild):
    await client.get_channel(563592973170769922).send(f":white_check_mark: **JOINED -->** `{guild.id}` | {guild.name}")

@client.event
async def on_guild_remove(guild):
    await client.get_channel(563592973170769922).send(f":x: **LEFT -->** `{guild.id}` | {guild.name}")

@client.event
async def on_message(message):
    if not client.realready: return
    if message.mentions:
        if message.mentions[0] == client.user:
            await message.channel.send(f"> {message.author.mention}, my prefix is **`{config.prefix[0]} `** (remember, `cli help`, not `Cli help`)"); return
    if message.author.id in client.ignore_list: return
    await client.process_commands(message)



# ================== TOOLS ==================

async def setting_create():
    #Return a setting dict
    setting = {'nsfw_mode': False}
    return setting

# def settings_plugin():
#     with open('config/bot_settings.json') as f:
#         try:
#             client.settings = json.load(f)
#         except IndexError: print("ERROR at <settings_plugin()>")

def prepformain():
    try:
        if client.load_count: return
    except AttributeError: client.load_count = 0
    client.extension_count = len(extensions)
    for extension in extensions:
        print(client.load_count, extension)
        if client.load_count == client.extension_count: break
        try:
            client.load_extension(extension)
            client.load_count += 1
        except discord.ext.commands.ExtensionNotFound: continue
    client.load_extension('cogs.avasoul_pack.avaAvatar')
    client.load_extension('cogs.avasoul_pack.avaDungeon')
    client.run(TOKEN, bot=True, reconnect=True)

def exitest():
    print("=========================== EXIT HERE ===================================")



if __name__ == '__main__':
    atexit.register(exitest)
    prepformain()








