import atexit
import asyncio

import discord
from discord.ext import commands
import discord.errors as discordErrors
from discord.ext.commands.cooldowns import BucketType

from cogs.avasoul_pack import avaThirdParty
from cogs.configs import SConfig







config = SConfig()
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
                'cogs.avasoul_pack.avaDBC',
                'cogs.error_handler']   # Always put error_handler at the BOTTOM!





# ================== CONFIGURATING ==================

while True:
    resp = input("| Pick a profile (default==[{}]): \n|= [{}]\n| > ".format(config.default_profile, ']\n|= ['.join(tuple(config.PROFILES.keys()))))
    if not resp: resp = config.default_profile; break
    try: config.PROFILES[resp]
    except KeyError: print("| <!> Invalid profile <!>")
    conf = input(f"| Choosing profile [{resp}]? (y/n)\n| > ")
    if conf == 'y': break

TOKEN = config.PROFILES[resp][0]
PREFIX = config.PROFILES[resp][1]






# ================== INITIALIZING ==================

client = commands.Bot(command_prefix=PREFIX)

client.thp = avaThirdParty.avaThirdParty(client=client)

client.myconfig = config
client.realready = False
client.ignore_list = [422100286656479243]
client.owner_id = config.owner_id
client.owner = client.get_user(client.owner_id)
client.support_server_invite = config.support_server_invite

client.remove_command('help')






# ================== EVENTS ==================

@client.event
async def on_ready():
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

def prepformain(TOKEN):
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
    prepformain(TOKEN)
