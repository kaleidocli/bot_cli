import atexit
import asyncio
import logging

import discord
from discord.ext import commands
import discord.errors as discordErrors
from discord.ext.commands.cooldowns import BucketType

from cogs.avasoul_pack import avaThirdParty
from cogs.configs import SConfig
from cogs.avasoul_pack.var import varMaster







dummy_config = SConfig()
extensions = [  'jishaku',
                # 'cogs.misc',
                # 'cogs.audio',
                # 'cogs.pydanboo',
                # 'cogs.tictactoe', 
                # 'cogs.hen',
                # 'cogs.guess',
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
    resp = input("| Pick a profile (default==[{}]): \n|= [{}]\n| > ".format(dummy_config.default_profile, ']\n|= ['.join(tuple(dummy_config.PROFILES.keys()))))
    if not resp: continue
    try: dummy_config.PROFILES[resp]
    except KeyError: print("| <!> Invalid profile <!>\n===============\n"); continue
    conf = input(f"| Choosing profile [{resp}]? (y/n)\n| > ")
    if conf == 'y': break

dummy_config.configProfile(resp)






# ================== INITIALIZING ==================

client = commands.Bot(command_prefix=dummy_config.PREFIX)

client.myconfig = SConfig()
client.myconfig.configProfile(resp)
client.thp = avaThirdParty.avaThirdParty(client=client)

client.realready = False
# client.IGNORE_LIST = []     # This list is not for banning! Instead, for temporary disabling command
client.varMaster = varMaster.varMaster()
client.owner_id = client.myconfig.owner_id
client.owner = client.get_user(client.owner_id)
client.support_server_invite = client.myconfig.support_server_invite

client.remove_command('help')






# ================== LOGGING ==================

logging.basicConfig(
                    filename=client.myconfig.logger,
                    filemode='a',
                    level=logging.WARNING,
                    format='============= %(asctime)s,%(msecs)d %(name)s %(levelname)s =============\n%(message)s\n\n\n',
                    datefmt='%H:%M:%S',
                    )
client.myLog = logging.getLogger('main')




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
            await message.channel.send(f"> {message.author.mention}, my prefix is **`{client.myconfig.PREFIX[0]} `** (remember, `cli help`, not `Cli help`)"); return
    if message.author.id in client.varMaster.varSys.ignore_list: return      # This list is not for banning! Instead, for temporary disabling command
    await client.process_commands(message)






# ================== TOOLS ==================

def prepformain(config):
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
    client.run(config.TOKEN, bot=config.IS_BOT, reconnect=True)

def exitest():
    print("=========================== EXIT HERE ===================================")






if __name__ == '__main__':
    atexit.register(exitest)
    prepformain(client.myconfig)
