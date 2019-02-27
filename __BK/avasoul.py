import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors

import asyncio
import random
import json
import math
import copy
from datetime import datetime, timedelta
from io import BytesIO
from os import listdir
import re

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from dateutil.relativedelta import relativedelta
import redis
from functools import partial
import imageio
from imgurpython import ImgurClient
import numpy as np
import aiomysql
import pymysql.err as mysqlError

redio = redis.Redis('localhost')

async def get_CURSOR():
    conn = await aiomysql.connect(host='localhost', user='root', password='mysql', port=3307, db='mycli', autocommit=True)
    _cursor = await conn.cursor()
    return conn, _cursor

loop = asyncio.get_event_loop()    
conn, _cursor = loop.run_until_complete(get_CURSOR())

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
        await self.data_plugin()
        await self.client.loop.run_in_executor(None, self.avatars_plugin_2)
        #await self.intoSQL()
        await self.prote_plugin()

    async def __cd_check(self, MSG, cmd_tag, warn):
        cdkey = cmd_tag + MSG.author.id
        if redio.exists(cdkey):
            sec = await self.client.loop.run_in_executor(None, redio.ttl, cdkey)
            sec = await self.converter('sec_to_hms', sec)
            await self.client.send_message(MSG.channel, f"{warn} Please wait **`{sec[0]}:{sec[1]}:{sec[2]}`**."); return False
        else: return True

        #        async def intoSQL(self):
        #            count = 17
        #            for key, pack in self.data['entity']['boss'].items():
        #                await _cursor.execute(f"""INSERT INTO model_mob VALUES ('mb{count}', "{pack['name']}", "{pack['branch']}", {pack['lp']}, {pack['str']}, {pack['chain']}, {pack['speed']}, 'query_goes_here');""")
        #                count += 1

        #        for id, item in self.data['item'].items():
        #            if 'melee' in item.tags: 
        #                query = f"INSERT INTO model_item (item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, price) VALUES ('{item.id}', '{item.name}', '{item.description}', '{' - '.join(item.tags)}', {item.weight}, {item.defend}, {item.multiplier}, {item.str}, 0, {item.sta}, {item.speed}, {item.price});"
        #            elif 'range_weapon' in item.tags: 
        #                query = f"INSERT INTO model_item (item_code, name, description, tags, weight, defend, round, str, intt, sta, price, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate) VALUES ('{item.id}', '{item.name}', '{item.description}', '{' - '.join(item.tags)}', {item.weight}, {item.defend}, '{item.round}', {item.str}, {item.int}, {item.sta}, {item.price}, {item.accuracy[0]}, {item.accuracy[1]}, {item.range[0]}, {item.range[1]}, {item.firing_rate});"
        #            elif 'supply' in item.tags: 
        #                query = f"INSERT INTO model_item (item_code, name, description, tags, price) VALUES ('{item.id}', '{item.name}', '{item.description}', '{' - '.join(item.tags)}', {item.price});"
        #            elif 'ammunition' in item.tags: 
        #                query = f"INSERT INTO model_item (item_code, name, description, tags, price, dmg, speed) VALUES ('{item.id}', '{item.name}', '{item.description}', '{' - '.join(item.tags)}', {item.price}, {item.dmg}, {item.speed});"
        #            print(query)
        #            await self.quefe(query)            
        #
        #        print("___SQL DONE ________________")

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
    @commands.cooldown(1, 5, type=BucketType.user)
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

        resu = await self.quefe(f"SELECT status FROM personal_info WHERE id='{id}'")
        if resu[0] != 'DEAD':
            await self.client.send_message(ctx.message.channel, f":warning: You've already incarnate!"); return

        ava = {}
        year, month, day, hour, minute = await self.client.loop.run_in_executor(None, self.time_get)

        if not resu:
            ava['name'] = name
            ava['dob'] = f"{day} - {month} - {year}"
            ava['age'] = 0
            ava['gender'] = random.choice(['m', 'f'])
            ava['race'] = random.choice(['rc0', 'rc1', 'rc2', 'rc3'])
            r_aura, r_min_H, r_max_H, r_min_W, r_max_W, r_size_1, r_size_2, r_size_3 = await self.quefe(f"SELECT aura, min_H, max_H, min_W, max_W, size_1, size_2, size_3 FROM model_race WHERE race_code='{ava['race']}';")
            if ava['gender'] == 'm':
                ava['height'] = random.choice(range(r_min_H + 10, r_max_H + 10))
                ava['weight'] = random.choice(range(r_min_W + 10, r_max_W + 10))
                ava['size'] = '78 - 80 - 90'
            else:
                ava['height'] = random.choice(range(r_min_H - 10, r_max_H - 10))
                ava['weight'] = random.choice(range(r_min_W - 10, r_max_W - 10))
                r_size_1 = r_size_1.split(' - '); r_size_2 = r_size_2.split(' - '); r_size_3 = r_size_3.split(' - ')
                ava['size'] = f'{random.choice(range(r_size_1[0], r_size_1[1]))} - {random.choice(range(r_size_2[0], r_size_2[1]))} - {random.choice(range(r_size_3[0], r_size_3[1]))}'

            # Charm calc
            ava['charm'] = 10
            if ava['height'] >= 180: ava['charm'] += 5
            elif ava['height'] <= 130: ava['charm'] -= 5
            
            if ava['weight'] <= 35 or ava['weight'] >= 90: ava['charm'] -= 5
            else: ava['charm'] += 5

            szl = ava['size'].split(' - ')
            if int(szl[0]) >= 25: ava['charm'] += 5
            if int(szl[1]) >= 75: ava['charm'] -= 5
            if int(szl[2]) >= 115: ava['charm'] += 5
            
            ava['partner'] = 'n/a'
            ava['avatar'] = 'av0'
            ava['avatars'] = ['av0', 'av1', 'av2']
            ava['EVO'] = 0
            ava['INTT'] = 0
            ava['STA'] = 100
            ava['MAX_STA'] = 100
            ava['STR'] = 0.5
            ava['LP'] = 1000
            ava['MAX_LP'] = 1000        
            ava['kills'] = 0; ava['deaths'] = 0
            ava['money'] = 100
            ava['perks'] = 0
            auras = {'FLAME': [0.5, 0, 0, 0], 'ICE': [0, 0.5, 0, 0], 'HOLY': [0, 0, 0.5, 0], 'DARK': [0, 0, 0, 0.5]}
            ava['auras'] = auras[r_aura]

            ava['arts'] = {'sword_art': {'chain_attack': 4}, 'pistol_art': {}}

            ava['cur_PLACE'] = 'region.0'
            ava['cur_MOB'] = 'n/a'
            ava['cur_USER'] = 'n/a'
            ava['cur_X'] = -1
            ava['cur_Y'] = -1
            ava['cur_QUEST'] = 'n/a'
            ava['combat_HANDLING'] = 'both'
            ava['right_hand'] = 'ar13'
            ava['left_hand'] = 'ar13'

            await self.quefe(f"INSERT INTO personal_info VALUES ('{id}', '{ava['name']}', '{ava['dob']}', {ava['age']}, '{ava['gender']}', '{ava['race']}', {ava['height']}, {ava['weight']}, '{ava['size']}', {ava['kills']}, {ava['deaths']}, {ava['charm']}, {ava['partner']}, {ava['money']}, {ava['perks']}, {ava['EVO']}, {ava['STR']}, {ava['INTT']}, {ava['STA']}, {ava['MAX_STA']}, {ava['LP']}, {ava['MAX_LP']}, {ava['auras'][0]}, {ava['auras'][1]}, {ava['auras'][2]}, {ava['auras'][3]}, '{ava['cur_MOB']}', '{ava['cur_USER']}', '{ava['cur_PLACE']}', {ava['cur_X']}, {ava['cur_Y']}, '{ava['cur_QUEST']}', '{ava['combat_HANDLING']}', '{ava['right_hand']}', '{ava['left_hand']}');")
            await self.quefe(f"INSERT INTO degrees VALUES ('{id}', 'Instinct');")
            # Guild
            await _cursor.execute(f"INSERT INTO pi_guild VALUES ('{id}', '{ava['name']}', 'iron', 0);")
            # Avatars
            for ava_code in ava['avatars']: await _cursor.execute(f"INSERT INTO pi_avatars VALUES ('{id}', '{ava_code}');")
            await _cursor.execute(f"INSERT INTO cosmetic_preset VALUES (0, '{ctx.message.author.id}', 'default of {ava['name']}','DEFAULT', 'av0', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF')")
            await _cursor.execute(f"INSERT INTO cosmetic_preset VALUES (0, '{ctx.message.author.id}', 'default of {ava['name']}', 'CURRENT', 'av0', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF')")
            # Arts
            await _cursor.execute(f"INSERT INTO pi_arts VALUES ('{ctx.meesage.author.id}', 'sword', 'chain_attack', 5)")
            # Inventory     ||      Add fist as a default weapon
            await _cursor.execute(f"INSERT INTO pi_inventory SELECT 0, {ctx.message.author.id}, item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, quantity, price, dmg, stealth, aura, illulink FROM model_item WHERE item_code='ar13';")
            #self.ava_dict[id] = ava 
            await self.client.say(f":white_check_mark: {ctx.message.author.mention} has successfully incarnated. **Welcome to this world!**")
        else:
            await self.quefe(f"UPDATE personal_info SET LP=1, STA=0, status='GREEN' WHERE id='{id}'")
            await self.client.say(f":white_check_mark: {ctx.message.author.mention} has successfully incarnated. **WELCOME BACK!**")            

    @commands.command(pass_context=True, aliases=['>'])
    async def ava(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        await self.ava_scan(ctx.message, type='all')

        try:
            id = ctx.message.mentions[0].id
            name = ctx.message.mentions[0].name
            _vmode = 'INDIRECT'
        except IndexError: id = ctx.message.author.id; name = ctx.message.author.name; _vmode = 'DIRECT'

        
        # Data get and paraphrase
        try: name, age, gender, money, right_hand, left_hand, combat_HANDLING, STA, MAX_STA, LP, MAX_LP, STR, INTT, partner  = await self.quefe(f"SELECT name, age, gender, money, right_hand, left_hand, combat_HANDLING, STA, MAX_STA, LP, MAX_LP, STR, INTT FROM personal_info WHERE id='{id}'")        
        except TypeError: await self.client.say(":warning: User has not incarnated!"); return

        if ctx.message.author.id not in ['214128381762076672', partner]: await self.client.say(":warning: You have to be user's *partner* to view their status!"); return

        degrees = '` `'.join(await self.quefe(f"SELECT degree FROM pi_degrees WHERE user_id='{id}';"))
        if right_hand != 'n/a':
            if right_hand == 'ar13': rh_name = await self.quefe(f"SELECT name FROM pi_inventory WHERE item_code='{right_hand}' AND user_id='{ctx.message.author.id}';")
            else: rh_name = await self.quefe(f"SELECT name FROM pi_inventory WHERE item_id='{right_hand}' AND user_id='{ctx.message.author.id}';")
            right_hand = f"`{right_hand}`|**{rh_name[0]}**"
        if left_hand != 'n/a': 
            if left_hand == 'ar13': lh_name = await self.quefe(f"SELECT name FROM pi_inventory WHERE item_code={left_hand} AND user_id='{ctx.message.author.id}';")
            else: lh_name = await self.quefe(f"SELECT name FROM pi_inventory WHERE item_id={left_hand} AND user_id='{ctx.message.author.id}';")
            left_hand = f"`{left_hand}`|**{lh_name[0]}**"

        # Status
        box = f"**{name}**\n**|** `Age` · {age}\n**|** `Gender` · {gender}\n**|** `Money` · ${money}\n····················\n**||** ` RIGHT` · {right_hand}⠀⠀⠀**||** `LEFT` · {left_hand}⠀⠀⠀**||** `POSE` · {combat_HANDLING} hand\n**·** `STA` {STA}/{MAX_STA}\n**·** `LP` {LP}/{MAX_LP}\n**·** `STR` {STR}\n**·** `INT` {INTT}"
        # Degrees
        box = box + f"\n**|** Degrees: `{degrees}`"
        await self.client.send_message(ctx.message.channel, box)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 30, type=BucketType.user)
    async def prote(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        await self.ava_scan(ctx.message, type='all')

        __mode = 'static'

        # Console
        raw = list(args)
        try:
            if raw[0] == 'gif': __mode = 'gif'
        except IndexError: pass

        # Colour n Character get
        co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death, char_name = await self.quefe(f"SELECT co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death, avatar_id FROM cosmetic_preset WHERE user_id='{ctx.message.author.id}' AND status='CURRENT';")
        #co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death = ('#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF')

        # STATIC =========
        async def magiking(ctx):

            # Info get
            age, evo, kill, death, money, name = await self.quefe(f"SELECT age, evo, kills, deaths, money, name FROM personal_info WHERE id='{ctx.message.author.id}';")
            guild_region, rank = await self.quefe(f"SELECT name, rank FROM pi_guild WHERE user_id='{ctx.message.author.id}';")
            g_region_name = await self.quefe(f"SELECT name FROM environ WHERE environ_code='{guild_region}';"); g_region_name = g_region_name[0]

            form_img = self.prote_lib['form'][0]
            char_img = self.prote_lib[char_name][random.choice(range(10))]
            char_img = char_img.resize((int(form_img.height/char_img.height*char_img.width), form_img.height))
            badge_img = self.prote_lib['badge'][rank.lower()]
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
            age = str(age).upper()
            if int(age) < 10: age = '0' + age
            evo = str(evo).upper()
            kill = str(kill).upper()
            death = str(death).upper()
            money = str(money).upper()
            guild = f"{guild_region} | {g_region_name}"
            rank = rank.upper()
            # Get text canvas
            nb = ImageDraw.Draw(name_box)
            dgb = ImageDraw.Draw(degree_box)
            mnb = ImageDraw.Draw(money_box)
            hori = ImageDraw.Draw(horizontal)
            # Write/Alligning
            nb.text((name_box.width/4, 0), name.upper(), font=fnt_name, fill=co_name)
            dgb.text((name_box.width/2, 0), guild.capitalize(), font=fnt_degree, fill=co_guild)
            mnb.text((0, 0), money, font=fnt_money, fill=co_money)
            hori.text((3, 541), age, font=fnt_age, fill=co_age)
            hori.text((730 - hori.textsize(guild, font=fnt_guild)[0], 540), guild, font=fnt_guild, fill=co_guild)
            hori.text((730 - hori.textsize(rank, font=fnt_rank)[0], 555), rank, font=fnt_rank, fill=co_rank)
            hori.text((700 - hori.textsize(evo, font=fnt_evo)[0], 420), evo, font=fnt_evo, fill=co_evo)
            hori.text((525 , 384), death, font=fnt_kd, fill=co_death)
            hori.text((547 , 334), kill, font=fnt_kd, fill=co_kill)
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
        async def gafiking(ctx, in_img, char_img):
            # Info get
            age, evo, kill, death, money, name = await self.quefe(f"SELECT age, evo, kills, deaths, money, name FROM personal_info WHERE id='{ctx.message.author.id}';")
            guild_region, rank = await self.quefe(f"SELECT name, rank FROM pi_guild WHERE user_id='{ctx.message.author.id}';")
            g_region_name = await self.quefe(f"SELECT name FROM environ WHERE environ_code='{guild_region}';"); g_region_name = g_region_name[0]

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
            age = str(age).upper()
            if int(age) < 10: age = '0' + age
            evo = str(evo).upper()
            kill = str(kill).upper()
            death = str(death).upper()
            money = str(money).upper()
            guild = f"{guild_region} | {g_region_name}"
            rank = rank.upper()
            # Get text canvas
            nb = ImageDraw.Draw(name_box)
            dgb = ImageDraw.Draw(degree_box)
            mnb = ImageDraw.Draw(money_box)
            hori = ImageDraw.Draw(horizontal)
            # Write/Alligning
            nb.text((name_box.width/4, 0), name.upper(), font=fnt_name, fill=co_name)
            dgb.text((name_box.width/2, 0), guild.capitalize(), font=fnt_degree, fill=co_partner)
            mnb.text((0, 0), money, font=fnt_money, fill=co_money)
            hori.text((3, 541), age, font=fnt_age, fill=co_age)
            hori.text((730 - hori.textsize(guild, font=fnt_guild)[0], 540), guild, font=fnt_guild, fill=co_guild)
            hori.text((730 - hori.textsize(rank, font=fnt_rank)[0], 555), rank, font=fnt_rank, fill=co_rank)
            hori.text((700 - hori.textsize(evo, font=fnt_evo)[0], 420), evo, font=fnt_evo, fill=co_evo)
            hori.text((525 , 384), death, font=fnt_kd, fill=co_death)
            hori.text((547 , 334), kill, font=fnt_kd, fill=co_kill)
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

                out_img = await gafiking(ctx, a, char_img)
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
            output_buffer = await magiking(ctx)
            await self.client.send_file(ctx.message.channel ,fp=output_buffer, filename='profile.png')
        elif __mode == 'gif':
            output_buffer = await cogif(ctx)         
            reembed = discord.Embed(colour = discord.Colour(0x011C3A))
            reembed.set_image(url=output_buffer['link'])
            await self.client.say(embed=reembed)

    @commands.command(pass_context=True, aliases=['>outfit'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def wardrobe(self, ctx, *args):

        raw = list(args)

        try:
            if raw[0] == 'save':
                # Naming
                try: pname = raw[1]
                except IndexError: pname = 'Untitled'

                # Quantity limit check
                if await _cursor.execute(f"SELECT * FROM cosmetic_preset WHERE user_id='{ctx.message.author.id}' AND status='CURRENT';") >= 3: await self.client.say(f":warning: You cannot have more than three presets at a time, {ctx.message.author.id}")

                await _cursor.execute(f"INSERT INTO cosmetic_preset(user_id, name, status, avatar_id, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death) SELECT {ctx.message.author.id}, '{pname}', 'PRESET', avatar_id, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death FROM cosmetic_preset WHERE user_id='{ctx.message.author.id}' AND status='CURRENT';")

                await self.client.say(f":white_check_mark: Created preset **{pname}**. Use `-wardrobe presets` to check its *id*."); return

            elif raw[0] == 'delete':
                try:
                    if await _cursor.execute(f"DELETE FROM cosmetic_preset WHERE preset_id='{raw[1]}' AND user_id='{ctx.message.author.id}' AND status!='DEFAULT';") == 0:
                        await self.client.say(":warning: Preset's id not found!"); return
                # E: Preset's id not given
                except IndexError: await self.client.say(":warning: Please provide the id!"); return

                await self.client.say(f":white_check_mark: Preset id `{raw[1]}` was deleted."); return
            
            elif raw[0] == 'load':
                # GET preset
                try: 
                    if raw[1] == 'default':
                        avatar_id, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death = await self.quefe(f"SELECT avatar_id, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death FROM cosmetic_preset WHERE user_id='{ctx.message.author.id}' AND status='DEFAULT';")
                    else:
                        avatar_id, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death = await self.quefe(f"SELECT avatar_id, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death FROM cosmetic_preset WHERE user_id='{ctx.message.author.id}' AND preset_id='{raw[1]}';")
                # E: Preset's id not found
                except (IndexError, TypeError): await self.client.say(":warning: Preset's id not found!"); return

                # UPDATE current
                await _cursor.execute(f"UPDATE cosmetic_preset SET user_id='{ctx.message.author.id}', name='current of {ctx.message.author.name}', status='CURRENT', avatar_id='{avatar_id}', co_name='{co_name}', co_partner='{co_partner}', co_money='{co_money}', co_age='{co_age}', co_guild='{co_guild}', co_rank='{co_rank}', co_evo='{co_evo}', co_kill='{co_kill}', co_death='{co_death}' WHERE user_id='{ctx.message.author.id}' AND status='CURRENT';")
                await self.client.say(":white_check_mark: Preset's loaded!"); return
            
            elif raw[0] == 'presets':
                line = ""

                presets = await self.quefe(f"SELECT preset_id, name, avatar_id FROM cosmetic_preset WHERE user_id='{ctx.message.author.id}' AND status NOT IN ('DEFAULT', 'CURRENT');", type='all')

                if not presets: await self.client.say(f"You have not created any presets yet **{ctx.message.author.name}**"); return

                for preset in presets:
                    line = line + f"\n `{preset[0]}` :bust_in_silhouette: **{preset[1]}** |< {preset[2]} >|"

                await self.client.say(f":gear: Your list of presets, {ctx.message.author.mention}\n----------------------{line}"); return
            
            else:
                # COLOUR
                try:
                    if not re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', raw[1]): await self.client.say(":warning: Please use **hexa-decimal** colour code!\n:moyai: You can get them here --> https://htmlcolorcodes.com/"); return
                    
                    coattri = {'name': 'co_name', 'age': 'co_age', 'money': 'co_money', 'partner': 'co_partner', 'guild': 'co_guild', 'rank': 'co_rank', 'evo': 'co_evo', 'kills': 'co_kill', 'deaths': 'co_death'}
                    try:
                        await _cursor.execute(f"UPDATE cosmetic_preset SET {coattri[raw[0]]}='{raw[1]}' WHERE user_id='{ctx.message.author.id}' AND status='CURRENT';")
                        await self.client.say(f":white_check_mark: Attribute's colour was changed to **`{raw[1]}`**."); return
                    # E: Attributes not found
                    except KeyError: await self.client.say(f":moyai: Please use the following attributes: **`{'`** **`'.join(list(coattri.keys()))}`**"); return

                # AVATAR
                # E: Color not given
                except IndexError:
                    try: 
                        if await _cursor.execute(f"UPDATE cosmetic_preset SET avatar_id='{raw[0]}' WHERE user_id='{ctx.message.author.id}' AND status='CURRENT' AND EXISTS (SELECT * FROM pi_avatars WHERE user_id='{ctx.message.author.id}' AND avatar_id='{raw[0]}');") == 0:
                            await self.client.say(f":warning: You don't own this avatar, **{ctx.message.author.name}**!"); return
                        await self.client.say(f":white_check_mark: Changed to `{raw[0]}`"); return
                    except mysqlError.IntegrityError: await self.client.say(f":warning: Avatar not found!"); return

        # AVATARs
        # E: No avatar given
        except IndexError:
            avatars = await self.quefe(f"SELECT avatar_id FROM pi_avatars WHERE user_id='{ctx.message.author.id}';", type='all')
            k = [x[0] for x in avatars]
            await self.client.say(f":moyai: Your avatars: `{'` `'.join(k)}`"); return


# ============= ACTIVITIES ==================

    @commands.command(pass_context=True, aliases=['>work'])
    @commands.cooldown(1, 10, type=BucketType.user)
    async def avawork(self, ctx, *args):
        cmd_tag = 'work'
        if not await self.ava_scan(ctx.message, type='life_check'): return
        if not await self.__cd_check(ctx.message, cmd_tag, f"We haven't heard anything from **{ctx.message.author.name}**, yet."): return
        raw = ' '.join(args)

        try: 
            requirement, duration, reward, sta, jname = await self.quefe(f"SELECT requirement, duration, reward, sta, name FROM model_job WHERE job_code='{raw[0]}';")
            try:
                STA, money = await self.quefe(f"SELECT STA, money FROM personal_info WHERE EXISTS (SELECT * FROM pi_degrees WHERE user_id='{ctx.message.author.id}' AND degree='{requirement.split(' - ')}');")
                if STA < sta: await self.client.say(f"Grab something to *eat*, **{ctx.message.author.name}** <:fufu:508437298808094742> You can't do anything with such STA."); return

                await _cursor.execute(f"UPDATE personal_info SET STA={STA - sta}, money={money + reward} WHERE id='{ctx.message.author.id}'")
                await self.client.say(f"**{ctx.message.author.name}** has just assigned to be `{raw[0]}`|**{jname}** for **${reward}**, which will last `{int(duration/240)}` days. Farewell!")
            # E: Unpack on empty query, due to degree not found
            except ValueError: await self.client.say(f":warning: You need `{self.jobs_dict[raw][0]}` to apply for this job!"); return
        except IndexError: await self.client.say(":warning: Please choose a job!"); return
        # E: Unpack on empty query, due to job_code not found
        except ValueError: await self.client.say(":x: Job's code not found!"); return

        await self.client.loop.run_in_executor(None, partial(redio.set, f'{cmd_tag}{ctx.message.author.id}', 'working', ex=duration, nx=True))

    @commands.command(pass_context=True, aliases=['>works'])
    @commands.cooldown(1, 10, type=BucketType.user)
    async def avaworks(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        search_query = ''
        for search in args:
            raw = search.split('==')
            try:
                if search_query: search_query += "AND"
                else: search_query += "WHERE"; first = raw[0]
                if raw[0].lower() == 'requirement': search_query += f" requirement='{raw[1].capitalize()}' "; continue
                search_query += f" {raw[0]}>={raw[1]} "
            # E: Invalid search
            except (AttributeError, IndexError): pass
        
        if search_query: search_query += f" ORDER BY {first} ASC"

        try:
            job_list = await self.quefe(f"SELECT job_code, name, description, requirement, duration, reward, sta FROM model_job {search_query};", type='all')
            if not job_list: await self.client.say(":warning: No result..."); return
        # E: Invalid syntax 
        except mysqlError.ProgrammingError: await self.client.say(":warning: **Invalid syntax.** For filtering, please use `[keyword]==[value]`"); return 
        # E: Invalid syx
        except mysqlError.InternalError: await self.client.say(":warning: **Invalid keywors.** Please use `reward`, `duration`, `requirement`, `sta`"); return

        def makeembed(top, least, pages, currentpage):
            line = ''

            line = "**-------------------- oo --------------------**\n" 
            for pack in job_list[top:least]:
                job_code, name, description, requirement, duration, reward, sta = pack
                line = line + f"""`{job_code}` ∙ **{name.capitalize()}**\n*"{description}"*\n**${reward}** | `{duration}`**s** | STA-`{sta}` | **Require:** `{requirement.replace(' - ', '` `')}`\n\n"""
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
        if pages > 1: await attachreaction(msg)
        else: return

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
                break

    @commands.command(pass_context=True, aliases=['>edu'])
    @commands.cooldown(1, 10, type=BucketType.user)
    async def avaedu(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        cur_X, cur_Y = await self.quefe(f"SELECT cur_X, cur_Y FROM personal_info WHERE id='{ctx.message.author.id}';")
        if not await self.area_scan(ctx, cur_X, cur_Y): await self.client.say(":warning: Educating facilities are only available within **Peace Belt**!"); return

        cmd_tag = 'edu'
        degrees = ['elementary', 'middleschool', 'highschool', 'associate', 'bachelor', 'master', 'doctorate']
        major = ['astrophysic', 'biology', 'chemistry', 'georaphy', 'mathematics', 'physics', 'education', 'archaeology', 'history', 'humanities', 'linguistics', 'literature', 'philosophy', 'psychology', 'management', 'international_bussiness', 'elemology', 'electronics', 'robotics', 'engineering']
 
        if args:
            resp = args[0]
        else: await self.client.say(f":books: Welcome to **Ascending Sanctuary of Siegfields**. Please, take time and have a look.\n:books: **`{'` ➠ `'.join(degrees)}`**\n:moyai: Syntax: `-avaedu [degree]` "); return

        # Check if the previous course has been finished yet
        if not await self.__cd_check(ctx.message, cmd_tag, f":books: *Enlightening requires one's most persevere and patience.*"): return

        try:
            await self.client.say(f":bulb: ... and what major would you prefer?\n|| **`{'` · `'.join(major)}`**")
            resp2 = await self.client.wait_for_message(channel=ctx.message.channel, author=ctx.message.author, timeout=10)
            # Major check
            if resp2.content.lower() not in major: await self.client.say(f":warning: Invalid major!"); return

            price, INTT_require, INTT_reward, degree_require, duration = await self.quefe(f"SELECT price, INTT_require, INTT_reward, degree_require, duration FROM model_degree WHERE degree='{resp.lower()}';")
            degree_require = degree_require.split(' of ')

            # DEGREE (and MAJOR) check
            query = f"SELECT money, INTT FROM personal_info WHERE EXISTS (SELECT * FROM pi_degrees WHERE user_id='{ctx.message.author.id}' AND degree='{degree_require[0]}'"

            try:
                try: money, INTT = await self.quefe(query + f" AND major='{degree_require[1]}');")
                # E: No major required
                except IndexError: money, INTT = await self.quefe(query + ");")
            # E: Query return NONE
            except ValueError: await self.client.say(f":warning: Your application does not meet the degree/major requirements, **{ctx.message.author.name}**."); return

            # MONEY and INTT check
            if money < price: await self.client.say(f":warning: You need **${price}** to enroll this program!"); return
            if INTT < INTT_require: await self.client.say(f":warning: You need **{INTT_require}**`INT` to enroll this program!"); return
            
            await self.client.send_message(ctx.message.channel, f":books: Program for `{resp.capitalize()} of {resp2.content.capitalize()}` requires:\n|| **${price}**\n|| **{duration/7200} months** to achieve.\n:scroll: As a result, you'll receive **`{resp.capitalize()} of {resp2.content.capitalize()}`** and `{INTT_reward}` **INT**. \n```Do you wish to proceed? (Y/N)```")

            rep = await self.client.wait_for_message(channel=ctx.message.channel, author=ctx.message.author, timeout=15)
            try:
                if rep.content.lower() == 'y': 
                    # Initialize
                    try: await _cursor.execute(f"INSERT INTO pi_degrees VALUES ('{ctx.message.author.id}', '{resp.lower()}', '{resp2.content.lower()}');")
                    except AttributeError: await _cursor.execute(f"INSERT INTO pi_degrees VALUES ('{ctx.message.author.id}', '{resp.lower()}', NULL);")
                    await _cursor.execute(f"UPDATE personal_info SET INTT={INTT + INTT_reward}, STA=0, money={money - price} WHERE id='{ctx.message.author.id}';")
                    # Cooldown set
                    await self.client.send_message(ctx.message.channel, f":white_check_mark: **${price}** has been deducted from your account.")
                    await self.client.loop.run_in_executor(None, partial(redio.set, f'{cmd_tag}{ctx.message.author.id}', 'degreeing', ex=duration, nx=True))
                elif rep.content.lower() == 'n': await self.client.say(f"Assignment session of {ctx.message.author.mention} is closed."); return
                else: raise AttributeError
            # E: Time-out, or invalid reply
            except AttributeError: await self.client.say(f":warning: Assignment session of {ctx.message.author.mention} is closed."); return

        # E: No respond
        except AttributeError: await self.client.say(":books: May the Olds look upon you..."); return
        # E: Invalid degree
        except (ValueError, TypeError): await self.client.say(":warning: Invalid degree!"); return

    @commands.command(pass_context=True, aliases=['>medic'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def avamedic(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        cur_X, cur_Y, LP, MAX_LP, money = await self.quefe(f"SELECT cur_X, cur_Y, LP, MAX_LP, money FROM personal_info WHERE id='{ctx.message.author.id}'")

        if not await self.area_scan(ctx, cur_X, cur_Y): await self.client.say(":warning: Medical treatments are only available within **Peace Belt**!"); return

        reco = MAX_LP - LP
        if reco == 0: await self.client.say(f":warning: **{ctx.message.author.name}**, your current LP is at max!"); return

        reco_scale = reco//(MAX_LP/20)
        if reco_scale == 0: reco_scale = 1
        
        cost = int(reco*reco_scale)

        # Inform
        await self.client.say(f"<:healing_heart:508220588872171522> Dear {ctx.message.author.mention},\n------------\n· Your damaged scale: `{reco_scale}`\n· Your LP requested: `{reco}`\n· Price: `${reco_scale}/LP`\n· Cost: `${cost}`\n------------\nPlease type `confirm` within 10s to receive the treatment.")
        if not await self.client.wait_for_message(content='confirm', timeout=10, author=ctx.message.author, channel=ctx.message.channel): await self.client.say(":warning: Treatment is declined!"); return
        if money < cost: await self.client.say(":warning: Insufficient balance!"); return

        # Treat
        await _cursor.execute(f"UPDATE personal_info SET money={money - cost}, LP={MAX_LP}")
        await self.client.say(f"<:healing_heart:508220588872171522> **${cost}** has been deducted from your account, **{ctx.message.author.name}**!"); return
        
    @commands.command(pass_context=True, aliases=['>guild', '>g'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def avaguild(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        await self.ava_scan(ctx.message)
        raw = list(args)

        name, rank, total_quests = await self.quefe(f"SELECT name, rank, total_quests FROM pi_guild WHERE user_id='{ctx.message.author.id}';")

        try:
            if name == 'n/a' and raw[0] != 'join':
                await self.client.say(":warning: You haven't joined any guilds yet!"); return
        except IndexError: await self.client.say(":warning: You haven't joined any guilds yet!"); return

        current_place, money = await self.quefe(f"SELECT cur_PLACE, money FROM personal_info WHERE id='{ctx.message.author.id}'")

        try:
            if raw[0] == 'join':
                # Check if user's in the same guild
                if name == current_place:
                    await self.client.say(f":warning: You've already been in that guild, **{ctx.message.author.name}**!"); return
                # ... or in other guilds
                elif name != 'n/a':
                    cost = abs(2000* (int(name.split('.')[1]) - int(current_place.split('.')[1])))
                # ... jor just want to join
                else: cost = 0

                await self.client.say(f":scales: **G.U.I.L.D** of `{current_place} | {self.environ[current_place]['name']}` :scales:\n------------------------------------------------\nJoining will require **${cost}** as a deposit which will be returned when you leave guild if: \n· You don't have any bad records.\n· You're alive.\n· You leave the guild before joining others\n------------------------------------------------\n:bell: **Do you wish to proceed?** (key: `joining confirm` | timeout=20s)")
                resp = await self.client.wait_for_message(timeout=20, content='joining confirm', author=ctx.message.author, channel=ctx.message.channel)           

                # Money check
                if money < cost: await self.client.say(":warning: Insufficient balance!"); return

                if not resp: await self.client.say(":warning: Request timed out!"); return

                await _cursor.execute(f"UPDATE personal_info SET money={money - cost} WHERE id='{ctx.message.author.id}';")
                await _cursor.execute(f"UPDATE pi_guild SET name='{current_place}', deposit=deposit+{cost} WHERE user_id='{ctx.message.author.id}';")
                await self.client.say(f":european_castle: Welcome, {ctx.message.author.mention}, to our big family all over Pralayr :european_castle:\nYou are no longer a lonely, nameless adventurer, but a member of `{current_place} | {self.environ[current_place]['name']}` guild, a part of **G.U.I.L.D**'s league. Please, newcomer, make yourself at home <3"); return

            elif raw[0] == 'leave':
                name, deposit = await self.quefe(f"SELECT name, deposit FROM pi_guild WHERE user_id='{ctx.message.author.id}'")

                await self.client.say(f":bell: {ctx.message.author.mention}, leaving `{current_place}|{self.environ[current_place]['name']}` guild? (key: `leaving confirm` | timeout=5s)")
                resp = await self.client.wait_for_message(timeout=5, content='leaving confirm', author=ctx.message.author, channel=ctx.message.channel)
                
                if not resp: await self.client.say(":warning: Request timed out!"); return

                await _cursor.execute(f"UPDATE personal_info SET money=money+{deposit} WHERE id='{ctx.message.author.id}';")
                await _cursor.execute(f"UPDATE pi_guild SET name='n/a', deposit=0 WHERE user_id='{ctx.message.author.id}';")
                await self.client.say(f":white_check_mark: Left guild. Deposit of **${deposit}** has been returned"); return

            elif raw[0] == 'quest':
                try:
                    if raw[1] == 'take':
                        # If quest's id given, accept the quest
                        try:
                            sample = {'iron': 3, 'bronze': 4, 'silver': 5, 'gold': 6, 'adamantite': 8, 'mithryl': 10}
                            if await self.quefe(f"SELECT COUNT(user_id) FROM pi_quests WHERE user_id='{ctx.message.author.id}' AND stats='DONE'") >= sample[rank]: await self.client.say(f":warning: You cannot handle more than **{sample[rank]}** quests at a time")

                            region, quest_line = await self.quefe(f"SELECT region, quest_line FROM model_quest WHERE quest_code='{raw[2]}';")
                            # Region check
                            if region != current_place: await self.client(f":european_castle: Quest `{raw[2]}` can only be taken in `{region}`!"); return

                            await _cursor.execute(f"INSERT INTO pi_quests (quest_code, user_id, stats) VALUES ('{raw[2]}', '{ctx.message.author.id}', 'ONGOING')")
                            
                            await self.client.say(f":white_check_mark: {quest_line.capitalize} quest `{raw[2]}`|`{region}` accepted! Use `-avaquest` to check your progress."); return
                        # E: Quest's id not found
                        except TypeError: await self.client.say(":warning: Quest not found!"); return
                        # E: Quest's id not given (and current_quest is also empty)
                        except IndexError: await self.client.say(f":warning: You're not on any quests at the moment, **{ctx.message.author.mention}**!"); return

                    elif raw[1] == 'leave': 
                        region, quest_line = await self.quefe(f"SELECT region, quest_line FROM model_quest WHERE quest_code='{raw[2]}';")
                        # Region check
                        if region != current_place: await self.client(f":european_castle: Quest `{raw[2]}` can only be left in `{region}`!"); return

                        if await _cursor.execute(f"DELETE FROM pi_quests WHERE user_id='214128381762076672' AND quest_id={raw[0]} AND stats='ONGOING'") == 0: await self.client.say(f":warning: An error has occured while leaving quest `{raw[2]}`! Please mind that you can't leave a completed quest."); return
                        await self.client.say(f":white_check_mark: Left {quest_line} quest with id `{raw[2]}`, aka. `{raw[2]}`|`{region}`")
                        return

                    elif raw[1] == 'redeem':
                        # Check if the quest is ONGOING     ||      Get stuff too :>
                        try: quest_code, check_quantity, check_query, reward_quantity, reward_query, region = await self.quefe(f"SELECT quest_code, check_quantity, check_query, reward_quantity, reward_query, region FROM model_quest WHERE quest_code=(SELECT quest_code FROM pi_quests WHERE quest_id={raw[2]} AND user_id='{ctx.message.author.id}' AND stats='ONGOING');")
                        except TypeError: await self.client(":warning: An error has occurred! Please mind that you cannot redeem a completed quest, scammer... <:fufu:520602319323267082>")

                        # Region check
                        if current_place != region: await self.client(f":european_castle: Quest `{raw[2]}` can only be redeemed in `{region}`!"); return

                        # Paste user_id to the two queries
                        check_query = check_query.replace('user_id_here', ctx.meesage.author.id)
                        reward_query = reward_query.replace('user_id_here', ctx.message.author.id)

                        # Requirement check
                        if await _cursor.execute(check_query) != check_quantity: await self.client.say(":european_castle: Your quest is not fulfilled. Please check again!")
                        
                        # Reward
                        if await _cursor.execute(reward_query) != reward_quantity: self.client.say(f":warning: A BUG HAS HAPPENED!"); return
                        # Increase total_quests by 1
                        await _cursor.execute(f"UPDATE pi_guild SET total_quests+=1 WHERE user_id='{ctx.message.author.id}';")
                        # Remove current quest
                        await _cursor.execute(f"UPDATE pi_quests SET stats='DONE' WHERE user_id='{ctx.message.author.id}' AND quest_id={raw[2]};")
                        # Inform
                        await self.client.say(f":european_castle: Glad we can work well, {ctx.message.author.id}. May the Olds look upon you!")
                        # Ranking check
                        sample2 = {'iron': ['bronze', 155], 'bronze': ['silver', 310], 'silver': ['gold', 465], 'gold': ['adamantite', 620], 'adamantite': ['mithryl', 755], 'mithryl': ['n/a', 0]}
                        if await _cursor.execute(f"UPDATE pi_guild SET rank='{sample2[rank][0]}' WHERE user_id='{ctx.message.author.id}' AND total_quests>={sample2[rank][1]};") == 1:
                            await self.client.say(f":beginner: Congrats, {ctx.message.author.mention}! You've been promoted to **{sample2[rank][0].upper()}**!")                         

                except IndexError:
                    bundle = await self.quefe(f"SELECT quest_code, quest_id FROM pi_quests WHERE user_id='{ctx.message.author.id}' AND stats='ONGOING';", type='all')
                    # ONGOING quest check
                    if not bundle: await self.client.say(f":european_castle: You have currently no active quest, **{ctx.message.author.name}**! Try get some and prove yourself."); return
                    for pack in bundle:
                        bundle2 = await self.quefe(f"SELECT requester, description, quest_line FROM model_quest WHERE quest_code='{pack[0]}';", type='all')

                    line = f"**ACTIVE QUEST:** {len(bundle)}\n-------------------------------------"
                    for pack, pack2 in zip(bundle, bundle2):
                        line += f"\n:scroll: `{pack[1]}` · `{pack[0]}`|**{pack2[2].capitalize()} quest** of **{pack2[0]}**\n**||** *{pack2[1]}*\n"

                    await self.client.say(line); return                

            elif raw[0] == 'quests':
                bundle = await self.quefe(f"SELECT quest_code, requester, description, quest_line FROM model_quest WHERE region='{current_place}';", type='all')
                completed_bundle = await self.quefe(f"SELECT quest_code FROM pi_quests WHERE user_id='{ctx.message.author.id}' AND stats='DONE' AND EXISTS (SELECT * FROM model_quest WHERE model_quest.quest_code=pi_quests.quest_code AND region='{current_place}');")
                # None check
                if not completed_bundle: completed_bundle = []

                def makeembed(top, least, pages, currentpage):
                    line = ''

                    line = f"**······················· -- ·······················**\n" 
                    for pack in bundle[top:least]:
                        if pack[0] in completed_bundle: marker = ':page_with_curl:'
                        else: marker = ':scroll:'
                        line += f"\n{marker} · `{pack[0]}` · **{pack[3].capitalize()} quest** of **{pack[1]}**\n**||** *{pack[2]}*\n"

                    reembed = discord.Embed(title = f"**`{self.environ[current_place]['name']}`** · `Total` {len(bundle)} · `Done` {len(completed_bundle)}", colour = discord.Colour(0x011C3A), description=line)
                    reembed.set_footer(text=f"Page {currentpage} of {pages}")
                    return reembed
                    #else:
                    #    await client.say("*Nothing but dust here...*")
                
                async def attachreaction(msg):
                    await self.client.add_reaction(msg, "\U00002b05")    #Left
                    await self.client.add_reaction(msg, "\U000027a1")    #Right

                pages = len(bundle)//5
                if len(bundle)%10 != 0: pages += 1
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
        except TypeError: await self.client.say(f":european_castle: **`{ctx.message.author.name}`'s G.U.I.L.D card** :european_castle: \n------------------------------------------------\n**`Guild`** · `{name}`|**{self.environ[name]['name']}`\n**`Rank`** · {rank}\n**`Total quests done`** · {total_quests}"); return

    @commands.command(pass_context=True, aliases=['>evolve'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def avaevolve(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        raw = list(args)
        evo_dict = {'lp': f"UPDATE personal_info SET MAX_LP=MAX_LP+ROUND(MAX_LP/100*5), ECO=EVO+1 WHERE id='{ctx.message.author.id}' AND perks>0;",
                    'sta': f"UPDATE personal_info SET MAX_STA=MAX_STA+ROUND(MAX_STA/100*10), ECO=EVO+1 WHERE id='{ctx.message.author.id}' AND perks>0;",
                    'str': f"UPDATE personal_info SET STR=STR+0.1, ECO=EVO+1 WHERE id='{ctx.message.author.id}' AND perks>0;",
                    'int': f"UPDATE personal_info SET INTT=INTT+0.1, ECO=EVO+1 WHERE id='{ctx.message.author.id}' AND perks>0;",
                    'flame': f"UPDATE personal_info SET au_FLAME=au_FLAME+0.05, ECO=EVO+1 WHERE id='{ctx.message.author.id}' AND perks>0;",
                    'ice': f"UPDATE personal_info SET au_ICE=au_ICE+0.05, ECO=EVO+1 WHERE id='{ctx.message.author.id}' AND perks>0;",
                    'holy': f"UPDATE personal_info SET au_HOLY=au_HOLY+0.05, ECO=EVO+1 WHERE id='{ctx.message.author.id}' AND perks>0;",
                    'dark': f"UPDATE personal_info SET au_DARK=au_DARK+0.05, ECO=EVO+1 WHERE id='{ctx.message.author.id}' AND perks>0;",
                    'charm': f"UPDATE personal_info SET charm=charm+1 WHERE id='{ctx.message.author.id}' AND preks>0;"}
        try:
            if await _cursor.execute(evo_dict[raw[0].lower()]) == 0: await self.client.say(":warning: Not enough perks!"); return

        # E: Attributes not found
        except KeyError: await self.client.say(":warning: Invalid attribute!"); return

        # E: Attri not given
        except TypeError: await self.client.say(f"<:zapp:524893958115950603> Perks can be spent on your attributes:\n________________________\n`LP` · +5% MAX_LP **||** `STA` · +10% MAX_STA **||** `STR` · +0.1 STR **||** `INT` · +0.1 INT\n `FLAME` · +0.05 aura **||** `ICE` · +0.05 aura **||** `HOLY` · +0.05 aura **||** `DARK` · +0.05 aura\n `CHARM` · +0.01 CHARM \n\n________________________\n**Your perks:** {self.ava_dict[ctx.message.author.id]['perks']}"); return

        await self.client.say("<:zapp:524893958115950603> Done. You can use `-ava` to recheck.")

    @commands.command(pass_context=True, aliases=['>infuse'])
    @commands.cooldown(1, 60, type=BucketType.user)
    async def avainfuse(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        raw = list(args)

        try:
            # Item's info get
            try:
                w_name, w_evo = await self.quefe(f"SELECT name, evo FROM pi_inventory WHERE user_id='{ctx.message.author.id}' AND item_id='{raw[0]}';")
                t_w_quantity, t_w_infuse_query, t_w_evo = await self.quefe(f"SELECT quantity, infuse_query, evo FROM pi_inventory WHERE user_id='{ctx.message.author.id}' AND item_id='{raw[1]}';")
            # E: Item's not found
            except TypeError: await self.client.say(":warning: Item's not found!"); return

            # Quantity check
            quantity = 1
            if w_evo != t_w_evo:
                if w_evo > t_w_quantity: await self.client.say(f":warning: You need a quantity of **{w_evo}** to infuse the item.") ; return
                quantity = w_evo

            # Get degree check sub-query
            try:
                inflv_dict = {10: ('elementary', 'elemology'), 
                            15: ('middleschool', 'elemology'),
                            20: ('highschool', 'elemology'),
                            25: ('associate', 'elemology'), 
                            30: ('bachelor', 'elemology'),
                            35: ('master', 'elemology'),
                            40: ('doctorate', 'elemology')}

                d_check = f"AND EXISTS (SELECT * FROM pi_degrees WHERE user_id='{ctx.message.author.id}' AND degree='{inflv_dict[w_evo][0]}' AND major='{inflv_dict[w_evo][1]}');"
            except KeyError: d_check = ''

            # Preparing
            t_w_infuse_query = t_w_infuse_query.replace('user_id_here', ctx.message.author.id).replace('item_id_here', raw[0])

            # INFUSE
            if await _cursor.execute(f"{t_w_infuse_query} {d_check};") == 0: await self.client.say(f":warning: You cannot infuse evo-`{w_evo}` item with your current status."); return

            # Remove
            if quantity == t_w_quantity: await _cursor.execute(f"DELETE FROM pi_inventory WHERE user_id='{ctx.message.author.id}' AND item_id='{raw[1]}';")
            else: await _cursor.execute(f"UPDATE pi_inventory SET quantity=quantity-{quantity} WHERE user_id='{ctx.message.author.id}' AND item_id='{raw[1]}';")

            # Inform :>
            await self.client.say(f":white_check_mark: Infusion with `{raw[0]}`|**{w_name}** was a success. The other item has been destroyed."); return

        # E: Not enough args
        except IndexError: await self.client.say(":warning: What? You think you can infuse thing out of nowhere?"); return

    @commands.command(pass_context=True, aliases=['>merge'])
    @commands.cooldown(1, 60, type=BucketType.user)
    async def avamerge(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        cmd_tag = 'merge'
        raw = list(args)

        # Check if the previous course has been finished yet
        if not await self.__cd_check(ctx.message, cmd_tag, f":books: *Enlightening requires one's most persevere and patience.*"): return

        try:
            # Item's info get
            try:
                w_name, w_evo, w_weight, w_defend, w_multiplier, w_str, w_intt, w_sta, w_speed, w_acc_randomness, w_acc_range, w_r_min, w_r_max, w_firing_rate, w_dmg, w_stealth = await self.quefe(f"SELECT name, evo, weight, defend, multiplier, str, intt, sta, speed, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth FROM pi_inventory WHERE user_id='{ctx.message.author.id}' AND item_id='{raw[0]}';")
                t_w_evo, t_w_weight, t_w_defend, t_w_multiplier, t_w_str, t_w_intt, t_w_sta, t_w_speed, t_w_acc_randomness, t_w_acc_range, t_w_r_min, t_w_r_max, t_w_firing_rate, t_w_dmg, t_w_stealth = await self.quefe(f"SELECT evo, weight, defend, multiplier, str, intt, sta, speed, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth FROM pi_inventory WHERE user_id='{ctx.message.author.id}' AND item_id='{raw[2]}';")
            # E: Item's not found
            except TypeError: await self.client.say(":warning: Item's not found!"); return

            # Degrees
            degrees = await self.quefe(f"SELECT degree FROM pi_degrees WHERE user_id='{ctx.message.author.id}' AND major='engineering';"); degrees = set(degrees)

            # Price
            price = abs(w_evo - t_w_evo)*len(degrees)*1000
            await self.client.say(f":tools: Merching these two items will cost you **${price}**.\n:bell: Proceed? (`merging confirmation`)")
            await self.client.wait_for_message(timeout=20, author=ctx.message.author, channel=ctx.message.channel, content='merging confirmation')

            # Deduct money
            if await _cursor.execute(f"UPDATE personal_info SET money=money-{price} WHERE id'{ctx.message.author.id}' AND money >= {price};") == 0:
                await self.client.say(":warning: Insufficient balance!"); return

            # MERGE
            W_weight = random.choice(range(w_weight + t_w_weight))
            W_defend = random.choice(range(w_defend + t_w_defend))
            W_multiplier = random.choice(range(w_multiplier + t_w_multiplier))
            W_str = random.choice(range(w_str, t_w_str))
            W_intt = random.choice(range(w_intt + t_w_intt))
            W_sta = random.choice(range(w_sta + t_w_sta))
            W_speed = random.choice(range(w_speed + t_w_speed))
            W_acc_randomness = random.choice(range(w_acc_randomness + t_w_acc_randomness))
            W_acc_range = random.choice(range(w_acc_range + t_w_acc_range))
            W_r_min = random.choice(range(w_r_min + t_w_r_min))
            W_r_max = random.choice(range(w_r_max + t_w_r_max))
            W_firing_rate = random.choice(range(w_firing_rate + t_w_firing_rate))
            W_dmg = random.choice(range(w_dmg + t_w_dmg))
            W_stealth = random.choice(range(w_stealth + t_w_stealth))

            # Insert
            await _cursor.execute(f"UPDATE pi_inventory SET weight={W_weight}, defend={W_defend}, multiplier={W_multiplier}, str={W_str}, intt={W_intt}, sta={W_sta}, speed={W_speed}, accuracy_randomness={W_acc_randomness}, accuracy_range={W_acc_range}, range_min={W_r_min}, range_max={W_r_max}, firing_rate={W_firing_rate}, dmg={W_dmg}, stealth={W_stealth} WHERE user_id='{ctx.message.author.id}' AND item_id='{raw[0]}';")
            await _cursor.execute(f"UPDATE pi_inventory SET weight={W_weight}, defend={W_defend}, multiplier={W_multiplier}, str={W_str}, intt={W_intt}, sta={W_sta}, speed={W_speed}, accuracy_randomness={W_acc_randomness}, accuracy_range={W_acc_range}, range_min={W_r_min}, range_max={W_r_max}, firing_rate={W_firing_rate}, dmg={W_dmg}, stealth={W_stealth} WHERE user_id='{ctx.message.author.id}' AND item_id='{raw[1]}';")

            # Inform :>
            await self.client.say(f":white_check_mark: Merged `{raw[0]}`|**{w_name}** with `{raw[0]}`|**{w_name}**!")
            await self.client.loop.run_in_executor(None, partial(redio.set, f'{cmd_tag}{ctx.message.author.id}', 'merging', ex=3600, nx=True))

        # E: Not enough args
        except IndexError: await self.client.say(":warning: How could you even merge something with its own?!"); return

    @commands.command(pass_context=True, aliases=['>hunt'])
    @commands.cooldown(1, 10, type=BucketType.user)
    async def avahunt(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        try: end_point, status, final_rq, final_rw = await self.quefe(f"SELECT end_point, status, reward_query, rewards FROM pi_hunt WHERE user_id='{ctx.message.author.id}';")
        except TypeError: status = 'DONE'

        if status == 'DONE':
            raw = list(args)

            STR, INTT, STA = await self.quefe(f"SELECT STR, INTT, STA FROM personal_info WHERE id='{ctx.message.author.id}';")

            # Get hunt limitation
            try: 
                limit = int(raw[0])
                if limit >= STA: limit = STA - 1
            except (IndexError, ValueError): limit = STA - 1

            if limit <= 0: await self.client.say(f"Go *get some food*, **{ctx.message.author.name}** <:fufu:508437298808094742> We cannot start a hunt with you exhausted like that."); return

            # Get animals based on INTT
            anis = await self.quefe(f"SELECT ani_code, str, sta, aggro, rewards, reward_query FROM model_animal WHERE intt<={INTT};", type='all')

            rewards = ''; reward_query = ''
            while STA > limit:
                # Get target
                target = random.choice(anis)

                # Decrease STA
                STA -= target[2]

                # Rate calc
                rate = STR - target[1]
                if rate < 0: rate = target[3]//rate
                elif rate > 0: rate = round(target[3]*rate)
                elif rate == 0: rate = 1

                # Decide if session is success
                if random.choice(range(rate)) != 0: continue

                rewards = rewards + f"\n· **{target[4]}**"
                reward_query = reward_query + f" {target[5]}"

            # Duration calc     ||      End_point calc
            duration = 60*limit//STR
            end_point = datetime.now() + timedelta(seconds=duration)
            end_point = end_point.strftime('%Y-%m-%d %H:%M:%S')

            # Insert
            if await _cursor.execute(f"UPDATE pi_hunt SET status='ONGOING', end_point='{end_point}', reward_query='{reward_query}', rewards='{rewards}' WHERE user_id='{ctx.message.author.id}';") == 0:
                await _cursor.execute(f"INSERT INTO pi_hunt VALUES ('{ctx.message.author.id}', '{end_point}', 'ONGOING', '{rewards}', '{reward_query}');")
            await _cursor.execute(f"UPDATE personal_info SET STA=STA-{limit} WHERE id='{ctx.message.author.id}';")
            await self.client.say(f":cowboy: Hang tight, {ctx.message.author.name}! The hunt will end at **`{end_point}`**."); return

        else:

            # Two points comparison
            delta = relativedelta(end_point, datetime.now())
            if datetime.now() < end_point: await self.client.say(f":cowboy: Not yet, {ctx.message.author.name}! Please wait **`{delta.hours}:{delta.minutes}:{delta.seconds}`**"); return

            # Rewarding
            if final_rq: 
                await _cursor.execute(final_rq)
            await _cursor.execute(f"UPDATE pi_hunt SET status='DONE' WHERE user_id='{ctx.message.author.id}';")
            await self.client.say(f":cowboy: Congrats, **{ctx.message.author.name}**. You've finished your hunt!{final_rw}"); return





# ============= COMMERCIAL ==================
# <!> CONCEPTS 
# <dir> acts as an id/ (type:list) used to look up the self.data.item   (aka. address)
# a <dir> (type:list) contains these info, respectively: [data_class][item_class][category][obj's id] e.g. item.arsenal.pistol.1
# Main weapon is a inventory <dir>      ||      ['item'][]

    @commands.command(pass_context=True, aliases=['>shop'])
    @commands.cooldown(1, 5, type=BucketType.user)    
    async def avashop(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        cur_PLACE, cur_X, cur_Y = await self.quefe(f"SELECT cur_PLACE, cur_X, cur_Y FROM personal_info WHERE id='{ctx.message.author.id}';")
        if not await self.area_scan(ctx, cur_X, cur_Y): await self.client.say(":warning: Shops are only available within **Peace Belt**!"); return

        # INSPECT ===============
        raw = list(args)
        try:
            # Get goods
            goods, environ_name = await self.quefe(f"SELECT goods, name FROM environ WHERE environ_code='{cur_PLACE}';")
            goods = goods.replace(' - ', "', '")
            # Get info
            try: 
                item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, aura, illulink, price = await self.quefe(f"""SELECT item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, aura, illulink, price FROM model_item WHERE '{raw[0]}' IN ('{goods}') AND  item_code='{raw[0]}';""")

                # Pointer
                if 'magic' in tags: pointer = ':crystal_ball:'
                else: pointer = '<:gun_pistol:508213644375621632>'
                # Aura icon
                aui = {'FLAME': 'https://imgur.com/3UnIPir.png', 'ICE': 'https://imgur.com/7HsDWfj.png', 'HOLY': 'https://imgur.com/lA1qfnf.png', 'DARK': 'https://imgur.com/yEksklA.png'}

                line = f""":scroll: **`『Weight』` ·** {weight} ⠀ ⠀:scroll: **`『Price』` ·** {price}\n\n```"{description}"```\n"""
                
                reembed = discord.Embed(title=f"`{item_code}`|**{' '.join([x for x in name.upper()])}**", colour = discord.Colour(0x011C3A), description=line)
                reembed.add_field(name=":scroll: Basic Status <:broadsword:508214667416698882>", value=f"**`『STR』` ·** {str}\n**`『INT』` ·** {intt}\n**`『STA』` ·** {sta}\n**`『MULTIPLIER』` ·** {multiplier}\n**`『DEFEND』` ·** {defend}\n**`『SPEED』` ·** {speed}", inline=True)

                try: acc_per = 10//accuracy_randomness
                except ZeroDivisionError: acc_per = 0
                reembed.add_field(name=f":scroll: Projector Status {pointer}", value=f"**`『RANGE』` ·** {range_min} - {range_max}m\n**`『STEALTH』` ·** {stealth}\n**`『FIRING-RATE』` ·** {firing_rate}\n**`『ACCURACY』` ·** {acc_per}%/{accuracy_range}m\n**-------------------**\n**`『ROUND』` ·** {round} \n**`『DMG』` ·** {dmg}", inline=True)

                reembed.set_thumbnail(url=aui[aura])
                if illulink != 'n/a': reembed.set_image(url=illulink)

                await self.client.say(embed=reembed); return
            # Tags given, instead of item_code
            except TypeError: pass
        # E: No args given
        except IndexError: pass

        # SEARCH =================
        lk_query = ''; sublk_price = ''; sublk_tag = ''
        for lkkey in raw:
            if not lk_query: lk_query = 'AND'
            # lkkey is PRICE
            try: 
                if not sublk_price: sublk_price = sublk_price + f" price<={int(lkkey)}"
                else: sublk_price = sublk_price + f" OR price={int(lkkey)}"
            # lkkey is TAG
            except ValueError:
                if lkkey == 'consumable': lkkey = f" {lkkey}"
                if not sublk_tag: sublk_tag = sublk_tag + f" tags LIKE '%{lkkey}%'"
                else: sublk_tag = sublk_tag + f" AND '%{lkkey}%'"

        if sublk_price: 
            if sublk_tag: lk_query = lk_query + f" ({sublk_price}) AND {sublk_tag}"
            else: lk_query = lk_query + f" ({sublk_price})"
        elif not sublk_price: lk_query = lk_query + f" {sublk_tag}"

        # BROWSE =================
        async def browse():
            items = await self.quefe(f"""SELECT item_code, name, description, tags, weight, quantity, price, aura FROM model_item WHERE item_code IN ('{goods}') {lk_query};""", type='all')

            if not items: await self.client.say(f":x: No result..."); return

            def makeembed(top, least, pages, currentpage):

                line = "**------------------------------ oo ------------------------------**\n" 

                for item in items[top:least]:
                    if 'melee' in item[3]:
                        icon = '<:broadsword:508214667416698882>'
                        #line = line + f""" `{item_code}` <:broadsword:508214667416698882> **{items[item_code].name}** | *"{items[item_code].description}"*\n|| `『Multiplier』{items[item_code].multiplier}` · `『Speed』{items[item_code].speed}` · `『STA』{items[item_code].sta}` \n|| **`Required`** STR-{items[item_code].str}\n|| **`Price`** ${items[item_code].price}\n++ `{'` `'.join(items[item_code].tags)}`\n\n"""
                    elif 'range_weapon' in item[3]:
                        icon = '<:gun_pistol:508213644375621632>'
                        #line = line + f""" `{item_code}` <:gun_pistol:508213644375621632> **{items[item_code].name}** | *"{items[item_code].description}"*\n|| `『Range』{items[item_code].range[0]}m - {items[item_code].range[1]}m`\n|| `『Accuracy』1:{items[item_code].accuracy[0]}/{items[item_code].accuracy[1]}m` · `『firing_rate』{items[item_code].firing_rate}` · `『stealth』{items[item_code].stealth}`\n|| **`Required`** STR-{items[item_code].str}/shot · STA-{items[item_code].sta}\n|| **`Price`**${items[item_code].price}\n++ `{'` `'.join(items[item_code].tags)}`\n\n"""
                    elif 'ammunition' in item[3]:
                        icon = '<:shotgun_slug:508217929532440586>'
                        #line = line + f""" `{item_code}` <:shotgun_slug:508217929532440586> **{items[item_code].name}** | *"{items[item_code].description}"*\n|| `『Damage』{items[item_code].dmg}` · `『Speed』{items[item_code].speed}`\n|| **`Price`** ${items[item_code].price}\n++ `{'` `'.join(items[item_code].tags)}`\n\n"""
                    elif 'supply' in item[3]:
                        icon = ':small_orange_diamond:'
                        #line = line + f""" `{item_code}` :small_orange_diamond: **{items[item_code].name}** \n|| *"{items[item_code].description}"*\n|| **`Price`** ${items[item_code].price}\n++ `{'` `'.join(items[item_code].tags)}`\n\n"""
                    line = line + f""" `{item[0]}` {icon} `{item[7]}`|**{item[1]}**\n|| *"{item[2]}"*\n|| `『Weight』{item[4]}` · **`Price`**`${item[6]}/{item[5]}`\n++ `{item[3].replace(' - ', '` `')}`\n\n"""
                        
                line = line + "**------------------------------ oo ------------------------------**" 

                reembed = discord.Embed(title = f":shopping_cart: SIEGFIELD's Market of `{cur_PLACE}|{environ_name}`", colour = discord.Colour(0x011C3A), description=line)
                reembed.set_footer(text=f"Total: {len(items)} | Page {currentpage} of {pages}")
                
                if line == "**------------------------------ oo ------------------------------**\n**------------------------------ oo ------------------------------**": return False
                else: return reembed
                #else:
                #    await client.say("*Nothing but dust here...*")
            
            async def attachreaction(msg):
                await self.client.add_reaction(msg, "\U000023ee")    #Top-left
                await self.client.add_reaction(msg, "\U00002b05")    #Left
                await self.client.add_reaction(msg, "\U000027a1")    #Right
                await self.client.add_reaction(msg, "\U000023ed")    #Top-right

            pages = int(len(items)/5)
            if len(items)%5 != 0: pages += 1
            currentpage = 1
            myembed = makeembed(0, 5, pages, currentpage)

            msg = await self.client.say(embed=myembed)
            await attachreaction(msg)

            while True:
                try:    
                    reaction, user = await self.client.wait_for_reaction(message=msg, timeout=15)
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
                    break

        await browse()

    @commands.command(pass_context=True, aliases=['>buy'])
    @commands.cooldown(1, 5, type=BucketType.user)    
    async def avabuy(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        cur_X, cur_Y, money, cur_PLACE = await self.quefe(f"SELECT cur_X, cur_Y, money, cur_PLACE FROM personal_info WHERE id='{ctx.message.author.id}';")

        if not await self.area_scan(ctx, cur_X, cur_Y): await self.client.say(":warning: You can only buy stuff within **Peace Belt**!"); return
        #await self.client.loop.run_in_executor(None, partial(redio.set, f'{cmd_tag}{ctx.message.author.id}', 'working', ex=duration, nx=True))

        raw = list(args); quantity = 1

        try: item_code = raw[0]
        except IndexError: await self.client.say(f":warning: Please provide item's code, **{ctx.message.author.name}**"); return

        try: 
            quantity = int(raw[1])

            # SCAM :)
            if quantity <= 0: await self.client.say("**Heyyyyyyyyy scammer-!**"); return

        # E: Quantity not given, or invalidly given
        except (IndexError, TypeError): pass
        
        # Get goods
        goods = await self.quefe(f"SELECT goods FROM environ WHERE environ_code='{cur_PLACE}';")

        # GET ITEM INFO
        try:
            name, tags, i_price, i_quantity = await self.quefe(f"""SELECT name, tags, price, quantity FROM model_item WHERE item_code='{item_code}' AND item_code IN ('{goods[0].replace(' - ', "', '")}');""")
            i_tags = tags.split(' - ')
        # E: Item code not found
        except TypeError: await self.client.say(":warning: Item_code/Item_id not found!"); return

        # TWO TYPES of obj: Serializable-obj and Unserializable obj
        # Validation
        #if isinstance(self.data['item'][item_code], ingredient): await self.client.say(f":warning: You cannot use this command to obtain the given item, {ctx.message.author.id}. Use `-trade` instead"); return

        # Money check
        if i_price*quantity > money: await self.client.say(":warning: Insufficience balance!"); return

        # Deduct money
        await _cursor.execute(f"UPDATE personal_info SET money=money-{i_price*quantity} WHERE id='{ctx.message.author.id}';")

        # Get the real quantity (according to the model_item's quantity)
        quantity = quantity*i_quantity

        # Greeting, of course :)
        await self.client.say(f":white_check_mark: `{quantity}` item **{name}** is successfully added to your inventory! Thank you for shoping!")

        # CONSUMABLE
        if 'consumable' in i_tags:
            # Create item in inventory. Ignore the given quantity please :>
            await _cursor.execute(f"INSERT INTO pi_inventory SELECT 0, '{ctx.message.author.id}', item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, infuse_query, quantity, price, dmg, stealth, evo, aura, illulink FROM model_item WHERE item_code='{item_code}';")
            # (MODEL FOR QUERY RECORD-TRANSFERING) ------- await _cursor.execute(f"INSERT INTO pi_inventory SELECT 0, {ctx.message.author.id}, item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, quantity, price, dmg, stealth FROM model_item WHERE item_code='{item_code}';")

        # INCONSUMABLE
        else:
            # Increase item_code's quantity
            if await _cursor.execute(f"UPDATE pi_inventory SET quantity=quantity+{quantity} WHERE user_id='{ctx.message.author.id}' AND item_code='{item_code}';") == 0:
                # E: item_code did not exist. Create one, with given quantity
                await _cursor.execute(f"INSERT INTO pi_inventory SELECT 0, '{ctx.message.author.id}', item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, infuse_query, {quantity}, price, dmg, stealth, evo, aura, illulink FROM model_item WHERE item_code='{item_code}';")

    @commands.command(pass_context=True, aliases=['>i'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def avainventory(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        cur_PLACE  = await self.quefe(f"SELECT cur_PLACE FROM personal_info WHERE id='{ctx.message.author.id}';")
        cur_PLACE = cur_PLACE[0]

        # INSPECT ===============
        raw = list(args)
        try:
            # Get info
            try: 
                item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, evo, aura, illulink, price = await self.quefe(f"""SELECT item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, evo, aura, illulink, price FROM pi_inventory WHERE item_id='{raw[0]}';""")
                if evo != 0: evo_plus = f"+{evo}"
                else: evo_plus = ''

                # Pointer
                if 'magic' in tags: pointer = ':crystal_ball:'
                else: pointer = '<:gun_pistol:508213644375621632>'
                # Aura icon
                aui = {'FLAME': 'https://imgur.com/3UnIPir.png', 'ICE': 'https://imgur.com/7HsDWfj.png', 'HOLY': 'https://imgur.com/lA1qfnf.png', 'DARK': 'https://imgur.com/yEksklA.png'}

                line = f""":scroll: **`『Weight』` ·** {weight} ⠀ ⠀:scroll: **`『Price』` ·** {price}\n```"{description}"```\n"""
                
                reembed = discord.Embed(title=f"`{item_code}`|**{' '.join([x for x in name.upper()])}** {evo_plus}", colour = discord.Colour(0x011C3A), description=line)
                reembed.add_field(name=":scroll: Basic Status <:broadsword:508214667416698882>", value=f"**`『STR』` ·** {str}\n**`『INT』` ·** {intt}\n**`『STA』` ·** {sta}\n**`『MULTIPLIER』` ·** {multiplier}\n**`『DEFEND』` ·** {defend}\n**`『SPEED』` ·** {speed}", inline=True)

                try: acc_per = 10//accuracy_randomness
                except ZeroDivisionError: acc_per = 0
                reembed.add_field(name=f":scroll: Projector Status {pointer}", value=f"**`『RANGE』` ·** {range_min} - {range_max}m\n**`『STEALTH』` ·** {stealth}\n**`『FIRING-RATE』` ·** {firing_rate}\n**`『ACCURACY』` ·** {acc_per}%/{accuracy_range}m\n**-------------------**\n**`『ROUND』` ·** {round} \n**`『DMG』` ·** {dmg}", inline=True)

                reembed.set_thumbnail(url=aui[aura])
                if illulink != 'n/a': reembed.set_image(url=illulink)

                await self.client.say(embed=reembed); return
            # Tags given, instead of item_code
            except TypeError: pass
        # E: No args given
        except IndexError: pass

        # SEARCH =================
        lk_query = ''; sublk_price = ''; sublk_tag = ''
        for lkkey in raw:
            if not lk_query: lk_query = 'AND'
            # lkkey is PRICE
            try: 
                if not sublk_price: sublk_price = sublk_price + f" price<={int(lkkey)}"
                else: sublk_price = sublk_price + f" OR price={int(lkkey)}"
            # lkkey is TAG
            except ValueError:
                if lkkey == 'consumable': lkkey = f" {lkkey}"
                if not sublk_tag: sublk_tag = sublk_tag + f" tags LIKE '%{lkkey}%'"
                else: sublk_tag = sublk_tag + f" AND '%{lkkey}%'"

        if sublk_price: 
            if sublk_tag: lk_query = lk_query + f" ({sublk_price}) AND {sublk_tag}"
            else: lk_query = lk_query + f" ({sublk_price})"
        elif not sublk_price: lk_query = lk_query + f" {sublk_tag}"

        async def browse():
            items = await self.quefe(f"""SELECT item_id, item_code, name, description, tags, weight, quantity, price, aura FROM pi_inventory WHERE user_id='{ctx.message.author.id}' {lk_query};""", type='all')

            if not items: await self.client.say(f":x: No result..."); return

            def makeembed(top, least, pages, currentpage):
                line = ''

                line = "**------------------------------ oo ------------------------------**\n" 

                for item in items:
                    if 'melee' in item[4]:
                        icon = '<:broadsword:508214667416698882>'
                        #line = line + f""" `{item_code}` <:broadsword:508214667416698882> **{items[item_code]['obj'].name}** | *"{items[item_code]['obj'].description}"* \n|| **`Required`** STR-{items[item_code]['obj'].str}\n|| **`Price`** ${items[item_code]['obj'].price}\n++ `{'` `'.join(items[item_code]['obj'].tags)}`\n\n"""
                    elif 'range_weapon' in item[4]:
                        icon = '<:gun_pistol:508213644375621632>'
                        #line = line + f""" `{item_code}` <:gun_pistol:508213644375621632> **{items[item_code]['obj'].name}** | *"{items[item_code]['obj'].description}"*\n|| **`Required`** **STR**-{items[item_code]['obj'].str}/shot · **STA**-{items[item_code]['obj'].sta}\n|| **`Price`**${items[item_code]['obj'].price}\n++ `{'` `'.join(items[item_code]['obj'].tags)}` \n\n"""
                    elif 'ammunition' in item[4]:
                        icon = '<:shotgun_slug:508217929532440586>'
                        #line = line + f""" `{item_code}` <:shotgun_slug:508217929532440586> **{self.data['item'][item_code].name}** | *"{self.data['item'][item_code].description}"* \n|| **`Price`** ${self.data['item'][item_code].price}\n|| **`Quantity`** {items[item_code]}\n++ `{'` `'.join(self.data['item'][item_code].tags)}`\n\n"""                        
                    elif 'supply' in item[4]:
                        icon = ':small_orange_diamond:'
                        #line = line + f""" `{item_code}` :small_orange_diamond: **{self.data['item'][item_code].name}** \n|| *"{self.data['item'][item_code].description}"*\n|| **`Price`** ${self.data['item'][item_code].price}\n|| **`Quantity`** {items[item_code]}\n++ `{'` `'.join(self.data['item'][item_code].tags)}`\n\n"""
                    elif 'ingredient' in item[4]:
                        icon = '<:green_ruby:520092621381697540>'
                        #line = line + f""" `{item_code}` <:green_ruby:520092621381697540> **{self.data['ingredient'][item_code].name}**\n|| *"{self.data['ingredient'][item_code].description}"*\n|| **`Price`** ${self.data['ingredient'][item_code].price}\n|| **`Quantity`** {items[item_code]}\n++ `{'` `'.join(self.data['ingredient'][item_code].tags)}`\n\n"""                            
                    line = line + f""" `{item[0]}` {icon} `{item[1]}`|`{item[8]}`|**{item[2]}**\n|| *"{item[3]}"*\n|| `『Weight』{item[5]}`\n|| **`Price`**`${item[7]}` · **`Quantity`**`{item[6]}`\n++ `{item[4].replace(' - ', '` `')}`\n\n"""
                            
                line = line + "**------------------------------ oo ------------------------------**" 

                reembed = discord.Embed(title = f"INVENTORY", colour = discord.Colour(0x011C3A), description=line)
                reembed.set_footer(text=f"Total: {len(items)} | Page {currentpage} of {pages}")
                return reembed
                #else:
                #    await client.say("*Nothing but dust here...*")
            
            async def attachreaction(msg):
                await self.client.add_reaction(msg, "\U000023ee")    #Top-left
                await self.client.add_reaction(msg, "\U00002b05")    #Left
                await self.client.add_reaction(msg, "\U000027a1")    #Right
                await self.client.add_reaction(msg, "\U000023ed")    #Top-right

            pages = int(len(items)/5)
            if len(items)%5 != 0: pages += 1
            currentpage = 1
            myembed = makeembed(0, 5, pages, currentpage)
        
            msg = await self.client.say(embed=myembed)
            await attachreaction(msg)

            while True:
                try:
                    reaction, user = await self.client.wait_for_reaction(message=msg, timeout=20)
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
    @commands.cooldown(1, 2, type=BucketType.user)
    async def avause(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        raw = list(args)
        slots = {"a": 'right_hand', "b": "left_hand"}

        try:
            # Filter
            int(raw[0])

            # INCONSUMABLE
            try:
                ##Get weapon info
                try: w_name, w_tags, w_quantity, w_eq, w_weight = await self.quefe(f"SELECT name, tags, quantity, effect_query, weight FROM pi_inventory WHERE user_id='{ctx.message.author.id}' AND item_id='{raw[0]}';")
                except TypeError: await self.client.say(f":warning: You don't own this item! (id.`{raw[0]}`)"); return

                if 'supply' in w_tags or 'ingredient' in w_tags: raise ZeroDivisionError

                ##Get slot_name
                try: slot_name = slots[raw[1]]
                except IndexError: slot_name = slots['a']
                except KeyError: await self.client.say(f":warning: Slots not found, **{ctx.message.author.name}**!\n:grey_question: There are `2` weapon slots available: `0` Main Weapon | `1` Secondary Weapon"); return
                ##Get weapon
                weapon = await self.quefe(f"SELECT {slot_name} FROM personal_info WHERE id='{ctx.message.author.id}';"); weapon = weapon[0]

                ##Equip
                if raw[0] != weapon:
                    await _cursor.execute(f"UPDATE personal_info SET {slot_name}='{raw[0]}' WHERE id='{ctx.message.author.id}';")
                    # Inform, of course :)
                    await self.client.say(f":white_check_mark: Equipped item `{raw[0]}`|**{w_name}** to `{slot_name}` slot!"); return
                ###Already equip    -----> Unequip
                else:
                    await _cursor.execute(f"UPDATE personal_info SET {slot_name}='ar13' WHERE id='{ctx.message.author.id}'")
                    await self.client.say(f":white_check_mark: Unequipped item `{raw[0]}`|**{w_name}** from *{slot_name}* slot!")
                    return
            # CONSUMABLE (Supply / Ingredient)
            except ZeroDivisionError:
                
                # Effect_query check
                if not w_eq: await self.client.say(":white_check_mark: Tried to use, but no effect received."); return

                ## Get quantity
                try:
                    target_id = ctx.message.author.id
                    quantity = int(raw[1])
                    # SCAM :)
                    if quantity <= 0: await self.client.say("**Heyyyyyyyyy scammer-!**"); return
                    if w_quantity <= quantity: 
                        quantity = w_quantity
                        quantity_query = f"DELETE FROM pi_inventory WHERE item_id='{raw[0]}' AND user_id='{target_id}';"

                ## E: No quantity given
                except IndexError:
                    target_id = ctx.message.author.id
                    quantity = 1
                    if w_quantity <= quantity: 
                        quantity = w_quantity
                        quantity_query = f"DELETE FROM pi_inventory WHERE item_id='{raw[0]}' AND user_id='{target_id}';"
                    else:
                        quantity_query = f"UPDATE pi_inventory SET quantity=quantity-{quantity} WHERE item_id='{raw[0]}' AND user_id='{target_id}';"

                ## E: Invalid type of quantity argument
                except TypeError:
                    ## Get target_id
                    try: target_id = ctx.message.mentions[0].id
                    ## E: No mention
                    except IndexError: target_id = ctx.message.author.id
                    quantity = 1
                    if w_quantity <= quantity:
                        quantity = w_quantity
                        quantity_query = f"DELETE FROM pi_inventory WHERE item_id='{raw[0]}' AND user_id='{target_id}';"
                    else:
                        quantity_query = f"UPDATE pi_inventory SET quantity=quantity-{quantity} WHERE item_id='{raw[0]}' AND user_id='{target_id}';"

                # Get target info
                try: t_name, t_STA, t_MAX_STA = await self.quefe(f"SELECT name, STA, MAX_STA FROM personal_info WHERE id='{target_id}';")
                except TypeError: await self.client.say(":warning: Target has not incarnated")
                # Prepair query
                w_eq = w_eq.replace("user_id_here", target_id)
                af_query = ''
                for time in range(quantity):
                    # Affect
                    af_query = af_query + w_eq

                # Weight check :">
                ex_query = ''
                if t_STA > t_MAX_STA:
                    # Weigh on the commander. Please don't change
                    ex_query = f"UPDATE personal_info SET weight=weight+{random.choice([0, 0.1, 0.2, 0.5, 1, 1.2, 1.5, 2])*w_weight*quantity} WHERE id='{ctx.message.author.id}';"
                await self.ava_scan(ctx.message, type='normalize', target_id=target_id)

                ## Adjusting things with quantity
                await _cursor.execute(quantity_query + af_query + ex_query)
                #print(quantity_query + af_query + ex_query)
                await self.client.say(f":white_check_mark: Used {quantity} `{raw[0]}`|**{w_name}** on **{t_name}**")                

        # E: Slot not given            
        except IndexError:
            # Switch
            mw, sw = await self.quefe(f"SELECT right_hand, {slots['b']} FROM personal_info WHERE id='{ctx.message.author.id}';")
            await _cursor.execute(f"UPDATE personal_info SET right_hand='{sw}', {slots['b']}='{mw}' WHERE id='{ctx.message.author.id}';")

            # Get line
            sw_name = await self.quefe(f"SELECT name FROM pi_inventory WHERE user_id='{ctx.message.author.id}' AND item_id='{sw}';")
            if sw_name: line_1 = f"`{sw}`|**{sw_name}** ➠ **right_hand**"
            else: line_1 = '**right_hand** is left empty'
            mw_name = await self.quefe(f"SELECT name FROM pi_inventory WHERE user_id='{ctx.message.author.id}' AND item_id='{mw}';")
            if mw_name: line_2 = f"`{mw}`|**{mw_name}** ➠ **{slots['b']}**'"
            else: line_2 = f"**{slots['b']}** is left empty"
            # Inform :)
            await self.client.say(f":twisted_rightwards_arrows: {line_1} **|** {line_2} "); return
    
        # E: <item_code> OR <slot> given, instead of <item_id>
        except ValueError:

            # SLOT SWITCHING
            try:
                # Switch
                mw, sw = await self.quefe(f"SELECT right_hand, {slots[raw[0]]} FROM personal_info WHERE id='{ctx.message.author.id}';")
                await _cursor.execute(f"UPDATE personal_info SET right_hand='{sw}', {slots['b']}='{mw}' WHERE id='{ctx.message.author.id}';")

                # Get line
                sw_name = await self.quefe(f"SELECT name FROM pi_inventory WHERE user_id='{ctx.message.author.id}' AND item_id='{sw}';")
                if sw_name: line_1 = f"`{sw}`|**{sw_name}** ➠ **right_hand**"
                else: line_1 = '**right_hand** is left empty'
                mw_name = await self.quefe(f"SELECT name FROM pi_inventory WHERE user_id='{ctx.message.author.id}' AND item_id='{mw}';")
                if mw_name: line_2 = f"`{mw}`|**{mw_name}** ➠ **{slots[raw[0]]}**'"
                else: line_2 = f"**{slots[raw[0]]}** is left empty"
                # Inform :)
                await self.client.say(f":twisted_rightwards_arrows: {line_1} **|** {line_2} "); return
            # E: Slot not found
            except KeyError: pass

    @commands.command(pass_context=True, aliases=['>trader'])
    async def avatrader(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        cmd_tag = 'trade'

        cur_PLACE, cur_X, cur_Y, money = await self.quefe(f"SELECT cur_PLACE, cur_X, cur_Y, money FROM personal_info WHERE id='{ctx.message.author.id}';")

        if not await self.area_scan(ctx, cur_X, cur_Y): await self.client.say(":warning: Traders aren't availablie outside of **Peace Belt**!"); return
        raw = list(args); quantity = 1

        # COOLDOWN
        #if not await self.__cd_check(ctx.message, cmd_tag, f"The storm is coming so they ran away."): return
        #else: await self.client.loop.run_in_executor(None, partial(redio.set, f'{cmd_tag}{ctx.message.author.id}', 'trading', ex=3600, nx=True))

        # Get cuisine
        cuisine, r_name = await self.quefe(f"SELECT cuisine, name FROM environ WHERE environ_code='{cur_PLACE}';")

        # Get menu
        menu = []
        for count in range(5):
            menu.append(random.choice(cuisine.split(' - ')))

        # Get items
        items = {}
        for item in set(menu):
            items[item] = await self.quefe(f"SELECT name, description, price, tags FROM model_ingredient WHERE ingredient_code='{item}';")

        # MENU
        line = "\n"
        for ig_code in menu:
            line = line + f""" `{ig_code}` <:green_ruby:520092621381697540> **{items[ig_code][0]}**\n|| *"{items[ig_code][1]}"*\n|| **`Market price`** ${items[ig_code][2]}\n++ `{items[ig_code][3].replace(' - ', '` `')}`\n\n"""
            
        reembed = discord.Embed(title = f"------------- KINUKIZA's MARKET of `{cur_PLACE}`|**{r_name}** -----------", colour = discord.Colour(0x011C3A), description=line)
        await self.client.say(embed=reembed)
        await self.client.say(':bell: Syntax: `!buy` `[item_code]` ||  Time out: 60s')

        def check(msg):
            return msg.content.startswith('!buy ')

        # First buy
        raw = await self.client.wait_for_message(author=ctx.message.author, check=check, timeout=10)
        try: 
            raw = raw.content.lower().split(' ')[1:]
            ig_code = raw[0]
            try: 
                quantity = int(raw[1])
                if quantity > 5: quantity = 5
                # SCAM :)
                if quantity <= 0: await self.client.say("Don't be dumb <:fufu:520602319323267082>"); return                
            # E: Quantity not given, or invalidly given
            except (IndexError, TypeError): pass

            # ig_code check    
            if ig_code not in menu: await self.client.say(":warning: The trader does not have this item at the moment. Sorry."); return
        except AttributeError: await self.client.say(":warning: Request timed out!"); return

        # Reconfirm
        price = int(items[ig_code][2]*random.choice([0.1, 0.2, 0.5, 1, 2, 5, 10]))
        await self.client.say(f"{ctx.message.author.mention}, the dealer set the price of **${price}** for __each__ item `{ig_code}`|**{items[ig_code][0]}**. \nThat would cost you **${price*quantity}** in total.\n:bell: Proceed? (y/n)")
        resp = await self.client.wait_for_message(author=ctx.message.author, timeout=10)
        try:
            if resp.content.lower() not in ['y', 'yes']: await self.client.say(":warning: Request declined!"); return
        except AttributeError: await self.client.say(":warning: Request declined!"); return
        
        try:
            # Money check
            if price*quantity <= money:
                # UN-SERIALIZABLE
                # Increase item_code's quantity
                if await _cursor.execute(f"UPDATE pi_inventory SET quantity=quantity+{quantity} WHERE user_id='{ctx.message.author.id}' AND item_code='{ig_code}';") == 0:
                    # E: item_code did not exist. Create one, with given quantity
                    await _cursor.execute(f"INSERT INTO pi_inventory SELECT 0, {ctx.message.author.id}, ingredient_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, infuse_query, {quantity}, price, dmg, stealth, evo, aura, illulink FROM model_ingredient WHERE ingredient_code='{ig_code}';")

                # Deduct money
                await _cursor.execute(f"UPDATE personal_info SET money=money-{price*quantity} WHERE id='{ctx.message.author.id}';")

            else: await self.client.say(":warning: Insufficience balance!"); return
        # E: Item_code not found
        except KeyError: await self.client.say(":warning: Item's code not found!"); return


        # Greeting, of course :)
        await self.client.say(f":white_check_mark: Received **{quantity}** item `{ig_code}`|**{items[ig_code][0]}**. Nice trade!")

    @commands.command(pass_context=True, aliases=['>sell'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def avasell(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        try: right_hand, left_hand = await self.quefe(f"SELECT right_hand, left_hand FROM personal_info WHERE id='{ctx.message.author.id}' AND cur_X<1 AND cur_Y<1;")
        # E: Out of PB
        except TypeError: await self.client.say(":warning: You think you can find customers outside of **Peace Belt**??"); return

        quantity = 1; raw = list(args)
        try: quantity = int(raw[1])
        except (IndexError, ValueError): pass

        # SCAM :)
        if quantity <= 0: await self.client.say("**Heyyyyyyyyy scammer-!**"); return  

        try: w_name, w_price, w_quantity, w_tags = await self.quefe(f"SELECT name, price, quantity, tags FROM pi_inventory WHERE user_id='{ctx.message.author.id}' AND item_id='{raw[0]}';")
        # E: Item_id not found
        except TypeError: await self.client.say(":warning: You don't own this weapon!"); return      

        if 'untradable' in w_tags: await self.client.say(f":warning: You cannot sell this item, {ctx.message.author.id}."); return

        try:
            # Selling
            # CONSUMABLE
            if not 'inconsumable' in w_tags:
                # Quantity check
                if quantity >= w_quantity:
                    quantity = w_quantity
                    quantity_query = f"DELETE FROM pi_inventory WHERE item_code='{raw[0]}' AND user_id='{ctx.message.author.id}';"
                else: quantity_query = f"UPDATE pi_inventory SET quantity=quantity-{quantity} WHERE item_code='{raw[0]}' AND user_id='{ctx.message.author.id}';"

                receive = int(w_price*random.choice([0.1, 0.2, 0.5, 0.6, 1, 1.5, 4])*quantity)
                receive_query = f"UPDATE personal_info SET money=money+{receive} WHERE id='{ctx.message.author.id}';"
             
            # INCONSUMABLE
            else:
                # Equipped weapon check
                if raw[0] in [right_hand, left_hand]: await self.client.say(":warning: You cannot sell an item that being equipped!"); return

                quantity_query = f"DELETE FROM pi_inventory WHERE item_id='{raw[0]}' AND user_id='{ctx.message.author.id}';"

                receive = int(w_price*random.choice([0.1, 0.25, 0.2, 0.4, 0.5, 0.6, 0.75, 1, 4])*quantity)
                receive_query = f"UPDATE personal_info SET money=money+{receive} WHERE id='{ctx.message.author.id}';"

        # E: Item_id not found
        except KeyError: await self.client.say(":warning: You don't own this weapon!"); return

        # Receiving money/Removing item
        await _cursor.execute(receive_query + quantity_query)

        await self.client.say(f":white_check_mark: You received **${receive}** from selling {quantity} `{raw[0]}`|**{w_name}**, **{ctx.message.author.name}**!")

    @commands.command(pass_context=True, aliases=['>give'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def avagive(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        raw = list(args)

        # Receiver check
        try: 
            receiver = ctx.message.mentions[0]
            try: 
                t_cur_X, t_cur_Y, t_cur_PLACE, t_partner = await self.quefe(f"SELECT cur_X, cur_Y, cur_PLACE, partner FROM personal_info WHERE id='{receiver.id}';")
                cur_X, cur_Y, cur_PLACE, money, partner = await self.quefe(f"SELECT cur_X, cur_Y, cur_PLACE, money, partner FROM personal_info WHERE id='{ctx.message.author.id}';")
            # E: Id not found
            except TypeError: await self.client.say(":warning: User don't have an ava!"); return
        except IndexError: await self.client.say(f":warning: Please provide a receiver, **{ctx.message.author.name}**!"); return

        # Distance check
        if cur_PLACE != t_cur_PLACE:
            if not (partner == receiver.id and t_partner == ctx.message.author.id):
                await self.client.say(f":warning: You need to be in the same region with the receiver, **{ctx.message.author.name}**!"); return
        if await self.distance_tools(cur_X, cur_Y, t_cur_X, t_cur_Y, int(args[0])/1000, int(args[1])/1000) > 50:
            if not (partner == receiver.id and t_partner == ctx.message.author.id):
                await self.client.say(f":warning: You need to be within **50 m** range of the receiver, **{ctx.message.author.name}**!"); return

        package = int(raw[0])

        # Money check
        try:
            if package > money: await self.client.say(":warning: Insufficient balance!"); return
            # SCAM :)
            if package <= 0: await self.client.say("**Heyyyyyyyyy scammer-!**"); return
        except ValueError: await self.client.say(":warning: Invalid syntax!"); return
            
        # Transfer
        await _cursor.execute(f"UPDATE personal_info SET money=money+IF(id='{ctx.message.author.id}', -{package}, {package}) WHERE id IN ('{ctx.message.author.id}', '{receiver.id}');")
        await self.client.say(f":white_check_mark: You've been given **${raw[0]}**, {receiver.mention}!")

    @commands.command(pass_context=True, aliases=['>trade'])
    @commands.cooldown(1, 10, type=BucketType.user)
    async def avatrade(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        raw = list(args)

        # Receiver check
        try: 
            receiver = ctx.message.mentions[0]
            try: 
                t_cur_X, t_cur_Y, t_cur_PLACE, t_money = await _cursor.execute(f"SELECT cur_X, cur_Y, cur_PLACE, money FROM personal_info WHERE id='{receiver.id}';")
                cur_X, cur_Y, cur_PLACE = await _cursor.execute(f"SELECT cur_X, cur_Y, cur_PLACE FROM personal_info WHERE id='{ctx.message.author.id}';")
            # E: Id not found
            except TypeError: await self.client.say(":warning: User don't have an ava!"); return
        except IndexError: await self.client.say(f":warning: Please provide a receiver, **{ctx.message.author.name}**!"); return

        # Distance check
        if cur_PLACE != t_cur_PLACE:
            await self.client.say(f":warning: You need to be in the same region with the receiver, **{ctx.message.author.name}**!"); return
        if await self.distance_tools(cur_X, cur_Y, t_cur_X, t_cur_Y, int(args[0])/1000, int(args[1])/1000) > 50:
            await self.client.say(f":warning: You need to be within **50 m** range of the receiver, **{ctx.message.author.name}**!"); return

        # Get item's info
        try: w_tags, w_name, w_quantity, w_code = await self.quefe(f"SELECT tags, name, quantity, item_code FROM pi_inventory WHERE user_id='{ctx.message.author.id}' AND item_id='{raw[0]}';")
        except TypeError: await self.client.say(":warning: You don't own this item!"); return

        if 'untradable' in w_tags: await self.client.say(f":warning: You cannot trade this item, **{ctx.message.author.name}**. It's *untradable*, look at its tags."); return

        # INCONSUMABLE
        if 'inconsumable' in w_tags:
            await _cursor.execute(f"UPDATE pi_inventory SET user_id='{receiver.id}' WHERE item_id='{raw[0]}';")
        
        # CONSUMABLE
        else:
            # Quantity given
            try:
                # Quantity check
                if int(raw[1]) >= w_quantity:
                    quantity = w_quantity
                    # Check if receiver has already had the item
                    if await _cursor.execute(f"UPDATE pi_inventory SET quantity=quantity+{quantity} WHERE user_id='{receiver.id}' AND item_code='{w_code}';") == 0:
                        await _cursor.execute(f"UPDATE pi_inventory SET user_id='{receiver.id}' WHERE item_id='{raw[0]}';")

                else:
                    quantity = int(raw[1])
                    # SCAM :)
                    if quantity <= 0: await self.client.say("**Heyyyyyyyyy scammer-!**"); return
                    # Check if receiver has already had the item
                    if await _cursor.execute(f"UPDATE pi_inventory SET quantity=quantity+{quantity} WHERE user_id='{receiver.id}' AND item_code='{w_code}';") == 0:
                        await _cursor.execute(f"INSERT INTO pi_inventory SELECT 0, '{receiver.id}', item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, {quantity}, price, dmg, stealth, aura, illulink FROM pi_inventory WHERE item_id='{w_code}' AND user_id='{ctx.message.author.id}';")
            # Quantit NOT given
            except (ValueError, IndexError): 
                quantity = 1
                # Check if receiver has already had the item
                if await _cursor.execute(f"UPDATE pi_inventory SET quantity=quantity+{quantity} WHERE user_id='{receiver.id}' AND item_code='{w_code}';") == 0:
                    await _cursor.execute(f"INSERT INTO pi_inventory SELECT 0, '{receiver.id}', item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, {quantity}, price, dmg, stealth, aura, illulink FROM pi_inventory WHERE item_id='{w_code}' AND user_id='{ctx.message.author.id}';")

        # Inform, of course :>
        await self.client.say(f":white_check_mark: You've been given `{quantity}` `{w_code}`|**{w_name}**, {ctx.message.author.mention}!")

    @commands.command(pass_context=True, aliases=['>bank'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def avabank(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        # Status check
        try: money, cur_X, cur_Y, age, status = await self.quefe(f"SELECT money, cur_X, cur_Y, age, status FROM personal_info WHERE id='{ctx.message.author.id}' AND status NOT IN ('ORANGE', 'RED');")
        except TypeError: await self.client.say(f":warning: You need a **GREEN** or **YELLOW** status to perform this command, **{ctx.message.author.name}**."); return

        # Coord check
        if not await self.area_scan(ctx, cur_X, cur_Y): await self.client.say(":warning: Banks are only available within **Peace Belt**!"); return

        # Account getting
        try: invs, invs_interst, invest_age, tier = await self.quefe(f"SELECT investment, interest, invest_age, tier FROM pi_bank WHERE user_id='{ctx.message.author.id}';")
        # E: User does not have account
        except TypeError:
            # Get confirmation
            await self.client.say(f":bank: Greeting, {ctx.message.author.mention}. It seems that there's no account has your id on it. Perhaps, would you like to open one?\n:bell: *Proceed?* (Key: `account confirm` | Timeout=10s)")
            if not await self.client.wait_for_message(timeout=10, author=ctx.message.author, channel=ctx.message.channel, content='account confirm'): await self.client.say(f":bank: Indeed. Why would mongrels need a bank account..."); return
            
            # Create account
            await _cursor.execute(f"INSERT INTO pi_bank VALUES ('{ctx.message.author.id}', 0, 0, 0.01, '1');")
            await self.client.say(f":white_check_mark: Your account has been successfully created!"); return

        raw = list(args)

        try:
            # INVEST
            if raw[0] == 'invest':
                try:
                    quantity = int(raw[1])
                    if quantity >= money: quantity = money
                    elif quantity < 0: await self.client.say("Don't be stupid <:fufu:520602319323267082>"); return

                    # Update prev investment, then the investment, then the invest_age
                    await _cursor.execute(f"UPDATE pi_bank SET investment=(investment+investment*{invs_interst}*{age - invest_age})+{quantity}, invest_age={age} WHERE user_id='{ctx.message.author.id}';")
                    await _cursor.execute(f"UPDATE personal_info SET money=money-{quantity}, status=IF(money>=0, 'GREEN', 'YELLOW') WHERE id='{ctx.message.author.id}';")

                    await self.client.say(f":white_check_mark: Added **${quantity}** to your account!"); return

                # E: Quantity not given
                except (IndexError, ValueError): await self.client.say(":warning: Please provide the amount you want to invest."); return

            # WITHDRAW
            elif raw[0] == 'withdraw':
                try:
                    if status == 'YELLOW': await self.client.say(":warning: You need a **GREEN** status to withdraw money."); return

                    quantity = int(raw[1])
                    if quantity >= invs: quantity = invs
                    elif quantity < 0: await self.client.say("Don't be stupid <:fufu:520602319323267082>"); return

                    # Update prev investment, then the investment, then the invest_age
                    await _cursor.execute(f"UPDATE pi_bank SET investment=(investment+investment*{invs_interst}*{age - invest_age})-{quantity}, invest_age={age} WHERE user_id='{ctx.message.author.id}';")
                    await _cursor.execute(f"UPDATE personal_info SET money=money+{quantity} WHERE id='{ctx.message.author.id}';")

                    await self.client.say(f":white_check_mark: **${quantity}** has just been withdrawn from your account!"); return
                # E: Quantity not given
                except (IndexError, ValueError): await self.client.say(":warning: Please provide the amount you want to withdraw."); return
            
            # TRANSFER
            elif raw[0] == 'transfer':
                try:
                    if status == 'YELLOW': await self.client.say(":warning: You need a **GREEN** status to transfer money."); return
                    
                    # Get quantity
                    for i in raw[1:]:
                        try: quantity = int(i)
                        except ValueError: continue
                        if quantity >= invs: quantity = invs
                        elif quantity < 0: await self.client.say("Don't be stupid <:fufu:520602319323267082>"); return

                    # Get target
                    target = ctx.message.mentions[0]
                    if not target: await self.client.say(":warning: Please provide a receiver"); return

                    # Tax and shiet
                    tax = 40 - int(tier)*5
                    try: q_atx = int(quantity/100*(100-tax))
                    except NameError: await self.client.say(":warning: Please provide the amount of money"); return

                    line = f"""```clean
        BEFORE Tax:⠀⠀⠀⠀⠀⠀⠀$ {quantity}
        TAX:⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀x⠀  {tax} %
        -----------------------------
        AFTER Tax:⠀⠀⠀⠀⠀⠀⠀⠀$ {q_atx}```"""

                    await self.client.say(f":bank: | **{ctx.message.author.name}**⠀⠀>>>⠀⠀**{target.name}**\n{line}:bell: Proceed? (Key: `transfer confirm` | Timeout=10s)")
                    if not await self.client.wait_for_message(timeout=15, author=target, channel=ctx.message.author.channel, content='transfer confirm'):
                        await self.client.say(f":bank: Aborted!"); return

                    # Transfer
                    if await _cursor.execute(f"UPDATE pi_bank SET investment=investment+{q_atx} WHERE id='{target.id}';") == 0:
                        await self.client.say(f":warning: User does not have a bank account!"); return
                    # Update prev investment, then the investment, then the invest_age
                    await _cursor.execute(f"UPDATE pi_bank SET investment=(investment+investment*{invs_interst}*{age - invest_age})-{quantity}, invest_age={age} WHERE user_id='{ctx.message.author.id}';")

                    await self.client.say(f":bank: **${q_atx}** has been successfully added to **{target.name}**'s bank account."); return

                # E: Quantity not given
                except (IndexError, ValueError): await self.client.say(":warning: Please provide the amount you want to withdraw."); return

            # LOAN
            elif raw[0] == 'loan':
                try:
                    if status == 'YELLOW': await self.client.say(":warning: You need a **GREEN** status to request a loan."); return
                    stata = 'GREEN'

                    quantity = int(raw[1])
                    if quantity >= invs: 
                        # Check if the loan is off-limit
                        if quantity > invs*3: await self.client.say(f":warning: You cannot loan 3 times your current balance"); return
                        stata = 'YELLOW'
                    elif quantity < 0: await self.client.say("Don't be stupid <:fufu:520602319323267082>"); return

                    # Update prev investment, then the investment, then the invest_age
                    await _cursor.execute(f"UPDATE pi_bank SET investment=(investment+investment*{invs_interst}*{age - invest_age})-{quantity}, invest_age={age} WHERE user_id='{ctx.message.author.id}';")
                    await _cursor.execute(f"UPDATE personal_info SET money=money+{quantity}, status='{stata}' WHERE id='{ctx.message.author.id}';")

                    await self.client.say(f":white_check_mark: **${quantity}** has just been withdrawn from your account!"); return
                # E: Quantity not given
                except (IndexError, ValueError): await self.client.say(":warning: Please provide the amount you want to withdraw."); return                         

            # UPGRADE
            elif raw[0] == 'upgrade':
                tier_dict = {'2': [('elementary', 'international_bussiness'), 0.02], 
                            '3': [('middleschool', 'international_bussiness'), 0.03], 
                            '4': [('highschool', 'international_bussiness'), 0.04], 
                            '5': [('associate', 'international_bussiness'), 0.05], 
                            '6': [('bachelor', 'international_bussiness'), 0.06], 
                            '7': [('master', 'international_bussiness'), 0.08], 
                            '8': [('doctorate', 'international_bussiness'), 0.1]}

                next_tier = str(int(tier) + 1)
                try:
                    # Update the tier, if the check is True
                    if await _cursor.execute(f"UPDATE pi_bank SET tier='{next_tier}', interest={tier_dict[next_tier][1]} WHERE user_id='{ctx.message.author.id}' AND EXISTS (SELECT * FROM pi_degrees WHERE user_id='{ctx.message.author.id}' AND degree='{tier_dict[next_tier][0][0]}' AND major='{tier_dict[next_tier][0][1]}');") == 0:
                        await self.client.say(f":bank: Sorry. Your request to upgrade to tier `{next_tier}` does not meet the criteria."); return
                except KeyError: await self.client.say(f":bank: Your current tier is `{tier}`, which is the highest."); return

                await self.client.say(f":white_check_mark: Upgraded to tier `{next_tier}`!"); return

            # DOWNGRADE
            elif raw[0] == 'downgrade':
                tier_dict = {'2': [('elementary', 'international_bussiness'), 0.02], 
                            '3': [('middleschool', 'international_bussiness'), 0.03], 
                            '4': [('highschool', 'international_bussiness'), 0.04], 
                            '5': [('associate', 'international_bussiness'), 0.05], 
                            '6': [('bachelor', 'international_bussiness'), 0.06], 
                            '7': [('master', 'international_bussiness'), 0.08], 
                            '8': [('doctorate', 'international_bussiness'), 0.1]}

                next_tier = str(int(tier) - 1)
                try:
                    # Update the tier, if the check is True
                    await _cursor.execute(f"UPDATE pi_bank SET tier='{next_tier}', interest={tier_dict[next_tier][1]} WHERE user_id='{ctx.message.author.id}';")
                except KeyError: await self.client.say(f":bank: Your current tier is `{tier}`, which is the lowest to be able to downgrade."); return

                await self.client.say(f":white_check_mark: Downgraded to tier `{next_tier}`!"); return

        # E: args not given
        except IndexError:

            line = f""":bank: `『TIER』` **· `{tier}`** ⠀⠀ ⠀:bank: `『INTEREST』` **· `{invs_interst}`** \n```$ {invs}```"""

            reembed = discord.Embed(title = f"{ctx.message.author.name.upper()}", colour = discord.Colour(0x011C3A), description=line)
            reembed.set_thumbnail(url=ctx.message.author.avatar_url)

            await self.client.say(embed=reembed)





# ============= LIFE ==================

    @commands.command(pass_context=True, aliases=['>marry'])
    @commands.cooldown(1, 60, type=BucketType.user)
    async def avamarry(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        try: target = ctx.message.mentions[0]
        except IndexError: await self.client.say(f":revolving_hearts: Please tell us your love one, **{ctx.message.author.name}**!"); return

        name, partner, cur_PLACE = await self.quefe(f"SELECT name, partner, cur_PLACE FROM personal_info WHERE id='{ctx.message.author.id}';")
        try: t_name, t_partner, t_cur_PLACE = await self.quefe(f"SELECT name, partner, cur_PLACE FROM personal_info WHERE id='{target.id}';")
        except TypeError: await self.client.say(f":warning: User has not incarnated yet, {ctx.message.author.name}!"); return

        if 'n/a' in [partner, t_partner]: await self.client(f":revolving_hearts: One of you has already been married, {ctx.message.author.name}!"); return
        if cur_PLACE != t_cur_PLACE: await self.client.say(f":revolving_hearts: You two need to be in the same region!"); return

        line = f"""```css
    ...{name.upper()}: "Father. Smith. Warrior. Mother. Maiden. Crone. Stranger. I am his/hers, and s/he is mine, from this day, until the end of my days."
    ...KALEI: "And you, [{t_name}]?"```"""

        line_no = f"""```css
    ...{name.upper()}: "Father. Smith. Warrior. Mother. Maiden. Crone. Stranger. I am his/hers, and s/he is mine, from this day, until the end of my days."
    ...KALEI: "And you, [{t_name}]?"
    ...{t_name.upper()}: "NOPE"```"""

        line_yes = f"""```css
    ...{name.upper()}: "Father. Smith. Warrior. Mother. Maiden. Crone. Stranger. I am his/hers, and s/he is mine, from this day, until the end of my days."
    ...KALEI: "And you, [{t_name}]?"
    ...{t_name.upper()}: "Father. Smith. Warrior. Mother. Maiden. Crone. Stranger. I am his/hers, and s/he is mine, from this day, until the end of my days."```"""

        msg = await self.client.say(line + f":revolving_heart: Hey {target.mention}, {ctx.message.author.mention} is asking you to be his partner. Please react if you accept their proposal!")
        await self.client.add_reaction(msg, "\U00002764")
        if not await self.client.wait_for_reaction(emoji='\U00002694', user=target, message=msg, timeout=30):
            await self.client.edit_message(msg, line_no); return
        await self.client.edit_message(msg, line_yes)

        # Add partner
        await _cursor.execute(f"UPDATE personal_info SET partner='{target.id}' WHERE id='{ctx.message.author.id}'; UPDATE personal_info SET partner='{ctx.message.author.id}' WHERE id='{target.id}';")





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
    @commands.cooldown(1, 3, type=BucketType.user)
    async def avaattack(self, ctx, *args):
        """ -avaattack [moves] [target]
            -avaattack [moves]              
            <!> ONE target of each creature type at a time. Mobs always come first, then user. Therefore you can't fight an user while fighting a mob
            <!> DO NOT lock on current_enemy at the beginning. Do it at the end."""
        if not await self.ava_scan(ctx.message, type='life_check'): return

        raw = list(args); __mode = 'PVP'

        # HANDLING CHECK =====================================
        try:
            note = {'both': '<:right_hand:521197677346553861><:left_hand:521197732162043922>', 'right': '<:right_hand:521197677346553861>', 'left': '<:left_hand:521197732162043922>'}

            await self.client.say(f'{note[raw[0]]} Changed to **{raw[0].upper()} hand** pose')
            await _cursor.execute(f"UPDATE personal_info SET combat_HANDLING='{raw[0].lower()}' WHERE id='{ctx.message.author.id}';"); return
        # E: Pose not given
        except IndexError: await self.client.say(f":warning: **{ctx.message.author.name}**, please make your moves!"); return
        # E: Moves given, not pose
        except KeyError: pass        

        # Get main_weapon, handling     ||      as well as checking coord
        try: combat_HANDLING, main_weapon = await self.quefe(f"SELECT combat_HANDLING, IF(combat_HANDLING IN ('both', 'right'), right_hand, left_hand) FROM personal_info WHERE id='{ctx.message.author.id}' AND cur_X>1 AND cur_Y>1;")
        # E: User in PB
        except TypeError: await self.client.say(":warning: You can't fight inside **Peace Belt**!"); return

        # Check if it's a PVP or PVE call
        # Then get the target (Mob/User)

        # Get user's info (always put last, for the sake of efficience)
        name, cur_MOB, cur_PLACE, cur_X, cur_Y, STA, STR = await self.quefe(f"SELECT name, cur_MOB, cur_PLACE, cur_X, cur_Y, STA, STR FROM personal_info WHERE id='{ctx.message.author.id}';")


        # INPUT CHECK =========================================
        # In case 2nd para is given
        try:
            # PVP   ||    USING MENTION
            if raw[1].startswith('<@'):
                # If there's no current_enemy   ||   # If there is, and the target is the current_enemy
                #if cur_USER == 'n/a':
                #    target = ctx.message.mentions[0]; target_id = target.id
                # If there is, but the target IS NOT the current_enemy. (Update: just freaking ignore it, for the sake of multiple battle sessions)         
                #elif ctx.message.mentions[0].id != cur_USER or raw[1] == cur_MOB: 
                #    await self.client.say(f":warning: Please finish your current fight with **{self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['user'][0].name}**!"); return
                #    target = ctx.message.mentions[0]; target_id = target.id
                target = ctx.message.mentions[0]; target_id = target.id
                __bmode = 'DIRECT'

            # PVE   ||    USING MOB'S ID
            elif raw[1].startswith('mob.'):
                # If there's no current_enemy   ||   # If there is, and the target is the current_enemy
                if not self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['mob'] or raw[1] == self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['mob'][0]:
                    target = raw[1]; __mode = 'PVE'; target_id = target
                # If there is, but the target IS NOT the current_enemy
                elif raw[1] != self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['mob'][0]: 
                    await self.client.say(f":warning: Please finish your current fight with the `{self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['mob'][0]}`!"); return

            # PVP   ||    USING USER'S ID
            else:
                try: 
                    target = await self.client.get_user_info(raw[0]); target_id = raw[0]
                except (discordErrors.NotFound, discordErrors.HTTPException): await self.client.say(":warning: Invalid user's id!"); return
                __bmode = 'INDIRECT'

        # In case 2nd para is not given, current_enemy is used
        except IndexError:
            # Mobs first. If there's no mob in current_enemy, then randomly pick one
            if cur_MOB == 'n/a':
                # If there's no mob lock on, then move on to user
                #   if not self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['user']:
                #       await self.client.say(":warning: You've not locked on anything yet!")
                #   else: 
                #       target = self.ava_dict[ctx.message.author.id]['realtime_zone']['current_enemy']['user']
                #       target_id = target.id
                target = random.choice(await self.quefe(f"SELECT mob_id FROM environ_mob WHERE region='{cur_PLACE}';", type='all'))[0]
                target_id = target
                __mode = 'PVE'
            else:
                target = cur_MOB
                target_id = target
                __mode = 'PVE'           


        # TARGET CHECK =========================================

        if __mode == 'PVP': 
            # Check if target has a ava     ||      GET TARGET's INFO
            try: t_cur_X, t_cur_Y, t_cur_PLACE = await self.quefe(f"SELECT cur_X, cur_Y, cur_PLACE FROM personal_info WHERE id='{target_id}' AND cur_PLACE='{cur_PLACE}';")
            # E: Invalid target, or target's not in the same region
            except TypeError:
                # Checking if target's cur_PLACE is the same as player's
                if not cur_PLACE == t_cur_PLACE: await self.client.say(f":warning: **{ctx.message.author.name}**, you and the target are not in the same region!"); return

                await self.client.say(":warning: Target don't have an ava!"); return

        elif __mode == 'PVE':
            # Check if target is a valid mob       ||       GET TARGET's INFO
            try: t_Ax, t_Ay, t_Bx, t_By, t_name = await self.quefe(f"SELECT limit_Ax, limit_Ay, limit_Bx, limit_By, name FROM environ_MOB WHERE mob_id='{target_id}' AND region='{cur_PLACE}';")
            # E: Invalid target, or target's not in the same region
            except TypeError: await self.client.say(f":warning: There is no `{target_id}` around! Perhap you should check your surrounding..."); return

            # Check if the user is in the mob's diversity
            if cur_X < t_Ax or cur_Y < t_Ay or cur_X > t_Bx or cur_Y > t_By:
                print(t_Ax, t_Ay, t_Bx, t_By, t_name)
                await self.client.say(f":warning: **{ctx.message.author.name}**, you can't engage the mob from your current location!"); return


        # WEAPON CHECK ==========================

        # Get weapon info
        w_multiplier, w_sta, w_speed = await self.quefe(f"SELECT multiplier, sta, speed FROM pi_inventory WHERE item_id='{main_weapon}';")

        # STA filter
        if len(raw[0])*w_sta < STA:
            if w_sta >= 100: await _cursor.execute(f"UPDATE personal_info SET STA=STA-2 WHERE id='{ctx.message.author.id}';")
            else: await _cursor.execute(f"UPDATE personal_info SET STA=STA-1 WHERE id='{ctx.message.author.id}';")
        else: await self.client.say(f":warning: {ctx.message.author.mention}, out of `STA`!"); return

        # Checking the length of moves
        moves_to_check = await self.quefe(f"SELECT value FROM pi_arts WHERE user_id='{ctx.message.author.id}' AND art_type='sword' AND art_name='chain_attack';")
        if len(raw[0]) > moves_to_check[0]:
            await self.client.say(f":warning: You cannot perform a `{len(raw[0])}-chain` attack, **{ctx.message.author.name}**!"); return

        # NOW THE FUN BEGIN =========================================

        counter_move = []

        # Decoding moves, as well as checking the moves. Get the counter_move
        for move in raw[0]:
            if move == 'a': counter_move.append('d')
            elif move == 'd': counter_move.append('b')
            elif move == 'b': counter_move.append('a')
            else: await self.client.say(f":warning: Invalid move! (move no. `{raw[0].index(move) + 1}` -> `{move}`)"); return
        
        # PVP use target, with personal_info =============================
        async def PVP():
            # If the duo share the same server, send msg to that server. If not, DM the attacked
            if __bmode == 'DIRECT': inbox = ctx.message
            else: inbox = await self.client.send_message(target, ctx.message.content)

            await self.client.add_reaction(inbox, '\U00002694')

            # GET TARGET's INFO the second time
            t_name, t_right_hand, t_left_hand, t_combat_HANDLING, t_STA = await self.quefe(f"SELECT name, right_hand, left_hand, combat_HANDLING, STA FROM personal_info WHERE id='{target_id}' AND cur_PLACE='{cur_PLACE}';")

            # Wait for move recognition     ||      The more STA consumed, the less time you have to recognize moves. Therefore, if you attack too many times, you'll be more vulnerable
            # RECOG is based on opponent's STA     ||      RECOG = oppo's STA / 30
            RECOG = t_STA / 30

            # If the attack is INDIRECT, multiple RECOG by 5
            if __bmode == 'INDIRECT': RECOG = RECOG*5

            if RECOG < 1: RECOG = 1
            if not await self.client.wait_for_reaction(emoji='\U00002694', user=target, message=inbox, timeout=RECOG):
                dmgdeal = round(STR*w_multiplier*len(counter_move))
                await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{target_id}';")
                await self.client.say(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{t_name}**"); return


            # Wait for response moves       ||        SPEED ('speed') of the sword
            def check(msg):
                return msg.content.startswith('!')
            
            SPEED = w_speed

            msg = await self.client.wait_for_message(timeout=SPEED, author=target, channel=inbox.channel, check=check)
            if not msg:
                dmgdeal = round(STR*w_multiplier*len(counter_move))
                await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{target_id}';")
                await self.client.say(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{target.name}**"); return
            
            # Measuring response moves
            hit_count = 0
            response_content = msg.content[1:]; diff = len(counter_move) - len(response_content)      # Measuring the length of the response
            if diff > 0: response_content += '-'*diff
            for move, response_move in zip(counter_move, response_content):
                if move != response_move: hit_count += 1

            # Conduct dealing dmg   ||  Conduct dealing STA dmg
            if hit_count == 0:
                await self.client.say(f"\n--------------------\n:shield: **{target.mention}** has successfully *guarded* all **{name}**'s attack!")

                # Recalculate the dmg, since hit_count == 0                
                ## Player's dmg
                if combat_HANDLING == 'both':
                    dmgdeal = round(STR*w_multiplier*len(counter_move))
                elif combat_HANDLING in ['right', 'left']:
                    dmgdeal = round(STR*w_multiplier*len(counter_move))*2
                ## Opponent's def
                if t_combat_HANDLING == 'both':
                    try:
                        tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE item_id='{t_left_hand}' AND user_id='{target_id}'")
                        dmgredu = 100 - tw_defend
                    except KeyError: dmgredu = 100    
                elif t_combat_HANDLING == 'right':
                    try:
                        tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE item_id='{t_right_hand}' AND user_id='{target_id}'")
                        dmgredu = 100 - tw_defend*2
                    except KeyError: dmgredu = 100
                elif t_combat_HANDLING == 'left':
                    try:
                        tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE item_id='{t_left_hand}' AND user_id='{target_id}'")
                        dmgredu = 100 - tw_defend*2
                    except KeyError: dmgredu = 100
                
                # If dmgredu > 0, backfire the attacker. If dmgredu >= 0, all dmg are neutralized
                temp_query = ''
                if dmgredu > 0:
                    temp_query += f"UPDATE personal_info SET STA=STA-{round(dmgdeal / 100 * abs(dmgredu))*tw_multiplier} WHERE id='{ctx.message.author.id}'; "
                    dmgredu = 0

                temp_query += f"UPDATE personal_info SET STA=STA-{round(dmgdeal / 100 * dmgredu)} WHERE id='{target_id}'; "
                await _cursor.execute(temp_query)

            else:

                # Recalculate the dmg             
                ## Player's dmg
                if combat_HANDLING == 'both':
                    dmgdeal = round(STR*w_multiplier*hit_count)
                elif combat_HANDLING in ['right', 'left']:
                    dmgdeal = round(STR*w_multiplier*hit_count)*2
                ## Opponent's def
                if t_combat_HANDLING == 'both':
                    tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE item_id='{t_left_hand}' AND user_id='{target_id}'")
                    dmgredu = 200 - tw_defend
                elif t_combat_HANDLING == 'right':
                    tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE item_id='{t_right_hand}' AND user_id='{target_id}'")
                    dmgredu = 200 - tw_defend*2
                elif t_combat_HANDLING == 'left':
                    tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE item_id='{t_left_hand}' AND user_id='{target_id}'")
                    dmgredu = 200 - tw_defend*2

                # If dmgredu > 0, backfire the attacker. If dmgredu >= 0, all dmg are neutralized
                temp_query = ''
                if dmgredu < 0:
                    temp_query += f"UPDATE personal_info SET STA=STA-{round(dmgdeal / 200 * abs(dmgredu))*tw_multiplier} WHERE id='{ctx.message.author.id}'; "
                    dmgredu = 0

                # Get dmgdeal (don't combine, for informing :>)
                dmgdeal = round(dmgdeal / 200 * dmgredu)
                temp_query += f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{target_id}'; "
                await _cursor.execute(temp_query)

                await self.client.say(f":dagger: **{ctx.message.author.name}** has dealt *{dmgdeal} DMG* to **{t_name}**")
        
            await self.ava_scan(ctx.message, 'life_check')

        # PVE use target_id, with environ_mob ======================
        if __mode == 'PVE':
            # ------------ USER PHASE   ||   User deal DMG 
            my_dmgdeal = round(STR*w_multiplier*len(counter_move))
            # Inform, of course :>
            await _cursor.execute(f"UPDATE environ_mob SET lp=lp-{my_dmgdeal} WHERE mob_id='{target_id}'; ")
            await self.client.say(f":dagger: **{name}** has dealt *{my_dmgdeal} DMG* to **「`{target_id}` | {t_name}」**!")


        if __mode == 'PVP':
            await PVP()
        elif __mode == 'PVE':
            await self.PVE(ctx.message, target_id)
        else: print("<<<<< OH SHIET >>>>>>>")

##########################

    @commands.command(pass_context=True, aliases=['>aim'])
    @commands.cooldown(1, 10, type=BucketType.user)
    async def avaaim(self, ctx, *args):
        # >Aim <coord_X> <coord_Y> <shots(optional)>      ||      >Aim <@user/mob_name> <shots(optional)>       ||          >Aim (defaul - shot=1)
        if not await self.ava_scan(ctx.message, type='life_check'): return

        # HANDLING CHECK =====================================
        raw = list(args)
        try:
            note = {'both': '<:right_hand:521197677346553861><:left_hand:521197732162043922>', 'right': '<:right_hand:521197677346553861>', 'left': '<:left_hand:521197732162043922>'}

            await self.client.say(f'{note[raw[0]]} Changed to **{raw[0].upper()} hand** pose')
            await _cursor.execute(f"UPDATE personal_info SET combat_HANDLING='{raw[0].lower()}' WHERE id='{ctx.message.author.id}';"); return
        # E: Pose not given
        except IndexError: await self.client.say(f":warning: **{ctx.message.author.name}**, please make your moves!"); return
        # E: Moves given, not pose
        except KeyError: pass


        # USER's INFO get ===================================================
        __mode = 'PVP'
        shots = 1

        # Get info     ||      as well as checking coord
        try: user_id, name, cur_PLACE, cur_X, cur_Y, cur_MOB, main_weapon, combat_HANDLING, STA, LP = await self.quefe(f"SELECT id, name, cur_PLACE, cur_X, cur_Y, cur_MOB, IF(combat_HANDLING IN ('both', 'right'), right_hand, left_hand), combat_HANDLING, STA, LP FROM personal_info WHERE id='{ctx.message.author.id}' AND cur_X>1 AND cur_Y>1;")
        # E: User in PB
        except TypeError: await self.client.say(":warning: You can't fight inside **Peace Belt**!"); return


        # INPUT ===============================================================

        # Get weapon's info
        w_round, w_firing_rate, w_sta, w_rmin, w_rmax, w_accu_randomness, w_accu_range, w_stealth, w_aura, w_multiplier, w_tags = await self.quefe(f"SELECT round, firing_rate, sta, range_min, range_max, accuracy_randomness, accuracy_range, stealth, aura, multiplier, tags FROM pi_inventory WHERE item_id='{main_weapon}';")
        w_tags = w_tags.split(' - ')
        if 'magic' in w_tags: _style = 'MAGIC'
        else: _style = 'PHYSIC'

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
                try: 
                    shots = int(raw[1])
                    if _style == 'MAGIC':
                        try: amount = int(raw[2])
                        except IndexError: amount = 1
                except IndexError: amount = 1
                except TypeError: amount = 1

            # Coord, shots provided     (if raw[0] is a mob_name, raise TypeError       ||      if raw[0] provided as <shots>, but raw[1] is not provided, raise IndexError)
            elif len(str(int(raw[0]))) <= 5 and len(raw[1]) <= 5 and _style == 'PHYSIC':
                print("OKAI HERE")
                X = int(raw[0])/1000; Y = int(raw[1])/1000

                # Get USER from COORD. If there are many users, randomly pick one.
                try: 
                    target_id = random.choice(await self.quefe(f"SELECT id FROM personal_info WHERE cur_X={X} AND cur_Y={Y} AND cur_PLACE='{cur_PLACE}';", type='all'))
                    target_id = target_id[0]
                    target = await self.client.get_user_info(target_id)
                    __bmode = 'DIRECT'
                    if not ctx.message.server.get_member(target_id): __bmode = 'INDIRECT'
                    if not target: await self.client.say(f"There's noone at **x:`{X:.3f}` y:`{Y:.3f}`** in {cur_PLACE}!"); return
                # E: Query's empty, since noone's at the given coord
                except IndexError: await self.client.say(f"There's noone at **x:`{X:.3f}` y:`{Y:.3f}`** in {cur_PLACE}!"); return
                
                # Get shots (if available and possible)
                try: 
                    shots = int(raw[2])
                except IndexError: pass
                except TypeError: pass

            # Shots AND amount given.     ||      Or coords, shots (and amount) given                     --------> MAGIC
            elif _style == 'MAGIC':
                print('YO HERE')
                # Coords, shots (and amount)
                try:
                    X = int(raw[0])/1000; Y = int(raw[1])/1000; shots = int(raw[2])

                    # Get USER from COORD. If there are many users, randomly pick one.
                    try: 
                        target_id = random.choice(await self.quefe(f"SELECT id FROM personal_info WHERE cur_X={X} AND cur_Y={Y} AND cur_PLACE='{cur_PLACE}';", type='all'))
                        target_id = target_id[0]
                        target = await self.client.get_user_info(target_id)
                        __bmode = 'DIRECT'
                        if not ctx.message.server.get_member(target_id): __bmode = 'INDIRECT'
                        if not target: await self.client.say(f"There's noone at **x:`{X:.3f}` y:`{Y:.3f}`** in {cur_PLACE}!"); return
                    # E: Query's empty, since noone's at the given coord
                    except (IndexError, TypeError): await self.client.say(f"There's noone at **x:`{X:.3f}` y:`{Y:.3f}`** in {cur_PLACE}!"); return

                    try: amount = int(raw[3])
                    except (IndexError, TypeError): amount = 1
                # Shots AND amount
                except (IndexError, TypeError):
                    shots = int(raw[0]); amount = int(raw[1])
                    raise IndexError

            else: await self.client.say(":warning: Please use 5-digit or lower coordinates!")       

        # Mob_name, shots provided
        except (TypeError, ValueError):
            print("HEREEE")
            # If there's no current_enemy   ||   # If there is, and the target is the current_enemy
            if cur_MOB == 'n/a' or raw[0] == cur_MOB:
                target = raw[0]; target_id = target
                __mode = 'PVE'
                # Get shots (if available and possible)
                try: 
                    shots = int(raw[1])
                    # try MAGIC
                    try: amount = int(raw[2])
                    except IndexError: amount = 1
                except (IndexError, TypeError): amount = 1 
            # If there is, but the target IS NOT the current_enemy
            elif raw[0] != cur_MOB: 
                await self.client.say(f":warning: Please finish your current fight with `{cur_MOB}`!"); return

        # ... or none of them, then we should randomly pick one :v        
        except IndexError:
            print("HER HERE")
            # Mobs first. If there's no mob in cur_MOB, then randomly pick one
            if cur_MOB == 'n/a':
                target_id = random.choice(await self.quefe(f"SELECT mob_id FROM environ_mob WHERE limit_Ax<{cur_X}<limit_Bx  AND limit_Ay<{cur_Y}<limit_By AND region='{cur_PLACE}';", type='all'))
                target_id = target_id[0]
                target = target_id
                __mode = 'PVE'
            # If there is, use cur_MOB
            else:
                target_id = cur_MOB
                target = target_id
                __mode = 'PVE'     

            if _style == 'PHYSIC':
                # Get shots (if available and possible)
                try: shots = int(raw[0])
                except (IndexError, TypeError): pass
         


        # TARGET CHECK =========================================================
        # (as well as init some variables)

        # Check if target has a ava
        if __mode == 'PVP': 
            # Check if target has a ava     ||      GET TARGET's INFO
            try: t_cur_X, t_cur_Y, t_cur_PLACE, t_combat_HANDLING, t_right_hand, t_left_hand = await self.quefe(f"SELECT cur_X, cur_Y, cur_PLACE, combat_HANDLING, right_hand, left_hand FROM personal_info WHERE id='{target_id}' AND cur_PLACE='{cur_PLACE}';")
            # E: Invalid target, or target's not in the same region
            except TypeError:
                # Checking if target's cur_PLACE is the same as player's
                if not cur_PLACE == t_cur_PLACE: await self.client.say(f":warning: **{ctx.message.author.name}**, you and the target are not in the same region!"); return

                await self.client.say(":warning: Target don't have an ava!"); return

        elif __mode == 'PVE':
            # Check if target is a valid mob       ||       GET TARGET's INFO
            try: t_Ax, t_Ay, t_Bx, t_By, t_name = await self.quefe(f"SELECT limit_Ax, limit_Ay, limit_Bx, limit_By, name FROM environ_MOB WHERE mob_id='{target_id}' AND region='{cur_PLACE}';")
            # E: Invalid target, or target's not in the same region
            except TypeError: await self.client.say(f":warning: There is no `{target_id}` around! Perhap you should check your surrounding..."); return

            # Check if the user is in the mob's diversity
            if cur_X < t_Ax or cur_Y < t_Ay or cur_X > t_Bx or cur_Y > t_By:
                print(t_Ax, t_Ay, t_Bx, t_By, t_name)
                await self.client.say(f":warning: **{ctx.message.author.name}**, you can't engage the mob from your current location!"); return


        # WEAPON CHECK ===========================================================

        # Distance get/check
        if __mode == 'PVP': 
            distance = await self.distance_tools(cur_X, cur_Y, t_cur_X, t_cur_Y)
            if distance > w_rmax or distance < w_rmin: await self.client.say(f":warning: **{ctx.message.author.name}**, the target is out of your weapon's range!"); return
        elif __mode == 'PVE':
            distance = 1                    # There is NO distance in a PVE battle, therefore the accuracy will always be at its lowest

        # AMMUNITION
        if shots > w_firing_rate: await self.client.say(f":warning: **{ctx.message.author.name}**, your weapon cannot perform `{shots}` shots in a row!"); return
        
        # Get ammu's info
        try:
            a_name, a_tags, a_speed, a_rlquery, a_dmg, a_quantity = await self.quefe(f"SELECT name, tags, speed, reload_query, dmg, quantity FROM pi_inventory WHERE item_code='{w_round}' AND user_id='{user_id}';")
            a_tags = a_tags.split(' - ')
        # E: Ammu not found --> Unpack error
        except TypeError: 
            if w_round not in ['am5', 'am6'] :
                a_name = await self.quefe(f"SELECT name FROM model_item WHERE item_code='{w_round}';")
                await self.client.say(f":warning: {ctx.message.author.mention}, OUT OF `{w_round} | {a_name}`!"); return
            else:
                a_name, a_tags, a_speed, a_rlquery, a_dmg = await self.quefe(f"SELECT name, tags, speed, reload_query, dmg FROM model_item WHERE item_code='{w_round}';")


        # Check shots VS quantity of the ammu_type. RELOAD.
        # MAGIC
        if w_round == 'am5':                    # LP -------------------- If kamikaze, halt them
            if LP <= shots*amount:
                await self.client.say(f":warning: **{ctx.message.author.name}**, please don't kill yourself..."); return
            else:
                a_rlquery = a_rlquery.replace('quantity_here', str(shots*amount)).replace('user_id_here', user_id)
                await _cursor.execute(a_rlquery)
        elif w_round == 'am6':                  # STA -------------------- If kamikaze, take the rest of the STA, split it into shots. Then decrease STA
            if STA <= shots*amount:
                amount = STA//shots
                a_rlquery = a_rlquery.replace('quantity_here', str(shots*amount)).replace('user_id_here', user_id)
                await _cursor.execute(a_rlquery)
            else:
                a_rlquery = a_rlquery.replace('quantity_here', str(shots*amount)).replace('user_id_here', user_id)
                await _cursor.execute(a_rlquery)            
        # PHYSIC
        else:
            if a_quantity <= shots:
                shots = a_quantity
                await _cursor.execute(f"DELETE FROM pi_inventory WHERE item_code='{w_round}' AND user_id='{user_id}';")
            else:
                a_rlquery = a_rlquery.replace('quantity_here', str(shots)).replace('user_id_here', user_id)
                await _cursor.execute(a_rlquery)

        # Filtering shots bases on STA remaining. If using physical, STA's decreased        ||          No filtering, while using magic. STA's NOT decreased (for using weapon).
        if _style == 'PHYSIC':
            if shots*w_sta < STA:
                if w_sta >= 100:
                    await _cursor.execute(f"UPDATE personal_info SET LP=LP-20 WHERE id='{user_id}';")
                else: 
                    await _cursor.execute(f"UPDATE personal_info SET LP=LP-10 WHERE id='{user_id}';")
            else:
                shots = STA//w_sta

        
        # PREPARING !!! =======================================================
        # Re-calc randomness
        if combat_HANDLING != 'both':
            w_accu_randomness = w_accu_randomness//2

        # Filtering shots
        bingos = 0
        for i in range(shots):
            if distance < w_accu_range:
                if random.choice(range(w_accu_randomness)) == 0: bingos += 1
            else:
                if random.choice(range(w_accu_randomness*(distance / w_accu_range))) == 0: bingos += 1
        print(f"BINGO: {bingos}")
        shots = bingos
        if shots == 0: 
            await self.client.say(f":interrobang: {ctx.message.author.mention}, you shot a lot but hit nothing...")
            if __bmode == 'INDIRECT': await self.client.send_message(target, f":sos: **Someone** is trying to hurt you, {target.mention}!")
            return

        #dmgdeal = ammu['dmg']*shots

        # PVP use target, with ava_dict =================================
        async def PVP():
            # PVE() already has a deletion. Please don't put this else where
            await self.client.delete_message(ctx.message)

            if distance < 100: a = 1
            else: a = distance/100
            
            # MAGIC
            if _style == 'MAGIC':
                verb = 'curse'
                field = '⠀'*int(shots)*w_stealth*int(a)        # <--- Braille white-space

                for shot in range(shots):
                    while True:
                        hole = random.choice(range(len(field)))
                        if field[hole] == '⠀': break
                    
                    if hole != 0:
                        field = field[:hole] + '·' + field[(hole + 1):]   # OOOOOOOOOOOOO
                    elif hole == len(field):
                        field = field[:hole] + '·'
                    else:
                        field = '·' + field[(hole + 1):]
            # PHYSICAL
            else:
                verb = 'shoot'
                field = '0'*int(shots)*w_stealth*int(a)
                counter_shot = []

                for shot in range(shots):
                    while True:
                        hole = random.choice(range(len(field)))
                        if field[hole] == 'O': break
                    counter_shot.append(str(hole)[-1])
                    
                    if hole != 0:
                        field = field[:hole] + '0' + field[(hole + 1):]   # OOOOOOOOOOOOO
                    elif hole == len(field):
                        field = field[:hole] + '0'
                    else:
                        field = '0' + field[(hole + 1):]


            # Depend on the distance, make the shooter anonymous
            if distance <= 1000: shooter = ctx.message.author.name
            else: shooter = 'Someone'

            # Check if the attack is DIRECT. If not, DM the attacked
            if __bmode == 'DIRECT': 
                inbox = await self.client.say(f""":sos: **{shooter}** is trying to *{verb}* you, {target.mention}!```css
{field}```""")
            else: 
                inbox = await self.client.send_message(target, f""":sos: **{shooter}** is trying to *{verb}* you, {target.mention}!```css
{field}```""")

            # MAGIC
            if _style == 'MAGIC':
                # Generate model moves
                model_moves = field.replace('⠀', '0').replace('·', '1')

                # Wait for response moves       ||        SPEED ('speed') of the bullet aka. <ammu>
                def check(msg):
                    return msg.content.startswith('!')
                
                SPEED = a_speed
                # If the attack is INDIRECT, multiple RECOG by 5
                if __bmode == 'INDIRECT': SPEED = SPEED*5
                msg = await self.client.wait_for_message(timeout=SPEED, author=target, channel=inbox.channel, check=check, content=f"!{model_moves}")
                
                if not msg:
                    dmgdeal = a_dmg*shots*amount

                    # AURA comes in
                    aura_dict = {'FLAME': 'au_FLAME', 'ICE': 'au_ICE', 'DARK': 'au_DARK', 'HOLY': 'au_HOLY'}
                    aura = await self.quefe(f"SELECT {aura_dict[w_aura]} FROM personal_info WHERE id='{user_id}';")
                    t_aura = await self.quefe(f"SELECT {aura_dict[w_aura]} FROM personal_info WHERE id='{target_id}';")
                    # Re-calc dmgdeal
                    try: dmgdeal = int(dmgdeal*t_aura[0]/aura[0])
                    except ZeroDivisionError: dmgdeal = int(dmgdeal*t_aura)

                    await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{target_id}';")
                    await self.client.say(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{t_name}**")
                    if __bmode == 'INDIRECT': await self.client.send_message(target, f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{t_name}**")
                    return
                else:
                    await self.client.say(f"\n--------------------\n:shield: **{target.mention}** has successfully *neutralized* all **{name}**'s spells!")
                    if __bmode == 'INDIRECT': await self.client.send_message(target, f"\n--------------------\n:shield: **{target.mention}** has successfully *neutralized* all **{name}**'s spells!")
                    return
            
                await self.ava_scan(ctx.message, 'life_check')

            # PHYSICAL
            else:
                # Wait for response moves       ||        SPEED ('speed') of the bullet aka. <ammu>
                def check(msg):
                    return msg.content.startswith('!')
                
                SPEED = a_speed
                # If the attack is INDIRECT, multiple RECOG by 5
                if __bmode == 'INDIRECT': SPEED = SPEED*5
                msg = await self.client.wait_for_message(timeout=SPEED, author=target, channel=inbox.channel, check=check)
                
                if not msg:
                    dmgdeal = a_dmg*shots
                    await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{target_id}';")
                    await self.client.say(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{t_name}**")
                    if __bmode == 'INDIRECT': await self.client.send_message(target, f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{t_name}**")
                    return

                # Measuring response moves
                hit_count = 0
                response_content = msg.content[1:]              # Measuring the length of the response
                # Fixing the length of response_content
                response_content = response_content + 'o'*(len(counter_shot) - len(response_content))

                # HIT COUNTER
                for shot, resp in zip(counter_shot, response_content):
                    if shot != resp: hit_count += 1

                # Conduct dealing dmg   ||  Conduct dealing STA dmg
                dmgdeal = a_dmg*hit_count
                if hit_count == 0:
                    await self.client.say(f"\n--------------------\n:shield: **{target.mention}** has successfully *guarded* all **{name}**'s attack!")
                    if __bmode == 'INDIRECT': await self.client.send_message(target, f"\n--------------------\n:shield: **{target.mention}** has successfully *guarded* all **{name}**'s attack!")

                    # Recalculate the dmg, since hit_count == 0                
                    ## Player's dmg
                    dmgdeal = round(a_dmg*len(counter_shot))
                    ## Opponent's def
                    if t_combat_HANDLING == 'both':
                        tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE item_id='{t_left_hand}' AND user_id='{target_id}'")
                        dmgredu = 100 - tw_defend
                    elif t_combat_HANDLING == 'right':
                        tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE item_id='{t_right_hand}' AND user_id='{target_id}'")
                        dmgredu = 100 - tw_defend*2
                    elif t_combat_HANDLING == 'left':
                        tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE item_id='{t_left_hand}' AND user_id='{target_id}'")
                        dmgredu = 100 - tw_defend*2                    
                    # If dmgredu >= 0, all dmg are neutralized
                    if dmgredu < 0:
                        dmgredu = 0

                    await _cursor.execute(f"UPDATE personal_info SET STA=STA-{round(dmgdeal / 100 * dmgredu)} WHERE id='{target_id}';")
                else:
                    # Recalculate the dmg             
                    ## Player's dmg
                    dmgdeal = round(a_dmg*hit_count)
                    ## Opponent's def
                    if t_combat_HANDLING == 'both':
                        try:
                            tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE item_id='{t_left_hand}' AND user_id='{target_id}'")
                            dmgredu = 200 - tw_defend
                        except KeyError: dmgredu = 200
                    elif t_combat_HANDLING == 'right':
                        try:
                            tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE item_id='{t_left_hand}' AND user_id='{target_id}'")
                            dmgredu = 200 - tw_defend*2
                        except KeyError: dmgredu = 200
                    elif t_combat_HANDLING == 'left':
                        try:
                            tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE item_id='{t_left_hand}' AND user_id='{target_id}'")
                            dmgredu = 200 - tw_defend*2
                        except KeyError: dmgredu = 200

                    # If dmgredu > 0, backfire the attacker. If dmgredu >= 0, all dmg are neutralized
                    if dmgredu < 0:
                        await _cursor.execute(f"UPDATE personal_info SET STA=STA-{round(dmgdeal / 200 * abs(dmgredu))*tw_multiplier} WHERE id='{user_id}';")
                        dmgredu = 0

                    # Get dmgdeal, for informing :>
                    dmgdeal = round(dmgdeal / 200 * dmgredu)
                    await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{target_id}';")

                    await self.client.say(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{t_name}**")
                    if __bmode == 'INDIRECT': await self.client.send_message(target, f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{t_name}**")
            
                await self.ava_scan(ctx.message, 'life_check')

        # PVE use target_id, with environ_mob ============================
        async def first_PVE():
            if _style == 'PHYSIC':
                # ------------ USER PHASE   ||   User deal DMG 
                my_dmgdeal = round(a_dmg*len(shots))
                # Inform, of course :>
                await _cursor.execute(f"UPDATE environ_mob SET lp=lp-{my_dmgdeal} WHERE mob_id='{target_id}'; ")
                await self.client.say(f":dagger: **{name}** has dealt *{my_dmgdeal} DMG* to **「`{target_id}` | {t_name}」**!")
            elif _style == 'MAGIC':
                my_dmgdeal = a_dmg*shots*amount

                # AURA comes in
                aura_dict = {'FLAME': 'au_FLAME', 'ICE': 'au_ICE', 'DARK': 'au_DARK', 'HOLY': 'au_HOLY'}
                aura = await self.quefe(f"SELECT {aura_dict[w_aura]} FROM personal_info WHERE id='{user_id}';")
                t_aura = await self.quefe(f"SELECT {aura_dict[w_aura]} FROM environ_mob WHERE mob_id='{target_id}';")
                # Re-calc dmgdeal
                try: dmgdeal = int(my_dmgdeal*t_aura[0]/aura[0])
                except ZeroDivisionError: dmgdeal = int(my_dmgdeal*t_aura[0])

                # Inform, of course :>
                await _cursor.execute(f"UPDATE environ_mob SET lp=lp-{dmgdeal} WHERE mob_id='{target_id}'; ")
                await self.client.say(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **「`{target_id}` | {t_name}」**!")


        if __mode == 'PVP':
            await PVP()
        elif __mode == 'PVE':
            await first_PVE()
            await self.PVE(ctx.message, target_id)
        else: print("<<<<< OH SHIET >>>>>>>")

##########################

    # This function handles the Mob phase
    # Melee PVE     ||      Start the mob phase.
    async def PVE(self, MSG, target_id):
        # Lock-on check. If 'n/a', proceed PVE. If the mob has already locked on other, return.
        try: 
            t_lp, t_name, t_speed, t_str, t_chain = await self.quefe(f"SELECT lp, name, speed, str, chain FROM environ_mob WHERE mob_id='{target_id}' AND lockon='n/a';")
            # Set lock-on, as the target is user_id
            await _cursor.execute(f"UPDATE environ_mob SET lock='{MSG.author.id}' WHERE mob_id='{target_id}';")
        except TypeError: return

        name, LP, STA, MAX_STA, user_id, cur_PLACE, cur_X, cur_Y, cur_MOB, combat_HANDLING, right_hand, left_hand = await self.quefe(f"SELECT name, LP, STA, MAX_STA, id, cur_PLACE, cur_X, cur_Y, cur_MOB, combat_HANDLING, right_hand, left_hand FROM personal_info WHERE id='{MSG.author.id}';")
        message_obj = False
        await self.client.delete_message(MSG)

        async def conclusing():
            # REFRESHING ===========================================
            name, LP, STA, user_id, cur_PLACE = await self.quefe(f"SELECT name, LP, STA, id, cur_PLACE FROM personal_info WHERE id='{MSG.author.id}';")
            #name, LP, STA, MAX_STA, user_id, cur_PLACE, cur_X, cur_Y, cur_MOB, combat_HANDLING, right_hand, left_hand = await self.quefe(f"SELECT name, LP, STA, MAX_STA, id, cur_PLACE, cur_X, cur_Y, cur_MOB, combat_HANDLING, right_hand, left_hand FROM personal_info WHERE id='{MSG.author.id}';")
            t_lp, t_name, t_speed = await self.quefe(f"SELECT lp, name, speed FROM environ_mob WHERE mob_id='{target_id}';")
            #t_lp, t_name, t_speed, t_str, t_chain = await self.quefe(f"SELECT lp, name, speed, str, chain FROM environ_mob WHERE mob_id='{target_id}';")


            if not await self.ava_scan(MSG, type='life_check'):
                return False
            if t_lp <= 0:
                await self.client.say(f"<:rip:524893132916129814> **{t_name}** is dead.")
                
                # Add one to the collection
                type = await vanishing()

                # If query effect zero row
                if await _cursor.execute(f"UPDATE pi_mobs_collection SET {type}={type}+1 WHERE user_id='{user_id}' AND region='{cur_PLACE}';") == 0:
                    await _cursor.execute(f"INSERT INTO pi_mobs_collection (user_id, region, {type}) VALUES ('{user_id}', '{cur_PLACE}', 1);")

                # Erase the current_enemy lock on off the target_id
                await _cursor.execute(f"UPDATE personal_info SET cur_MOB='n/a' WHERE id='{user_id}';")
                return False 

            msg = f"--------------------\n**{name}:** `{LP}` LP  |  `{STA}` STA\n**{t_name}:** `{t_lp}` LP\n--------------------"
            return msg

        async def vanishing():
            # Looting
            mob_code, rewards, reward_query, region, t_Ax, t_Ay, t_Bx, t_By = await self.quefe(f"SELECT mob_code, rewards, reward_query, region, limit_Ax, limit_Ay, limit_Bx, limit_By FROM environ_mob WHERE mob_id='{target_id}';")
            await _cursor.execute(reward_query.replace('user_id_here', MSG.author.id))

            await self.client.say(f"<:chest:507096413411213312> Congrats **{MSG.author.mention}**, you've received **{rewards.replace(' | ', '** and **')}** from **「`{target_id}` | {t_name}」**!")
            
            # Get the <mob> prototype
            name, branch, lp, str, chain, speed, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY = await self.quefe(f"SELECT name, branch, lp, str, chain, speed, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY FROM model_mob WHERE mob_code='{mob_code}';")
            rewards = rewards.split(' | ')

            # Generating rewards
            status = []; objecto = []; bingo_list = []
            for reward in rewards:
                stuff = reward.split(' - ')
                if random.choice(range(int(stuff[2]))) == 0:
                    if stuff[0] == 'money': bingo_list.append(f"${stuff[1]}")

                    # Stats reward
                    if stuff[0] in ['money']: status.append(f"{stuff[0]}={stuff[0]}+{int(stuff[1])}")
                    # ... other shit
                    else: 
                        # Get item/weapon's info
                        temp = await self.quefe(f"SELECT * FROM model_item WHERE item_code='{stuff[0]}';")
                        # SERI / UN-SERI check
                        # SERI
                        if 'inconsumbale' in temp[2].split(' - '):
                            objecto.append(f"""INSERT INTO pi_inventory VALUE ("user_id_here", {', '.join(temp)});""")
                        # UN-SERI
                        else: objecto.append(f"""UPDATE pi_inventory SET quantity=quantity+{random.choice(range(stuff[1]))} WHERE user_id="user_id_here" AND item_code='{stuff[0]}';""")
            stata = f"""UPDATE personal_info SET {', '.join(status)} WHERE id="user_id_here"; """
            rewards_query = f"{stata} {' '.join(objecto)}"

            # Remove the old mob from DB
            await _cursor.execute(f"DELETE FROM environ_mob WHERE mob_id='{target_id}';")

            # Insert the mob to DB
            await _cursor.execute(f"""INSERT INTO environ_mob VALUES (0, 'mob', '{mob_code}', "{name}", '{branch}', {lp}, {str}, {chain}, {speed}, {au_FLAME}, {au_ICE}, {au_DARK}, {au_HOLY}, '{' | '.join(bingo_list)}', '{rewards_query}', '{region}', {t_Ax}, {t_Ay}, {t_Bx}, {t_By}, 'n/a');""")
            counter_get = await self.quefe("SELECT MAX(id_counter) FROM environ_mob")
            await _cursor.execute(f"UPDATE environ_mob SET mob_id='mob.{counter_get[0]}' WHERE id_counter={counter_get[0]};")

            return branch

        # ------------ MOB PHASE    ||   Mobs attack, user defend
        async def battle(message_obj):

            async def attack():
                mmoves = [random.choice(['a', 'd', 'b']) for move in range(t_chain)]
                
                # Decoding moves, as well as checking the moves. Get the counter_move
                counter_mmove = []
                for move in mmoves:
                    if move == 'a': counter_mmove.append('d')
                    elif move == 'd': counter_mmove.append('b')
                    elif move == 'b': counter_mmove.append('a')

                dmg = t_str
                return dmg, mmoves, counter_mmove

            # ======================================================

            if not await conclusing(): return False

            dmg, mmove, counter_mmove = await attack()

            await self.client.say(f"**{t_name}** performed an attack on {MSG.author.mention}: `{' '.join(mmove)}`")

            # Wait for response moves
            def check(msg):
                return msg.content.startswith('!')
            
            msg = await self.client.wait_for_message(timeout=t_speed, author=MSG.author, channel=MSG.channel, check=check)            #timeout=10
            try: await self.client.delete_message(msg)
            except: pass

            if not msg: 
                dmgdeal = round(dmg*len(mmove))
                await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                pack_1 = f":dagger: **「`{target_id}` | {t_name}」** has dealt *{dmgdeal} DMG* to **{MSG.author.mention}**!"
                pack_2 = await conclusing()
                if pack_2: msg_pack = await self.client.send_message(MSG.channel, f"{pack_1}\n{pack_2}")
                else: msg_pack = False
                if message_obj: await self.client.delete_message(message_obj)
                return msg_pack
            # Fleeing method    ||     Success rate base on user's current STA
            elif msg.content == '!flee':
                if STA <= 0: rate = MAX_STA//1 + 1
                else: rate = MAX_STA//STA + 1
                # Succesfully --> End battling session
                if random.choice(range(int(rate))) == 0:
                    await self.client.say(f"{MSG.author.mention}, you've successfully escape from the mob!")
                    # Erase the current_enemy lock on off the target_id
                    await _cursor.execute(f"UPDATE personal_info SET cur_MOB='n/a' WHERE id='{user_id}'; ")
                    return False
                # Fail ---> Continue, with the consequences
                else:
                    dmgdeal = round(dmg*len(mmove))*2
                    await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                    pack_1 = f":dagger::dagger: As **{name}** failed to flee, **「`{target_id}` | {t_name}」** has dealt a critical DMG of *{dmgdeal}*!"
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
                    await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                    pack_1 = f":dagger::dagger: As **{name}** failed to switch, **「`{target_id}` | {t_name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await self.client.send_message(MSG.channel, f"{pack_1}\n{pack_2}")
                    else: msg_pack = False
                    if message_obj: await self.client.delete_message(message_obj)
                    return msg_pack
                # E: Different region
                try:
                    sw_cur_PLACE, sw_cur_X, sw_cur_Y = await self.quefe(f"SELECT cur_PLACE, cur_X, cur_Y FROM personal_info WHERE id='{switchee.id}'; ")
                    if cur_PLACE != sw_cur_PLACE: 
                        await self.client.say(f":warning: {switchee.mention} and {MSG.author.mention}, you have to be in the same region!")
                        dmgdeal = round(dmg*len(mmove))*2
                        await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                        pack_1 = f":dagger::dagger: As **{name}** failed to switch, **「`{target_id}` | {t_name}」** has dealt a critical DMG of *{dmgdeal}*!"
                        pack_2 = await conclusing()
                        if pack_2: msg_pack = await self.client.send_message(MSG.channel, f"{pack_1}\n{pack_2}")
                        else: msg_pack = False                       
                        if message_obj: await self.client.delete_message(message_obj)
                        return msg_pack                        
                ## E: Switchee doesn't have ava
                except TypeError:
                    await self.client(f":warning: User **{switchee.name}** doesn't have an *ava*!")
                    dmgdeal = round(dmg*len(mmove))*2
                    await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                    pack_1 = f":dagger::dagger: As **{name}** failed to switch, **「`{target_id}` | {t_name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await self.client.send_message(MSG.channel, f"{pack_1}\n{pack_2}")
                    else: msg_pack = False                       
                    if message_obj: await self.client.delete_message(message_obj)
                    return msg_pack                                            
                # E: Out of switching_range
                if await self.distance_tools(cur_X, cur_Y, sw_cur_X, sw_cur_Y) > 5:
                    await self.client(f":warning: {switchee.mention} and {MSG.author.mention}, you can only switch within *5 metres*!")
                    dmgdeal = round(dmg*len(mmove))*2
                    await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                    pack_1 = f":dagger::dagger: As **{name}** failed to switch, **「`{target_id}` | {t_name}」** has dealt a critical DMG of *{dmgdeal}*!"
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
                    await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                    pack_1 = f":dagger::dagger: As **{name}** failed to switch, **「`{target_id}` | {t_name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await self.client.send_message(MSG.channel, f"{pack_1}\n{pack_2}")
                    else: msg_pack = False                     
                    if message_obj: await self.client.delete_message(message_obj)
                    return msg_pack                        
                # E: Wrong user
                if MSG.author not in switch_resp.mentions:
                    dmgdeal = round(dmg*len(mmove))*2
                    await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                    pack_1 = f":dagger::dagger: As **{name}** failed to switch, **「`{target_id}` | {t_name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await self.client.send_message(MSG.channel, f"{pack_1}\n{pack_2}")
                    else: msg_pack = False                    
                    if message_obj: await self.client.delete_message(message_obj)
                    return msg_pack                                
                
                # Proceed duo-teleportation
                await self.tele_procedure(cur_PLACE, switchee.id, cur_X, cur_Y)
                await self.tele_procedure(cur_PLACE, user_id, sw_cur_X, sw_cur_Y)
                # End the switcher PVE-session
                ## Remove the current_enemy lock-on of the switcher
                await _cursor.execute(f"UPDATE personal_info SET cur_MOB='n/a' WHERE id='{user_id}'; ")
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
                dmgdeal = t_str*len(counter_mmove)

                if STA > 0:
                    # Deal
                    if combat_HANDLING == 'both':
                        w_defend = await self.quefe(f"SELECT defend FROM pi_inventory WHERE item_id='{left_hand}' AND user_id='{user_id}'"); w_defend = w_defend[0]
                        dmgredu = 100 - w_defend
                    elif combat_HANDLING == 'right':
                        w_defend = await self.quefe(f"SELECT defend FROM pi_inventory WHERE item_id='{right_hand}' AND user_id='{user_id}'"); w_defend = w_defend[0]
                        dmgredu = 100 - w_defend*2
                    elif combat_HANDLING == 'left':
                        w_defend = await self.quefe(f"SELECT defend FROM pi_inventory WHERE item_id='{left_hand}' AND user_id='{user_id}'"); w_defend = w_defend[0]
                        dmgredu = 100 - w_defend*2
                    # Check STA
                    tem = round(dmgdeal / 100 * dmgredu)
                    if tem > STA:
                        await _cursor.execute(f"UPDATE personal_info SET STA=0 WHERE id='{user_id}';")
                    else: await _cursor.execute(f"UPDATE personal_info SET STA=STA-{tem} WHERE id='{user_id}';")
                
                # Inform
                pack_1 = f"\n--------------------\n:shield: {MSG.author.mention} has successfully *guarded* all **「`{target_id}` | {t_name}」**'s attack!"
                pack_2 = await conclusing()
                if pack_2: msg_pack = await self.client.send_message(MSG.channel, f"{pack_1}\n{pack_2}")
                else: msg_pack = False
                if message_obj: await self.client.delete_message(message_obj)
                return msg_pack

            else:
                dmgdeal = t_str*hit_count 

                # Deal
                if combat_HANDLING == 'both':
                    w_defend = await self.quefe(f"SELECT defend FROM pi_inventory WHERE item_id='{left_hand}' AND user_id='{user_id}'"); w_defend = w_defend[0]
                    dmgredu = 200 - w_defend
                elif combat_HANDLING == 'right':
                    w_defend = await self.quefe(f"SELECT defend FROM pi_inventory WHERE item_id='{right_hand}' AND user_id='{user_id}'"); w_defend = w_defend[0]
                    dmgredu = 200 - w_defend
                elif combat_HANDLING == 'left':
                    w_defend = await self.quefe(f"SELECT defend FROM pi_inventory WHERE item_id='{left_hand}' AND user_id='{user_id}'"); w_defend = w_defend[0]
                    dmgredu = 200 - w_defend

                # Get dmgdeal for informing :>
                dmgdeal = round(dmgdeal / 200 * dmgredu)
                await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}';")

                # Inform
                pack_1 = f"\n--------------------\n:dagger: **「`{target_id}` | {t_name}」** has dealt *{dmgdeal} DMG* to **{MSG.author.mention}**!"
                pack_2 = await conclusing()
                if pack_2: msg_pack = await self.client.send_message(MSG.channel, f"{pack_1}\n{pack_2}")
                else: msg_pack = False
                if message_obj: await self.client.delete_message(message_obj)
                return msg_pack

        if target_id != cur_MOB:
            await _cursor.execute(f"UPDATE personal_info SET cur_MOB='{target_id}' WHERE id='{user_id}'; ")

            # Init the fight
            message_obj = await battle(message_obj)
            while isinstance(message_obj, discord.message.Message):
                message_obj = await battle(message_obj)
            if message_obj: 
                await self.PVE(message_obj[0], message_obj[1])
        else:
            await _cursor.execute(f"UPDATE personal_info SET cur_MOB='{target_id}' WHERE id='{user_id}'; ")

##########################

#    @commands.command(pass_context=True, aliases=['>cast'])
#    @commands.cooldown(1, 60, type=BucketType.user)
#    async def avacast(self, ctx, *args):

##########################




# ============= TACTICAL ==============
    @commands.command(pass_context=True, aliases=['>rad'])
    @commands.cooldown(1, 60, type=BucketType.user)
    async def avaradar(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        cur_PLACE, cur_X, cur_Y = await self.quefe(f"SELECT cur_PLACE, cur_X, cur_Y FROM personal_info WHERE id='{ctx.message.author.id}';")
        xrange = 0.1; yrange = 0.1
        try: 
            # Check if the range is off-limit
            # Get xrange
            if float(args[0])/1000 <= xrange: xrange = float(args[0])/1000
            # Get yrange
            try:
                if float(args[1])/1000 <= yrange: yrange = float(args[1])/1000
            except IndexError: yrange = xrange
        except (IndexError, ValueError): pass

        # Pacing through the required field
        coords_list = await self.quefe(f"SELECT cur_X, cur_Y FROM personal_info WHERE {cur_X - xrange}<=cur_X AND cur_X<={cur_X + xrange} AND {cur_Y - yrange}<=cur_Y AND cur_Y<={cur_Y + yrange};", type='all')
        coords_list = list(coords_list)
        # Remove user's own id
        coords_list.remove((cur_X, cur_Y))

        if not coords_list: await self.client.say(f":satellite: No sign of life in `{xrange*1000}m x {yrange*1000}m` square radius around us..."); return

        def makeembed(top, least, pages, currentpage):
            line = ''

            line = "**< < < < < < < < < < < < < < < < · > > > > > > > > > > > > > > > > >**\n" 
            for coords in coords_list[top:least]:
                line = line + f"\n◉ `X`|**{coords[0]} · `Y`|**{coords[1]}**\n"

            reembed = discord.Embed(title = f":satellite: `{xrange*2*1000}m x {yrange*2*1000}m` square radius, with user as the center", colour = discord.Colour(0x011C3A), description=line)
            reembed.set_footer(text=f"Currently at `{cur_X}` - `{cur_Y}` - `{cur_PLACE}` || Page {currentpage} of {pages}")
            return reembed
            #else:
            #    await client.say("*Nothing but dust here...*")
        
        async def attachreaction(msg):
            await self.client.add_reaction(msg, "\U000023ee")    #Top-left
            await self.client.add_reaction(msg, "\U00002b05")    #Left
            await self.client.add_reaction(msg, "\U000027a1")    #Right
            await self.client.add_reaction(msg, "\U000023ed")    #Top-right

        pages = len(coords_list)//10
        if len(coords_list)%10 != 0: pages += 1
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
    @commands.cooldown(1, 5, type=BucketType.user)    
    async def avatele(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        cur_PLACE, cur_X, cur_Y = await self.quefe(f"SELECT cur_PLACE, cur_X, cur_Y FROM personal_info WHERE id='{ctx.message.author.id}';")
        if not args: await self.client.say(f":fireworks: {ctx.message.author.mention}, you are currently at **x:`{cur_X:.3f}` y:`{cur_Y:.3f}`** in `{cur_PLACE}`|**{self.environ[cur_PLACE]['name']}**"); return

        # COORD
        try:
            x = int(args[0])/1000; y = int(args[1])/1000
            if len(args[0]) <= 5 and len(args[1]) <= 5:
                if x > self.environ[cur_PLACE]['info']['border'][0]: x = self.environ[cur_PLACE]['info']['border'][0]
                if y > self.environ[cur_PLACE]['info']['border'][1]: y = self.environ[cur_PLACE]['info']['border'][1]
                if x < 0: x = -1
                if y < 0: y = -1
                # Check if <distance> is provided
                try:
                    distance = int(args[2])
                    prior_x = x; prior_y = y
                    x, y = await self.distance_tools(cur_X, cur_Y, x, y, distance=distance, type='d-c')
                    # Coord check
                    if x > self.environ[cur_PLACE]['info']['border'][0]: x = self.environ[cur_PLACE]['info']['border'][0]
                    if y > self.environ[cur_PLACE]['info']['border'][1]: y = self.environ[cur_PLACE]['info']['border'][1]
                    if x < 0: x = 0
                    if y < 0: y = 0
                except (IndexError, ValueError): pass
                
                # Procede teleportation
                await self.tele_procedure(cur_PLACE, ctx.message.author.id, x, y)

                # Informmmm :>
                try: await self.client.say(f":round_pushpin: Successfully move `{distance}m` toward **x:`{prior_x:.3f}` y: `{prior_y:.3f}`**\n:fireworks: Now you're at **x:`{x:.3f}` y:`{y:.3f}`** in `{cur_PLACE}`|**{self.environ[cur_PLACE]['name']}**!")
                except NameError: await self.client.say(f":round_pushpin: Successfully move to **x:`{x:.3f}` y:`{y:.3f}`** in `{cur_PLACE}`|**{self.environ[cur_PLACE]['name']}**!")
            else: await self.client.say(f":warning: Please use 5-digit coordinates!"); return
        except IndexError: await self.client.say(f":warning: Out of map's range!"); return

        # PLACE
        except (KeyError, ValueError):
            if not args[0] in list(self.environ.keys()): await self.client.say(f"**{args[0]}**... There is no such place here, perhap it's from another era?"); return

            if cur_X <= 1 and cur_Y <=1:
                await _cursor.execute(f"UPDATE personal_info SET cur_PLACE='{args[0]}' WHERE id='{ctx.message.author.id}';")
                await self.client.say(f":round_pushpin: Successfully move to `{args[0]}`|**{self.environ[args[0]]['name']}**!")
            else: await self.client.say(f":warning: You can only travel between regions inside **Peace Belt**!"); return

    @commands.command(pass_context=True, aliases=['>mdist'])
    async def measure_dist(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        cur_X, cur_Y = await self.quefe(f"SELECT cur_X, cur_Y FROM personal_info WHERE id='{ctx.message.author.id}';")

        try:
            distance = await self.distance_tools(cur_X, cur_Y, int(args[0])/1000, int(args[1])/1000)
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

    async def ava_scan(self, MSG, type='all', target_id='n/a'):
        # Get target
        #try: target = await self.client.get_user_info(target_id)
        #except discordErrors.NotFound:
        target = MSG.author
        target_id = target.id

        # Status check
        try: 
            LP, MAX_LP, STA, MAX_STA, cur_X, cur_Y, status, dob = await self.quefe(f"SELECT LP, MAX_LP, STA, MAX_STA, cur_X, cur_Y, status, dob FROM personal_info WHERE id='{target_id}'")
        except TypeError: await self.client.send_message(MSG.channel, f"{target.mention}, you don't have an *avatar*. Use `-incarnate` to create one."); return
        if status == 'DEAD': 
            #if target_id == MSG.author.id: await self.client.send_message(MSG.channel, f"<:rip:524893132916129814> You. Are. Dead, **{target.mention}**. Have a nice day!"); return
            #else: await self.client.send_message(MSG.channel, f"<:rip:524893132916129814> The target **{target.name}** was dead, **{MSG.author.mention}**. *Press F to pay respect.*"); return
            await self.client.send_message(MSG.channel, f"<:rip:524893132916129814> You. Are. Dead, **{target.mention}**. Have a nice day!"); return

        # Time check
        if type == 'all':
            time_pack = await self.client.loop.run_in_executor(None, self.time_get)

            await _cursor.execute(f"UPDATE personal_info SET age={time_pack[0] - int(dob.split(' - ')[2])} WHERE id='{target_id}';")
            return True
        # STA, LP, sign_in check
        elif type == 'life_check':
            if cur_X < 0 or cur_Y < 0: await self.client.say(f":warning: {target.mention}, please **sign in**. Just `-tele` somewhere you like and you'll be signed in the world's map."); return False
            if STA < 0: await _cursor.execute(f"UPDATE personal_info SET LP=LP-{abs(STA)}, STA=0 WHERE id='{target_id}';")
            if LP <= 0:
                # Status reset
                reviq = f"UPDATE personal_info SET status='DEAD', cur_PLACE='region.0', cur_X=-1, cur_Y=-1, cur_MOB='n/a', cur_USER='n/a', right_hand='ar13', left_hand='ar13', money=0, perks=0, deaths=deaths+1 WHERE id='{target_id}';"
                # Remove FULL and ONGOING quests
                reviq = reviq + f" DELETE FROM pi_quests WHERE user_id='{target_id}' AND stats IN ('FULL', 'ONGOING');"
                # Remove all items but ar13|Fist (Default)
                reviq = reviq + f" DELETE FROM pi_inventory WHERE user_id='{target_id}' AND item_code!='ar13';"
                await _cursor.execute(reviq)

                await self.client.say(f"<:rip:524893132916129814> {target.mention}, you are dead. Please re-incarnate.")
                return False
            return True
        # Readjust the incorrect value
        elif type == 'normalize':
            query = ''
            if STA > MAX_STA: query = query + f"UPDATE personal_info SET STA=MAX_STA WHERE id='{target_id}';"
            if LP > MAX_LP: query = query + f"UPDATE personal_info SET LP=MAX_LP WHERE id='{target_id}';"
            try: await _cursor.execute(query)
            except mysqlError.InternalError: pass
            return True

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
        await _cursor.execute(f"UPDATE personal_info SET cur_X={desti_x}, cur_Y={desti_y} WHERE id='{user_id}';")
        # Assign the coord to ava
        #self.ava_dict[user_id]['realtime_zone']['current_coord'] = [desti_x, desti_y]

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

    @commands.command(pass_context=True)
    @check_id()
    async def avaava_giveitem(self, ctx, *args):
        raw = list(args)

        try:
            storage = raw[0]
            item_code = raw[1]
            try: quantity = int(raw[2])
            except IndexError: quantity = 1
        except IndexError: await self.client.say(f":warning: Args missing")

        # GET ITEM INFO
        try:
            if storage == 'it': 
                tags = await self.quefe(f"""SELECT name, tags, price, quantity FROM model_item WHERE item_code='{item_code}';""")
                i_tags = tags[0].split(' - ')
        # E: Item code not found
        except TypeError: await self.client.say(":warning: Item_code/Item_id not found!"); return

        # ITEM
        if storage == 'it':
            # CONSUMABLE
            if 'consumable' in i_tags:
                # Create item in inventory. Ignore the given quantity please :>
                await _cursor.execute(f"INSERT INTO pi_inventory SELECT 0, '{ctx.message.author.id}', item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, infuse_query, quantity, price, dmg, stealth, evo, aura, illulink FROM model_item WHERE item_code='{item_code}';")
                # (MODEL FOR QUERY RECORD-TRANSFERING) ------- await _cursor.execute(f"INSERT INTO pi_inventory SELECT 0, {ctx.message.author.id}, item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, quantity, price, dmg, stealth FROM model_item WHERE item_code='{item_code}';")

            # INCONSUMABLE
            else:
                # Increase item_code's quantity
                if await _cursor.execute(f"UPDATE pi_inventory SET quantity=quantity+{quantity} WHERE user_id='{ctx.message.author.id}' AND item_code='{item_code}';") == 0:
                    # E: item_code did not exist. Create one, with given quantity
                    await _cursor.execute(f"INSERT INTO pi_inventory SELECT 0, '{ctx.message.author.id}', item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, infuse_query, {quantity}, price, dmg, stealth, evo, aura, illulink FROM model_item WHERE item_code='{item_code}';")

        # INGREDIENT
        elif storage == 'ig':
            # UN-SERIALIZABLE
            # Increase item_code's quantity
            if await _cursor.execute(f"UPDATE pi_inventory SET quantity=quantity+{quantity} WHERE user_id='{ctx.message.author.id}' AND item_code='{item_code}';") == 0:
                # E: item_code did not exist. Create one, with given quantity
                await _cursor.execute(f"INSERT INTO pi_inventory SELECT 0, {ctx.message.author.id}, ingredient_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, infuse_query, quantity, price, dmg, stealth, evo, aura, illulink FROM model_ingredient WHERE ingredient_code='{item_code}';")

        await self.client.say(":white_check_mark: Done.")

    async def quefe(self, query, args=None, type='one'):
        """args ---> tuple"""

        await _cursor.execute(query, args=args)
        if type == 'all': resu = await _cursor.fetchall()
        else: resu = await _cursor.fetchone()
        return resu

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

    async def data_plugin(self):

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


        async def world_built():
            for floor in list(self.environ.keys()):
                
                # ----------- MOB/BOSS initialize ------------
                for mob_code, pack in self.environ[floor]['info']['diversity'].items():
                    # Quantity of kind in a diversity check
                    qk = await self.quefe(f"SELECT COUNT(*) FROM environ_mob WHERE mob_code='{mob_code}' AND region='{floor}';")
                    if qk[0] == pack[0]: continue
                    elif qk[0] < pack[0]: pack[0] -= qk[0]
                    
                    # Get the <mob> prototype
                    name, branch, lp, str, chain, speed, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY = await self.quefe(f"SELECT name, branch, lp, str, chain, speed, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY FROM model_mob WHERE mob_code='{mob_code}';")
                    rewards = rewards.split(' | ')
                    
                    # Mass production
                    for count in range(pack[0]):
                        # Generating rewards
                        status = []; objecto = []; bingo_list = []
                        for reward in rewards:
                            stuff = reward.split(' - ')
                            if random.choice(range(int(stuff[2]))) == 0:
                                if stuff[0] == 'money': bingo_list.append(f"${stuff[1]}")

                                # Stats reward
                                if stuff[0] in ['money']: status.append(f"{stuff[0]}={stuff[0]}+{int(stuff[1])}")
                                # ... other shit
                                else: 
                                    # Get item/weapon's info
                                    temp = await self.quefe(f"SELECT * FROM model_item WHERE item_code='{stuff[0]}';")
                                    # SERI / UN-SERI check
                                    # SERI
                                    if 'inconsumbale' in temp[2].split(' - '):
                                        objecto.append(f"""INSERT INTO pi_inventory VALUE ("user_id_here", {', '.join(temp)});""")
                                    # UN-SERI
                                    else: objecto.append(f"""UPDATE pi_inventory SET quantity=quantity+{random.choice(range(stuff[1]))} WHERE user_id="user_id_here" AND item_code='{stuff[0]}';""")
                        stata = f"""UPDATE personal_info SET {', '.join(status)} WHERE id="user_id_here"; """
                        rewards_query = f"{stata} {' '.join(objecto)}"

                        # Insert the mob to DB
                        await _cursor.execute(f"""INSERT INTO environ_mob VALUES (0, 'mob', '{mob_code}', "{name}", '{branch}', {lp}, {str}, {chain}, {speed}, {au_FLAME}, {au_ICE}, {au_DARK}, {au_HOLY}, '{' | '.join(bingo_list)}', '{rewards_query}', '{floor}', {pack[1]}, {pack[2]}, {pack[3]}, {pack[4]}, 'n/a');""")
                        counter_get = await self.quefe("SELECT MAX(id_counter) FROM environ_mob")
                        await _cursor.execute(f"UPDATE environ_mob SET mob_id='mob.{counter_get[0]}' WHERE id_counter={counter_get[0]};")

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

        async def rtzone_refresh():
            #fix_list = await self.quefe("SELECT id FROM personal_info WHERE cur_MOB != 'n/a' OR cur_USER != 'n/a';", type='all')
            #for user_id in fix_list:
            await _cursor.execute(f"UPDATE personal_info SET cur_MOB='n/a', cur_USER='n/a';")

        await world_built()
        await rtzone_refresh()
        
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

        prote_codes = {'Iris': 'av0', 'Zoey': 'av1', 'Ardena': 'av2'}        

        def ImageGen_supporter(char, rawimg):
            img = Image.open(f'C:/Users/DELL/Desktop/bot_cli/data/profile/char/{char}/{rawimg}').convert('RGBA')
            self.prote_lib[prote_codes[char]].append(img)

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
            self.prote_lib[prote_codes[char]] = []
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



















