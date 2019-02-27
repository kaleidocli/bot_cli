import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

import asyncio
import random
import json
import math
import copy
from datetime import datetime
from io import BytesIO
from os import listdir

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from dateutil.relativedelta import relativedelta
import redis
from functools import partial
import imageio
from imgurpython import ImgurClient
import numpy as np

redio = redis.Redis('localhost')

def check_id():
    def inner(ctx):
        return ctx.message.author.id == '214128381762076672'       
    return commands.check(inner)

class avasoul:
    def __init__(self, client):
        self.client = client
        self.ava_dict = {}
        self.prote_lib = {}
        self.jobs_dict = {}
        self.data_ARSENAL = {}; self.data_SUPPLY = {}; self.data_AMMU = {}
        self.data = {}
        self.environ = {}
        self.client_id = '594344297452325'
        self.client_secret = '2e29f3c50797fa6d5aad8b5bef527b214683a3ff'
        self.imgur_client = ImgurClient(self.client_id, self.client_secret)

    async def on_ready(self):
        await self.client.loop.run_in_executor(None, self.avatars_plugin)
        await self.client.loop.run_in_executor(None, self.data_plugin)
        await self.client.loop.run_in_executor(None, self.avatars_plugin_2)
        await self.prote_plugin()

    async def __cd_check(self, MSG, cmd_tag, warn):
        cdkey = cmd_tag + MSG.author.id
        if redio.exists(cdkey):
            sec = await self.client.loop.run_in_executor(None, redio.ttl, cdkey)
            sec = await self.converter('sec_to_hms', sec)
            await self.client.send_message(MSG.channel, f"{warn} Please wait `{sec[0]}:{sec[1]}:{sec[2]}`."); return False
        else: return True


    @commands.command(pass_context=True)
    async def profile(self, ctx):
        user_name = ctx.message.author.name
        user_avatar = ctx.message.author.avatar_url
        user_createpoint = ctx.message.author.created_at

        profile_box = discord.Embed(
            title = user_name.upper(),
            color = 0xB1F1FA,
            description = "WORKING on IT"
        )
        #profile_box.set_author(name=f"`joined {user_createpoint}`")
        profile_box.set_thumbnail(url=user_avatar)

        await self.client.send_message(ctx.message.channel, embed=profile_box)

    #@commands.command(pass_context=True)
    #async def milestime(self, ctx):
    #    self.client.STONE = datetime.now()
    #    self.data_updating()

    @commands.command(pass_context=True)
    async def sekaitime(self, ctx):
        year, month, day, hour, minute = await self.client.loop.run_in_executor(None, self.time_get)
        calendar_format = {'month': {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}}
        a = ['st', 'nd', 'rd']
        if day%10 in [1, 2, 3]:
            postfix = a[(day%10) - 1]
        else: postfix = 'th'
        await self.client.say(f"__=====__ `{hour:02d}:{minute:02d}` :calendar_spiral: {calendar_format['month'][month]} {day}{postfix}, {year} __=====__")
        
    @commands.command(pass_context=True)
    async def incarnate(self, ctx, *args):
        id = ctx.message.author.id; name = ctx.message.author.name

        # Create a living entity (creator-only)
        if args and ctx.message.author.id == '214128381762076672': id = ' '.join(args); name = id

        if id in list(self.ava_dict.keys()): 
            if not isinstance(self.ava_dict[id], list):
                await self.client.send_message(ctx.message.channel, f"You've already incarnate, **{self.ava_dict[id]['name']}**!"); return

        ava = {}
        year, month, day, hour, minute = await self.client.loop.run_in_executor(None, self.time_get)

        ava['name'] = name
        ava['dob'] = [day, month, year]
        ava['age'] = 0
        ava['gender'] = random.choice(['m', 'f'])
        if ava['gender'] == 'm':
            ava['height'] = random.choice(range(175, 205))
            ava['weight'] = random.choice(range(72, 90))
        else:
            ava['height'] = random.choice(range(155, 180))
            ava['weight'] = random.choice(range(50, 80))
        ava['avatar'] = 'Iris'
        ava['avatars'] = ['Iris', 'Ardena', 'Zoey']
        ava['EVO'] = 0
        ava['INT'] = 0
        ava['STA'] = 100
        ava['MAX_STA'] = 100
        ava['STR'] = 0
        ava['LP'] = 1000
        ava['MAX_LP'] = 1000
        try: ava['k/d'] = self.ava_dict[id]
        except KeyError: ava['k/d'] = [0, 0]
        ava['mobs_collection'] = {'mob': {}, 'boss': {}}
        ava["guild"] = {"name":"n/a","rank":"iron","quest":{"region.0":{"region_tier":"n/a","region_completed_quests":[]},"region.1":{"region_tier":"n/a","region_completed_quests":[]},"region.2":{"region_tier":"n/a","region_completed_quests":[]},"region.3":{"region_tier":"n/a","region_completed_quests":[]},"region.4":{"region_tier":"n/a","region_completed_quests":[]},"region.5":{"region_tier":"n/a","region_completed_quests":[]},"region.6":{"region_tier":"n/a","region_completed_quests":[]},"region.7":{"region_tier":"n/a","region_completed_quests":[]},"region.8":{"region_tier":"n/a","region_completed_quests":[]},"region.9":{"region_tier":"n/a","region_completed_quests":[]},"region.10":{"region_tier":"n/a","region_completed_quests":[]},"region.11":{"region_tier":"n/a","region_completed_quests":[]},"region.12":{"region_tier":"n/a","region_completed_quests":[]},"region.13":{"region_tier":"n/a","region_completed_quests":[]},"region.14":{"region_tier":"n/a","region_completed_quests":[]},"region.15":{"region_tier":"n/a","region_completed_quests":[]},"region.-1":{"region_tier":"n/a","region_completed_quests":[]},"region.-2":{"region_tier":"n/a","region_completed_quests":[]},"region.-3":{"region_tier":"n/a","region_completed_quests":[]},"region.-4":{"region_tier":"n/a","region_completed_quests":[]},"region.-5":{"region_tier":"n/a","region_completed_quests":[]},"region.-6":{"region_tier":"n/a","region_completed_quests":[]},"region.-7":{"region_tier":"n/a","region_completed_quests":[]},"region.-8":{"region_tier":"n/a","region_completed_quests":[]},"region.-9":{"region_tier":"n/a","region_completed_quests":[]},"region.-10":{"region_tier":"n/a","region_completed_quests":[]},"region.-11":{"region_tier":"n/a","region_completed_quests":[]},"region.-12":{"region_tier":"n/a","region_completed_quests":[]},"region.-13":{"region_tier":"n/a","region_completed_quests":[]},"region.-14":{"region_tier":"n/a","region_completed_quests":[]},"region.-15":{"region_tier":"n/a","region_completed_quests":[]}},"total_completed_quests":[]}
        ava['money'] = 100
        ava['perks'] = 0
        ava['degrees'] = ['Instinct']
        ava['arts'] = {'sword_art': {'chain_attack': 4}, 'pistol_art': {}}
        ava['right_hand'] = 'n/a'
        ava['left_hand'] = 'n/a'
        # Inventory init
        ava['inventory'] = {}
        ava['realtime_zone'] = {'current_place': 'region.0', 'current_coord': ['n/a', 'n/a'],'current_enemy': {"mob": [], "user": []}, "combat": {"handling": "2h", "buff": {}}, 'current_quest': ''}
        self.ava_dict[id] = ava 
        await self.client.say(f":white_check_mark: {ctx.message.author.mention} has successfully incarnated. **Welcome to this world!**")
        await self.client.loop.run_in_executor(None, self.avatars_updating)

    @commands.command(pass_context=True, aliases=['>'])
    async def ava(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        await self.ava_scan(ctx.message, type='all')
        await self.client.loop.run_in_executor(None, self.avatars_updating)
        
        raw = list(args)
        if raw and ctx.message.author.id == '214128381762076672': 
            if raw[0] in self.ava_dict.keys(): id = raw[0]; name = self.ava_dict[id]['name']
            else: await self.client.say("Avatar's ID not found!")
        else: id = ctx.message.author.id; name = ctx.message.author.name
        # Data paraphrase
        main_weapon = self.ava_dict[id]['right_hand']
        if main_weapon != 'n/a': main_weapon = f"`{main_weapon}`|**{self.ava_dict[ctx.message.author.id]['inventory'][main_weapon]['obj'].name}**"
        secondary_weapon = self.ava_dict[id]['left_hand']
        if secondary_weapon != 'n/a': secondary_weapon = f"`{secondary_weapon}`|**{self.ava_dict[ctx.message.author.id]['inventory'][secondary_weapon]['obj'].name}**"
        # Status
        box = f"**{name}**\n**|** `Age` · {self.ava_dict[id]['age']}\n**|** `Gender` · {self.ava_dict[id]['gender']}\n**|** `Money` · ${self.ava_dict[id]['money']}\n····················\n**||** ` LEFT` · {main_weapon}\n**||** `RIGHT` · {secondary_weapon}\n**||** `POSE` · {self.ava_dict[id]['realtime_zone']['combat']['handling']} hand\n**·** `STA` {self.ava_dict[id]['STA']}/{self.ava_dict[id]['MAX_STA']}\n**·** `LP` {self.ava_dict[id]['LP']}/{self.ava_dict[id]['MAX_LP']}\n**·** `INT` {self.ava_dict[id]['INT']}"
        # Degrees
        box = box + f"\n**|** Degrees: `{'` `'.join(self.ava_dict[id]['degrees'])}`"
        await self.client.send_message(ctx.message.channel, box)

    @commands.command(pass_context=True)
    async def prote(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        await self.ava_scan(ctx.message, type='all')
        
        curcosmetic = self.ava_dict[ctx.message.author.id]['config']['cosmetic']['current']
        __mode = 'static'
        char_name = self.ava_dict[ctx.message.author.id]['config']['cosmetic']['current']['avatar']

        # Console
        raw = list(args)
        try:
            if raw[0].lower() == 'set':
                try:
                    # AVA                
                    if raw[1] == 'avatar':
                        try:
                            if args[2].capitalize() in self.ava_dict[ctx.message.author.id]['avatars']: 
                                curcosmetic['avatar'] = args[0].capitalize()
                                await self.client.say(":white_check_mark: Done."); return
                            else: await self.client.say(f":warning: Avatar not found!\nYour avatars: `{'` `'.join(self.ava_dict[ctx.message.author.id]['avatars'])}`"); return
                        # E: Avatar not found
                        except KeyError: await self.client.say(f":moyai: Please use the following avatars:\n`{'` `'.join(self.ava_dict[ctx.message.author.id]['avatars'])}`"); return
                    # COLOURING
                    else:
                        pack = []
                        try:
                            # Check
                            raw[5]
                            # Check, as well as packaging
                            for value in raw[2:6]:
                                try: pack.append(int(value))
                                # E: Invalid value given (int expected)
                                except ValueError: await self.client.say(":warning: Invalid argument given! Please use int."); return
                            curcosmetic[raw[1]] = list(pack)
                            await self.client.say(":white_check_mark: Colour's changed!"); return
                        # E: Not enough arguments
                        except IndexError: await self.client.say(":warning: Not enough arguments! Requires 4 arguments (R, G, B, A)\n`-prote set [attribute] [R] [G] [B] [A]`"); return
                        # E: Attribute not found
                        except KeyError: await self.client.say(f":moyai: Attribute not found! Please use the following:\n`{'` `'.join(list(curcosmetic.keys()))}`"); return
                # E: Attribute not found
                except (KeyError, IndexError):
                    await self.client.say(f":moyai: Please use the following attributes:\n`{'` `'.join(list(curcosmetic.keys()))}`"); return
            elif raw[0].lower() == 'save':
                try:
                    # Overwrite
                    if raw[1] in list(self.ava_dict[ctx.message.author.id]['config']['cosmetic']['presets'].keys()):
                        if raw[1] == 'default': await self.client.say("Don't be stupid <:fufu:520602319323267082>"); return
                        # Confirmation
                        await self.client.say(":bell: Preset has already existed. **OVERWRITE?** (type `overwrite confirm` to proceed)")
                        if not await self.client.wait_for_message(content='overwrite confirm', timeout=10, author=ctx.message.author, channel=ctx.message.channel): await self.client.say(":warning: Aborted!"); return
                        # Proceed
                        self.ava_dict[ctx.message.author.id]['config']['cosmetic']['presets'][raw[1]] = curcosmetic
                        await self.client.say(":white_check_mark: Completed overwriting"); return
                    # Create new
                    else:
                        # Saves quantity check
                        if len(self.ava_dict[ctx.message.author.id]['config']['cosmetic']['presets']) >= 3: await self.client.say(":warning: You cannot have more than 2 custom presets at a time!"); return

                        # Proceed
                        self.ava_dict[ctx.message.author.id]['config']['cosmetic']['presets'][raw[1]] = curcosmetic
                        await self.client.say(f":white_check_mark: Created preset `{raw[1]}`"); return
                # E: Name not given
                except IndexError: await self.client.say(":warning: Please give the name of your preset!"); return
            elif raw[0].lower() == 'load':
                try:
                    self.ava_dict[ctx.message.author.id]['config']['cosmetic']['current'] = self.ava_dict[ctx.message.author.id]['config']['cosmetic']['presets'][raw[1]]
                    await self.client.say(":white_check_mark: Preset's loaded!"); return
                # E: Missing arg
                except IndexError: await self.client.say(":warning: Please give a preset's name!"); return
                # E: Name not found
                except KeyError: await self.client.say(":warning: Preset not found!"); return
            elif raw[0].lower() == 'presets':
                line = ""
                for name in list(self.ava_dict[ctx.message.author.id]['config']['cosmetic']['presets'].keys()):
                    if name == 'default': pass
                    line = line + f"\n· `{name}`"
                await self.client.say(f":gear: Your list of presets, {ctx.message.author.mention}{line}"); return
            elif raw[0].lower() == 'gif': __mode = 'gif'
        except IndexError: pass
        
        
        # STATIC =========
        def magiking(ctx):

            #img = Image.open('sampleimg.jpg').convert('RGBA')
            form_img = self.prote_lib['form'][0]
            char_img = self.prote_lib[char_name][random.choice(range(10))]
            char_img = char_img.resize((int(form_img.height/char_img.height*char_img.width), form_img.height))
            badge_img = self.prote_lib['badge'][self.ava_dict[ctx.message.author.id]['guild']['rank'].lower()]
            badge_img = badge_img.resize((int(badge_img.width/1.5), int(badge_img.height/1.5)))
            bg = self.prote_lib['bg'][0]
            bg = bg.resize((800, 600))
            bg = bg.filter(ImageFilter.GaussianBlur(2.6))           # prev(best)=2.6
            name_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
            degree_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
            money_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
            horizontal = Image.new('RGBA', form_img.size, (255, 255, 255, 0))

            # Font Set
            fnt_name = self.prote_lib['font']['name']            # Name
            fnt_degree = self.prote_lib['font']['degree']        # Degrees
            fnt_age = self.prote_lib['font']['age']              # Age
            fnt_kd = self.prote_lib['font']['k/d']               # K/D
            fnt_guild = self.prote_lib['font']['guild']          # Guild
            fnt_rank = self.prote_lib['font']['rank']            # Rank
            fnt_evo = self.prote_lib['font']['evo']              # evo
            fnt_money = self.prote_lib['font']['money']          # Money

            # Get info
            age = str(self.ava_dict[ctx.message.author.id]['age']).upper()
            if int(age) < 10: age = '0' + age
            evo = str(self.ava_dict[ctx.message.author.id]['EVO']).upper()
            kill = str(self.ava_dict[ctx.message.author.id]['k/d'][0]).upper()
            death = str(self.ava_dict[ctx.message.author.id]['k/d'][1]).upper()
            money = str(self.ava_dict[ctx.message.author.id]['money']).upper()
            guild = f"{self.ava_dict[ctx.message.author.id]['guild']['name']} | {self.environ[self.ava_dict[ctx.message.author.id]['guild']['name']]['name']}"
            rank = self.ava_dict[ctx.message.author.id]['guild']['rank'].upper()
            # Get text canvas
            nb = ImageDraw.Draw(name_box)
            dgb = ImageDraw.Draw(degree_box)
            mnb = ImageDraw.Draw(money_box)
            hori = ImageDraw.Draw(horizontal)
            # Write/Alligning
            nb.text((name_box.width/4, 0), self.ava_dict[ctx.message.author.id]['name'].upper(), font=fnt_name, fill=tuple(curcosmetic['name']))
            dgb.text((name_box.width/2, 0), self.ava_dict[ctx.message.author.id]['guild']['name'].capitalize(), font=fnt_degree, fill=tuple(curcosmetic['partner']))
            mnb.text((0, 0), money, font=fnt_money, fill=tuple(curcosmetic['money']))
            hori.text((3, 541), age, font=fnt_age, fill=tuple(curcosmetic['age']))
            hori.text((730 - hori.textsize(guild, font=fnt_guild)[0], 540), guild, font=fnt_guild, fill=tuple(curcosmetic['guild']))
            hori.text((730 - hori.textsize(rank, font=fnt_rank)[0], 555), rank, font=fnt_rank, fill=tuple(curcosmetic['rank']))
            hori.text((700 - hori.textsize(evo, font=fnt_evo)[0], 420), evo, font=fnt_evo, fill=tuple(curcosmetic['evo']))
            hori.text((525 , 384), death, font=fnt_kd, fill=tuple(curcosmetic['death']))
            hori.text((547 , 334), kill, font=fnt_kd, fill=tuple(curcosmetic['kill']))
            # Rotating
            name_box = name_box.rotate(90)
            degree_box = degree_box.rotate(90)
            money_box = money_box.rotate(90, center=(400, 0))

            # Middle aligning
            char_midcoordX = 50 + int((398 - char_img.width)/2)
            if char_midcoordX < 0: char_midcoordX = 0

            # Composing
            bg.alpha_composite(badge_img, dest=(800 - (badge_img.width + 5), 5))
            bg.alpha_composite(form_img)
            bg.alpha_composite(char_img, dest=(char_midcoordX, 8))            #Prev=56
            bg.alpha_composite(name_box, dest=(0, 38), source=(108, 0))
            bg.alpha_composite(degree_box, dest=(0, 10), source=(45, 0))
            bg.alpha_composite(money_box, dest=(344, 89))
            bg.alpha_composite(horizontal)

            output_buffer = BytesIO()
            bg.save(output_buffer, 'png')
            output_buffer.seek(0)
        
            #bg.show()
            return output_buffer

        # GIF ============        
        def gafiking(ctx, in_img, char_img):

            #img = Image.open('sampleimg.jpg').convert('RGBA')
            form_img = self.prote_lib['form'][0]
            char_img = self.prote_lib[char_name][random.choice(range(10))]
            char_img = char_img.resize((int(form_img.height/char_img.height*char_img.width), form_img.height))
            badge_img = self.prote_lib['badge'][self.ava_dict[ctx.message.author.id]['guild']['rank'].lower()]
            badge_img = badge_img.resize((int(badge_img.width/1.5), int(badge_img.height/1.5)))
            bg = self.prote_lib['bg'][0]
            bg = bg.resize((800, 600))
            bg = bg.filter(ImageFilter.GaussianBlur(2.6))           # prev(best)=2.6
            name_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
            degree_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
            money_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
            horizontal = Image.new('RGBA', form_img.size, (255, 255, 255, 0))

            # Font Set
            fnt_name = self.prote_lib['font']['name']            # Name
            fnt_degree = self.prote_lib['font']['degree']        # Degrees
            fnt_age = self.prote_lib['font']['age']              # Age
            fnt_kd = self.prote_lib['font']['k/d']               # K/D
            fnt_guild = self.prote_lib['font']['guild']          # Guild
            fnt_rank = self.prote_lib['font']['rank']            # Rank
            fnt_evo = self.prote_lib['font']['evo']              # evo
            fnt_money = self.prote_lib['font']['money']          # Money

            # Get info
            age = str(self.ava_dict[ctx.message.author.id]['age']).upper()
            if int(age) < 10: age = '0' + age
            evo = str(self.ava_dict[ctx.message.author.id]['EVO']).upper()
            kill = str(self.ava_dict[ctx.message.author.id]['k/d'][0]).upper()
            death = str(self.ava_dict[ctx.message.author.id]['k/d'][1]).upper()
            money = str(self.ava_dict[ctx.message.author.id]['money']).upper()
            guild = f"{self.ava_dict[ctx.message.author.id]['guild']['name']} | {self.environ[self.ava_dict[ctx.message.author.id]['guild']['name']]['name']}"
            rank = self.ava_dict[ctx.message.author.id]['guild']['rank'].upper()
            # Get text canvas
            nb = ImageDraw.Draw(name_box)
            dgb = ImageDraw.Draw(degree_box)
            mnb = ImageDraw.Draw(money_box)
            hori = ImageDraw.Draw(horizontal)
            # Write/Alligning
            nb.text((name_box.width/4, 0), self.ava_dict[ctx.message.author.id]['name'].upper(), font=fnt_name, fill=tuple(curcosmetic['name']))
            dgb.text((name_box.width/2, 0), self.ava_dict[ctx.message.author.id]['guild']['name'].capitalize(), font=fnt_degree, fill=tuple(curcosmetic['partner']))
            mnb.text((0, 0), money, font=fnt_money, fill=tuple(curcosmetic['money']))
            hori.text((3, 541), age, font=fnt_age, fill=tuple(curcosmetic['age']))
            hori.text((730 - hori.textsize(guild, font=fnt_guild)[0], 540), guild, font=fnt_guild, fill=tuple(curcosmetic['guild']))
            hori.text((730 - hori.textsize(rank, font=fnt_rank)[0], 555), rank, font=fnt_rank, fill=tuple(curcosmetic['rank']))
            hori.text((700 - hori.textsize(evo, font=fnt_evo)[0], 420), evo, font=fnt_evo, fill=tuple(curcosmetic['evo']))
            hori.text((525 , 384), death, font=fnt_kd, fill=tuple(curcosmetic['death']))
            hori.text((547 , 334), kill, font=fnt_kd, fill=tuple(curcosmetic['kill']))
            # Rotating
            name_box = name_box.rotate(90)
            degree_box = degree_box.rotate(90)
            money_box = money_box.rotate(90, center=(400, 0))

            # Middle aligning
            char_midcoordX = 50 + int((398 - char_img.width)/2)
            if char_midcoordX < 0: char_midcoordX = 0

            # Composing
            bg.alpha_composite(badge_img, dest=(800 - (badge_img.width + 5), 5))
            bg.alpha_composite(form_img)
            bg.alpha_composite(char_img, dest=(char_midcoordX, 8))            #Prev=56
            bg.alpha_composite(name_box, dest=(0, 38), source=(108, 0))
            bg.alpha_composite(degree_box, dest=(0, 10), source=(45, 0))
            bg.alpha_composite(money_box, dest=(344, 89))
            bg.alpha_composite(horizontal)

            output_buffer = BytesIO()
            bg.save(output_buffer, 'png')
            output_buffer.seek(0)

            #bg.show()
            return bg

        async def cogif(ctx):
            particles = []
            outImPart = []

            particles = imageio.mimread('C:/Users/DELL/Downloads/gif/classroom.gif', memtest=False)
            char_img = self.prote_lib[char_name][random.choice(range(10))]
            count = 0
            # This is for the sake of off-set
            while True:
                print(f"LOOOPPPPP {count}")
                if count > 60: break
                particle = particles[count]
                a = Image.fromarray(particle)

                out_img = await self.client.loop.run_in_executor(None, gafiking, ctx, a, char_img)
                asyncio.sleep(0)
                #outImPart.append(np.asarray(a))
                outImPart.append(out_img)
                count += 3

            output_buffer = BytesIO()
            #imageio.mimwrite(output_buffer, outImPart)
            outImPart[0].save(output_buffer, save_all=True, format='gif', append_images=outImPart, loop=0)
            output_buffer.seek(0)
            return await self.client.loop.run_in_executor(None, self.imgur_client.upload, output_buffer)
            #return output_buffer
        
        if __mode == 'static':
            output_buffer = magiking(ctx)
            await self.client.send_file(ctx.message.channel ,fp=output_buffer, filename='profile.png')
        elif __mode == 'gif':
            output_buffer = await cogif(ctx)         
            reembed = discord.Embed(colour = discord.Colour(0x011C3A))
            reembed.set_image(url=output_buffer['link'])
            await self.client.say(embed=reembed)
        
        await self.client.loop.run_in_executor(None, self.avatars_updating)

# ============= ACTIVITIES ==================

    @commands.command(pass_context=True, aliases=['>work'])
    async def avawork(self, ctx, *args):
        cmd_tag = 'work'
        if not await self.ava_scan(ctx.message, type='life_check'): return
        if not await self.__cd_check(ctx.message, cmd_tag, f"We haven't heard anything from **{ctx.message.author.name}**, yet."): return
        raw = ' '.join(args)

        try:
            if raw.lower() in list(self.jobs_dict.keys()):
                if self.jobs_dict[raw][0] in self.ava_dict[ctx.message.author.id]['degrees']:
                    duration = self.jobs_dict[raw][1]; salary = self.jobs_dict[raw][3]
                    self.ava_dict[ctx.message.author.id]['STA'] -= self.jobs_dict[raw][2]
                    self.ava_dict[ctx.message.author.id]['money'] += salary
                    await self.client.say(f"**{ctx.message.author.name}** has signed a *{int(duration/240)} days* contract for **${salary}** as a *{raw.capitalize()}*. Farewell!")
                else: await self.client.say(f":warning: You need `{self.jobs_dict[raw][0]}` to apply for this job!"); return
            else: await self.client.say(":x: Jobs not found!"); return
        except IndexError: await self.client.say(":warning: Please choose a job!"); return

        await self.client.loop.run_in_executor(None, self.avatars_updating)
        await self.client.loop.run_in_executor(None, partial(redio.set, f'{cmd_tag}{ctx.message.author.id}', 'working', ex=duration, nx=True))

    @commands.command(pass_context=True, aliases=['>works'])
    async def avaworks(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        job_list = []
        raw = ''.join(args)
        if raw:
            raw = raw.split('==')
            if raw[0].lower() == 'money': search_no = 3; raw = int(raw[-1])
            elif raw[0].lower() == 'time': search_no = 1; raw = int(raw[-1]) 
            elif raw[0].lower() == 'sta': search_no = 2; raw = int(raw[-1]) 
            elif raw[0].lower() == 'degree': search_no = 0; raw = raw[-1].capitalize()
            else: await self.client.say(":warning: Invalid search tag!"); return

            for job in list(self.jobs_dict.keys()):
                if raw == self.jobs_dict[job][search_no]:
                    job_list.append(job)
        else: job_list = list(self.jobs_dict.keys())


        def makeembed(top, least, pages, currentpage):
            line = ''

            line = "**-------------------- oo --------------------**\n" 
            for i in job_list[top:least]:
                line = line + f"∙ **{i.capitalize()}**\n`${self.jobs_dict[i][3]}` | `{self.jobs_dict[i][1]}s` | `{self.jobs_dict[i][2]}` STA | **Require: **`{self.jobs_dict[i][0]}`\n"
            line = line + "**-------------------- oo --------------------**" 

            reembed = discord.Embed(title = f"JOBS", colour = discord.Colour(0x011C3A), description=line)
            reembed.set_footer(text=f"Page {currentpage} of {pages}")
            return reembed
            #else:
            #    await client.say("*Nothing but dust here...*")
        
        async def attachreaction(msg):
            await self.client.add_reaction(msg, "\U000023ee")    #Top-left
            await self.client.add_reaction(msg, "\U00002b05")    #Left
            await self.client.add_reaction(msg, "\U000027a1")    #Right
            await self.client.add_reaction(msg, "\U000023ed")    #Top-right

        pages = len(job_list)//10
        if len(job_list)%10 != 0: pages += 1
        currentpage = 1
        myembed = makeembed(0, 10, pages, currentpage)
        msg = await self.client.say(embed=myembed)
        await attachreaction(msg)

        while True:
            try:    
                reaction, user = await self.client.wait_for_reaction(message=msg, timeout=15)
                if reaction.emoji == "\U000027a1" and user.id == ctx.message.author.id and currentpage < pages:
                    currentpage += 1
                    myembed = makeembed(currentpage*10-10, currentpage*10, pages, currentpage)
                    await self.client.clear_reactions(msg)
                    await self.client.edit_message(msg, embed=myembed)
                    await attachreaction(msg)
                elif reaction.emoji == "\U00002b05" and user.id == ctx.message.author.id and currentpage > 1:
                    currentpage -= 1
                    myembed = makeembed(currentpage*10-10, currentpage*10, pages, currentpage)
                    await self.client.clear_reactions(msg)
                    await self.client.edit_message(msg, embed=myembed)
                    await attachreaction(msg)
                elif reaction.emoji == "\U000023ee" and user.id == ctx.message.author.id and currentpage != 1:
                    currentpage = 1
                    myembed = makeembed(currentpage*10-10, currentpage*10, pages, currentpage)
                    await self.client.clear_reactions(msg)
                    await self.client.edit_message(msg, embed=myembed)
                    await attachreaction(msg)
                elif reaction.emoji == "\U000023ed" and user.id == ctx.message.author.id and currentpage != pages:
                    currentpage = pages
                    myembed = makeembed(currentpage*10-10, currentpage*10, pages, currentpage)
                    await self.client.clear_reactions(msg)
                    await self.client.edit_message(msg, embed=myembed)
                    await attachreaction(msg)
            except TypeError: 
                await self.client.delete_message(msg); break

    @commands.command(pass_context=True, aliases=['>edu'])
    async def avaedu(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        if not await self.area_scan(ctx, self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][0], self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][1]): await self.client.say(":warning: Educating facilities are only available within **Peace Belt**!"); return

        cmd_tag = 'edu'
        degrees = {'elementary': [2000, 0.2, 3600, 'instinct', 'n/a'], 'middleschool': [2000, 0.2, 5400, 'elementary', 'n/a'], 'highschool': [2000, 0.2, 7200, 'middleschool', 'n/a'], 'associate': [10000, 0.5, 14400, 'highschool', 3], 'bachelor': [20000, 0.4, 14400, 'associate', 4.6], 'master': [30000, 1, 28800, 'bachelor', 6], 'doctorate': [50000, 1, 28800, 'master', 9]}
        major = ['astrophysic', 'biology', 'chemistry', 'georaphy', 'mathematics', 'physics', 'education', 'archaeology', 'history', 'humanities', 'linguistics', 'literature', 'philosophy', 'psychology', 'management', 'international_bussiness', 'computer science', 'electronics', 'robotics', 'engineering']
        raw = list(args)
        
        if not raw: 
            await self.client.send_message(ctx.message.channel, f":books: There are {len(list(degrees.keys()))} levels of education:\n`{'` `'.join(list(degrees.keys()))}`")
            return
        
        # Check if the previous course has been finished yet
        if not await self.__cd_check(ctx.message, cmd_tag, f"Hey! Knowledge requires time!"): return
        
        if raw[0].lower() in list(degrees.keys()):
            try:
                if raw[0].lower() in ['associate', 'bachelor', 'master', 'doctorate'] and raw[1] in major:
                    requiring = f"{degrees[raw[0]][3].capitalize()} of {raw[1].capitalize()}"; desiring = f"{raw[0].capitalize()} of {raw[1].capitalize()}"
                    # Check if ava has the required degree or enough money, or required amount of INT (if needed)
                    if requiring not in self.ava_dict[ctx.message.author.id]['degrees']: await self.client.say(f"{ctx.message.author.mention}, you need `{requiring}` degree before getting `{desiring}` degree!"); return
                    elif self.ava_dict[ctx.message.author.id]['money'] < degrees[raw[0]][0]: await self.client.say(f"{ctx.message.author.mention}, you need **${degrees[raw[0]][0]}** to enroll this program!"); return
                    elif self.ava_dict[ctx.message.author.id]['INT'] < degrees[raw[0]][4]: await self.client.say(f"{ctx.message.author.mention}, you need **{degrees[raw[0]][4]}**`INT` to enroll this program!"); return

                    await self.client.send_message(ctx.message.channel, f":book: Program for `{desiring}` requires **${degrees[raw[0]][0]}** and **{degrees[raw[0]][2]/7200} months** to achieve.\n:scroll: As a result you'll get a `{desiring}` degree and **{degrees[raw[0]][1]} INT**. \n```Do you wish to proceed? (Y/N)```")
                else:
                    requiring = degrees[raw[0]][3].capitalize(); desiring = raw[0].upper()
                    # Check if ava has the required degree or enough money
                    if requiring not in self.ava_dict[ctx.message.author.id]['degrees']: await self.client.say(f"{ctx.message.author.mention}, you need `{requiring}` degree before getting `{desiring}` degree!"); return
                    elif self.ava_dict[ctx.message.author.id]['money'] < degrees[raw[0]][0]: await self.client.say(f"{ctx.message.author.mention}, you need **${degrees[raw[0]][0]}** to enroll this program!"); return

                    await self.client.send_message(ctx.message.channel, f":book: Program for `{desiring}` requires **${degrees[raw[0]][0]}** and **{degrees[raw[0]][2]/7200} months** to achieve.\n:scroll: As a result you'll get a `{desiring}` degree and **{degrees[raw[0]][1]} INT**. \n:bell: **Do you wish to proceed?** (Y/N)")
            except IndexError:
                await self.client.say(f":warning: {ctx.message.author.mention}, please choose one of the following fields:\n `{'` `'.join(list(major))}`"); return

            while True:
                rep = await self.client.wait_for_message(channel=ctx.message.channel, author=ctx.message.author, timeout=30)
                try:
                    if rep.content.lower() == 'y': 
                        # Initialize
                        self.ava_dict[ctx.message.author.id]['degrees'].append(raw[0].capitalize())
                        self.ava_dict[ctx.message.author.id]['INT'] += 1
                        self.ava_dict[ctx.message.author.id]['STA'] -= 80
                        self.ava_dict[ctx.message.author.id]['money'] -= degrees[raw[0]][0]
                        await self.client.loop.run_in_executor(None, self.avatars_updating)
                        # Cooldown set
                        await self.client.send_message(ctx.message.channel, f":white_check_mark: **${degrees[raw[0]][0]}** has been deducted from your account.")
                        await self.client.loop.run_in_executor(None, partial(redio.set, f'{cmd_tag}{ctx.message.author.id}', 'degreeing', ex=degrees[raw[0]][2], nx=True))
                    elif rep.content.lower() == 'n': await self.client.say(f"Assignment session of {ctx.message.author.mention} is closed."); break
                    else: pass
                except AttributeError: await self.client.say(f":warning: Assignment session of {ctx.message.author.mention} is closed."); break

        else: await self.client.say(f":moyai: {ctx.message.author.mention}, please choose one of these programs:\n `{'` `'.join(list(degrees.keys()))}`")

    @commands.command(pass_context=True, aliases=['>medic'])
    async def avamedic(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        if not await self.area_scan(ctx, self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][0], self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][1]): await self.client.say(":warning: Medical treatments are only available within **Peace Belt**!"); return

        reco = self.ava_dict[ctx.message.author.id]['MAX_LP'] - self.ava_dict[ctx.message.author.id]['LP']
        if reco == 0: await self.client.say(f":warning: {ctx.message.author.mention}, your current LP is at max!"); return

        reco_scale = reco//(self.ava_dict[ctx.message.author.id]['MAX_LP']/20)
        if reco_scale == 0: reco_scale = 1
        
        cost = int(reco*reco_scale)

        # Inform
        await self.client.say(f"<:healing_heart:508220588872171522> Dear {ctx.message.author.mention},\n------------\n· Your damaged scale: `{reco_scale}`\n· Your LP requested: `{reco}`\n· Price: `${reco_scale}/LP`\n· Cost: `${cost}`\n------------\nPlease type `confirm` within 10s to receive the treatment.")
        if not await self.client.wait_for_message(content='confirm', timeout=10, author=ctx.message.author, channel=ctx.message.channel): await self.client.say(":warning: Treatment is declined!"); return

        # Treat
        self.ava_dict[ctx.message.author.id]['money'] -= cost
        self.ava_dict[ctx.message.author.id]['LP'] = self.ava_dict[ctx.message.author.id]['MAX_LP']
        await self.client.say(f"<:healing_heart:508220588872171522> **${cost}** has been deducted from your account, {ctx.message.author.mention}!"); return
        
    @commands.command(pass_context=True, aliases=['>guild', '>g'])
    async def avaguild(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        await self.ava_scan(ctx.message)
        raw = list(args)

        try:
            if self.ava_dict[ctx.message.author.id]['guild']['name'] == 'n/a' and raw[0] != 'join':
                await self.client.say(":warning: You haven't joined any guilds yet!"); return
        except IndexError: await self.client.say(":warning: You haven't joined any guilds yet!"); return

        if not raw:
            current_place = self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place']
            user_guild = self.ava_dict[ctx.message.author.id]['guild']
            await self.client.say(f":european_castle: **`{ctx.message.author.name}`'s G.U.I.L.D card** :european_castle: \n------------------------------------------------\n**`Guild` · **`{user_guild['name']} | {self.environ[self.ava_dict[ctx.message.author.id]['guild']['name']]['name']}`\n**`Rank` · **{user_guild['rank']}\n**`Total quests done` · **{user_guild['total_completed_quests']}"); return

        if raw[0] == 'join':
            current_place = self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place']

            # Check if user in other guilds
            if self.ava_dict[ctx.message.author.id]['guild']['name'] != 'n/a':
                cost = 0
            # ... or in the same guild
            elif self.ava_dict[ctx.message.author.id]['guild']['name'] == current_place:
                await self.client.say(f":warning: You've already been in that guild, {ctx.message.author.mention}!")           ; return
            else: cost = 2000
            # Money check
            if self.ava_dict[ctx.message.author.id]['money'] < cost: await self.client.say(":warning: Insufficient balance!"); return

            await self.client.say(f":scales: **G.U.I.L.D** of `{current_place} | {self.environ[current_place]['name']}` :scales:\n------------------------------------------------\nJoining will require **${cost}** as a deposit which will be returned when you leave guild if: \n· You don't have any bad records.\n· You're alive. \n------------------------------------------------\n:bell: **Do you wish to proceed?** (y/n)")
            resp = await self.client.wait_for_message(timeout=10, author=ctx.message.author, channel=ctx.message.channel)           

            try: 
                if resp.content.lower() not in ['yes', 'y']: await self.client.say(":warning: Request declined!"); return
                self.ava_dict[ctx.message.author.id]['money'] -= cost
                self.ava_dict[ctx.message.author.id]['guild']['name'] = current_place
                await self.client.say(f":european_castle: Welcome, {ctx.message.author.mention}, to our big family all over Pralayr :european_castle:\nYou are no longer a lonely, nameless adventurer, but a member of `{current_place} | {self.environ[current_place]['name']}` guild, a part of **G.U.I.L.D**'s league. Please, newcomer, make your self at home <3"); return
            except AttributeError: await self.client.say(":warning: Request timed out!"); return

        elif raw[0] == 'leave':
            current_place = self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place']
            cost = 2000

            await self.client.say(f":bell: {ctx.message.author.mention}, leaving `{current_place} | {self.environ[current_place]['name']}` guild? (y/n)")
            resp = await self.client.wait_for_message(timeout=10, author=ctx.message.author, channel=ctx.message.channel)     
            
            try: 
                if resp.content.lower() not in ['yes', 'y']: await self.client.say(":warning: Request declined!"); return
                self.ava_dict[ctx.message.author.id]['money'] += cost
                self.ava_dict[ctx.message.author.id]['guild']['name'] = 'n/a'
                await self.client.say(f":white_check_mark: Left guild. Deposit of **${cost}** has been returned"); return
            except AttributeError: await self.client.say(":warning: Request timed out!"); return



        elif raw[0] == 'quest':
            await self.client.loop.run_in_executor(None, self.avatars_updating)
            current_quest = self.ava_dict[ctx.message.author.id]['realtime_zone']['current_quest']      #requirement: [0]Type [1]Path/... [2]Quantity
            current_place = self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place']

            if current_quest:
                # Options
                try:
                    if raw[1] == 'leave': 
                        self.ava_dict[ctx.message.author.id]['realtime_zone']['current_quest'] = ''
                        await self.client.say(f":white_check_mark: Left quest `{current_quest['branch'].split('/')[2]}` of **{self.environ[current_quest['branch'].split('/')[0]]['name']}**!")
                        return
                except IndexError: pass

                # Requirement check's type
                prog = await self.ava_manip(ctx.message, 'stt_check', current_quest['requirement'][1], 1, 0)
                if not prog: prog = 0
                if current_quest['requirement'][0] == 'status':
                    # Requirement check                
                    if prog >= current_quest['requirement'][2]:
                        # Reward
                        if current_quest['reward'][0] == 'status': await self.ava_manip(ctx.message, 'stt_adjust', current_quest['reward'][1], 'add', current_quest['reward'][2])
                        if current_quest['reward'][0] == 'money': pass
                        if current_quest['reward'][0] == 'item': pass
                        # Add to the completed_quest
                        self.ava_dict[ctx.message.author.id]['guild']['quests'][current_place]['region_completed_quests'].append(current_quest['branch'])
                        # Increase total_completed_quests by 1
                        self.ava_dict[ctx.message.author.id]['guild']['total_completed_quests'] += 1
                        # Remove current quest
                        self.ava_dict[ctx.message.author.id]['realtime_zone']['current_quest'] = ''
                        # Inform
                        await self.client.say(":white_check_mark: Rewarded!"); return
                        # Ranking check
                        if self.ava_dict[ctx.message.author.id]['guild']['rank'] == 'iron' and self.ava_dict[ctx.message.author.id]['guild']['total_completed_quests'] >= 155: 
                            self.ava_dict[ctx.message.author.id]['guild']['rank'] = 'bronze'; await self.client.say(f":beginner: Congrats, {ctx.message.author.mention}! You've been promoted to **BRONZE**!")
                        elif self.ava_dict[ctx.message.author.id]['guild']['rank'] == 'bronze' and self.ava_dict[ctx.message.author.id]['guild']['total_completed_quests'] >= 310: 
                            self.ava_dict[ctx.message.author.id]['guild']['rank'] = 'silver'; await self.client.say(f":beginner: Congrats, {ctx.message.author.mention}! You've been promoted to **SILVER**!")                            
                        elif self.ava_dict[ctx.message.author.id]['guild']['rank'] == 'silver' and self.ava_dict[ctx.message.author.id]['guild']['total_completed_quests'] >= 465: 
                            self.ava_dict[ctx.message.author.id]['guild']['rank'] = 'gold'; await self.client.say(f":beginner: Congrats, {ctx.message.author.mention}! You've been promoted to **GOLD**!")                            
                        elif self.ava_dict[ctx.message.author.id]['guild']['rank'] == 'gold' and self.ava_dict[ctx.message.author.id]['guild']['total_completed_quests'] >= 620: 
                            self.ava_dict[ctx.message.author.id]['guild']['rank'] = 'adamantite'; await self.client.say(f":beginner: Congrats, {ctx.message.author.mention}! You've been promoted to **ADAMANTITE**!")                            
                await self.client.say(f":scroll: You are currently on quest `{current_quest['branch'].split('/')[2]}` of **{self.environ[current_quest['branch'].split('/')[0]]['name']}**\n---------------\n**Progress:**\n· `{current_quest['description']}` [{prog}/{current_quest['requirement'][2]}]\n**Reward:**\n· `{current_quest['reward'][1]}` +{current_quest['reward'][2]}")
                
            else:
                # If quest's id given, accept the quest
                try: 
                    self.ava_dict[ctx.message.author.id]['realtime_zone']['current_quest'] = self.environ[self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place']]['characteristic']['quest']['main'][raw[1]]
                    await self.client.say(":white_check_mark: Quest accepted! Use `-avaquest` to check your progress."); return
                # E: Quest's id not found
                except KeyError: await self.client.say(":warning: Quest not found!"); return
                # E: Quest's id not given (and current_quest is also empty)
                except IndexError: await self.client.say(f":warning: You're not on any quests at the moment, {ctx.message.author.mention}!"); return
        
        elif raw[0] == 'quests':
            current_place = self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place']
            quest_shortcut = self.environ[current_place]['characteristic']['quest'][current_place]['main']
            quest_list = list(quest_shortcut.keys())
            try: region_completed_quests = self.ava_dict[ctx.message.author.id]['guild']['quests'][current_place]['region_completed_quests']
            except KeyError: region_completed_quests = []

            def makeembed(top, least, pages, currentpage):
                line = ''

                line = f"**···················· -- ····················**\n" 
                for i in quest_list[top:least]:
                    if quest_shortcut[i]['branch'] in region_completed_quests: marker = '__<:tick_yes:515012376962138112>__'
                    else: marker = '__<:tick_no:515012452635770882>__'
                    line = line + f"{marker} · `{i}` · **{quest_shortcut[i]['requester']}**'s quest · \n| {quest_shortcut[i]['description']} \n||| Rewards: `{quest_shortcut[i]['reward'][1]}` +{quest_shortcut[i]['reward'][2]}\n\n"
                line = line + "**···················· -- ····················**" 

                reembed = discord.Embed(title = f":scroll: `{self.environ[current_place]['name']}` · Total: {len(quest_list)} · Done: {len(region_completed_quests)}", colour = discord.Colour(0x011C3A), description=line)
                reembed.set_footer(text=f"Page {currentpage} of {pages}")
                return reembed
                #else:
                #    await client.say("*Nothing but dust here...*")
            
            async def attachreaction(msg):
                await self.client.add_reaction(msg, "\U00002b05")    #Left
                await self.client.add_reaction(msg, "\U000027a1")    #Right

            pages = len(quest_list)//5
            if len(quest_list)%10 != 0: pages += 1
            currentpage = 1
            myembed = makeembed(0, 5, pages, currentpage)
            msg = await self.client.say(embed=myembed)
            await attachreaction(msg)

            while True:
                try:    
                    reaction, user = await self.client.wait_for_reaction(message=msg, timeout=15)
                    if reaction.emoji == "\U000027a1" and user.id == ctx.message.author.id and currentpage < pages:
                        currentpage += 1
                        myembed = makeembed(currentpage*10-10, currentpage*10, pages, currentpage)
                        await self.client.edit_message(msg, embed=myembed)                        
                        await self.client.remove_reaction(msg, reaction.emoji, user)
                    elif reaction.emoji == "\U00002b05" and user.id == ctx.message.author.id and currentpage > 1:
                        currentpage -= 1
                        myembed = makeembed(currentpage*10-10, currentpage*10, pages, currentpage)
                        await self.client.edit_message(msg, embed=myembed)                        
                        await self.client.remove_reaction(msg, reaction.emoji, user)
                    elif reaction.emoji == "\U000023ee" and user.id == ctx.message.author.id and currentpage != 1:
                        currentpage = 1
                        myembed = makeembed(currentpage*10-10, currentpage*10, pages, currentpage)
                        await self.client.edit_message(msg, embed=myembed)                        
                        await self.client.remove_reaction(msg, reaction.emoji, user)
                    elif reaction.emoji == "\U000023ed" and user.id == ctx.message.author.id and currentpage != pages:
                        currentpage = pages
                        myembed = makeembed(currentpage*10-10, currentpage*10, pages, currentpage)
                        await self.client.edit_message(msg, embed=myembed)                        
                        await self.client.remove_reaction(msg, reaction.emoji, user)
                except TypeError: 
                    break

    @commands.command(pass_context=True, aliases=['>evolve'])
    async def avaevolve(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        raw = list(args)

        if not raw: await self.client.say(f":cyclone: You can spend your perks on the following attributes of your status:\n________________________\n`LP` · +5% MAX_LP\n`STA` · +10% MAX_STA\n`STR` · +0.1 STR\n`INT` · +0.1 INT\n________________________\n**Your perks:** {self.ava_dict[ctx.message.author.id]['perks']}"); return

        # Perk check
        if self.ava_dict[ctx.message.author.id]['perks'] == 0: await self.client.say(":warning: Not enough perks!"); return

        if raw[0].lower() == 'lp': self.ava_dict[ctx.message.author.id]['MAX_LP'] = self.ava_dict[ctx.message.author.id]['MAX_LP'] + int(self.ava_dict[ctx.message.author.id]['MAX_LP']/100*5)
        elif raw[0].lower() == 'sta': self.ava_dict[ctx.message.author.id]['MAX_STA'] = self.ava_dict[ctx.message.author.id]['MAX_STA'] + int(self.ava_dict[ctx.message.author.id]['MAX_STA']/100*10)
        elif raw[0].lower() == 'str': self.ava_dict[ctx.message.author.id]['STR'] += 0.1
        elif raw[0].lower() == 'int':self.ava_dict[ctx.message.author.id]['INT'] += 0.1
        # E: Attributes not found
        else: await self.client.say(":warning: Invalid attribute!")

        await self.client.say(":cyclone: Done. You can use `-ava` to recheck.")
        await self.client.loop.run_in_executor(None, self.avatars_updating)




# ============= COMMERCIAL ==================
# <!> CONCEPTS 
# <dir> acts as an id/ (type:list) used to look up the self.data.item   (aka. address)
# a <dir> (type:list) contains these info, respectively: [data_class][item_class][category][obj's id] e.g. item.arsenal.pistol.1
# Main weapon is a inventory <dir>      ||      ['item'][]

    @commands.command(pass_context=True, aliases=['>shop'])
    async def avashop(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        if not await self.area_scan(ctx, self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][0], self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][1]): await self.client.say(":warning: Shops are only available within **Peace Belt**!"); return
        current_place = self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place']
        

        raw = list(args)
        try: 
            try: 
                lookup_price = int(raw[0])
                try: lookup_weapon = raw[1]
                except IndexError: lookup_weapon = 'all'
            # E: args1 is a weapon
            except ValueError: 
                lookup_weapon = raw[0]
                try: lookup_price = int(raw[1])
                # E: args2 not given
                except IndexError: lookup_price = 'all'
                # E: args2 invalid (int expected, but str found)
                except ValueError: lookup_price = 'all'
        # E: args1 not given
        except IndexError: lookup_weapon = 'all'; lookup_price = 'all'

        async def browse():
            items = self.data['item']
            item_codes = list(items.keys())
            # Filtering OUT
            for item_code in list(items.keys()):
                if lookup_price != 'all':                
                    if items[item_code].price > lookup_price: item_codes.remove(item_code); continue  
                if lookup_weapon != 'all':
                    if lookup_weapon not in items[item_code].tags: item_codes.remove(item_code); continue

            def makeembed(top, least, pages, currentpage):
                line = ''

                line = "**------------------------------ oo ------------------------------**\n" 

                for item_code in item_codes[top:least]:
                    if 'melee' in items[item_code].tags:
                        line = line + f""" `{item_code}` <:broadsword:508214667416698882> **{items[item_code].name}** | *"{items[item_code].description}"*\n|| `『Multiplier』{items[item_code].multiplier}` · `『Speed』{items[item_code].speed}` · `『STA』{items[item_code].sta}` \n|| **`Required`** STR-{items[item_code].str}\n|| **`Price`** ${items[item_code].price}\n++ `{'` `'.join(items[item_code].tags)}`\n\n"""
                        #line = line + f""" `{item_code}` <:broadsword:508214667416698882> **{items[item_code].name}** | *"{items[item_code].description}"*\n|| **`Multiplier`** {items[item_code].multiplier} · **`Speed`** {items[item_code].speed} · **`STA`** {items[item_code].sta}**\n++ `{'` `'.join(items[item_code].tags)}` \n|| **`Required`** STR-{items[item_code].str}\n|| **`Price`** ${items[item_code].price}\n"""
                    elif 'range_weapon' in items[item_code].tags:
                        line = line + f""" `{item_code}` <:gun_pistol:508213644375621632> **{items[item_code].name}** | *"{items[item_code].description}"*\n|| `『Range』{items[item_code].range[0]}m - {items[item_code].range[1]}m`\n|| `『Accuracy』1:{items[item_code].accuracy[0]}/{items[item_code].accuracy[1]}m` · `『firing_rate』{items[item_code].firing_rate}` · `『stealth』{items[item_code].stealth}`\n|| **`Required`** STR-{items[item_code].str}/shot · STA-{items[item_code].sta}\n|| **`Price`**${items[item_code].price}\n++ `{'` `'.join(items[item_code].tags)}`\n\n"""
                        #line = line + f""" `{item_code}` <:gun_pistol:508213644375621632> **{items[item_code].name}** | *"{items[item_code].description}"*\n|| **`Range`** {items[item_code].range[0]} - {items[item_code].range[1]} m\n|| **`Accuracy`** 1:{items[item_code].accuracy[0]}/{items[item_code].accuracy[1]} m\n|| **`firing_rate`** {items[item_code].firing_rate} · **`stealth`** {items[item_code].stealth}**\n++ `{'` `'.join(items[item_code].tags)}` \n|| **`Required`** **STR**-{items[item_code].str}/shot · **STA**-{items[item_code].sta}\n|| **`Price`**${items[item_code].price}\n"""
                    elif isinstance(items[item_code], ammunition):
                        line = line + f""" `{item_code}` <:shotgun_slug:508217929532440586> **{items[item_code].name}** | *"{items[item_code].description}"*\n|| `『Damage』{items[item_code].dmg}` · `『Speed』{items[item_code].speed}`\n|| **`Price`** ${items[item_code].price}\n++ `{'` `'.join(items[item_code].tags)}`\n\n"""                        
                        #line = line + f""" `{item_code}` <:shotgun_slug:508217929532440586> **{items[item_code].name}** | *"{items[item_code].description}"*\n|| **`Damage`** {items[item_code].dmg} · **`Speed`** {items[item_code].speed}\n++ `{'` `'.join(items[item_code].tags)}` \n|| **`Price`** ${items[item_code].price}\n"""                        
                    elif isinstance(items[item_code], item):
                        line = line + f""" `{item_code}` :small_orange_diamond: **{items[item_code].name}** \n|| *"{items[item_code].description}"*\n|| **`Price`** ${items[item_code].price}\n++ `{'` `'.join(items[item_code].tags)}`\n\n"""
                        
                line = line + "**------------------------------ oo ------------------------------**" 

                reembed = discord.Embed(title = f":shopping_cart: SIEGFIELD's Market of `{current_place} | {self.environ[current_place]['name']}`", colour = discord.Colour(0x011C3A), description=line)
                reembed.set_footer(text=f"Page {currentpage} of {pages}")
                
                if line == "**------------------------------ oo ------------------------------**\n**------------------------------ oo ------------------------------**": return False
                else: return reembed
                #else:
                #    await client.say("*Nothing but dust here...*")
            
            async def attachreaction(msg):
                await self.client.add_reaction(msg, "\U000023ee")    #Top-left
                await self.client.add_reaction(msg, "\U00002b05")    #Left
                await self.client.add_reaction(msg, "\U000027a1")    #Right
                await self.client.add_reaction(msg, "\U000023ed")    #Top-right

            pages = int(len(item_codes)/5)
            if len(item_codes)%5 != 0: pages += 1
            currentpage = 1
            myembed = makeembed(0, 5, pages, currentpage)

            if not myembed and lookup_weapon != 'all' and lookup_price != 'all': await self.client.say(f":x: No result..."); return
            elif not myembed and lookup_weapon != 'all': await self.client.say(f":x: Search result for tag `{lookup_weapon}`: ..."); return
            elif not myembed and lookup_price != 'all': await self.client.say(f":x: Search result for `${lookup_price}`: ..."); return
            msg = await self.client.say(embed=myembed)
            await attachreaction(msg)

            while True:
                try:    
                    reaction, user = await self.client.wait_for_reaction(message=msg, timeout=30)
                    if reaction.emoji == "\U000027a1" and user.id == ctx.message.author.id and currentpage < pages:
                        currentpage += 1
                        myembed = makeembed(currentpage*5-5, currentpage*5, pages, currentpage)
                        await self.client.edit_message(msg, embed=myembed)                        
                        await self.client.remove_reaction(msg, reaction.emoji, user)
                    elif reaction.emoji == "\U00002b05" and user.id == ctx.message.author.id and currentpage > 1:
                        currentpage -= 1
                        myembed = makeembed(currentpage*5-5, currentpage*5, pages, currentpage)
                        await self.client.edit_message(msg, embed=myembed)                        
                        await self.client.remove_reaction(msg, reaction.emoji, user)
                    elif reaction.emoji == "\U000023ee" and user.id == ctx.message.author.id and currentpage != 1:
                        currentpage = 1
                        myembed = makeembed(currentpage*5-5, currentpage*5, pages, currentpage)
                        await self.client.edit_message(msg, embed=myembed)                        
                        await self.client.remove_reaction(msg, reaction.emoji, user)
                    elif reaction.emoji == "\U000023ed" and user.id == ctx.message.author.id and currentpage != pages:
                        currentpage = pages
                        myembed = makeembed(currentpage*5-5, currentpage*5, pages, currentpage)
                        await self.client.edit_message(msg, embed=myembed)                        
                        await self.client.remove_reaction(msg, reaction.emoji, user)
                except TypeError: 
                    await self.client.delete_message(msg); break

        await browse()

    @commands.command(pass_context=True, aliases=['>buy'])
    async def avabuy(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        if not await self.area_scan(ctx, self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][0], self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][1]): await self.client.say(":warning: You can only buy stuff within **Peace Belt**!"); return
        #await self.client.loop.run_in_executor(None, partial(redio.set, f'{cmd_tag}{ctx.message.author.id}', 'working', ex=duration, nx=True))

        raw = list(args); quantity = 1
        if not raw: await self.client.say(f":moyai: {ctx.message.author.mention} || `-avabuy [item_code] [*quantity]`"); return
        
        item_code = raw[0]
        try: 
            quantity = int(raw[1])

            # SCAM :)
            if quantity <= 0: await self.client.say("**Heyyyyyyyyy scammer-!**"); return

        # E: Quantity not given, or invalidly given
        except (IndexError, TypeError): pass
        
        # TWO TYPES of obj: Serializable-obj and Unserializable obj
        try:
            # Validation
            if isinstance(self.data['item'][item_code], ingredient): await self.client.say(f":warning: You cannot use this command to obtain the given item, {ctx.message.author.id}. Use `-trade` instead"); return

            # Money check
            if self.data['item'][item_code].price*quantity <= self.ava_dict[ctx.message.author.id]['money']:

                # SERIALIZABLE
                if self.data['item'][item_code].tags[0] in ['arsenal']:
                    # Generate item_id
                    item_id = int(await self.client.loop.run_in_executor(None, partial(redio.get, 'item_id_counter')))
                    await self.client.loop.run_in_executor(None, partial(redio.set, 'item_id_counter', str(item_id+1)))
                    # Create item in inventory (objectize included)
                    self.ava_dict[ctx.message.author.id]['inventory'][str(item_id)] = {'item_id': str(item_id), 'item_code': item_code, 'obj': self.data['item'][item_code], 'dict': self.data['item'][item_code].bkdict}
                    await self.client.loop.run_in_executor(None, self.avatars_updating)

                # UN-SERIALIZABLE
                else:
                    # Increase item_code's quantity
                    try:    
                        self.ava_dict[ctx.message.author.id]['inventory'][item_code] += quantity
                    # E: item_code did not exist. Create one, with given quantity
                    except KeyError:
                        self.ava_dict[ctx.message.author.id]['inventory'][item_code] = quantity
                    await self.client.loop.run_in_executor(None, self.avatars_updating)
                # Deduct money
                self.ava_dict[ctx.message.author.id]['money'] -= self.data['item'][item_code].price*quantity

            else: await self.client.say(":warning: Insufficience balance!"); return

        # E: Item_code not found
        except KeyError: await self.client.say(":warning: Item_code/Item_id not found!"); return


        # Greeting, of course :)
        await self.client.say(f":white_check_mark: **{quantity}** item `{self.data['item'][item_code].name}` is successfully added to your inventory! Thank you for shoping!")

    @commands.command(pass_context=True, aliases=['>i'])
    async def avainventory(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        raw = list(args)
        try: 
            try: 
                lookup_price = int(raw[0])
                try: lookup_weapon = raw[1]
                except IndexError: lookup_weapon = 'all'
            # E: args1 is a weapon
            except ValueError: 
                lookup_weapon = raw[0]
                try: lookup_price = int(raw[1])
                # E: args2 not given
                except IndexError: lookup_price = 'all'
                # E: args2 invalid (int expected, but str found)
                except ValueError: lookup_price = 'all'
        # E: args1 not given
        except IndexError: lookup_weapon = 'all'; lookup_price = 'all'        

        async def browse():
            items = self.ava_dict[ctx.message.author.id]['inventory']
            item_codes = list(items.keys())
            
            # Filtering OUT
            for item_code in list(items.keys()):
                if lookup_price != 'all':
                    # UN-SERI
                    try:
                        if self.data['item'][item_code].price > lookup_price: item_codes.remove(item_code); continue
                    # SERI
                    except TypeError:
                        if items[item_code]['obj'].price > lookup_price: item_codes.remove(item_code); continue            
                if lookup_weapon != 'all':
                    # E: SERI
                    try:
                        if lookup_weapon not in items[item_code]['obj'].tags: item_codes.remove(item_code); continue
                    # E: UN-SERI
                    except TypeError:
                        # Supp
                        try: 
                            if lookup_weapon not in self.data['item'][item_code].tags: item_codes.remove(item_code); continue
                        # Ingre
                        except KeyError: 
                            if lookup_weapon not in self.data['ingredient'][item_code].tags: item_codes.remove(item_code); continue

            def makeembed(top, least, pages, currentpage):
                line = ''

                line = "**------------------------------ oo ------------------------------**\n" 

                for item_code in item_codes[top:least]:
                    # SERIALIZABLE
                    try:
                        if 'melee' in items[item_code]['obj'].tags:
                            line = line + f""" `{item_code}` <:broadsword:508214667416698882> **{items[item_code]['obj'].name}** | *"{items[item_code]['obj'].description}"* \n|| **`Required`** STR-{items[item_code]['obj'].str}\n|| **`Price`** ${items[item_code]['obj'].price}\n++ `{'` `'.join(items[item_code]['obj'].tags)}`\n\n"""
                            #line = line + f""" `{item_code}` <:broadsword:508214667416698882> **{items[item_code]['obj'].name}** | *"{items[item_code]['obj'].description}"*\n|| **`Multiplier`** {items[item_code]['obj'].multiplier} · **`Speed`** {items[item_code]['obj'].speed} · **`STA`** {items[item_code]['obj'].sta}**\n++ `{'` `'.join(items[item_code]['obj'].tags)}` \n|| **`Required`** STR-{items[item_code]['obj'].str}\n|| **`Price`** ${items[item_code]['obj'].price}\n\n"""
                        elif 'range_weapon' in items[item_code]['obj'].tags:
                            line = line + f""" `{item_code}` <:gun_pistol:508213644375621632> **{items[item_code]['obj'].name}** | *"{items[item_code]['obj'].description}"*\n|| **`Required`** **STR**-{items[item_code]['obj'].str}/shot · **STA**-{items[item_code]['obj'].sta}\n|| **`Price`**${items[item_code]['obj'].price}\n++ `{'` `'.join(items[item_code]['obj'].tags)}` \n\n"""
                            #line = line + f""" `{item_code}` <:gun_pistol:508213644375621632> **{items[item_code]['obj'].name}** | *"{items[item_code]['obj'].description}"*\n|| **`Range`** {items[item_code]['obj'].range[0]} - {items[item_code]['obj'].range[1]} m\n|| **`Accuracy`** 1:{items[item_code]['obj'].accuracy[0]}/{items[item_code]['obj'].accuracy[1]} m\n|| **`firing_rate`** {items[item_code]['obj'].firing_rate} · **`stealth`** {items[item_code]['obj'].stealth}**\n++ `{'` `'.join(items[item_code]['obj'].tags)}` \n|| **`Required`** **STR**-{items[item_code]['obj'].str}/shot · **STA**-{items[item_code]['obj'].sta}\n|| **`Price`**${items[item_code]['obj'].price}\n\n"""
                    # UN-SERIALIZABLE
                    except TypeError:
                        # Supp
                        try:
                            if isinstance(self.data['item'][item_code], ammunition):
                                line = line + f""" `{item_code}` <:shotgun_slug:508217929532440586> **{self.data['item'][item_code].name}** | *"{self.data['item'][item_code].description}"* \n|| **`Price`** ${self.data['item'][item_code].price}\n|| **`Quantity`** {items[item_code]}\n++ `{'` `'.join(self.data['item'][item_code].tags)}`\n\n"""                        
                                #line = line + f""" `{item_code}` <:shotgun_slug:508217929532440586> **{self.data['item'][item_code].name}** | *"{self.data['item'][item_code].description}"*\n|| **`Damage`** {self.data['item'][item_code].dmg} · **`Speed`** {self.data['item'][item_code].speed}\n++ `{'` `'.join(self.data['item'][item_code].tags)}` \n|| **`Price`** ${self.data['item'][item_code].price}\n\n"""                        
                            elif isinstance(self.data['item'][item_code], item):
                                line = line + f""" `{item_code}` :small_orange_diamond: **{self.data['item'][item_code].name}** \n|| *"{self.data['item'][item_code].description}"*\n|| **`Price`** ${self.data['item'][item_code].price}\n|| **`Quantity`** {items[item_code]}\n++ `{'` `'.join(self.data['item'][item_code].tags)}`\n\n"""
                                #line = line + f""" `{item_code}` :small_orange_diamond: **{self.data['item'][item_code].name}** \n|| *"{self.data['item'][item_code].description}"*\n++ `{'` `'.join(self.data['item'][item_code].tags)}`\n|| **`Price`** ${self.data['item'][item_code].price}\n\n"""
                        # Ingre        
                        except KeyError:
                            if isinstance(self.data['ingredient'][item_code], ingredient):
                                line = line + f""" `{item_code}` <:green_ruby:520092621381697540> **{self.data['ingredient'][item_code].name}**\n|| *"{self.data['ingredient'][item_code].description}"*\n|| **`Price`** ${self.data['ingredient'][item_code].price}\n|| **`Quantity`** {items[item_code]}\n++ `{'` `'.join(self.data['ingredient'][item_code].tags)}`\n\n"""                            
                            
                line = line + "**------------------------------ oo ------------------------------**" 

                reembed = discord.Embed(title = f"INVENTORY", colour = discord.Colour(0x011C3A), description=line)
                reembed.set_footer(text=f"Page {currentpage} of {pages}")

                if line == "**------------------------------ oo ------------------------------**\n**------------------------------ oo ------------------------------**": return False
                else: return reembed
                #else:
                #    await client.say("*Nothing but dust here...*")
            
            async def attachreaction(msg):
                await self.client.add_reaction(msg, "\U000023ee")    #Top-left
                await self.client.add_reaction(msg, "\U00002b05")    #Left
                await self.client.add_reaction(msg, "\U000027a1")    #Right
                await self.client.add_reaction(msg, "\U000023ed")    #Top-right

            pages = int(len(item_codes)/5)
            if len(item_codes)%5 != 0: pages += 1
            currentpage = 1
            myembed = makeembed(0, 5, pages, currentpage)

            if not myembed and lookup_weapon != 'all' and lookup_price != 'all': await self.client.say(f":x: No result..."); return
            elif not myembed and lookup_weapon != 'all': await self.client.say(f":x: Search result for tag `{lookup_weapon}`: ..."); return
            elif not myembed and lookup_price != 'all': await self.client.say(f":x: Search result for `${lookup_price}`: ..."); return            
            msg = await self.client.say(embed=myembed)
            await attachreaction(msg)

            while True:
                try:    
                    reaction, user = await self.client.wait_for_reaction(message=msg, timeout=30)
                    if reaction.emoji == "\U000027a1" and user.id == ctx.message.author.id and currentpage < pages:
                        currentpage += 1
                        myembed = makeembed(currentpage*5-5, currentpage*5, pages, currentpage)
                        await self.client.edit_message(msg, embed=myembed)                        
                        await self.client.remove_reaction(msg, reaction.emoji, user)
                    elif reaction.emoji == "\U00002b05" and user.id == ctx.message.author.id and currentpage > 1:
                        currentpage -= 1
                        myembed = makeembed(currentpage*5-5, currentpage*5, pages, currentpage)
                        await self.client.edit_message(msg, embed=myembed)                        
                        await self.client.remove_reaction(msg, reaction.emoji, user)
                    elif reaction.emoji == "\U000023ee" and user.id == ctx.message.author.id and currentpage != 1:
                        currentpage = 1
                        myembed = makeembed(currentpage*5-5, currentpage*5, pages, currentpage)
                        await self.client.edit_message(msg, embed=myembed)                        
                        await self.client.remove_reaction(msg, reaction.emoji, user)
                    elif reaction.emoji == "\U000023ed" and user.id == ctx.message.author.id and currentpage != pages:
                        currentpage = pages
                        myembed = makeembed(currentpage*5-5, currentpage*5, pages, currentpage)
                        await self.client.edit_message(msg, embed=myembed)                        
                        await self.client.remove_reaction(msg, reaction.emoji, user)
                except TypeError: 
                    await self.client.delete_message(msg); break
        
        await browse()
        
    @commands.command(pass_context=True, aliases=['>use', '>u'])
    async def avause(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        raw = list(args)
        slots = {"a": 'right_hand', "b": "left_hand"}

        # ARSENAL
        try:
            # Filter
            int(raw[0])

            ##Check if item's available
            if raw[0] in list(self.ava_dict[ctx.message.author.id]['inventory'].keys()):
                ##Get slot_name
                try: slot_name = slots[raw[1]]
                except IndexError: slot_name = slots['a']
                except KeyError: await self.client.say(f":warning: Slots not found, {ctx.message.author.mention}!\n:grey_question: There are `2` weapon slots available: `0` Main Weapon | `1` Secondary Weapon"); return
                ##Equip
                if raw[0] != self.ava_dict[ctx.message.author.id][slot_name]:
                    self.ava_dict[ctx.message.author.id][slot_name] = raw[0]
                ###Already equip    -----> Unequip
                else: 
                    self.ava_dict[ctx.message.author.id][slot_name] = 'n/a' 
                    await self.client.say(f":white_check_mark: Unequipped item `{raw[0]}`|**{self.ava_dict[ctx.message.author.id]['inventory'][raw[0]]['obj'].name}** from *{slot_name}* slot!")
                    return
                # Inform, of course :)
                await self.client.say(f":white_check_mark: Equipped item `{raw[0]}`|**{self.ava_dict[ctx.message.author.id]['inventory'][raw[0]]['obj'].name}** to `{slot_name}` slot!")
            else:
                print(list(self.ava_dict[ctx.message.author.id]['inventory'].keys()))
                await self.client.say(f":warning: You don't own this weapon! `(id.{raw[0]})`"); return

        # E: Slot not given            
        except IndexError:
            # Switch
            sw = self.ava_dict[ctx.message.author.id][slots['b'].lower()]
            mw = self.ava_dict[ctx.message.author.id]['right_hand']
            self.ava_dict[ctx.message.author.id]['right_hand'] = sw
            self.ava_dict[ctx.message.author.id][slots['b'].lower()] = mw
            # Get line
            try: line_1 = f"`{self.ava_dict[ctx.message.author.id]['inventory'][sw]['obj'].name}` ➠ **right_hand**"
            except KeyError: line_1 = '**right_hand** is left empty'
            try: line_2 = f"`{self.ava_dict[ctx.message.author.id]['inventory'][mw]['obj'].name}` ➠ **{slots['b']}**'"
            except KeyError: line_2 = f"**{slots['b']}** is left empty"
            # Inform :)
            await self.client.say(f":twisted_rightwards_arrows: {line_1} **|** {line_2} "); return                
    
        # E: <item_code> OR <slot> given, instead of <item_id>
        except ValueError:

            # SLOT SWITCHING
            try:
                # Switch
                sw = self.ava_dict[ctx.message.author.id][slots[raw[0]].lower()]
                mw = self.ava_dict[ctx.message.author.id]['right_hand']
                self.ava_dict[ctx.message.author.id]['right_hand'] = sw
                self.ava_dict[ctx.message.author.id][slots[raw[0]].lower()] = mw
                # Get line
                try: line_1 = f"`{self.ava_dict[ctx.message.author.id]['inventory'][sw]['obj'].name}` ➠ **right_hand**"
                except KeyError: line_1 = '**right_hand** is left empty'
                try: line_2 = f"`{self.ava_dict[ctx.message.author.id]['inventory'][mw]['obj'].name}` ➠ **{slots[raw[0]]}**"
                except KeyError: line_2 = f"**{slots[raw[0]]}** is left empty"
                # Inform :)
                await self.client.say(f":twisted_rightwards_arrows: {line_1} **|** {line_2} "); return
            # E: Slot not found
            except KeyError: pass

            # SUPPLY n INGREDIENT
            ##Check if item's available
            try:
                items = self.ava_dict[ctx.message.author.id]['inventory']

                if not isinstance(items[raw[0]], int): await self.client.say(f":warning: This item is **inconsumble**, {ctx.message.author.mention}!"); return

                ## Get quantity
                try: 
                    quantity = int(raw[1])
                    if items[raw[0]] < quantity: quantity = items[raw[0]]
                    # SCAM :)
                    if quantity <= 0: await self.client.say("**Heyyyyyyyyy scammer-!**"); return
                ## E: No quantity given     ||      Invalid type of quantity argument
                except (IndexError, TypeError): quantity = 1

                for time in range(quantity):
                    # Affect
                    # SUPPLY
                    try: 
                        self.data['item'][raw[0]].func[0](self.data['item'][raw[0]].func[1], ctx.message.author.id)
                        name = self.data['item'][raw[0]].name
                    # INGREDIENT
                    except KeyError:
                        self.data['ingredient'][raw[0]].func[0](self.data['ingredient'][raw[0]].func[1], ctx.message.author.id)
                        # Weight check :">
                        if self.ava_dict[ctx.message.author.id]['STA'] > self.ava_dict[ctx.message.author.id]['MAX_STA']:
                            self.ava_dict[ctx.message.author.id]['weight'] += random.choice([0.3, 0.5, 0.6, 0.7])*quantity
                            await self.ava_scan(ctx.message, type='normalize')
                        name = self.data['ingredient'][raw[0]].name

                ## Decrease quantity
                items[raw[0]] -= quantity
                ## Quantity remaining check
                if items[raw[0]] <= 0: del items[raw[0]]
                await self.client.say(f":white_check_mark: Used `{quantity}` `{raw[0]}`|**{name}**")
            # E: item_code not found
            except KeyError: await self.client.say(f":warning: You don't own this item!"); return

        # E: Argument not found
        #except KeyError: await self.client.say(":warning: Invalid `class`, `category` or `id`!"); return
        # E: Not enough arguments
        #except IndexError: await self.client.say(f"**Syntax: **`-avaequip <item_class>.<category>.<id> <quantity(supply-optional) | slot(arsenal-optional)>`\n· **Classes: **`{'` `'.join(list(self.ava_dict[ctx.message.author.id]['inventory'].keys()))}`"); return

    @commands.command(pass_context=True, aliases=['>trader'])
    async def avatrader(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        cmd_tag = 'trade'

        if not await self.area_scan(ctx, self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][0], self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][1]): await self.client.say(":warning: Traders don't go outside of **Peace Belt**!"); return
        raw = list(args); quantity = 1

        # COOLDOWN
        #if not await self.__cd_check(ctx.message, cmd_tag, f"The storm is coming so they ran away."): return
        #else: await self.client.loop.run_in_executor(None, partial(redio.set, f'{cmd_tag}{ctx.message.author.id}', 'trading', ex=3600, nx=True))


        # Get menu
        menu = []
        for count in range(5):
            menu.append(random.choice(self.environ[self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place']]['characteristic']['cuisine']))

        # MENU
        line = "\n"
        for ig_code in menu:
            line = line + f""" `{ig_code}` <:green_ruby:520092621381697540> **{self.data['ingredient'][ig_code].name}**\n|| *"{self.data['ingredient'][ig_code].description}"*\n|| **`Market price`** ${self.data['ingredient'][ig_code].price}\n++ `{'` `'.join(self.data['ingredient'][ig_code].tags)}`\n\n"""
            
        reembed = discord.Embed(title = f"------------- KINUKIZA's MART ( of {self.environ[self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place']]['name']}) -----------", colour = discord.Colour(0x011C3A), description=line)
        await self.client.say(embed=reembed)
        await self.client.say(':bell: Syntax: `buy [item_code]` ||  Time out: 10s')

        def check(msg):
            return msg.content.startswith('buy ')

        # First buy
        raw = await self.client.wait_for_message(author=ctx.message.author, check=check, timeout=10)
        try: 
            raw = raw.content.lower().split(' ')[1:]
            ig_code = raw[0]
            try: 
                quantity = int(raw[1])
                if quantity > 5: await self.client.say(f":warning: {ctx.message.author.mention}, the requested quantity has pass the limitation. (max=5)"); return
                # SCAM :)
                if quantity <= 0: await self.client.say("Don't be dumb <:fufu:520602319323267082>"); return                
            # E: Quantity not given, or invalidly given
            except (IndexError, TypeError): pass

            # ig_code check    
            if ig_code not in menu: await self.client.say(":warning: Item not found *in the dealing board*!"); return
        except AttributeError: await self.client.say(":warning: Request timed out!"); return

        # Reconfirm
        price = int(self.data['ingredient'][ig_code].price*random.choice([0.1, 0.2, 0.5, 1, 2, 5, 10]))
        await self.client.say(f"{ctx.message.author.mention}, the dealer set the price of **${price}** for __each__ item `{ig_code}`|**{self.data['ingredient'][ig_code].name}**. \nThat would cost you **${price*quantity}** in total.\n:bell: Proceed? (y/n)")
        resp = await self.client.wait_for_message(author=ctx.message.author, timeout=10)
        try:
            if resp.content.lower() not in ['y', 'yes']: await self.client.say(":warning: Request declined!"); return
        except AttributeError: await self.client.say(":warning: Request declined!"); return
        
        try:
            # Money check
            if self.data['ingredient'][ig_code].price*quantity <= self.ava_dict[ctx.message.author.id]['money']:
                # UN-SERIALIZABLE
                # Increase item_code's quantity
                try:    
                    self.ava_dict[ctx.message.author.id]['inventory'][ig_code] += quantity
                # E: item_code did not exist. Create one, with given quantity
                except KeyError:
                    self.ava_dict[ctx.message.author.id]['inventory'][ig_code] = quantity
                await self.client.loop.run_in_executor(None, self.avatars_updating)

                # Deduct money
                self.ava_dict[ctx.message.author.id]['money'] -= self.data['ingredient'][ig_code].price*quantity

            else: await self.client.say(":warning: Insufficience balance!"); return
        # E: Item_code not found
        except KeyError: await self.client.say(":warning: Item's code not found!"); return


        # Greeting, of course :)
        await self.client.say(f":white_check_mark: Received **{quantity}** item `{ig_code}`|**{self.data['ingredient'][ig_code].name}**. Nice trade!")

    @commands.command(pass_context=True, aliases=['>sell'])
    async def avasell(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        if not await self.area_scan(ctx, self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][0], self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][1]): await self.client.say(":warning: You think you can find customers outside of **Peace Belt**?"); return

        quantity = 1
        raw = list(args)

        items = self.ava_dict[ctx.message.author.id]['inventory']

        try: quantity = int(raw[1])
        except IndexError: pass

        # SCAM :)
        if quantity <= 0: await self.client.say("**Heyyyyyyyyy scammer-!**"); return        

        try:
            # Selling
            # SUPP n INGR n AMMU
            if isinstance(items[raw[0]], int):
                # Quantity check
                if items[raw[0]] < quantity: quantity = items[raw[0]]            

                # SUPP n AMMU
                try: receive = (self.data['item'][raw[0]].price//random.choice([1, 2, 3]))*quantity
                # INGR
                except KeyError: receive = (self.data['ingredient'][raw[0]].price//random.choice([1, 3]))*quantity

                # Quantity decrease
                items[raw[0]] -= quantity
                # Quantity check
                if items[raw[0]] == 0: del items[raw[0]]
                
                # Get name
                name = self.data['ingredient'][raw[0]].name
            # WEAPON
            elif isinstance(items[raw[0]]['obj'], weapon):
                # Equipped weapon check
                if raw[0] in [self.ava_dict[ctx.message.author.id]['right_hand'], self.ava_dict[ctx.message.author.id]['left_hand']]: await self.client.say(":warning: You cannot sell an item that being equipped!"); return

                receive = items[raw[0]]['obj'].price//random.choice([1, 2, 3, 4])
                name = items[raw[0]]['obj'].name

                del items[raw[0]]
        # E: Item_id not found
        except KeyError: await self.client.say(":warning: You don't own this weapon!"); return

        # Receiving
        self.ava_dict[ctx.message.author.id]['money'] += receive

        await self.client.say(f":white_check_mark: You received **${receive}** from selling {quantity} `{raw[0]}`|**{name}**, {ctx.message.author.mention}!")

    @commands.command(pass_context=True, aliases=['>give'])
    async def avagive(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        raw = list(args)

        # Receiver check
        try: 
            receiver = ctx.message.mentions[0]
            if receiver.id not in list(self.ava_dict.keys()): await self.client.say(":warning: User don't have an ava!"); return
        except IndexError: await self.client.say(f":warning: Please provide a receiver, {ctx.message.author.mention}!"); return

        # Distance check
        if self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place'] != self.ava_dict[receiver.id]['realtime_zone']['current_place']:
            await self.client.say(f":warning: You need to be in the same region with the receiver, {ctx.message.author.mention}!"); return
        if await self.distance_tools(self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][0], self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][1], self.ava_dict[receiver.author.id]['realtime_zone']['current_coord'][0], self.ava_dict[receiver.id]['realtime_zone']['current_coord'][1], int(args[0])/1000, int(args[1])/1000) > 10:
            await self.client.say(f":warning: You need to be within **10 m** range of the receiver, {ctx.message.author.mention}!"); return

        # Money check
        try:
            if int(raw[0]) > self.ava_dict[ctx.message.author.id]['money']: await self.client.say(":warning: Insufficient balance!"); return
            # SCAM :)
            if int(raw[0]) <= 0: await self.client.say("**Heyyyyyyyyy scammer-!**"); return
        except ValueError: await self.client.say(":warning: Invalid syntax!"); return
            
        # Transfer
        self.ava_dict[ctx.message.author.id]['money'] -= int(raw[0])
        self.ava_dict[receiver.id]['money'] += int(raw[0])
        await self.client.say(f":white_check_mark: You've been given **${raw[0]}**, {receiver.mention}!")

    @commands.command(pass_context=True, aliases=['>trade'])
    async def avatrade(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        raw = list(args)

        # Receiver check
        try: 
            receiver = ctx.message.mentions[0]
            if receiver.id not in list(self.ava_dict.keys()): await self.client.say(":warning: User don't have an ava!"); return
        except IndexError: await self.client.say(f":warning: Please provide a receiver, {ctx.message.author.mention}!"); return

        # Distance check
        if self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place'] != self.ava_dict[receiver.id]['realtime_zone']['current_place']:
            await self.client.say(f":warning: You need to be in the same region with the receiver, {ctx.message.author.mention}!"); return
        if await self.distance_tools(self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][0], self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][1], self.ava_dict[receiver.author.id]['realtime_zone']['current_coord'][0], self.ava_dict[receiver.id]['realtime_zone']['current_coord'][1], int(args[0])/1000, int(args[1])/1000) > 10:
            await self.client.say(f":warning: You need to be within **10 m** range of the receiver, {ctx.message.author.mention}!"); return

        # SERI
        try:
            if 'untradable' in self.ava_dict[ctx.message.author.id]['inventory'][raw[0]]['obj'].tags: await self.client.say(f":warning: You cannot trade this item, {ctx.message.author.mention}. It's *untradable*, look at the tags."); return
            self.ava_dict[receiver.id]['inventory'][raw[0]] = self.ava_dict[ctx.message.author.id]['inventory'][raw[0]]
            
            name = self.ava_dict[ctx.message.author.id]['inventory'][raw[0]]['obj']
            del self.ava_dict[ctx.message.author.id]['inventory'][raw[0]]
        # E: Item's id not found
        except KeyError: await self.client.say(":warning: You don't own this item!"); return
        
        # UN-SERI
        except TypeError:                
            # Quantity given
            try:
                # Quantity check
                if int(raw[1]) > self.ava_dict[ctx.message.author.id]['inventory'][raw[0]]: quantity = self.ava_dict[ctx.message.author.id]['inventory'][raw[0]]
                else: quantity = int(raw[1])
                # SCAM :)
                if quantity <= 0: await self.client.say("**Heyyyyyyyyy scammer-!**"); return
            # Quantit NOT given
            except ValueError: quantity = 1

            # Receiver already had the item
            try: self.ava_dict[receiver.id]['inventory'][raw[0]] += quantity
            except KeyError: self.ava_dict[receiver.id]['inventory'][raw[0]] = quantity

            try: name = self.data['item'][raw[0]].name
            except KeyError: name = self.data['ingredient'][raw[0]].name

        # Inform, of course :>
        await self.client.say(f":white_check_mark: You've been given `{quantity}` `{raw[0]}`|**{name}**, {ctx.message.author.mention}!")




# ============= !< BATTLE >! ==================
# <!> CONCEPTS
# ---- WEAPON ----
### We value a melee mainly by 3 elements: SPEED, MULTIPLIER, STA              
### We value a range_weapon mainly by AMMUNITION and 4 elements: RANGE, ACCURACY, FIRE_RATE, STEALTH.
### We value a kind of ammunition mainly by 3 elements: SPEED, DMG, MONEY

# ---- BATTLING ----
### A PVE (of all kind of weapons) battle session consists of two phases: 1.User 2.Mob. 
### A PVP (of all kind of weapons) battle session consists of one phase only: The user phase, as the attacking side
###### A melee PVE will lead to a melee single-phase or multi-phase battle
###### A range_weapon PVE will (maybe, eventually) lead to a melee single-phase or multi-phase battle


    # This function/command handles the User's MELEE phase
    # Melee PVE ||      Start the USER MELEE phase.     ||          Melee PVP ||       Start the USER MELEE attacking phase.
    @commands.command(pass_context=True, aliases=['>atk'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def avaattack(self, ctx, *args):
        """ -avaattack [moves] [target]
            -avaattack [moves]              
            <!> ONE target of each creature type at a time. Mobs always come first, then user. Therefore you can't fight an user while fighting a mob
            <!> DO NOT lock on current_enemy at the beginning. Do it at the end."""
        if not await self.ava_scan(ctx.message, type='life_check'): return

        raw = list(args); __mode = 'PVP'

        # HANDLING
        try:
            note = {'both': '<:right_hand:521197677346553861><:left_hand:521197732162043922>', 'right': '<:right_hand:521197677346553861>', 'left': '<:left_hand:521197732162043922>'}

            self.ava_dict[ctx.message.author.id]['realtime_zone']['combat']['handling'] = raw[0]
            await self.client.say(f'{note[raw[0]]} Change to **{raw[0]} hand** pose'); return
        except KeyError: pass

        current_coord = self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord']
        if await self.area_scan(ctx, current_coord[0], current_coord[1]): await self.client.say(":warning: You can't fight inside **Peace Belt**!"); return


        if not raw: await self.client.say(f":warning: {ctx.message.author.mention}, please make your moves!"); return
            # Check if it's a PVP or PVE call
            # Then get the target (Mob/User)
        # In case 2nd para is given
        try:
            if raw[1].startswith('<@'):
                # If there's no current_enemy   ||   # If there is, and the target is the current_enemy
                if not self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['user']:
                    target = ctx.message.mentions[0]; target_id = target.id
                # If there is, but the target IS NOT the current_enemy. (Update: just freaking ignore it, for the sake of multiple battle sessions)         
                elif ctx.message.mentions[0] != self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['user'][0] or raw[1] == self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['mob'][0]: 
                    #await self.client.say(f":warning: Please finish your current fight with **{self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['user'][0].name}**!"); return
                    target = ctx.message.mentions[0]; target_id = target.id
                __bmode = 'DIRECT'
                if not ctx.message.server.get_member(target_id): __bmode = 'INDIRECT'
            else:
                # If there's no current_enemy   ||   # If there is, and the target is the current_enemy
                if not self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['mob'] or raw[1] == self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['mob'][0]:
                    target = raw[1]; __mode = 'PVE'; target_id = target
                # If there is, but the target IS NOT the current_enemy
                elif raw[1] != self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['mob'][0]: 
                    await self.client.say(f":warning: Please finish your current fight with the `{self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['mob'][0]}`!"); return
        # In case 2nd para is not given, current_enemy is used
        except IndexError:
            # Mobs first. If there's no mob in current_enemy, then randomly pick one
            if not self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['mob']:
                # If there's no mob lock on, then move on to user
                #   if not self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['user']:
                #       await self.client.say(":warning: You've not locked on anything yet!")
                #   else: 
                #       target = self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['user']
                #       target_id = target.id
                target = random.choice(list(self.environ[self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place']]['mob'].keys()))
                target_id = target
                __mode = 'PVE'
            else:
                target = self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['mob'][0]
                target_id = target
                __mode = 'PVE'           

        counter_move = []

        # Check if player equip a weapon
        if self.ava_dict[ctx.message.author.id]['realtime_zone']['combat']['handling'] in ['both', 'right']: main_weapon = self.ava_dict[ctx.message.author.id]['right_hand']
        elif self.ava_dict[ctx.message.author.id]['realtime_zone']['combat']['handling'] == 'left': main_weapon = self.ava_dict[ctx.message.author.id]['left_hand']

        if main_weapon == 'n/a': await self.client.say(f":warning: {ctx.message.author.mention}, please **equip** a weapon"); return
        # Check if player equip a melee
        weapon = self.ava_dict[ctx.message.author.id]['inventory'][main_weapon]['obj']
        if 'melee' not in weapon.tags: await self.client.say(f":warning: {ctx.message.author.mention}, you need a **melee weapon** to use this cmd!"); return
        # Check if target has a ava
        if __mode == 'PVP': 
            if not target_id in list(self.ava_dict.keys()): await self.client.say(":warning: Target don't have an ava!"); return
            # Checking the current_place
            if not self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place'] == self.ava_dict[target.id]['realtime_zone']['current_place']:
                await self.client.say(f":warning: {ctx.message.author.mention}, you and the target are not in the same region!"); return
                
        elif __mode == 'PVE':
            if target_id.split('.')[0] == 'boss':
                bosses = self.environ[self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place']]['info']['boss']
                # Check if the current region has the given boss
                if not bosses or target_id not in list(bosses.keys()): return
                boss_coord = bosses[target_id][1]
                # Check if the user is in range of the boss
                if current_coord[0] < boss_coord[0][0] or current_coord[1] < boss_coord[0][1] or current_coord[0] > boss_coord[1][0] or current_coord[1] > boss_coord[1][1]:
                    await self.client.say(f":warning: {ctx.message.author.mention}, you can't engage the boss from your current location!"); return

            elif not target_id in list(self.environ[self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place']]['mob'].keys()): 
                await self.client.say(f":warning: There is no `{target_id}` around! Perhap you should check your surrounding..."); return
        
        # STA filter
        if len(raw[0])*weapon.sta < self.ava_dict[ctx.message.author.id]['STA']:
            if weapon.sta >= 100: self.ava_dict[ctx.message.author.id]['STA'] -= 2
            else: self.ava_dict[ctx.message.author.id]['STA'] -= 1
        else: await self.client.say(f":warning: {ctx.message.author.mention}, out of `STA`!"); return

        # Checking the length of moves
        if len(raw[0]) > self.ava_dict[ctx.message.author.id]['arts']['sword_art']['chain_attack']:
            await self.client.say(f":warning: You cannot perform a `{len(raw[0])}-chain` attack, {ctx.message.author.mention}!"); return

        # Decoding moves, as well as checking the moves. Get the counter_move
        for move in raw[0]:
            if move == 'a': counter_move.append('d')
            elif move == 'd': counter_move.append('b')
            elif move == 'b': counter_move.append('a')
            else: await self.client.say(f":warning: Invalid move! (move no. `{raw[0].index(move) + 1}` -> `{move}`)"); return
        
        # PVP use target, with ava_dict =================
        async def PVP():
            # If the duo share the same server, send msg to that server. If not, DM the attacked
            if __bmode == 'DIRECT': inbox = ctx.message
            else: inbox = await self.client.send_message(target, ctx.message.content)

            await self.client.add_reaction(inbox, '\U00002694')

            # Wait for move recognition     ||      The more STA consumed, the less time you have to recognize moves. Therefore, if you attack too many times, you'll be more vulnerable
            # RECOG is based on opponent's STA     ||      RECOG = oppo's STA / 30
            RECOG = self.ava_dict[target.id]['STA'] / 30

            # If the attack is INDIRECT, multiple RECOG by 5
            if __bmode == 'INDIRECT': RECOG = RECOG*5

            if RECOG < 1: RECOG = 1
            if not await self.client.wait_for_reaction(emoji='\U00002694', user=target, message=inbox, timeout=RECOG):
                dmgdeal = round(self.ava_dict[ctx.message.author.id]['STR']*weapon.multiplier*len(counter_move))
                self.ava_dict[target.id]['LP'] -= dmgdeal; await self.client.say(f":dagger: **{ctx.message.author.name}** has dealt *{dmgdeal} DMG* to **{target.name}**"); return


            # Wait for response moves       ||        SPEED ('speed') of the sword
            def check(msg):
                return msg.content.startswith('!')
            
            SPEED = weapon.speed

            msg = await self.client.wait_for_message(timeout=SPEED, author=target, channel=inbox.channel, check=check)
            if not msg: 
                dmgdeal = round(self.ava_dict[ctx.message.author.id]['STR']*weapon.multiplier*len(counter_move))
                self.ava_dict[target.id]['LP'] -= dmgdeal; await self.client.say(f":dagger: **{ctx.message.author.name}** has dealt *{dmgdeal} DMG* to **{target.name}**"); return
            
            # Measuring response moves
            hit_count = 0
            response_content = msg.content[1:]; diff = len(counter_move) - len(response_content)      # Measuring the length of the response
            if diff > 0: response_content += '-'*diff
            for move, response_move in zip(counter_move, response_content):
                if move != response_move: hit_count += 1

            # Conduct dealing dmg   ||  Conduct dealing STA dmg
            if hit_count == 0:
                await self.client.say(f"·\n·\n·\n·\n:shield: **{target.mention}** has successfully *guarded* all **{ctx.message.author.name}**'s attack!")

                # Recalculate the dmg, since hit_count == 0                
                ## Player's dmg
                if self.ava_dict[ctx.message.author.id]['realtime_zone']['combat']['handling'] == 'both':
                    dmgdeal = round(self.ava_dict[ctx.message.author.id]['STR']*weapon.multiplier*len(counter_move))
                elif self.ava_dict[ctx.message.author.id]['realtime_zone']['combat']['handling'] in ['right', 'left']:
                    dmgdeal = round(self.ava_dict[ctx.message.author.id]['STR']*weapon.multiplier*len(counter_move))*2
                ## Opponent's def
                if self.ava_dict[target.id]['realtime_zone']['combat']['handling'] == 'both':
                    try:
                        def_weapon = dmgredu = 100 - self.ava_dict[target.id]['inventory'][self.ava_dict[target.id]['left_hand']]['obj']
                        dmgredu = 100 - def_weapon.defend
                    except KeyError: dmgredu = 100    
                elif self.ava_dict[target.id]['realtime_zone']['combat']['handling'] == 'right':
                    try:
                        def_weapon = self.ava_dict[target.id]['inventory'][self.ava_dict[target.id]['right_hand']]['obj']
                        dmgredu = 100 - def_weapon.defend*2
                    except KeyError: dmgredu = 100
                elif self.ava_dict[target.id]['realtime_zone']['combat']['handling'] == 'left':
                    try:
                        def_weapon = self.ava_dict[target.id]['inventory'][self.ava_dict[target.id]['left_hand']]['obj']
                        dmgredu = 100 - def_weapon.defend*2
                    except KeyError: dmgredu = 100
                
                # If dmgredu > 0, backfire the attacker. If dmgredu >= 0, all dmg are neutralized
                if dmgredu < 0:
                    self.ava_dict[ctx.message.author.id]['STA'] -= round(dmgdeal / 100 * abs(dmgredu))*def_weapon.multiplier
                    dmgredu = 0

                self.ava_dict[target.id]['STA'] -= round(dmgdeal / 100 * dmgredu)
            else:

                # Recalculate the dmg             
                ## Player's dmg
                if self.ava_dict[ctx.message.author.id]['realtime_zone']['combat']['handling'] == 'both':
                    dmgdeal = round(self.ava_dict[ctx.message.author.id]['STR']*weapon.multiplier*hit_count)
                elif self.ava_dict[ctx.message.author.id]['realtime_zone']['combat']['handling'] in ['right', 'left']:
                    dmgdeal = round(self.ava_dict[ctx.message.author.id]['STR']*weapon.multiplier*hit_count)*2
                ## Opponent's def
                if self.ava_dict[target.author.id]['realtime_zone']['combat']['handling'] == 'both':
                    def_weapon = dmgredu = 200 - self.ava_dict[target.id]['inventory'][self.ava_dict[target.id]['left_hand']]['obj']
                    dmgredu = 200 - def_weapon.defend
                elif self.ava_dict[target.author.id]['realtime_zone']['combat']['handling'] == 'right':
                    def_weapon = self.ava_dict[target.id]['inventory'][self.ava_dict[target.id]['right_hand']]['obj']
                    dmgredu = 200 - def_weapon.defend*2
                elif self.ava_dict[target.author.id]['realtime_zone']['combat']['handling'] == 'left':
                    def_weapon = self.ava_dict[target.id]['inventory'][self.ava_dict[target.id]['left_hand']]['obj']
                    dmgredu = 200 - def_weapon.defend*2

                # If dmgredu > 0, backfire the attacker. If dmgredu >= 0, all dmg are neutralized
                if dmgredu < 0:
                    self.ava_dict[ctx.message.author.id]['STA'] -= round(dmgdeal / 200 * abs(dmgredu))*def_weapon.multiplier
                    dmgredu = 0

                # Get dmgdeal, for informing :>
                dmgdeal = round(dmgdeal / 200 * dmgredu)
                self.ava_dict[target.id]['LP'] -= dmgdeal

                await self.client.say(f":dagger: **{ctx.message.author.name}** has dealt *{dmgdeal} DMG* to **{target.name}**")
        
            await self.ava_scan(ctx.message, 'life_check')

        # PVE use target_id, with self.environ ======================
        if __mode == 'PVE':
            # ------------ USER PHASE   ||   User deal DMG 
            my_dmgdeal = round(self.ava_dict[ctx.message.author.id]['STR']*weapon.multiplier*len(counter_move))
            # Inform, of course :>
            self.environ[self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place']]['mob'][target_id].lp -= my_dmgdeal; await self.client.say(f":dagger: **{ctx.message.author.name}** has dealt *{my_dmgdeal} DMG* to **「`{target_id}` | {self.environ[self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place']]['mob'][target_id].name}」**!")
    

        if __mode == 'PVP':
            await PVP()
        elif __mode == 'PVE':
            await self.PVE(ctx.message, target_id)
        else: print("<<<<< OH SHIET >>>>>>>")

##########################

    @commands.command(pass_context=True, aliases=['>aim'])
    @commands.cooldown(1, 60, type=BucketType.user)
    async def avaaim(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        current_coord = self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord']
        if await self.area_scan(ctx, current_coord[0], current_coord[1]): await self.client.say(":warning: No gunfire *inside* **Peace Belt**!"); return
        raw = list(args); __mode = 'PVP'
        shots = 1
        # >Aim <coord_X> <coord_Y> <shots(optional)>      ||      >Aim <@user/mob_name> <shots(optional)>

        await self.client.delete_message(ctx.message)

        ### ALL ELEMENT GET     (target, coord, shots)
        try:
            target = ''
            print("HEH")
            # @User, shots provided
            if raw[0].startswith('<@'):
                print("JUST HERE")
                # Get user
                target = ctx.message.mentions[0]; target_id = target.id
                __bmode = 'DIRECT'
                # Get shots (if available and possible)
                try: shots = int(raw[1])
                except IndexError: pass
                except TypeError: pass

            # Coord, shots provided     (if raw[0] is a mob_name, raise TypeError       ||      if raw[0] provided as <shots>, but raw[1] is not, raise IndexError)
            elif len(str(int(raw[0]))) <= 5 and len(raw[1]) <= 5:
                print("OKAI HERE")
                X = int(raw[0])/1000; Y = int(raw[1])/1000
                current_place = self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place']

                # Get user from coord
                print(int(X), int(Y), X, Y)
                print(self.environ[current_place]['map'][int(X)][int(Y)])
                for user_id in self.environ[current_place]['map'][int(X)][int(Y)]:
                    try:
                        if self.ava_dict[user_id]['realtime_zone']['current_coord'] == [X, Y]:
                            target = await self.client.get_user_info(user_id); target_id = user_id
                            __bmode = 'DIRECT'
                            if not ctx.message.server.get_member(target_id): __bmode = 'INDIRECT'                            
                            break
                    except TypeError:
                        await self.client.say(f"There's noone at X:`{X}` Y:`{Y}` in {current_place}!"); return
                if not target: await self.client.say(f"There's noone at **x:`{X:.3f}` y:`{Y:.3f}`** in {current_place}!"); return
                
                # Get shots (if available and possible)
                try: shots = int(raw[2])
                except IndexError: pass
                except TypeError: pass
            else: await self.client.say(":warning: Please use 5-digit or lower coordinates!")       

        # Mob_name, shots provided
        except (TypeError, ValueError):
            print("HEREEE")
            # If there's no current_enemy   ||   # If there is, and the target is the current_enemy
            if not self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['mob'] or raw[0] == self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['mob'][0]:
                target = raw[0]; __mode = 'PVE'; target_id = target
            # If there is, but the target IS NOT the current_enemy
            elif raw[0] != self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['mob'][0]: 
                await self.client.say(f":warning: Please finish your current fight with the `{self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['mob'][0]}`!"); return

        # Or none of them, then we should randomly pick one :v        
        except IndexError:
            print("HER HERE")
            # Mobs first. If there's no mob in current_enemy, then randomly pick one
            if not self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['mob']:
                target = random.choice(list(self.environ[self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place']]['mob'].keys()))
                target_id = target
                __mode = 'PVE'
            # If there is, use current_enemy
            else:
                target = self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['mob'][0]
                target_id = target
                __mode = 'PVE'     

            # Get shots (if available and possible)
            try: shots = int(raw[0])
            except IndexError: pass
            except TypeError: pass                


        ### CHECKING TIMES!!!   (as well as init some variables)
        # Weapon
        if self.ava_dict[ctx.message.author.id]['realtime_zone']['combat']['handling'] in ['both', 'right']: main_weapon = self.ava_dict[ctx.message.author.id]['right_hand']
        elif self.ava_dict[ctx.message.author.id]['realtime_zone']['combat']['handling'] == 'left': main_weapon = self.ava_dict[ctx.message.author.id]['left_hand']

        if main_weapon == 'n/a': await self.client.say(f":warning: {ctx.message.author.mention}, please **equip** a weapon"); return
        # If weapon is <range_weapon>
        weapon = self.ava_dict[ctx.message.author.id][main_weapon]['obj']
        if 'range_weapon' in weapon.tags: await self.client.say(f":warning: {ctx.message.author.mention}, you need a **range weapon** to use this cmd!"); return

        # Check if target has a ava
        if __mode == 'PVP': 
            if not target_id in list(self.ava_dict.keys()): await self.client.say(":warning: Target don't have an ava!"); return
            # Checking the current_place (aka. region)
            if not self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place'] == self.ava_dict[target.id]['realtime_zone']['current_place']:
                await self.client.say(f":warning: {ctx.message.author.mention}, you and the target are not in the same region!"); return
        elif __mode == 'PVE':
            if target_id.split('.')[0] == 'boss':
                bosses = self.environ[self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place']]['info']['boss']
                # Check if the current region has the given boss
                if not bosses or target_id not in list(bosses.keys()): return
                boss_coord = bosses[target_id][1]
                # Check if the user is in range of the boss
                if current_coord[0] < boss_coord[0][0] or current_coord[1] < boss_coord[0][1] or current_coord[0] > boss_coord[1][0] or current_coord[1] > boss_coord[1][1]:
                    await self.client.say(f":warning: {ctx.message.author.mention}, you can't engage the boss from your current location!"); return

            elif not target_id in list(self.environ[self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place']]['mob'].keys()): 
                await self.client.say(f":warning: There is no `{target_id}` around! Perhap you should check your surrounding..."); return

        # Ammunition
        if shots > weapon.firing_rate: await self.client.say(f":warning: {ctx.message.author.mention}, your gun cannot cannot fire `{shots}` shots in a row!"); return
        # Check the avaibility of ammo
        # Check the ammu type of weapon
        if weapon.round == 'all':
            # Pick the first ammu type in ammunition list
            while True: 
                ammu_keys = [a for a in self.data['item'] if isinstance(a, ammunition)]
                ammu_key = list(set(ammu_keys).intersection(set(self.ava_dict[ctx.message.author.id]['inventory'].keys())))[0]
        else:
            # Get the weapon's ammu type
            if weapon.round in list(self.ava_dict[ctx.message.author.id]['inventory'].keys()): ammu_key = weapon.round
            else: await self.client.say(f":warning: {ctx.message.author.mention}, OUT OF `{weapon.round} | {self.data['inventory'][weapon.round].name}`!"); return
        # Check the quantity of the ammu_type
        if self.ava_dict[ctx.message.author.id]['inventory'][ammu_key] <= shots:
            shots = self.ava_dict[ctx.message.author.id]['inventory'][ammu_key]
            del self.ava_dict[ctx.message.author.id]['inventory'][ammu_key]
            ammu = self.data['item'][ammu_key]
        else:
            self.ava_dict[ctx.message.author.id]['inventory'][ammu_key] -= shots             
            ammu = self.data['item'][ammu_key]

        # STA filter
        if shots*weapon.sta < self.ava_dict[ctx.message.author.id]['STA']:
            if weapon.sta >= 100: self.ava_dict[ctx.message.author.id]['STA'] -= 20
            else: self.ava_dict[ctx.message.author.id]['STA'] -= 10
        else:
            shots = self.ava_dict[ctx.message.author.id]['STA']//weapon.sta

        # Distance get
        if __mode == 'PVP':
            user_coord = self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord']
            target_coord = self.ava_dict[target_id]['realtime_zone']['current_coord'] 
            distance = await self.distance_tools(user_coord[0], user_coord[1], target_coord[0], target_coord[1])
            if distance > weapon.range[1] or distance < weapon.range[0]: await self.client.say(f":warning: {ctx.message.author.mention}, the target is out of your gun's range!"); return
        elif __mode == 'PVE':
            distance = 1                    # There is NO distance in a PVE battle, therefore the accuracy will always be at its lowest

        
        ### PREPARING !!!
        # Filtering shots
        bingos = 0
        for i in range(shots):
            if distance < weapon.accuracy[1]:
                if random.choice(range(weapon.accuracy[0])) == 0: print("AA~~"); bingos += 1
            else:
                if random.choice(range(weapon.accuracy[0]*(distance / weapon.accuracy[1]))) == 0: bingos += 1
        print(f"BINGO: {bingos}")
        shots = bingos
        if shots == 0: await self.client.say(f":interrobang: {ctx.message.author.mention}, you shot a lot but hit nothing..."); return

        #dmgdeal = ammu['dmg']*shots

        # PVP use target, with ava_dict =================
        async def PVP():
            if distance < 100: a = 1
            else: a = distance/100
            field = 'O'*int(shots)*weapon.stealth*int(a)
            counter_shot = []

            for shot in range(shots):
                while True:
                    hole = random.choice(range(len(field)))
                    print(hole)
                    if field[hole] == 'O': break
                counter_shot.append(str(hole))
                
                if hole != 0:
                    field = field[:hole] + '0' + field[(hole + 1):]   # OOOOOOOOOOOOO
                elif hole == len(field):
                    field = field[:hole] + '0'
                else:
                    field = '0' + field[(hole + 1):]

            if distance <= 1000: shooter = ctx.message.author.name
            else: shooter = 'Someone'
            # Check if the attack is DIRECT. If not, DM the attacked
            if __bmode == 'DIRECT': 
                inbox = await self.client.send_message(target, f""":sos: **{shooter}** is trying to shoot you {target.mention}```css
{field}```""")
            else: 
                inbox = await self.client.send_message(target, f""":sos: **{shooter}** is trying to shoot you {target.mention}```css
{field}```""")

            # Wait for response moves       ||        SPEED ('speed') of the bullet aka. <ammu>
            def check(msg):
                return msg.content.startswith('!')
            
            SPEED = ammu.speed
            # If the attack is INDIRECT, multiple RECOG by 5
            if __bmode == 'INDIRECT': SPEED = SPEED*5
            msg = await self.client.wait_for_message(timeout=SPEED, author=target, channel=inbox.channel, check=check)
            if not msg: 
                dmgdeal = ammu.dmg*shots
                self.ava_dict[target.id]['LP'] -= dmgdeal; await self.client.say(f":dagger: **{ctx.message.author.name}** has dealt *{dmgdeal} DMG* to **{target.name}**"); return

            # Measuring response moves
            hit_count = 0
            response_content = msg.content[1:]; a = response_content.split(' ')     # Measuring the length of the response
            print(counter_shot)
            print(a)
            for shot in counter_shot:
                if shot not in response_content: hit_count += 1

            # Conduct dealing dmg   ||  Conduct dealing STA dmg
            dmgdeal = ammu.dmg*hit_count
            if hit_count == 0:
                await self.client.say(f"·\n·\n·\n·\n:shield: **{target.mention}** has successfully *guarded* all **{ctx.message.author.name}**'s attack!")

                # Recalculate the dmg, since hit_count == 0                
                ## Player's dmg
                if self.ava_dict[ctx.message.author.id]['realtime_zone']['combat']['handling'] == 'both':
                    dmgdeal = round(self.ava_dict[ctx.message.author.id]['STR']*weapon.multiplier*len(counter_shot))
                elif self.ava_dict[ctx.message.author.id]['realtime_zone']['combat']['handling'] in ['right', 'left']:
                    dmgdeal = round(self.ava_dict[ctx.message.author.id]['STR']*weapon.multiplier*len(counter_shot))*2
                ## Opponent's def
                if self.ava_dict[target.author.id]['realtime_zone']['combat']['handling'] == 'both':
                    def_weapon = dmgredu = 100 - self.ava_dict[target.id]['inventory'][self.ava_dict[target.id]['left_hand']]['obj']
                    dmgredu = 100 - def_weapon.defend
                elif self.ava_dict[target.author.id]['realtime_zone']['combat']['handling'] == 'right':
                    def_weapon = self.ava_dict[target.id]['inventory'][self.ava_dict[target.id]['right_hand']]['obj']
                    dmgredu = 100 - def_weapon.defend*2
                elif self.ava_dict[target.author.id]['realtime_zone']['combat']['handling'] == 'left':
                    def_weapon = self.ava_dict[target.id]['inventory'][self.ava_dict[target.id]['left_hand']]['obj']
                    dmgredu = 100 - def_weapon.defend*2
                
                # If dmgredu >= 0, all dmg are neutralized
                if dmgredu < 0:
                    dmgredu = 0

                self.ava_dict[target.id]['STA'] -= round(dmgdeal / 100 * dmgredu)                
            else:
                # Recalculate the dmg             
                ## Player's dmg
                if self.ava_dict[ctx.message.author.id]['realtime_zone']['combat']['handling'] == 'both':
                    dmgdeal = round(self.ava_dict[ctx.message.author.id]['STR']*weapon.multiplier*hit_count)
                elif self.ava_dict[ctx.message.author.id]['realtime_zone']['combat']['handling'] in ['right', 'left']:
                    dmgdeal = round(self.ava_dict[ctx.message.author.id]['STR']*weapon.multiplier*hit_count)*2
                ## Opponent's def
                if self.ava_dict[target.id]['realtime_zone']['combat']['handling'] == 'both':
                    try:
                        def_weapon = dmgredu = 200 - self.ava_dict[target.id]['inventory'][self.ava_dict[target.id]['left_hand']]['obj']
                        dmgredu = 200 - def_weapon.defend
                    except KeyError: dmgredu = 200
                elif self.ava_dict[target.id]['realtime_zone']['combat']['handling'] == 'right':
                    try:
                        def_weapon = self.ava_dict[target.id]['inventory'][self.ava_dict[target.id]['right_hand']]['obj']
                        dmgredu = 200 - def_weapon.defend*2
                    except KeyError: dmgredu = 200
                elif self.ava_dict[target.id]['realtime_zone']['combat']['handling'] == 'left':
                    try:
                        def_weapon = self.ava_dict[target.id]['inventory'][self.ava_dict[target.id]['left_hand']]['obj']
                        dmgredu = 200 - def_weapon.defend*2
                    except KeyError: dmgredu = 200

                # If dmgredu > 0, backfire the attacker. If dmgredu >= 0, all dmg are neutralized
                if dmgredu < 0:
                    self.ava_dict[ctx.message.author.id]['STA'] -= round(dmgdeal / 200 * abs(dmgredu))*def_weapon.multiplier
                    dmgredu = 0

                # Get dmgdeal, for informing :>
                dmgdeal = round(dmgdeal / 200 * dmgredu)
                self.ava_dict[target.id]['LP'] -= dmgdeal

                await self.client.say(f":dagger: **{ctx.message.author.name}** has dealt *{dmgdeal} DMG* to **{target.name}**")
        
            await self.ava_scan(ctx.message, 'life_check')

        if __mode == 'PVP':
            await PVP()
        elif __mode == 'PVE':
            await self.PVE(ctx.message, target_id)
        else: print("<<<<< OH SHIET >>>>>>>")

##########################

    # This function handles the Mob phase
    # Melee PVE     ||      Start the mob phase.
    async def PVE(self, MSG, target_id):
        current_mob = target_id
        user_id = MSG.author.id
        current_place = self.ava_dict[user_id]['realtime_zone']['current_place']
        message_obj = False
        await self.client.delete_message(MSG)

        async def conclusing():
            ava_lifecheck = await self.ava_scan(MSG, type='life_check')
            if not ava_lifecheck:
                await self.client.loop.run_in_executor(None, self.avatars_updating) 
                return False
            if int(self.environ[current_place]['mob'][current_mob].lp) <= 0:
                await self.client.say(f":skull: **{self.environ[current_place]['mob'][current_mob].name}** is dead.")
                
                # Add one to the collection
                type = await vanishing()                    
                try: self.ava_dict[MSG.author.id]['mobs_collection'][type][current_place] += 1
                # E: current_place not in mobs_collection's type key
                except KeyError: self.ava_dict[MSG.author.id]['mobs_collection'][type][current_place] = 1
                # E: current_place is an invalid type
                except TypeError: self.ava_dict[MSG.author.id]['mobs_collection'][type][current_place] = 1

                # Erase the current_enemy lock on off the target_id
                del self.ava_dict[MSG.author.id]['realtime_zone']['current_enemy']['mob'][0]
                await self.client.loop.run_in_executor(None, self.avatars_updating)
                return False 

            msg = f"--------------------\n**{self.ava_dict[MSG.author.id]['name']}:** `{self.ava_dict[MSG.author.id]['LP']}` LP  |  `{self.ava_dict[MSG.author.id]['STA']}` STA\n**{self.environ[current_place]['mob'][current_mob].name}:** `{self.environ[current_place]['mob'][current_mob].lp}` LP\n--------------------"
            return msg

        async def vanishing():
            # Looting
            a = []
            for drop in self.environ[current_place]['mob'][current_mob].drop_item():
                if drop[0] in ['money']:
                    a.append(f"**${drop[1]}**")
                    #Adding to the inventory
                    self.ava_dict[MSG.author.id]['money'] += drop[1]
                else: 
                    a.append(f"{drop[1]} **{drop[0]}**")

            await self.client.say(f"<:chest:507096413411213312> Congrats **{self.ava_dict[MSG.author.id]['name']}**, you've received {' and '.join(a)} from **「`{current_mob}` | {self.environ[current_place]['mob'][current_mob].name}」**!")
            
            # Get the type to reproduce later
            type = self.environ[current_place]['mob'][current_mob].branch.split('.')[1]
            del self.environ[current_place]['mob'][current_mob]

            # Reproducing
            pointer = -5
            while True:
                prev_name = list(self.environ[current_place]['mob'].keys())[pointer].split('.')
                if prev_name[0] != 'boss': break
                else: pointer -= 1

            name = f"{prev_name[0]}.{int(prev_name[-1]) + random.choice(range(10))}"
            #protomob = self.data['entity']['mob'][prev_name[0]]
            protomob = self.data['entity']['mob'][type]
            self.environ[current_place]['mob'][name] = mob(protomob)
            return prev_name[0]

        # ------------ MOB PHASE    ||   Mobs attack, user defend
        async def battle(message_obj):
            if not await conclusing(): return False

            dmg, mmove, counter_mmove = self.environ[current_place]['mob'][current_mob].attack()

            await self.client.say(f"**{self.environ[current_place]['mob'][current_mob].name}** performed an attack on {MSG.author.mention}: `{' '.join(mmove)}`")

            # Wait for response moves
            def check(msg):
                return msg.content.startswith('!')
            
            MSPEED = self.environ[current_place]['mob'][current_mob].speed
            msg = await self.client.wait_for_message(timeout=MSPEED, author=MSG.author, channel=MSG.channel, check=check)            #timeout=10
            try: await self.client.delete_message(msg)
            except: pass

            if not msg: 
                dmgdeal = round(dmg*len(mmove))
                self.ava_dict[MSG.author.id]['LP'] -= dmgdeal
                pack_1 = f":dagger: **「`{current_mob}` | {self.environ[current_place]['mob'][current_mob].name}」** has dealt *{dmgdeal} DMG* to **{MSG.author.mention}**!"
                pack_2 = await conclusing()
                if pack_2: msg_pack = await self.client.send_message(MSG.channel, f"{pack_1}\n{pack_2}")
                else: msg_pack = False
                if message_obj: await self.client.delete_message(message_obj)
                return msg_pack
            # Fleeing method    ||     Success rate base on user's current STA
            elif msg.content == '!flee':
                if self.ava_dict[MSG.author.id]['STA'] <= 0: rate = self.ava_dict[MSG.author.id]['MAX_STA']//1 + 1
                else: rate = self.ava_dict[MSG.author.id]['MAX_STA']//self.ava_dict[MSG.author.id]['STA'] + 1
                # Succesfully --> End battling session
                if random.choice(range(int(rate))) == 0:
                    await self.client.say(f"{MSG.author.mention}, you've successfully escape from the mob!")
                    # Erase the current_enemy lock on off the target_id
                    del self.ava_dict[MSG.author.id]['realtime_zone']['current_enemy']['mob'][0]
                    await self.client.loop.run_in_executor(None, self.avatars_updating)
                    return False
                # Fail ---> Continue, with the consequences
                else:
                    dmgdeal = round(dmg*len(mmove))*2
                    self.ava_dict[MSG.author.id]['LP'] -= dmgdeal
                    pack_1 = f":dagger::dagger: As **{self.ava_dict[MSG.author.id]['name']}** failed to flee, **「`{current_mob}` | {self.environ[current_place]['mob'][current_mob].name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await self.client.send_message(MSG.channel, f"{pack_1}\n{pack_2}")
                    else: msg_pack = False
                    if message_obj: await self.client.delete_message(message_obj)
                    return msg_pack
            # Switching method      ||      Switching_range=5m
            elif msg.content.startswith('!switch'):
                # E: No switchee found
                try: switchee = msg.mentions[0]
                except IndexError: 
                    dmgdeal = round(dmg*len(mmove))*2
                    self.ava_dict[MSG.author.id]['LP'] -= dmgdeal
                    pack_1 = f":dagger::dagger: As **{self.ava_dict[MSG.author.id]['name']}** failed to switch, **「`{current_mob}` | {self.environ[current_place]['mob'][current_mob].name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await self.client.send_message(MSG.channel, f"{pack_1}\n{pack_2}")
                    else: msg_pack = False
                    if message_obj: await self.client.delete_message(message_obj)
                    return msg_pack
                # E: Different region
                try:
                    if current_place != self.ava_dict[switchee.id]['realtime_zone']['current_place']: 
                        await self.client(f":warning: {switchee.mention} and {MSG.author.mention}, you have to be in the same region!")
                        dmgdeal = round(dmg*len(mmove))*2
                        self.ava_dict[MSG.author.id]['LP'] -= dmgdeal
                        pack_1 = f":dagger::dagger: As **{self.ava_dict[MSG.author.id]['name']}** failed to switch, **「`{current_mob}` | {self.environ[current_place]['mob'][current_mob].name}」** has dealt a critical DMG of *{dmgdeal}*!"
                        pack_2 = await conclusing()
                        if pack_2: msg_pack = await self.client.send_message(MSG.channel, f"{pack_1}\n{pack_2}")
                        else: msg_pack = False                       
                        if message_obj: await self.client.delete_message(message_obj)
                        return msg_pack                        
                ## E: Switchee doesn't have ava
                except KeyError:
                    await self.client(f":warning: User **{switchee.name}** doesn't have an *ava*!")
                    dmgdeal = round(dmg*len(mmove))*2
                    self.ava_dict[MSG.author.id]['LP'] -= dmgdeal
                    pack_1 = f":dagger::dagger: As **{self.ava_dict[MSG.author.id]['name']}** failed to switch, **「`{current_mob}` | {self.environ[current_place]['mob'][current_mob].name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await self.client.send_message(MSG.channel, f"{pack_1}\n{pack_2}")
                    else: msg_pack = False                       
                    if message_obj: await self.client.delete_message(message_obj)
                    return msg_pack                                            
                # E: Out of switching_range
                if await self.distance_tools(self.ava_dict[MSG.author.id]['realtime_zone']['current_coord'][0], self.ava_dict[MSG.author.id]['realtime_zone']['current_coord'][1], self.ava_dict[switchee.id]['realtime_zone']['current_coord'][0], self.ava_dict[switchee.id]['realtime_zone']['current_coord'][1]) > 5:
                    await self.client(f":warning: {switchee.mention} and {MSG.author.mention}, you can only switch within *5 metres*!")
                    dmgdeal = round(dmg*len(mmove))*2
                    self.ava_dict[MSG.author.id]['LP'] -= dmgdeal
                    pack_1 = f":dagger::dagger: As **{self.ava_dict[MSG.author.id]['name']}** failed to switch, **「`{current_mob}` | {self.environ[current_place]['mob'][current_mob].name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await self.client.send_message(MSG.channel, f"{pack_1}\n{pack_2}")
                    else: msg_pack = False                     
                    if message_obj: await self.client.delete_message(message_obj)
                    return msg_pack                        
                # Wait for response
                switch_resp = await self.client.wait_for_message(timeout=5, author=switchee, channel=MSG.channel, check=check)
                # E: No response
                if not switch_resp:
                    dmgdeal = round(dmg*len(mmove))*2
                    self.ava_dict[MSG.author.id]['LP'] -= dmgdeal
                    pack_1 = f":dagger::dagger: As **{self.ava_dict[MSG.author.id]['name']}** failed to switch, **「`{current_mob}` | {self.environ[current_place]['mob'][current_mob].name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await self.client.send_message(MSG.channel, f"{pack_1}\n{pack_2}")
                    else: msg_pack = False                     
                    if message_obj: await self.client.delete_message(message_obj)
                    return msg_pack                        
                # E: Wrong user
                if MSG.author not in switch_resp.mentions:
                    dmgdeal = round(dmg*len(mmove))*2
                    self.ava_dict[MSG.author.id]['LP'] -= dmgdeal
                    pack_1 = f":dagger::dagger: As **{self.ava_dict[MSG.author.id]['name']}** failed to switch, **「`{current_mob}` | {self.environ[current_place]['mob'][current_mob].name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await self.client.send_message(MSG.channel, f"{pack_1}\n{pack_2}")
                    else: msg_pack = False                    
                    if message_obj: await self.client.delete_message(message_obj)
                    return msg_pack                                
                
                # Proceed duo-teleportation
                switchee_coord = self.ava_dict[switchee.id]['realtime_zone']['current_coord']
                await self.tele_procedure(current_place, switchee.id, self.ava_dict[MSG.author.id]['realtime_zone']['current_coord'][0], self.ava_dict[MSG.author.id]['realtime_zone']['current_coord'][1])
                await self.tele_procedure(current_place, MSG.author.id, switchee_coord[0], switchee_coord[1])
                # End the switcher PVE-session
                ## Remove the current_enemy lock-on of the switcher      
                del self.ava_dict[MSG.author.id]['realtime_zone']['current_enemy']['mob'][0]
                await self.client.loop.run_in_executor(None, self.avatars_updating)
                # Proceed PVE-session re-focus
                await self.client.say(f":arrows_counterclockwise: {MSG.author.mention} and {switchee.mention}, **SWITCH!!**")
                return [switch_resp, target_id]

                

            # Measuring response moves
            hit_count = 0
            response_content = msg.content[1:]; diff = len(counter_mmove) - len(response_content)      # Measuring the length of the response
            if diff > 0: response_content += '-'*diff                                              # Balancing the length (if needed)
            for move, response_move in zip(counter_mmove, response_content):
                if move != response_move: hit_count += 1
            print(f"HIT COUNT: {hit_count} ----- {response_content} ------ {counter_mmove}")

            # Conduct dealing dmg   ||  Conduct dealing STA dmg
            if hit_count == 0:
                dmgdeal = self.environ[current_place]['mob'][current_mob].str*len(counter_mmove)

                # Deal
                if self.ava_dict[MSG.author.id]['realtime_zone']['combat']['handling'] == 'both':
                    try:
                        def_weapon = dmgredu = 100 - self.ava_dict[MSG.author.id]['inventory'][self.ava_dict[MSG.author.id]['left_hand']]['obj']
                        dmgredu = 100 - def_weapon.defend
                    except KeyError: dmgredu = 100    
                elif self.ava_dict[MSG.author.id]['realtime_zone']['combat']['handling'] == 'right':
                    try:
                        def_weapon = self.ava_dict[MSG.author.id]['inventory'][self.ava_dict[MSG.author.id]['right_hand']]['obj']
                        dmgredu = 100 - def_weapon.defend*2
                    except KeyError: dmgredu = 100
                elif self.ava_dict[MSG.author.id]['realtime_zone']['combat']['handling'] == 'left':
                    try:
                        def_weapon = self.ava_dict[MSG.author.id]['inventory'][self.ava_dict[MSG.author.id]['left_hand']]['obj']
                        dmgredu = 100 - def_weapon.defend*2
                    except KeyError: dmgredu = 100
                self.ava_dict[MSG.author.id]['STA'] -= round(dmgdeal / 100 * dmgredu)
                
                # Inform
                pack_1 = f"·\n·\n·\n·\n:shield: {MSG.author.mention} has successfully *guarded* all **「`{target_id}` | {self.environ[current_place]['mob'][current_mob].name}」**'s attack!"
                pack_2 = await conclusing()
                if pack_2: msg_pack = await self.client.send_message(MSG.channel, f"{pack_1}\n{pack_2}")
                else: msg_pack = False
                if message_obj: await self.client.delete_message(message_obj)
                return msg_pack

            else:
                dmgdeal = self.environ[current_place]['mob'][current_mob].str*hit_count 

                # Deal
                if self.ava_dict[MSG.author.id]['realtime_zone']['combat']['handling'] == 'both':
                    try:
                        def_weapon = dmgredu = 200 - self.ava_dict[MSG.author.id]['inventory'][self.ava_dict[MSG.author.id]['left_hand']]['obj']
                        dmgredu = 200 - def_weapon.defend
                    except KeyError: dmgredu = 200    
                elif self.ava_dict[MSG.author.id]['realtime_zone']['combat']['handling'] == 'right':
                    try:
                        def_weapon = self.ava_dict[MSG.author.id]['inventory'][self.ava_dict[MSG.author.id]['right_hand']]['obj']
                        dmgredu = 200 - def_weapon.defend*2
                    except KeyError: dmgredu = 200
                elif self.ava_dict[MSG.author.id]['realtime_zone']['combat']['handling'] == 'left':
                    try:
                        def_weapon = self.ava_dict[MSG.author.id]['inventory'][self.ava_dict[MSG.author.id]['left_hand']]['obj']
                        dmgredu = 200 - def_weapon.defend*2
                    except KeyError: dmgredu = 200

                # Get dmgdeal for informing :>
                dmgdeal = round(dmgdeal / 200 * dmgredu)
                self.ava_dict[MSG.author.id]['LP'] -= dmgdeal

                # Inform
                pack_1 = f":dagger: **「`{current_mob}` | {self.environ[current_place]['mob'][current_mob].name}」** has dealt *{dmgdeal} DMG* to **{MSG.author.mention}**!"
                pack_2 = await conclusing()
                if pack_2: msg_pack = await self.client.send_message(MSG.channel, f"{pack_1}\n{pack_2}")
                else: msg_pack = False
                if message_obj: await self.client.delete_message(message_obj)
                return msg_pack
                
        if target_id not in self.ava_dict[MSG.author.id]['realtime_zone']['current_enemy']['mob']:
            self.ava_dict[MSG.author.id]['realtime_zone']['current_enemy']['mob'] = [target_id]

            # Init the fight
            message_obj = await battle(message_obj)
            while isinstance(message_obj, discord.message.Message):  
                message_obj = await battle(message_obj)
            if message_obj: 
                await self.PVE(message_obj[0], message_obj[1])
        else:
            self.ava_dict[MSG.author.id]['realtime_zone']['current_enemy']['mob'] = [target_id]

##########################

#    @commands.command(pass_context=True, aliases=['>cast'])
#    @commands.cooldown(1, 60, type=BucketType.user)
#    async def avacast(self, ctx, *args):

##########################




# ============= TACTICAL ==============
    @commands.command(pass_context=True, aliases=['>rad'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def avaradar(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        current_place = self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place']
        current_X, current_Y = self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord']
        user_ids = []
        xrange = 1; yrange = 1
        try: 
            # Get xrange
            xrange = int(args[0])
            # Get yrange. If not, yrange = xrange (scan_field is a square)
            try: yrange = int(args[1])
            except IndexError: yrange = xrange
            # Check if scan_field out of border
            if not (xrange < self.environ[current_place]['info']['border'][0] and yrange < self.environ[current_place]['info']['border'][1]):
                await self.client.say(f":warning: Out of border! {ctx.message.author.mention}, the area of this region is `{self.environ[current_place]['info']['border'][0]}km x {self.environ[current_place]['info']['border'][1]}km`")
        except IndexError: pass

        # Pacing through the required field
        xtemp = int(current_X - xrange); ytemp = int(current_Y - yrange)
        if xtemp < 0: xtemp = 0
        if ytemp < 0: ytemp = 0
        for x in self.environ[current_place]['map'][xtemp:int(current_X + xrange + 1)]:
            for block in x[ytemp:int(current_Y + yrange + 1)]:
                user_ids += block
        # Remove user's own id
        user_ids.remove(ctx.message.author.id)

        if not user_ids: await self.client.say(f":satellite: No sign of life in the radius of `{xrange*2+1}km x {yrange*2+1}km` square radius..."); return

        def makeembed(top, least, pages, currentpage):
            line = ''

            line = "**-------------------- < > --------------------**\n" 
            for user_id in user_ids[top:least]:
                line = line + f"∙ **x: {self.ava_dict[user_id]['realtime_zone']['current_coord'][0]} y: {self.ava_dict[user_id]['realtime_zone']['current_coord'][1]}**\n"
            line = line + "**-------------------- < > --------------------**" 

            reembed = discord.Embed(title = f":satellite: `{xrange*2+1}km x {yrange*2+1}km` square radius, with user as the center", colour = discord.Colour(0x011C3A), description=line)
            reembed.set_footer(text=f"Page {currentpage} of {pages}")
            return reembed
            #else:
            #    await client.say("*Nothing but dust here...*")
        
        async def attachreaction(msg):
            await self.client.add_reaction(msg, "\U000023ee")    #Top-left
            await self.client.add_reaction(msg, "\U00002b05")    #Left
            await self.client.add_reaction(msg, "\U000027a1")    #Right
            await self.client.add_reaction(msg, "\U000023ed")    #Top-right

        pages = len(user_ids)//10
        if len(user_ids)%10 != 0: pages += 1
        currentpage = 1
        myembed = makeembed(0, 10, pages, currentpage)
        msg = await self.client.say(embed=myembed)
        await attachreaction(msg)

        while True:
            try:    
                reaction, user = await self.client.wait_for_reaction(message=msg, timeout=20)
                if reaction.emoji == "\U000027a1" and user.id == ctx.message.author.id and currentpage < pages:
                    currentpage += 1
                    myembed = makeembed(currentpage*10-10, currentpage*10, pages, currentpage)
                    await self.client.edit_message(msg, embed=myembed)                        
                    await self.client.remove_reaction(msg, reaction.emoji, user)
                elif reaction.emoji == "\U00002b05" and user.id == ctx.message.author.id and currentpage > 1:
                    currentpage -= 1
                    myembed = makeembed(currentpage*10-10, currentpage*10, pages, currentpage)
                    await self.client.edit_message(msg, embed=myembed)                        
                    await self.client.remove_reaction(msg, reaction.emoji, user)
                elif reaction.emoji == "\U000023ee" and user.id == ctx.message.author.id and currentpage != 1:
                    currentpage = 1
                    myembed = makeembed(currentpage*10-10, currentpage*10, pages, currentpage)
                    await self.client.edit_message(msg, embed=myembed)                        
                    await self.client.remove_reaction(msg, reaction.emoji, user)
                elif reaction.emoji == "\U000023ed" and user.id == ctx.message.author.id and currentpage != pages:
                    currentpage = pages
                    myembed = makeembed(currentpage*10-10, currentpage*10, pages, currentpage)
                    await self.client.edit_message(msg, embed=myembed)                        
                    await self.client.remove_reaction(msg, reaction.emoji, user)
            except TypeError: 
                await self.client.delete_message(msg); break

    @commands.command(pass_context=True, aliases=['>tele'])
    async def avatele(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        region = self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place']
        if not args: await self.client.say(f":fireworks: {ctx.message.author.mention}, you are currently **x:`{self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][0]:.3f}` y: `{self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][1]:.3f}`** at `{self.environ[region]['name']}`"); return

        # COORD
        try:
            x = int(args[0])/1000; y = int(args[1])/1000
            if len(args[0]) <= 5 and len(args[1]) <= 5:
                if not x <= 50 and x >= 0 and y <= 50 and y >= 0: await self.client.say(f":warning: Please use **x** in range `0 - 50000`, **y** in range `0 - 50000`!"); return
                # Check if <distance> is provided
                try:
                    distance = int(args[2])
                    x, y = await self.distance_tools(self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][0], self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][1], x, y, distance=distance, type='d-c')
                except IndexError: pass
                # Check if there's anyone have the same coord in the coord block
                current_place = self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place']
                coord_block = self.environ[current_place]['map'][int(x)][int(y)]
                if coord_block:
                    for user_id in coord_block:
                        if self.ava_dict[user_id]['realtime_zone']['current_coord'] == [x, y]: 
                            await self.client.say(f":warning: The position has already been taken!"); return
                
                # Procede teleportation
                await self.tele_procedure(current_place, ctx.message.author.id, x, y)

                # Informmmm :>
                try: await self.client.say(f":round_pushpin: Successfully move `{distance}m` toward **x:`{x:.3f}` y: `{y:.3f}`** at `{self.environ[region]['name']}`!")
                except NameError: await self.client.say(f":round_pushpin: Successfully move to **x:`{x:.3f}` y: `{y:.3f}`** at `{self.environ[region]['name']}`!")
                await self.client.loop.run_in_executor(None, self.avatars_updating)
            else: await self.client.say(f":warning: Please use 5-digit coordinates!"); return
        except IndexError: await self.client.say(f":warning: Out of map's range!"); return

        # PLACE
        except (KeyError, ValueError):    
            if not args[0] in list(self.environ.keys()): await self.client.say(f"**{args[0]}**... There is no such place here, perhap it's from another era?"); return

            if self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][0] <= 1 and self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][1] <=1:
                self.ava_dict[ctx.message.author.id]['realtime_zone']['current_place'] = args[0]
                await self.client.say(f":round_pushpin: Successfully move to `{self.environ[args[0]]['name']}`!")
                await self.client.loop.run_in_executor(None, self.avatars_updating)
            else: await self.client.say(f":warning: You can only travel between regions inside **Peace Belt**!"); return

    @commands.command(pass_context=True, aliases=['>mdist'])
    async def measure_dist(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        try:
            distance = await self.distance_tools(self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][0], self.ava_dict[ctx.message.author.id]['realtime_zone']['current_coord'][1], int(args[0])/1000, int(args[1])/1000)
            await self.client.say(f"REsult: {distance}m")
        except IndexError: pass



# ============= ITEMS =================
## user_id is inputed seperately
       
    def heal(self, type, user_id):
        # 10%
        if type == '0': self.ava_dict[user_id]['LP'] += int(self.ava_dict[user_id]['MAX_LP']//100*10)
        # 25%
        elif type == '1': self.ava_dict[user_id]['LP'] += int(self.ava_dict[user_id]['MAX_LP']//100*25)
        # 100%
        elif type == '2': self.ava_dict[user_id]['LP'] += self.ava_dict[user_id]['MAX_LP']

        # Normalizing
        if self.ava_dict[user_id]['LP'] > self.ava_dict[user_id]['MAX_LP']: self.ava_dict[user_id]['LP'] = self.ava_dict[user_id]['MAX_LP']

    def recovery(self, type, user_id):
        # 10%
        if type == '0': self.ava_dict[user_id]['STA'] += int(self.ava_dict[user_id]['MAX_STA']//100*10)
        # 25%
        elif type == '1': self.ava_dict[user_id]['STA'] += int(self.ava_dict[user_id]['MAX_STA']//100*25)
        # 100%
        elif type == '2': self.ava_dict[user_id]['STA'] += self.ava_dict[user_id]['MAX_STA']

        # Normalizing
        if self.ava_dict[user_id]['STA'] > self.ava_dict[user_id]['MAX_STA']: self.ava_dict[user_id]['STA'] = self.ava_dict[user_id]['MAX_STA']        

    def heal_bit(self, amount, user_id):
        self.ava_dict[user_id]['LP'] += amount

        # Normalizing
        if self.ava_dict[user_id]['LP'] > self.ava_dict[user_id]['MAX_LP']: self.ava_dict[user_id]['LP'] = self.ava_dict[user_id]['MAX_LP']

    def recovery_bit(self, amount, user_id):
        self.ava_dict[user_id]['STA'] += int(self.ava_dict[user_id]['MAX_STA']//100*10)

        # Normalizing
        if self.ava_dict[user_id]['STA'] > self.ava_dict[user_id]['MAX_STA']: self.ava_dict[user_id]['STA'] = self.ava_dict[user_id]['MAX_STA']         



# ============= SPELLS =================




# ============= TOOLS =================

    async def ava_scan(self, MSG, type='all'):
        try:
            # Status check. If user_id not found, raise KeyError
            if isinstance(self.ava_dict[MSG.author.id], list): await self.client.send_message(MSG.channel, f"{MSG.author.mention}, you are **dead**. Use `-incarnate` re-incarnate."); return False
            # Time check
            if type == 'all':
                year, month, day, hour, minute = await self.client.loop.run_in_executor(None, self.time_get)
                self.ava_dict[MSG.author.id]['age'] = year - self.ava_dict[MSG.author.id]['dob'][2]
                return True
            # STA, LP, sign_in check
            elif type == 'life_check':
                if self.ava_dict[MSG.author.id]['realtime_zone']['current_coord'] == ['n/a', 'n/a']: await self.client.say(f":warning: {MSG.author.mention}, please **sign in**. Just `-tele` somewhere you like and you'll be signed in the world's map."); return False
                if self.ava_dict[MSG.author.id]['STA'] < 0: self.ava_dict[MSG.author.id]['LP'] -= abs(self.ava_dict[MSG.author.id]['STA']); self.ava_dict[MSG.author.id]['STA'] = 0
                if self.ava_dict[MSG.author.id]['LP'] <= 0:
                    # Sign out of the map
                    realtime_pack = self.ava_dict[MSG.author.id]['realtime_zone']
                    self.environ[realtime_pack['current_place']]['map'][realtime_pack['current_coord'][0]][realtime_pack['current_coord'][1]].remove(MSG.author.id)
                    self.ava_dict[MSG.author.id]['realtime_zone'] = {'current_place': 'region.0', 'current_coord': ['n/a', 'n/a'],'current_enemy': {"mob": [], "user": []}, "combat": {"handling": "2h", "buff": {}}, 'current_quest': ''}
                    # Reset
                    self.ava_dict[MSG.author.id]['mobs_collection'] = {'mob': {}, 'boss': {}}
                    self.ava_dict[MSG.author.id]["guild"] = {"name":"n/a","rank":"iron","quest":{"region.0":{"region_tier":"n/a","region_completed_quests":[]},"region.1":{"region_tier":"n/a","region_completed_quests":[]},"region.2":{"region_tier":"n/a","region_completed_quests":[]},"region.3":{"region_tier":"n/a","region_completed_quests":[]},"region.4":{"region_tier":"n/a","region_completed_quests":[]},"region.5":{"region_tier":"n/a","region_completed_quests":[]},"region.6":{"region_tier":"n/a","region_completed_quests":[]},"region.7":{"region_tier":"n/a","region_completed_quests":[]},"region.8":{"region_tier":"n/a","region_completed_quests":[]},"region.9":{"region_tier":"n/a","region_completed_quests":[]},"region.10":{"region_tier":"n/a","region_completed_quests":[]},"region.11":{"region_tier":"n/a","region_completed_quests":[]},"region.12":{"region_tier":"n/a","region_completed_quests":[]},"region.13":{"region_tier":"n/a","region_completed_quests":[]},"region.14":{"region_tier":"n/a","region_completed_quests":[]},"region.15":{"region_tier":"n/a","region_completed_quests":[]},"region.-1":{"region_tier":"n/a","region_completed_quests":[]},"region.-2":{"region_tier":"n/a","region_completed_quests":[]},"region.-3":{"region_tier":"n/a","region_completed_quests":[]},"region.-4":{"region_tier":"n/a","region_completed_quests":[]},"region.-5":{"region_tier":"n/a","region_completed_quests":[]},"region.-6":{"region_tier":"n/a","region_completed_quests":[]},"region.-7":{"region_tier":"n/a","region_completed_quests":[]},"region.-8":{"region_tier":"n/a","region_completed_quests":[]},"region.-9":{"region_tier":"n/a","region_completed_quests":[]},"region.-10":{"region_tier":"n/a","region_completed_quests":[]},"region.-11":{"region_tier":"n/a","region_completed_quests":[]},"region.-12":{"region_tier":"n/a","region_completed_quests":[]},"region.-13":{"region_tier":"n/a","region_completed_quests":[]},"region.-14":{"region_tier":"n/a","region_completed_quests":[]},"region.-15":{"region_tier":"n/a","region_completed_quests":[]}},"total_completed_quests":[]}
                    self.ava_dict[MSG.author.id]['money'] = 0
                    self.ava_dict[MSG.author.id]['perks'] = 0
                    self.ava_dict[MSG.author.id]['degrees'] = ['Instinct']
                    self.ava_dict[MSG.author.id]['right_hand'] = 'n/a'
                    self.ava_dict[MSG.author.id]['left_hand'] = 'n/a'
                    self.ava_dict[MSG.author.id]['inventory'] = {}
                    # K/D
                    self.ava_dict[MSG.author.id]['k/d'][1] += 1

                    await self.client.say(f":skull: {MSG.author.mention}, you are dead. Please re-incarnate.")
                    await self.client.loop.run_in_executor(None, self.avatars_updating)
                    return False
                return True
            # Readjust the incorrect value
            elif type == 'normalize':
                if self.ava_dict[MSG.author.id]['STA'] > self.ava_dict[MSG.author.id]['MAX_STA']: self.ava_dict[MSG.author.id]['STA'] = self.ava_dict[MSG.author.id]['MAX_STA']
                if self.ava_dict[MSG.author.id]['LP'] > self.ava_dict[MSG.author.id]['MAX_LP']: self.ava_dict[MSG.author.id]['LP'] = self.ava_dict[MSG.author.id]['MAX_LP']
                return True
        # E: Avatar not found
        except KeyError: await self.client.send_message(MSG.channel, f"{MSG.author.mention}, you don't have an *avatar*. Use `-incarnate` to create one.")

    async def area_scan(self, ctx, x, y):
        if x <= 1 and y <= 1: return True
        else: return False

    async def ava_manip(self, MSG, function, *args):
        """· def stt_adjust(parameter, adjustment, value)
           · def stt_check(path)    ---    Dict only, seperate by /"""
        user_id = MSG.author.id

        def stt_adjust(parameter, adjustment, value):
            if adjustment == 'add': self.ava_dict[user_id][parameter] += int(value)
            elif adjustment == 'subtract': self.ava_dict[user_id][parameter] += int(value)
            elif adjustment == 'multiply': self.ava_dict[user_id][parameter] = int(self.ava_dict[user_id][parameter]*value)
            elif adjustment == 'divide': self.ava_dict[user_id][parameter] = int(self.ava_dict[user_id][parameter]//value)

        def stt_check(path, creation_perm, endpoint=''):
            a = path.split('/')
            copy = self.ava_dict[user_id][a[0]]
            # Traverse. In case trarvesing is jammed, create the following nodes if permitted
            for node in a[1:]:
                try: copy = copy[node]
                except KeyError: 
                    if creation_perm == 1: 
                        # Make extra node
                        extra_node = {}; stuff = {}
                        for minode in reversed(a[a.index(node) + 1:]):
                            if a.index(minode) == -1: stuff = endpoint; continue
                            # Wrap stuff inside extra_node, labeled with minode. Then make extra_node a stuff
                            extra_node[minode] = stuff
                            stuff = extra_node
                        
                        print(extra_node)
                        print(self.ava_dict[user_id][a[0]])
                        # Replicate old one/nối dài 
                        old_node = {}; stuff_2 = []
                        print(a[1:a.index(node) + 1])
                        for minode in a[1:a.index(node) + 1]:
                            if a.index(minode) == 1: stuff_2.append(self.ava_dict[user_id][a[0]]); print("HERERERERRRRRRRR")
                            elif a.index(minode) == a.index(node): 
                                print("HUUUUUUUURURUR")
                                print(node)
                                print(minode)
                                #old_node = stuff_2[-1]
                                #stuff_2.append(old_node[node])
                                old_node = stuff_2[-1]
                                #thing[node] = extra_node
                                old_node[a[a.index(minode) - 1]] = {node: extra_node}
                                stuff_2[-1] = old_node
                            else: 
                                print("HEEEEEEEEEEE???")
                                old_node = stuff_2[-1]
                                #old_node[minode] = {node: extra_node}
                                old_node[a[a.index(minode) - 1]] = {node: extra_node}
                                stuff_2.append(old_node) 

                        print(stuff_2)
                        somenode = ''
                        if len(stuff_2) > 1:
                            for binode, minode in zip(reversed(stuff_2), reversed(a[1:a.index(node) + 1])):
                                stuff_2.reverse()
                                prev_binode = stuff_2[stuff_2.index(binode) - 1]
                                if not somenode: prev_binode[minode] = binode; somenode = prev_binode
                                else:
                                    prev_binode[minode] = somenode; somenode = prev_binode

                            self.ava_dict[user_id][a[0]] = somenode                        
                        
                    else: raise KeyError
                    print(self.ava_dict[user_id][a[0]])
                    return endpoint
            return copy

        if function == 'stt_adjust': stt_adjust(args[0], args[1], float(args[2]))
        # args[1]:Permission    args[2]:enpoint
        elif function == 'stt_check': 
            try: return stt_check(args[0], args[1], args[2])
            except IndexError: 
                try: return stt_check(args[0], args[1])
                except IndexError: return stt_check(args[0], 0)

    async def converter(self, type, *args):
        if type == 'sec_to_hms':
            hour = args[0]//3600
            if hour != 0: 
                secleft = args[0]%3600
                min = secleft//60
            else:
                secleft = args[0]
                min = secleft//60
            if min != 0:
                sec = secleft%60
            else:
                sec = secleft
            return (hour, min, sec)

    def objectize(self, dict, type, *args): 
        if type[0] == 'weapon':
            if type[1] == 'melee':
                return weapon((dict['name'], dict['id'], dict['description'], dict['tags'], dict['price'], dict['weight'], dict['defend'], dict['multiplier'], dict['str'], dict['sta'], dict['speed'], dict), 'melee')
            elif type[1] == 'range_weapon':
                return weapon((dict['name'], dict['id'], dict['description'], dict['tags'], dict['price'], dict['weight'], dict['defend'], dict['round'], dict['str'], dict['int'], dict['sta'], dict['accuracy'], dict['range'], dict['firing_rate'], dict['stealth'], dict), 'range_weapon')
        elif type[0] == 'ammunition':
            return ammunition((dict['name'], dict['id'], dict['description'], dict['tags'], dict['price'], dict['dmg'], dict['speed'], dict))
        elif type[0] == 'supply':
            return item((dict['name'], dict['id'], dict['description'], dict['tags'], dict['price'], dict), args[0])
        elif type[0] == 'ingredient':
            return ingredient((dict['name'], dict['id'], dict['description'], dict['tags'], dict['price'], dict), args[0])

    #Generate random file's name from the path
    async def file_gen_random(self, path):
        file_name = ''
        file_name = await self.client.loop.run_in_executor(None, random.choice, await self.client.loop.run_in_executor(None, listdir, path))
        return file_name

    async def distance_tools(self, x1, y1, x2, y2, distance=0, type='c-d'):
        """|| Tools\n
           x1, y1, x2, y2, distance: float\n
           (x1, y1: user's coord)\n
           return: distance"""

        if type == 'c-d':
            dist_x = abs(x1 - x2); dist_y = abs(y1 - y2)

            return int(math.sqrt(dist_x*dist_x + dist_y*dist_y)*1000)

        elif type == 'd-c':
            dist_x = abs(x1 - x2); dist_y = abs(y1 - y2)
            # Distance from A to B      ||      distance --> Distance from A to C
            full_dist = math.sqrt(dist_x*dist_x + dist_y*dist_y)*1000

            # Thales thingy
            small_dist_x = (distance*dist_x)/full_dist
            small_dist_y = (distance*dist_y)/full_dist

            # Calc coord, then return
            if x1 >= x2: C_x = x1 - small_dist_x
            else: C_x = x1 + small_dist_x
            if y1 >= y2: C_y = y1 - small_dist_y
            else: C_y = y1 + small_dist_y
            
            return C_x, C_y #round(C_x, 3) , round(C_y, 3)

    async def tele_procedure(self, current_place, user_id, desti_x, desti_y):
        """x, y: float"""
        # Assign the user's id to coord / Resign the user's id from the old coord
        self.environ[current_place]['map'][int(desti_x)][int(desti_y)].append(user_id)
        self.environ[current_place]['map'][int(self.ava_dict[user_id]['realtime_zone']['current_coord'][0])][int(self.ava_dict[user_id]['realtime_zone']['current_coord'][1])].remove(user_id)
        # Assign the coord to ava
        self.ava_dict[user_id]['realtime_zone']['current_coord'] = [desti_x, desti_y]

    @commands.command(pass_context=True)
    @check_id()
    async def get_imgur(self, ctx, *args):
        if args:
            if '.png' not in args[0] or '.jpg' not in args[0] or '.jpeg' not in args[0] or '.gif' not in args[0]:
                await self.client.say(f":warning: {ctx.message.author.mention}, invalid link!"); return
            else: source = args[0]
        else:
            package = ctx.message.attachments
            if package: source = package[0]['proxy_url']
            else: return

        resp = await self.client.loop.run_in_executor(None, self.imgur_client.upload_from_url, source)
        reembed = discord.Embed(description=f"{resp['link']}", colour = discord.Colour(0x011C3A))
        reembed.set_image(url=resp['link'])
        await self.client.say(embed=reembed)



# ============= DATA MANIPULATION =================

    @commands.command(pass_context=True)
    @check_id()
    async def avadata_add(self, ctx, *args):
        raw = list(args); data_obj = {}
        dir = raw[0].split('.')

        # Split raw into info pieces, as well as pack it into <data_obj>
        for piece in raw[1:]:
            piece = piece.split('==')
            data_obj[piece[0]] = piece[1]
        # Update the self.data
        try:
            if dir[0] == 'item':
                if dir[1] == 'arsenal':
                    data_obj['id'] = str(int(self.data['item']['arsenal'][dir[2]][-1]['id']) + 1)   # Get data_obj's id
                    self.data['item']['arsenal'][dir[2]].append(data_obj)
                    await self.client.loop.run_in_executor(None, self.data_updating, 'arsenal')
        except IndexError: await self.client.say(":warning: Invalid directory!")

        await self.client.say(":white_check_mark: Item added!")

    @commands.command(pass_context=True)
    @check_id()
    async def avaava_kill(self, ctx, *args):
        u = ' '.join(args)
        try: 
            del self.ava_dict[u]
            await self.client.say(f":white_check_mark: User **{u}** is deleted!")
            await self.client.loop.run_in_executor(None, self.avatars_updating)
        except KeyError: await self.client.say(f":x: User **{u}** not found!")

    def time_get(self):
        day = 1; month = 1; year = 1
        delta = relativedelta(datetime.now(), self.client.STONE)
        #print(f"DELTA: {delta.days} || {delta.months} || {delta.years}")

        if not delta.months: delta.months = 1
        if not delta.years: delta.years = 1
        # Year
        year = (delta.days+(delta.months*30))*delta.years
        # Month
        try: month = int(delta.hours/2)
        except: pass
        secs_temp = delta.seconds + 60*delta.minutes + 3600*(delta.hours%2)
        # Day
        day = int(secs_temp/240)
        # Hour
        if secs_temp <= 240:
            hour = int(secs_temp/10)
        elif secs_temp > 240:
            hour = int((secs_temp%240)/10)
        # Minute
        if secs_temp <= 10:
            minute = int(secs_temp/0.16)
        elif secs_temp > 10:
            minute = int((secs_temp%10)/0.16)

        if not year: year = 1
        if not month: month = 1
        
        return year, month, day, hour, minute
                
    def avatars_updating(self, type='obj_included'):
        if not type: type = 'obj_included'
        if type == 'obj_included':
            temp = copy.deepcopy(self.ava_dict)
            for user_id in list(temp.keys()):
                for item_id in list(temp[user_id]['inventory'].keys()):
                    try: temp[user_id]['inventory'][item_id]['obj'] = {}
                    # E: UN-SERI
                    except TypeError: pass

            with open('data/avatar.json', 'w') as f:
                json.dump(temp, f, indent=4)
            
        else:
            with open('data/avatar.json', 'w') as f:
                json.dump(self.ava_dict, f, indent=4)

    def avatars_plugin(self):
        with open('data/avatar.json') as f:
            try:
                self.ava_dict = json.load(f)
            except IndexError: print("ERROR at <avatars_plugin()>")

    def avatars_plugin_2(self):
        for user_id in list(self.ava_dict.keys()):
            for item_id in list(self.ava_dict[user_id]['inventory'].keys()):
                try:
                    self.ava_dict[user_id]['inventory'][item_id]['obj'] = self.objectize(self.ava_dict[user_id]['inventory'][item_id]['dict'], ['weapon', self.ava_dict[user_id]['inventory'][item_id]['dict']['tags'][1]])
                # E: UN-SERIALIZABLE
                except (KeyError, TypeError): pass

    def data_plugin(self):

        # TIME get
        with open('data/time.json') as f:
            try:
                time_pack = json.load(f)
            except IndexError: print("ERROR at <data_plugin(__TIME__)>")
        self.client.STONE = datetime(time_pack[0], time_pack[1], time_pack[2], hour=time_pack[3], minute=time_pack[4])


        # JOBS get
        with open('data/jobs.json') as f:
            try:
                self.jobs_dict = json.load(f)
            except IndexError: print("ERROR at <data_plugin(__JOBS__)>")


        # ARSENAL Inventories get
        with open('data/arsenal.json') as f:
            try:
                self.data_ARSENAL = json.load(f)
            except IndexError: print("ERROR at <data_plugin(__ARSENAL__)>")
        for id in list(self.data_ARSENAL.keys()):
            self.data_ARSENAL[id] = self.objectize(self.data_ARSENAL[id], ['weapon', self.data_ARSENAL[id]['tags'][1]])
        print('___ARSENAL plugin() done')


        # AMUNNITION Inventories get
        with open('data/ammunition.json') as f:
            try:
                self.data_AMMU = json.load(f)
            except IndexError: print("ERROR at <data_plugin(__AMMU__)>")
        for id in list(self.data_AMMU.keys()):
            self.data_AMMU[id] = self.objectize(self.data_AMMU[id], ['ammunition'])
        print('___AMMU plugin() done')


        # SUPPLY Inventories get        
        with open('data/supply.json') as f:
            try:
                self.data_SUPPLY = json.load(f)
            except IndexError: print("ERROR at <data_plugin(__SUPPLY__)>")
        supfunc_dict = {'it0': [self.heal, '0'], 'it1': [self.heal, '1'], 'it2': [self.heal, '2'], 'it3': [self.recovery, '0'], 'it4': [self.recovery, '1'], 'it5': [self.recovery, '2']}                
        for id in list(self.data_SUPPLY.keys()):
            self.data_SUPPLY[id] = self.objectize(self.data_SUPPLY[id], ['supply'], supfunc_dict[id])
        print('___SUPPLY plugin() done')


        # INGREDIENT
        data_INGREDIENT = {}
        with open('data/ingredient.json') as f:
            try:
                data_INGREDIENT = json.load(f)
            except IndexError: print("ERROR at <data_plugin(__INGREDIENT__)>")
        igfunc_dict = {'ig0': [self.recovery_bit, 10], 'ig1': [self.recovery_bit, 10], 'ig2': [self.recovery_bit, 30]}                                
        for id in list(data_INGREDIENT.keys()):
            data_INGREDIENT[id] = self.objectize(data_INGREDIENT[id], ['ingredient'], igfunc_dict[id])
        print('___INGREDIENT plugin() done')


        # QUESTS
        data_QUESTS = {}
        with open('data/quests.json') as f:
            try:
                data_QUESTS = json.load(f)
            except IndexError: print("ERROR at <data_plugin(__QUESTS__)>")
        print('___QUESTS plugin() done')


        # ENTITIES
        data_ENTITY = {}
        with open('data/living_entities.json') as f:
            try:
                data_ENTITY = json.load(f)
            except IndexError: print("ERROR at <data_plugin(__ENTITY__)>")
        print('___ENTITY plugin() done')


        # REGION    
        data_REGION = {}  
        with open('data/region.json') as f:
            try:
                data_REGION = json.load(f)
            except IndexError: print("ERROR at <data_plugin(__REGION__)>")
        print('___REGION plugin() done')        


        # ENTITY and INGREDIENT are dictionaries to look up, not to be used
        self.data = {'item': {**self.data_ARSENAL, **self.data_SUPPLY, **self.data_AMMU}, 'entity': data_ENTITY, 'ingredient': data_INGREDIENT}
        self.environ = data_REGION


        def world_built():
            for floor in list(self.environ.keys()):
                
                # ----------- MOB initialize ------------
                for mob_pack in self.environ[floor]['info']['diversity']:
                    # Get the <mob> prototype
                    protomob = self.data['entity']['mob'][mob_pack[0]]
                    
                    # Mass production
                    for count in range(mob_pack[1]):

                        if not self.environ[floor]['mob']: 
                            self.environ[floor]['mob']['mob.0'] = mob(protomob); continue
                            #self.environ[floor]['mob']['slime.0'] = mob('slime.0', 50, 10, {'money': ['money', 5, 1]}); continue

                        prev_name = list(self.environ[floor]['mob'].keys())[-1].split('.')
                        name = f"{prev_name[0]}.{int(prev_name[-1]) + random.choice(range(5))}"
                        
                        self.environ[floor]['mob'][name] = mob(protomob)

                # ----------- BOSS initialize ------------
                for boss_id, boss_info in self.environ[floor]['info']['boss'].items():
                    self.environ[floor]['mob'][boss_id] = mob(self.data['entity']['boss'][boss_info[0]])

                # ----------- MAP initialize -------------
                map = []
                for x in range(51):
                    x = []
                    for y in range(51):
                        x.append([])
                    map.append(x)
                #Assign user's id onto the map
                for user_id in list(self.ava_dict.keys()):
                    try: map[int(self.ava_dict[user_id]['realtime_zone']['current_coord'][0])][int(self.ava_dict[user_id]['realtime_zone']['current_coord'][1])].append(user_id)
                    except TypeError: pass
                #Return the map
                self.environ[floor]['map'] = map
                
                # ----------- QUESTS initialize ----------                
                try: self.environ[floor]['characteristic']['quest'] = data_QUESTS
                except KeyError: print("KEY_ERROR")
            
            print("___WORLD built() done")  

        world_built()
        
    def data_updating(self, update_kw):
        if update_kw == 'arsenal':
            with open('data/arsenal.json', 'w') as f:
                json.dump(self.data['item']['arsenal'], f, indent=4)
        elif update_kw == 'time_pack':    
            time_pack = (self.client.STONE.year, self.client.STONE.month, self.client.STONE.day, self.client.STONE.hour, self.client.STONE.minute)
            with open('data/time.json', 'w') as f:
                json.dump(time_pack, f, indent=4)

    async def prote_plugin(self):
        #def byte_supporter(img, output_buffer, char):
        #    output_buffer = BytesIO()
        #    img.save(output_buffer, 'png')
        #    output_buffer.seek(0)
        #    self.prote_lib[char].append(output_buffer)

        def ImageGen_supporter(char, rawimg):
            img = Image.open(f'C:/Users/DELL/Desktop/bot_cli/data/profile/char/{char}/{rawimg}').convert('RGBA')
            self.prote_lib[char].append(img)

        def bg_plugin(): 
            self.prote_lib['bg'] = []
            img = Image.open(f'C:/Users/DELL/Desktop/bot_cli/data/profile/bg/LoveRibbon/tv roomalt.jpg').convert('RGBA')
            self.prote_lib['bg'].append(img)
        
        def form_plugin():
            self.prote_lib['form'] = []
            img = Image.open('C:/Users/DELL/Desktop/bot_cli/data/profile/form3.png').convert('RGBA')
            self.prote_lib['form'].append(img)
        
        def badge_plugin():
            ranking_badges = {'iron': 'badge_IRON.png', 'bronze': 'badge_BRONZE.png', 'silver': 'badge_SILVER.png', 'gold': 'badge_GOLD.png', 'adamantite': 'badge_ADAMANTITE.png', 'mithryl': 'badge_MITHRYL.png'}
            self.prote_lib['badge'] = {}
            for key, dir in ranking_badges.items():
                self.prote_lib['badge'][key] = Image.open(f'C:/Users/DELL/Desktop/bot_cli/data/profile/badges/{dir}').convert('RGBA')

        def font_plugin():
            self.prote_lib['font'] = {}
            self.prote_lib['font']['name'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/profile/ERASLGHT.ttf', 70)    # Name
            self.prote_lib['font']['degree'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/profile/ERASLGHT.ttf', 14)  # Degrees
            self.prote_lib['font']['age'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/profile/ERASLGHT.ttf', 54)     # Age
            self.prote_lib['font']['k/d'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/profile/ERASLGHT.ttf', 59)    # K/D
            self.prote_lib['font']['evo'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/profile/ERASLGHT.ttf', 122)    # Evo
            self.prote_lib['font']['guild'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/profile/ERASLGHT.ttf', 19)   # Guild
            self.prote_lib['font']['rank'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/profile/ERASLGHT.ttf', 39)    # Rank
            self.prote_lib['font']['money'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/profile/ERASLGHT.ttf', 53)   # Money

        await self.client.loop.run_in_executor(None, bg_plugin)
        await self.client.loop.run_in_executor(None, form_plugin)
        await self.client.loop.run_in_executor(None, font_plugin)
        await self.client.loop.run_in_executor(None, badge_plugin)
        for char in ['Iris', 'Zoey', 'Ardena']:
            self.prote_lib[char] = []
            for rawimg in listdir(f'C:/Users/DELL/Desktop/bot_cli/data/profile/char/{char}'):
                await self.client.loop.run_in_executor(None, ImageGen_supporter, char, rawimg)


        print('___PROTE plugin() done')



class mob:
    def __init__(self, whole_pack):
        self.name = whole_pack['name']
        self.lp = whole_pack['lp']
        self.str = whole_pack['str']
        self.speed = whole_pack['speed']
        self.drop = whole_pack['drop']
        self.branch = whole_pack['branch']
        self.chain = whole_pack['chain']

    def attack(self):
        mmoves = [random.choice(['a', 'd', 'b']) for move in range(self.chain)]
        
        # Decoding moves, as well as checking the moves. Get the counter_move
        counter_mmove = []
        for move in mmoves:
            if move == 'a': counter_mmove.append('d')
            elif move == 'd': counter_mmove.append('b')
            elif move == 'b': counter_mmove.append('a')

        dmg = self.str
        return dmg, mmoves, counter_mmove

    #def defend(self, )

    def drop_item(self):
        drops = []
        for item in list(self.drop.keys()):
            # [0]: Item's name || [1]: Quantity || [2]: Drop rate
            ###Randoming pick
            if random.choice(range(self.drop[item][2])) == 0:
                ###Randoming quantity
                drops.append([self.drop[item][0], random.choice(range(self.drop[item][1]))])
        return drops
            
class item:
    """
    package: A tuple of status required to create an item\n
    func:    A list containing: 1.Function 2.Other values required"""
    def __init__(self, package, func):
        self.name, self.id, self.description, self.tags, self.price, self.bkdict = package
        self.func = func

class ingredient:
    """
    package: A tuple of status required to create an item\n
    func:    A list containing: 1.Function 2.Other values required"""
    def __init__(self, package, func):
        self.name, self.id, self.description, self.tags, self.price, self.bkdict = package
        self.func = func

class weapon:
    def __init__(self, package, type, func=None, upgrade=None):
        # Unpack guidance
        if type == 'melee': self.name, self.id, self.description, self.tags, self.price, self.weight, self.defend, self.multiplier, self.str, self.sta, self.speed, self.bkdict = package
        elif type == 'range_weapon': self.name, self.id, self.description, self.tags, self.price, self.weight, self.defend, self.round, self.str, self.int, self.sta, self.accuracy, self.range, self.firing_rate, self.stealth, self.bkdict = package

        self.func = func
        self.upgrade = upgrade

class ammunition:
    def __init__(self, package):
        self.name, self.id, self.description, self.tags, self.price, self.dmg, self.speed, self.bkdict = package

def setup(client):
    client.add_cog(avasoul(client))



















