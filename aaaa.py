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
# blacklist = []
minikeylist = []
char_dict = {'a': '\U0001f1e6', 'b': '\U0001f1e7', 'c': '\U0001f1e8', 'd': '\U0001f1e9', 'e': '\U0001f1ea', 'f': '\U0001f1eb', 'g': '\U0001f1ec', 'h': '\U0001f1ed', 'i': '\U0001f1ee', 'j': '\U0001f1ef', 'k': '\U0001f1f0',
            'l': '\U0001f1f1', 'm': '\U0001f1f2', 'n': '\U0001f1f3', 'o': '\U0001f1f4', 'p': '\U0001f1f5', 'q': '\U0001f1f6', 'r': '\U0001f1f7', 's': '\U0001f1f8', 't': '\U0001f1f9', 'u': '\U0001f1fa', 'v': '\U0001f1fb', 'w': '\U0001f1fc', 'x': '\U0001f1fd', 'y': '\U0001f1fe', 'z': '\U0001f1ff'}

extensions = [  'jishaku',
                # 'cogs.audio',
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
client.ignore_list = []
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
    await client.change_presence(activity=discord.Game(name='with aknalumos <3 With prefix: [cli ]'))
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
            await message.channel.send(f"> {message.author.mention}, my prefix is **`{config.prefix[0]}`**!"); return
    if message.author.id in client.ignore_list: return
    await client.process_commands(message)



# ================== MISC ==================

@client.command()
async def ping(ctx, *args):
    embed = discord.Embed(description=f":stopwatch: **`-{round(client.latency*1000, 2)}`** ms", color=0xFFC26F)
    await ctx.send(embed=embed)

@client.command()
async def aknalumos(ctx, *args):
    await ctx.send("Aknalumos' best friend.")

@client.command()
@check_id()
async def braillize(ctx, *args):
    session = aiohttp.ClientSession()
    raw = list(args)
    if raw:
        try: 
            size = int(raw[0])
            if size < 2: size = 2
        except: size = 2
    else: size = 2
    package = ctx.message.attachments
    print(package)
    
    def magic(Image_obj, size):
        average = lambda x: sum(x)/len(x) if len(x) > 0 else 0
        start = 0x2800
        char_width = size             #DF=10
        char_height = char_width * 2
        dither = 0              #DF=10
        sensitivity = 0.72       #DF=0.8
        char_width_divided = round(char_width / 2)
        char_height_divided = round(char_height / 4)
        #filename = "../Pictures/Anthony Foxx official portrait.jpg"
        #filename = "../Pictures/bait k.jpg"
        #filename = "sample.png"

        base = Image_obj
        match = lambda a, b: a < b if "--invert" in sys.argv else a > b
        def image_average(x1, y1, x2, y2):
            return average([average(base.getpixel((x, y))[:3]) for x in range(x1, x2) for y in range(y1, y2)])
        def convert_index(x):
            return {3: 6, 4: 3, 5: 4, 6: 5}.get(x, x)

        seq = ''; allseq = ''

        for y in range(0, base.height - char_height - 1, char_height):
            for x in range(0, base.width - char_width - 1, char_width):
                byte = 0x0
                index = 0
                for xn in range(2):
                    for yn in range(4):
                        avg = image_average(x + (char_height_divided * xn), y + (char_width_divided * yn), x + (char_height_divided * (xn + 1)), y + (char_width_divided * (yn + 1)))
                        if match(avg + random.randint(-dither, dither), sensitivity * 0xFF):
                            byte += 2**convert_index(index)
                        index += 1
                # ONE ROW
                seq = seq + chr(start + byte)
            # ALL ROWS
            allseq = allseq + seq + '\n'
            seq = ''
        return allseq
    #H1068 W800

    async with session.get(package[0]['proxy_url']) as resp:
        bmage = await resp.read()
        bmg = BytesIO(bmage)
        #img = Image.frombytes('RGBA', (package[0]['height'], package[0]['width']), bmage)
        img = Image.open(bmg)

        a = magic(img, size)
        with open('imaging/ascii_out.txt', 'w', encoding='utf-8') as f:
            f.write(a)
        await ctx.send_file(file=('result.png', 'imaging/ascii_out.txt'))
        print('DONE')
   
@client.command()
async def say(ctx, *args):
    raw = list(args)

    if not args: await ctx.send('Say WOTTTTT??'); return

    if random.choice([True, False]):
        random.shuffle(raw)
        try: await ctx.message.delete()
        except discordErrors.Forbidden: pass
        await ctx.send(f"{' '.join(raw)}".lower().capitalize())
    elif msg_bank:
        try: 
            temp = random.choice(msg_bank)
            try: await ctx.message.delete()
            except discordErrors.Forbidden: pass
            await ctx.send(temp.content)
        except AttributeError:
            temp = random.choice(msg_bank)
            try: await ctx.message.delete()
            except discordErrors.Forbidden: pass
            await ctx.send(embed=temp.embeds[0])
    else:
        random.shuffle(raw)
        try: await ctx.message.delete()
        except discordErrors.Forbidden: pass
        await ctx.send(f"{' '.join(raw)}".lower().capitalize())


msg_bank = []; memo_mode = False; cur_learning = []
@client.command()
@check_id()
async def memorize(ctx, *args):
    global memo_mode
    global cur_learning
    global msg_bank

    # Console
    try:
        if args[0] == 'stop':
            if not cur_learning[0].cancelled():
                cur_learning[0].cancel()
                await ctx.send(":white_check_mark:")
                memo_mode = False; return
            else: await ctx.send(":x:"); return
    except IndexError: pass

    # Memo mode check
    if memo_mode: await ctx.send("Chotto chotto, i've already been memorizing another channel!"); return

    # Channel's id      ||      Default count
    try: channel_id = int(args[0])
    except IndexError: channel_id = ctx.channel.id
    except ValueError: await ctx.send(":warning: Invalid channel's id"); return
    try: 
        df_count = int(args[1])
        if df_count >= 1000:
            df_count = int(args[1])
    except (IndexError, ValueError): df_count = 25

    # Init
    await ctx.send(f"Memorizing anxima {df_count} of channel **`{channel_id}`**...")
    memo_mode = True
    msg_bank = []
    a = client.loop.create_task(memorizing(channel_id, df_count))
    try: cur_learning[0] = a
    except IndexError: cur_learning.append(a)

@client.command()
@commands.cooldown(1, 5, type=BucketType.guild)
async def stick(ctx, *args):
    global char_dict
    try: msg = await ctx.channel.get_message(int(args[0]))
    except IndexError: await ctx.send("Missing `message_id`"); return
    except ValueError: await ctx.send("Invalid `message_id`"); return

    try: sticker = ''.join(args[1:])
    except IndexError: await ctx.send("Missing `sticker`"); return

    count = 0; limit = 10
    for stick in sticker:
        if count > limit: return
        await msg.add_reaction(char_dict[stick.lower()])
        count += 1

@client.command(aliases=['ctd'])
@check_id()
async def countdown(ctx, *args):
    try: duration = int(args[0])
    except IndexError: await ctx.send(":warning: Missing `duration`"); return
    except TypeError: await ctx.send(":warning: Invalid `duration`"); return

    msg_a = ' '.join(args[1:])
    try: answer = msg_a.split(' || ')[1]
    except IndexError: answer = ''
    try: msg = msg_a.split(' || ')[0]
    except IndexError: msg = msg

    for tick in range(duration):
        await ctx.send(f"**{msg}** :stopwatch: **`{duration - tick}`** secs", delete_after=1)
        await asyncio.sleep(1)

    if answer: await ctx.send(answer)

@client.command()
@commands.cooldown(1, 5, type=BucketType.guild)
async def typestuff(ctx, *args):
    try: await client.get_channel(int(args[0])).trigger_typing(); return
    except (IndexError, TypeError): pass
    await ctx.trigger_typing()

@client.command()
@commands.cooldown(1, 2, type=BucketType.user)
async def act(ctx, *, args):
    acts = {'yay': 'https://imgur.com/dvKPLJH.gif',
            'mumu': 'https://imgur.com/UEA7ME0.gif',
            'yaya': 'https://imgur.com/BsHjshO.gif',
            'huray': 'https://imgur.com/oayh25M.gif',
            'nom': 'https://imgur.com/QzH4Irq.gif',
            'shake': 'https://imgur.com/yG86BOm.gif',
            'eto': 'https://imgur.com/nmjwmiW.gif',
            'sneak': 'https://imgur.com/QzotxLT.gif',
            'scared': 'https://imgur.com/6a1v0oK.gif',
            'aaa': 'https://imgur.com/2xS3kXK.gif',
            'snack': 'https://imgur.com/eCfbVBK.gif',
            'zzz': 'https://imgur.com/N1Sv2hC.gif'}

    if args == 'all' or not args: await ctx.send(f"`{'` `'.join(acts.keys())}`"); return

    temb = discord.Embed(colour=0x36393E)
    try: temb.set_image(url=acts[args])
    except KeyError: return
    await ctx.send(embed=temb)

@client.command()
@commands.cooldown(1, 10, type=BucketType.guild)
async def minikey(ctx, *args):
    global minikeylist
    max_player = 3
    players = {}

    # Players get
    try:
        max_player = int(args[0])
        if max_player < 2: max_player = 2
    except (ValueError, IndexError): pass

    if ctx.channel.id in minikeylist: await ctx.send(":warning: Game's already started in this channel!"); return
    minikeylist.append(ctx.channel.id)

    introm = await ctx.send(f":key:**`{max_player}`**:key: `minigame`|**WHO GOT THE KEY** :key:**`{max_player}`**:key:")
    await introm.add_reaction('\U0001f511')
    await asyncio.sleep(1)
    def RC(reaction, user):
        return reaction.emoji == '\U0001f511' and user.id not in list(players.keys())

    # Queueing
    while True:
        try: pack = await client.wait_for('reaction_add', timeout=10, check=RC)       # reaction, user
        except asyncio.TimeoutError:
            if len(list(players.keys())) >= 3: max_player = len(list(players.keys()))
            else: await ctx.send(f":warning: Requires **{max_player}** to start!"); minikeylist.remove(ctx.channel.id); return

        cur_player = max_player
        players[pack[1].id] = [False, pack[1]]
        await introm.edit(content=introm.content+f"\n:key: [**{pack[1].name}**] has joined the game.")
        if len(list(players.keys())) == max_player: break

    # Whisper
    while True:
        KEYER = random.choice(list(players.keys()))
        players[KEYER] = [True, players[KEYER][1]]
        try: await players[KEYER][1].send(":key: <---- *Keep it*"); break
        except discordErrors.Forbidden: pass

    await ctx.send(f":key::key::key: Alright, **{max_player} seekers!** Ping who you doubt. Ping wrong, you're dead, or else, hoo-ray~~ **GAME START!!**")

    def MC(message):
        try: tar = message.mentions[0]
        except (TypeError, IndexError): return False
        return message.author.id in list(players.keys()) and tar.id in list(players.keys())

    while True:
        try: resp = await client.wait_for('message', timeout=180, check=MC)
        except asyncio.TimeoutError: await ctx.send(":warning: Game ended due to afk."); break
        
        # SEEKER
        if not players[resp.author.id][0]:
            if players[resp.mentions[0].id][0]: await ctx.send(f"<:laurel:495914127609561098> **SEEKER WON!** Congrats, {resp.author.mention}! You caught the *keeper* ----> ||{resp.mentions[0]}||!!"); break
            else:
                await ctx.send(f"{resp.author.mention}... ***OOF***"); cur_player -= 1
                del players[resp.author.id]
        
        # KEEPER
        else:
            pock = players[resp.mentions[0].id]
            if pock[0]: await ctx.send(f"<:laurel:495914127609561098> **SEEKER WON!** The *keeper* killed themselves.. GG {resp.author.mention}"); break
            else:
                await ctx.send(f"{pock[1].mention}... ***KILLED***"); cur_player -= 1
                del players[pock[1].id]

        if cur_player == 1:
            await ctx.send(f"<:laurel:495914127609561098> **KEEPER WON!** Nice one, {players[KEYER][1].mention}!"); break

    minikeylist.remove(ctx.channel.id)



# ================== TOOLS ==================

async def memorizing(channel_id, df_count):
    global msg_bank
    global memo_mode
    count = 0

    def C_check(m):
        return m.channel.id == channel_id

    while count < df_count:
        msg = await client.wait_for('message', check=C_check)

        # Mention check
        if msg.mentions: continue

        # Attachment check
        try: msg.content = msg.attachments[0].url
        except IndexError: pass
            
        print(count)
        msg_bank.append(msg)
        count += 1
    memo_mode = False

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
        client.load_extension(extension)
        client.load_count += 1
    client.load_extension('cogs.avasoul_pack.avaAvatar')
    client.load_extension('cogs.avasoul_pack.avaDungeon')
    client.run(TOKEN, bot=True, reconnect=True)

def exitest():
    print("=========================== EXIT HERE ===================================")



if __name__ == '__main__':
    atexit.register(exitest)
    prepformain()








