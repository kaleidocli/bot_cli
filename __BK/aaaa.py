import discord
from discord.ext import commands
#from discord.ext.commands import Bot, BucketType

from os import listdir
from io import BytesIO
import importlib
import sys
import random
import asyncio
import json
from datetime import datetime

from PIL import Image

import aiohttp

help_dict = {}
ava_dict = {}

extensions = ['cogs.error_handler', 'cogs.ai', 'cogs.audio', 'cogs.pydanboo', 'cogs.tictactoe', 'cogs.custom_speech', 'cogs.hen', 'cogs.avasoul', 'cogs.guess']
TOKEN = 'NDQ5Mjc4ODExMzY5MTExNTUz.Dl2k3A.pGUlnO4HDB2xCH31iXa3uTUJxqA'
#TOKEN = 'NDQ2NDMxODcyNTQ1ODQ5MzU0.Dm4nJQ.KXmpoZjn47UMNoPSsT34hq_NiQo'                    #thebluecat

client = commands.Bot(command_prefix = '>')
client.remove_command('help')
session = aiohttp.ClientSession()

@client.event
async def on_ready():
    await client.loop.run_in_executor(None, help_dict_plugin)
    await client.loop.run_in_executor(None, settings_plugin)
    await client.change_presence(game=discord.Game(name='with aknalumos <3'))
    print("|||||   THE BOT IS READY   |||||")

def check_id():
    def inner(ctx):
        return ctx.message.author.id == '214128381762076672'       
    return commands.check(inner)

@client.command(pass_context=True)
async def help(ctx, *args):
    global help_dict
    raw = list(args)

    # Overall help
    if not raw:
        box = discord.Embed(
            title = '**K A L E I D O S C O P E    C L I**',
            description = """A talking bot with some tiny functions.
                            ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ """,
            colour = discord.Colour(0xB1F1FA)
        )
        box.set_footer(text="""
                            by aknalumos#7317""")
        box.set_thumbnail(url='https://cdn.discordapp.com/avatars/449278811369111553/d4a3085e1b4a9b77d51abf8da3ebcc22.jpg')
        box.add_field(name='Config commands', value='help | setting | invite | dir', inline=False)
        box.add_field(name='Audio', value='join | leave | stop | volume | cli | yolo ', inline=False)
        box.add_field(name='NSFW (`-help nsfw`)', value='hen | nhen | dhen ', inline=False)
        box.add_field(name='Miscellaneous (`-help game`)', value='custom_speech | guess | ttt', inline=False)
    # Specific help
    else:
        des = f"『**Description**』\n{help_dict[raw[0]]['description']}\n\n『**Syntax**』\n{help_dict[raw[0]]['syntax']}\n\n『**Note**』\n{help_dict[raw[0]]['note']}\n\n『**Aliase**』\n{help_dict[raw[0]]['aliase']}"
        box = discord.Embed(
            title = raw[0],
            description = des,
            colour = discord.Colour(0xB1F1FA)           
        )


    await client.say(embed=box)

@client.command()
@check_id()
async def invite():
    await client.say("Hey use this to invite me -> https://discordapp.com/api/oauth2/authorize?client_id=449278811369111553&permissions=238157120&scope=bot")

@client.command(pass_context=True)
async def ping(ctx, *args):
    if ctx.message.content: await client.send_message(ctx.message.channel, f"```{ctx.message.content}```\n{ctx.message.content}"); print(type(ctx.message.content))
    else: await client.say("`Ping!`")
    print(args, type(args[1]))

@client.command(pass_context=True)
@check_id()
async def setting(ctx, *args):
    raw = list(args)

    if len(raw) <= 2:
        if raw[0].lower() == 'nsfw':
            if raw[1] == 'on':
                if ctx.message.server.id in list(client.settings.keys()):
                    client.settings[ctx.message.server.id]['nsfw_mode'] = True
                    await client.loop.run_in_executor(None, settings_updating)
                    await client.send_message(ctx.message.channel, ":unlock: `NSFW` is now **enabled**.")
                else:
                    client.settings[ctx.message.server.id] = await setting_create()
                    client.settings[ctx.message.server.id]['nsfw_mode'] = True
                    await client.loop.run_in_executor(None, settings_updating)
                    await client.send_message(ctx.message.channel, ":unlock: `NSFW` is now **enabled**.")
            elif raw[1] == 'off':
                if ctx.message.server.id in list(client.settings.keys()):
                    client.settings[ctx.message.server.id]['nsfw_mode'] = False
                    await client.loop.run_in_executor(None, settings_updating)
                    await client.send_message(ctx.message.channel, ":lock: `NSFW` is now **disabled**.")
                else:
                    client.settings[ctx.message.server.id] = await setting_create()
                    client.settings[ctx.message.server.id]['nsfw_mode'] = False   
                    await client.loop.run_in_executor(None, settings_updating)
                    await client.send_message(ctx.message.channel, ":lock: `NSFW` is now **disabled**.")                 
            else:
                await client.say(':no_entry_sign: Please use the right syntax.')
        else:
            await client.say(':no_entry_sign: Please use the right syntax.')
    else:
        await client.say(':no_entry_sign: Please use the right syntax.')

@client.command(pass_context=True)
async def settings(ctx):
    info = ''

    srvr_settings = client.settings[ctx.message.server.id]
    for key in list(srvr_settings.keys()):
        info += f"| **{key}**: `{srvr_settings[key]}`"
    await client.say(info)

@client.command(pass_context=True, help='Shutdown the bot.')
@check_id()
async def shutdown(ctx):
    await client.say(f":wave: Bot's successfully shut down by {ctx.message.author}!")
    #exit()

@client.command(pass_context=True)
@check_id()
async def takethis(ctx, *args):
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
        await client.send_file(ctx.message.channel, 'imaging/ascii_out.txt')
        print('DONE')



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
    if message.author == client.user:
        return
    if message.author.bot: return

#Generate random file's name from the path
async def file_gen_random(path):
    file_name = ''
    file_name = await client.loop.run_in_executor(None, random.choice, await client.loop.run_in_executor(None, listdir, path))
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