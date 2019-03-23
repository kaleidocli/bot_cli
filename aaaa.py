import discord
from discord.ext import commands
import discord.errors as discordErrors
from discord.ext.commands.cooldowns import BucketType
#from discord.ext.commands import Bot, BucketType

import os
from io import BytesIO
import importlib
import sys
import random
import asyncio
import json
from datetime import datetime
from nltk import word_tokenize

from PIL import Image
import emoji

import aiohttp
import psutil

import configs

help_dict = {}
ava_dict = {}
bulb = True
blacklist = []
minikeylist = []
char_dict = {'a': '\U0001f1e6', 'b': '\U0001f1e7', 'c': '\U0001f1e8', 'd': '\U0001f1e9', 'e': '\U0001f1ea', 'f': '\U0001f1eb', 'g': '\U0001f1ec', 'h': '\U0001f1ed', 'i': '\U0001f1ee', 'j': '\U0001f1ef', 'k': '\U0001f1f0',
            'l': '\U0001f1f1', 'm': '\U0001f1f2', 'n': '\U0001f1f3', 'o': '\U0001f1f4', 'p': '\U0001f1f5', 'q': '\U0001f1f6', 'r': '\U0001f1f7', 's': '\U0001f1f8', 't': '\U0001f1f9', 'u': '\U0001f1fa', 'v': '\U0001f1fb', 'w': '\U0001f1fc', 'x': '\U0001f1fd', 'y': '\U0001f1fe', 'z': '\U0001f1ff'}

#extensions = ['cogs.error_handler', 'cogs.ai', 'cogs.audio', 'cogs.pydanboo', 'cogs.tictactoe', 'cogs.custom_speech', 'cogs.hen', 'cogs.avasoul', 'cogs.guess']
extensions = ['cogs.error_handler', 'cogs.tictactoe', 'cogs.custom_speech', 'cogs.hen', 'cogs.guess', 'jishaku', 'cogs.avasoul', 'cogs.audio']
TOKEN = configs.TOKEN

prefixes = {336642139381301249: 'cli ', 545945459747979265: 'cli ', 493467473870454785: 'cli '} # {Guild: [list, of, prefixes]}
async def get_pref(bot, message):
    if not message.guild:  # dms
        return ">"
    try: prefix = prefixes[message.guild.id]   # could also use a list of prefixes
    except KeyError: prefix = '>'
    return commands.when_mentioned_or(prefix)(bot, message)

client = commands.Bot(command_prefix=get_pref)
client.remove_command('help')

@client.event
async def on_ready():
    await client.loop.run_in_executor(None, help_dict_plugin)
    await client.loop.run_in_executor(None, settings_plugin)
    await client.change_presence(activity=discord.Game(name='with aknalumos <3'))
    print("|||||   THE BOT IS READY   |||||")

def check_id():
    def inner(ctx):
        return ctx.author.id == 214128381762076672
    return commands.check(inner)

async def help(ctx, *args):
    global help_dict
    raw = list(args)

    try: prefix = prefixes[ctx.guild.id]
    except KeyError: prefix = '>'

    # Overall help
    if not raw:
        box = discord.Embed(
            title = '**K A L E I D O S C O P E    C L I**',
            description = f"""⠀⠀ | A tiny rpg bot with tiny rpg functions.
                            ```dsconfig
⠀| For RPG commands, please use: {prefix}guide
⠀| For RPG concepts, please use: {prefix}concept
⠀| For normal commands, please use: {prefix}help```""",
            colour = discord.Colour(0xB1F1FA)
        )
        box.set_footer(text="""⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀by aknalumos#7317""")
        box.set_thumbnail(url='https://imgur.com/TW9dmXy.png')
        #box.add_field(name=f'**||** ~~Audio~~', value='`join` | `leave` | `stop` \n`volume` | `cli` | `yolo` ', inline=True)
        #box.add_field(name='**||** ~~Configuration~~', value='`help` | `setting` \n`invite` | `dir`', inline=True)
        #box.add_field(name=f'**||** ~~NSFW~~', value='`hen` | `nhen` | `dhen`', inline=True)
        box.add_field(name=f'**||** RPG', value=f'RPG games. Gather a party and real-timely fight mobs side by side to fulfill quests!\nGet degrees, work hard for money, hunt for ingredients to craft weapons and stuff. Marry your love ones, make children and teach them!\n· Use `{prefix}guide` for more info', inline=True)
        box.add_field(name=f'**||** Miscellaneous', value='`guess` | `ttt` | `say`', inline=True)
        box.add_field(name=f'⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀', value='**||** Support server! https://discord.gg/4wJHCBp')

    # Specific help
    else:
        try: des = f"『**Description**』\n{help_dict[raw[0]]['description']}\n\n『**Syntax**』\n{help_dict[raw[0]]['syntax']}\n\n『**Note**』\n{help_dict[raw[0]]['note']}\n\n『**Aliase**』\n{help_dict[raw[0]]['aliase']}"
        except KeyError: ctx.send("I'm not gonna tell ya <:fufu:508437298808094742>"); return
        box = discord.Embed(
            title = raw[0],
            description = des,
            colour = discord.Colour(0xB1F1FA)           
        )


    await ctx.send(embed=box)

@client.command()
async def statas(ctx, *args):
    mem = psutil.virtual_memory()

    temb = discord.Embed(title=f"<a:ramspin:547325170726207499> {bytes2human(mem.used)}/{bytes2human(mem.total)} ({round(mem.used/mem.total*100)}%)", colour = discord.Colour(0xB1F1FA))

    await ctx.send(embed=temb)

@client.command()
@check_id()
async def megaturn(ctx, *args):
    global bulb
    try:
        if args[0].lower() == 'on':
            if bulb: await ctx.send(":warning: Already **ON**!"); return
            bulb = True
            await ctx.send(":bell: Bot is **ON**!"); return
        elif args[0].lower() == 'off':
            if not bulb: await ctx.send(":warning: Already **OFF**!"); return
            bulb = False
            await ctx.send(":no_bell: Bot is now **OFF**!"); return           
    except IndexError: pass

@client.command()
@check_id()
async def megarestart(ctx, *args):
    await ctx.send(f"<a:dukwalk:555241951390334998> **Okai!**")
    os.system("python C:/Users/DELL/Desktop/bot_cli/aaaa.py")
    await client.logout()

@client.command()
async def invite(ctx):
    #await ctx.send("Hey use this to invite me -> https://discordapp.com/api/oauth2/authorize?client_id=449278811369111553&permissions=238157120&scope=bot")
    temb = discord.Embed(description="""[===== Invite =====](https://discordapp.com/api/oauth2/authorize?client_id=449278811369111553&permissions=104193344&scope=bot)\n◈ Before inviting this bot, you must acknowledge and accept the following:\n· High-ratio shutdown session, with random length and for **no reason**.\n| Any DM-ed complaints relevant to the incident will result in a ban.\nHowever, compensation with evidences will be responsed and should be sent in *support server*.\nTrying to DM twice on the above problem will result in a ban.\nDM abusing will result in a **"Enemy of the Pralaeyr"**.
                                \n· Buggy gameplay, low latency.\n| Any bot-abusing activities will result in a ban.\nHowever, *bot-breaking* is encouraged, and any bugs should be reported in *support server/Bug-report*
                                \n· Violation in data, balance and activities of the players.\n| This is a testing bot. You are the guinea pig. Oink <:fufu:508437298808094742>
                                \n[===== Support Server =====](https://discordapp.com/api/oauth2/authorize?client_id=449278811369111553&permissions=238157120&scope=bot)""")
    await ctx.send(embed=temb)

@client.command()
@check_id()
async def leave_guild(ctx):
    await ctx.send("Okay.......")
    await ctx.guild.leave()

@client.command()
async def ping(ctx, *args):
    embed = discord.Embed(description=f":stopwatch: **`-{round(client.latency*1000, 2)}`** ms", color=0xFFC26F)
    await ctx.send(embed=embed)

@client.command()
async def aknalumos(ctx, *args):
    await ctx.send("Aknalumos' best friend.")

@client.command()
@check_id()
async def setting(ctx, *args):
    raw = list(args)

    if len(raw) <= 2:
        if raw[0].lower() == 'nsfw':
            if raw[1] == 'on':
                if ctx.message.guild.id in list(client.settings.keys()):
                    client.settings[ctx.message.guild.id]['nsfw_mode'] = True
                    await client.loop.run_in_executor(None, settings_updating)
                    await ctx(":unlock: `NSFW` is now **enabled**.")
                else:
                    client.settings[ctx.message.guild.id] = await setting_create()
                    client.settings[ctx.message.guild.id]['nsfw_mode'] = True
                    await client.loop.run_in_executor(None, settings_updating)
                    await ctx.say(":unlock: `NSFW` is now **enabled**.")
            elif raw[1] == 'off':
                if ctx.message.guild.id in list(client.settings.keys()):
                    client.settings[ctx.message.guild.id]['nsfw_mode'] = False
                    await client.loop.run_in_executor(None, settings_updating)
                    await ctx.say(":lock: `NSFW` is now **disabled**.")
                else:
                    client.settings[ctx.message.guild.id] = await setting_create()
                    client.settings[ctx.message.guild.id]['nsfw_mode'] = False   
                    await client.loop.run_in_executor(None, settings_updating)
                    await ctx.say(":lock: `NSFW` is now **disabled**.")                 
            else:
                await ctx.say(':no_entry_sign: Please use the right syntax.')
        else:
            await ctx.say(':no_entry_sign: Please use the right syntax.')
    else:
        await ctx.say(':no_entry_sign: Please use the right syntax.')

@client.command()
async def settings(ctx):
    info = ''

    srvr_settings = client.settings[ctx.message.server.id]
    for key in list(srvr_settings.keys()):
        info += f"| **{key}**: `{srvr_settings[key]}`"
    await ctx.send(info)

@client.command()
@check_id()
async def shutdown(ctx):
    await ctx.send(f":wave: Bot's successfully shut down by {ctx.message.author}!")
    exit()

@client.command()
@check_id()
async def delele(ctx, *args):
    try:
        msg = await ctx.channel.get_message(int(args[0]))
        await msg.delete()
    # E: Invalid args
    except ValueError: await ctx.send(":warning: Invalid **`message id`**"); return
    # E: Msg not found
    except discordErrors.NotFound: await ctx.send(":warning: Message not found!"); return
    # E: No permission
    except discordErrors.Forbidden: await ctx.send("No you can't <:fufu:508437298808094742>"); return

@client.command()
@check_id()
async def takethis(ctx, *args):
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

@client.command()
async def swear(ctx, *args):
    args = list(args)
    resp = ''; resp2 = ''
    swears = {'vn': ['địt', 'đĩ', 'đụ', 'cặc', 'cằc', 'đéo', 'cứt', 'lồn', 'nứng', 'vãi', 'lồn má', 'đĩ lồn', 'tét lồn', 'dí lồn'],
            'en': ['fucking', 'cunt', 'shit', 'motherfucker', 'faggot', 'retard', 'goddamn', 'jerk']}
    subj = ['fucking', 'faggot', 'goddamn', 'jerk', 'asshole', 'freaking', 'son of the bitch']
    endp = [', you fucking hear me?', ' faggot', ', you fucking gay', ' fucking retard', ' motherfucker', ' bitch', ' faggot', ' asshole', ', dickkk', ', and fuck you', ', fucking idiots', ' you shitty head']
    expp = ['sucking', 'orally fucking', 'killing', 'fucking', 'jerking']
    fl_fuck = ['your mom', 'the whole world just to', 'sick little bastard', 'the hell outa', 'my ass']

    #model_subject = ('i', 'he', 'she', 'you', 'they', 'it', "you're", "youre", 'we', "it's", "i'm", "im", 'i')
    #model_questionWH = ('what', 'why', 'where', 'when', 'how', 'which', 'who', 'y', 'wat', 'wot')
    #model_questionYN = ('is', 'are', 'were', 'have', 'has', 'was', 'do', 'does', 'did')
    #model_sentenceNEGATIVE = ('not', "didn't", "don't", "doesn't", "isn't", "aren't", "haven't", "hasn't", "wasn't", "weren't", "didn't", "dont", "doesnt", "isnt", "arent", "havent", "hasnt", "wasnt", "werent", "hadn't", "hadnt")

    # Swear
    if args[0] not in swears.keys(): lang = 'en'
    else: lang = args[0]; args.pop(0)

    args = word_tokenize(' '.join(args).lower())

    if lang == 'en':
        for word in args:
            ## SUBJECT scan
            #if word in model_subject:
            #    scursor = args.index(word)
            #    SUBJECT = args[scursor]
            #    OBJECT = args[scursor+1:]
            #    preSUB = args[:scursor-1]
            #    _mode = 'ENGLISH'
            #    break

            _mode = 'ENGRISK'
            if random.choice([True, False]):
                if word.lower() in ['i', 'he', 'she', 'you', 'they', 'it', "you're", "youre", 'we', "it's", "i'm", "im", 'is', 'are', 'will', 'so', "don't", 'not']:
                    resp += f" {word} {random.choice(subj)}"; continue
                elif word.lower() == args[-1]:
                    resp += f" {word}{random.choice(endp)}"; continue
                elif word.lower() in ['love', 'like', 'hate', 'luv']:
                    resp += f" {word} {random.choice(expp)}"; continue
                elif word.lower() in ['fuck', 'fck', 'suck']:
                    resp += f" {word} {random.choice(fl_fuck)}"; continue
                elif word.lower() in ['bastard', 'dick', 'shit', 'bitch', 'jerk']:
                    resp += f" {word} {random.choice(['like you', 'filthy like you'])}"; continue
                resp += f" {word} {random.choice(swears[lang])}"
            else: resp += f" {word}"
        
        #for word in args:
        #    # SUBJECT scan
        #    if word in model_subject:
        #        scursor = args.index(word)
        #        SUBJECT = args[scursor]
        #        OBJECT = args[scursor+1:]
        #        preSUB = args[:scursor-1]
        #        _mode = 'ENGLISH'
        #        break

        #if _mode == 'ENGLISH':
        #    a = set(preSUB).intersection(model_questionWH)
        #    if set(preSUB).intersection(model_questionWH):
        #        __form = 'WH'
        #        preSUB.index(a[0])

        #    elif set(preSUB).intersection(model_questionYN): __form = 'YN'
        #    elif set(OBJECT).intersection(('?', '??', '???', '????', '..?')): __form = 'YN'
        #    elif set(preSUB).intersection(model_sentenceNEGATIVE): __form = 'YN'
        #    elif set(OBJECT).intersection(model_sentenceNEGATIVE): __form = 'NE'
        #    else: __form = 'NORMAL'

    else:
        for word in args:
            if random.choice([True, False]): resp += f" {word} {random.choice(swears[lang])}"
            else: resp += f" {word}"

    # Mock
    for char in resp:
        if random.choice([True, False]): resp2 += char.upper()
        else: resp2 += char

    try: await ctx.message.delete()
    except discordErrors.Forbidden: pass    

    await ctx.send(resp2)

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

@client.command()
@commands.cooldown(1, 5, type=BucketType.guild)
async def countline(ctx, *args):
    dir_main = os.path.dirname(os.path.realpath(__file__))
    dirs = ['C:/Users/DELL/Desktop/bot_cli/cogs', dir_main]
    length=0
    for dir_path in dirs:
        for f in os.listdir(dir_path):
            if not f.endswith(".py"):
                continue
            else:
                with open(dir_path+"/"+f , 'r', encoding="utf8") as b:
                    lines = b.readlines()
                    length+=len(lines)

    await ctx.send(f"<a:ramspin:547325170726207499> **`{length}` lines**")

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
    await ctx.trigger_typing()

@client.command()
@commands.cooldown(1, 2, type=BucketType.user)
async def act(ctx, *,args):
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

    if args == 'all': await ctx.send(f"`{'` `'.join(acts.keys())}`"); return

    temb = discord.Embed(colour=0x36393E)
    try: temb.set_image(url=acts[args])
    except KeyError: return
    await ctx.send(embed=temb)

@client.command()
@check_id()
@commands.cooldown(1, 10, type=BucketType.guild)
async def block(ctx, *,args):
    global blacklist
    try: target = ctx.message.mentions[0]
    except commands.CommandError: await ctx.send("Invalid `user`"); return
    except IndexError: await ctx.send("Missing `user`"); return
    blacklist.append(str(target.id))
    await ctx.send(':white_check_mark:')
    
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

@client.command()
async def source(ctx, *args):
    await ctx.send('https://github.com/kaleidocli/bot_cli')


# ==============================================


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

def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n

async def setting_create():
    #Return a setting dict
    setting = {'nsfw_mode': False}
    return setting

def settings_plugin():
    with open('config/bot_settings.json') as f:
        try:
            client.settings = json.load(f)
        except IndexError: print("ERROR at <settings_plugin()>")

def settings_updating():
    with open('config/bot_settings.json', 'w') as f:
        json.dump(client.settings, f, indent=4)

def help_dict_plugin():
    global help_dict

    with open('config/help.json') as f:
        #try:
        help_dict = json.load(f)
        #except: print("ERROR at <help_dict_plugin()>")



@client.event
async def on_message(message):
    global bulb; global prefixes; global blacklist

    if message.author == client.user:
        return
    if message.author.bot: return
    #if str(message.author.id) in blacklist: return

    #if not bulb:
    #    try:
    #        if not message.content.startswith(f'{prefixes[message.guild.id]}megaturn'): return
    #    except KeyError:
    #        if not message.content.startswith(f'>megaturn'): return
    await client.process_commands(message)

#Generate random file's name from the path
async def file_gen_random(path):
    file_name = ''
    file_name = await client.loop.run_in_executor(None, random.choice, await client.loop.run_in_executor(None, os.listdir, path))
    return file_name


if __name__ == '__main__':
    for extension in extensions:
        client.load_extension(extension)
    client.run(TOKEN)



































































    #@client.command(pass_context=True)











# ====================================

#async def guess(ctx):
 #   key = ''; fname = ''; hint_list = []; hint = ''
#
 #   #Get key
 #   key = file_gen_random('game/q')
 #   print(key)
 #   #Get image file name from the <key> folder and send it. Generate the hint.
 #   fname = file_gen_random(f'game/q/{key}')
 #   await client.send_file(ctx.message.channel, f"game/q/{key}/{fname}")
 #   for c in key:
 #       if c == ' ': hint_list.append(c)
#        else: hint_list.append('-')
#    hint = ''.join(hint_list)
#    await client.say(f":bulb: **HINT:** {hint}")
#
#    #Wait for the answer
#    answer = await client.wait_for_message(content=key, timeout=30, channel=ctx.message.channel, author=ctx.message.author)
#    try:
#        if answer.content.lower() == key.lower():
#            await client.say("**Congrats!!!**")
#    except AttributeError:
#        await client.say("**Duh loseerrrrr**")