import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors

import asyncio
import random
import json
import math
import copy
import tempfile
import re
import traceback
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from io import BytesIO
from os import listdir

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio
from imgurpython import ImgurClient
from functools import partial
import numpy as np
import aiomysql
import redis
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
        return ctx.message.author.id == 214128381762076672
    return commands.check(inner)

class avasoul:
    def __init__(self, client):
        self.client = client
        self.ava_dict = {}
        self.prote_lib = {}
        self.jobs_dict = {}
        self.trigg = {}
        self.data_ARSENAL = {}; self.data_SUPPLY = {}; self.data_AMMU = {}
        self.data = {}
        self.environ = {}
        self.client_id = '594344297452325'
        self.client_secret = '2e29f3c50797fa6d5aad8b5bef527b214683a3ff'
        self.imgur_client = ImgurClient(self.client_id, self.client_secret)
        self.thepoof = 0

        self.biome = {'SAVANNA': 'https://imgur.com/qc1NNIu.png',
                    'JUNGLE': 'https://imgur.com/3j786qW.png',
                    'DESERT': 'https://imgur.com/U0wtRU7.png',
                    'RUIN': 'https://imgur.com/O8rHzCR.png',
                    'FROST': 'https://imgur.com/rjwiDU4.png',
                    'MOUNTAIN': 'https://imgur.com/cxwSH7m.png',
                    'OCEAN': 'https://imgur.com/fQFO2b4.png'}

    async def on_ready(self):
        if self.thepoof: return
        await self.client.loop.run_in_executor(None, self.avatars_plugin)
        await self.data_plugin()
        await self.client.loop.run_in_executor(None, self.avatars_plugin_2)
        #await self.intoSQL()
        print(self.thepoof)
        self.thepoof += 1
        await self.prote_plugin()

    @commands.command()
    @check_id()
    async def spinthewheel(self, ctx):
        await self.prote_plugin()

    async def __cd_check(self, MSG, cmd_tag, warn):
        cdkey = cmd_tag + str(MSG.author.id)
        if redio.exists(cdkey):
            sec = await self.client.loop.run_in_executor(None, redio.ttl, cdkey)
            await MSG.channel.send(f"{warn} Please wait `{timedelta(seconds=int(sec))}`."); return False
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

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    # =====================================================================================================================

    #@commands.command(pass_context=True)
    #async def milestime(self, ctx):
    #    self.client.STONE = datetime.now()
    #    self.data_updating()

    @commands.command()
    @check_id()
    async def avauda(self, ctx):

        # AVATARs
        temp = await self.quefe(f"SELECT avatar_id FROM model_avatar", type='all')
        avas = [i[0] for i in temp]

        user_ids = await self.quefe("SELECT id FROM personal_info", type='all')
        master_que = ''
        for pack in user_ids:
            que = ''
            for ava in avas:
                que = que + f"INSERT INTO pi_avatars (user_id, avatar_id) SELECT '{pack[0]}', '{ava}' WHERE NOT EXISTS (SELECT * FROM pi_avatars WHERE user_id='{pack[0]}' AND avatar_id='{ava}'); "
            master_que = master_que + que
        await _cursor.execute(master_que)

        # BACKGROUNDs
        temp = await self.quefe(f"SELECT bg_code FROM model_background", type='all')
        avas = [i[0] for i in temp]

        user_ids = await self.quefe("SELECT id FROM personal_info", type='all')
        master_que = ''
        for pack in user_ids:
            que = ''
            for ava in avas:
                que = que + f"INSERT INTO pi_backgrounds (user_id, bg_code) SELECT '{pack[0]}', '{ava}' WHERE NOT EXISTS (SELECT * FROM pi_backgrounds WHERE user_id='{pack[0]}' AND bg_code='{ava}'); "
            master_que = master_que + que
        await _cursor.execute(master_que)

        await ctx.send(":white_check_mark:")


    # =====================================================================================================================


    @commands.command(aliases=['skt'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def sekaitime(self, ctx):
        year, month, day, hour, minute = await self.client.loop.run_in_executor(None, self.time_get)
        calendar_format = {'month': {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}}
        a = ['st', 'nd', 'rd']
        if day%10 in [1, 2, 3]:
            postfix = a[(day%10) - 1]
        else: postfix = 'th'
        await ctx.send(f"__=====__ `{hour:02d}:{minute:02d}` :calendar_spiral: {calendar_format['month'][month]} {day}{postfix}, {year} __=====__")

    @commands.command(aliases=['worldinfo'])
    @commands.cooldown(1, 30, type=BucketType.user)
    async def sekaiinfo(self, ctx):
        users = await self.quefe(f"SELECT COUNT(id) FROM personal_info;")
        races = await self.quefe(f"SELECT COUNT(race_code) FROM model_race;")
        c_quests = await self.quefe(f"SELECT COUNT(user_id) FROM pi_quests;")
        quests = await self.quefe(f"SELECT COUNT(quest_code) FROM model_quest;")
        animals = await self.quefe(f"SELECT COUNT(ani_code) FROM model_animal;")
        c_mobs = await self.quefe(f"SELECT COUNT(id_counter) FROM environ_mob;")
        mobs = await self.quefe(f"SELECT COUNT(mob_code) FROM environ_diversity;")
        formulas = await self.quefe(f"SELECT COUNT(formula_code) FROM model_formula;")
        ingredients = await self.quefe(f"SELECT COUNT(ingredient_code) FROM model_ingredient;")
        items = await self.quefe(f"SELECT COUNT(item_code) FROM model_item;")
        p_items = await self.quefe(f"SELECT COUNT(item_id) FROM pi_inventory;")

        year, month, day, hour, minute = await self.client.loop.run_in_executor(None, self.time_get)

        reembed = discord.Embed(title='**T H E  P R A L A E Y R**', description=f"```Structured by 5 different regions, Pralaeyr has lasted for {year} years, {month} months, {day} days, {hour} hours and {minute} minutes```", colour = discord.Colour(0x011C3A))
        reembed.add_field(name=":couple: Population", value=f"· `{users[0]}`, with `{races[0]}` different races.")
        reembed.add_field(name=":smiling_imp: Mobs and Animals", value=f"· `{c_mobs[0]}` alive mobs, with `{mobs[0]}` different kind of mobs.\n· `{animals[0]}` kind of animals.")
        reembed.add_field(name=":package: Items and Ingredients", value=f"· `{p_items[0]}` current items, with `{ingredients[0]}` kind of ingredients and `{items[0]}` kind of items.")
        reembed.add_field(name=":tools: Formulas and Quests", value=f"· `{formulas[0]}` formulas.\n· `{c_quests[0]}` current quests, with `{quests[0]}` different kind of quests.")

        await ctx.send(embed=reembed)

    @commands.command()
    async def incarnate(self, ctx, *args):
        id = str(ctx.message.author.id); name = ctx.message.author.name

        # Create a living entity (creator-only)
        if args:
            if str(ctx.message.author.id) == '214128381762076672':
                try: id = str(ctx.message.mentions[0].id); name = ctx.message.mentions[0].name
                except IndexError: id = ' '.join(args); name = id
            else: await ctx.send(":no_entry_sign: You wish :>"); return

        resu = await self.quefe(f"SELECT stats FROM personal_info WHERE id='{id}'")
        try:
            if resu[0] != 'DEAD':
                await ctx.send(f"<:osit:544356212846886924> You've already incarnate!"); return
        except TypeError: pass

        ava = {}
        year, month, day, hour, minute = await self.client.loop.run_in_executor(None, self.time_get)

        if not resu:
            ava['name'] = await self.inj_filter(name[0:20])
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
                ava['size'] = f'{random.choice(range(int(r_size_1[0]), int(r_size_1[1])))} - {random.choice(range(int(r_size_2[0]), int(r_size_2[1])))} - {random.choice(range(int(r_size_3[0]), int(r_size_3[1])))}'

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
            ava['merit'] = 0
            ava['perks'] = 5
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

            await self.quefe(f"INSERT INTO personal_info VALUES ('{id}', '{ava['name']}', '{ava['dob']}', {ava['age']}, '{ava['gender']}', '{ava['race']}', {ava['height']}, {ava['weight']}, '{ava['size']}', 'GREEN', {ava['kills']}, {ava['deaths']}, {ava['charm']}, '{ava['partner']}', {ava['money']}, {ava['merit']}, {ava['perks']}, {ava['EVO']}, {ava['STR']}, {ava['INTT']}, {ava['STA']}, {ava['MAX_STA']}, {ava['LP']}, {ava['MAX_LP']}, {ava['auras'][0]}, {ava['auras'][1]}, {ava['auras'][2]}, {ava['auras'][3]}, '{ava['cur_MOB']}', '{ava['cur_USER']}', '{ava['cur_PLACE']}', {ava['cur_X']}, {ava['cur_Y']}, '{ava['cur_QUEST']}', '{ava['combat_HANDLING']}', '{ava['right_hand']}', '{ava['left_hand']}');")
            await self.quefe(f"INSERT INTO pi_degrees VALUES ('{id}', 'Instinct', NULL);")
            # Guild
            await _cursor.execute(f"INSERT INTO pi_guild VALUES ('{id}', 'region.0', 'iron', 0, 0);")
            # Avatars
            for ava_code in ava['avatars']: await _cursor.execute(f"INSERT INTO pi_avatars VALUES ('{id}', '{ava_code}');")
            await _cursor.execute(f"INSERT INTO pi_backgrounds VALUES ('{id}', 'bg0');")
            await _cursor.execute(f"INSERT INTO cosmetic_preset VALUES (0, '{ctx.author.id}', 'default of {ava['name']}','DEFAULT', 'av0', 'bg0', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF')")
            await _cursor.execute(f"INSERT INTO cosmetic_preset VALUES (0, '{ctx.author.id}', 'default of {ava['name']}', 'CURRENT', 'av0', 'bg0', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF')")
            # Arts
            await _cursor.execute(f"INSERT INTO pi_arts VALUES ('{ctx.author.id}', 'sword', 'chain_attack', 5)")
            # Inventory     |      Add fist as a default weapon
            await _cursor.execute(f"SELECT func_it_reward('{ctx.author.id}', 'ar13', 1);")
            #self.ava_dict[id] = ava 
            await ctx.send(f":white_check_mark: {ctx.author.mention} has successfully incarnated. **Welcome to this world!**\n· You are currently logged out. Use `teleport 1 1` to log in. Then you may check our profile by `profile`.\n· Info? `help`. Concepts? `concept`")
        else:
            await _cursor.execute(f"UPDATE personal_info SET LP=1, STA=1, stats='GREEN' WHERE id='{id}'; UPDATE pi_inventory SET existence='GOOD' WHERE user_id='{id}' AND item_code='ar13';")
            await ctx.send(f":white_check_mark: {ctx.message.author.mention} has successfully incarnated. **WELCOME BACK!**")            

    @commands.command()
    async def kms(self, ctx, *args):
        query = f"""DELETE FROM pi_degrees WHERE user_id='{ctx.author.id}';
                    DELETE FROM pi_guild WHERE user_id='{ctx.author.id}';
                    DELETE FROM cosmetic_preset WHERE user_id='{ctx.author.id}';
                    DELETE FROM pi_arts WHERE user_id='{ctx.author.id}';
                    UPDATE pi_inventory SET existence='BAD' WHERE user_id='{ctx.author.id}';
                    UPDATE pi_land SET user_id='BAD' WHERE user_id='{ctx.author.id}';
                    DELETE FROM pi_bank WHERE user_id='{ctx.author.id}';
                    DELETE FROM pi_avatars WHERE user_id='{ctx.author.id}';
                    DELETE FROM pi_backgrounds WHERE user_id='{ctx.author.id}';
                    DELETE FROM pi_hunt WHERE user_id='{ctx.author.id}';
                    DELETE FROM pi_mobs_collection WHERE user_id='{ctx.author.id}';
                    DELETE FROM pi_rest WHERE user_id='{ctx.author.id}';
                    DELETE FROM pi_quests WHERE user_id='{ctx.author.id}';
                    DELETE FROM personal_info WHERE id='{ctx.author.id}';"""
        
        await ctx.send(":bell: Please type `deletion confirm` to proceed.")

        def UMCc_check(m):
            return m.channel == ctx.channel and m.author == ctx.author and m.content.lower() == 'deletion confirm'

        try: await self.client.wait_for('message', timeout=15, check=UMCc_check)
        except asyncio.TimeoutError: await ctx.send(f"<:osit:544356212846886924> Requested time-out!"); return
        
        await _cursor.execute(query)
        await ctx.send(f":white_check_mark: *Sayonara, {ctx.author.name}!* May the Olds look upon you..."); return

    @commands.command(aliases=['p'])
    async def profile(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        await self.ava_scan(ctx.message, type='all')

        try:
            member = await commands.UserConverter().convert(ctx, args[0])
            id = member.id
            name = member.name
            _vmode = 'INDIRECT'
        except IndexError: id = str(ctx.message.author.id); name = ctx.message.author.name; _vmode = 'DIRECT'
        except commands.CommandError: await ctx.send("<:osit:544356212846886924> Invalid user"); return
        
        # Data get and paraphrase
        try: name, age, gender, money, merit, right_hand, left_hand, combat_HANDLING, STA, MAX_STA, LP, MAX_LP, STR, INTT, partner, evo = await self.quefe(f"SELECT name, age, gender, money, merit, right_hand, left_hand, combat_HANDLING, STA, MAX_STA, LP, MAX_LP, STR, INTT, partner, evo FROM personal_info WHERE id='{id}'")        
        except TypeError: await ctx.send("<:osit:544356212846886924> User has not incarnated!"); return

        if str(ctx.message.author.id) not in ['214128381762076672', partner, f'{ctx.author.id}']: await ctx.send("<:osit:544356212846886924> You have to be user's *partner* to view their status!"); return

        degrees = '` `'.join(await self.quefe(f"SELECT degree FROM pi_degrees WHERE user_id='{id}';"))
        if right_hand != 'n/a':
            if right_hand == 'ar13': rh_name = await self.quefe(f"SELECT name FROM pi_inventory WHERE existence='GOOD' AND item_code='{right_hand}' AND user_id='{ctx.author.id}';")
            else: rh_name = await self.quefe(f"SELECT name FROM pi_inventory WHERE existence='GOOD' AND item_id='{right_hand}' AND user_id='{str(ctx.message.author.id)}';")
            right_hand = f"`{right_hand}`|**{rh_name[0]}**"
        if left_hand != 'n/a': 
            lh_name = await self.quefe(f"SELECT name FROM pi_inventory WHERE existence='GOOD' AND (item_code='{left_hand}' OR item_id='{left_hand}') AND user_id='{str(ctx.message.author.id)}';")
            left_hand = f"`{left_hand}`|**{lh_name[0]}**"

        lmao = {'f': 'female', 'm': 'male'}
        # Status
        box = f"\n░░░░ **{name}** | {lmao[gender].capitalize()}, {age} ░░░░\n╟**`Money`** · <:36pxGold:548661444133126185>{money}\n╟**`Merit`** · {merit}\n╟**`Degrees`** · `{degrees}`\n━━━━━╾ {combat_HANDLING.capitalize()} hand ╼━━━━\n╟**`RIGHT`** · {right_hand}\n╟**`LEFT`** · {left_hand}\n━━━━━╾ **`EVO`** {evo} ╼━━━━━━\n**·** `STA` {STA}/{MAX_STA}\n**·** `LP` {LP}/{MAX_LP}\n**·** `STR` {STR}\n**·** `INT` {INTT}"
        await ctx.author.send(box)
        await ctx.send(":incoming_envelope: **Bang!** <a:blob_snu:531060438142812190> *From Cli with love*")

    @commands.command(aliases=['a'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def avatar(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        await self.ava_scan(ctx.message, type='all')

        __mode = 'static'

        # Console
        raw = list(args)
        try:
            if raw[0] == 'gif': __mode = 'gif'; user_id = ctx.author.id
            else:
                try: 
                    member = await commands.UserConverter().convert(ctx, raw[0])
                    user_id = member.id
                except IndexError: user_id = ctx.author.id
                except commands.CommandError: await ctx.send("<:osit:544356212846886924> User not found"); return
        except IndexError: user_id = ctx.author.id

        # Colour n Character get
        try: co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death, char_name, bg_code = await self.quefe(f"SELECT co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death, avatar_id, bg_code FROM cosmetic_preset WHERE user_id='{user_id}' AND stats='CURRENT';")
        except TypeError: await ctx.send(f"<:osit:544356212846886924> User has not incarnated! ({user_id})"); return
        #co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death = ('#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF')

        # STATIC =========
        async def magiking(ctx):

            # Info get
            age, evo, kill, death, money, name, partner = await self.quefe(f"SELECT age, evo, kills, deaths, money, name, (SELECT name FROM personal_info WHERE id=partner) FROM personal_info WHERE id='{user_id}';")
            guild_region, rank = await self.quefe(f"SELECT name, rank FROM pi_guild WHERE user_id='{user_id}';")
            g_region_name = await self.quefe(f"SELECT name FROM environ WHERE environ_code='{guild_region}';"); g_region_name = g_region_name[0]

            form_img = self.prote_lib['form'][0]
            char_img = random.choice(self.prote_lib[char_name])
            #char_img = char_img.resize((int(form_img.height/char_img.height*char_img.width), form_img.height))
            badge_img = self.prote_lib['badge'][rank.lower()]
            #badge_img = badge_img.resize((int(badge_img.width/1.5), int(badge_img.height/1.5)))
            #bg = self.prote_lib['bg'][0]
            bg = copy.deepcopy(random.choice(self.prote_lib['bg'][bg_code]))
            #bg = bg.resize((800, 600))
            #bg = bg.filter(ImageFilter.GaussianBlur(2.6))           # prev(best)=2.6
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
            dgb.text((name_box.width/2, 0), partner.capitalize(), font=fnt_degree, fill=co_partner)
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
            age, evo, kill, death, money, name = await self.quefe(f"SELECT age, evo, kills, deaths, money, name FROM personal_info WHERE id='{user_id}';")
            guild_region, rank = await self.quefe(f"SELECT name, rank FROM pi_guild WHERE user_id='{user_id}';")
            g_region_name = await self.quefe(f"SELECT name FROM environ WHERE environ_code='{guild_region}';"); g_region_name = g_region_name[0]

            #img = Image.open('sampleimg.jpg').convert('RGBA')
            form_img = self.prote_lib['form'][0]
            #char_img = char_img.resize((int(form_img.height/char_img.height*char_img.width), form_img.height))
            badge_img = self.prote_lib['badge'][rank.lower()]
            #badge_img = badge_img.resize((int(badge_img.width/1.5), int(badge_img.height/1.5)))
            bg = copy.deepcopy(in_img)
            #bg = bg.resize((800, 600))
            #bg = bg.filter(ImageFilter.GaussianBlur(2.6))           # prev(best)=2.6
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

            particles = self.prote_lib['bg_gif'][0]
            char_img = self.prote_lib[char_name][random.choice(range(10))]
            count = 0; partilen = len(particles)
            # This is for the sake of off-set
            while True:
                print(f"LOOOPPPPP {count}")
                if count > partilen: break
                try:
                    #particle = particles[count]
                    #a = Image.fromarray(particle)  

                    #out_img = await gafiking(ctx, a, char_img)
                    out_img = await gafiking(ctx, particles[count], char_img)
                    await asyncio.sleep(0.1)
                    #outImPart.append(np.asarray(a))
                    outImPart.append(out_img)
                except IndexError: break
                count += 15

            output_buffer = BytesIO()
            #imageio.mimwrite(output_buffer, outImPart)
            outImPart[0].save(output_buffer, save_all=True, format='gif', append_images=outImPart, loop=0)
            output_buffer.seek(0)
            #return await self.client.loop.run_in_executor(None, self.imgur_client.upload, output_buffer)
            #return output_buffer
            await ctx.send(file=discord.File(fp=output_buffer, filename='profile.gif'))
        
        if __mode == 'static':
            await ctx.trigger_typing()
            output_buffer = await magiking(ctx)
            await ctx.send(file=discord.File(fp=output_buffer, filename='profile.png'))
        elif __mode == 'gif':
            await ctx.trigger_typing()
            #output_buffer = await cogif(ctx)         
            #reembed = discord.Embed(colour = discord.Colour(0x011C3A))
            #reembed.set_image(url=output_buffer['link'])
            #await ctx.send(embed=reembed)
            #await ctx.send(file=discord.File(fp=output_buffer, filename='profile.gif'))
            await cogif(ctx)

    @commands.command(aliases=['guide'])
    @commands.cooldown(1, 7, type=BucketType.user)
    async def help(self, ctx, *args):
        raw = list(args); temb_socket = []
        prefixes = {336642139381301249: 'cli '}

        try: prefix = prefixes[ctx.guild.id]
        except KeyError: prefix = '>'

        if not raw:
            temball = discord.Embed(
                title = '**G U I D E**⠀⠀|⠀⠀**R P G  C O M M A N D S**',
                description = f"""
                                 ```dsconfig
⠀| For RPG commands, please use: {prefix}help
⠀| For RPG concepts, please use: {prefix}concept```
                                **『Lore』**
                                \tYou - a Remnant as many others - woke up in the middle of an unreal world, where reality mixed with fantasy, where space and time were torn apart into *regions*.
                                \tSince the Seraph, human have fought their way to reunite its race and called themselves, **"United Regions of The Pralaeyr"**, later pointed their swords at the pit and the summit of Pralaeyr.
                                \t"To fight the darkness of the fantasy and to free the human race from the Pralaeyr", firsts of the Remnants have sworn.

                                **『Support Server』**
                                Cli nee-chan is still underconstruction!
                                For better experience and support? Join her server <3 https://discord.gg/4wJHCBp
                                """,
                colour = discord.Colour(0xB1F1FA)
            )
            #**『How to understand?』**
            #**>** **`[..]`**: Compulsory argument **`{{..}}`**: Optional argument
            #**>** **`REQUIREMENTS`** are placed next to the command's name. These are not compulsory, but worth consideration when invoked.
            #**>** **`TAGS`** are placed at the very end.
            #**>** To inspect a command: `guide [command]`
            temball.set_thumbnail(url='https://imgur.com/EQsptpa.png')
            temball.set_image(url="https://imgur.com/OGs47ty.png")
            temball.set_footer(text=f"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀")
            temb_socket.append(temball)

            tembs = [['**P E R S O N A L  I N F O**', "| **`profile` \n::** DM you your status \n| **`avatar` \n::** Display your avatar\n| **`wardrobe` \n::** Show all avatar of yours\n| **`incarnate` \n::** Create a character"],
                    ['**A C T I V I T I E S**', "| **`work` \n::** Sign up for a job\n| **`works` \n::** View all jobs\n| **`edu` \n::** Stuff relevant to *education*\n| **`guild` \n::** Stuff relevant to *guild*\n| **`evolve` \n::** Evolve/Upgrade your status"],
                    ['**C O M M E R C I A L**', "| **`shop` \n::** View region's shop\n| **`buy` \n::** Buy items from shop\n| **`inventory` \n::** View your inventory\n| **`trader` \n::** View/Buy what the traders sell\n| **`trade` \n::** Trade items with a player\n| **`sell` \n::** Sell items\n| **`give` \n::** Give money to a player\n| **`bank` \n::** Stuff relevant to *banking*"],
                    ['**C O M B A T**', "| **`use` \n::** Equip items. Consume items. Switch weapons' slot\n| **`attack` \n::** Attack someone/something. Change pose\n| **`aim` \n::** Shoot someone/something. Change pose"],
                    ['**T A C T I C A L**', "\n| **`tele` \n::** Teleport\n| **`medic` \n::** Heal\n| **`infuse` \n::** Infuse items\n| **`merge` \n::** Merge items\n| **`hunt` \n::** Go for a hunt"],
                    ['**T O O L S**', "| **`sekaitime` \n::** View current time of Pralaeyr\n| **`radar` \n::** Scan map for players\n| **`mdist` \n::** Calculate distance"]]
            for stuff in tembs:
                tembeach = discord.Embed(
                    title = stuff[0],
                    description = f"""______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ 
                    {stuff[1]}""",
                    colour = discord.Colour(0xB1F1FA)
                )
                tembeach.set_thumbnail(url='https://imgur.com/EQsptpa.png')
                temb_socket.append(tembeach)

            async def browse():
                async def attachreaction(msg):
                    await msg.add_reaction("\U000023ee")    #Top-left
                    await msg.add_reaction("\U00002b05")    #Left
                    await msg.add_reaction("\U000027a1")    #Right
                    await msg.add_reaction("\U000023ed")    #Top-right

                cursor = 0
                emli = temb_socket
                pages = len(temb_socket)
                msg = await ctx.send(embed=emli[cursor])
                await attachreaction(msg)

                def UM_check(reaction, user):
                    return user.id == ctx.author.id and reaction.message.id == msg.id

                while True:
                    try:
                        reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=UM_check)
                        if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                            cursor += 1
                            await msg.edit(embed=emli[cursor])
                            try: await msg.remove_reaction(reaction.emoji, user)
                            except discordErrors.Forbidden: pass
                        elif reaction.emoji == "\U00002b05" and cursor > 0:
                            cursor -= 1
                            await msg.edit(embed=emli[cursor])
                            try: await msg.remove_reaction(reaction.emoji, user)
                            except discordErrors.Forbidden: pass
                        elif reaction.emoji == "\U000023ee" and cursor != 0:
                            cursor = 0
                            await msg.edit(embed=emli[cursor])
                            try: await msg.remove_reaction(reaction.emoji, user)
                            except discordErrors.Forbidden: pass
                        elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                            cursor = pages - 1
                            await msg.edit(embed=emli[cursor])
                            try: await msg.remove_reaction(reaction.emoji, user)
                            except discordErrors.Forbidden: pass
                    except asyncio.TimeoutError:
                        await msg.delete(); return

            await browse(); return

        # Search
        try: command, aliases, syntax, description, tags, requirement = await self.quefe(f"SELECT command, aliases, syntax, description, tags, requirement FROM sys_command WHERE command='{raw[0]}';")
        # E: No result. Instead try to search for familiar
        except TypeError:
            packs = await self.quefe(f"SELECT command FROM sys_command WHERE command LIKE '%{raw[0]}%' OR aliases LIKE '%{raw[0]}%';", type='all')
            # E: No familiar found
            if not packs: await ctx.send(":x: Commands not found"); return

            line = ''
            for pack in packs:
                line = line + f"""
· {pack[0]}"""
            temb = discord.Embed(title=':mag_right:⠀⠀You were saying...', description=f"```{line}```", colour = discord.Colour(0xB1F1FA))
            await ctx.send(embed=temb); return


        if requirement == 'n/a': temp_des = ''
        else: temp_des = f"⠀|⠀{requirement}"

        temb = discord.Embed(
                    title=f"**{command.upper()}** {temp_des}",
                    description='⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀',
                    colour = discord.Colour(0xB1F1FA))
        temb.add_field(name='**『Syntax』**', value=f"{syntax}\n⠀", inline=True)
        temb.add_field(name='**『Aliases』**', value=f"{aliases}\n⠀", inline=True)
        temb.add_field(name='**『Description』**', value=f"{description}", inline=False)
        temb.set_footer(text=f"<{tags.replace(' - ', '> <')}>", icon_url='https://imgur.com/EQsptpa.png')

        await ctx.send(embed=temb)

    @commands.command(aliases=['cc'])
    @commands.cooldown(1, 3, type=BucketType.user)
    async def concept(self, ctx, *args):
        raw = list(args); temb_socket = []

        if not raw:
            temball = discord.Embed(
                title = '**C O N C E P T S**⠀⠀|⠀⠀**R P G  W I K I**',
                description = """
                ```dsconfig
Definition? Mechanism? Lore? Yaaa```
                                **『YOU. ARE. CONFUSED...』**
                                \tYou walk into our worlds, you are confused. You might have known the commands, but you could have not fully embraced the nature of it.
                                \tThis may be your guidance to the basis of this world, or may it let you acknowledge the furthest corner of the system.
                                \tYour choice, to learn more or to stay still. May the Olds look upon you

                                **『.. SO. ARE. WE.』**
                                We, the devs, might not be able to please your curiosity, since... we sometimes cannot remember all of what the Pralaeyr can do!
                                May it be a mistake, or may it be not enough, if you don't mind, please come to our support server! https://discord.gg/4wJHCBp
                                """,
                                colour = discord.Colour(0xB1F1FA)
            )
            temball.set_thumbnail(url='https://imgur.com/ZneprKF.png')
            temball.set_footer(text=f"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀")
            temball.set_image(url='https://imgur.com/4ixM0TR.png')
            temb_socket.append(temball)

            tembs = [['**E N T I T Y**', "| **`Items` \n::** Things that you can keep in your inventory\n| **`Arsenal` \n::** Weaponary \n| **`Ingredients` \n::** Stuff that usually sold by traders\n| **`Supply`\n::** Stuff that usually sold in shops"],
                    ['**M E C H A N I C**', "| **`LP` \n::** Basically HP\n| **`STR` \n::** Strength\n| **`INT` \n::** Intelligence\n| **`STA` \n::** Stamina\n| **`Charm` \n::** How pretty you are\n| **`Evolution` \n::** Or EVO. Show how many upgrades you've been through"]]
            for stuff in tembs:
                tembeach = discord.Embed(
                    title = stuff[0],
                    description = f"""______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______ ______
                    {stuff[1]}""",
                    colour = discord.Colour(0xB1F1FA)
                )
                tembeach.set_thumbnail(url='https://imgur.com/ZneprKF.png')
                temb_socket.append(tembeach)

            #temb.add_field(name="Remnant's", value='| **`remnant`** \n| **`avatar`** \n| **`wardrobe`** \n| **`incarnate`**', inline=True)
            #temb.add_field(name='Activities', value="| **`work`** \n| **`works`** \n| **`edu`** \n| **`medic`** \n| **`guild`** \n| **`evolve`** \n| **`infuse`** \n| **`merge`** \n| **`hunt`**", inline=True)
            #temb.add_field(name='Commercial', value="| **`shop`** \n| **`buy`** \n| **`inventory`** \n| **`trader`** \n| **`trade`** \n| **`sell`** \n| **`give`** \n| **`bank`**", inline=True)
            #temb.add_field(name="Actions", value="| **`use`** \n| **`attack`** \n| **`aim`** \n| **`tele`**", inline=True)
            #temb.add_field(name="Actions", value="| **`sekaitime`** \n| **`radar`** \n| **`mdist`**", inline=True)

            async def browse():
                async def attachreaction(msg):
                    await msg.add_reaction("\U000023ee")    #Top-left
                    await msg.add_reaction("\U00002b05")    #Left
                    await msg.add_reaction("\U000027a1")    #Right
                    await msg.add_reaction("\U000023ed")    #Top-right

                cursor = 0
                emli = temb_socket
                pages = len(temb_socket)
                msg = await ctx.send(embed=emli[cursor])
                await attachreaction(msg)

                def UM_check(reaction, user):
                    return user.id == ctx.author.id and reaction.message.id == msg.id

                while True:
                    try:
                        reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=UM_check)
                        if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                            cursor += 1
                            await msg.edit(embed=emli[cursor])
                            try: await msg.remove_reaction(reaction.emoji, user)
                            except discordErrors.Forbidden: pass
                        elif reaction.emoji == "\U00002b05" and cursor > 0:
                            cursor -= 1
                            await msg.edit(embed=emli[cursor])
                            try: await msg.remove_reaction(reaction.emoji, user)
                            except discordErrors.Forbidden: pass
                        elif reaction.emoji == "\U000023ee" and cursor != 0:
                            cursor = 0
                            await msg.edit(embed=emli[cursor])
                            try: await msg.remove_reaction(reaction.emoji, user)
                            except discordErrors.Forbidden: pass
                        elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                            cursor = pages - 1
                            await msg.edit(embed=emli[cursor])
                            try: await msg.remove_reaction(reaction.emoji, user)
                            except discordErrors.Forbidden: pass
                    except asyncio.TimeoutError:
                        await msg.delete(); return

            await browse(); return

        # Search
        try: concept, description, tags, typee = await self.quefe(f"SELECT concept, description, tags, type FROM sys_concept WHERE concept='{raw[0]}';")
        # E: No result. Instead try to search for familiar
        except TypeError:
            packs = await self.quefe(f"SELECT concept FROM sys_concept WHERE concept LIKE '%{raw[0]}%' OR tags LIKE '%{raw[0]}%';", type='all')
            # E: No familiar found
            if not packs: await ctx.send(":x: Concept not found"); return

            line = ''
            for pack in packs:
                line = line + f"""
· {pack[0]}"""
            temb = discord.Embed(title=':mag_right:⠀⠀You were saying...', description=f"```{line}```", colour = discord.Colour(0xB1F1FA))
            await ctx.send(embed=temb); return

        temb = discord.Embed(
                    title=f"**{concept.upper()}**⠀⠀|⠀⠀{typee}",
                    description=f'{description}',
                    colour = discord.Colour(0xB1F1FA))
        temb.set_thumbnail(url='https://imgur.com/EQsptpa.png')
        temb.set_footer(text=f"<{tags.replace(' - ', '> <')}>", icon_url='https://imgur.com/TW9dmXy.png')

        await ctx.send(embed=temb)


    @commands.command(aliases=['wb'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def wardrobe(self, ctx, *args):

        raw = list(args)

        try:
            if raw[0] == 'save':
                # Naming
                try: pname = raw[1]
                except IndexError: pname = 'Untitled'

                # Quantity limit check
                if await _cursor.execute(f"SELECT * FROM cosmetic_preset WHERE user_id='{str(ctx.message.author.id)}' AND stats='CURRENT';") >= 3: await ctx.send(f"<:osit:544356212846886924> You cannot have more than three presets at a time, {str(ctx.message.author.id)}")

                await _cursor.execute(f"INSERT INTO cosmetic_preset(user_id, name, stats, avatar_id, bg_code, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death) SELECT {str(ctx.message.author.id)}, '{pname}', 'PRESET', avatar_id, bg_code, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death FROM cosmetic_preset WHERE user_id='{str(ctx.message.author.id)}' AND stats='CURRENT';")

                await ctx.send(f":white_check_mark: Created preset **{pname}**. Use `-wardrobe presets` to check its *id*."); return

            elif raw[0] == 'delete':
                try:
                    if await _cursor.execute(f"DELETE FROM cosmetic_preset WHERE preset_id='{raw[1]}' AND user_id='{ctx.author.id}' AND stats!='DEFAULT';") == 0:
                        await ctx.send("<:osit:544356212846886924> Preset's id not found!"); return
                # E: Preset's id not given
                except IndexError: await ctx.send("<:osit:544356212846886924> Please provide the id!"); return

                await ctx.send(f":white_check_mark: Preset id `{raw[1]}` was deleted."); return
            
            elif raw[0] == 'load':
                # GET preset
                try: 
                    if raw[1] == 'default':
                        avatar_id, bg_code, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death = await self.quefe(f"SELECT avatar_id, bg_code, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death FROM cosmetic_preset WHERE user_id='{str(ctx.message.author.id)}' AND stats='DEFAULT';")
                    else:
                        avatar_id, bg_code, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death = await self.quefe(f"SELECT avatar_id, bg_code, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death FROM cosmetic_preset WHERE user_id='{str(ctx.message.author.id)}' AND preset_id='{raw[1]}';")
                # E: Preset's id not found
                except (IndexError, TypeError): await ctx.send("<:osit:544356212846886924> Preset's id not found!"); return

                # UPDATE current
                await _cursor.execute(f"UPDATE cosmetic_preset SET user_id='{str(ctx.message.author.id)}', name='current of {ctx.message.author.name}', stats='CURRENT', avatar_id='{avatar_id}', bg_code='{bg_code}', co_name='{co_name}', co_partner='{co_partner}', co_money='{co_money}', co_age='{co_age}', co_guild='{co_guild}', co_rank='{co_rank}', co_evo='{co_evo}', co_kill='{co_kill}', co_death='{co_death}' WHERE user_id='{str(ctx.message.author.id)}' AND stats='CURRENT';")
                await ctx.send(":white_check_mark: Preset's loaded!"); return
            
            elif raw[0] == 'presets':
                line = ""

                presets = await self.quefe(f"SELECT preset_id, name, avatar_id FROM cosmetic_preset WHERE user_id='{str(ctx.message.author.id)}' AND stats NOT IN ('DEFAULT', 'CURRENT');", type='all')

                if not presets: await ctx.send(f"You have not created any presets yet **{ctx.message.author.name}**"); return

                for preset in presets:
                    line = line + f"\n `{preset[0]}` :bust_in_silhouette: **{preset[1]}** |< {preset[2]} >|"

                await ctx.send(f":gear: Your list of presets, {ctx.message.author.mention}\n----------------------{line}"); return

            elif raw[0] in ['background', 'bg']: raise IndexError

            else:
                # COLOUR
                try:
                    if not re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}<:36pxGold:548661444133126185>', raw[1]): await ctx.send("<:osit:544356212846886924> Please use **hexa-decimal** colour code!\n:moyai: You can get them here --> https://htmlcolorcodes.com/"); return
                    
                    coattri = {'name': 'co_name', 'age': 'co_age', 'money': 'co_money', 'partner': 'co_partner', 'guild': 'co_guild', 'rank': 'co_rank', 'evo': 'co_evo', 'kills': 'co_kill', 'deaths': 'co_death'}
                    try:
                        await _cursor.execute(f"UPDATE cosmetic_preset SET {coattri[raw[0]]}='{raw[1]}' WHERE user_id='{str(ctx.message.author.id)}' AND stats='CURRENT';")
                        await ctx.send(f":white_check_mark: Attribute's colour was changed to **`{raw[1]}`**."); return
                    # E: Attributes not found
                    except KeyError: await ctx.send(f":moyai: Please use the following attributes: **`{'`** **`'.join(list(coattri.keys()))}`**"); return

                # AVATAR
                # E: Color not given
                except IndexError:
                    if raw[0].startswith('av'):
                        try:
                            if await _cursor.execute(f"UPDATE cosmetic_preset SET avatar_id='{raw[0]}' WHERE user_id='{ctx.author.id}' AND stats='CURRENT' AND EXISTS (SELECT * FROM pi_avatars WHERE user_id='{ctx.author.id}' AND avatar_id='{raw[0]}');") == 0:
                                await ctx.send(f"<:osit:544356212846886924> You don't own this avatar, **{ctx.author.name}**!"); return
                            await ctx.send(f":white_check_mark: Changed to `{raw[0]}`"); return
                        except mysqlError.IntegrityError: await ctx.send(f"<:osit:544356212846886924> Avatar not found!"); return
                    else:
                        try: 
                            if await _cursor.execute(f"UPDATE cosmetic_preset SET bg_code='{raw[0]}' WHERE user_id='{ctx.author.id}' AND stats='CURRENT' AND EXISTS (SELECT * FROM pi_backgrounds WHERE user_id='{ctx.author.id}' AND bg_code='{raw[0]}');") == 0:
                                await ctx.send(f"<:osit:544356212846886924> You don't own this avatar, **{ctx.author.name}**!"); return
                            await ctx.send(f":white_check_mark: Changed to `{raw[0]}`"); return
                        except mysqlError.IntegrityError: await ctx.send(f"<:osit:544356212846886924> Background not found!"); return

        # AVATARs
        # E: No avatar given
        except IndexError:
            line = ''

            async def browse():
                if not args:
                    items2 = await self.quefe(f"SELECT avatar_id FROM pi_avatars WHERE user_id='{ctx.author.id}';", type='all')
                    if not items2: await ctx.send(f":x: No result..."); return

                    items = []
                    for item in items2:
                        ava_id, name, description = await self.quefe(f"SELECT avatar_id, name, description FROM model_avatar WHERE avatar_id='{item[0]}';")
                        items.append([ava_id, name, description])

                    def makeembed(top, least, pages, currentpage):
                        line = '' 

                        for item in items[top:least]:
                            
                            line = line + f"""\n`{item[0]}` · **{item[1]}**\n⠀⠀⠀| *"{item[2]}"*"""

                        reembed = discord.Embed(title = f"<a:blob_trashcan:531060436163100697> **{ctx.author.name}**'s avatars", colour = discord.Colour(0x011C3A), description=line)
                        reembed.set_footer(text=f"Total: {len(items)} | Closet {currentpage} of {pages}")
                        return reembed
                        #else:
                        #    await ctx.send("*Nothing but dust here...*")
                    
                    async def attachreaction(msg):
                        await msg.add_reaction("\U000023ee")    #Top-left
                        await msg.add_reaction("\U00002b05")    #Left
                        await msg.add_reaction("\U000027a1")    #Right
                        await msg.add_reaction("\U000023ed")    #Top-right

                    pages = int(len(items)/5)
                    if len(items)%5 != 0: pages += 1
                    currentpage = 1
                    cursor = 0

                    emli = []
                    for curp in range(pages):
                        myembed = makeembed(currentpage*5-5, currentpage*5, pages, currentpage)
                        emli.append(myembed)
                        currentpage += 1

                    if pages > 1:
                        msg = await ctx.send(embed=emli[cursor])
                        await attachreaction(msg)
                    else: 
                        msg = await ctx.send(embed=emli[cursor], delete_after=15)
                        return

                    def UM_check(reaction, user):
                        return user.id == ctx.author.id and reaction.message.id == msg.id

                    while True:
                        try:
                            reaction, user = await self.client.wait_for('reaction_add', timeout=15, check=UM_check)
                            if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                                cursor += 1
                                await msg.edit(embed=emli[cursor])
                                try: await msg.remove_reaction(reaction.emoji, user)
                                except discordErrors.Forbidden: pass
                            elif reaction.emoji == "\U00002b05" and cursor > 0:
                                cursor -= 1
                                await msg.edit(embed=emli[cursor])
                                try: await msg.remove_reaction(reaction.emoji, user)
                                except discordErrors.Forbidden: pass
                            elif reaction.emoji == "\U000023ee" and cursor != 0:
                                cursor = 0
                                await msg.edit(embed=emli[cursor])
                                try: await msg.remove_reaction(reaction.emoji, user)
                                except discordErrors.Forbidden: pass
                            elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                                cursor = pages - 1
                                await msg.edit(embed=emli[cursor])
                                try: await msg.remove_reaction(reaction.emoji, user)
                                except discordErrors.Forbidden: pass
                        except asyncio.TimeoutError:
                            await msg.delete(); return

                else:
                    items2 = await self.quefe(f"SELECT bg_code FROM pi_backgrounds WHERE user_id='{ctx.author.id}';", type='all')
                    if not items2: await ctx.send(f":x: No result..."); return

                    items = []
                    for item in items2:
                        ava_id, name, description = await self.quefe(f"SELECT bg_code, name, description FROM model_background WHERE bg_code='{item[0]}';")
                        items.append([ava_id, name, description])

                    def makeembed(top, least, pages, currentpage):
                        line = '' 

                        for item in items[top:least]:
                            
                            line = line + f"""\n`{item[0]}` · **{item[1]}**\n⠀⠀⠀| *"{item[2]}"*"""

                        reembed = discord.Embed(title = f"<a:blob_trashcan:531060436163100697> **{ctx.author.name}**'s backgrounds", colour = discord.Colour(0x011C3A), description=line)
                        reembed.set_footer(text=f"Total: {len(items)} | Closet {currentpage} of {pages}")
                        return reembed
                        #else:
                        #    await ctx.send("*Nothing but dust here...*")
                    
                    async def attachreaction(msg):
                        await msg.add_reaction("\U000023ee")    #Top-left
                        await msg.add_reaction("\U00002b05")    #Left
                        await msg.add_reaction("\U000027a1")    #Right
                        await msg.add_reaction("\U000023ed")    #Top-right

                    pages = int(len(items)/5)
                    if len(items)%5 != 0: pages += 1
                    currentpage = 1
                    cursor = 0

                    emli = []
                    for curp in range(pages):
                        myembed = makeembed(currentpage*5-5, currentpage*5, pages, currentpage)
                        emli.append(myembed)
                        currentpage += 1

                    if pages > 1:
                        msg = await ctx.send(embed=emli[cursor])
                        await attachreaction(msg)
                    else: 
                        msg = await ctx.send(embed=emli[cursor], delete_after=15)
                        return

                    def UM_check(reaction, user):
                        return user.id == ctx.author.id and reaction.message.id == msg.id

                    while True:
                        try:
                            reaction, user = await self.client.wait_for('reaction_add', timeout=15, check=UM_check)
                            if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                                cursor += 1
                                await msg.edit(embed=emli[cursor])
                                try: await msg.remove_reaction(reaction.emoji, user)
                                except discordErrors.Forbidden: pass
                            elif reaction.emoji == "\U00002b05" and cursor > 0:
                                cursor -= 1
                                await msg.edit(embed=emli[cursor])
                                try: await msg.remove_reaction(reaction.emoji, user)
                                except discordErrors.Forbidden: pass
                            elif reaction.emoji == "\U000023ee" and cursor != 0:
                                cursor = 0
                                await msg.edit(embed=emli[cursor])
                                try: await msg.remove_reaction(reaction.emoji, user)
                                except discordErrors.Forbidden: pass
                            elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                                cursor = pages - 1
                                await msg.edit(embed=emli[cursor])
                                try: await msg.remove_reaction(reaction.emoji, user)
                                except discordErrors.Forbidden: pass
                        except asyncio.TimeoutError:
                            await msg.delete(); return

            await browse()

    @commands.command(aliases=['happybirthday', 'hpbd'])
    async def daily(self, ctx, *args):
        cmd_tag = 'daily'
        if not await self.ava_scan(ctx.message, type='life_check'): return
        if not await self.__cd_check(ctx.message, cmd_tag, f"<:fufu:508437298808094742> Oops. It's not your birthday yet, **{ctx.author.name}**."): return

        await _cursor.execute(f"SELECT func_ig_reward('{ctx.author.id}', 'ig77', 1);")
        await ctx.send(f":cake: Happy birthday! Here's a `ig77`|**Cake**!")
        await self.client.loop.run_in_executor(None, partial(redio.set, f'{cmd_tag}{ctx.author.id}', 'working', ex=86400, nx=True))

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def rename(self, ctx, *, name):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        
        if not name: await ctx.send("<:osit:544356212846886924> `rename [name]`"); return
        if len(name) > 21: await ctx.send("<:osit:544356212846886924> Names can only contain 21 characters."); return

        name = await self.inj_filter(name)

        await self.quefe(f"UPDATE personal_info SET name='{name}' WHERE id='{ctx.author.id}';")
        await ctx.send(f":white_check_mark: Your name's changed to **{name}**.")

    @commands.command()
    @commands.cooldown(1, 2, type=BucketType.user)
    async def pralaeyr(self, ctx):
        await ctx.send("https://media.discordapp.net/attachments/381963689470984203/546796245994307595/map_description.png")

    @commands.command(aliases=['tut'])
    @commands.cooldown(1, 3, type=BucketType.user)
    async def tutorial(self, ctx, *args):
        await ctx.send("GO. TEACH. YOURSELF.")



# ============= ACTIVITIES ==================

    @commands.command(aliases=['job'])
    @commands.cooldown(1, 10, type=BucketType.user)
    async def work(self, ctx, *args):
        cmd_tag = 'work'
        if not await self.ava_scan(ctx.message, type='life_check'): return
        if not await self.__cd_check(ctx.message, cmd_tag, f"**{ctx.author.name}**, you are working."): return
        raw = list(args)

        try: 
            requirement, duration, reward, sta, jname = await self.quefe(f"SELECT requirement, duration, reward, sta, name FROM model_job WHERE job_code='{raw[0]}';")
            try:
                reli = requirement.split(' - '); full_cheq = ''
                for ree in reli:
                    ree = ree.split(' of ')
                    cheq = f"degree='{ree[0]}'"
                    try: cheq = cheq + f" AND major='{ree[1]}'"
                    except IndexError: pass

                    full_cheq = full_cheq + f" AND EXISTS (SELECT * FROM pi_degrees WHERE user_id='{ctx.author.id}' AND {cheq})"

                STA, money = await self.quefe(f"""SELECT STA, money FROM personal_info WHERE id='{ctx.author.id}' {full_cheq};""")
                if STA < sta: await ctx.send(f"Grab something to *eat*, **{ctx.author.name}** <:fufu:508437298808094742> You can't do anything with such STA."); return

                await ctx.send(f":briefcase: **{ctx.author.name}** wants to be `{raw[0]}`|**{jname}** for `{int(duration/240)}` days. We'll prepay you **<:36pxGold:548661444133126185>{reward}**!")
                await _cursor.execute(f"UPDATE personal_info SET STA={STA - sta}, money={money + reward} WHERE id='{ctx.author.id}'")
            # E: Unpack on empty query, due to degree not found
            except TypeError: await ctx.send(f""":briefcase: You need `{"', '".join(requirement.split(' - '))}` to apply for this job!"""); return
        except IndexError: await ctx.send(":briefcase: Please choose a job! You can use `works` check what you can do"); return
        # E: Unpack on empty query, due to job_code not found
        except TypeError: await ctx.send(":x: Job's code not found!"); return

        await self.client.loop.run_in_executor(None, partial(redio.set, f'{cmd_tag}{ctx.author.id}', 'working', ex=duration, nx=True))

    @commands.command(aliases=['jobs'])
    @commands.cooldown(1, 10, type=BucketType.user)
    async def works(self, ctx, *args):

        search_query = ''
        for search in args:
            try:
                try:
                    if int(search): kww = 'sta'
                    else: kww = 'sta'
                except ValueError:
                    if search.startswith('$'): kww = 'reward'
                    elif search.endswith('s'): kww = 'duration'
                    else: kww = 'requirement'

                if search_query: search_query += "AND"
                else: search_query += "WHERE"; first = kww

                if kww == 'requirement': search_query += f" requirement LIKE '%{search.capitalize()}%' "
                else: search_query += f" {kww}>={search} "
            # E: Invalid search
            except (AttributeError, IndexError): pass
        
        if search_query: search_query += f" ORDER BY {first} ASC"

        try:
            job_list = await self.quefe(f"SELECT job_code, name, description, requirement, duration, reward, sta FROM model_job {search_query};", type='all')
            if not job_list: await ctx.send("<:osit:544356212846886924> No result..."); return
        # E: Invalid syntax 
        except mysqlError.ProgrammingError: await ctx.send("<:osit:544356212846886924> **Invalid syntax.** For filtering, please use `[keyword]==[value]`"); return 
        # E: Invalid syx
        except mysqlError.InternalError: await ctx.send("<:osit:544356212846886924> **Invalid keywors.** Please use `reward`, `duration`, `requirement`, `sta`"); return

        def makeembed(top, least, pages, currentpage):
            line = ''

            line = "**-------------------- oo --------------------**\n" 
            for pack in job_list[top:least]:
                job_code, name, description, requirement, duration, reward, sta = pack
                line = line + f"""`{job_code}` ∙ **{name.capitalize()}**\n*"{description}"*\n**<:36pxGold:548661444133126185>{reward}** | `{duration}`**s** | STA-`{sta}` | **Require:** `{requirement.replace(' - ', '` `')}`\n\n"""
            line = line + "**-------------------- oo --------------------**" 

            reembed = discord.Embed(title = f"JOBS", colour = discord.Colour(0x011C3A), description=line)
            reembed.set_footer(text=f"Page {currentpage} of {pages}")
            return reembed
            #else:
            #    await ctx.send("*Nothing but dust here...*")
        
        async def attachreaction(msg):
            await msg.add_reaction("\U000023ee")    #Top-left
            await msg.add_reaction("\U00002b05")    #Left
            await msg.add_reaction("\U000027a1")    #Right
            await msg.add_reaction("\U000023ed")    #Top-right

        pages = len(job_list)//5
        if len(job_list)%5 != 0: pages += 1
        currentpage = 1
        cursor = 0

        emli = []
        for curp in range(pages):
            myembed = makeembed(currentpage*5-5, currentpage*5, pages, currentpage)
            emli.append(myembed)
            currentpage += 1

        if pages > 1:
            msg = await ctx.send(embed=emli[cursor])
            await attachreaction(msg)
        else: msg = await ctx.send(embed=emli[cursor], delete_after=21); return

        def UM_check(reaction, user):
            return user.id == ctx.message.author.id and reaction.message.id == msg.id

        while True:
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=20, check=UM_check)
                if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                    cursor += 1
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U00002b05" and cursor > 0:
                    cursor -= 1
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U000023ee" and cursor != 0:
                    cursor = 0
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                    cursor = pages - 1
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
            except asyncio.TimeoutError:
                await msg.delete(); return

    @commands.command(aliases=['edu'])
    @commands.cooldown(1, 10, type=BucketType.user)
    async def education(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        cur_X, cur_Y = await self.quefe(f"SELECT cur_X, cur_Y FROM personal_info WHERE id='{str(ctx.message.author.id)}';")
        if not await self.area_scan(ctx, cur_X, cur_Y): await ctx.send("<:osit:544356212846886924> Educating facilities are only available within **Peace Belt**!"); return

        cmd_tag = 'edu'
        degrees = ['elementary', 'middleschool', 'highschool', 'associate', 'bachelor', 'master', 'doctorate']
        major = ['astrophysic', 'biology', 'chemistry', 'georaphy', 'mathematics', 'physics', 'education', 'archaeology', 'history', 'humanities', 'linguistics', 'literature', 'philosophy', 'psychology', 'management', 'international_bussiness', 'elemology', 'electronics', 'robotics', 'engineering']
 
        try: resp = args[0]
        except IndexError: await ctx.send(f":books: Welcome to **Ascending Sanctuary of Siegfields**. Please, take time and have a look.\n:books: **`{'` ➠ `'.join(degrees)}`**"); return

        # Check if the previous course has been finished yet
        if not await self.__cd_check(ctx.message, cmd_tag, f":books: *Enlightening requires one's most persevere and patience.*"): return

        def UMC_check(m):
            return m.channel == ctx.channel and m.author == ctx.author 

        try:
            temp1 = await ctx.send(f":bulb: ... and what major would you prefer?\n| **`{'` · `'.join(major)}`**")

            try: resp2 = await self.client.wait_for('message', check=UMC_check, timeout=20)
            # E: No respond
            except asyncio.TimeoutError: await ctx.send(":books: May the Olds look upon you..."); return
            # Major check
            if resp2.content.lower() not in major: await ctx.send(f"<:osit:544356212846886924> Invalid major!"); return

            await temp1.delete()

            price, INTT_require, INTT_reward, degree_require, duration = await self.quefe(f"SELECT price, INTT_require, INTT_reward, degree_require, duration FROM model_degree WHERE degree='{resp.lower()}';")
            degree_require = degree_require.split(' of ')

            # DEGREE (and MAJOR) check
            query = f"SELECT money, INTT FROM personal_info WHERE EXISTS (SELECT * FROM pi_degrees WHERE user_id='{ctx.author.id}' AND degree='{degree_require[0]}'"

            try:
                try: money, INTT = await self.quefe(query + f" AND major='{degree_require[1]}') AND id='{ctx.author.id}';")
                # E: No major required
                except IndexError: money, INTT = await self.quefe(query + f") AND id='{ctx.author.id}';")
            # E: Query return NONE
            except TypeError: await ctx.send(f"<:osit:544356212846886924> Your application does not meet the degree/major requirements, **{ctx.message.author.name}**."); return

            # MONEY and INTT check
            if money < price: await ctx.send(f"<:osit:544356212846886924> You need **<:36pxGold:548661444133126185>{price}** to enroll this program!"); return
            if INTT < INTT_require: await ctx.send(f"<:osit:544356212846886924> You need **{INTT_require}**`INT` to enroll this program!"); return
            
            temp2 = await ctx.send(f":books: Program for `{resp.capitalize()} of {resp2.content.capitalize()}`:\n| **Price:** <:36pxGold:548661444133126185>{price}\n| **Duration:** {duration/7200} months\n**Result:** · **`{resp.capitalize()} of {resp2.content.capitalize()}`** · `{INTT_reward}` INT. \n:bell: Do you wish to proceed? (Key: `enroll confirm` | Timeout=15s)")

            def UMCc_check(m):
                return m.channel == ctx.channel and m.author == ctx.author and m.content.lower() == 'enroll confirm'

            try: await self.client.wait_for('message', timeout=15, check=UMCc_check)
            except asyncio.TimeoutError: await ctx.send(f"<:osit:544356212846886924> Assignment session of {ctx.message.author.mention} is closed."); return
            await temp2.delete()

            # Initialize
            try: await _cursor.execute(f"INSERT INTO pi_degrees VALUES ('{ctx.author.id}', '{resp.lower()}', '{resp2.content.lower()}');")
            except AttributeError: await _cursor.execute(f"INSERT INTO pi_degrees VALUES ('{str(ctx.message.author.id)}', '{resp.lower()}', NULL);")
            await _cursor.execute(f"UPDATE personal_info SET INTT={INTT + INTT_reward}, STA=0, money={money - price} WHERE id='{ctx.author.id}';")
            # Cooldown set
            await ctx.send(f":white_check_mark: **<:36pxGold:548661444133126185>{price}** has been deducted from your account.")
            await self.client.loop.run_in_executor(None, partial(redio.set, f'{cmd_tag}{ctx.author.id}', 'degreeing', ex=duration, nx=True))

        # E: Invalid degree
        except ZeroDivisionError: await ctx.send("<:osit:544356212846886924> Invalid degree!"); return

    @commands.command(aliases=['med'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def medication(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        cur_X, cur_Y, LP, MAX_LP, money = await self.quefe(f"SELECT cur_X, cur_Y, LP, MAX_LP, money FROM personal_info WHERE id='{str(ctx.message.author.id)}'")

        if not await self.area_scan(ctx, cur_X, cur_Y): await ctx.send("<:osit:544356212846886924> Medical treatments are only available within **Peace Belt**!"); return

        reco = MAX_LP - LP
        if reco == 0: await ctx.send(f"<:osit:544356212846886924> **{ctx.message.author.name}**, your current LP is at max!"); return

        reco_scale = reco//(MAX_LP/20)
        if reco_scale == 0: reco_scale = 1
        
        cost = int(reco*reco_scale)

        def UMCc_check(m):
            return m.channel == ctx.channel and m.content == 'treatment confirm' and m.author == ctx.author

        # Inform
        await ctx.send(f"<:healing_heart:508220588872171522> Dear {ctx.message.author.mention},\n------------\n· Your damaged scale: `{reco_scale}`\n· Your LP requested: `{reco}`\n· Price: <:36pxGold:548661444133126185>`{reco_scale}/LP`\n· Cost: <:36pxGold:548661444133126185>`   {cost}`\n------------\nPlease type `treatment confirm` within 20s to receive the treatment.")
        try: await self.client.wait_for('message', check=UMCc_check, timeout=20)
        except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Treatment is declined!"); return
        if money < cost: await ctx.send("<:osit:544356212846886924> Insufficient balance!"); return

        # Treat
        await _cursor.execute(f"UPDATE personal_info SET money={money - cost}, LP={MAX_LP}")
        await ctx.send(f"<:healing_heart:508220588872171522> **<:36pxGold:548661444133126185>{cost}** has been deducted from your account, **{ctx.message.author.name}**!"); return

    @commands.command(aliases=['evo'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def evolve(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        perks, evo, LP = await self.quefe(f"SELECT perks, EVO, LP FROM personal_info WHERE id='{ctx.author.id}';")

        raw = list(args)


        evo_dict = {'lp': f"UPDATE personal_info SET MAX_LP=MAX_LP+ROUND(MAX_LP/100*5), EVO=EVO+1, perks=perks-1 WHERE id='{ctx.author.id}' AND perks>0;",
                    'sta': f"UPDATE personal_info SET MAX_STA=MAX_STA+ROUND(MAX_STA/100*10), EVO=EVO+1, perks=perks-1 WHERE id='{str(ctx.message.author.id)}' AND perks>0;",
                    'str': f"UPDATE personal_info SET STR=STR+0.1, EVO=EVO+1, perks=perks-1 WHERE id='{str(ctx.message.author.id)}' AND perks>0;",
                    'int': f"UPDATE personal_info SET INTT=INTT+0.1, EVO=EVO+1, perks=perks-1 WHERE id='{str(ctx.message.author.id)}' AND perks>0;",
                    'flame': f"UPDATE personal_info SET au_FLAME=au_FLAME+0.05, EVO=EVO+1, perks=perks-1 WHERE id='{str(ctx.message.author.id)}' AND perks>0;",
                    'ice': f"UPDATE personal_info SET au_ICE=au_ICE+0.05, EVO=EVO+1, perks=perks-1 WHERE id='{str(ctx.message.author.id)}' AND perks>0;",
                    'holy': f"UPDATE personal_info SET au_HOLY=au_HOLY+0.05, EVO=EVO+1, perks=perks-1 WHERE id='{str(ctx.message.author.id)}' AND perks>0;",
                    'dark': f"UPDATE personal_info SET au_DARK=au_DARK+0.05, EVO=EVO+1, perks=perks-1 WHERE id='{str(ctx.message.author.id)}' AND perks>0;",
                    'charm': f"UPDATE personal_info SET charm=charm+1, perks=perks-1 WHERE id='{str(ctx.message.author.id)}' AND perks>0;"}

        try:
            if raw[0] == 'transfuse':
                if evo < 6: await ctx.send(f"<:osit:544356212846886924> Your evolution has to be more than 6 to proceed transfusion!"); return
                if perks == 0: await ctx.send(f"<:osit:544356212846886924> You have no perks."); return
                try: target = ctx.message.mentions[0]
                except IndexError: await ctx.send("<:osit:544356212846886924> Please mention the one you want!"); return

                t_evo = await self.quefe(f"SELECT EVO FROM personal_info WHERE id='{target.id}';")
                if not t_evo: await ctx.send("<:osit:544356212846886924> User has not incarnated yet!"); return

                rate = abs(evo - t_evo)
                if rate == 10: rate = 0
                if rate > 10: rate = 10
                if await self.percenter(9 - rate):
                    await ctx.send("<:zapp:524893958115950603> Transfusion succeeded!")
                    await _cursor.execute(f"UPDATE personal_info SET perks=perks-1 WHERE id='{ctx.author.id}'; UPDATE personal_info SET EVO=EVO+1 WHERE id='{target.id}';"); return
                else:
                    try: loss = round(LP/(10 - rate))
                    except ZeroDivisionError: loss = 1

                    await ctx.send(f"<:osit:544356212846886924> Transfusion failed! You've lost **{loss} LP**, **{ctx.author.name}** and **{target.name}**.")
                    await _cursor.execute(f"UPDATE personal_info SET LP=LP-{loss} WHERE id='{ctx.author.id}' OR id='{target.name}';"); return

            elif raw[0] == 'mutate':
                msg = await ctx.send(f"<:zapp:524893958115950603> All your basic status will *randomly change*. You may even die.\n:bell: **ARE**. **YOU**. **SURE**?")

                await msg.add_reaction("\U00002705")

                def UM_check(reaction, user):
                    return user.id == ctx.author.id and reaction.message.id == msg.id

                try: await self.client.wait_for('reaction_add', timeout=20, check=UM_check)
                except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request decline!"); return

                LP, MAX_LP, STA, STR, INT = await self.quefe(f"SELECT LP, MAX_LP, STA, STR, INT FROM personal_info WHERE id='{ctx.author.id}';")
                await _cursor.execute(f"UPDATE personal_info SET perks=perks-1, LP={random.randint(0, LP*2)}, MAX_LP={random.randint(0, MAX_LP*2)}, STA={random.randint(0, STA*2)}, STR={random.randint(0, round(STR*2))}, INT={random.randint(0, round(INT*2))} WHERE id='{ctx.author.id}';")
                await ctx.send("<:osit:544356212846886924> Mutation succeed! Check your profile immidiately..."); return


            if await _cursor.execute(evo_dict[raw[0].lower()]) == 0: await ctx.send("<:osit:544356212846886924> Not enough perks!"); return

        # E: Attributes not found
        except KeyError: await ctx.send("<:osit:544356212846886924> Invalid attribute!"); return

        # E: Attri not given
        except IndexError: await ctx.send(f"<:zapp:524893958115950603> Perks can be spent on your attributes:\n________________________\n**|** `LP` · +5% MAX_LP \n**|** `STA` · +10% MAX_STA \n**|** `STR` · +0.1 STR\n**|** `INT` · +0.1 INT\n**|** `FLAME` · +0.05 aura \n**|** `ICE` · +0.05 aura \n**|** `HOLY` · +0.05 aura \n**|** `DARK` · +0.05 aura\n**|** `CHARM` · +0.01 CHARM \n________________________\n**Your perks:** {perks}\n**Your evolution:** {evo}"); return

        await ctx.send("<:zapp:524893958115950603> Done. You may use `profile` to check.")

    @commands.command()
    @commands.cooldown(1, 60, type=BucketType.user)
    async def infuse(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        raw = list(args)

        try:
            # Item's info get
            try:
                w_name, w_evo = await self.quefe(f"SELECT name, evo FROM pi_inventory WHERE existence='GOOD' AND user_id='{str(ctx.message.author.id)}' AND item_id='{raw[0]}';")
                t_w_quantity, t_w_infuse_query, t_w_evo = await self.quefe(f"SELECT quantity, infuse_query, evo FROM pi_inventory WHERE existence='GOOD' AND user_id='{str(ctx.message.author.id)}' AND item_id='{raw[1]}';")
            # E: Item's not found
            except TypeError: await ctx.send("<:osit:544356212846886924> Item's not found!"); return

            if not t_w_infuse_query: await ctx.send(f"<:osit:544356212846886924> The second item cannot be used as an infusion's ingredient"); return

            # Quantity check
            quantity = 1
            if w_evo != t_w_evo:
                if w_evo > t_w_quantity: await ctx.send(f"<:osit:544356212846886924> You need a quantity of **{w_evo}** to infuse the item.") ; return
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

                d_check = f"AND EXISTS (SELECT * FROM pi_degrees WHERE user_id='{str(ctx.message.author.id)}' AND degree='{inflv_dict[w_evo][0]}' AND major='{inflv_dict[w_evo][1]}');"
            except KeyError: d_check = ''

            # Preparing
            t_w_infuse_query = t_w_infuse_query.replace('user_id_here', str(ctx.message.author.id)).replace('item_id_here', raw[0])

            # INFUSE
            if await _cursor.execute(f"{t_w_infuse_query} {d_check};") == 0: await ctx.send(f"<:osit:544356212846886924> You cannot infuse EVO`{w_evo}` item with your current status."); return

            # Remove
            if quantity == t_w_quantity: await _cursor.execute(f"UPDATE pi_inventory SET existence='BAD' WHERE user_id='{ctx.author.id}' AND item_id='{raw[1]}';")
            else: await _cursor.execute(f"UPDATE pi_inventory SET quantity=quantity-{quantity} WHERE user_id='{str(ctx.message.author.id)}' AND item_id='{raw[1]}';")

            # Inform :>
            await ctx.send(f":white_check_mark: Infusion with `{raw[0]}`|**{w_name}** was a success. The other item has been destroyed."); return

        # E: Not enough args
        except IndexError: await ctx.send("<:osit:544356212846886924> What? You think you can infuse thing out of nowhere?"); return

    @commands.command()
    @commands.cooldown(1, 60, type=BucketType.user)
    async def merge(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        cmd_tag = 'merge'
        raw = list(args)

        # Check if the previous course has been finished yet
        if not await self.__cd_check(ctx.message, cmd_tag, f"No."): return

        try:
            # Item's info get
            try:
                w_name, w_evo, w_weight, w_defend, w_multiplier, w_str, w_intt, w_sta, w_speed, w_acc_randomness, w_acc_range, w_r_min, w_r_max, w_firing_rate, w_dmg, w_stealth = await self.quefe(f"SELECT name, evo, weight, defend, multiplier, str, intt, sta, speed, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth FROM pi_inventory WHERE existence='GOOD' AND user_id='{str(ctx.message.author.id)}' AND item_id='{raw[0]}';")
                t_w_evo, t_w_weight, t_w_defend, t_w_multiplier, t_w_str, t_w_intt, t_w_sta, t_w_speed, t_w_acc_randomness, t_w_acc_range, t_w_r_min, t_w_r_max, t_w_firing_rate, t_w_dmg, t_w_stealth = await self.quefe(f"SELECT evo, weight, defend, multiplier, str, intt, sta, speed, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth FROM pi_inventory WHERE existence='GOOD' AND user_id='{str(ctx.message.author.id)}' AND item_id='{raw[1]}';")
            # E: Item's not found
            except TypeError: await ctx.send("<:osit:544356212846886924> Item's not found!"); return

            # Degrees
            degrees = await self.quefe(f"SELECT degree FROM pi_degrees WHERE user_id='{str(ctx.message.author.id)}' AND major='engineering';"); degrees = set(degrees)

            # Price
            price = (abs(w_evo - t_w_evo)*1000)//10*(10 - len(degrees))

            def UMCc_check(m):
                return m.channel == ctx.channel and m.content == 'merging confirm' and m.author == ctx.author

            await ctx.send(f":tools: Merching these two items will cost you **<:36pxGold:548661444133126185>{price}**.\n:bell: Proceed? (Key: `merging confirmation` | Timeout=20s)")
            try: await self.client.wait_for('message', timeout=20, check=UMCc_check)
            except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request timeout!"); return

            # Deduct money
            if await _cursor.execute(f"UPDATE personal_info SET money=money-{price} WHERE id'{str(ctx.message.author.id)}' AND money >= {price};") == 0:
                await ctx.send("<:osit:544356212846886924> Insufficient balance!"); return

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
            await _cursor.execute(f"UPDATE pi_inventory SET weight={W_weight}, defend={W_defend}, multiplier={W_multiplier}, str={W_str}, intt={W_intt}, sta={W_sta}, speed={W_speed}, accuracy_randomness={W_acc_randomness}, accuracy_range={W_acc_range}, range_min={W_r_min}, range_max={W_r_max}, firing_rate={W_firing_rate}, dmg={W_dmg}, stealth={W_stealth} WHERE user_id='{str(ctx.message.author.id)}' AND item_id='{raw[0]}';")
            await _cursor.execute(f"UPDATE pi_inventory SET weight={W_weight}, defend={W_defend}, multiplier={W_multiplier}, str={W_str}, intt={W_intt}, sta={W_sta}, speed={W_speed}, accuracy_randomness={W_acc_randomness}, accuracy_range={W_acc_range}, range_min={W_r_min}, range_max={W_r_max}, firing_rate={W_firing_rate}, dmg={W_dmg}, stealth={W_stealth} WHERE user_id='{str(ctx.message.author.id)}' AND item_id='{raw[1]}';")

            # Inform :>
            await ctx.send(f":white_check_mark: Merged `{raw[0]}`|**{w_name}** with `{raw[0]}`|**{w_name}**!")
            await self.client.loop.run_in_executor(None, partial(redio.set, f'{cmd_tag}{str(ctx.message.author.id)}', 'merging', ex=7200, nx=True))

        # E: Not enough args
        except IndexError: await ctx.send("<:osit:544356212846886924> How could you even merge something with its own?!"); return

    @commands.command()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def hunt(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        try: end_point, stats, final_rq, final_rw = await self.quefe(f"SELECT end_point, stats, reward_query, rewards FROM pi_hunt WHERE user_id='{ctx.author.id}';")
        except TypeError: stats = 'DONE'

        if stats == 'DONE':
            raw = list(args)

            STR, INTT, STA = await self.quefe(f"SELECT STR, INTT, STA FROM personal_info WHERE id='{ctx.author.id}';")

            # Get hunt limitation
            try:
                limit = int(raw[0])
                if limit >= STA: limit = STA - 1
            except (IndexError, ValueError): limit = STA - 1

            if limit <= 0: await ctx.send(f"Go *get some food*, **{ctx.message.author.name}** <:fufu:508437298808094742> We cannot start a hunt with you exhausted like that."); return

            # Get animals based on INTT
            anis = await self.quefe(f"SELECT ani_code, str, sta, aggro, rewards, reward_query FROM model_animal WHERE intt<={INTT};", type='all')


            # Reward generating
            rewards = '\n'; reward_query = ''
            while STA > limit:
                # Get target
                target = random.choice(anis)

                # Decrease STA
                STA -= target[2]

                # Rate calc
                rate = STR - target[1]
                if rate > 1: rate = target[3]//rate
                elif rate < 1:
                    rate = round(target[3]*abs(rate))
                    if rate == 1: rate = 2
                elif rate == 1: rate = target[3]

                # Decide if session is success
                if random.choice(range(rate)) != 0: continue

                rewards = rewards + f"★ {target[4]}\n"
                reward_query = reward_query + f" {target[5]}"

            # Reward_query preparing
            if reward_query:
                tem_que = reward_query
                reward_query = reward_query.replace('user_id_here', f"{ctx.author.id}")
                comrades = await self.quefe(f"SELECT user_id FROM pi_party WHERE party_id=(SELECT party_id FROM pi_party WHERE user_id='{ctx.author.id}');", type='all')
                for comrade in comrades:
                    reward_query = reward_query + tem_que.replace('user_id_here', f"{comrade[0]}")
                if comrades: rewards = rewards + f"And **{len(comrades)}** comrades of yours will receive the same."

            # Duration calc     |      End_point calc
            duration = 60*limit//STR
            end_point = datetime.now() + timedelta(seconds=duration)
            end_point = end_point.strftime('%Y-%m-%d %H:%M:%S')

            # Insert
            if await _cursor.execute(f"""UPDATE pi_hunt SET stats='ONGOING', end_point='{end_point}', reward_query="{reward_query}", rewards='{rewards}' WHERE user_id='{ctx.author.id}';""") == 0:
                await _cursor.execute(f"""INSERT INTO pi_hunt VALUES ('{ctx.author.id}', '{end_point}', 'ONGOING', '{rewards}', "{reward_query}");""")
            await _cursor.execute(f"UPDATE personal_info SET STA=STA-{limit} WHERE id='{ctx.author.id}';")
            await ctx.send(f":cowboy: Hang tight, **{ctx.author.name}**! The hunt will end after **`{timedelta(seconds=duration)}`**."); return

        else:

            # Two points comparison
            delta = relativedelta(end_point, datetime.now())
            if datetime.now() < end_point: await ctx.send(f":cowboy: Hold right there, {ctx.message.author.name}! Come back after **`{delta.hours:02d}:{delta.minutes:02d}:{delta.seconds:02d}`**"); return

            # Rewarding
            if final_rq:
                await _cursor.execute(final_rq)
            await _cursor.execute(f"UPDATE pi_hunt SET stats='DONE' WHERE user_id='{ctx.author.id}';")
            await ctx.send(f":cowboy: Congrats, **{ctx.message.author.name}**. You've finished your hunt!{final_rw}"); return

    @commands.command(aliases=['sleep'])
    @commands.cooldown(3, 60, type=BucketType.user)
    async def rest(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        cur_X, cur_Y= await self.quefe(f"SELECT cur_X, cur_Y FROM personal_info WHERE id='{ctx.author.id}';")
        if not await self.area_scan(ctx, cur_X, cur_Y): await ctx.send("<:osit:544356212846886924> No you cannot rest outside of **Peace Belt**!"); return

        try:
            stats, rest_point = await self.quefe(f"SELECT stats, rest_point FROM pi_rest WHERE user_id='{ctx.author.id}';")
            if stats == 'REST': await ctx.send(f"<:osit:544356212846886924> You're already resting, **{ctx.author.name}**."); return 
        except TypeError: pass

        rest_point = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if await _cursor.execute(f"UPDATE pi_rest SET stats='REST', rest_point='{rest_point}' WHERE user_id='{ctx.author.id}'; UPDATE personal_info SET STA=0 WHERE id='{ctx.author.id}';") == 0:
            await _cursor.execute(f"INSERT INTO pi_rest VALUES ('{ctx.author.id}', 'REST', '{rest_point}'); UPDATE personal_info SET STA=0 WHERE id='{ctx.author.id}';")

        await ctx.send(f"<:zzzz:544354429315579905> Rested at `{rest_point}`"); return

    @commands.command(aliases=['awake'])
    @commands.cooldown(3, 60, type=BucketType.user)
    async def wake(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        cur_X, cur_Y, charm, MAX_STA, MAX_LP, LP = await self.quefe(f"SELECT cur_X, cur_Y, charm, MAX_STA, MAX_LP, LP FROM personal_info WHERE id='{ctx.author.id}';")
        if not await self.area_scan(ctx, cur_X, cur_Y): await ctx.send("<:osit:544356212846886924> No you cannot rest outside of **Peace Belt**!"); return

        rest_point = await self.quefe(f"SELECT rest_point FROM pi_rest WHERE user_id='{ctx.author.id}' AND stats='REST';")
        try: rest_point = rest_point[0]
        except TypeError: await ctx.send(f"<:osit:544356212846886924> You're not sleeping, **{ctx.author.name}**"); return

        delta = relativedelta(datetime.now(), rest_point)
        reco_rate = LP/(MAX_LP/2)
        if reco_rate < 0.25: reco_rate = 0.25

        duration = delta.minutes+(delta.hours*60)+(delta.days*1440)
        sta_receive = round(reco_rate*(duration/(charm/60)))
        if sta_receive > MAX_STA: sta_receive = MAX_STA

        msg = await ctx.send(f":bell: You've rested for `{duration}` minutes, **{ctx.author.name}**. Get **{sta_receive} STA**?")
        def UM_check(reaction, user):
            return user.id == ctx.author.id and reaction.message.id == msg.id and reaction.emoji == '\U00002600'

        await msg.add_reaction("\U00002600")
        try: await self.client.wait_for('reaction_add', timeout=10, check=UM_check)
        except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request timed out."); return

        await _cursor.execute(f"UPDATE personal_info SET STA={sta_receive} WHERE id='{ctx.author.id}'; UPDATE pi_rest SET stats='AWAKE' WHERE user_id='{ctx.author.id}';")
        await ctx.send(f":sunrise_over_mountains: Beneath piles of cotton growling an annoying voice... *Groaaarrr!* Good.. morning? You've recovered **{sta_receive}**`STA`!"); return

    @commands.command()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def craft(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        if not args: await ctx.send(":tools: Craft? Cook? Anything you want~!"); return

        raw = list(args)
        pack_values = []

        # Get packs
        packs = raw[0].split('+')
        # Get pack
        for pack in packs:
            # Split pack --> [item_id, quantity]
            pack = pack.split('*')
            # Get item_id
            try: item_id = int(pack[0])
            except (IndexError, TypeError): await ctx.send(f"<:osit:544356212846886924> Missing item's id"); return
            except ValueError: await ctx.send(f"<:osit:544356212846886924> Invalid item's id"); return
            # Get quantity
            try: quantity = int(pack[1])
            except ValueError: await ctx.send(f"<:osit:544356212846886924> Invalid item's id"); return
            except (IndexError, TypeError): quantity = 1

            # Get craft_value
            craft_value = await self.quefe(f"SELECT craft_value FROM pi_inventory WHERE existence='GOOD' AND user_id='{ctx.author.id}' AND item_id={item_id} AND quantity>={quantity};")

            # Calculate each pack
            try: pack_values.append(craft_value[0]*quantity)
            except TypeError: await ctx.send(f"<:osit:544356212846886924> You don't have **{quantity}** item `{item_id}`. Please check your *item's id* or *its quantity*."); return
        # Calculate total craft_value
        total_cv = sum(pack_values)

        # Get FORMULA
        try: check_query, effect_query, info_msg = await self.quefe(f"SELECT check_query, effect_query, info_msg FROM model_formula WHERE formula_value={total_cv};")
        except TypeError: await ctx.send(":tools: Oops! You tried but nothing happened :<"); return

        info_msg = info_msg.split(' || ')
        if check_query:
            check_query = check_query.replace('user_id_here', f"{ctx.author.id}")
            if _cursor.execute(check_query) == 0: await ctx.send(f":tools: Oops! {info_msg[1]} :<"); return

        effect_query = effect_query.replace('user_id_here', f"{ctx.author.id}")

        # Take effect (reward, effect, etc.)
        if await _cursor.execute(effect_query) == 0: await ctx.send(f":tools: Oops! {info_msg[1]} :<"); return
        
        # Inform
        await ctx.send(f":tools: {info_msg[0]} **Successfully crafted!**")

    @commands.command(aliases=['crafts'])
    @commands.cooldown(1, 10, type=BucketType.user)
    async def formulas(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        # FORMULA
        try:
            if args[0].startswith('fm'):
                try: formula_code, name, formula_value, description, tags, kit = await self.quefe(f"SELECT formula_code, name, formula_value, description, tags, kit FROM model_formula WHERE formula_code='{args[0]}';")
                except TypeError: await ctx.send(":tools: Formula not found!"); return
            
            temb = discord.Embed(title=f":tools: `{formula_code}`|**{name}**", description=f"""```{description}```""", colour = discord.Colour(0x011C3A))
            temb.add_field(name=f'╟ K I T [{formula_value}]', value=f'╟ {kit}', inline=True)
            temb.add_field(name=f'╟ T A G S', value=f"╟ `{tags.replace(' - ', '` · `')}`", inline=True)

            await ctx.send(embed=temb, delete_after=15)

        except IndexError:

            formus = await self.quefe(f"SELECT formula_code, description, tags FROM model_formula;", type='all')

            def makeembed(top, least, pages, currentpage):
                line = ''

                for formu in formus[top:least]:
                    line = line + f"╟ `{formu[0]}` | **`{formu[1]}`** | `{formu[2].replace(' - ', '` `')}`\n"

                reembed = discord.Embed(colour = discord.Colour(0x011C3A), description=line)
                reembed.set_footer(text=f"------ {currentpage}/{pages} ------")
                return reembed
                #else:
                #    await ctx.send("*Nothing but dust here...*")
            
            async def attachreaction(msg):
                await msg.add_reaction("\U000023ee")    #Top-left
                await msg.add_reaction("\U00002b05")    #Left
                await msg.add_reaction("\U000027a1")    #Right
                await msg.add_reaction("\U000023ed")    #Top-right

            pages = len(formus)//10
            if len(formus)%10 != 0: pages += 1
            currentpage = 1
            cursor = 0

            emli = []
            for curp in range(pages):
                myembed = makeembed(currentpage*10-10, currentpage*10, pages, currentpage)
                emli.append(myembed)
                currentpage += 1

            if pages > 1: 
                msg = await ctx.send(embed=emli[cursor])
                await attachreaction(msg)
            else: msg = await ctx.send(embed=emli[cursor], delete_after=21); return

            def UM_check(reaction, user):
                return user.id == ctx.message.author.id and reaction.message.id == msg.id

            while True:
                try:    
                    reaction, user = await self.client.wait_for('reaction_add', timeout=20, check=UM_check)
                    if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                        cursor += 1
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                    elif reaction.emoji == "\U00002b05" and cursor > 0:
                        cursor -= 1
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                    elif reaction.emoji == "\U000023ee" and cursor != 0:
                        cursor = 0
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                    elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                        cursor = pages - 1
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                except asyncio.TimeoutError:
                    await msg.delete(); return







# ============= COMMERCIAL ================
# <!> CONCEPTS 
# <dir> acts as an id/ (type:list) used to look up the self.data.item   (aka. address)
# a <dir> (type:list) contains these info, respectively: [data_class][item_class][category][obj's id] e.g. item.arsenal.pistol.1v
# Main weapon is a inventory <dir>      |      ['item'][]

    @commands.command(aliases=['s'])
    @commands.cooldown(1, 5, type=BucketType.user)    
    async def shop(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        cur_PLACE, cur_X, cur_Y = await self.quefe(f"SELECT cur_PLACE, cur_X, cur_Y FROM personal_info WHERE id='{str(ctx.message.author.id)}';")
        if not await self.area_scan(ctx, cur_X, cur_Y): await ctx.send("<:osit:544356212846886924> Shops are only available within **Peace Belt**!"); return

        # INSPECT ===============
        raw = list(args)
        try:
            # Get goods
            ## Regions
            try: goods, environ_name = await self.quefe(f"SELECT goods, name FROM environ WHERE environ_code='{cur_PLACE}';")
            ## Lands
            except TypeError:
                goods, environ_name = await self.quefe(f"SELECT goods, name FROM pi_land WHERE land_code='{cur_PLACE}';")
                if not goods: await ctx.send("There's not been goods through here, it seems..."); return
            goods = goods.replace(' - ', "', '")
            # Get info
            try:
                item_code, name, description, tags, weight, defend, multiplier, strr, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, aura, illulink, price = await self.quefe(f"""SELECT item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, aura, illulink, price FROM model_item WHERE '{raw[0]}' IN ('{goods}') AND  item_code='{raw[0]}';""")

                # Pointer
                if 'magic' in tags: pointer = ':crystal_ball:'
                else: pointer = '<:gun_pistol:508213644375621632>'
                # Aura icon
                aui = {'FLAME': 'https://imgur.com/3UnIPir.png', 'ICE': 'https://imgur.com/7HsDWfj.png', 'HOLY': 'https://imgur.com/lA1qfnf.png', 'DARK': 'https://imgur.com/yEksklA.png'}

                line = f""":scroll: **`『Weight』` ·** {weight} ⠀ ⠀:scroll: **`『Price』` ·** {price}\n\n```"{description}"```\n"""
                
                reembed = discord.Embed(title=f"`{item_code}`|**{' '.join([x for x in name.upper()])}**", colour = discord.Colour(0x011C3A), description=line)
                reembed.add_field(name=":scroll: Basic Status <:broadsword:508214667416698882>", value=f"**`『STR』` ·** {strr}\n**`『INT』` ·** {intt}\n**`『STA』` ·** {sta}\n**`『MULTIPLIER』` ·** {multiplier}\n**`『DEFEND』` ·** {defend}\n**`『SPEED』` ·** {speed}", inline=True)

                try: acc_per = 10//accuracy_randomness
                except ZeroDivisionError: acc_per = 0
                reembed.add_field(name=f":scroll: Projector Status {pointer}", value=f"**`『RANGE』` ·** {range_min} - {range_max}m\n**`『STEALTH』` ·** {stealth}\n**`『FIRING-RATE』` ·** {firing_rate}\n**`『ACCURACY』` ·** {acc_per}%/{accuracy_range}m\n**-------------------**\n**`『ROUND』` ·** {round} \n**`『DMG』` ·** {dmg}", inline=True)

                reembed.set_thumbnail(url=aui[aura])
                if illulink != 'n/a': reembed.set_image(url=illulink)

                await ctx.send(embed=reembed); return
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

            if not items: await ctx.send(f":x: No result..."); return

            def makeembed(top, least, pages, currentpage):

                line = f"**╔═══════╡**`Total: {len(items)}`**╞═══════**\n" 

                for item in items[top:least]:
                    if 'melee' in item[3]:
                        icon = '<:broadsword:508214667416698882>'
                        #line = line + f""" `{item_code}` <:broadsword:508214667416698882> **{items[item_code].name}** | *"{items[item_code].description}"*\n| `『Multiplier』{items[item_code].multiplier}` · `『Speed』{items[item_code].speed}` · `『STA』{items[item_code].sta}` \n| **`Required`** STR-{items[item_code].str}\n| **`Price`** <:36pxGold:548661444133126185>{items[item_code].price}\n++ `{'` `'.join(items[item_code].tags)}`\n\n"""
                    elif 'range_weapon' in item[3]:
                        icon = '<:gun_pistol:508213644375621632>'
                        #line = line + f""" `{item_code}` <:gun_pistol:508213644375621632> **{items[item_code].name}** | *"{items[item_code].description}"*\n| `『Range』{items[item_code].range[0]}m - {items[item_code].range[1]}m`\n| `『Accuracy』1:{items[item_code].accuracy[0]}/{items[item_code].accuracy[1]}m` · `『firing_rate』{items[item_code].firing_rate}` · `『stealth』{items[item_code].stealth}`\n| **`Required`** STR-{items[item_code].str}/shot · STA-{items[item_code].sta}\n| **`Price`**<:36pxGold:548661444133126185>{items[item_code].price}\n++ `{'` `'.join(items[item_code].tags)}`\n\n"""
                    elif 'ammunition' in item[3]:
                        icon = '<:shotgun_slug:508217929532440586>'
                        #line = line + f""" `{item_code}` <:shotgun_slug:508217929532440586> **{items[item_code].name}** | *"{items[item_code].description}"*\n| `『Damage』{items[item_code].dmg}` · `『Speed』{items[item_code].speed}`\n| **`Price`** <:36pxGold:548661444133126185>{items[item_code].price}\n++ `{'` `'.join(items[item_code].tags)}`\n\n"""
                    elif 'supply' in item[3]:
                        icon = ':small_orange_diamond:'
                        #line = line + f""" `{item_code}` :small_orange_diamond: **{items[item_code].name}** \n| *"{items[item_code].description}"*\n| **`Price`** <:36pxGold:548661444133126185>{items[item_code].price}\n++ `{'` `'.join(items[item_code].tags)}`\n\n"""
                    line = line + f""" `{item[0]}` {icon} `{item[7]}`|**{item[1]}**\n╟ *"{item[2]}"*\n╟** `『Weight』{item[4]}`** · **`『Price』`<:36pxGold:548661444133126185>`{item[6]}/{item[5]}`**\n**╟╼**`{item[3].replace(' - ', '`·`')}`\n\n"""

                line = line + f"**╚═════════╡**`{currentpage}/{pages}`**╞══════════**"

                reembed = discord.Embed(title = f":shopping_cart: SIEGFIELD's Market of `{cur_PLACE}|{environ_name}`", colour = discord.Colour(0x011C3A), description=line)
                
                if line == "**╔═══════╡**`Total: 0`**╞═══════**\n**╚═════════╡**`0/0`**╞══════════**": return False
                else: return reembed
                #else:
                #    await ctx.send("*Nothing but dust here...*")
            
            async def attachreaction(msg):
                await msg.add_reaction("\U000023ee")    #Top-left
                await msg.add_reaction("\U00002b05")    #Left
                await msg.add_reaction("\U000027a1")    #Right
                await msg.add_reaction("\U000023ed")    #Top-right

            pages = int(len(items)/5)
            if len(items)%5 != 0: pages += 1
            currentpage = 1
            cursor = 0

            emli = []
            for curp in range(pages):
                myembed = makeembed(currentpage*5-5, currentpage*5, pages, currentpage)
                emli.append(myembed)
                currentpage += 1

            msg = await ctx.send(embed=emli[cursor])
            if pages > 1: await attachreaction(msg)
            else: return

            def UM_check(reaction, user):
                return user.id == ctx.author.id and reaction.message.id == msg.id

            while True:
                try:
                    reaction, user = await self.client.wait_for('reaction_add', timeout=20, check=UM_check)
                    if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                        cursor += 1
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                    elif reaction.emoji == "\U00002b05" and cursor > 0:
                        cursor -= 1
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                    elif reaction.emoji == "\U000023ee" and cursor != 0:
                        cursor = 0
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                    elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                        cursor = pages - 1
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                except asyncio.TimeoutError:
                    break

        await browse()

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)    
    async def buy(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        cur_X, cur_Y, money, cur_PLACE = await self.quefe(f"SELECT cur_X, cur_Y, money, cur_PLACE FROM personal_info WHERE id='{str(ctx.message.author.id)}';")

        if not await self.area_scan(ctx, cur_X, cur_Y): await ctx.send("<:osit:544356212846886924> You can only buy stuff within **Peace Belt**!"); return
        #await self.client.loop.run_in_executor(None, partial(redio.set, f'{cmd_tag}{str(ctx.message.author.id)}', 'working', ex=duration, nx=True))

        raw = list(args); quantity = 1

        try: item_code = raw[0]
        except IndexError: await ctx.send(f"<:osit:544356212846886924> Please provide item's code, **{ctx.message.author.name}**"); return

        try: 
            quantity = int(raw[1])

            # SCAM :)
            if quantity <= 0: await ctx.send("**Heyyyyyyyyy scammer-!**"); return

        # E: Quantity not given, or invalidly given
        except (IndexError, TypeError): pass
        
        # Get goods
        if cur_PLACE.startswith('land.'): goods = await self.quefe(f"SELECT goods FROM pi_land WHERE land_code='{cur_PLACE}';")
        else: goods = await self.quefe(f"SELECT goods FROM environ WHERE environ_code='{cur_PLACE}';")

        if not goods: await ctx.send("<:osit:544356212846886924> Nothing to buy here..."); return

        # GET ITEM INFO
        try:
            name, tags, i_price, i_quantity = await self.quefe(f"""SELECT name, tags, price, quantity FROM model_item WHERE item_code='{item_code}' AND item_code IN ('{goods[0].replace(' - ', "', '")}');""")
            i_tags = tags.split(' - ')
        # E: Item code not found
        except TypeError: await ctx.send("<:osit:544356212846886924> Item_code/Item_id not found!"); return

        # TWO TYPES of obj: Serializable-obj and Unserializable obj
        # Validation
        #if isinstance(self.data['item'][item_code], ingredient): await ctx.send(f"<:osit:544356212846886924> You cannot use this command to obtain the given item, {str(ctx.message.author.id)}. Use `-trade` instead"); return

        # Money check
        if i_price*quantity > money: await ctx.send("<:osit:544356212846886924> Insufficience balance!"); return

        # Deduct money
        await _cursor.execute(f"UPDATE personal_info SET money=money-{i_price*quantity} WHERE id='{str(ctx.message.author.id)}';")

        # Get the real quantity (according to the model_item's quantity)
        quantity = quantity*i_quantity

        # Greeting, of course :)
        await ctx.send(f":white_check_mark: `{quantity}` item **{name}** is successfully added to your inventory! Thank you for shoping!")

        # INCONSUMABLE
        if 'inconsumable' in i_tags:
            # Create item in inventory. Ignore the given quantity please :>
            #await _cursor.execute(f"INSERT INTO pi_inventory SELECT 0, '{str(ctx.message.author.id)}', item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, infuse_query, order_query, passive_query, ultima_query, quantity, price, dmg, stealth, evo, aura, craft_value, illulink FROM model_item WHERE item_code='{item_code}';")
            for i in range(quantity):
                await _cursor.execute(f"SELECT func_it_reward('{ctx.author.id}', '{item_code}', 1);")
            # (MODEL FOR QUERY RECORD-TRANSFERING) ------- await _cursor.execute(f"INSERT INTO pi_inventory SELECT 0, {str(ctx.message.author.id)}, item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, quantity, price, dmg, stealth FROM model_item WHERE item_code='{item_code}';")

        # CONSUMABLE
        else:
            await _cursor.execute(f"SELECT func_it_reward('{ctx.author.id}', '{item_code}', {quantity});")
            # Increase item_code's quantity
            #if await _cursor.execute(f"UPDATE pi_inventory SET quantity=quantity+{quantity} WHERE user_id='{str(ctx.message.author.id)}' AND item_code='{item_code}';") == 0:
            #    # E: item_code did not exist. Create one, with given quantity
            #    await _cursor.execute(f"INSERT INTO pi_inventory SELECT 0, '{str(ctx.message.author.id)}', item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, infuse_query, order_query, passive_query, ultima_query, {quantity}, price, dmg, stealth, evo, aura, craft_value, illulink FROM model_item WHERE item_code='{item_code}';")

    @commands.command(aliases=['i'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def inventory(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        cur_PLACE  = await self.quefe(f"SELECT cur_PLACE FROM personal_info WHERE id='{str(ctx.message.author.id)}';")
        cur_PLACE = cur_PLACE[0]

        # INSPECT ===============
        raw = list(args)
        try:
            # Get info
            try: 
                item_code, name, description, tags, weight, defend, multiplier, strr, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, evo, aura, illulink, price = await self.quefe(f"""SELECT item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, evo, aura, illulink, price FROM pi_inventory WHERE existence='GOOD' AND item_id='{raw[0]}';""")
                if evo != 0: evo_plus = f"+{evo}"
                else: evo_plus = ''

                # Pointer
                if 'magic' in tags: pointer = ':crystal_ball:'
                else: pointer = '<:gun_pistol:508213644375621632>'
                # Aura icon
                aui = {'FLAME': 'https://imgur.com/3UnIPir.png', 'ICE': 'https://imgur.com/7HsDWfj.png', 'HOLY': 'https://imgur.com/lA1qfnf.png', 'DARK': 'https://imgur.com/yEksklA.png'}

                line = f""":scroll: **`『Weight』` ·** {weight} ⠀ ⠀:scroll: **`『Price』` ·** {price}\n```"{description}"```\n"""
                
                reembed = discord.Embed(title=f"`{item_code}`|**{' '.join([x for x in name.upper()])}** {evo_plus}", colour = discord.Colour(0x011C3A), description=line)
                reembed.add_field(name=":scroll: Basic Status <:broadsword:508214667416698882>", value=f"**`『STR』` ·** {strr}\n**`『INT』` ·** {intt}\n**`『STA』` ·** {sta}\n**`『MULTIPLIER』` ·** {multiplier}\n**`『DEFEND』` ·** {defend}\n**`『SPEED』` ·** {speed}", inline=True)

                try: acc_per = 10//accuracy_randomness
                except ZeroDivisionError: acc_per = 0
                reembed.add_field(name=f":scroll: Projector Status {pointer}", value=f"**`『RANGE』` ·** {range_min} - {range_max}m\n**`『STEALTH』` ·** {stealth}\n**`『FIRING-RATE』` ·** {firing_rate}\n**`『ACCURACY』` ·** {acc_per}%/{accuracy_range}m\n**-------------------**\n**`『ROUND』` ·** {round} \n**`『DMG』` ·** {dmg}", inline=True)

                reembed.set_thumbnail(url=aui[aura])
                if illulink != 'n/a': reembed.set_image(url=illulink)

                await ctx.send(embed=reembed, delete_after=30); return
            # Tags given, instead of item_id
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
            items = await self.quefe(f"""SELECT item_id, item_code, name, description, tags, weight, quantity, price, aura FROM pi_inventory WHERE existence='GOOD' AND user_id='{str(ctx.message.author.id)}' {lk_query};""", type='all')

            if not items: await ctx.send(f":x: No result..."); return

            def makeembed(top, least, pages, currentpage):
                line = f"**╔═══════╡**`Total: {len(items)}`**╞═══════**\n" 

                for item in items[top:least]:
                    if 'melee' in item[4]:
                        icon = '<:broadsword:508214667416698882>'
                        #line = line + f""" `{item_code}` <:broadsword:508214667416698882> **{items[item_code]['obj'].name}** | *"{items[item_code]['obj'].description}"* \n| **`Required`** STR-{items[item_code]['obj'].str}\n| **`Price`** <:36pxGold:548661444133126185>{items[item_code]['obj'].price}\n++ `{'` `'.join(items[item_code]['obj'].tags)}`\n\n"""
                    elif 'range_weapon' in item[4]:
                        icon = '<:gun_pistol:508213644375621632>'
                        #line = line + f""" `{item_code}` <:gun_pistol:508213644375621632> **{items[item_code]['obj'].name}** | *"{items[item_code]['obj'].description}"*\n| **`Required`** **STR**-{items[item_code]['obj'].str}/shot · **STA**-{items[item_code]['obj'].sta}\n| **`Price`**<:36pxGold:548661444133126185>{items[item_code]['obj'].price}\n++ `{'` `'.join(items[item_code]['obj'].tags)}` \n\n"""
                    elif 'ammunition' in item[4]:
                        icon = '<:shotgun_slug:508217929532440586>'
                        #line = line + f""" `{item_code}` <:shotgun_slug:508217929532440586> **{self.data['item'][item_code].name}** | *"{self.data['item'][item_code].description}"* \n| **`Price`** <:36pxGold:548661444133126185>{self.data['item'][item_code].price}\n| **`Quantity`** {items[item_code]}\n++ `{'` `'.join(self.data['item'][item_code].tags)}`\n\n"""                        
                    elif 'supply' in item[4]:
                        icon = ':small_orange_diamond:'
                        #line = line + f""" `{item_code}` :small_orange_diamond: **{self.data['item'][item_code].name}** \n| *"{self.data['item'][item_code].description}"*\n| **`Price`** <:36pxGold:548661444133126185>{self.data['item'][item_code].price}\n| **`Quantity`** {items[item_code]}\n++ `{'` `'.join(self.data['item'][item_code].tags)}`\n\n"""
                    elif 'ingredient' in item[4]:
                        icon = '<:green_ruby:520092621381697540>'
                        #line = line + f""" `{item_code}` <:green_ruby:520092621381697540> **{self.data['ingredient'][item_code].name}**\n| *"{self.data['ingredient'][item_code].description}"*\n| **`Price`** <:36pxGold:548661444133126185>{self.data['ingredient'][item_code].price}\n| **`Quantity`** {items[item_code]}\n++ `{'` `'.join(self.data['ingredient'][item_code].tags)}`\n\n"""                            
                    else: icon = ':tools:'
                    line = line + f""" `{item[0]}` {icon} `{item[1]}`| **{item[2]}** [{item[6]}]\n╟ *"{item[3]}"*\n**╟ `『Weight』{item[5]}`** · **`『Price』`<:36pxGold:548661444133126185>`{item[7]}`**\n**╟╼**`{item[4].replace(' - ', '`·`')}`\n\n"""
                            
                line = line + f"**╚═════════╡**`{currentpage}/{pages}`**╞══════════**" 

                reembed = discord.Embed(title = f"░░░░░<:mili_bag:507144828874915860> **I N V E N T O R Y** <:mili_bag:507144828874915860>░░░░░", colour = discord.Colour(0x011C3A), description=line)
                return reembed
                #else:
                #    await ctx.send("*Nothing but dust here...*")
            
            async def attachreaction(msg):
                await msg.add_reaction("\U000023ee")    #Top-left
                await msg.add_reaction("\U00002b05")    #Left
                await msg.add_reaction("\U000027a1")    #Right
                await msg.add_reaction("\U000023ed")    #Top-right

            pages = int(len(items)/5)
            if len(items)%5 != 0: pages += 1
            currentpage = 1
            cursor = 0

            emli = []
            for curp in range(pages):
                myembed = makeembed(currentpage*5-5, currentpage*5, pages, currentpage)
                emli.append(myembed)
                currentpage += 1

            if pages > 1:
                msg = await ctx.send(embed=emli[cursor])
                await attachreaction(msg)
            else: 
                msg = await ctx.send(embed=emli[cursor], delete_after=15)
                return

            def UM_check(reaction, user):
                return user.id == ctx.author.id and reaction.message.id == msg.id

            while True:
                try:
                    reaction, user = await self.client.wait_for('reaction_add', timeout=15, check=UM_check)
                    if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                        cursor += 1
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                    elif reaction.emoji == "\U00002b05" and cursor > 0:
                        cursor -= 1
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                    elif reaction.emoji == "\U000023ee" and cursor != 0:
                        cursor = 0
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                    elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                        cursor = pages - 1
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                except asyncio.TimeoutError:
                    await msg.delete(); return

        await browse()

    @commands.command(aliases=['u'])
    @commands.cooldown(1, 2, type=BucketType.user)
    async def use(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        raw = list(args)
        slots = {"a": 'right_hand', "b": "left_hand"}

        try:
            # Filter
            int(raw[0])

            # INCONSUMABLE
            try:
                ##Get weapon info
                try: w_name, w_tags, w_eq, w_weight, w_code = await self.quefe(f"SELECT name, tags, effect_query, weight, item_code FROM pi_inventory WHERE existence='GOOD' AND user_id='{ctx.author.id}' AND item_id='{raw[0]}';")
                except TypeError: await ctx.send(f"<:osit:544356212846886924> You don't own this item! (id.`{raw[0]}`)"); return

                if 'supply' in w_tags or 'ingredient' in w_tags: raise ZeroDivisionError

                ##Get slot_name
                try: slot_name = slots[raw[1]]
                except IndexError: slot_name = slots['a']
                except KeyError: await ctx.send(f"<:osit:544356212846886924> Slots not found, **{ctx.message.author.name}**!\n:grey_question: There are `2` weapon slots available: `0` Main Weapon | `1` Secondary Weapon"); return
                ##Get weapon
                weapon = await self.quefe(f"SELECT {slot_name} FROM personal_info WHERE id='{str(ctx.message.author.id)}';"); weapon = weapon[0]

                ##Equip
                if raw[0] != weapon:
                    await _cursor.execute(f"UPDATE personal_info SET {slot_name}='{raw[0]}' WHERE id='{str(ctx.message.author.id)}';")
                    # Inform, of course :)
                    await ctx.send(f":white_check_mark: Equipped item `{raw[0]}`|**{w_name}** to `{slot_name}` slot!"); return
                ###Already equip    -----> Unequip
                else:
                    await _cursor.execute(f"UPDATE personal_info SET {slot_name}='ar13' WHERE id='{str(ctx.message.author.id)}'")
                    await ctx.send(f":white_check_mark: Unequipped item `{raw[0]}`|**{w_name}** from *{slot_name}* slot!")
                    return
            # CONSUMABLE (Supply / Ingredient)
            except ZeroDivisionError:
                
                # Effect_query check
                if not w_eq: await ctx.send(":white_check_mark: Tried to use, but no effect received."); return

                ## Get quantity
                try:
                    target_id = str(ctx.message.author.id)
                    quantity = int(raw[1])
                    # SCAM :)
                    if quantity <= 0: await ctx.send("**Heyyyyyyyyy scammer-!**"); return
                    #if w_quantity <= quantity: 
                        #quantity = w_quantity
                        #quantity_query = f"UPDATE pi_inventory SET existence='BAD' WHERE item_id={raw[0]} AND user_id='{target_id}';"
                    #else:
                    #    quantity_query = f"UPDATE pi_inventory SET quantity=quantity-{quantity} WHERE item_id='{raw[0]}' AND user_id='{target_id}';"
                    quantity_query = f"SELECT func_i_delete('{target_id}', '{w_code}', {quantity});"

                ## E: No quantity given
                except IndexError:
                    target_id = str(ctx.message.author.id)
                    quantity = 1
                    #if w_quantity <= quantity: 
                    #    quantity = w_quantity
                    #    quantity_query = f"UPDATE pi_inventory SET existence='BAD' WHERE item_id={raw[0]} AND user_id='{target_id}';"
                    #else:
                    #    quantity_query = f"UPDATE pi_inventory SET quantity=quantity-{quantity} WHERE item_id='{raw[0]}' AND user_id='{target_id}';"
                    quantity_query = f"SELECT func_i_delete('{target_id}', '{w_code}', {quantity});"

                ## E: Invalid type of quantity argument
                except TypeError:
                    ## Get target_id
                    try: target_id = str(ctx.message.mentions[0].id)
                    ## E: No mention
                    except IndexError: target_id = str(ctx.author.id)
                    quantity = 1
                    #if w_quantity <= quantity:
                    #    quantity = w_quantity
                    #    quantity_query = f"UPDATE pi_inventory SET existence='BAD' WHERE item_id={raw[0]} AND user_id='{target_id}';"
                    #else:
                    #    quantity_query = f"UPDATE pi_inventory SET quantity=quantity-{quantity} WHERE item_id='{raw[0]}' AND user_id='{target_id}';"
                    quantity_query = f"SELECT func_i_delete('{target_id}', '{w_code}', {quantity});"

                # Get target info
                try: t_name, t_STA, t_MAX_STA = await self.quefe(f"SELECT name, STA, MAX_STA FROM personal_info WHERE id='{target_id}';")
                except TypeError: await ctx.send("<:osit:544356212846886924> Target has not incarnated")
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
                    ex_query = f"UPDATE personal_info SET weight=weight+{random.choice([0, 0.1, 0.2, 0.5, 1, 1.2, 1.5, 2])*w_weight*quantity} WHERE id='{str(ctx.message.author.id)}';"

                ## Adjusting things with quantity
                await _cursor.execute(quantity_query + af_query + ex_query)
                await self.ava_scan(ctx.message, type='normalize', target_id=target_id)
                #print(quantity_query + af_query + ex_query)
                await ctx.send(f":white_check_mark: Used {quantity} `{raw[0]}`|**{w_name}** on **{t_name}**")                

        # E: Slot not given            
        except IndexError:
            # Switch
            mw, sw = await self.quefe(f"SELECT right_hand, {slots['b']} FROM personal_info WHERE id='{str(ctx.message.author.id)}';")
            await _cursor.execute(f"UPDATE personal_info SET right_hand='{sw}', {slots['b']}='{mw}' WHERE id='{str(ctx.message.author.id)}';")

            # Get line
            sw_name = await self.quefe(f"SELECT name FROM pi_inventory WHERE existence='GOOD' AND user_id='{str(ctx.message.author.id)}' AND item_id='{sw}';")
            if sw_name: line_1 = f"`{sw}`|**{sw_name}** ➠ **right_hand**"
            else: line_1 = '**right_hand** is left empty'
            mw_name = await self.quefe(f"SELECT name FROM pi_inventory WHERE existence='GOOD' AND user_id='{str(ctx.message.author.id)}' AND item_id='{mw}';")
            if mw_name: line_2 = f"`{mw}`|**{mw_name}** ➠ **{slots['b']}**'"
            else: line_2 = f"**{slots['b']}** is left empty"
            # Inform :)
            await ctx.send(f":twisted_rightwards_arrows: {line_1} **|** {line_2} "); return
    
        # E: <item_code> OR <slot> given, instead of <item_id>
        except ValueError:

            # SLOT SWITCHING
            try:
                # Switch
                mw, sw = await self.quefe(f"SELECT right_hand, {slots[raw[0]]} FROM personal_info WHERE id='{str(ctx.message.author.id)}';")
                await _cursor.execute(f"UPDATE personal_info SET right_hand='{sw}', {slots['b']}='{mw}' WHERE id='{str(ctx.message.author.id)}';")

                # Get line
                sw_name = await self.quefe(f"SELECT name FROM pi_inventory WHERE existence='GOOD' AND user_id='{str(ctx.message.author.id)}' AND item_id='{sw}';")
                if sw_name: line_1 = f"`{sw}`|**{sw_name}** ➠ **right_hand**"
                else: line_1 = '**right_hand** is left empty'
                mw_name = await self.quefe(f"SELECT name FROM pi_inventory WHERE existence='GOOD' AND user_id='{str(ctx.message.author.id)}' AND item_id='{mw}';")
                if mw_name: line_2 = f"`{mw}`|**{mw_name}** ➠ **{slots[raw[0]]}**'"
                else: line_2 = f"**{slots[raw[0]]}** is left empty"
                # Inform :)
                await ctx.send(f":twisted_rightwards_arrows: {line_1} **|** {line_2} "); return
            # E: Slot not found
            except KeyError: pass

    @commands.command()
    @commands.cooldown(2, 900, type=BucketType.user)
    async def trader(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        cmd_tag = 'trade'

        cur_PLACE, cur_X, cur_Y, money = await self.quefe(f"SELECT cur_PLACE, cur_X, cur_Y, money FROM personal_info WHERE id='{str(ctx.message.author.id)}';")

        if not await self.area_scan(ctx, cur_X, cur_Y): await ctx.send("<:osit:544356212846886924> Traders aren't availablie outside of **Peace Belt**!"); return
        raw = list(args); quantity = 1

        # COOLDOWN
        if not await self.__cd_check(ctx.message, cmd_tag, f"The storm is coming so they ran away."): return

        # Get cuisine
        try: cuisine, r_name = await self.quefe(f"SELECT cuisine, name FROM environ WHERE environ_code='{cur_PLACE}';")
        except TypeError:
            cuisine, r_name = await self.quefe(f"SELECT cuisine, name FROM pi_land WHERE land_code='{cur_PLACE}';")
            if not cuisine: await ctx.send("Traders are not through here, it seems..."); return

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
            line = line + f""" `{ig_code}` <:green_ruby:520092621381697540> **{items[ig_code][0]}**\n| *"{items[ig_code][1]}"*\n| **`Market price`** <:36pxGold:548661444133126185>{items[ig_code][2]}\n++ `{items[ig_code][3].replace(' - ', '` `')}`\n\n"""
            
        reembed = discord.Embed(title = f"------------- KINUKIZA's MARKET of `{cur_PLACE}`|**{r_name}** -----------", colour = discord.Colour(0x011C3A), description=line)
        temp1 = await ctx.send(embed=reembed)
        await ctx.send(':bell: Syntax: `!buy` `[item_code]` |  Time out: 60s')

        def UMCc_check(m):
            return m.channel == ctx.channel and m.content.startswith('!buy') and m.author == ctx.author

        # First buy
        try: 
            raw = await self.client.wait_for('message', check=UMCc_check, timeout=60)
            await temp1.delete()
        except asyncio.TimeoutError: 
            await ctx.send("<:osit:544356212846886924> Request timed out!")
            await temp1.delete(); return

        raw = raw.content.lower().split(' ')[1:]
        ig_code = raw[0]
        try: 
            quantity = int(raw[1])
            if quantity > 10: quantity = 10
            # SCAM :)
            if quantity <= 0: await ctx.send("Don't be dumb <:fufu:520602319323267082>"); return                
        # E: Quantity not given, or invalidly given
        except (IndexError, TypeError): pass

        # ig_code check    
        if ig_code not in menu: await ctx.send("<:osit:544356212846886924> The trader does not have this item at the moment. Sorry."); return

        # Reconfirm
        def UMCc_check2(m):
            return m.channel == ctx.channel and m.content == 'trade confirm' and m.author == ctx.author

        price = int(items[ig_code][2]*random.choice([0.1, 0.2, 0.5, 1, 2, 5, 10]))
        await ctx.send(f"{ctx.message.author.mention}, the dealer set the price of **<:36pxGold:548661444133126185>{price}** for __each__ item `{ig_code}`|**{items[ig_code][0]}**. \nThat would cost you **<:36pxGold:548661444133126185>{price*quantity}** in total.\n:bell: Proceed? (Key: `trade confirm` | Timeout=10s)")
        try: await self.client.wait_for('message', check=UMCc_check2, timeout=10)
        except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request declined!"); return
        
        try:
            # Money check
            if price*quantity <= money:
                # UN-SERIALIZABLE
                # Increase item_code's quantity
                await _cursor.execute(f"SELECT func_ig_reward('{ctx.author.id}', '{ig_code}', {quantity});")
                #if await _cursor.execute(f"UPDATE pi_inventory SET quantity=quantity+{quantity} WHERE user_id='{str(ctx.message.author.id)}' AND item_code='{ig_code}';") == 0:
                    # E: item_code did not exist. Create one, with given quantity
                #    await _cursor.execute(f"INSERT INTO pi_inventory SELECT 0, {str(ctx.message.author.id)}, ingredient_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, infuse_query, order_query, passive_query, ultima_query, {quantity}, price, dmg, stealth, evo, aura, craft_value, illulink FROM model_ingredient WHERE ingredient_code='{ig_code}';")

                # Deduct money
                await _cursor.execute(f"UPDATE personal_info SET money=money-{price*quantity} WHERE id='{str(ctx.message.author.id)}';")

            else: await ctx.send("<:osit:544356212846886924> Insufficience balance!"); return
        # E: Item_code not found
        except KeyError: await ctx.send("<:osit:544356212846886924> Item's code not found!"); return


        # Greeting, of course :)
        await self.client.loop.run_in_executor(None, partial(redio.set, f'{cmd_tag}{ctx.author.id}', 'trading', ex=2700, nx=True))
        await ctx.send(f":white_check_mark: Received **{quantity}** item `{ig_code}`|**{items[ig_code][0]}**. Nice trade!")

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def sell(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        raw = list(args)

        # PLAYER SELL ===============================
        try: item_id = int(raw[0])
        except IndexError: await ctx.send("<:osit:544356212846886924> Missing item's id!"); return
        except ValueError: await ctx.send("<:osit:544356212846886924> Invalid item's id!"); return

        try:
            if len(raw) >= 4:
                receiver = await commands.MemberConverter().convert(ctx, raw[3])
                try: quantity = int(raw[1])
                except ValueError: await ctx.send("<:osit:544356212846886924> Invalid quantity"); return
                try: price = int(raw[2])
                except ValueError: await ctx.send("<:osit:544356212846886924> Invalid price"); return
            elif len(raw) == 3:
                receiver = await commands.MemberConverter().convert(ctx, raw[2])
                quantity = 1
                try: price = int(raw[1])
                except ValueError: await ctx.send("<:osit:544356212846886924> Invalid price"); return
            elif len(raw) == 2:
                receiver = await commands.MemberConverter().convert(ctx, raw[1])
                quantity = 1; price = 1
            else: raise commands.CommandError

            try:
                t_cur_X, t_cur_Y, t_cur_PLACE, t_money = await self.quefe(f"SELECT cur_X, cur_Y, cur_PLACE, money FROM personal_info WHERE id='{receiver.id}';")
                cur_X, cur_Y, cur_PLACE = await self.quefe(f"SELECT cur_X, cur_Y, cur_PLACE FROM personal_info WHERE id='{ctx.author.id}';")
            # E: Id not found
            except TypeError: await ctx.send("<:osit:544356212846886924> User don't have an ava!"); return

            # Get item's info
            try: w_tags, w_name, w_quantity, w_code = await self.quefe(f"SELECT tags, name, quantity, item_code FROM pi_inventory WHERE existence='GOOD' AND user_id='{ctx.author.id}' AND item_id='{item_id}';")
            except TypeError: await ctx.send("<:osit:544356212846886924> You don't own this item!"); return

            # Tradable check
            if 'untradable' in w_tags: await ctx.send(f"<:osit:544356212846886924> You cannot trade this item, **{ctx.message.author.name}**. It's *untradable*, look at its tags."); return

            msg = await ctx.send(f"**{ctx.author.name}** wants to sell you **{quantity}** `{w_code}`|**{w_name}**. Accept, {receiver.mention}?")
            await msg.add_reaction('\U0001f6d2')

            def RUM_check(reaction, user):
                return user == receiver and reaction.message.id == msg.id and str(reaction.emoji) == '\U0001f6d2' 

            try: await self.client.wait_for('reaction_add', check=RUM_check, timeout=20)
            except asyncio.TimeoutError: await ctx.send(":x: Deal cancelled"); return

            # Money check
            if price > t_money: await ctx.send("<:osit:544356212846886924> Insufficient ballance!"); return

            # Distance check
            if cur_PLACE != t_cur_PLACE:
                await ctx.send(f"<:osit:544356212846886924> You need to be in the same region with the receiver, **{ctx.author.name}**!"); return
            if await self.distance_tools(cur_X, cur_Y, t_cur_X, t_cur_Y) > 50:
                await ctx.send(f"<:osit:544356212846886924> You need to be within **50 m** range of the receiver, **{ctx.author.name}**!"); return

            # INCONSUMABLE
            if 'inconsumable' in w_tags:
                await _cursor.execute(f"UPDATE pi_inventory SET user_id='{receiver.id}' WHERE item_id='{item_id}';")
            
            # CONSUMABLE
            else:
                # Quantity given
                try:
                    # Quantity check
                    if int(raw[1]) >= w_quantity:
                        quantity = w_quantity
                        # Check if receiver has already had the item
                        await _cursor.execute(f"SELECT func_ig_reward('{receiver.id}', '{w_code}', {quantity}); UPDATE pi_inventory SET existence='BAD' WHERE user_id='{ctx.author.id}' AND item_code='{w_code}';")

                    else:
                        quantity = int(raw[1])
                        # SCAM :)
                        if quantity <= 0: await ctx.send("**Heyyyyyyyyy scammer-!**"); return
                        # Check if receiver has already had the item
                        await _cursor.execute(f"SELECT func_ig_reward('{receiver.id}', '{w_code}', {quantity}); UPDATE pi_inventory SET quantity=quantity-{quantity} WHERE user_id='{ctx.author.id}' AND item_code='{w_code}';")
                # Quantity NOT given
                except (ValueError, IndexError): 
                    quantity = 1
                    # Check if receiver has already had the item
                    await _cursor.execute(f"SELECT func_ig_reward('{receiver.id}', '{w_code}', {quantity}); UPDATE pi_inventory SET quantity=quantity-{quantity} WHERE user_id='{ctx.author.id}' AND item_code='{w_code}';")

            # Inform, of course :>
            await ctx.send(f":white_check_mark: You've been given `{quantity}` `{w_code}`|**{w_name}**, {ctx.message.author.mention}!"); return

        except commands.CommandError:
            try: quantity = int(raw[1])
            except (IndexError, ValueError): quantity = 1

        # BOT SELL ==================================
        try: right_hand, left_hand = await self.quefe(f"SELECT right_hand, left_hand FROM personal_info WHERE id='{ctx.author.id}' AND cur_X<1 AND cur_Y<1;")
        # E: Out of PB
        except TypeError: await ctx.send("<:osit:544356212846886924> You think you can find customers outside of **Peace Belt**??"); return

        quantity = 1
        try: quantity = int(raw[1])
        except (IndexError, ValueError): pass

        # SCAM :)
        if quantity <= 0: await ctx.send("**Heyyyyyyyyy scammer-!**"); return  

        try: w_name, w_price, w_quantity, w_tags = await self.quefe(f"SELECT name, price, quantity, tags FROM pi_inventory WHERE existence='GOOD' AND user_id='{ctx.author.id}' AND item_id='{item_id}';")
        # E: Item_id not found
        except TypeError: await ctx.send("<:osit:544356212846886924> You don't own this weapon!"); return      
        # E: Item_id not given
        except IndexError: await ctx.send("<:osit:544356212846886924> Missing argument"); return

        if 'untradable' in w_tags: await ctx.send(f"<:osit:544356212846886924> You cannot sell this item, **{ctx.author.name}**."); return

        try:
            # Selling
            # CONSUMABLE
            if not 'inconsumable' in w_tags:
                # Quantity check
                if quantity >= w_quantity:
                    quantity = w_quantity
                    quantity_query = f"UPDATE pi_inventory SET existence='BAD' WHERE item_id={raw[0]} AND user_id='{ctx.author.id}';"
                else: quantity_query = f"UPDATE pi_inventory SET quantity=quantity-{quantity} WHERE item_id={raw[0]} AND user_id='{ctx.author.id}';"

                receive = int(w_price*random.choice([0.1, 0.2, 0.5, 0.6, 1, 1.5, 4])*quantity)
                receive_query = f"UPDATE personal_info SET money=money+{receive} WHERE id='{ctx.author.id}';"
             
            # INCONSUMABLE
            else:
                # Equipped weapon check
                if raw[0] in [right_hand, left_hand]: await ctx.send("<:osit:544356212846886924> You cannot sell an item that being equipped!"); return

                quantity_query = f"UPDATE pi_inventory SET existence='BAD' WHERE item_id={raw[0]} AND user_id='{ctx.author.id}';"

                receive = int(w_price*random.choice([0.1, 0.25, 0.2, 0.4, 0.5, 0.6, 0.75, 1, 4])*quantity)
                receive_query = f"UPDATE personal_info SET money=money+{receive} WHERE id='{str(ctx.message.author.id)}';"

        # E: Item_id not found
        except KeyError: await ctx.send("<:osit:544356212846886924> You don't own this weapon!"); return

        # Receiving money/Removing item
        await _cursor.execute(receive_query + quantity_query)

        await ctx.send(f":white_check_mark: You received **<:36pxGold:548661444133126185>{receive}** from selling {quantity} `{item_id}`|**{w_name}**, **{ctx.message.author.name}**!")

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def give(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        raw = list(args)

        # Receiver check
        try:
            receiver = await commands.UserConverter().convert(ctx, raw[1])
            try:
                t_cur_X, t_cur_Y, t_cur_PLACE, t_partner = await self.quefe(f"SELECT cur_X, cur_Y, cur_PLACE, partner FROM personal_info WHERE id='{receiver.id}';")
                cur_X, cur_Y, cur_PLACE, money, partner = await self.quefe(f"SELECT cur_X, cur_Y, cur_PLACE, money, partner FROM personal_info WHERE id='{ctx.author.id}';")
            # E: Id not found
            except TypeError: await ctx.send("<:osit:544356212846886924> User don't have an ava!"); return
        except (commands.CommandError, IndexError): await ctx.send(f"<:osit:544356212846886924> Please provide a receiver, **{ctx.author.name}**!"); return

        try: package = int(raw[0])
        except (IndexError, ValueError): await ctx.send(f"<:osit:544356212846886924> Please provide an amount of money you want to give"); return

        # Distance check
        if cur_PLACE != t_cur_PLACE:
            if not (partner == str(receiver.id) and t_partner == str(ctx.author.id)):
                await ctx.send(f"<:osit:544356212846886924> You need to be in the same region with the receiver, **{ctx.author.name}**!"); return
        if await self.distance_tools(cur_X, cur_Y, t_cur_X, t_cur_Y) > 50:
            if not (partner == str(receiver.id) and t_partner == str(ctx.author.id)):
                await ctx.send(f"<:osit:544356212846886924> You need to be within **50 m** range of the receiver, **{ctx.author.name}**!"); return

        # Money check
        try:
            if package > money: await ctx.send("<:osit:544356212846886924> Insufficient balance!"); return
            # SCAM :)
            if package <= 0: await ctx.send("**Heyyyyyyyyy scammer-!**"); return
        except ValueError: await ctx.send("<:osit:544356212846886924> Invalid syntax!"); return
            
        # Transfer
        await _cursor.execute(f"UPDATE personal_info SET money=money+IF(id='{ctx.author.id}', -{package}, {package}) WHERE id IN ('{ctx.author.id}', '{receiver.id}');")
        await ctx.send(f":white_check_mark: You've been given **<:36pxGold:548661444133126185>{raw[0]}**, {receiver.mention}!")

    @commands.cooldown(1, 10, type=BucketType.user)
    async def trade(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        raw = list(args)

        # Receiver check
        try: 
            receiver = ctx.message.mentions[0]
            try: 
                t_cur_X, t_cur_Y, t_cur_PLACE, t_money = await _cursor.execute(f"SELECT cur_X, cur_Y, cur_PLACE, money FROM personal_info WHERE id='{receiver.id}';")
                cur_X, cur_Y, cur_PLACE = await _cursor.execute(f"SELECT cur_X, cur_Y, cur_PLACE FROM personal_info WHERE id='{str(ctx.message.author.id)}';")
            # E: Id not found
            except TypeError: await ctx.send("<:osit:544356212846886924> User don't have an ava!"); return
        except IndexError: await ctx.send(f"<:osit:544356212846886924> Please provide a receiver, **{ctx.message.author.name}**!"); return

        # Distance check
        if cur_PLACE != t_cur_PLACE:
            await ctx.send(f"<:osit:544356212846886924> You need to be in the same region with the receiver, **{ctx.message.author.name}**!"); return
        if await self.distance_tools(cur_X, cur_Y, t_cur_X, t_cur_Y, int(args[0])/1000, int(args[1])/1000) > 50:
            await ctx.send(f"<:osit:544356212846886924> You need to be within **50 m** range of the receiver, **{ctx.message.author.name}**!"); return

        # Get item's info
        try: w_tags, w_name, w_quantity, w_code = await self.quefe(f"SELECT tags, name, quantity, item_code FROM pi_inventory WHERE existence='GOOD' AND user_id='{str(ctx.message.author.id)}' AND item_id='{raw[0]}';")
        except TypeError: await ctx.send("<:osit:544356212846886924> You don't own this item!"); return

        if 'untradable' in w_tags: await ctx.send(f"<:osit:544356212846886924> You cannot trade this item, **{ctx.message.author.name}**. It's *untradable*, look at its tags."); return

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
                    if quantity <= 0: await ctx.send("**Heyyyyyyyyy scammer-!**"); return
                    # Check if receiver has already had the item
                    if await _cursor.execute(f"UPDATE pi_inventory SET quantity=quantity+{quantity} WHERE user_id='{receiver.id}' AND item_code='{w_code}';") == 0:
                        await _cursor.execute(f"INSERT INTO pi_inventory SELECT 0, '{receiver.id}', item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, order_query, passive_query, ultima_query, {quantity}, price, dmg, stealth, aura, craft_value, illulink FROM pi_inventory WHERE existence='GOOD' AND item_id='{w_code}' AND user_id='{str(ctx.message.author.id)}';")
            # Quantit NOT given
            except (ValueError, IndexError): 
                quantity = 1
                # Check if receiver has already had the item
                if await _cursor.execute(f"UPDATE pi_inventory SET quantity=quantity+{quantity} WHERE user_id='{receiver.id}' AND item_code='{w_code}';") == 0:
                    await _cursor.execute(f"INSERT INTO pi_inventory SELECT 0, '{receiver.id}', item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, order_query, passive_query, ultima_query, {quantity}, price, dmg, stealth, aura, craft_value, illulink FROM pi_inventory WHERE existence='GOOD' AND item_id='{w_code}' AND user_id='{str(ctx.message.author.id)}';")

        # Inform, of course :>
        await ctx.send(f":white_check_mark: You've been given `{quantity}` `{w_code}`|**{w_name}**, {ctx.message.author.mention}!")

    @commands.command(aliases=['b'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def bank(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        # Status check
        try: money, cur_X, cur_Y, age, stats = await self.quefe(f"SELECT money, cur_X, cur_Y, age, stats FROM personal_info WHERE id='{str(ctx.message.author.id)}' AND stats NOT IN ('ORANGE', 'RED');")
        except TypeError: await ctx.send(f"<:osit:544356212846886924> You need a **GREEN** or **YELLOW** status to perform this command, **{ctx.message.author.name}**."); return

        # Coord check
        if not await self.area_scan(ctx, cur_X, cur_Y): await ctx.send("<:osit:544356212846886924> Banks are only available within **Peace Belt**!"); return

        # Account getting
        try: invs, invs_interst, invest_age, tier = await self.quefe(f"SELECT investment, interest, invest_age, tier FROM pi_bank WHERE user_id='{str(ctx.message.author.id)}';")
        # E: User does not have account
        except TypeError:
            # Get confirmation
            def UMCc_check(m):
                return m.channel == ctx.channel and m.content == 'account confirm' and m.author == ctx.author

            await ctx.send(f":bank: Greeting, {ctx.message.author.mention}. It seems that there's no account has your id on it. Perhaps, would you like to open one?\n:bell: *Proceed?* (Key: `account confirm` | Timeout=10s)")
            try: await self.client.wait_for('message', timeout=10, check=UMCc_check)
            except asyncio.TimeoutError: await ctx.send(f":bank: Indeed. Why would mongrels need a bank account..."); return
            
            # Create account
            await _cursor.execute(f"INSERT INTO pi_bank VALUES ('{str(ctx.message.author.id)}', 0, 0, 0.01, '1');")
            await ctx.send(f":white_check_mark: Your account has been successfully created!"); return

        raw = list(args)

        try:
            # INVEST
            if raw[0] == 'invest':
                try:
                    quantity = int(raw[1])
                    if quantity >= money: quantity = money
                    elif quantity < 0: await ctx.send("Don't be stupid <:fufu:520602319323267082>"); return

                    # Update prev investment, then the investment, then the invest_age
                    await _cursor.execute(f"UPDATE pi_bank SET investment=(investment+investment*{invs_interst}*{age - invest_age})+{quantity}, invest_age={age} WHERE user_id='{str(ctx.message.author.id)}';")
                    await _cursor.execute(f"UPDATE personal_info SET money=money-{quantity}, stats=IF(money>=0, 'GREEN', 'YELLOW') WHERE id='{str(ctx.message.author.id)}';")

                    await ctx.send(f":white_check_mark: Added **<:36pxGold:548661444133126185>{quantity}** to your account!"); return

                # E: Quantity not given
                except (IndexError, ValueError): await ctx.send("<:osit:544356212846886924> Please provide the amount you want to invest."); return

            # WITHDRAW
            elif raw[0] == 'withdraw':
                try:
                    if stats == 'YELLOW': await ctx.send("<:osit:544356212846886924> You need a **GREEN** status to withdraw money."); return

                    quantity = int(raw[1])
                    if quantity >= invs: quantity = invs
                    elif quantity < 0: await ctx.send("Don't be stupid <:fufu:520602319323267082>"); return

                    # Update prev investment, then the investment, then the invest_age
                    await _cursor.execute(f"UPDATE pi_bank SET investment=(investment+investment*{invs_interst}*{age - invest_age})-{quantity}, invest_age={age} WHERE user_id='{str(ctx.message.author.id)}';")
                    await _cursor.execute(f"UPDATE personal_info SET money=money+{quantity} WHERE id='{str(ctx.message.author.id)}';")

                    await ctx.send(f":white_check_mark: **<:36pxGold:548661444133126185>{quantity}** has just been withdrawn from your account!"); return
                # E: Quantity not given
                except (IndexError, ValueError): await ctx.send("<:osit:544356212846886924> Please provide the amount you want to withdraw."); return
            
            # TRANSFER
            elif raw[0] == 'transfer':
                try:
                    if stats == 'YELLOW': await ctx.send("<:osit:544356212846886924> You need a **GREEN** status to transfer money."); return
                    
                    # Get quantity
                    for i in raw[1:]:
                        try: quantity = int(i)
                        except ValueError: continue
                        if quantity >= invs: quantity = invs
                        elif quantity < 0: await ctx.send("Don't be stupid <:fufu:520602319323267082>"); return

                    # Get target
                    target = ctx.message.mentions[0]
                    if not target: await ctx.send("<:osit:544356212846886924> Please provide a receiver"); return

                    # Tax and shiet
                    tax = 40 - int(tier)*5
                    try: q_atx = int(quantity/100*(100-tax))
                    except NameError: await ctx.send("<:osit:544356212846886924> Please provide the amount of money"); return

                    line = f"""```clean
        BEFORE Tax:⠀⠀⠀⠀⠀⠀⠀$ {quantity}
        TAX:⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀x⠀  {tax} %
        -----------------------------
        AFTER Tax:⠀⠀⠀⠀⠀⠀⠀⠀$ {q_atx}```"""

                    def UMCc_check2(m):
                        return m.channel == ctx.channel and m.content == 'transfer confirm' and m.author == ctx.author

                    await ctx.send(f":credit_card: | **{ctx.message.author.name}**⠀⠀>>>⠀⠀**{target.name}**\n{line}:bell: Proceed? (Key: `transfer confirm` | Timeout=15s)")
                    try: await self.client.wait_for('message', timeout=15, chec=UMCc_check2)
                    except asyncio.TimeoutError: await ctx.send(f":credit_card: Aborted!"); return

                    # Transfer
                    if await _cursor.execute(f"UPDATE pi_bank SET investment=investment+{q_atx} WHERE id='{target.id}';") == 0:
                        await ctx.send(f"<:osit:544356212846886924> User does not have a bank account!"); return
                    # Update prev investment, then the investment, then the invest_age
                    await _cursor.execute(f"UPDATE pi_bank SET investment=(investment+investment*{invs_interst}*{age - invest_age})-{quantity}, invest_age={age} WHERE user_id='{str(ctx.message.author.id)}';")

                    await ctx.send(f":credit_card: **<:36pxGold:548661444133126185>{q_atx}** has been successfully added to **{target.name}**'s bank account."); return

                # E: Quantity not given
                except (IndexError, ValueError): await ctx.send("<:osit:544356212846886924> Please provide the amount you want to withdraw."); return

            # LOAN
            elif raw[0] == 'loan':
                try:
                    if stats == 'YELLOW': await ctx.send("<:osit:544356212846886924> You need a **GREEN** status to request a loan."); return
                    stata = 'GREEN'

                    quantity = int(raw[1])
                    if quantity >= invs: 
                        # Check if the loan is off-limit
                        if quantity > invs*3: await ctx.send(f"<:osit:544356212846886924> You cannot loan 3 times your current balance"); return
                        stata = 'YELLOW'
                    elif quantity < 0: await ctx.send("Don't be stupid <:fufu:520602319323267082>"); return

                    # Update prev investment, then the investment, then the invest_age
                    await _cursor.execute(f"UPDATE pi_bank SET investment=(investment+investment*{invs_interst}*{age - invest_age})-{quantity}, invest_age={age} WHERE user_id='{str(ctx.message.author.id)}';")
                    await _cursor.execute(f"UPDATE personal_info SET money=money+{quantity}, stats='{stata}' WHERE id='{str(ctx.message.author.id)}';")

                    await ctx.send(f":white_check_mark: **<:36pxGold:548661444133126185>{quantity}** has just been withdrawn from your account!"); return
                # E: Quantity not given
                except (IndexError, ValueError): await ctx.send("<:osit:544356212846886924> Please provide the amount you want to withdraw."); return                         

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
                    if await _cursor.execute(f"UPDATE pi_bank SET tier='{next_tier}', interest={tier_dict[next_tier][1]} WHERE user_id='{str(ctx.message.author.id)}' AND EXISTS (SELECT * FROM pi_degrees WHERE user_id='{str(ctx.message.author.id)}' AND degree='{tier_dict[next_tier][0][0]}' AND major='{tier_dict[next_tier][0][1]}');") == 0:
                        await ctx.send(f":bank: Sorry. Your request to upgrade to tier `{next_tier}` does not meet the criteria."); return
                except KeyError: await ctx.send(f":bank: Your current tier is `{tier}`, which is the highest."); return

                await ctx.send(f":white_check_mark: Upgraded to tier `{next_tier}`!"); return

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
                    await _cursor.execute(f"UPDATE pi_bank SET tier='{next_tier}', interest={tier_dict[next_tier][1]} WHERE user_id='{str(ctx.message.author.id)}';")
                except KeyError: await ctx.send(f":bank: Your current tier is `{tier}`, which is the lowest to be able to downgrade."); return

                await ctx.send(f":white_check_mark: Downgraded to tier `{next_tier}`!"); return

        # E: args not given
        except IndexError:

            line = f""":bank: `『TIER』` **· `{tier}`** ⠀⠀ ⠀:bank: `『INTEREST』` **· `{invs_interst}`** \n```$ {invs}```"""

            reembed = discord.Embed(title = f"{ctx.message.author.name.upper()}", colour = discord.Colour(0x011C3A), description=line)
            reembed.set_thumbnail(url=ctx.message.author.avatar_url)

            await ctx.send(embed=reembed)




# ================ LIFE ===================
        
    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def guild(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        await self.ava_scan(ctx.message)
        raw = list(args)

        name, rank, total_quests = await self.quefe(f"SELECT name, rank, total_quests FROM pi_guild WHERE user_id='{ctx.author.id}';")

        try:
            if name == 'n/a' and raw[0] != 'join':
                await ctx.send("<:osit:544356212846886924> You haven't joined any guilds yet!"); return
        except IndexError: await ctx.send("<:osit:544356212846886924> You haven't joined any guilds yet!"); return

        current_place, money = await self.quefe(f"SELECT cur_PLACE, money FROM personal_info WHERE id='{ctx.author.id}'")

        try:
            if raw[0] == 'join':
                # Check if user's in the same guild
                if name == current_place:
                    await ctx.send(f"<:osit:544356212846886924> You've already been in that guild, **{ctx.message.author.name}**!"); return
                # ... or in other guilds
                elif name != 'n/a':
                    cost = abs(2000* (int(name.split('.')[1]) - int(current_place.split('.')[1])))
                # ... jor just want to join
                else: cost = 0

                def UMCc_check(m):
                    return m.channel == ctx.channel and m.content == 'joining confirm' and m.author == ctx.author

                await ctx.send(f":scales: **G.U.I.L.D** of `{current_place} | {self.environ[current_place]['name']}` :scales:\n------------------------------------------------\nJoining will require **<:36pxGold:548661444133126185>{cost}** as a deposit which will be returned when you leave guild if: \n· You don't have any bad records.\n· You're alive.\n· You leave the guild before joining others\n------------------------------------------------\n:bell: **Do you wish to proceed?** (key: `joining confirm` | timeout=20s)")
                try: await self.client.wait_for('message', timeout=20, check=UMCc_check)           
                except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request timed out!"); return

                # Money check
                if money < cost: await ctx.send("<:osit:544356212846886924> Insufficient balance!"); return

                await _cursor.execute(f"UPDATE personal_info SET money={money - cost} WHERE id='{str(ctx.message.author.id)}';")
                await _cursor.execute(f"UPDATE pi_guild SET name='{current_place}', deposit=deposit+{cost} WHERE user_id='{str(ctx.message.author.id)}';")
                await ctx.send(f":european_castle: Welcome, {ctx.message.author.mention}, to our big family all over Pralayr :european_castle:\nYou are no longer a lonely, nameless adventurer, but a member of `{current_place} | {self.environ[current_place]['name']}` guild, a part of **G.U.I.L.D**'s league. Please, newcomer, make yourself at home <3"); return

            elif raw[0] == 'leave':
                name, deposit = await self.quefe(f"SELECT name, deposit FROM pi_guild WHERE user_id='{str(ctx.message.author.id)}'")

                def UMCc_check(m):
                    return m.channel == ctx.channel and m.content == 'leaving confirm' and m.author == ctx.author

                await ctx.send(f":bell: {ctx.message.author.mention}, leaving `{current_place}|{self.environ[current_place]['name']}` guild? (key: `leaving confirm` | timeout=5s)")
                try: await self.client.wait_for('message', timeout=5, check=UMCc_check)
                except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request timed out!"); return

                await _cursor.execute(f"UPDATE personal_info SET money=money+{deposit} WHERE id='{str(ctx.message.author.id)}';")
                await _cursor.execute(f"UPDATE pi_guild SET name='n/a', deposit=0 WHERE user_id='{str(ctx.message.author.id)}';")
                await ctx.send(f":white_check_mark: Left guild. Deposit of **<:36pxGold:548661444133126185>{deposit}** has been returned"); return

            elif raw[0] == 'quest':
                try:
                    if raw[1] == 'take':
                        # If quest's id given, accept the quest
                        try:
                            sample = {'iron': 3, 'bronze': 4, 'silver': 5, 'gold': 6, 'adamantite': 8, 'mithryl': 10}
                            if await _cursor.execute(f"SELECT * FROM pi_quests WHERE user_id='{ctx.author.id}' AND quest_code='{raw[2]}';") >= 1: await ctx.send("<:osit:544356212846886924> Quest has already been taken or done"); return
                            if await _cursor.execute(f"SELECT COUNT(user_id) FROM pi_quests WHERE user_id='{ctx.author.id}' AND stats='ONGOING'") >= sample[rank]: await ctx.send(f"<:osit:544356212846886924> You cannot handle more than **{sample[rank]}** quests at a time")

                            region, quest_code, quest_line, quest_name, snap_query, quest_sample, eval_meth, effect_query, reward_query = await self.quefe(f"SELECT region, quest_code, quest_line, name, snap_query, sample, eval_meth, effect_query, reward_query FROM model_quest WHERE quest_code='{raw[2]}';")
                            snap_query = snap_query.replace('user_id_here', f'{ctx.author.id}')
                            # Region check
                            if region != current_place and quest_line != 'DAILY': await self.client(f":european_castle: Quest `{raw[2]}` is only available in `{region}`!"); return
                            

                            temp = snap_query.split(' || ')
                            temp2 = []
                            for que in temp:
                                a = await self.quefe(que)
                                try: temp2.append(str(a[0]))
                                except TypeError: temp2.append('0')
                            snapshot = ' || '.join(temp2)

                            await _cursor.execute(f"""INSERT INTO pi_quests VALUES (0, '{quest_code}', '{ctx.author.id}', "{snap_query}", '{snapshot}', '{quest_sample}', '{eval_meth}', "{effect_query}", "{reward_query}", 'FULL');""")
                            
                            await ctx.send(f":white_check_mark: {quest_line.capitalize()} quest `{raw[2]}`|**{quest_name}** accepted! Use `quest` to check your progress."); return
                        # E: Quest's id not found
                        except ValueError: await ctx.send("<:osit:544356212846886924> Quest not found"); return
                        # E: Quest's id not given (and current_quest is also empty)
                        except IndexError: await ctx.send(f"Take what?"); return

                    elif raw[1] == 'leave': 
                        try:
                            region, quest_line = await self.quefe(f"SELECT region, quest_line FROM model_quest WHERE quest_code='{raw[2]}';")
                            # Region check
                            if region != current_place and quest_line != 'DAILY': await ctx.send(f":european_castle: You need to be in `{region}` in order to leave {quest_line} quest `{raw[2]}`"); return
                        except TypeError: await ctx.send("<:osit:544356212846886924> You have not taken this quest yet!"); return

                        if await _cursor.execute(f"DELETE FROM pi_quests WHERE user_id='{ctx.author.id}' AND quest_id={raw[0]} AND stats!='ONGOING'") == 0: await ctx.send(f"<:osit:544356212846886924> You cannot leave a completed quest"); return
                        await ctx.send(f":european_castle: Left {quest_line} quest `{raw[2]}`|`{region}` (id.`{raw[2]}`)"); return

                    elif raw[1] == 'redeem':
                        # Check if the quest is ONGOING     |      Get stuff too :>
                        try: snapshot, snap_query, quest_sample, stats, eval_meth, effect_query, reward_query = await self.quefe(f"SELECT snapshot, snap_query, sample, stats, eval_meth, effect_query, reward_query FROM pi_quests WHERE quest_id={raw[2]} AND user_id='{ctx.author.id}';")
                        except TypeError: await ctx.send(f"<:osit:544356212846886924> Quest not found, **{ctx.author.name}**")
                        snap_query = snap_query.replace('user_id_here', f'{ctx.author.id}')
                        effect_query = effect_query.replace('user_id_here', f'{ctx.author.id}')
                        reward_query = reward_query.replace('user_id_here', f'{ctx.author.id}')

                        if stats == 'DONE': await ctx.send("<:osit:544356212846886924> A quest cannot be redeem twice, scammer... <:fufu:520602319323267082>"); return

                        # Get current snapshot
                        temp = snap_query.split(' || ')
                        quest_sample = quest_sample.split(' || ')
                        snapshot = snapshot.split(' || ')
                        cur_snapshot = []
                        for sque in temp:
                            a = await self.quefe(sque)
                            try: cur_snapshot.append(a[0])
                            except TypeError: cur_snapshot.append('0')

                        # Evaluating
                        if eval_meth == '>=':
                            for a, b, c in zip(cur_snapshot, snapshot, quest_sample):
                                if not (a - b) >= c: await ctx.send(":european_castle: The quest has not been fulfilled yet"); return
                        elif eval_meth == '==':
                            for a, c in zip(cur_snapshot, quest_sample):
                                if not a == c: await ctx.send(":european_castle: The quest has not been fulfilled yet"); return
                        if eval_meth == '<=':
                            for a, b, c in zip(cur_snapshot, snapshot, quest_sample):
                                if not (a - b) <= c: await ctx.send(":european_castle: The quest has not been fulfilled yet"); return
                        elif eval_meth == '>':
                            for a, c in zip(cur_snapshot, quest_sample):
                                if not a >= c: await ctx.send(":european_castle: The quest has not been fulfilled yet"); return
                        elif eval_meth == '<':
                            for a, c in zip(cur_snapshot, quest_sample):
                                if not a <= c: await ctx.send(":european_castle: The quest has not been fulfilled yet"); return

                        # Reward n Affect
                        await _cursor.execute(reward_query + effect_query)
                        # Increase total_quests by 1
                        await _cursor.execute(f"UPDATE pi_guild SET total_quests+=1 WHERE user_id='{ctx.author.id}';")
                        # Remove if daily, else keep
                        if quest_line == 'DAILY': await _cursor.execute(f"DELETE FROM pi_quests WHERE user_id='{ctx.author.id}' AND quest_id={raw[0]};")
                        else: await _cursor.execute(f"UPDATE pi_quests SET stats='DONE' WHERE user_id='{ctx.author.id}' AND quest_id={raw[2]};")
                        # Inform
                        await ctx.send(f":european_castle: Glad we can work out well, {ctx.author.id}. May the Olds look upon you!")
                        # Ranking check
                        sample2 = {'iron': ['bronze', 155], 'bronze': ['silver', 310], 'silver': ['gold', 465], 'gold': ['adamantite', 620], 'adamantite': ['mithryl', 755], 'mithryl': ['n/a', 0]}
                        if await _cursor.execute(f"UPDATE pi_guild SET rank='{sample2[rank][0]}' WHERE user_id='{str(ctx.message.author.id)}' AND total_quests>={sample2[rank][1]};") == 1:
                            await ctx.send(f":beginner: Congrats, {ctx.message.author.mention}! You've been promoted to **{sample2[rank][0].upper()}**!")                         

                except IndexError:
                    bundle = await self.quefe(f"SELECT quest_id, quest_code, snap_query, snapshot, sample, eval_meth FROM pi_quests WHERE user_id='{ctx.author.id}' AND stats IN ('ONGOING', 'FULL');", type='all')
                    # ONGOING quest check
                    if not bundle: await ctx.send(f":european_castle: You have currently no active quest, **{ctx.author.name}**! Try get some and prove yourself."); return
                    for pack in bundle:
                        bundle2 = await self.quefe(f"SELECT name, description, quest_line FROM model_quest WHERE quest_code='{pack[1]}';", type='all')

                    line = f"**『ACTIVE QUEST』** {len(bundle)}\n━━━━━━━━━━━━━━"
                    for pack, pack2 in zip(bundle, bundle2):
                        # Get current snapshot
                        eval_meth = pack[5]
                        temp = pack[2].split(' || ')
                        quest_sample = pack[4].split(' || ')
                        snapshot = pack[3].split(' || ')
                        cur_snapshot = []
                        for sque in temp:
                            a = await self.quefe(sque)
                            try: cur_snapshot.append(a[0])
                            except TypeError: cur_snapshot.append('0')

                        # Create cur_snapshot-sample pack
                        line += f"\n:scroll: `{pack[0]}` · `{pack[1]}`|**{pack2[0]}**"
                        if eval_meth == '>=':
                            for a, b, c in zip(cur_snapshot, snapshot, quest_sample):
                                try: rate = int(((int(a) - int(b))/int(c))*10)
                                except ZeroDivisionError: rate = 0
                                line = line + f"\n:: {'∎'*rate + '━'*(10-rate)} ({int(a) - int(b)}/{c})"
                        elif eval_meth == '==':
                            for a, c in zip(cur_snapshot, quest_sample):
                                if a == c: rate = 10
                                else: rate = 0
                                line = line + f"\n:: {'∎'*rate + '━'*(10-rate)} ({int(a) - int(b)}/{c})"
                        elif eval_meth == '<=':
                            for a, b, c in zip(cur_snapshot, snapshot, quest_sample):
                                try: rate = int(((int(a) - int(b))/int(c))*10)
                                except ZeroDivisionError: rate = 0
                                line = line + f"\n:: {'∎'*rate + '━'*(10-rate)} ({int(a) - int(b)}/{c})"
                        elif eval_meth == '>':
                            for a, c in zip(cur_snapshot, quest_sample):
                                try: rate = int((int(a)/int(c))*10)
                                except ZeroDivisionError: rate = 0
                                line = line + f"\n:: {'∎'*rate + '━'*(10-rate)} ({int(a) - int(b)}/{c})"
                        elif eval_meth == '<':
                            for a, c in zip(cur_snapshot, quest_sample):
                                try: rate = int((int(a)/int(c))*10)
                                except ZeroDivisionError: rate = 0
                                line = line + f"\n:: {'∎'*rate + '━'*(10-rate)} ({int(a) - int(b)}/{c})"

                    await ctx.send(line); return                

            elif raw[0] == 'quests':
                bundle = await self.quefe(f"SELECT quest_code, name, description, quest_line FROM model_quest WHERE region='{current_place}';", type='all')
                completed_bundle = await self.quefe(f"SELECT quest_code FROM pi_quests WHERE user_id='{ctx.author.id}' AND stats='DONE' AND EXISTS (SELECT * FROM model_quest WHERE model_quest.quest_code=pi_quests.quest_code AND region='{current_place}');")
                # None check
                if not completed_bundle: completed_bundle = []

                def makeembed(top, least, pages, currentpage):
                    line = ''

                    line = f"\n```『Total』{len(bundle)}⠀⠀⠀⠀『Done』{len(completed_bundle)}```"
                    for pack in bundle[top:least]:
                        if pack[0] in completed_bundle: marker = ':page_with_curl:'
                        else: marker = ':scroll:'
                        line += f"""\n{marker} **`{pack[0]}`**|`{pack[3].capitalize()} quest`\n⠀⠀⠀|**"{pack[1]}"**\n⠀⠀⠀|*"{pack[2]}"*\n"""

                    reembed = discord.Embed(title = f"`{current_place}`|**QUEST BULLETIN**", colour = discord.Colour(0x011C3A), description=f"{line}\n⠀⠀⠀⠀")
                    reembed.set_footer(text=f"Board {currentpage} of {pages}")
                    return reembed
                    #else:
                    #    await ctx.send("*Nothing but dust here...*")
                
                async def attachreaction(msg):
                    await msg.add_reaction("\U00002b05")    #Left
                    await msg.add_reaction("\U000027a1")    #Right

                pages = int(len(bundle)/5)
                if len(bundle)%5 != 0: pages += 1
                currentpage = 1
                cursor = 0

                emli = []
                for curp in range(pages):
                    myembed = makeembed(currentpage*5-5, currentpage*5, pages, currentpage)
                    emli.append(myembed)
                    currentpage += 1

                msg = await ctx.send(embed=emli[cursor])
                if pages > 1: await attachreaction(msg)
                else: return

                def UM_check(reaction, user):
                    return user.id == ctx.author.id and reaction.message.id == msg.id

                while True:
                    try:    
                        reaction, user = await self.client.wait_for('reaction_add', timeout=15, check=UM_check)
                        if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                            cursor += 1
                            await msg.edit(embed=emli[cursor])
                            try: await msg.remove_reaction(reaction.emoji, user)
                            except discordErrors.Forbidden: pass
                        elif reaction.emoji == "\U00002b05" and cursor > 0:
                            cursor -= 1
                            await msg.edit(embed=emli[cursor])
                            try: await msg.remove_reaction(reaction.emoji, user)
                            except discordErrors.Forbidden: pass
                        elif reaction.emoji == "\U000023ee" and cursor != 0:
                            cursor = 0
                            await msg.edit(embed=emli[cursor])
                            try: await msg.remove_reaction(reaction.emoji, user)
                            except discordErrors.Forbidden: pass
                        elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                            cursor = pages - 1
                            await msg.edit(embed=emli[cursor])
                            try: await msg.remove_reaction(reaction.emoji, user)
                            except discordErrors.Forbidden: pass
                    except asyncio.TimeoutError:
                        break

        except IndexError: await ctx.send(f":european_castle: **`{ctx.message.author.name}`'s G.U.I.L.D card** :european_castle: \n------------------------------------------------\n**`Guild`** · `{name}`|**{self.environ[name]['name']}**\n**`Rank`** · {rank}\n**`Total quests done`** · {total_quests}"); return

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def quest(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        await self.ava_scan(ctx.message)
        raw = list(args)

        name, rank = await self.quefe(f"SELECT name, rank FROM pi_guild WHERE user_id='{ctx.author.id}';")

        try:
            if name == 'n/a' and raw[0] != 'join':
                await ctx.send("<:osit:544356212846886924> You haven't joined any guilds yet!"); return
        except IndexError: await ctx.send("<:osit:544356212846886924> You haven't joined any guilds yet!"); return

        current_place = await self.quefe(f"SELECT cur_PLACE, money FROM personal_info WHERE id='{ctx.author.id}'"); current_place = current_place[0]

        try:
            if raw[0] == 'take':
                # If quest's id given, accept the quest
                try:
                    sample = {'iron': 3, 'bronze': 4, 'silver': 5, 'gold': 6, 'adamantite': 8, 'mithryl': 10}
                    if await _cursor.execute(f"SELECT * FROM pi_quests WHERE user_id='{ctx.author.id}' AND quest_code='{raw[1]}';") >= 1: await ctx.send("<:osit:544356212846886924> Quest has already been taken or done"); return
                    if await _cursor.execute(f"SELECT COUNT(user_id) FROM pi_quests WHERE user_id='{ctx.author.id}' AND stats='ONGOING'") >= sample[rank]: await ctx.send(f"<:osit:544356212846886924> You cannot handle more than **{sample[rank]}** quests at a time")

                    region, quest_code, quest_line, quest_name, snap_query, quest_sample, eval_meth, effect_query, reward_query = await self.quefe(f"SELECT region, quest_code, quest_line, name, snap_query, sample, eval_meth, effect_query, reward_query FROM model_quest WHERE quest_code='{raw[1]}';")
                    snap_query = snap_query.replace('user_id_here', f'{ctx.author.id}')
                    # Region check
                    if region != current_place and quest_line != 'DAILY': await self.client(f":european_castle: Quest `{raw[1]}` is only available in `{region}`!"); return
                    

                    temp = snap_query.split(' || ')
                    temp2 = []
                    for que in temp:
                        a = await self.quefe(que)
                        try: temp2.append(str(a[0]))
                        except TypeError: temp2.append('0')
                    snapshot = ' || '.join(temp2)

                    await _cursor.execute(f"""INSERT INTO pi_quests VALUES (0, '{quest_code}', '{ctx.author.id}', "{snap_query}", '{snapshot}', '{quest_sample}', '{eval_meth}', "{effect_query}", "{reward_query}", 'FULL');""")
                    
                    await ctx.send(f":white_check_mark: {quest_line.capitalize()} quest `{raw[1]}`|**{quest_name}** accepted! Use `quest` to check your progress."); return
                # E: Quest's id not found
                except ValueError: await ctx.send("<:osit:544356212846886924> Quest not found"); return
                # E: Quest's id not given (and current_quest is also empty)
                except IndexError: await ctx.send(f"Take what?"); return

            elif raw[0] == 'leave': 
                try:
                    quest_code = await self.quefe(f"SELECT quest_code FROM pi_quests WHERE quest_id={raw[1]};")
                    region, quest_line, name = await self.quefe(f"SELECT region, quest_line, name FROM model_quest WHERE quest_code='{quest_code[0]}';")
                    # Region check
                    if region != current_place and quest_line != 'DAILY': await ctx.send(f":european_castle: You need to be in `{region}` in order to leave {quest_line} quest `{quest_code}`|**{name}**"); return
                except TypeError: await ctx.send("<:osit:544356212846886924> You have not taken this quest yet!"); return

                if await _cursor.execute(f"DELETE FROM pi_quests WHERE user_id='{ctx.author.id}' AND quest_id={raw[1]} AND stats!='ONGOING'") == 0: await ctx.send(f"<:osit:544356212846886924> You cannot leave a completed quest"); return
                await ctx.send(f":european_castle: Left {quest_line} quest `{quest_code[0]}`|`{name}` (id.`{raw[1]}`)"); return

            elif raw[0] == 'redeem':
                # Check if the quest is ONGOING     |      Get stuff too :>
                try: snapshot, snap_query, quest_sample, stats, eval_meth, effect_query, reward_query = await self.quefe(f"SELECT snapshot, snap_query, sample, stats, eval_meth, effect_query, reward_query FROM pi_quests WHERE quest_id={raw[1]} AND user_id='{ctx.author.id}';")
                except TypeError: await ctx.send(f"<:osit:544356212846886924> Quest not found, **{ctx.author.name}**")
                snap_query = snap_query.replace('user_id_here', f'{ctx.author.id}')
                effect_query = effect_query.replace('user_id_here', f'{ctx.author.id}')
                reward_query = reward_query.replace('user_id_here', f'{ctx.author.id}')

                if stats == 'DONE': await ctx.send("<:osit:544356212846886924> A quest cannot be redeem twice, scammer... <:fufu:520602319323267082>"); return

                # Get current snapshot
                temp = snap_query.split(' || ')
                quest_sample = quest_sample.split(' || ')
                snapshot = snapshot.split(' || ')
                cur_snapshot = []
                for sque in temp:
                    a = await self.quefe(sque)
                    try: cur_snapshot.append(a[0])
                    except TypeError: cur_snapshot.append('0')

                # Evaluating
                if eval_meth == '>=':
                    for a, b, c in zip(cur_snapshot, snapshot, quest_sample):
                        if not (a - int(b)) >= int(c): await ctx.send(":european_castle: The quest has not been fulfilled yet"); return
                elif eval_meth == '==':
                    for a, c in zip(cur_snapshot, quest_sample):
                        if not a == int(c): await ctx.send(":european_castle: The quest has not been fulfilled yet"); return
                if eval_meth == '<=':
                    for a, b, c in zip(cur_snapshot, snapshot, quest_sample):
                        if not (a - int(b)) <= int(c): await ctx.send(":european_castle: The quest has not been fulfilled yet"); return
                elif eval_meth == '>':
                    for a, c in zip(cur_snapshot, quest_sample):
                        if not a >= int(c): await ctx.send(":european_castle: The quest has not been fulfilled yet"); return
                elif eval_meth == '<':
                    for a, c in zip(cur_snapshot, quest_sample):
                        if not a <= int(c): await ctx.send(":european_castle: The quest has not been fulfilled yet"); return

                # Reward n Affect
                await _cursor.execute(reward_query + effect_query)
                # Increase total_quests by 1
                await _cursor.execute(f"UPDATE pi_guild SET total_quests=total_quests+1 WHERE user_id='{ctx.author.id}';")
                # Remove if daily, else keep
                if quest_line == 'DAILY': await _cursor.execute(f"DELETE FROM pi_quests WHERE user_id='{ctx.author.id}' AND quest_id={raw[1]};")
                else: await _cursor.execute(f"UPDATE pi_quests SET stats='DONE' WHERE user_id='{ctx.author.id}' AND quest_id={raw[1]};")
                # Inform
                await ctx.send(f":european_castle: Glad we can work out well, {ctx.author.id}. May the Olds look upon you!")
                # Ranking check
                sample2 = {'iron': ['bronze', 155], 'bronze': ['silver', 310], 'silver': ['gold', 465], 'gold': ['adamantite', 620], 'adamantite': ['mithryl', 755], 'mithryl': ['n/a', 0]}
                if await _cursor.execute(f"UPDATE pi_guild SET rank='{sample2[rank][0]}' WHERE user_id='{str(ctx.message.author.id)}' AND total_quests>={sample2[rank][1]};") == 1:
                    await ctx.send(f":beginner: Congrats, {ctx.message.author.mention}! You've been promoted to **{sample2[rank][0].upper()}**!")                         

        except IndexError:
            bundle = await self.quefe(f"SELECT quest_id, quest_code, snap_query, snapshot, sample, eval_meth FROM pi_quests WHERE user_id='{ctx.author.id}' AND stats IN ('ONGOING', 'FULL');", type='all')
            # ONGOING quest check
            if not bundle: await ctx.send(f":european_castle: You have currently no active quest, **{ctx.author.name}**! Try get some and prove yourself."); return
            bundle2 = []
            for pack in bundle:
                tempbu = await self.quefe(f"SELECT name, description, quest_line FROM model_quest WHERE quest_code='{pack[1]}';", type='all')
                bundle2.append(tempbu[0])

            temb = discord.Embed(title = f"『ACTIVE QUEST』", colour = discord.Colour(0x011C3A), description=f"```━━━━━━━Total [{len(bundle)}]━━━━━━━```")
            for pack, pack2 in zip(bundle, bundle2):
                # Get current snapshot
                eval_meth = pack[5]
                temp = pack[2].split(' || ')
                quest_sample = pack[4].split(' || ')
                snapshot = pack[3].split(' || ')
                cur_snapshot = []
                for sque in temp:
                    a = await self.quefe(sque)
                    try: cur_snapshot.append(a[0])
                    except TypeError: cur_snapshot.append('0')

                line = ''

                # Create cur_snapshot-sample pack
                if eval_meth == '>=':
                    for a, b, c in zip(cur_snapshot, snapshot, quest_sample):
                        try: rate = int(((int(a) - int(b))/int(c))*10)
                        except ZeroDivisionError: rate = 0
                        line = line + f"\n:: {'∎'*rate + '━'*(10-rate)} ({int(a) - int(b)}/{c})"
                elif eval_meth == '==':
                    for a, c in zip(cur_snapshot, quest_sample):
                        if a == c: rate = 10
                        else: rate = 0
                        line = line + f"\n:: {'∎'*rate + '━'*(10-rate)} ({int(a) - int(b)}/{c})"
                elif eval_meth == '<=':
                    for a, b, c in zip(cur_snapshot, snapshot, quest_sample):
                        try: rate = int(((int(a) - int(b))/int(c))*10)
                        except ZeroDivisionError: rate = 0
                        line = line + f"\n:: {'∎'*rate + '━'*(10-rate)} ({int(a) - int(b)}/{c})"
                elif eval_meth == '>':
                    for a, c in zip(cur_snapshot, quest_sample):
                        try: rate = int((int(a)/int(c))*10)
                        except ZeroDivisionError: rate = 0
                        line = line + f"\n:: {'∎'*rate + '━'*(10-rate)} ({int(a) - int(b)}/{c})"
                elif eval_meth == '<':
                    for a, c in zip(cur_snapshot, quest_sample):
                        try: rate = int((int(a)/int(c))*10)
                        except ZeroDivisionError: rate = 0
                        line = line + f"\n:: {'∎'*rate + '━'*(10-rate)} ({int(a) - int(b)}/{c})"
                temb.add_field(name=f"`{pack[0]}` :scroll: {pack2[2].capitalize()} quest `{pack[1]}`|**{pack2[0]}**", value=line)

            await ctx.send(embed=temb, delete_after=20); return                

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def quests(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        await self.ava_scan(ctx.message)
        raw = list(args)

        name = await self.quefe(f"SELECT name FROM pi_guild WHERE user_id='{ctx.author.id}';"); name = name[0]

        try:
            if name == 'n/a' and raw[0] != 'join':
                await ctx.send("<:osit:544356212846886924> You haven't joined any guilds yet!"); return
        except IndexError: await ctx.send("<:osit:544356212846886924> You haven't joined any guilds yet!"); return

        current_place = await self.quefe(f"SELECT cur_PLACE FROM personal_info WHERE id='{ctx.author.id}'"); current_place = current_place[0]

        bundle = await self.quefe(f"SELECT quest_code, name, description, quest_line FROM model_quest WHERE region='{current_place}';", type='all')
        completed_bundle = await self.quefe(f"SELECT quest_code FROM pi_quests WHERE user_id='{ctx.author.id}' AND stats='DONE' AND EXISTS (SELECT * FROM model_quest WHERE model_quest.quest_code=pi_quests.quest_code AND region='{current_place}');")
        # None check
        if not completed_bundle: completed_bundle = []

        def makeembed(top, least, pages, currentpage):
            line = ''

            line = f"\n```『Total』{len(bundle)}⠀⠀⠀⠀『Done』{len(completed_bundle)}```"
            for pack in bundle[top:least]:
                if pack[0] in completed_bundle: marker = ':page_with_curl:'
                else: marker = ':scroll:'
                line += f"""\n{marker} **`{pack[0]}`**|`{pack[3].capitalize()} quest`\n⠀⠀⠀|**"{pack[1]}"**\n⠀⠀⠀|*"{pack[2]}"*\n"""

            reembed = discord.Embed(title = f"`{current_place}`|**QUEST BULLETIN**", colour = discord.Colour(0x011C3A), description=f"{line}\n⠀⠀⠀⠀")
            reembed.set_footer(text=f"Board {currentpage} of {pages}")
            return reembed
            #else:
            #    await ctx.send("*Nothing but dust here...*")
        
        async def attachreaction(msg):
            await msg.add_reaction("\U00002b05")    #Left
            await msg.add_reaction("\U000027a1")    #Right

        pages = int(len(bundle)/5)
        if len(bundle)%5 != 0: pages += 1
        currentpage = 1
        cursor = 0

        emli = []
        for curp in range(pages):
            myembed = makeembed(currentpage*5-5, currentpage*5, pages, currentpage)
            emli.append(myembed)
            currentpage += 1

        msg = await ctx.send(embed=emli[cursor])
        if pages > 1: await attachreaction(msg)
        else: return

        def UM_check(reaction, user):
            return user.id == ctx.author.id and reaction.message.id == msg.id

        while True:
            try:    
                reaction, user = await self.client.wait_for('reaction_add', timeout=15, check=UM_check)
                if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                    cursor += 1
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U00002b05" and cursor > 0:
                    cursor -= 1
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U000023ee" and cursor != 0:
                    cursor = 0
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                    cursor = pages - 1
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
            except asyncio.TimeoutError:
                break

    @commands.command(aliases=['pp'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def party(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        raw = list(args)
        
        try:
            if raw[0] in ['create', 'make']:
                # Check if user has already join a party
                try:
                    party_id, role = await self.quefe(f"SELECT party_id, role FROM pi_party WHERE user_id='{ctx.author.id}';")
                    await ctx.send(f":fleur_de_lis: You've already been a *{role.lower()}* of party `{party_id}`."); return
                except TypeError: pass

                # Create party_id
                count = 0; party_id = 0
                for i in str(ctx.author.id):
                    if count == 3: party_id += int(i); count = 1
                    else: party_id += int(i)*int(i); count += 1

                # Max member
                try: 
                    mxmem = int(raw[1])
                    if mxmem >= 10: mxmem = 10
                except (IndexError, TypeError): mxmem = 5

                # Privacy
                try:
                    if raw[2].lower() not in ['public', 'private']: privac = 'PUBLIC'
                except IndexError: privac = 'PUBLIC'

                try:
                    await _cursor.execute(f"INSERT INTO environ_party VALUES ('{party_id}', 'Party of {ctx.author.name}', '{privac}', 1, {mxmem}); INSERT INTO pi_party VALUES ('{ctx.author.id}', '{party_id}', 'LEADER');")
                except mysqlError.IntegrityError:
                    await _cursor.execute(f"INSERT INTO environ_party VALUES ('{party_id+1}', 'Party of {ctx.author.name}', '{privac}', 1, {mxmem}); INSERT INTO pi_party VALUES ('{ctx.author.id}', '{party_id}', 'LEADER');")
                await ctx.send(embed=discord.Embed(description=f":fleur_de_lis: Party `{party_id}`|**Party of {ctx.author.name}** is created. Good hunt, remnants!", colour=0xF4A400)); return

            elif raw[0] == 'leave':
                # Check if user has joined a party
                try: party_id, role = await self.quefe(f"SELECT party_id, role FROM pi_party WHERE user_id='{ctx.author.id}';")
                except TypeError: await ctx.send(f":fleur_de_lis: You have no party."); return

                # Leave     ||      Party members check
                if role.lower() == 'leader': await ctx.send(":fleur_de_lis: Leaders cannot abandon their comrades! If one's that coward, they'd use `party dismiss`."); return
                await _cursor.execute(f"DELETE FROM pi_party WHERE user_id='{ctx.author.id}' AND party_id='{party_id}'; UPDATE environ_party SET member=member-1 WHERE party_id='{party_id}'; DELETE FROM environ_party WHERE party_id='{party_id}' AND quantity<=0;")

                await ctx.send(embed=discord.Embed(description=f":fleur_de_lis: Left party `{party_id}` as a {role}", colour=0xF4A400)); return

            elif raw[0] == 'dismiss':
                # Check if user has joined a party
                try: party_id, role = await self.quefe(f"SELECT party_id, role FROM pi_party WHERE user_id='{ctx.author.id}';")
                except TypeError: await ctx.send(f":fleur_de_lis: You have no party."); return

                # Leader check
                if role.lower() != 'leader': await ctx.send(f":fleur_de_lis: Only leaders can do this!"); return

                def UMC_check(m):
                    return m.channel == ctx.channel and m.author == ctx.author and m.content == 'dismiss confirm'

                await ctx.send(":fleur_de_lis: Dismissing the party will force other members to leave it too.\n:bell: Are you sure? (Key=`dismiss confirm` | Timeout=10s)")
                try: await self.client.wait_for('message', timeout=10, check=UMC_check)
                except asyncio.TimeoutError: await ctx.send(f"<:osit:544356212846886924> Request time-out!"); return

                await _cursor.execute(f"DELETE FROM pi_party WHERE party_id='{party_id}'; DELETE FROM environ_party WHERE party_id='{party_id}';")
                await ctx.send(":white_check_mark: Dismissed! May the Olds look upon you..."); return

            elif raw[0] in ['member', 'mem', 'status']:
                users = await self.quefe(f"SELECT user_id, role FROM pi_party WHERE party_id=(SELECT party_id FROM pi_party WHERE user_id='{ctx.author.id}');", type='all')
                line = ''
                marker = {'MEMBER': ':fleur_de_lis:', 'LEADER': '<:fleurdelis:543234110559092756>'}
                try:
                    for user in users:
                        LP, MAX_LP, STA, MAX_STA, cur_X, cur_Y, cur_PLACE, merit, name = await self.quefe(f"SELECT LP, MAX_LP, STA, MAX_STA, cur_X, cur_Y, cur_PLACE, merit, name FROM personal_info WHERE id='{user[0]}';")
                        line = line + f"╬ **{name}**[{merit}] {marker[user[1]]} `{cur_X:.3f}`·`{cur_Y:.3f}`·`{cur_PLACE}`|**`LP`**`{int(LP/MAX_LP*100)}%`·**`STA`**`{int(STA/MAX_STA*100)}%`\n"
                except IndexError: await ctx.send(":fleur_de_lis: You have no party."); return
                await ctx.send(embed=discord.Embed(description=line, colour=0xF4A400))

            elif raw[0] == 'invite':
                # Check if user has joined a party
                try: party_id, role = await self.quefe(f"SELECT party_id, role FROM pi_party WHERE user_id='{ctx.author.id}';")
                except TypeError: await ctx.send(f":fleur_de_lis: You have no party."); return

                # Leader check
                if role.lower() != 'leader': await ctx.send(f":fleur_de_lis: Only leaders can do this!"); return

                try: user = ctx.message.mentions[0]
                # E: No mentioning
                except IndexError: await ctx.send(":fleur_de_lis: Please mention someone..."); return

                if user.id == ctx.author.id: await ctx.send("Don't be dumb <:fufu:520602319323267082>"); return

                try: 
                    stats, cur_MOB, cur_USER = await self.quefe(f"SELECT stats, cur_MOB, cur_USER FROM personal_info WHERE id='{user.id}';")
                    if stats == 'DEATH': await ctx.send(f"<:osit:544356212846886924> The dead can't speak."); return
                    if cur_MOB != 'n/a' or cur_USER != 'n/a': await ctx.send(f"<:osit:544356212846886924> The player is in combat!"); return
                # User not incarnate
                except TypeError: await ctx.send(f"<:osit:544356212846886924> User has not incarnated yet, **{ctx.author.name}**"); return

                try:
                    tparty_id, trole = await self.quefe(f"SELECT party_id, role FROM pi_party WHERE user_id='{user.id}';")
                    await ctx.send(f":fleur_de_lis: User has already been a {trole.lower()} of party `{tparty_id}`!"); return
                except TypeError: pass

                msg = await ctx.send(f":fleur_de_lis: Hey {user.mention}, you received a party `{party_id}` invitation from **{ctx.author.name}**!\n:bell: React :white_check_mark: to accept! (Timeout=30s)")
        
                def RUM_check(reaction, u):
                    return u == user and reaction.message.id == msg.id and str(reaction.emoji) == "\U00002705"

                await msg.add_reaction("\U00002705")
                try: await self.client.wait_for('reaction_add', check=RUM_check, timeout=30)
                except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Invitation's declined!"); return

                if await _cursor.execute(f"UPDATE environ_party SET member=member+1 WHERE party_id='{party_id}' AND member<=max_member;") == 0:
                    await ctx.send(f":fleur_de_lis: Party has reached maximum members"); return
                await _cursor.execute(f"INSERT INTO pi_party VALUES ('{user.id}', '{party_id}', 'MEMBER');")
                await ctx.send(f":fleur_de_lis: {ctx.author.mention}, meet your new comrade of party `{party_id}` - {user.mention}."); return

            elif raw[0] == 'kick':
                # Check if user has joined a party
                try: party_id, role = await self.quefe(f"SELECT party_id, role FROM pi_party WHERE user_id='{ctx.author.id}';")
                except TypeError: await ctx.send(f":fleur_de_lis: You have no party."); return

                # Leader check
                if role.lower() != 'leader': await ctx.send(f":fleur_de_lis: Only leaders can do this!"); return

                try: user = ctx.message.mentions[0]
                # E: No mentioning
                except IndexError: 
                    try: 
                        int(raw[1])
                        user.id = str(raw[1])
                    except ValueError: await ctx.send("<:osit:544356212846886924> Invalid id!"); return
                    except IndexError: await ctx.send(":fleur_de_lis: Please mention someone..."); return

                if int(user.id) == ctx.author.id: await ctx.send("Don't be dumb <:fufu:520602319323267082>"); return

                if await _cursor.execute(f"SELECT stats FROM personal_info WHERE id='{user.id}';") == 0:
                    await ctx.send(f"<:osit:544356212846886924> User has not incarnated yet, **{ctx.author.name}**"); return

                if await _cursor.execute(f"SELECT role FROM pi_party WHERE user_id='{user.id}' AND party_id='{party_id}';") == 0:
                    await ctx.send(":fleur_de_lis: The user is not in your party."); return

                await _cursor.execute(f"DELETE FROM pi_party WHERE user_id='{user.id}' AND party_id='{party_id}';")
                if await _cursor.execute(f"UPDATE environ_party SET member=member-1 WHERE party_id='{party_id}' AND member>1;") == 0:
                    await _cursor.execute(f"DELETE FROM environ_party WHERE party_id='{party_id}' AND member=1;")
                    await ctx.send(f":fleur_de_lis: User **{user.name}** is kicked and party {party_id} is deleted."); return
                await ctx.send(f":fleur_de_lis: User **{user.name}** is kicked."); return

            elif raw[0] == 'rally':
                try: party_id, role = await self.quefe(f"SELECT party_id, role FROM pi_party WHERE user_id='{ctx.author.id}';")
                except TypeError: await ctx.send(f":fleur_de_lis: You have no party."); return

                # LEADER
                if role == 'LEADER':
                    # Get party info
                    rally, RP = await self.quefe(f"SELECT rally, RP FROM environ_party WHERE party_id='{party_id}';")
                    if rally == 'ACTIVE': await ctx.send(f":fleur_de_lis: Your party has already rallied, **{ctx.author.name}**!"); return
                    elif RP < 200: await ctx.send(f":fleur_de_lis: Your party's **RP** is **{RP}**, which is lower than **200 RP** required."); return

                    msg = await ctx.send(f":fleur_de_lis: Rallying in 15 secs and **all** members in this region will be teleported to your coordinates. \n:bell: React :x: to *cancel*.")

                    def RUM_check(reaction, u):
                        return u == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) == "\U0000274c"

                    await msg.add_reaction("\U0000274c")
                    try: 
                        await self.client.wait_for('reaction_add', check=RUM_check, timeout=15)
                        await msg.edit(content=":fleur_de_lis: Rally cancelled!"); return
                    except asyncio.TimeoutError: await msg.delete()

                    users = await self.quefe(f"SELECT user_id FROM pi_party WHERE party_id='{party_id}' AND user_id!={ctx.author.id};", type='all')
                    
                    cur_X, cur_Y, cur_PLACE, STA = await self.quefe(f"SELECT cur_X, cur_Y, cur_PLACE, STA FROM personal_info WHERE id='{ctx.author.id}';")
                    # Teleporting
                    tele_count = 0
                    for user_id in users:
                        if await _cursor.execute(f"UPDATE personal_info SET cur_X={cur_X}, cur_Y={cur_Y}, STA=MAX_STA WHERE id='{user_id[0]}' AND cur_PLACE='{cur_PLACE}';"): tele_count += 1
                    
                    if tele_count == 0: await ctx.send(":fleur_de_lis: *oof*... No one gave a :poop:"); return

                    duration = 300
                    await ctx.send(f"<a:WindFlag_SMALL:543592541929472010> {tele_count} answers to the battle-cry. For `{duration}` secs, **TO THE LEADER!**")

                    # Update rallier/party
                    await _cursor.execute(f"UPDATE personal_info SET STA=MAX_STA WHERE id='{ctx.author.id}'; UPDATE environ_party SET rally='ACTIVE', RP={int(RP/2)} WHERE party_id='{party_id}';")
                    await asyncio.sleep(duration)
                    await _cursor.execute(f"UPDATE environ_party SET rally='PASSIVE' WHERE party_id='{party_id}';"); await ctx.send(":fleur_de_lis: Rally stop!"); return

                # MEMBER
                elif role == 'MEMBER':
                    # Get party's info
                    rally, RP = await self.quefe(f"SELECT rally, RP FROM environ_party WHERE party_id='{party_id}';")
                    if rally == 'PASSIVE': await ctx.send(f":fleur_de_lis: Leader has not called for you, **{ctx.author.name}**!"); return
                    elif RP < 200: await ctx.send(f":fleur_de_lis: Your party's **RP** is **{RP}**, which is lower than **200 RP** required."); return

                    # Get leader's info
                    leader_id = await self.quefe(f"SELECT user_id FROM pi_party WHERE party_id='{party_id}' AND role='LEADER';")
                    try: cur_X, cur_Y, cur_PLACE = await self.quefe(f"SELECT cur_X, cur_Y, cur_PLACE FROM personal_info WHERE id='{ctx.author.id}' AND stats!='DEAD' AND cur_PLACE==(SELECT cur_PLACE FROM personal_info WHERE id='{ctx.author.id}');")
                    except TypeError: await ctx.send("Your leader is not *available* <:fufu:520602319323267082>"); return

                    await _cursor.execute(f"UPDATE personal_info SET cur_X={cur_X}, cur_Y={cur_Y}, STA=STA+IF(id='{leader_id}', 5, 0) WHERE id IN ('{leader_id}', '{ctx.author.id}');")
                    await ctx.send(f"<a:WindFlag_SMALL:543592541929472010> Joined the leader at **`{cur_X}`** · **`{cur_Y}`** · **`{cur_PLACE}`**!!"); return
                    


        except IndexError:
            marker = {'MEMBER': ':fleur_de_lis:', 'LEADER': '<:fleurdelis:543234110559092756>'}
            try: party_id, role = await self.quefe(f"SELECT party_id, role FROM pi_party WHERE user_id='{ctx.author.id}';")
            except TypeError: await ctx.send(f"<:osit:544356212846886924> You've not joined any parties yet, **{ctx.author.name}**!"); return

            await ctx.send(embed=discord.Embed(description=f"{marker[role]} Currently in party `{party_id}` as a {role.lower()}.", colour=0xF4A400)); return

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def npc(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        if not args:
            npcs = await self.quefe(f"SELECT name, description, branch, EVO, illulink, npc_code FROM model_npc;", type='all')

            def makeembed(curp, pages, currentpage):
                npc = npcs[curp]

                temb = discord.Embed(title = f"`{npc[5]}` | **{npc[0].upper()}**\n━━━━━━━ {npc[2].capitalize()} NPC-{npc[3]}", description = f"""```dsconfig
    {npc[1]}```""", colour = discord.Colour(0x011C3A))
                temb.set_image(url=random.choice(npc[4].split(' <> ')))

                return temb

            async def attachreaction(msg):
                await msg.add_reaction("\U000023ee")    #Top-left
                await msg.add_reaction("\U00002b05")    #Left
                await msg.add_reaction("\U000027a1")    #Right
                await msg.add_reaction("\U000023ed")    #Top-right

            pages = len(npcs)
            currentpage = 1
            cursor = 0

            emli = []
            for curp in range(pages):
                myembed = makeembed(curp, pages, currentpage)
                emli.append(myembed)
                currentpage += 1

            if pages > 1: 
                msg = await ctx.send(embed=emli[cursor])
                await attachreaction(msg)
            else: msg = await ctx.send(embed=emli[cursor], delete_after=30); return

            def UM_check(reaction, user):
                return user.id == ctx.message.author.id and reaction.message.id == msg.id

            while True:
                try:    
                    reaction, user = await self.client.wait_for('reaction_add', timeout=20, check=UM_check)
                    if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                        cursor += 1
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                    elif reaction.emoji == "\U00002b05" and cursor > 0:
                        cursor -= 1
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                    elif reaction.emoji == "\U000023ee" and cursor != 0:
                        cursor = 0
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                    elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                        cursor = pages - 1
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                except asyncio.TimeoutError:
                    await msg.delete(); return


        try: npc = await self.quefe(f"SELECT name, description, branch, EVO, illulink FROM model_npc WHERE npc_code='{args[0]}';")
        except IndexError: await ctx.send(f"<:osit:544356212846886924> Missing npc's code"); return

        if not npc: await ctx.send("<:osit:544356212846886924> NPC not found!"); return

        temb = discord.Embed(title = f"`{args[0]}` | **{npc[0].upper()}**\n━━━━━━━ {npc[2].capitalize()} NPC-{npc[3]}", description = f"""```dsconfig
{npc[1]}```""", colour = discord.Colour(0x011C3A))
        temb.set_image(url=random.choice(npc[4].split(' <> ')))

        await ctx.send(embed=temb)

    @commands.command(aliases=['I'])
    @commands.cooldown(1, 15, type=BucketType.user)
    async def interact(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        try: intera_kw = args[1]
        except IndexError: intera_kw = 'talk'

        # User's info
        cur_PLACE, cur_X, cur_Y, charm = await self.quefe(f"SELECT cur_PLACE, cur_X, cur_Y, charm FROM personal_info WHERE id='{ctx.author.id}';")

        # NPC / Item
        try:
            try: entity_code, entity_name, illulink = await self.quefe(f"SELECT item_id, name, illulink FROM pi_inventory WHERE item_id='{int(args[0])}' AND user_id='n/a' AND existence='GOOD';")
            # E: Item not found --> Silently ignore
            except TypeError: await ctx.message.add_reaction('\U00002754'); return
        except ValueError:
            try: entity_code, entity_name, illulink = await self.quefe(f"SELECT npc_code, name, illulink FROM model_npc WHERE npc_code='{args[0]}' OR name LIKE '%{args[0]}%'")
            # E: NPC not found --> Silently ignore
            except TypeError: await ctx.message.add_reaction('\U00002754'); return

        # Relationship's info
        try: value_chem, value_impression, flag = await self.quefe(f"SELECT value_chem, value_impression, flag FROM pi_relationship WHERE user_id='{ctx.author.id}' AND target_code='{entity_code}';")
        # E: Relationship not initiated. Init one.
        except TypeError:
            value_chem = 0; value_impression = 0; flag = 'n/a'
            await _cursor.execute(f"INSERT INTO pi_relationship VALUES (0, '{ctx.author.id}', '{entity_code}', {value_chem}, {value_impression}, '{flag}');")

        # Interaction's info
        try: entity_code, trigg, data_goods, effect_query, lines, limit_chem, effect_line = await self.quefe(f"SELECT entity_code, trigg, data_goods, effect_query, line, limit_chem, effect_line FROM environ_interaction WHERE entity_code='{entity_code}' AND intera_kw='{intera_kw}' AND limit_flag='{flag}' AND (({value_chem}>=limit_chem AND chem_compasign='>=') OR ({value_chem}<limit_chem AND chem_compasign='<')) AND (({value_impression}>=limit_impression AND imp_compasign='>=') OR ({value_impression}<limit_impression AND imp_compasign='<')) AND region='{cur_PLACE}' AND limit_Ax<={cur_X} AND {cur_X}<limit_Bx AND limit_Ay<={cur_Y} AND {cur_Y}<limit_By ORDER BY limit_Ax DESC, limit_Bx ASC, limit_Ay DESC, limit_By ASC, limit_chem DESC, limit_impression DESC LIMIT 1;")
        except TypeError: await ctx.message.add_reaction('\U00002754'); return         # Silently ignore         #await ctx.send("<:osit:544356212846886924> Entity not found!"); return

        # TRIGGER !!!!!!!!!!!!!!!!!!!
        if trigg != 'n/a':
            pack = [ctx, data_goods,entity_code]
            try: pack.append(args[2:])
            except IndexError: pass

            await self.trigg[trigg](pack)
            return

        async def line_gen(first_time=False, effect_line=None):
            if effect_line:
                line = [effect_line]
            else:
                linu = random.choice(lines.split(' ||| '))
                line = linu.split(' <> ')
            dura = round(len(line[0])/10)

            if await self.percenter(value_chem - limit_chem, total=100) or first_time:
                temb = discord.Embed(title=f"`{entity_code}` <:__:544354428338044929> **{entity_name}**", description=f"""```css
    {line[0]}```""", colour = 0x36393E)

                try:
                    temb.set_image(url=line[1])
                    dura += 10
                except IndexError: pass
                temb.set_thumbnail(url=random.choice(illulink.split(' <> ')))
                temb.set_footer(text='⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀')
                return temb, dura, True

            else:
                temb = discord.Embed(title=f"`{entity_code}` <:__:544354428338044929> **{entity_name}**", description=f"""```css
    Oops sorry. I gotta go. Bai ya~```""", colour = 0x36393E)
                try:
                    temb.set_image(url=line[1])
                    dura += 10
                except IndexError: pass
                temb.set_thumbnail(url=random.choice(illulink.split(' <> ')))
                temb.set_footer(text='⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀')
                return temb, dura, False

        if effect_query:
            effect_query = effect_query.replace('user_id_here', f"{ctx.author.id}")
            await _cursor.execute(f"UPDATE pi_relationship SET value_chem=value_chem+1+{round(charm/50)} WHERE user_id='{ctx.author.id}' AND target_code='{entity_code}'; {effect_query}")
            temb, dura, checkk = await line_gen(first_time=True, effect_line=effect_line)
            msg = await ctx.send(embed=temb, delete_after=dura+5); return
        else: await _cursor.execute(f"UPDATE pi_relationship SET value_chem=value_chem+{random.choice([-1, 0, 0, 1])}+{round(charm/50)} WHERE user_id='{ctx.author.id}' AND target_code='{entity_code}';")

        temb, dura, checkk = await line_gen(first_time=True)
        msg = await ctx.send(embed=temb)
        await msg.add_reaction(':__:544354428338044929')

        while True:
            def RUM_check(reaction, user):
                return user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) == "<:__:544354428338044929>"

            try:
                await self.client.wait_for('reaction_add', check=RUM_check, timeout=dura)
                temb, dura, checkk = await line_gen()
                if checkk: await msg.edit(embed=temb)
                else: await msg.edit(embed=temb, delete_after=5); return

            except asyncio.TimeoutError:
                await msg.delete(); return






# ================ SOCIAL ==================

    @commands.command()
    @commands.cooldown(1, 90, type=BucketType.user)
    async def marry(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        try: target = ctx.message.mentions[0]
        except IndexError: await ctx.send(f":revolving_hearts: Please tell us your love one, **{ctx.message.author.name}**!"); return

        name, partner, cur_PLACE = await self.quefe(f"SELECT name, partner, cur_PLACE FROM personal_info WHERE id='{ctx.author.id}';")
        try: t_name, t_partner, t_cur_PLACE = await self.quefe(f"SELECT name, partner, cur_PLACE FROM personal_info WHERE id='{target.id}';")
        except TypeError: await ctx.send(f"<:osit:544356212846886924> User has not incarnated yet, {ctx.message.author.name}!"); return

        if 'n/a' not in [partner, t_partner]: await ctx.send(f":revolving_hearts: One of you has already been married, {ctx.author.name}!"); return
        if cur_PLACE != t_cur_PLACE: await ctx.send(f":revolving_hearts: You two need to be in the same region!"); return

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

        msg = await ctx.send(line + f" :revolving_hearts: Hey {target.mention}... {ctx.message.author.mention} is asking you to be their partner!")
        
        def RUM_check(reaction, user):
            return user == target and reaction.message.id == msg.id and str(reaction.emoji) == "\U00002764"

        await msg.add_reaction("\U00002764")
        try: await self.client.wait_for('reaction_add', check=RUM_check, timeout=60)
        except asyncio.TimeoutError: await msg.edit(content=line_no); return
        await msg.edit(content=line_yes)

        # Add partner
        await _cursor.execute(f"UPDATE personal_info SET partner='{target.id}' WHERE id='{ctx.author.id}'; UPDATE personal_info SET partner='{str(ctx.message.author.id)}' WHERE id='{target.id}';")

    @commands.command()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def divorce(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        partner = await self.quefe(f"SELECT partner, (SELECT name FROM personal_info WHERE id=partner) FROM personal_info WHERE id='{ctx.author.id}';")
        if partner[0] == 'n/a': await ctx.send("<:osit:544356212846886924> As if you have a partner :P"); return

        def UMCc_check(m):
            return m.channel == ctx.channel and m.author == ctx.author and m.content == "let's fcking divorce"

        # NAME
        await ctx.send(f":broken_heart: Divorce with **{partner[1]}**?\n||:bell: Timeout=15s · Key=`let's fcking divorce`||")
        try: 
            await self.client.wait_for('message', timeout=15, check=UMCc_check)
        except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request times out!"); return

        await _cursor.execute(f"UPDATE personal_info SET partner='n/a' WHERE id IN ('{ctx.author.id}', '{partner[0]}');")
        await ctx.send(":broken_heart: You are now strangers, to each other.")

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def like(self, ctx, *args):
        cmd_tag = 'like'
        if not await self.ava_scan(ctx.message, type='life_check'): return
        if not await self.__cd_check(ctx.message, cmd_tag, f"<:fufu:508437298808094742> You cannot award more merits at the moment, **{ctx.author.name}**."): return

        # Get target
        try: target = ctx.message.mentions[0]
        except (IndexError, TypeError): await ctx.send(f"<:osit:544356212846886924> Missing the receiver, **{ctx.author.name}**"); return

        if await _cursor.execute(f"UPDATE personal_info SET merit=merit+1 WHERE id='{target.id}';") == 0:
            await ctx.send(f"<:osit:544356212846886924> User has not incarnated, **{ctx.author.name}**!"); return

        await ctx.send(f"<:4_:544354428396896276> **{ctx.author.name}** has given {target.mention} a merit!")
        await self.client.loop.run_in_executor(None, partial(redio.set, f'{cmd_tag}{ctx.author.id}', 'like', ex=86400, nx=True))

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def dislike(self, ctx, *args):
        cmd_tag = 'dislike'
        if not await self.ava_scan(ctx.message, type='life_check'): return
        if not await self.__cd_check(ctx.message, cmd_tag, f"<:fufu:508437298808094742> You cannot negate more merits at the moment, **{ctx.author.name}**."): return

        # Get target
        try: target = ctx.message.mentions[0]
        except (IndexError, TypeError): await ctx.send(f"<:osit:544356212846886924> Missing the target, **{ctx.author.name}**"); return

        if await _cursor.execute(f"UPDATE personal_info SET merit=merit-1 WHERE id='{target.id}';") == 0:
            await ctx.send(f"<:osit:544356212846886924> User has not incarnated, **{ctx.author.name}**!"); return

        await ctx.send(f"<:argh:544354429302865932> **{ctx.author.name}** has humiliate {target.mention}!")
        await self.client.loop.run_in_executor(None, partial(redio.set, f'{cmd_tag}{ctx.author.id}', 'dislike', ex=86400, nx=True))







# ================ KINGDOM =================

    @commands.command(aliases=['kingdom'])
    @commands.cooldown(1, 7, type=BucketType.user)
    async def land(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        raw = list(args)

        try:
            if raw[0] == 'create':
                # User's info
                cur_PLACE, money, merit = await self.quefe(f"SELECT cur_PLACE, money, merit FROM personal_info WHERE id='{ctx.author.id}';")

                if await _cursor.execute(f"SELECT * FROM pi_land WHERE user_id='{ctx.author.id}' AND region='{cur_PLACE}';"): await ctx.send("<:osit:544356212846886924> You can only have 1 land per region"); return
                #try: money_lim = round(10000+(10000/(lands_quantity/10)))
                #except ZeroDivisionError: money_lim = 10000
                #merit_lim = 10*(lands_quantity+1)
                #if not merit_lim: merit_lim = 20
                money_lim = 10000
                merit_lim = 20

                # Region's info
                land_slot, r_biome, r_name = await self.quefe(f"SELECT land_slot, biome, name FROM environ WHERE environ_code='{cur_PLACE}';")

                # Checks
                if money < money_lim: await ctx.send(f":crown: You need at least **<:36pxGold:548661444133126185>{money_lim}** to found a land in `{cur_PLACE}`|**{r_name}**"); return
                elif merit < merit_lim: await ctx.send(f":crown: You need at least **{merit_lim} merits** to found a land in `{cur_PLACE}`|**{r_name}**"); return
                elif land_slot == 0: await ctx.send(f":crown: All slots are full in `{cur_PLACE}`|**{r_name}**. You may try to buy from other players."); return

                # Biome get
                biome = random.choice(r_biome.split(' - '))

                def UMCc_check(m):
                    return m.channel == ctx.channel and m.author == ctx.author

                # NAME
                msg = await ctx.send(":crown: Shall speak your wish, the name is asked?\n||:bell: Timeout=30s · Please give a name||")
                try: 
                    resp = await self.client.wait_for('message', timeout=30, check=UMCc_check)
                    l_name = resp.content
                    await msg.delete()
                except asyncio.TimeoutError: l_name = f"City of **{ctx.author.name}**"; await msg.delete()

                govs = {
                    'FASCISM': (15, 15000, 50),
                    'COMMUNISM': (25, 8000, 70),
                    'DEMOCRACY': (45, 9000, 25)
                }

                def UMCc_check2(m):
                    return m.channel == ctx.channel and m.author == ctx.author and m.content.upper() in govs.keys()

                # GOVERNMENT
                msg = await ctx.send(f":crown: This territory of yours, how would you rule?\n:bell: Timeout=30s || **May your choice be thorough**, reversion is unable: **`{'` · `'.join(govs.keys())}`**")
                try:
                    resp = await self.client.wait_for('message', timeout=30, check=UMCc_check2)
                    l_gov = resp.content.upper()
                    await msg.delete()
                except asyncio.TimeoutError:
                    l_gov = random.choice(govs.keys())
                    await msg.delete()

                def UMCc_check3(m):
                    return m.channel == ctx.channel and m.author == ctx.author and m.content == 'founding confirm'
                
                msg = await ctx.send(f":crown: Then **{l_name}** it is - a **{l_gov.capitalize()}** government - in the middle of `{biome.capitalize()}` biome.\n:bell: Proceed? (Key=`founding confirm`||Timeout=30s)")
                try:
                    resp = await self.client.wait_for('message', timeout=30, check=UMCc_check3)
                    await msg.delete()
                except asyncio.TimeoutError: 
                    await ctx.send(f":crown: Looks like you're not a decisive person heh? Come back later.")
                    await msg.delete(); return

                latest = await self.quefe(f"SELECT land_id FROM pi_land ORDER BY land_id DESC LIMIT 1;")

                await _cursor.execute(f"INSERT INTO pi_land VALUES ({latest[0]+1}, 'land.{latest[0]+1}', '{ctx.author.id}', '{cur_PLACE}', '{biome}', '{l_name}', 'Property of {ctx.author.name}', '{l_gov}', 'lel', 1, 1, {money_lim}, 1000, {govs[l_gov][2]}, 1, 1, 1000, {govs[l_gov][0]}, {govs[l_gov][1]}, 1000, 0, 0, 0.01, 0.01, '', '',''); UPDATE personal_info SET money=money-{money_lim} WHERE id='{ctx.author.id}'; INSERT INTO pi_tax VALUES ('land.{latest[0]+1}', 50, 50, 50, 50)")
                await ctx.send(':crown: Bless you on the road to glory...')
      
            elif raw[0] in ['chart', 'board']:
                cur_PLACE = await self.quefe(f"SELECT cur_PLACE FROM personal_info WHERE id='{ctx.author.id}';"); cur_PLACE = cur_PLACE[0]
                r_name, r_plprice = await self.quefe(f"SELECT name, plot_price FROM environ WHERE environ_code='{cur_PLACE}';")

                await ctx.trigger_typing()
                # Time
                taim = await self.client.loop.run_in_executor(None, self.time_get)                  # year, month, day, hour, minute        

                resus = []
                for t_cursor in [-1, -2, -3, -4, -5]:
                    tatem = list(taim)
                    tatem[2] += t_cursor

                    resu = await self.realty_calc(r_plprice, tatem, [-2, -1, 0, 1, 2])
                    resus.append(resu)
                maxar = max(resus)
                resus.reverse()

                async def magik():
                    # Barring
                    bar_box = Image.new('RGBA', (523, 446), (255, 255, 255, 0))
                    count = 70
                    print(resus)
                    bar = self.prote_lib['stock_bar'][0]

                    bg = copy.deepcopy(self.prote_lib['bg_stock'][0])

                    fnt_region = self.prote_lib['font']['stock_region']
                    fnt_bar = self.prote_lib['font']['stock_region_bar']
                    fnt_name = self.prote_lib['font']['stock_region_name']

                    region_box = Image.new('RGBA', bg.size, (255, 255, 255, 0))

                    stonu = ImageDraw.Draw(bg)

                    for resu in resus:
                        verti_lim = bar_box.width - round(bar_box.size[0] / maxar * resu)
                        print(verti_lim, maxar, bar_box.width, round(bar_box.size[0] / maxar * resu))
                        if (verti_lim - bar_box.width) > -100: verti_lim = bar_box.width - 125

                        bar_box.alpha_composite(bar, dest=(0, count), source=(verti_lim, 0))
                        stonu_X = bg.width - verti_lim - 225
                        if stonu_X <= 234 + 10: stonu_X = 254
                        stonu.text((stonu_X, count - 5), f"$ {resu}", font=fnt_bar, fill=(134, 73, 37, 225))
                        count += 70

                    rb = ImageDraw.Draw(region_box)

                    rb.text((region_box.width/4, 0), f"{cur_PLACE}", font=fnt_region, fill=(134, 73, 37, 225))
                    rb.text((region_box.width/4 + 20, 20), f"{r_name.upper()}", font=fnt_name, fill=(134, 73, 37, 200))

                    region_box = region_box.rotate(90)

                    bg.alpha_composite(region_box, dest=(0, 0), source=(70, 0))
                    bg.alpha_composite(bar_box, dest=(234, 0), source=(0, 0))

                    output_buffer = BytesIO()
                    bg.save(output_buffer, 'png')
                    output_buffer.seek(0)
                    return output_buffer
                
                output_buffer = await magik()
                await ctx.send(file=discord.File(fp=output_buffer, filename='stock.png'))

            else:
                land_code = raw[0]

                if raw[1] == 'description':
                    try: desc = await self.inj_filter(' '.join(raw[2:18]))
                    except IndexError: await ctx.send("<:osit:544356212846886924> Missing content of description!"); return

                    if not await _cursor.execute(f"UPDATE pi_land SET description='{desc}' WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';"):
                        await ctx.send(f"<:osit:544356212846886924> You don't own this land, **{ctx.author.name}**"); return
                    await ctx.send(":white_check_mark: Done")

                elif raw[1] == 'currency':
                    try: currency = await self.inj_filter(' '.join(raw[2:6]))
                    except IndexError: await ctx.send("<:osit:544356212846886924> Missing currency name!"); return

                    if not await _cursor.execute(f"UPDATE pi_land SET currency='{currency}' WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';"):
                        await ctx.send(f"<:osit:544356212846886924> You don't own this land, **{ctx.author.name}**"); return
                    await ctx.send(":white_check_mark: Done")

                elif raw[1] in ['image', 'illustration']:
                    try:
                        illulink = await self.illulink_check(' '.join(raw[2:]))
                        if not illulink: await ctx.send("<:osit:544356212846886924> Invalid link!"); return
                    except IndexError: await ctx.send("<:osit:544356212846886924> Missing link!"); return

                    if not await _cursor.execute(f"UPDATE pi_land SET illulink='{illulink}' WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';"):
                        await ctx.send(f"<:osit:544356212846886924> You don't own this land, **{ctx.author.name}**"); return
                    await ctx.send(":white_check_mark: Done")

                elif raw[1] == 'shop':
                    # Land info
                    try: l_goods, l_region, l_name = await self.quefe(f"SELECT goods, region, name FROM pi_land WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';")
                    except TypeError: await ctx.send(f"<:osit:544356212846886924> You don't own this land, **{ctx.author.name}**"); return
                    
                    # Region info
                    goods, name = await self.quefe(f"SELECT goods, name FROM environ WHERE environ_code='{l_region}';")
                    l_goods = l_goods.split(' - ')
                    try: l_goods = l_goods.remove('')
                    except ValueError: pass

                    try:
                        if raw[2] not in goods.split(' - '): await ctx.send(f"<:osit:544356212846886924> The anchoring region - `{l_region}`|**{name}** - only accepts **`{goods.replace(' - ', '` · `')}`**"); return
                    except IndexError: await ctx.send(f"<:osit:544356212846886924> Missing item's code"); return

                    if not l_goods: l_goods = []

                    if raw[2] in l_goods:
                        l_goods.remove(raw[2])
                        await _cursor.execute(f"UPDATE pi_land SET goods='{' - '.join(l_goods)}' WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';;")
                        await ctx.send(f":crown: Removed `{raw[2]}` from shops in `{land_code}`|**{l_name}**"); return
                    else:
                        l_goods.append(raw[2])
                        await _cursor.execute(f"UPDATE pi_land SET goods='{' - '.join(l_goods)}' WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';;")
                        await ctx.send(f":crown: Added `{raw[2]}` to shops in `{land_code}`|**{l_name}**"); return

                elif raw[1] == 'trader':
                    # Land info
                    try: l_cuisine, l_region, l_name = await self.quefe(f"SELECT cuisine, region, name FROM pi_land WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';")
                    except TypeError: await ctx.send(f"<:osit:544356212846886924> You don't own this land, **{ctx.author.name}**"); return
                    
                    # Region info
                    cuisine, name = await self.quefe(f"SELECT cuisine, name FROM environ WHERE environ_code='{l_region}';")
                    l_cuisine = l_cuisine.split(' - ')
                    try: l_cuisine = l_cuisine.remove('')
                    except ValueError: pass

                    try:
                        if raw[2] not in cuisine.split(' - '): await ctx.send(f"<:osit:544356212846886924> The anchoring region - `{l_region}`|**{name}** - only accepts **`{cuisine.replace(' - ', '` · `')}`**"); return
                    except IndexError: await ctx.send(f"<:osit:544356212846886924> Missing item's code"); return

                    if not l_cuisine: l_cuisine = []

                    if raw[2] in l_cuisine:
                        l_cuisine.remove(raw[2])
                        await _cursor.execute(f"UPDATE pi_land SET cuisine='{' - '.join(l_cuisine)}' WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';;")
                        await ctx.send(f":crown: Removed `{raw[2]}` from traders in `{land_code}`|**{l_name}**"); return
                    else:
                        l_cuisine.append(raw[2])
                        await _cursor.execute(f"UPDATE pi_land SET cuisine='{' - '.join(l_cuisine)}' WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';;")
                        await ctx.send(f":crown: Added `{raw[2]}` to traders in `{land_code}`|**{l_name}**"); return


        except IndexError:
            try: region = f"AND region='{args[0]}'"
            except IndexError: region = ''

            # TAXXXXXXXXXXX
            await _cursor.execute(f"UPDATE pi_land pl INNER JOIN pi_tax px ON px.land_code=pl.land_code SET pl.treasury=pl.treasury+pl.GDP/100*px.tax_treasury*(SELECT DATEDIFF(NOW(), px.last_point)), pl.resource=pl.resource+pl.GDP/100*px.tax_resource*(SELECT DATEDIFF(NOW(), px.last_point)), pl.v_HAPPY=pl.v_HAPPY+pl.GDE/100*px.tax_HAPPY*(SELECT DATEDIFF(NOW(), px.last_point)), pl.faith=pl.faith+pl.GDE/100*px.tax_faith*(SELECT DATEDIFF(NOW(), px.last_point)), px.last_point=NOW() WHERE pl.user_id='{ctx.author.id}'")

            lands = await self.quefe(f"SELECT land_code, name, description, biome, region, currency, government, population, treasury, resource, faith, v_plot, v_plot_total, v_productive, v_HAPPY, v_HEALTH, v_CULTURE, illulink, border_X, border_Y, GDP, GDE FROM pi_land WHERE user_id='{ctx.author.id}' {region};", type='all')

            if not lands: await ctx.send(":crown: You have no lands :>")

            def makeembed(curp, pages, currentpage):
                land = lands[curp]

                reembed = discord.Embed(title = f":crown: `{land[6]}` · `{land[0]}` | **{land[1].capitalize()}**", description = f"""```dsconfig
        {land[2]}```""", colour = discord.Colour(0x011C3A))
                reembed.add_field(name=":scales: Property", value=f"╟`Region` · **{land[4]}**\n╟`Population` · **{land[7]}**\n╟`Plots` · {land[11]}/**{land[12]}**\n╟`Area` · **`{land[18]:.2f} x {land[19]:.2f}`**")
                reembed.add_field(name=":amphora: Resource", value=f"╟`Treasury` · **{land[8]} {land[5]}**\n╟`Resource` · **{land[9]}**\n╟`Faith` · **{land[10]}**\n╟`GDP` · **{land[20]}**\n╟`GDE` · **{land[21]}**")
                reembed.add_field(name=":innocent: Life", value=f"╟`HEALTH` · **{land[15]}**⠀⠀⠀⠀⠀`HAPPY` · **{land[14]}**\n╟`CULTURE` · **{land[16]}**⠀⠀⠀⠀⠀⠀`Productive` · **{land[13]}**")
                reembed.set_footer(text=f"═════╡{len(lands)}╞══╡{currentpage}/{pages}╞═════")
                reembed.set_image(url=land[17])
                reembed.set_thumbnail(url=self.biome[land[3]])

                return reembed

            async def attachreaction(msg):
                await msg.add_reaction("\U000023ee")    #Top-left
                await msg.add_reaction("\U00002b05")    #Left
                await msg.add_reaction("\U000027a1")    #Right
                await msg.add_reaction("\U000023ed")    #Top-right

            pages = len(lands)
            currentpage = 1
            cursor = 0

            emli = []
            for curp in range(pages):
                myembed = makeembed(curp, pages, currentpage)
                emli.append(myembed)
                currentpage += 1

            if pages > 1: 
                msg = await ctx.send(embed=emli[cursor])
                await attachreaction(msg)
            else: msg = await ctx.send(embed=emli[cursor], delete_after=30); return

            def UM_check(reaction, user):
                return user.id == ctx.message.author.id and reaction.message.id == msg.id

            while True:
                try:    
                    reaction, user = await self.client.wait_for('reaction_add', timeout=20, check=UM_check)
                    if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                        cursor += 1
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                    elif reaction.emoji == "\U00002b05" and cursor > 0:
                        cursor -= 1
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                    elif reaction.emoji == "\U000023ee" and cursor != 0:
                        cursor = 0
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                    elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                        cursor = pages - 1
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                except asyncio.TimeoutError:
                    await msg.delete(); return

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def lands(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        # User's info
        cur_PLACE = await self.quefe(f"SELECT cur_PLACE FROM personal_info WHERE id='{ctx.author.id}';")

        # Info
        total_lands = await _cursor.execute(f"SELECT * FROM pi_land WHERE user_id='{ctx.author.id}';")
        lands = await _cursor.execute(f"SELECT * FROM pi_land WHERE user_id='{ctx.author.id}' AND region='{cur_PLACE[0]}';")
        dem = await _cursor.execute(f"SELECT * FROM pi_land WHERE user_id='{ctx.author.id}' AND government='DEMOCRACY';")
        fas = await _cursor.execute(f"SELECT * FROM pi_land WHERE user_id='{ctx.author.id}' AND government='FASCISM';")
        com = await _cursor.execute(f"SELECT * FROM pi_land WHERE user_id='{ctx.author.id}' AND government='COMMUNISM';")

        await ctx.send(f":crown: **{ctx.author.name.upper()}**'s\n════╦═════════════\n**Local**  ║  **{lands}**  lands\n**Total**  ║  **{total_lands}**  lands\n`DEMOCRACY`  ║   **{dem}**  lands\n`FASCISM`      ║   **{fas}**  lands\n`COMMUNISM`  ║   **{com}**  lands\n═══════╩══════════", delete_after=20)

    @commands.command()
    @commands.cooldown(1, 300, type=BucketType.user)
    async def expand(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        raw = list(args)

        # User's info
        charm = await self.quefe(f"SELECT charm FROM personal_info WHERE id='{ctx.author.id}';")

        # Land's info
        try: gov, plot_total, treasury, name, resource, region = await self.quefe(f"SELECT government, v_plot_total, treasury, name, resource, region FROM pi_land WHERE user_id='{ctx.author.id}' AND land_code='{raw[0]}';")
        except IndexError: await ctx.send("<:osit:544356212846886924> Missing land's code"); return
        except TypeError: await ctx.send(f"<:osit:544356212846886924> You don't own this land, {ctx.author.name}"); return
        
        # Get init price
        init_price = await self.quefe(f"SELECT plot_price FROM environ WHERE environ_code='{region}';")
        temppr = init_price[0]

        # Quantity control
        try: quantity = int(raw[1])
        except (IndexError, ValueError): quantity = 1

        # Time
        taim = await self.client.loop.run_in_executor(None, self.time_get)                  # year, month, day, hour, minute

        # Preparing
        if gov != 'FASCISM': init_price = init_price[0] + (10 * plot_total - 10 * charm[0])
        else: init_price = init_price[0]
        final_price = await self.realty_calc(init_price, taim, [-2, -1, 0, 1, 2])
        final_price *= quantity
        if gov == 'DEMOCRACY': resource = round(resource/5)
        else: resource = round(resource/10)

        if treasury < final_price: await ctx.send(f"<:osit:544356212846886924> Your land needs at least <:36pxGold:548661444133126185> **{final_price}** to expand **{quantity} plots**"); return

        #def UMCc_check(m):
        #    return m.channel == ctx.channel and m.author == ctx.author and m.content == 'expansion confirm'

        # NAME
        await ctx.send(f":crown: By {ctx.author.mention}, requesting for `{raw[0]}`|**{name}** of `{region}`:\n╟`Original price` · <:36pxGold:548661444133126185> **{temppr}**/plot\n╟`Plots` · **{quantity}**\n=====================\n╟`Final price` · <:36pxGold:548661444133126185> **{final_price}**\n╟`Resource bonus` · {resource}\n=========================\n:crown: Your land - `{raw[0]}`|**{name}** - has expanded **{quantity} plots!**")
        #try: 
        #     await self.client.wait_for('message', timeout=20, check=UMCc_check)
        #    await msg.delete()
        #except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request timeout!"); await msg.delete(); return

        #await ctx.send(f":crown: Your land - `{raw[0]}`|**{name}** - has expanded **{quantity} plots!**")

        border = random.choice(['border_X', 'border_Y'])
        await _cursor.execute(f"UPDATE pi_land SET v_plot=v_plot+{quantity}, v_plot_total=v_plot_total+{quantity}, treasury=treasury-{final_price}, resource=resource+{resource}, {border}={border}+{0.01*quantity} WHERE land_code='{raw[0]}' AND user_id='{ctx.author.id}'; UPDATE environ SET land_slot=land_slot-{quantity} WHERE environ_code='{region}';")

    @commands.command()
    @commands.cooldown(1, 600, type=BucketType.user)
    async def shrink(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        raw = list(args)

        # Land's info
        try: gov, name, resource, region = await self.quefe(f"SELECT government, name, resource, region FROM pi_land WHERE user_id='{ctx.author.id}' AND land_code='{raw[0]}';")
        except ValueError: await ctx.send("<:osit:544356212846886924> Invalid land's id"); return
        except IndexError: await ctx.send("<:osit:544356212846886924> Missing land's id"); return
        except TypeError: await ctx.send(f"<:osit:544356212846886924> You don't own this land, {ctx.author.name}"); return
        
        # Get init price
        init_price = await self.quefe(f"SELECT plot_price FROM environ WHERE environ_code='{region}';")
        temppr = init_price[0]

        # Quantity control
        try: quantity = int(raw[1])
        except (IndexError, ValueError): quantity = 1

        # Time
        taim = await self.client.loop.run_in_executor(None, self.time_get)                  # year, month, day, hour, minute

        # Preparing
        init_price = init_price[0]
        final_price = await self.realty_calc(init_price, taim, [-2, -1, 0, 1, 2])
        final_price *= quantity
        if gov == 'DEMOCRACY': resource = round(resource/5)
        else: resource = round(resource/10)

        # NAME
        await ctx.send(f":crown: Selling **{quantity}** plots in `{raw[0]}`|**{name}** of `{region}`:\n╟`Original price` · <:36pxGold:548661444133126185> **{temppr}**/plot\n=====================\n╟`Receive` · <:36pxGold:548661444133126185> **{final_price}**\n╟`Resource lost` · {resource}")

        await _cursor.execute(f"UPDATE pi_land SET v_plot=v_plot-{quantity}, v_plot_total=v_plot_total-{quantity}, treasury=treasury-{final_price}, resource=resource-{resource} WHERE land_code='{raw[0]}' AND user_id='{ctx.author.id}'; UPDATE environ SET land_slot=land_slot-{quantity} WHERE environ_code='{region}';")



    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def unit(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        raw = list(args)

        # ADJUSTING
        try:
            try: unit_id = int(raw[0])
            except ValueError: land_cq = f" AND land_code='{args[0]}'"; raise IndexError
            except IndexError: land_cq = ''; raise IndexError

            if raw[1] == 'description':
                try: desc = await self.inj_filter(' '.join(raw[2:18]))
                except IndexError: await ctx.send("<:osit:544356212846886924> Missing content of description!"); return

                if not await _cursor.execute(f"UPDATE pi_unit SET description='{desc}' WHERE unit_id={unit_id} AND land_code IN (SELECT land_code FROM pi_land WHERE user_id='{ctx.author.id}');"):
                    await ctx.send(f"<:osit:544356212846886924> You don't own this land, **{ctx.author.name}**"); return
                await ctx.send(":white_check_mark: Done")

            elif raw[1] == 'name':
                try: name = await self.inj_filter(' '.join(raw[2:6]))
                except IndexError: await ctx.send("<:osit:544356212846886924> Missing unit's name!"); return

                if not await _cursor.execute(f"UPDATE pi_unit SET name='{name}' WHERE unit_id={unit_id} AND land_code IN (SELECT land_code FROM pi_land WHERE user_id='{ctx.author.id}');"):
                    await ctx.send(f"<:osit:544356212846886924> You don't own this land, **{ctx.author.name}**"); return
                await ctx.send(":white_check_mark: Done")

            elif raw[1] in ['image', 'illustration']:
                try:
                    illulink = await self.illulink_check(' '.join(raw[2:]))
                    if not illulink: await ctx.send("<:osit:544356212846886924> Invalid link!"); return
                except IndexError: await ctx.send("<:osit:544356212846886924> Missing link!"); return

                if not await _cursor.execute(f"UPDATE pi_unit SET illulink='{illulink}' WHERE unit_id={unit_id} AND land_code IN (SELECT land_code FROM pi_land WHERE user_id='{ctx.author.id}');"):
                    await ctx.send(f"<:osit:544356212846886924> You don't own this land, **{ctx.author.name}**"); return
                await ctx.send(":white_check_mark: Done")
        
        # ALL UNIT
        except IndexError:
            # Land check
            lands = await self.quefe(f"SELECT land_code, name FROM pi_land WHERE user_id='{ctx.author.id}' {land_cq};", type='all')

            troops = []
            for land in lands:
                troops.append(await self.quefe(f"SELECT v_treasury, v_resource, v_faith, unit_id, name, description, entity, str, intt, sta, speed, stealth, as_NAVAL, as_AIR, as_LAND, as_MIRACLE, as_FAITH, as_ARCH, as_BIO, as_TECH, illulink, '{land[0]}', '{land[1]}', max_sta FROM pi_unit WHERE land_code='{land[0]}';", type='all'))
            troops = troops[0]

            def makeembed(curp, pages, currentpage):
                troop = troops[curp]

                reembed = discord.Embed(title = f"""`{troop[3]}` | **{troop[4].upper()}**
            ━━━━━━ of land `{troop[21]}` | {troop[22]}""", description = f"""```dsconfig
        {troop[5]}```""", colour = discord.Colour(0x011C3A))
                reembed.add_field(name=":label: Value", value=f"╟`Entity` · **{troop[6]}**\n╟`Treasury` · **{troop[0]}**\n╟`Resource` · **{troop[1]}**\n╟`Faith` · **{troop[2]}**")
                reembed.add_field(name=":crossed_swords: Status", value=f"╟`STR` · **{troop[7]}**\n╟`INT` · **{troop[8]}**\n╟`STA` · **{troop[9]}**/**{troop[23]}**\n╟`SPEED` · **{troop[10]}**\n╟`STEALTH` · **{troop[11]}**")
                reembed.add_field(name=":bookmark: Aspect", value=f"╟`Naval`**`{troop[12]}`**⠀·⠀`Air`**`{troop[13]}`**⠀·⠀`Land`**`{troop[14]}`**⠀·⠀`Miracle`**`{troop[15]}`**\n╟`Faith`**`{troop[16]}`**⠀·⠀`Architect`**`{troop[17]}`**⠀·⠀`Bio`**`{troop[18]}`**⠀·⠀`Tech`**`{troop[19]}`**")
                reembed.set_footer(text=f"═════╡{len(troops)}╞══╡{currentpage}/{pages}╞═════")
                reembed.set_image(url=troop[20])

                return reembed

            async def attachreaction(msg):
                await msg.add_reaction("\U000023ee")    #Top-left
                await msg.add_reaction("\U00002b05")    #Left
                await msg.add_reaction("\U000027a1")    #Right
                await msg.add_reaction("\U000023ed")    #Top-right

            pages = len(troops)
            currentpage = 1
            cursor = 0

            emli = []
            for curp in range(pages):
                myembed = makeembed(curp, pages, currentpage)
                emli.append(myembed)
                currentpage += 1

            if pages > 1: 
                msg = await ctx.send(embed=emli[cursor])
                await attachreaction(msg)
            else: msg = await ctx.send(embed=emli[cursor], delete_after=30); return

            def UM_check(reaction, user):
                return user.id == ctx.message.author.id and reaction.message.id == msg.id

            while True:
                try:    
                    reaction, user = await self.client.wait_for('reaction_add', timeout=20, check=UM_check)
                    if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                        cursor += 1
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                    elif reaction.emoji == "\U00002b05" and cursor > 0:
                        cursor -= 1
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                    elif reaction.emoji == "\U000023ee" and cursor != 0:
                        cursor = 0
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                    elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                        cursor = pages - 1
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                except asyncio.TimeoutError:
                    await msg.delete(); return

    @commands.command(aliases=['troops', 'forces'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def units(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        troops = await self.quefe(f"SELECT v_treasury, v_resource, v_faith, unit_code, name, description, entity, str, intt, sta, speed, stealth, as_NAVAL, as_AIR, as_LAND, as_MIRACLE, as_FAITH, as_ARCH, as_BIO, as_TECH, illulink FROM model_unit;", type='all')

        def makeembed(curp, pages, currentpage):
            troop = troops[curp]

            reembed = discord.Embed(title = f"`{troop[3]}` | **{troop[4].upper()}**", description = f"""```dsconfig
    {troop[5]}```""", colour = discord.Colour(0x011C3A))
            reembed.add_field(name=":label: Value", value=f"╟`Entity` · **{troop[6]}**\n╟`Treasury` · **{troop[0]}**\n╟`Resource` · **{troop[1]}**\n╟`Faith` · **{troop[2]}**")
            reembed.add_field(name=":crossed_swords: Status", value=f"╟`STR` · **{troop[7]}**\n╟`INT` · **{troop[8]}**\n╟`STA` · **{troop[9]}**\n╟`SPEED` · **{troop[10]}**\n╟`STEALTH` · **{troop[11]}**")
            reembed.add_field(name=":bookmark: Aspect", value=f"╟`Naval`**`{troop[12]}`**⠀·⠀`Air`**`{troop[13]}`**⠀·⠀`Land`**`{troop[14]}`**⠀·⠀`Miracle`**`{troop[15]}`**\n╟`Faith`**`{troop[16]}`**⠀·⠀`Architect`**`{troop[17]}`**⠀·⠀`Bio`**`{troop[18]}`**⠀·⠀`Tech`**`{troop[19]}`**")
            reembed.set_footer(text=f"═════╡{len(troops)}╞══╡{currentpage}/{pages}╞═════")
            reembed.set_image(url=troop[20])

            return reembed

        async def attachreaction(msg):
            await msg.add_reaction("\U000023ee")    #Top-left
            await msg.add_reaction("\U00002b05")    #Left
            await msg.add_reaction("\U000027a1")    #Right
            await msg.add_reaction("\U000023ed")    #Top-right

        pages = len(troops)
        currentpage = 1
        cursor = 0

        emli = []
        for curp in range(pages):
            myembed = makeembed(curp, pages, currentpage)
            emli.append(myembed)
            currentpage += 1

        if pages > 1: 
            msg = await ctx.send(embed=emli[cursor])
            await attachreaction(msg)
        else: msg = await ctx.send(embed=emli[cursor], delete_after=30); return

        def UM_check(reaction, user):
            return user.id == ctx.message.author.id and reaction.message.id == msg.id

        while True:
            try:    
                reaction, user = await self.client.wait_for('reaction_add', timeout=20, check=UM_check)
                if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                    cursor += 1
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U00002b05" and cursor > 0:
                    cursor -= 1
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U000023ee" and cursor != 0:
                    cursor = 0
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                    cursor = pages - 1
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
            except asyncio.TimeoutError:
                await msg.delete(); return

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def union(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        
        # UNIT info
        try: u1_id = int(args[0])
        except IndexError: await ctx.send("<:osit:544356212846886924> Missing *first* unit's id"); return
        except ValueError: await ctx.send("<:osit:544356212846886924> Invalid unit's id!"); return

        try: u2_id = int(args[1])
        except IndexError: await ctx.send("<:osit:544356212846886924> Missing *second* unit's id"); return
        except ValueError: await ctx.send("<:osit:544356212846886924> Invalid unit's id!"); return

        # LAND list
        lands = await self.quefe(f"SELECT land_code FROM pi_land WHERE user_id='{ctx.author.id}';", type='all')
        try: lands = lands[0]
        except IndexError: await ctx.send("<:osit:544356212846886924> You have no land"); return
        lands_1 = "', '".join(lands)
        lands_2 = f" AND m.land_code IN ({lands_1})"
        lands_1 = f" AND p.land_code IN ({lands_1})"

        def UMCc_check(m):
            return m.channel == ctx.channel and m.author == ctx.author and m.content == 'union confirm'

        # NAME
        await ctx.send(f":crown: {ctx.author.mention} requrest to union unit `{u2_id}` to unit `{u1_id}`, which will disband the prior. Proceed?\n||:bell: Timeout=15s · Key=`union confirm`||")
        try: 
            await self.client.wait_for('message', timeout=15, check=UMCc_check)
        except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request times out!"); return


        # UNION
        a = await _cursor.execute(f"""UPDATE pi_unit p INNER JOIN pi_unit m ON m.unit_id={u2_id} {lands_2}
                                        SET p.entity=p.entity+quantity_in*m.entity, p.max_entity=p.max_entity+quantity_in*m.entity, p.evo=p.evo+m.evo, p.str=p.str+m.str, p.intt=p.intt+m.intt, p.sta=p.sta+m.sta, p.speed=p.speed+m.speed, p.stealth=p.stealth+m.stealth, p.as_NAVAL=p.as_NAVAL+m.as_NAVAL, p.as_AIR=p.as_AIR+m.as_AIR, p.as_LAND=p.as_LAND+m.as_LAND, p.as_MIRACLE=p.as_MIRACLE+m.as_MIRACLE, p.as_FAITH=p.as_FAITH+m.as_FAITH, p.as_ARCH=p.as_ARCH+m.as_ARCH, p.as_BIO=p.as_BIO+m.as_BIO, p.as_TECH=p.as_TECH+m.as_TECH, p.v_treasury=p.v_treasury+m.v_treasury, p.v_resource=p.v_resource+m.v_resource, p.v_faith=p.v_faith+m.v_faith, p.v_plot=p.v_plot+m.v_plot
                                        WHERE p.unit_id={u1_id} {lands_1};""")

        if not a: await ctx.send("<:osit:544356212846886924> You don't own one of those units!"); return

        await _cursor.execute(f"DELETE FROM pi_unit WHERE unit_id={u2_id};")

        await ctx.send(":crown: The deed is done. Result can be checked!")

    @commands.command()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def order(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        raw = list(args)

        # ============ INFO GET =============
        ## ITEM ======
        try:
            __swi = 'id'
            try: i_name, item_code, i_quantity, i_tags, i_id = await self.quefe(f"SELECT name, item_code, quantity, tags, item_id FROM pi_inventory WHERE existence='GOOD' AND user_id='{ctx.author.id}' AND item_id={int(raw[1])} AND quantity>0;")
            except ValueError: i_name, item_code, i_quantity, i_tags, i_id = await self.quefe(f"SELECT name, item_code, quantity, tags, item_id FROM pi_inventory WHERE existence='GOOD' AND user_id='{ctx.author.id}' AND item_code='{raw[1]}' AND quantity>0;")
        except IndexError: await ctx.send(f":crown: Please provide `item_id`, **{ctx.author.name}**."); return
        except TypeError:
            ## INFRASTRUCTURE ======
            if raw[1].startswith('u'):
                try:
                    i_name, item_code, i_quantity, i_tags = await self.quefe(f"SELECT name, unit_code, entity, tags FROM model_unit WHERE unit_code='{raw[1]}';")
                    __swi = 'code'
                except TypeError: await ctx.send(f"<:osit:544356212846886924> Unit's not found!"); return
            else: await ctx.send(f":crown: You don't own this item, **{ctx.author.name}**!"); return

        # Quantity control
        try: quantity = int(raw[2])
        except (IndexError, TypeError): quantity = 1
        if __swi == 'id':
            if quantity == i_quantity:
                quantity = i_quantity
                decrq = f" UPDATE pi_inventory SET existence='BAD' WHERE item_id={i_id} AND user_id='{ctx.author.id}';"
            elif quantity > i_quantity: await ctx.send("<:osit:544356212846886924> Not enough items!"); return
            else: decrq = f" UPDATE pi_inventory SET quantity=quantity-{quantity} WHERE item_id={i_id} AND user_id='{ctx.author.id}';"
        else: decrq = ''
        if ' token ' in i_tags: decrq = ''

        # Order's info          ||      Depend on quantity, the outcome will be different
        try: o_itc, description, o_urc, o_itq, o_urintt, o_ursta, o_urasp, o_enr, o_lpl, o_lbre, o_lpol, o_ltr, o_lres, o_lfa, o_dura, o_re, o_req = await self.quefe(f"SELECT item_code, description, unit_required_code, item_quantity, unit_required_intt, unit_required_sta, unit_required_aspect, entity_required, land_plot, land_biome_restricted, land_pollution, land_treasury, land_resource, land_faith, duration, reward, reward_query FROM model_order WHERE item_code='{item_code}' AND item_quantity={quantity};")
        except TypeError: await ctx.send(f"<:osit:544356212846886924> You tried giving {quantity} `{item_code}`|**{i_name}** to them, but nothing happened..."); return

        # Unit's info       ||      For checking entity, intt, asp...
        try: land_code, u_name, entity, intt, asp, u_sta = await self.quefe(f"SELECT land_code, name, entity, intt, {o_urasp}, sta FROM pi_unit WHERE unit_id={raw[0]};")
        except ValueError: await ctx.send(f"<:osit:544356212846886924> Invalid `unit's id`!"); return
        except TypeError: await ctx.send(f":crown: You don't own this unit, **{ctx.author.name}**!"); return
        except IndexError: await ctx.send(f":crown: Please provide `unit's id`, **{ctx.author.name}**."); return

        # Land's info
        try: l_biome, l_name, l_plot, l_productive, l_HAPPY, l_HEALTH, l_CULTURE, l_gov, l_treasury, l_resource, l_faith, currency = await self.quefe(f"SELECT biome, name, v_plot, v_productive, v_HAPPY, v_HEALTH, v_CULTURE, government, treasury, resource, faith, currency FROM pi_land WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';")
        except TypeError: await ctx.send(f"<:osit:544356212846886924> You don't own this land! (`{land_code}`)"); return

        # Unit_required's info      ||      Mainly for checking entity_quantity
        if o_urc == 'n/a':
            uu_rq = 0
            uu_name = 'n/a'
            uu_id = 0
        else:
            try: uu_rq, uu_name, uu_id = await self.quefe(f"SELECT entity, name, unit_id FROM pi_unit WHERE land_code='{land_code}' AND unit_code='{o_urc}';")
            except TypeError: await ctx.send(f"<:osit:544356212846886924> Your land - `{land_code}`|**{l_name}** - is missing infrastructure (code.`{o_urc}`)"); return

        # =========== PREPARE 1 ===========
        if l_gov == 'COMMUNISM': 
            cost_entity = o_enr
            cost_entity += round(cost_entity) * o_itq
        elif l_gov == 'DEMOCRACY':
            cost_entity = o_enr - l_HAPPY/100 * o_itq
            cost_entity -= round(cost_entity/100*l_HAPPY) * o_itq
        else: cost_entity = o_enr
        if cost_entity < 0: cost_entity = 0
        
        if l_biome in o_lbre.split(' || '):
            cost_sta = o_ursta * 2
            try: cost_infra = o_lpl + round(o_lpl/(asp + 1))
            except ZeroDivisionError: cost_infra = o_lpl + o_lpl
        else: cost_sta = o_ursta; cost_infra = o_lpl
        if cost_entity != o_enr: 
            try: cost_sta = round(cost_sta/o_enr*cost_entity)
            except ZeroDivisionError: cost_sta = round(cost_sta*cost_entity)

        if l_gov != 'COMMUNISM': cost_plot = o_lpl - (asp * o_itq)
        if cost_plot < 0: cost_plot = 0

        if l_gov == 'COMMUNISM':
            o_lfa = o_lfa - round(o_lfa/1000*l_CULTURE)
            if o_lfa < 0: o_lfa = 0
        elif l_gov == 'DEMOCRACY':
            try:
                o_ltr -= round(l_treasury/o_ltr)/o_ltr
                if o_ltr < 0: o_ltr = 0
            except ZeroDivisionError: pass
        elif l_gov == 'FASCISM':
            try:
                o_lres = round(o_lres*(1000/l_HEALTH))
                if o_lres < 0: o_lres = 0
            except ZeroDivisionError: pass

        # =========== CHECK ===========
        if o_urc != 'n/a':
            if uu_rq < cost_infra: await ctx.send(f"<:osit:544356212846886924> Your land - `{land_code}`|**{l_name}** - needs at least **{cost_infra}** infrastructure (code.`{o_urc}`) for this order"); return
        if entity < cost_entity: await ctx.send(f"<:osit:544356212846886924> Unit `{raw[0]}`|**{u_name}** needs at least **{cost_entity} entities** for this order"); return
        if intt < o_urintt: await ctx.send(f"<:osit:544356212846886924> Unit `{raw[0]}`|**{u_name}** needs at least **{o_urintt} INT** for this order"); return
        if l_plot < cost_plot: await ctx.send(f"<:osit:544356212846886924> Your land - `{land_code}`|**{l_name}** - needs at least **{cost_plot} plots** for this order"); return
        if l_treasury < o_ltr: await ctx.send(f"<:osit:544356212846886924> Your land - `{land_code}`|**{l_name}** - needs at least **{o_ltr} {currency}** for this order"); return
        if l_resource < o_lres: await ctx.send(f"<:osit:544356212846886924> Your land - `{land_code}`|**{l_name}** - needs at least **{o_lres} resources** for this order"); return
        if l_faith < o_lfa: await ctx.send(f"<:osit:544356212846886924> Your land - `{land_code}`|**{l_name}** - needs at least **{o_lfa} faith** for this order"); return

        # =========== PREPARE 2 ===========
        limit = round(o_dura/10)
        if l_productive == 0: l_productive = random.choice([0, 1])
        try: duration = round((o_dura/cost_entity*o_enr)/1000)
        except ZeroDivisionError: duration = round((o_dura*o_enr)/1000)
        duration += round(abs(l_productive/1000*(1000 - l_productive)) + duration/(asp + 1))
        dis_sta = o_ursta - u_sta
        if dis_sta > 5000: await ctx.send("<:osit:544356212846886924> Your unit. Needs. Rest."); return
        elif dis_sta > 0: duration = duration + dis_sta*10
        if duration < limit: duration = limit
        end_point = datetime.now() + timedelta(seconds=int(duration))
        end_point = end_point.strftime('%Y-%m-%d %H:%M:%S')

        if o_lpol >= 0: cost_pol = o_lpol + round((abs(l_productive - 1000)/(asp + 1)))
        else: cost_pol = o_lpol - round((abs(l_productive - 1000)/(asp + 1)))
        temp = l_productive - cost_pol
        if temp <= 0:
            if l_gov == 'COMMUNISM': xtra = f", v_HEALTH=v_HEALTH+{temp}, v_productive={temp}"
            elif l_gov == 'DEMOCRACY': xtra = f", v_HAPPY=v_HAPPY+{temp}, v_productive={temp}"
            else: f", v_productive={temp}"
        else: xtra = f", v_productive={temp}"

        # =========== CONFIRM ==============
        temb = discord.Embed(title=f":crown: From **{ctx.author.name}** ➠ to `{raw[0]}`|**{u_name}** of `{land_code}`|**{l_name}**", description=f"""```dsconfig
    {description}```""", colour = discord.Colour(0x011C3A))
        temb.add_field(name="COST", value=f"╟ {quantity} `{o_itc}`|**{i_name}**\n╟`TREASURY` · **{o_ltr}**\n╟`RESOURCE` · **{o_lres}**\n╟`FAITH` · **{o_lfa}**")
        temb.add_field(name="CONSEQUENCES", value=f"\n╟`Pollution` · **{cost_pol}**\n╟**{cost_infra}** plots of `{uu_id}`|**{uu_name}**\n╟**{cost_entity}** entities of unit `{raw[0]}`|**{u_name}**\n╟`STA` · **{cost_sta}**")
        temb.set_footer(text=f"[Est. duration] {duration} seconds", icon_url=ctx.author.avatar_url)

        msg = await ctx.send(embed=temb)
        await msg.add_reaction("\U00002705")
        def RUM_check(reaction, user):
            return user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) == '\U00002705'
        try:
            await self.client.wait_for('reaction_add', check=RUM_check, timeout=20)
            await ctx.send(f":crown: Order has been successfully sent, and will be fulfilled after **`{duration}` seconds!**")
            await msg.delete()
        except asyncio.TimeoutError: 
            await ctx.send("<:osit:544356212846886924> Request timeout")
            await msg.delete()
            return

        # =========== QUERY =============
        reward_query = o_req.replace("user_id_here", f'{ctx.author.id}').replace("quantity_here", f"{quantity}").replace("land_code_here", f"{land_code}").replace("unit_id_here", f"{raw[0]}")
        reduce_query = ''
        if cost_infra: reward_query = reward_query + f"UPDATE pi_land SET v_plot=v_plot+{cost_infra} WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';"
        # This one is for unit2
        if o_urc != 'n/a':
            reward_query = reward_query + f" UPDATE pi_unit SET entity=entity+{cost_infra} WHERE unit_code='{o_urc}' AND land_code='{land_code}';"
            reduce_query = f"UPDATE pi_unit SET entity=entity-{cost_infra} WHERE unit_code='{o_urc}' AND land_code='{land_code}';"        # DO NOT TAKE THIS ELSEWHERE, other records has n/a in code too
        # This one is for unit1
        reward_query = reward_query + f" UPDATE pi_unit SET entity=entity+{cost_entity} WHERE unit_id={raw[0]} AND land_code='{land_code}'; "

        cost_query = f"""{decrq}
                        UPDATE pi_unit SET sta=sta-{cost_sta}, entity=entity-{cost_entity} WHERE unit_id={raw[0]} AND land_code='{land_code}';
                        {reduce_query}
                        UPDATE pi_land SET treasury=treasury-{o_ltr}, resource=resource-{o_lres}, faith=faith-{o_lfa}{xtra}, v_plot=v_plot-{cost_infra} WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';
                        INSERT INTO pi_order VALUES (0, {raw[0]}, {uu_id}, '{land_code}', "{description}", "{end_point}", "{o_re}", "{reward_query}");"""

        # ORDER
        await _cursor.execute(cost_query)

    @commands.command()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def orders(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        land_dict = {}
        lands = await self.quefe(f"SELECT land_code, name FROM pi_land WHERE user_id='{ctx.author.id}';", type='all')
        if not lands: await ctx.send(f"<:osit:544356212846886924> You have no land, **{ctx.author.name}**"); return
        for land in lands:
            land_dict[f"{land[0]}"] = land[1]

        orders = await self.quefe(f"""SELECT order_id, unit_id, land_code, description, end_point FROM pi_order WHERE land_code IN ('{"' '".join(land_dict.keys())}');""", type='all')

        def makeembed(top, least, pages, currentpage):
            line = '\n'

            for order in orders[top:least]:
                delta = relativedelta(order[4], datetime.now())
                line = line + f"""╡**`{delta.hours:02d}:{delta.minutes:02d}:{delta.seconds:02d}`**╞ `{order[0]}`|"{order[3]}" || `{order[1]}` of `{order[2]}`|{land_dict[f'{order[2]}']}||\n"""

            reembed = discord.Embed(title = f":crown: **{ctx.author.name.upper()}**'s Orders", colour = discord.Colour(0x011C3A), description=line)
            reembed.set_footer(text=f'{len(orders)} | {currentpage}/{pages}')
            return reembed
            #else:
            #    await ctx.send("*Nothing but dust here...*")
        
        async def attachreaction(msg):
            await msg.add_reaction("\U000023ee")    #Top-left
            await msg.add_reaction("\U00002b05")    #Left
            await msg.add_reaction("\U000027a1")    #Right
            await msg.add_reaction("\U000023ed")    #Top-right

        pages = len(orders)//4
        if len(orders)%4 != 0: pages += 1
        currentpage = 1
        cursor = 0

        emli = []
        for curp in range(pages):
            myembed = makeembed(currentpage*4-4, currentpage*4, pages, currentpage)
            emli.append(myembed)
            currentpage += 1

        if not emli: await ctx.send(":crown: All orders are fulfilled!"); return
        if pages > 1: 
            await attachreaction(msg)
            msg = await ctx.send(embed=emli[cursor])
        else: msg = await ctx.send(embed=emli[cursor], delete_after=30); return

        def UM_check(reaction, user):
            return user.id == ctx.message.author.id and reaction.message.id == msg.id

        while True:
            try:    
                reaction, user = await self.client.wait_for('reaction_add', timeout=20, check=UM_check)
                if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                    cursor += 1
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U00002b05" and cursor > 0:
                    cursor -= 1
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U000023ee" and cursor != 0:
                    cursor = 0
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                    cursor = pages - 1
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
            except asyncio.TimeoutError:
                await msg.delete(); return

    @commands.command(aliases=['col'])
    @commands.cooldown(3, 5, type=BucketType.user)
    async def collect(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        # Order's info
        try: 
            end_point, rewards, reward_query, land_code, description = await self.quefe(f"SELECT end_point, rewards, reward_query, land_code, description FROM pi_order WHERE order_id={int(args[0])};")
        except ValueError: await ctx.send("<:osit:544356212846886924> Invalid `order_id`!"); return
        except IndexError: await ctx.send("<:osit:544356212846886924> Missing `order_id`"); return
        except TypeError: await ctx.send("<:osit:544356212846886924> Order's not found!"); return

        # Order's check
        if await _cursor.execute(f"SELECT * FROM pi_land WHERE user_id='{ctx.author.id}' AND land_code='{land_code}';") == 0: await ctx.send("<:osit:544356212846886924> Order's not found!"); return

        delta = relativedelta(end_point, datetime.now())
        if datetime.now() < end_point: await ctx.send(f":cowboy: *{description}* **`{delta.hours:02d}:{delta.minutes:02d}:{delta.seconds:02d}`** to go!"); return

        await ctx.send(f":crown: **Order's done!** You've received...\n{rewards}", delete_after=20)

        a = await _cursor.execute(f"{reward_query} DELETE FROM pi_order WHERE order_id={args[0]}")
        print(a)


    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def tax(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return
        sec = {'treasury': ['tax_treasury', 'tax_resource', 'resource'], 'resource': ['tax_resource', 'tax_treasury', 'treasury'], 'faith': ['tax_faith', 'tax_HAPPY','happy'], 'happy': ['tax_HAPPY', 'tax_faith', 'faith']}

        try:
            # Info get
            land_code = args[0]
            try:
                if args[1] not in sec.keys(): await ctx.send(f"<:osit:544356212846886924> Unknown tax' type. Please use: **`{'` `'.join(sec.keys())}`**)"); return
            except IndexError: await ctx.send(f"<:osit:544356212846886924> Missing tax' type. Please use: (**`{'` `'.join(sec.keys())}`**)"); return
            try:
                if int(args[2]) > 100 or int(args[2]) < 0: await ctx.send("<:osit:544356212846886924> Percentage only varies from 0 - 100"); return
            except IndexError: await ctx.send("<:osit:544356212846886924> Missing percentage (0 - 100)"); return
            except ValueError: await ctx.send("<:osit:544356212846886924> Invalid percentage!"); return

            # Make effect
            if await _cursor.execute(f"UPDATE pi_tax SET {sec[args[1]][0]}={args[2]}, {sec[args[1]][1]}=100-{args[2]} WHERE land_code='{land_code}' AND EXISTS (SELECT * FROM pi_land WHERE land_code='{land_code}');") == 0:
                await ctx.send(f"<:osit:544356212846886924> You don't own this land, **{ctx.author.name}**"); return
            await ctx.send(f":crown: **{args[1].capitalize()} tax** is set to **{args[2]}%**, and also changes **{sec[args[1]][2].capitalize()} tax**.")
        
        # Tax board
        except IndexError:
            # TAX info
            taxes = await self.quefe(f"SELECT land_code, tax_treasury, tax_resource, tax_HAPPY, tax_faith FROM pi_tax WHERE land_code IN (SELECT land_code FROM pi_land WHERE user_id='{ctx.author.id}');", type='all')
            if not taxes: await ctx.send(f"<:osit:544356212846886924> You have no land, **{ctx.author.name}**"); return

            def makeembed(curp, pages, currentpage):
                tax = taxes[curp]

                reembed = discord.Embed(title = f":crown: T A X || **`{tax[0]}`**⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", description = f"""```prolog
    Treasury/Resource: {tax[1]}/{tax[2]} %
    Happy/Faith: {tax[3]}/{tax[4]} %```""", colour = discord.Colour(0x011C3A))

                return reembed

            async def attachreaction(msg):
                await msg.add_reaction("\U000023ee")    #Top-left
                await msg.add_reaction("\U00002b05")    #Left
                await msg.add_reaction("\U000027a1")    #Right
                await msg.add_reaction("\U000023ed")    #Top-right

            pages = len(taxes)
            currentpage = 1
            cursor = 0

            emli = []
            for curp in range(pages):
                myembed = makeembed(curp, pages, currentpage)
                emli.append(myembed)
                currentpage += 1

            if pages > 1: 
                msg = await ctx.send(embed=emli[cursor])
                await attachreaction(msg)
            else: msg = await ctx.send(embed=emli[cursor], delete_after=15); return

            def UM_check(reaction, user):
                return user.id == ctx.message.author.id and reaction.message.id == msg.id

            while True:
                try:    
                    reaction, user = await self.client.wait_for('reaction_add', timeout=10, check=UM_check)
                    if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                        cursor += 1
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                    elif reaction.emoji == "\U00002b05" and cursor > 0:
                        cursor -= 1
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                    elif reaction.emoji == "\U000023ee" and cursor != 0:
                        cursor = 0
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                    elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                        cursor = pages - 1
                        await msg.edit(embed=emli[cursor])
                        try: await msg.remove_reaction(reaction.emoji, user)
                        except discordErrors.Forbidden: pass
                except asyncio.TimeoutError:
                    await msg.delete(); return





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
    # Melee PVE |      Start the USER MELEE phase.     |          Melee PVP |       Start the USER MELEE attacking phase.
    @commands.command(pass_context=True, aliases=['atk'])
    @commands.cooldown(1, 3, type=BucketType.user)
    async def attack(self, ctx, *args):
        """ -avaattack [moves] [target]
            -avaattack [moves]              
            <!> ONE target of each creature type at a time. Mobs always come first, then user. Therefore you can't fight an user while fighting a mob
            <!> DO NOT lock on current_enemy at the beginning. Do it at the end."""
        if not await self.ava_scan(ctx.message, type='life_check'): return

        raw = list(args); __mode = 'PVP'

        # HANDLING CHECK =====================================
        try:
            note = {'both': '<:right_hand:521197677346553861><:left_hand:521197732162043922>', 'right': '<:right_hand:521197677346553861>', 'left': '<:left_hand:521197732162043922>'}

            await ctx.send(f'{note[raw[0]]} Changed to **{raw[0].upper()} hand** pose')
            await _cursor.execute(f"UPDATE personal_info SET combat_HANDLING='{raw[0].lower()}' WHERE id='{str(ctx.message.author.id)}';"); return
        # E: Pose not given
        except IndexError: await ctx.send(f"<:osit:544356212846886924> **{ctx.message.author.name}**, missing arguments!"); return
        # E: Moves given, not pose
        except KeyError: pass

        # Get main_weapon, handling     |      as well as checking coord
        try: combat_HANDLING, main_weapon = await self.quefe(f"SELECT combat_HANDLING, IF(combat_HANDLING IN ('both', 'right'), right_hand, left_hand) FROM personal_info WHERE id='{str(ctx.message.author.id)}' AND cur_X>1 AND cur_Y>1;")
        # E: User in PB
        except TypeError: await ctx.send("<:osit:544356212846886924> You can't fight inside **Peace Belt**!"); return

        # Check if it's a PVP or PVE call
        # Then get the target (Mob/User)

        # Get user's info (always put last, for the sake of efficience)
        name, cur_MOB, cur_PLACE, cur_X, cur_Y, STA, STR = await self.quefe(f"SELECT name, cur_MOB, cur_PLACE, cur_X, cur_Y, STA, STR FROM personal_info WHERE id='{str(ctx.message.author.id)}';")


        # INPUT CHECK =========================================
        target = None; target_id = None; raw_move = None

        for copo in raw:
            # PVP   |    USING MENTION
            if copo.startswith('<@'):
                target = ctx.message.mentions[0]; target_id = str(target.id)
                __bmode = 'DIRECT'

            # PVE   |    USING MOB'S ID
            elif copo.startswith('mob.') or copo.startswith('boss'):
                # If there's no current_enemy   |   # If there is, and the target is the current_enemy
                if cur_MOB == 'n/a' or copo == cur_MOB:
                    if copo == 'boss': 
                        target = await self.quefe(f"SELECT mob_id FROM environ_mob WHERE branch='boss' AND region='{cur_PLACE}';"); target = target[0]; __mode = 'PVE'; target_id = target
                    else: target = copo; __mode = 'PVE'; target_id = target
                # If there is, but the target IS NOT the current_enemy
                elif copo != cur_MOB:
                    await ctx.send(f"<:osit:544356212846886924> Please finish your current fight with the `{self.ava_dict[str(ctx.message.author.id)]['realtime_zone']['current_enemy']['mob'][0]}`!"); return

            # PVP   |    USING USER'S ID
            else:
                try:
                    try: 
                        target = await self.client.get_user(int(copo))
                        if not target: await ctx.send("<:osit:544356212846886924> User's not found"); return
                        target_id = target.id
                    except (discordErrors.NotFound, discordErrors.HTTPException, TypeError): await ctx.send("<:osit:544356212846886924> Invalid user's id!"); return
                    __bmode = 'INDIRECT'
                # MOVES     |      acabcbabbba
                except ValueError: 
                    raw_move = copo

        # In case target is not given, current_enemy is used
        if not target:
            # Mobs first. If there's no mob in current_enemy, then randomly pick one
            if cur_MOB == 'n/a':
                target = random.choice(await self.quefe(f"SELECT mob_id FROM environ_mob WHERE region='{cur_PLACE}';", type='all'))[0]
                target_id = target
                __mode = 'PVE'
            else:
                target = cur_MOB
                target_id = target
                __mode = 'PVE'
        
        if not raw_move: await ctx.send(f"<:osit:544356212846886924> Please make your move!"); return


        # TARGET CHECK =========================================

        if __mode == 'PVP': 
            # Check if target has a ava     |      GET TARGET's INFO
            try: t_cur_X, t_cur_Y, t_cur_PLACE = await self.quefe(f"SELECT cur_X, cur_Y, cur_PLACE FROM personal_info WHERE id='{target_id}' AND cur_PLACE='{cur_PLACE}';")
            # E: Invalid target, or target's not in the same region
            except TypeError:
                await ctx.send("<:osit:544356212846886924> Target don't have an ava, or you and the target are not in the same region!"); return

        elif __mode == 'PVE':
            # Check if target is a valid mob       |       GET TARGET's INFO
            try: t_Ax, t_Ay, t_Bx, t_By, t_name = await self.quefe(f"SELECT limit_Ax, limit_Ay, limit_Bx, limit_By, name FROM environ_MOB WHERE mob_id='{target_id}' AND region='{cur_PLACE}';")
            # E: Invalid target, or target's not in the same region
            except TypeError: await ctx.send(f"<:osit:544356212846886924> There is no `{target_id}` around! Perhap you should check your surrounding..."); return

            # Check if the user is in the mob's diversity
            if cur_X < t_Ax or cur_Y < t_Ay or cur_X > t_Bx or cur_Y > t_By:
                print(cur_X, cur_Y)
                print(t_Ax, t_Ay, t_Bx, t_By, t_name)
                await ctx.send(f"<:osit:544356212846886924> **{ctx.message.author.name}**, you can't engage the mob from your current location!"); return


        # WEAPON CHECK ==========================

        # Get weapon info
        try: w_multiplier, w_sta, w_speed = await self.quefe(f"SELECT multiplier, sta, speed FROM pi_inventory WHERE existence='GOOD' AND item_id='{main_weapon}';")
        # E: main_weapon is a item_code (e.g. ar13)
        except TypeError: w_multiplier, w_sta, w_speed = await self.quefe(f"SELECT multiplier, sta, speed FROM pi_inventory WHERE existence='GOOD' AND item_code='{main_weapon}' and user_id='{ctx.author.id}';")

        # STA filter
        if len(raw_move)*w_sta <= STA:
            if w_sta >= 100: await _cursor.execute(f"UPDATE personal_info SET STA=STA-2 WHERE id='{str(ctx.message.author.id)}';")
            else: await _cursor.execute(f"UPDATE personal_info SET STA=STA-1 WHERE id='{str(ctx.message.author.id)}';")
        else: await ctx.send(f"<:osit:544356212846886924> {ctx.author.mention}, out of `STA`!"); return

        # Checking the length of moves
        moves_to_check = await self.quefe(f"SELECT value FROM pi_arts WHERE user_id='{str(ctx.message.author.id)}' AND art_type='sword' AND art_name='chain_attack';")
        if len(raw_move) > moves_to_check[0]:
            await ctx.send(f"<:osit:544356212846886924> You cannot perform a `{len(raw_move)}-chain` attack, **{ctx.message.author.name}**!"); return

        # NOW THE FUN BEGIN =========================================

        counter_move = []

        # Decoding moves, as well as checking the moves. Get the counter_move
        for move in raw_move:
            if move == 'a': counter_move.append('d')
            elif move == 'd': counter_move.append('b')
            elif move == 'b': counter_move.append('a')
            else: await ctx.send(f"<:osit:544356212846886924> Invalid move! (move no. `{raw_move.index(move) + 1}` -> `{move}`)"); return
        
        # PVP use target, with personal_info =============================
        async def PVP():
            # If the duo share the same server, send msg to that server. If not, DM the attacked
            if __bmode == 'DIRECT': inbox = ctx.message
            else: inbox = await target.send(ctx.message.content)

            await inbox.add_reaction('\U00002694')

            # GET TARGET's INFO the second time
            t_name, t_right_hand, t_left_hand, t_combat_HANDLING, t_STA = await self.quefe(f"SELECT name, right_hand, left_hand, combat_HANDLING, STA FROM personal_info WHERE id='{target_id}' AND cur_PLACE='{cur_PLACE}';")

            # Wait for move recognition     |      The more STA consumed, the less time you have to recognize moves. Therefore, if you attack too many times, you'll be more vulnerable
            # RECOG is based on opponent's STA     |      RECOG = oppo's STA / 30
            RECOG = t_STA / 30

            # If the attack is INDIRECT, multiple RECOG by 5
            if __bmode == 'INDIRECT': RECOG = RECOG*5

            def RUM_check(reaction, user):
                return user == target and reaction.message.id == inbox.id and str(reaction.emoji) == '\U00002694'

            if RECOG < 1: RECOG = 1
            try: await self.client.wait_for('reaction_add', check=RUM_check, timeout=RECOG)
            except asyncio.TimeoutError:
                dmgdeal = round(STR*w_multiplier*len(counter_move))
                await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{target_id}';")
                await ctx.send(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{t_name}**"); return


            # Wait for response moves       |        SPEED ('speed') of the sword
            SPEED = w_speed

            def UCc_check(m):
                return m.author == target and m.channel == inbox.channel and m.content.startswith('!')

            try: msg = await self.client.wait_for('message', timeout=SPEED, check=UCc_check)
            except asyncio.TimeoutError:
                dmgdeal = round(STR*w_multiplier*len(counter_move))
                await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{target_id}';")
                await ctx.send(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{target.name}**"); return
            
            # Measuring response moves
            hit_count = 0
            response_content = msg.content[1:]; diff = len(counter_move) - len(response_content)      # Measuring the length of the response
            if diff > 0: response_content += '-'*diff
            for move, response_move in zip(counter_move, response_content):
                if move != response_move: hit_count += 1

            # Conduct dealing dmg   |  Conduct dealing STA dmg
            if hit_count == 0:
                await ctx.send(f"\n:shield: **{target.mention}** ⌫ **{name}**")

                # Recalculate the dmg, since hit_count == 0                
                ## Player's dmg
                if combat_HANDLING == 'both':
                    dmgdeal = round(STR*w_multiplier*len(counter_move))
                elif combat_HANDLING in ['right', 'left']:
                    dmgdeal = round(STR*w_multiplier*len(counter_move))*2
                ## Opponent's def
                if t_combat_HANDLING == 'both':
                    try:
                        tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND (item_code='{t_left_hand}' OR item_id='{t_left_hand}') AND user_id='{target_id}'")
                        dmgredu = 100 - tw_defend
                    except KeyError: dmgredu = 100    
                elif t_combat_HANDLING == 'right':
                    try:
                        tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND (item_code='{t_right_hand}' OR item_id='{t_right_hand}') AND user_id='{target_id}'")
                        dmgredu = 100 - tw_defend*2
                    except KeyError: dmgredu = 100
                elif t_combat_HANDLING == 'left':
                    try:
                        tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND (item_code='{t_left_hand}' OR item_id='{t_left_hand}') AND user_id='{target_id}'")
                        dmgredu = 100 - tw_defend*2
                    except KeyError: dmgredu = 100
                
                # If dmgredu > 0, backfire the attacker. If dmgredu >= 0, all dmg are neutralized
                temp_query = ''
                if dmgredu > 0:
                    temp_query += f"UPDATE personal_info SET STA=STA-{round(dmgdeal / 100 * abs(dmgredu))*tw_multiplier} WHERE id='{str(ctx.message.author.id)}'; "
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
                    tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_left_hand}' AND user_id='{target_id}'")
                    dmgredu = 200 - tw_defend
                elif t_combat_HANDLING == 'right':
                    tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_right_hand}' AND user_id='{target_id}'")
                    dmgredu = 200 - tw_defend*2
                elif t_combat_HANDLING == 'left':
                    tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_left_hand}' AND user_id='{target_id}'")
                    dmgredu = 200 - tw_defend*2

                # If dmgredu > 0, backfire the attacker. If dmgredu >= 0, all dmg are neutralized
                temp_query = ''
                if dmgredu < 0:
                    temp_query += f"UPDATE personal_info SET STA=STA-{round(dmgdeal / 200 * abs(dmgredu))*tw_multiplier} WHERE id='{str(ctx.message.author.id)}'; "
                    dmgredu = 0

                # Get dmgdeal (don't combine, for informing :>)
                dmgdeal = round(dmgdeal / 200 * dmgredu)
                temp_query += f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{target_id}'; "
                await _cursor.execute(temp_query)

                await ctx.send(f":dagger: **{ctx.message.author.name}** has dealt *{dmgdeal} DMG* to **{t_name}**")
        
            await self.ava_scan(ctx.message, 'life_check')

        # PVE use target_id, with environ_mob ======================
        if __mode == 'PVE':
            # ------------ USER PHASE   |   User deal DMG 
            my_dmgdeal = round(STR*w_multiplier*len(counter_move))
            # Inform, of course :>
            await _cursor.execute(f"UPDATE environ_mob SET lp=lp-{my_dmgdeal} WHERE mob_id='{target_id}'; ")
            await ctx.send(f":dagger: **{name}** has dealt *{my_dmgdeal} DMG* to **「`{target_id}` | {t_name}」**!", delete_after=8)

        if __mode == 'PVP':
            await PVP()
        elif __mode == 'PVE':
            await self.PVE(ctx.message, target_id)
        else: print("<<<<< OH SHIET >>>>>>>")

##########################

    @commands.command()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def aim(self, ctx, *args):
        # >Aim <coord_X> <coord_Y> <shots(optional)>      |      >Aim <@user/mob_name> <shots(optional)>       |          >Aim (defaul - shot=1)
        if not await self.ava_scan(ctx.message, type='life_check'): return

        # HANDLING CHECK =====================================
        raw = list(args)
        try:
            note = {'both': '<:right_hand:521197677346553861><:left_hand:521197732162043922>', 'right': '<:right_hand:521197677346553861>', 'left': '<:left_hand:521197732162043922>'}

            await ctx.send(f'{note[raw[0]]} Changed to **{raw[0].upper()} hand** pose')
            await _cursor.execute(f"UPDATE personal_info SET combat_HANDLING='{raw[0].lower()}' WHERE id='{str(ctx.message.author.id)}';"); return
        # E: Pose not given
        except IndexError: await ctx.send(f"<:osit:544356212846886924> **{ctx.message.author.name}**, please make your moves!"); return
        # E: Moves given, not pose
        except KeyError: pass


        # USER's INFO get ===================================================
        __mode = 'PVP'
        shots = 1

        # Get info     |      as well as checking coord
        try: user_id, name, cur_PLACE, cur_X, cur_Y, cur_MOB, main_weapon, combat_HANDLING, STA, LP = await self.quefe(f"SELECT id, name, cur_PLACE, cur_X, cur_Y, cur_MOB, IF(combat_HANDLING IN ('both', 'right'), right_hand, left_hand), combat_HANDLING, STA, LP FROM personal_info WHERE id='{str(ctx.message.author.id)}' AND cur_X>1 AND cur_Y>1;")
        # E: User in PB
        except TypeError: await ctx.send("<:osit:544356212846886924> You can't fight inside **Peace Belt**!"); return


        # INPUT ===============================================================

        # Get weapon's info
        w_round, w_firing_rate, w_sta, w_rmin, w_rmax, w_accu_randomness, w_accu_range, w_stealth, w_aura, w_multiplier, w_tags = await self.quefe(f"SELECT round, firing_rate, sta, range_min, range_max, accuracy_randomness, accuracy_range, stealth, aura, multiplier, tags FROM pi_inventory WHERE existence='GOOD' AND item_id='{main_weapon}';")
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
                target = ctx.message.mentions[0]; target_id = str(target.id)
                __bmode = 'DIRECT'
                # Get shots (if available and possible)
                try: 
                    shots = int(raw[1])
                    if _style == 'MAGIC':
                        try: amount = int(raw[2])
                        except IndexError: amount = 1
                except IndexError: amount = 1
                except TypeError: amount = 1

            # Coord, shots provided     (if raw[0] is a mob_name, raise TypeError       |      if raw[0] provided as <shots>, but raw[1] is not provided, raise IndexError)
            elif len(str(int(raw[0]))) <= 5 and len(raw[1]) <= 5 and _style == 'PHYSIC':
                print("OKAI HERE")
                X = int(raw[0])/1000; Y = int(raw[1])/1000

                # Get USER from COORD. If there are many users, randomly pick one.
                try: 
                    target_id = random.choice(await self.quefe(f"SELECT id FROM personal_info WHERE cur_X={X} AND cur_Y={Y} AND cur_PLACE='{cur_PLACE}';", type='all'))
                    target_id = target_id[0]
                    target = await self.client.get_user(int(target_id))
                    __bmode = 'DIRECT'
                    if not ctx.message.server.get_member(target_id): __bmode = 'INDIRECT'
                    if not target: await ctx.send(f"There's noone at **x:`{X:.3f}` y:`{Y:.3f}`** in {cur_PLACE}!"); return
                # E: Query's empty, since noone's at the given coord
                except IndexError: await ctx.send(f"There's noone at **x:`{X:.3f}` y:`{Y:.3f}`** in {cur_PLACE}!"); return
                
                # Get shots (if available and possible)
                try: 
                    shots = int(raw[2])
                except IndexError: pass
                except TypeError: pass

            # Shots AND amount given.     |      Or coords, shots (and amount) given                     --------> MAGIC
            elif _style == 'MAGIC':
                print('YO HERE')
                # Coords, shots (and amount)
                try:
                    X = int(raw[0])/1000; Y = int(raw[1])/1000; shots = int(raw[2])

                    # Get USER from COORD. If there are many users, randomly pick one.
                    try: 
                        target_id = random.choice(await self.quefe(f"SELECT id FROM personal_info WHERE cur_X={X} AND cur_Y={Y} AND cur_PLACE='{cur_PLACE}';", type='all'))
                        target_id = target_id[0]
                        target = await self.client.get_user(int(target_id))
                        __bmode = 'DIRECT'
                        if not ctx.message.server.get_member(target_id): __bmode = 'INDIRECT'
                        if not target: await ctx.send(f"There's noone at **x:`{X:.3f}` y:`{Y:.3f}`** in {cur_PLACE}!"); return
                    # E: Query's empty, since noone's at the given coord
                    except (IndexError, TypeError): await ctx.send(f"There's noone at **x:`{X:.3f}` y:`{Y:.3f}`** in {cur_PLACE}!"); return

                    try: amount = int(raw[3])
                    except (IndexError, TypeError): amount = 1
                # Shots AND amount
                except (IndexError, TypeError):
                    shots = int(raw[0]); amount = int(raw[1])
                    raise IndexError

            else: await ctx.send("<:osit:544356212846886924> Please use 5-digit or lower coordinates!")       

        # Mob_id, shots provided
        except (TypeError, ValueError):
            print("HEREEE")
            # If there's no current_enemy   |   # If there is, and the target is the current_enemy
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
                await ctx.send(f"<:osit:544356212846886924> Please finish your current fight with `{cur_MOB}`!"); return

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
            # Check if target has a ava     |      GET TARGET's INFO
            try: t_cur_X, t_cur_Y, t_cur_PLACE, t_combat_HANDLING, t_right_hand, t_left_hand = await self.quefe(f"SELECT cur_X, cur_Y, cur_PLACE, combat_HANDLING, right_hand, left_hand FROM personal_info WHERE id='{target_id}' AND cur_PLACE='{cur_PLACE}';")
            # E: Invalid target, or target's not in the same region
            except TypeError:
                await ctx.send("<:osit:544356212846886924> Target don't have an ava, or you and the target are not in the same region!"); return

        elif __mode == 'PVE':
            # Check if target is a valid mob       |       GET TARGET's INFO
            try: t_Ax, t_Ay, t_Bx, t_By, t_name = await self.quefe(f"SELECT limit_Ax, limit_Ay, limit_Bx, limit_By, name FROM environ_MOB WHERE mob_id='{target_id}' AND region='{cur_PLACE}';")
            # E: Invalid target, or target's not in the same region
            except TypeError: await ctx.send(f"<:osit:544356212846886924> There is no `{target_id}` around! Perhap you should check your surrounding..."); return

            # Check if the user is in the mob's diversity
            if cur_X < t_Ax or cur_Y < t_Ay or cur_X > t_Bx or cur_Y > t_By:
                print(t_Ax, t_Ay, t_Bx, t_By, t_name)
                await ctx.send(f"<:osit:544356212846886924> **{ctx.message.author.name}**, you can't engage the mob from your current location!"); return


        # WEAPON CHECK ===========================================================

        # Distance get/check
        if __mode == 'PVP': 
            distance = await self.distance_tools(cur_X, cur_Y, t_cur_X, t_cur_Y)
            if distance > w_rmax or distance < w_rmin: await ctx.send(f"<:osit:544356212846886924> **{ctx.message.author.name}**, the target is out of your weapon's range!"); return
        elif __mode == 'PVE':
            distance = 1                    # There is NO distance in a PVE battle, therefore the accuracy will always be at its lowest

        # AMMUNITION
        if shots > w_firing_rate: await ctx.send(f"<:osit:544356212846886924> **{ctx.message.author.name}**, your weapon cannot perform `{shots}` shots in a row!"); return
        
        # Get ammu's info
        try:
            a_name, a_tags, a_speed, a_rlquery, a_dmg, a_quantity = await self.quefe(f"SELECT name, tags, speed, reload_query, dmg, quantity FROM pi_inventory WHERE existence='GOOD' AND item_code='{w_round}' AND user_id='{user_id}';")
            a_tags = a_tags.split(' - ')
        # E: Ammu not found --> Unpack error
        except TypeError: 
            if w_round not in ['am5', 'am6'] :
                a_name = await self.quefe(f"SELECT name FROM model_item WHERE item_code='{w_round}';")
                await ctx.send(f"<:osit:544356212846886924> {ctx.message.author.mention}, OUT OF `{w_round} | {a_name}`!"); return
            else:
                a_name, a_tags, a_speed, a_rlquery, a_dmg = await self.quefe(f"SELECT name, tags, speed, reload_query, dmg FROM model_item WHERE item_code='{w_round}';")


        # Check shots VS quantity of the ammu_type. RELOAD.
        # MAGIC
        if w_round == 'am5':                    # LP -------------------- If kamikaze, halt them
            if LP <= shots*amount:
                await ctx.send(f"<:osit:544356212846886924> **{ctx.message.author.name}**, please don't kill yourself..."); return
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
                await _cursor.execute(f"UPDATE pi_inventory SET existence='BAD' WHERE item_code='{w_round}' AND user_id='{user_id}';")
            else:
                a_rlquery = a_rlquery.replace('quantity_here', str(shots)).replace('user_id_here', user_id)
                await _cursor.execute(a_rlquery)

        # Filtering shots bases on STA remaining. If using physical, STA's decreased        |          No filtering, while using magic. STA's NOT decreased (for using weapon).
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
            await ctx.send(f":interrobang: {ctx.message.author.mention}, you shot a lot but hit nothing...")
            if __bmode == 'INDIRECT': await target.send(f":sos: **Someone** is trying to hurt you, {target.mention}!")
            return

        #dmgdeal = ammu['dmg']*shots

        # PVP use target, with ava_dict =================================
        async def PVP():
            # PVE() already has a deletion. Please don't put this else where
            try: await ctx.message.delete()
            except discordErrors.Forbidden: pass

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
                inbox = await ctx.send(f""":sos: **{shooter}** is trying to *{verb}* you, {target.mention}!```css
{field}```""")
            else: 
                inbox = await target.send(f""":sos: **{shooter}** is trying to *{verb}* you, {target.mention}!```css
{field}```""")

            # MAGIC
            if _style == 'MAGIC':
                # Generate model moves
                model_moves = field.replace('⠀', '0').replace('·', '1')

                # Wait for response moves       |        SPEED ('speed') of the bullet aka. <ammu>
                def UCc_check(m):
                    return m.author == target and m.channel == inbox.channel and m.content == f"!{model_moves}"
                
                SPEED = a_speed
                # If the attack is INDIRECT, multiple RECOG by 5
                if __bmode == 'INDIRECT': SPEED = SPEED*5
                try: msg = await self.client.wait_for('message', timeout=SPEED, check=UCc_check)
                except asyncio.TimeoutError:
                    dmgdeal = a_dmg*shots*amount

                    # AURA comes in
                    aura_dict = {'FLAME': 'au_FLAME', 'ICE': 'au_ICE', 'DARK': 'au_DARK', 'HOLY': 'au_HOLY'}
                    aura = await self.quefe(f"SELECT {aura_dict[w_aura]} FROM personal_info WHERE id='{user_id}';")
                    t_aura = await self.quefe(f"SELECT {aura_dict[w_aura]} FROM personal_info WHERE id='{target_id}';")
                    # Re-calc dmgdeal
                    try: dmgdeal = int(dmgdeal*t_aura[0]/aura[0])
                    except ZeroDivisionError: dmgdeal = int(dmgdeal*t_aura)

                    await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{target_id}';")
                    await ctx.send(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{t_name}**")
                    if __bmode == 'INDIRECT': await target.send(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{t_name}**")
                    return
                else:
                    await ctx.send(f"\n--------------------\n:shield: **{target.mention}** has successfully *neutralized* all **{name}**'s spells!")
                    if __bmode == 'INDIRECT': await target.send(f"\n--------------------\n:shield: **{target.mention}** has successfully *neutralized* all **{name}**'s spells!")
                    return
            
                await self.ava_scan(ctx.message, 'life_check')

            # PHYSICAL
            else:
                # Wait for response moves       |        SPEED ('speed') of the bullet aka. <ammu>
                def UC_check(m):
                    return m.author == target and m.channel == inbox.channel and m.content.startswith('!')
                
                SPEED = a_speed
                # If the attack is INDIRECT, multiple RECOG by 5
                if __bmode == 'INDIRECT': SPEED = SPEED*5
                try: msg = await self.client.wait_for('message', timeout=SPEED, check=UC_check)
                except asyncio.TimeoutError:
                    dmgdeal = a_dmg*shots
                    await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{target_id}';")
                    await ctx.send(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{t_name}**")
                    if __bmode == 'INDIRECT': await target.send(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{t_name}**")
                    return

                # Measuring response moves
                hit_count = 0
                response_content = msg.content[1:]              # Measuring the length of the response
                # Fixing the length of response_content
                response_content = response_content + 'o'*(len(counter_shot) - len(response_content))

                # HIT COUNTER
                for shot, resp in zip(counter_shot, response_content):
                    if shot != resp: hit_count += 1

                # Conduct dealing dmg   |  Conduct dealing STA dmg
                dmgdeal = a_dmg*hit_count
                if hit_count == 0:
                    await ctx.send(f"\n:shield: **{target.mention}** ⌫ **{name}**")
                    if __bmode == 'INDIRECT': await target.send(f"\n:shield: **{target.mention}** ⌫ **{name}**")

                    # Recalculate the dmg, since hit_count == 0                
                    ## Player's dmg
                    dmgdeal = round(a_dmg*len(counter_shot))
                    ## Opponent's def
                    if t_combat_HANDLING == 'both':
                        tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_left_hand}' AND user_id='{target_id}'")
                        dmgredu = 100 - tw_defend
                    elif t_combat_HANDLING == 'right':
                        tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_right_hand}' AND user_id='{target_id}'")
                        dmgredu = 100 - tw_defend*2
                    elif t_combat_HANDLING == 'left':
                        tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_left_hand}' AND user_id='{target_id}'")
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
                            tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_left_hand}' AND user_id='{target_id}'")
                            dmgredu = 200 - tw_defend
                        except KeyError: dmgredu = 200
                    elif t_combat_HANDLING == 'right':
                        try:
                            tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_left_hand}' AND user_id='{target_id}'")
                            dmgredu = 200 - tw_defend*2
                        except KeyError: dmgredu = 200
                    elif t_combat_HANDLING == 'left':
                        try:
                            tw_defend, tw_multiplier = await self.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_left_hand}' AND user_id='{target_id}'")
                            dmgredu = 200 - tw_defend*2
                        except KeyError: dmgredu = 200

                    # If dmgredu > 0, backfire the attacker. If dmgredu >= 0, all dmg are neutralized
                    if dmgredu < 0:
                        await _cursor.execute(f"UPDATE personal_info SET STA=STA-{round(dmgdeal / 200 * abs(dmgredu))*tw_multiplier} WHERE id='{user_id}';")
                        dmgredu = 0

                    # Get dmgdeal, for informing :>
                    dmgdeal = round(dmgdeal / 200 * dmgredu)
                    await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{target_id}';")

                    await ctx.send(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{t_name}**")
                    if __bmode == 'INDIRECT': await target.send(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{t_name}**")
            
                await self.ava_scan(ctx.message, 'life_check')

        # PVE use target_id, with environ_mob ============================
        async def first_PVE():
            if _style == 'PHYSIC':
                # ------------ USER PHASE   |   User deal DMG 
                my_dmgdeal = round(a_dmg*len(shots))
                # Inform, of course :>
                await _cursor.execute(f"UPDATE environ_mob SET lp=lp-{my_dmgdeal} WHERE mob_id='{target_id}'; ")
                await ctx.send(f":dagger: **{name}** ⋙ *{my_dmgdeal} DMG* ⋙ **「`{target_id}` | {t_name}」**!")
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
                await ctx.send(f":dagger: **{name}** ⋙ *{dmgdeal} DMG* ⋙ **「`{target_id}` | {t_name}」**!")


        if __mode == 'PVP':
            await PVP()
        elif __mode == 'PVE':
            await first_PVE()
            await self.PVE(ctx.message, target_id)
        else: print("<<<<< OH SHIET >>>>>>>")

##########################

    # This function handles the Mob phase
    # Melee PVE     |      Start the mob phase.
    async def PVE(self, MSG, target_id):
        # Lock-on check. If 'n/a', proceed PVE. If the mob has already locked on other, return.
        try:
            t_name, t_speed, t_str, t_chain = await self.quefe(f"SELECT name, speed, str, chain FROM environ_mob WHERE mob_id='{target_id}' AND lockon='n/a';")
            # Set lock-on, as the target is user_id
            await _cursor.execute(f"UPDATE environ_mob SET lockon='{MSG.author.id}' WHERE mob_id='{target_id}';")
        except TypeError: return

        name, evo, STA, MAX_STA, user_id, cur_PLACE, cur_X, cur_Y, cur_MOB, combat_HANDLING, right_hand, left_hand = await self.quefe(f"SELECT name, evo, STA, MAX_STA, id, cur_PLACE, cur_X, cur_Y, cur_MOB, combat_HANDLING, right_hand, left_hand FROM personal_info WHERE id='{MSG.author.id}';")
        message_obj = False
        try: await MSG.delete()
        except discordErrors.Forbidden: pass

        async def conclusing():
            # REFRESHING ===========================================
            name, LP, STA, user_id, cur_PLACE = await self.quefe(f"SELECT name, LP, STA, id, cur_PLACE FROM personal_info WHERE id='{MSG.author.id}';")
            #name, LP, STA, MAX_STA, user_id, cur_PLACE, cur_X, cur_Y, cur_MOB, combat_HANDLING, right_hand, left_hand = await self.quefe(f"SELECT name, LP, STA, MAX_STA, id, cur_PLACE, cur_X, cur_Y, cur_MOB, combat_HANDLING, right_hand, left_hand FROM personal_info WHERE id='{MSG.author.id}';")
            t_lp, t_name = await self.quefe(f"SELECT lp, name FROM environ_mob WHERE mob_id='{target_id}';")
            #t_lp, t_name, t_speed, t_str, t_chain = await self.quefe(f"SELECT lp, name, speed, str, chain FROM environ_mob WHERE mob_id='{target_id}';")


            if not await self.ava_scan(MSG, type='life_check'):
                return False
            if t_lp <= 0:
                await MSG.channel.send(f"<:tumbstone:544353849264177172> **{t_name}** is dead.")
                
                # Add one to the collection
                type = await vanishing()

                # If query effect zero row
                if await _cursor.execute(f"UPDATE pi_mobs_collection SET {type}={type}+1 WHERE user_id='{user_id}' AND region='{cur_PLACE}';") == 0:
                    await _cursor.execute(f"INSERT INTO pi_mobs_collection (user_id, region, {type}) VALUES ('{user_id}', '{cur_PLACE}', 1);")

                # Erase the current_enemy lock on off the target_id

                await _cursor.execute(f"UPDATE personal_info SET cur_MOB='n/a' WHERE id='{user_id}';")
                return False 

            msg = f"╔═══════════\n╟:heartpulse:`{LP}` :muscle:`{STA}` ⠀⠀ |〖**{name}**〗\n╟:heartpulse:`{t_lp}`⠀⠀⠀⠀⠀⠀⠀⠀|〖**{t_name}**〗\n╚═══════════"
            return msg

        async def vanishing():
            # Looting
            mob_code, rewards, reward_query, region, t_Ax, t_Ay, t_Bx, t_By = await self.quefe(f"SELECT mob_code, rewards, reward_query, region, limit_Ax, limit_Ay, limit_Bx, limit_By FROM environ_mob WHERE mob_id='{target_id}';")
            await _cursor.execute(reward_query.replace('user_id_here', str(MSG.author.id)))

            await MSG.channel.send(f"<:chest:507096413411213312> Congrats **{MSG.author.mention}**, you've received **{rewards.replace(' | ', '** and **')}** from **「`{target_id}` | {t_name}」**!")
            
            # Get the <mob> prototype
            name, branch, lp, strr, chain, speed, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY, t_evo = await self.quefe(f"SELECT name, branch, lp, str, chain, speed, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY, evo FROM model_mob WHERE mob_code='{mob_code}';")
            rewards = rewards.split(' | ')

            # Generating rewards
            status = []; objecto = []; bingo_list = []
            for reward in rewards:
                stuff = reward.split(' - ')
                if random.choice(range(int(stuff[2]))) == 0:
                    if stuff[0] == 'money': bingo_list.append(f"<:36pxGold:548661444133126185>{stuff[1]}")

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
            # Merit calc
            merrire = t_evo - evo + 1
            if merrire < 0: merrire = 0
            else:
                if target_id.startswith('boss'): merrire = int(merrire/2*10)
            stata = f"""UPDATE personal_info SET {', '.join(status)}, merrit=merrit+{merrire} WHERE id="user_id_here"; """
            rewards_query = f"{stata} {' '.join(objecto)}"

            # Remove the old mob from DB
            await _cursor.execute(f"DELETE FROM environ_mob WHERE mob_id='{target_id}';")

            # Insert the mob to DB
            await _cursor.execute(f"""INSERT INTO environ_mob VALUES (0, 'mob', '{mob_code}', "{name}", '{branch}', {lp}, {strr}, {chain}, {speed}, {au_FLAME}, {au_ICE}, {au_DARK}, {au_HOLY}, '{' | '.join(bingo_list)}', '{rewards_query}', '{region}', {t_Ax}, {t_Ay}, {t_Bx}, {t_By}, 'n/a');""")
            counter_get = await self.quefe("SELECT MAX(id_counter) FROM environ_mob")
            await _cursor.execute(f"UPDATE environ_mob SET mob_id='mob.{counter_get[0]}' WHERE id_counter={counter_get[0]};")

            return branch

        # ------------ MOB PHASE    |   Mobs attack, user defend
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

            decl_msg = await MSG.channel.send(f":crossed_swords: **{t_name}** ⋙ `{' '.join(mmove)}` ⋙ {MSG.author.mention} ")

            # Wait for response moves
            def UCc_check(m):
                return m.author == MSG.author and m.channel == MSG.channel and m.content.startswith('!')
            
            try:
                msg = await self.client.wait_for('message', timeout=t_speed, check=UCc_check)            #timeout=10
                await decl_msg.delete()
            except asyncio.TimeoutError:
                dmgdeal = round(dmg*len(mmove))
                await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                pack_1 = f":dagger: **「`{target_id}` | {t_name}」** ⋙ ***{dmgdeal} DMG*** ⋙ {MSG.author.mention}!"
                pack_2 = await conclusing()
                if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                else: msg_pack = False
                if message_obj: await message_obj.delete()
                await decl_msg.delete()
                return msg_pack

            try: await msg.delete()
            except: pass

            # Fleeing method    |     Success rate base on user's current STA
            if msg.content == '!flee':
                if STA <= 0: rate = MAX_STA//1 + 1
                else: rate = MAX_STA//STA + 1
                # Succesfully --> End battling session
                if random.choice(range(int(rate))) == 0:
                    await MSG.channel.send(f"{MSG.author.mention}, you've successfully escape from the mob!")
                    # Erase the current_enemy lock on off the target_id
                    await _cursor.execute(f"UPDATE personal_info SET cur_MOB='n/a' WHERE id='{user_id}'; UPDATE environ_mob SET lockon='n/a' WHERE mob_id='{target_id}'")
                    return False
                # Fail ---> Continue, with the consequences
                else:
                    dmgdeal = round(dmg*len(mmove))*2
                    await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                    pack_1 = f"\n:dagger::dagger: As **{name}** failed to flee, **「`{target_id}` | {t_name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                    else: msg_pack = False
                    if message_obj: await message_obj.delete()
                    return msg_pack
            # Switching method      |      Switching_range=5m
            elif msg.content.startswith('!switch'):
                # E: No switchee found
                try: switchee = msg.mentions[0]
                except IndexError: 
                    dmgdeal = round(dmg*len(mmove))*2
                    await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                    pack_1 = f"\n:dagger::dagger: As **{name}** failed to switch, **「`{target_id}` | {t_name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                    else: msg_pack = False
                    if message_obj: await message_obj.delete()
                    return msg_pack
                # E: Different region
                try:
                    sw_cur_PLACE, sw_cur_X, sw_cur_Y = await self.quefe(f"SELECT cur_PLACE, cur_X, cur_Y FROM personal_info WHERE id='{switchee.id}'; ")
                    if cur_PLACE != sw_cur_PLACE: 
                        await MSG.channel.send(f"<:osit:544356212846886924> {switchee.mention} and {MSG.author.mention}, you have to be in the same region!")
                        dmgdeal = round(dmg*len(mmove))*2
                        await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                        pack_1 = f"\n:dagger::dagger: As **{name}** failed to switch, **「`{target_id}` | {t_name}」** has dealt a critical DMG of *{dmgdeal}*!"
                        pack_2 = await conclusing()
                        if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                        else: msg_pack = False                       
                        if message_obj: await message_obj.delete()
                        return msg_pack                        
                ## E: Switchee doesn't have ava
                except TypeError:
                    await MSG.channel.send(f"<:osit:544356212846886924> User **{switchee.name}** doesn't have an *ava*!")
                    dmgdeal = round(dmg*len(mmove))*2
                    await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                    pack_1 = f"\n:dagger::dagger: As **{name}** failed to switch, **「`{target_id}` | {t_name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                    else: msg_pack = False                       
                    if message_obj: await message_obj.delete()
                    return msg_pack                                            
                # E: Out of switching_range
                if await self.distance_tools(cur_X, cur_Y, sw_cur_X, sw_cur_Y) > 5:
                    await self.client(f"<:osit:544356212846886924> {switchee.mention} and {MSG.author.mention}, you can only switch within *5 metres*!")
                    dmgdeal = round(dmg*len(mmove))*2
                    await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                    pack_1 = f"\n:dagger::dagger: As **{name}** failed to switch, **「`{target_id}` | {t_name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                    else: msg_pack = False                     
                    if message_obj: await message_obj.delete()
                    return msg_pack

                # Wait for response
                def UC_check2(m):
                    return m.author == switchee and m.channel == MSG.channel and m.content.startswith('!')

                try: switch_resp = await self.client.wait_for('message', timeout=5, check=UC_check2)
                # E: No response
                except asyncio.TimeoutError:
                    dmgdeal = round(dmg*len(mmove))*2
                    await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                    pack_1 = f"\n:dagger::dagger: As **{name}** failed to switch, **「`{target_id}` | {t_name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                    else: msg_pack = False                     
                    if message_obj: await message_obj.delete()
                    return msg_pack                        
                # E: Wrong user
                if MSG.author not in switch_resp.mentions:
                    dmgdeal = round(dmg*len(mmove))*2
                    await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                    pack_1 = f"\n:dagger::dagger: As **{name}** failed to switch, **「`{target_id}` | {t_name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                    else: msg_pack = False                    
                    if message_obj: await message_obj.delete()
                    return msg_pack                                
                
                # Proceed duo-teleportation
                await self.tele_procedure(cur_PLACE, str(switchee.id), cur_X, cur_Y)
                await self.tele_procedure(cur_PLACE, user_id, sw_cur_X, sw_cur_Y)
                # End the switcher PVE-session
                ## Remove the current_enemy lock-on of the switcher
                await _cursor.execute(f"UPDATE personal_info SET cur_MOB='n/a' WHERE id='{user_id}'; ")
                # Proceed PVE-session re-focus
                await MSG.channel.send(f":arrows_counterclockwise: {MSG.author.mention} and {switchee.mention}, **SWITCH!!**")
                return [switch_resp, target_id]

                

            # Measuring response moves
            hit_count = 0
            response_content = msg.content[1:]; diff = len(counter_mmove) - len(response_content)      # Measuring the length of the response
            if diff > 0: response_content += '-'*diff                                              # Balancing the length (if needed)
            for move, response_move in zip(counter_mmove, response_content):
                if move != response_move: hit_count += 1
            print(f"HIT COUNT: {hit_count} ----- {response_content} ------ {counter_mmove}")

            # Conduct dealing dmg   |  Conduct dealing STA dmg
            if hit_count == 0:
                dmgdeal = t_str*len(counter_mmove)

                if STA > 0:
                    # Deal
                    if combat_HANDLING == 'both':
                        w_defend = await self.quefe(f"SELECT defend FROM pi_inventory WHERE existence='GOOD' AND (item_id='{left_hand}' OR item_code='{left_hand}') AND user_id='{user_id}'"); w_defend = w_defend[0]
                        dmgredu = 100 - w_defend
                    elif combat_HANDLING == 'right':
                        w_defend = await self.quefe(f"SELECT defend FROM pi_inventory WHERE existence='GOOD' AND (item_id='{right_hand}' OR item_code='{right_hand}') AND user_id='{user_id}'"); w_defend = w_defend[0]
                        dmgredu = 100 - w_defend*2
                    elif combat_HANDLING == 'left':
                        w_defend = await self.quefe(f"SELECT defend FROM pi_inventory WHERE existence='GOOD' AND (item_id='{left_hand}' OR item_code='{left_hand}') AND user_id='{user_id}'"); w_defend = w_defend[0]
                        dmgredu = 100 - w_defend*2
                    # Check STA
                    tem = round(dmgdeal / 100 * dmgredu)
                    if tem > STA:
                        await _cursor.execute(f"UPDATE personal_info SET STA=0 WHERE id='{user_id}';")
                    else: await _cursor.execute(f"UPDATE personal_info SET STA=STA-{tem} WHERE id='{user_id}';")
                
                # Inform
                pack_1 = f"\n:shield: {MSG.author.mention} ⌫ **「`{target_id}`|{t_name}」**"
                pack_2 = await conclusing()
                if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                else: msg_pack = False
                if message_obj: await message_obj.delete()
                return msg_pack

            else:
                dmgdeal = t_str*hit_count 

                # Deal
                if combat_HANDLING == 'both':
                    w_defend = await self.quefe(f"SELECT defend FROM pi_inventory WHERE existence='GOOD' AND (item_id='{left_hand}' OR item_code='{left_hand}') AND user_id='{user_id}'"); w_defend = w_defend[0]
                    dmgredu = 200 - w_defend
                elif combat_HANDLING == 'right':
                    w_defend = await self.quefe(f"SELECT defend FROM pi_inventory WHERE existence='GOOD' AND (item_id='{right_hand}' OR item_code='{right_hand}') AND user_id='{user_id}'"); w_defend = w_defend[0]
                    dmgredu = 200 - w_defend
                elif combat_HANDLING == 'left':
                    w_defend = await self.quefe(f"SELECT defend FROM pi_inventory WHERE existence='GOOD' AND (item_id='{left_hand}' OR item_code='{left_hand}') AND user_id='{user_id}'"); w_defend = w_defend[0]
                    dmgredu = 200 - w_defend

                # Get dmgdeal for informing :>
                dmgdeal = round(dmgdeal / 200 * dmgredu)
                await _cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}';")

                # Inform
                pack_1 = f"\n:dagger: **「`{target_id}` | {t_name}」** ⋙ *{dmgdeal} DMG* ⋙ **{MSG.author.mention}**"
                pack_2 = await conclusing()
                if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                else: msg_pack = False
                if message_obj: await message_obj.delete()
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

#    @commands.command(aliases=['>cast'])
#    @commands.cooldown(1, 60, type=BucketType.user)
#    async def avacast(self, ctx, *args):

##########################




# ============= TACTICAL ==============
    @commands.command(aliases=['scan', 'rad'])
    @commands.cooldown(1, 30, type=BucketType.user)
    async def radar(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        cur_X, cur_Y = await self.quefe(f"SELECT cur_X, cur_Y FROM personal_info WHERE id='{str(ctx.message.author.id)}';")
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

        if not coords_list: await ctx.send(f":satellite: No sign of life in `{xrange*1000}m x {yrange*1000}m` square radius around us..."); return

        img = Image.new('RGB', (100, 100))
        cvs = ImageDraw.Draw(img)
        for coords in coords_list:
            real_X = (cur_X - coords[0])*1000
            if real_X >= 0: real_X = 50 - real_X
            else: real_X = 50 + real_X
            real_Y = (cur_Y - coords[1])*1000
            if real_Y >= 0: real_Y = 50 - real_Y
            else: real_Y = 50 + real_Y

            cvs.point([(real_X, real_Y), (real_X+1, real_Y), (real_X, real_Y+1), (real_X+1, real_Y+1)], fill=(156, 230, 133, 0))

        output_buffer = BytesIO()
        img.save(output_buffer, 'png')
        output_buffer.seek(0)

        f = discord.File(fp=output_buffer, filename='radar.png')
        #await ctx.send(file=)

        def makeembed(top, least, pages, currentpage):
            line = ""; swi = True

            for coords in coords_list[top:least]:
                if swi: line = line + f"\n╠ **`{coords[0]:.3f}`** · **`{coords[1]:.3f}`**"; swi = False
                else: line = line + f"⠀⠀⠀╠ **`{coords[0]:.3f}`** · **`{coords[1]:.3f}`**"; swi = True

            reembed = discord.Embed(title = f":satellite: [{xrange*2*1000}m x {yrange*2*1000}m] square radius, with user as the center", colour = discord.Colour(0x011C3A), description=line)
            reembed.set_footer(text=f"{len(coords_list)} detected | List {currentpage} of {pages}")
            reembed.set_thumbnail(url="attachment://radar.png")
            return reembed
            #else:
            #    await ctx.send("*Nothing but dust here...*")
        
        async def attachreaction(msg):
            await msg.add_reaction("\U000023ee")    #Top-left
            await msg.add_reaction("\U00002b05")    #Left
            await msg.add_reaction("\U000027a1")    #Right
            await msg.add_reaction("\U000023ed")    #Top-right

        pages = len(coords_list)//10
        if len(coords_list)%10 != 0: pages += 1
        currentpage = 1
        cursor = 0

        emli = []
        for curp in range(pages):
            myembed = makeembed(currentpage*10-10, currentpage*10, pages, currentpage)
            emli.append(myembed)
            currentpage += 1

        msg = await ctx.send(file=f, embed=emli[cursor], delete_after=30)
        if pages > 1: await attachreaction(msg)
        else: return

        def UM_check(reaction, user):
            return user.id == ctx.author.id and reaction.message.id == msg.id

        while True:
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=20, check=UM_check)
                if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                    cursor += 1
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U00002b05" and cursor > 0:
                    cursor -= 1
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U000023ee" and cursor != 0:
                    cursor = 0
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                    cursor = pages - 1
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
            except asyncio.TimeoutError: 
                return

    @commands.command(aliases=['tele'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def teleport(self, ctx, *args):
        cur_PLACE, cur_X, cur_Y, stats = await self.quefe(f"SELECT cur_PLACE, cur_X, cur_Y, stats FROM personal_info WHERE id='{ctx.author.id}';")

        if stats == 'DEAD': await self.ava_scan(ctx.message, type='life_check')

        # COORD
        if not args:
            if cur_PLACE.startswith('region.'): r_name = await self.quefe(f"SELECT name FROM environ WHERE environ_code='{cur_PLACE}';")
            else: r_name = await self.quefe(f"SELECT name FROM pi_land WHERE land_code='{cur_PLACE}';")
            await ctx.send(f":map: **`{cur_X:.3f}`** · **`{cur_Y:.3f}`** · `{cur_PLACE}`|**{r_name[0]}** · {ctx.message.author.mention}", delete_after=5); return

        try:
            x = int(args[0])/1000; y = int(args[1])/1000

            # Region INFO
            if cur_PLACE.startswith('region.'): r_name, border_X, border_Y = await self.quefe(f"SELECT name, border_X, border_Y FROM environ WHERE environ_code='{cur_PLACE}'")
            # Land INFO
            else:
                try: r_name, border_X, border_Y = await self.quefe(f"SELECT name, border_X, border_Y FROM pi_land WHERE land_code='{cur_PLACE}'")
                except TypeError: await ctx.send(f"**{cur_PLACE}**... There is no such place here, perhap it's from another era?"); return

            if len(args[0]) <= 5 and len(args[1]) <= 5:
                if x > border_X: x = border_X
                if y > border_Y: y = border_Y
                if x < 0: x = -1
                if y < 0: y = -1
                # Check if <distance> is provided
                try:
                    distance = int(args[2])
                    prior_x = x; prior_y = y
                    x, y = await self.distance_tools(cur_X, cur_Y, x, y, distance=distance, type='d-c')
                    # Coord check
                    if x > border_X: x = border_X
                    if y > border_Y: y = border_Y
                    if x < 0: x = 0
                    if y < 0: y = 0
                except (IndexError, ValueError): pass
                
                # Procede teleportation
                await self.tele_procedure(cur_PLACE, str(ctx.author.id), x, y)

                # Informmmm :>
                try: await ctx.send(f"<:dual_cyan_arrow:543662534612353044>`{distance}m`<:dual_cyan_arrow:543662534612353044> toward **`{prior_x:.3f}`** · **`{prior_y:.3f}`**\n:map: Now you're at **`{x:.3f}`** · **`{y:.3f}`** · `{cur_PLACE}`|**{r_name}**!", delete_after=5)
                except NameError: await ctx.send(f":map: [{cur_X:.3f}, {cur_Y:.3f}] <:dual_cyan_arrow:543662534612353044> **`{x:.3f}`** · **`{y:.3f}`** · `{cur_PLACE}`|**{r_name}**!", delete_after=5)
            else: await ctx.send(f"<:osit:544356212846886924> Please use 5-digit coordinates!"); return
        except IndexError: await ctx.send(f"<:osit:544356212846886924> Out of map's range!"); return

        # PLACE
        except (KeyError, ValueError):
            if cur_PLACE == args[0]: await ctx.send("<:osit:544356212846886924> You're already there :|")

            # Region INFO
            if args[0].startswith('region.'): r_name, border_X, border_Y = await self.quefe(f"SELECT name, border_X, border_Y FROM environ WHERE environ_code='{args[0]}'")
            # Land INFO
            else:
                try: r_name, border_X, border_Y = await self.quefe(f"SELECT name, border_X, border_Y FROM pi_land WHERE land_code='{args[0]}'")
                except TypeError: await ctx.send(f"**{args[0]}**... There is no such place here, perhap it's from another era?"); return

            if cur_X <= 1 and cur_Y <=1:
                await _cursor.execute(f"UPDATE personal_info SET cur_PLACE='{args[0]}' WHERE id='{ctx.author.id}';")
                await ctx.send(f":round_pushpin: Successfully move to `{args[0]}`|**{r_name}**!", delete_after=5)
            else: await ctx.send(f"<:osit:544356212846886924> You can only travel between regions inside **Peace Belt**!"); return

    @commands.command(aliases=['md'])
    async def measure_distance(self, ctx, *args):
        if not await self.ava_scan(ctx.message, type='life_check'): return

        cur_X, cur_Y = await self.quefe(f"SELECT cur_X, cur_Y FROM personal_info WHERE id='{str(ctx.message.author.id)}';")

        try:
            distance = await self.distance_tools(cur_X, cur_Y, int(args[0])/1000, int(args[1])/1000)
            await ctx.send(f":straight_ruler\n::triangular_ruler: Result: **`{distance}m`**")
        except IndexError: pass

    @commands.command(aliases=['map'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def regions(self, ctx, *args):
        cur_PLACE = await self.quefe(f"SELECT cur_PLACE FROM personal_info WHERE id='{ctx.author.id}';")
        regions = await self.quefe(f"SELECT environ_code, name, description, illulink, border_X, border_Y, biome, land_slot, cuisine, goods FROM environ ORDER BY ord ASC;", type='all')

        async def makeembed(curp, pages, currentpage):
            region = regions[curp]; line = ''; swi = 0
            players = await _cursor.execute(f"SELECT * FROM personal_info WHERE cur_PLACE='{region[0]}';")
            mobs = await _cursor.execute(f"SELECT * FROM environ_mob WHERE region='{region[0]}';")
            mob_types = await self.quefe(f"SELECT mob_code, quantity FROM environ_diversity WHERE environ_code='{region[0]}';", type='all')

            for m in mob_types:
                if swi == 0: line = line + f"╟**`{m[0]}`**`[{m[1]}]`"; swi += 2
                elif swi < 4: line = line + f"⠀·⠀**`{m[0]}`**`[{m[1]}]`"; swi += 1
                elif swi == 4: line = line + f"\n╟**`{m[0]}`**`[{m[1]}]`"; swi = 2

            reembed = discord.Embed(title = f":map: `{region[0]}`|**{region[1]}**", description = f"""```dsconfig
    {region[2]}```""", colour = discord.Colour(0x011C3A))
            reembed.add_field(name=":bar_chart: Entities", value=f"╟`Players` · **{players}**\n╟`Mobs` · **{mobs}**", inline=True)
            reembed.add_field(name=":bar_chart: Terrain", value=f"╟`Area` · {region[4]}m x {region[5]}m\n╟`Land` · **{region[7]}** slots\n╟`Biomes` · *{region[6].replace(' - ', '*, *')}*", inline=True)
            reembed.add_field(name=f":smiling_imp: Diversity ({len(mob_types)})", value=line, inline=True)
            reembed.add_field(name=":scales: Economy", value=f"╟`Shop` · Selling **{len(region[9].split(' - '))}** items\n╟`Traders` · Selling **{len(region[8].split(' - '))}** ingredients", inline=True)
            reembed.set_thumbnail(url=self.biome[region[6].split(' - ')[0]])
            reembed.set_image(url=region[3])
            return reembed, region[0]
            #else:
            #    await ctx.send("*Nothing but dust here...*")
        
        async def attachreaction(msg):
            await msg.add_reaction("\U000023ee")    #Top-left
            await msg.add_reaction("\U00002b05")    #Left
            await msg.add_reaction("\U000027a1")    #Right
            await msg.add_reaction("\U000023ed")    #Top-right
            await msg.add_reaction("\U0001f50e")    #Top-right

        pages = len(regions)
        currentpage = 1
        cursor = 0

        emli = []
        for curp in range(pages):
            myembed, region_tag = await makeembed(curp, pages, currentpage)
            emli.append((myembed, region_tag))
            currentpage += 1

        if cur_PLACE:
            for em in emli:
                if em[1] == cur_PLACE[0]: cursor = emli.index(em); break
        else:
            for em in emli:
                if em[1] == 'region.0': cursor = emli.index(em); break

        msg = await ctx.send(embed=emli[cursor][0])
        if pages > 1: await attachreaction(msg)
        else: return

        def UM_check(reaction, user):
            return user.id == ctx.author.id and reaction.message.id == msg.id

        while True:
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=20, check=UM_check)
                if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                    cursor += 1
                    await msg.edit(embed=emli[cursor][0])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U00002b05" and cursor > 0:
                    cursor -= 1
                    await msg.edit(embed=emli[cursor][0])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U0001f50e":
                    temsg = await ctx.send(":mag_right: Please provide region's code (e.g. `region.0`)")

                    def UMC_check(m):
                        return m.channel == ctx.channel and m.author == ctx.author

                    try: m = await self.client.wait_for('message', timeout=15, check=UMC_check)
                    except asyncio.TimeoutError: await ctx.send(f"<:osit:544356212846886924> Requested time-out!"); return

                    for em in emli:
                        if em[1] == m.content: tembed = em[0]; break
                    await temsg.delete()
                    try: await msg.edit(embed=tembed)
                    except NameError: await ctx.send("<:osit:544356212846886924> Region not found :<"); continue
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U000023ee" and cursor != 0:
                    cursor = 0
                    await msg.edit(embed=emli[cursor][0])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                    cursor = pages - 1
                    await msg.edit(embed=emli[cursor][0])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
            except asyncio.TimeoutError: 
                await msg.delete(); return






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



# ============= ADMIN ==================

    @commands.command()
    @check_id()
    async def megagive(self, ctx, *args):
        try: target = await commands.MemberConverter().convert(ctx, args[0])
        except commands.CommandError: await ctx.send("Invalid `user`"); return
        except IndexError: await ctx.send("Missing `user`"); return

        try: money = int(args[1])
        except IndexError: await ctx.send('Missing `money`'); return
        except ValueError: await ctx.send('Invalid `money`'); return

        if await _cursor.execute(f"UPDATE personal_info SET money=money+{money} WHERE id='{target.id}';") == 0:
            await ctx.send(f"User **{target.name}** has not incarnted"); return
        
        await ctx.send(f":white_check_mark: Under the name of almighty Aknalumos, **<:36pxGold:548661444133126185>{money}** has been given to **{target.name}**!"); return

    @commands.command()
    @check_id()
    async def megatao(self, ctx, *args):
        try: target = await commands.MemberConverter().convert(ctx, args[0])
        except commands.CommandError: await ctx.send("Invalid `user`"); return
        except IndexError: await ctx.send("Missing `user`"); return

        try: item_code = args[1]
        except IndexError: await ctx.send("Missing `item_code`"); return

        try: quantity = int(args[2])
        except (ValueError, IndexError): quantity = 1

        if item_code.startswith('ig'):
            t = await _cursor.execute(f"SELECT func_ig_reward('{target.id}', '{item_code}', {quantity}); ")
        elif item_code.startswith('it') or item_code.startswith('ar') or item_code.startswith('am') or item_code.startswith('bp'):
            t = await _cursor.execute(f"SELECT func_it_reward('{target.id}', '{item_code}', {quantity}); ")
        elif item_code.startswith('if'):
            try: land_code = args[3]
            except IndexError: await ctx.send("Missing `land_code`"); return
            t = await _cursor.execute(f"SELECT func_if_reward('{land_code}', '{item_code}', {quantity}); ")
        
        if not t: await ctx.send(":x:"); print(t); return
        await ctx.send(f":white_check_mark: Given {quantity} `{item_code}` to **{target.name}**")

    @commands.command()
    @check_id()
    async def megafreeze(self, ctx, *args):
        try:
            target_id = ctx.message.mentions[0].id
            cmd_tag = args[1]
            if cmd_tag.startswith('<@'): cmd_tag = args[0]
        except (IndexError, TypeError): await ctx.send(":warning: Missing stuff!"); return

        if await self.client.loop.run_in_executor(None, partial(redio.delete, f'{cmd_tag}{target_id}')) == 0: await ctx.send(':x:')
        else: await ctx.send(':white_check_mark:')

    @commands.command()
    @check_id()
    async def megakill(self, ctx, *args):
        if not args: await ctx.send(":warning: Missing user!"); return
        try: 
            target_id = ctx.message.mentions[0].id
            target_name = ctx.message.mentions[0].mention
        except (IndexError, TypeError):
            target_id = args[0]
            target_name = args[0]

        query = f"""DELETE FROM pi_degrees WHERE user_id='{target_id}';
                    DELETE FROM pi_guild WHERE user_id='{target_id}';
                    DELETE FROM cosmetic_preset WHERE user_id='{target_id}';
                    DELETE FROM pi_arts WHERE user_id='{target_id}';
                    UPDATE pi_inventory SET existence='BAD' WHERE user_id='{target_id}';
                    UPDATE pi_land SET user_id='BAD' WHERE user_id='{target_id}';
                    DELETE FROM pi_bank WHERE user_id='{target_id}';
                    DELETE FROM pi_avatars WHERE user_id='{target_id}';
                    DELETE FROM pi_hunt WHERE user_id='{target_id}';
                    DELETE FROM pi_mobs_collection WHERE user_id='{target_id}';
                    DELETE FROM pi_rest WHERE user_id='{target_id}';
                    DELETE FROM pi_quests WHERE user_id='{target_id}';
                    DELETE FROM personal_info WHERE id='{target_id}';"""

        if await _cursor.execute(query) == 0:
            await ctx.send(':warning: User has not incarnated'); return
        await ctx.send(f":white_check_mark: Slashed {target_name} into half. Bai ya~")


# ============= TOOLS =================

    async def ava_scan(self, MSG, type='all', target_id='n/a'):
        # Get target
        #try: target = await self.client.get_user_info(int(target_id))
        #except discordErrors.NotFound:
        target = MSG.author
        target_id = str(target.id)

        # Status check
        try: 
            LP, MAX_LP, STA, MAX_STA, cur_X, cur_Y, stats, dob = await self.quefe(f"SELECT LP, MAX_LP, STA, MAX_STA, cur_X, cur_Y, stats, dob FROM personal_info WHERE id='{target_id}'")
        except TypeError: await MSG.channel.send(f"You don't have a *character*, **{MSG.author.name}**. Use `incarnate` to create one."); return
        if stats == 'DEAD': 
            #if target_id == MSG.author.id: await MSG.channel.say(f"<:tumbstone:544353849264177172> You. Are. Dead, **{target.mention}**. Have a nice day!"); return
            #else: await MSG.channel.send(f"<:tumbstone:544353849264177172> The target **{target.name}** was dead, **{MSG.author.mention}**. *Press F to pay respect.*"); return
            await MSG.channel.send(f"<:tumbstone:544353849264177172> You. Are. Dead, **{target.mention}**. Have a nice day!"); return

        # Time check
        if type == 'all':
            time_pack = await self.client.loop.run_in_executor(None, self.time_get)

            await _cursor.execute(f"UPDATE personal_info SET age={time_pack[0] - int(dob.split(' - ')[2])} WHERE id='{target_id}';")
            return True
        # STA, LP, sign_in check
        elif type == 'life_check':
            if cur_X < 0 or cur_Y < 0: await MSG.channel.send(f"<:osit:544356212846886924> {target.mention}, please **log in**. Just use command `teleport` anywhere and you'll be signed in the world's map. (e.g. `teleport 1 1`)"); return False
            if STA < 0: await _cursor.execute(f"UPDATE personal_info SET LP=LP-{abs(STA)}, STA=0 WHERE id='{target_id}';")
            if LP <= 0:
                # Status reset
                reviq = f"UPDATE personal_info SET stats='DEAD', cur_PLACE='region.0', cur_X=-1, cur_Y=-1, cur_MOB='n/a', cur_USER='n/a', right_hand='ar13', left_hand='ar13', money=0, perks=0, deaths=deaths+1 WHERE id='{target_id}';"
                # Remove FULL and ONGOING quests
                reviq = reviq + f" DELETE FROM pi_quests WHERE user_id='{target_id}' AND stats IN ('FULL', 'ONGOING');"
                # Remove all items but ar13|Fist (Default)
                reviq = reviq + f" UPDATE pi_inventory SET existence='BAD' WHERE user_id='{target_id}' AND item_code!='ar13';"
                await _cursor.execute(reviq)

                await MSG.channel.send(f"<:tumbstone:544353849264177172> {target.mention}, you are dead. Please re-incarnate.")
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
        user_id = str(MSG.author.id)

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
        """| Tools\n
           x1, y1, x2, y2, distance: float\n
           (x1, y1: user's coord)\n
           return: distance"""

        if type == 'c-d':
            dist_x = abs(x1 - x2); dist_y = abs(y1 - y2)

            return int(math.sqrt(dist_x*dist_x + dist_y*dist_y)*1000)

        elif type == 'd-c':
            dist_x = abs(x1 - x2); dist_y = abs(y1 - y2)
            # Distance from A to B      |      distance --> Distance from A to C
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
        await _cursor.execute(f"UPDATE personal_info SET cur_X={desti_x:.3}, cur_Y={desti_y:.3} WHERE id='{user_id}';")
        # Assign the coord to ava
        #self.ava_dict[user_id]['realtime_zone']['current_coord'] = [desti_x, desti_y]

    @commands.command(pass_context=True)
    @check_id()
    async def get_imgur(self, ctx, *args):
        if args:
            if '.png' not in args[0] or '.jpg' not in args[0] or '.jpeg' not in args[0] or '.gif' not in args[0]:
                await ctx.send(f"<:osit:544356212846886924> {ctx.message.author.mention}, invalid link!"); return
            else: source = args[0]
        else:
            package = ctx.message.attachments
            if package: source = package[0]['proxy_url']
            else: return

        resp = await self.client.loop.run_in_executor(None, self.imgur_client.upload_from_url, source)
        reembed = discord.Embed(description=f"{resp['link']}", colour = discord.Colour(0x011C3A))
        reembed.set_image(url=resp['link'])
        await ctx.send(embed=reembed)

    async def percenter(self, percent, total=10):
        total = range(total)
        if len(total) <= 0 or percent <= 0: return False
        if random.choice(total) <= percent: return True
        else: return False

    async def inj_filter(self, text):
        text = text.replace("'", ' ')
        text = text.replace("=", ' ')
        text = text.replace("`", ' ')
        text = text.replace("\"", ' ')
        text = text.replace(";", ' ')
        text = text.replace("DROP ", "DR0P ")
        text = text.replace("TRUNCATE ", 'TRUNKATE ')
        text = text.replace("DELETE ", 'DELELE ')
        text = text.replace("UPDATE ", "UPDOTE ")
        return text

    async def space_out(self, text):
        return ' '.join([f"{ch} " for ch in text])

    async def realty_calc(self, inipr, taim, averange):
        temp = []
        for time_cursor in averange:
            init_price = inipr
            print(taim, init_price)
            if taim[0] % 10 == 0:
                if (taim[2] + time_cursor) % 10 == 0: init_price *= 10
                else: init_price /= 10
            elif taim[0] % 7 == 0:
                if (taim[2] + time_cursor) % 7 == 0: init_price *= 7
                else: init_price /= 7
            elif taim[0] % 5 == 0:
                if (taim[2] + time_cursor) % 5 == 0: init_price *= 5
                else: init_price /= 5
            elif taim[0] % 3 == 0:
                if (taim[2] + time_cursor) % 3 == 0: init_price *= 3
                else: init_price /= 3
            elif taim[0] % 2 == 0:
                if (taim[2] + time_cursor) % 2 == 0: init_price *= 2
                else: init_price /= 2

            if (taim[2] + time_cursor) % 10 == 0:
                if taim[0] % 10 == 0: init_price /= 10
                else: init_price *= 10
            elif (taim[2] + time_cursor) % 7 == 0:
                if taim[0] % 7 == 0: init_price /= 7
                else: init_price *= 7
            elif (taim[2] + time_cursor) % 5 == 0:
                if taim[0] % 5 == 0: init_price /= 5
                else: init_price *= 5
            elif (taim[2] + time_cursor) % 3 == 0:
                if taim[0] % 3 == 0: init_price /= 3
                else: init_price *= 3
            elif (taim[2] + time_cursor) % 2 == 0:
                if taim[0] % 2 == 0: init_price /= 2
                else: init_price *= 2

            temp.append(init_price)
        print("RAW Realty Sess", temp)
        return int(np.mean(temp))

    async def illulink_check(self, illulink):
        temp = discord.Embed()
        try:
            temp.set_image(url=illulink)
            return illulink
        except discordErrors.HTTPException: return False





# ============= DATA MANIPULATION =================

    @commands.command()
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
        except IndexError: await ctx.send("<:osit:544356212846886924> Invalid directory!")

        await ctx.send(":white_check_mark: Item added!")

    @commands.command()
    @check_id()
    async def avaava_giveitem(self, ctx, *args):
        raw = list(args)

        try:
            storage = raw[0]
            item_code = raw[1]
            try: quantity = int(raw[2])
            except IndexError: quantity = 1
        except IndexError: await ctx.send(f"<:osit:544356212846886924> Args missing")

        # GET ITEM INFO
        try:
            if storage == 'it': 
                tags = await self.quefe(f"""SELECT name, tags, price, quantity FROM model_item WHERE item_code='{item_code}';""")
                i_tags = tags[0].split(' - ')
        # E: Item code not found
        except TypeError: await ctx.send("<:osit:544356212846886924> Item_code/Item_id not found!"); return

        # ITEM
        if storage == 'it':
            # CONSUMABLE
            if 'consumable' in i_tags:
                # Create item in inventory. Ignore the given quantity please :>
                await _cursor.execute(f"INSERT INTO pi_inventory SELECT 0, '{str(ctx.message.author.id)}', item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, infuse_query, order_query, passive_query, ultima_query, quantity, price, dmg, stealth, evo, aura, craft_value, illulink FROM model_item WHERE item_code='{item_code}';")
                # (MODEL FOR QUERY RECORD-TRANSFERING) ------- await _cursor.execute(f"INSERT INTO pi_inventory SELECT 0, {str(ctx.message.author.id)}, item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, quantity, price, dmg, stealth FROM model_item WHERE item_code='{item_code}';")

            # INCONSUMABLE
            else:
                # Increase item_code's quantity
                if await _cursor.execute(f"UPDATE pi_inventory SET quantity=quantity+{quantity} WHERE user_id='{str(ctx.message.author.id)}' AND item_code='{item_code}';") == 0:
                    # E: item_code did not exist. Create one, with given quantity
                    await _cursor.execute(f"INSERT INTO pi_inventory SELECT 0, '{str(ctx.message.author.id)}', item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, infuse_query, order_query, passive_query, ultima_query, {quantity}, price, dmg, stealth, evo, aura, craft_value, illulink FROM model_item WHERE item_code='{item_code}';")

        # INGREDIENT
        elif storage == 'ig':
            # UN-SERIALIZABLE
            # Increase item_code's quantity
            if await _cursor.execute(f"UPDATE pi_inventory SET quantity=quantity+{quantity} WHERE user_id='{str(ctx.message.author.id)}' AND item_code='{item_code}';") == 0:
                # E: item_code did not exist. Create one, with given quantity
                await _cursor.execute(f"INSERT INTO pi_inventory SELECT 0, {str(ctx.message.author.id)}, ingredient_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, infuse_query, order_query, passive_query, ultima_query, quantity, price, dmg, stealth, evo, aura, craft_value, illulink FROM model_ingredient WHERE ingredient_code='{item_code}';")

        await ctx.send(":white_check_mark: Done.")

    @commands.command()
    @check_id()
    async def todo(self, ctx, *args):
        if not args:
            bundle = await self.quefe("SELECT taime, content, id FROM tz_todo", type='all')
            line = '\n'

            try:
                for pack in bundle:
                    line = line + f"**━{pack[2]}━━━━━{pack[0]}━━━**\n{pack[1]}\n"
            except TypeError:
                line = line + f"**━{bundle[2]}━━━━━{bundle[0]}━━━**\n{bundle[1]}\n"

            reembed = discord.Embed(description=line, color=discord.Colour(0xB1F1FA))
            await ctx.send(embed=reembed, delete_after=20); return

        if args[0] in ['create', 'add', 'make']:
            content = ' '.join(args[1:])
            create_point = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            await _cursor.execute(f"INSERT INTO tz_todo VALUES (0, '{content}', '{create_point}')")
            await ctx.send(":white_check_mark: Done"); return
        elif args[0] == 'delete':
            try: 
                if await _cursor.execute(f"DELETE FROM tz_todo WHERE id='{args[1]}';") == 0:
                    await ctx.send("Id not found"); return
            except IndexError: await ctx.send("Hey you, I need an id."); return
            await ctx.send(f"Deleted todo `{args[1]}`")

    async def quefe(self, query, args=None, type='one'):
        """args ---> tuple"""
        global conn
        global _cursor

        try: await _cursor.execute(query, args=args)
        except RuntimeError: return ''
        except mysqlError.OperationalError:
            loop.stop()
            conn, _cursor = loop.run_until_complete(get_CURSOR())
            await _cursor.execute(query, args=args)
        if type == 'all': resu = await _cursor.fetchall()
        else: resu = await _cursor.fetchone()
        return resu

    def time_get(self):
        day = 1; month = 1; year = 1
        delta = relativedelta(datetime.now(), self.client.STONE)
        #print(f"DELTA: {delta.days} | {delta.months} | {delta.years}")

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
            regions = await self.quefe("SELECT environ_code FROM environ", type='all')

            for region in regions:
                region = region[0]
                
                # ----------- MOB/BOSS/NPC initialize ------------
                mobs = await self.quefe(f"SELECT mob_code, quantity, limit_Ax, limit_Ay, limit_Bx, limit_By FROM environ_diversity WHERE environ_code='{region}';", type='all')

                for mob in mobs:
                    mob = list(mob)
                    # MOB
                    if mob[0].startswith('mb'):
                        # Quantity of kind in a diversity check
                        qk = await self.quefe(f"SELECT COUNT(*) FROM environ_mob WHERE mob_code='{mob[0]}' AND region='{region}';")
                        if qk[0] == mob[1]: continue
                        elif qk[0] < mob[1]: mob[1] -= qk[0]
                        
                        # Get the <mob> prototype
                        name, branch, lp, str, chain, speed, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY = await self.quefe(f"SELECT name, branch, lp, str, chain, speed, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY FROM model_mob WHERE mob_code='{mob[0]}';")
                        rewards = rewards.split(' | ')
                        
                        # Mass production
                        for count in range(mob[1]):
                            # Generating rewards
                            status = []; objecto = []; bingo_list = []
                            for reward in rewards:
                                stuff = reward.split(' - ')
                                if random.choice(range(int(stuff[2]))) == 0:
                                    if stuff[0] == 'money': bingo_list.append(f"<:36pxGold:548661444133126185>{stuff[1]}")

                                    # Stats reward
                                    if stuff[0] in ['money']: status.append(f"{stuff[0]}={stuff[0]}+{int(stuff[1])}")
                                    # ... other shit
                                    else:
                                        # Get item/weapon's info
                                        temp = await self.quefe(f"SELECT * FROM model_item WHERE item_code='{stuff[0]}';")
                                        # SERI / UN-SERI check
                                        # SERI
                                        if 'inconsumbale' in temp[2].split(' - '):
                                            #objecto.append(f"""INSERT INTO pi_inventory VALUE ("user_id_here", {', '.join(temp)});""")
                                            objecto.append(f"""SELECT func_it_reward('user_id_here', '{stuff[0]}', '{random.choice(range(stuff[1]))}');""")
                                        # UN-SERI
                                        else:
                                            #objecto.append(f"""UPDATE pi_inventory SET quantity=quantity+{random.choice(range(stuff[1]))} WHERE user_id="user_id_here" AND item_code='{stuff[0]}';""")
                                            objecto.append(f"""SELECT func_ig_reward('user_id_here', '{stuff[0]}', '{random.choice(range(stuff[1]))}');""")
                            stata = f"""UPDATE personal_info SET {', '.join(status)} WHERE id="user_id_here"; """
                            rewards_query = f"{stata} {' '.join(objecto)}"

                            # Insert the mob to DB
                            await _cursor.execute(f"""INSERT INTO environ_mob VALUES (0, 'mob', '{mob[0]}', "{name}", '{branch}', {lp}, {str}, {chain}, {speed}, {au_FLAME}, {au_ICE}, {au_DARK}, {au_HOLY}, '{' | '.join(bingo_list)}', '{rewards_query}', '{region}', {mob[2]}, {mob[3]}, {mob[4]}, {mob[5]}, 'n/a');""")
                            counter_get = await self.quefe("SELECT MAX(id_counter) FROM environ_mob")
                            await _cursor.execute(f"UPDATE environ_mob SET mob_id='mob.{counter_get[0]}' WHERE id_counter={counter_get[0]};")
                    
                    # NPC
                    elif mob[0].startswith('p'):
                        # Quantity of kind in a diversity check
                        qk = await self.quefe(f"SELECT COUNT(*) FROM environ_npc WHERE npc_code='{mob[0]}' AND region='{region}';")
                        if qk[0] == mob[1]: continue
                        elif qk[0] < mob[1]: mob[1] -= qk[0]
                        
                        # Get the <mob> prototype
                        name, branch, lp, str, chain, speed, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY = await self.quefe(f"SELECT name, branch, lp, str, chain, speed, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY FROM model_npc WHERE npc_code='{mob[0]}';")
                        if rewards:
                            rewards = rewards.split(' | ')
                            
                            
                            # Mass production
                            for count in range(mob[1]):
                                # Generating rewards
                                status = []; objecto = []; bingo_list = []
                                for reward in rewards:
                                    stuff = reward.split(' - ')
                                    if random.choice(range(int(stuff[2]))) == 0:
                                        if stuff[0] == 'money': bingo_list.append(f"<:36pxGold:548661444133126185>{stuff[1]}")

                                        # Stats reward
                                        if stuff[0] in ['money']: status.append(f"{stuff[0]}={stuff[0]}+{int(stuff[1])}")
                                        # ... other shit
                                        else:
                                            # Get item/weapon's info
                                            temp = await self.quefe(f"SELECT * FROM model_item WHERE item_code='{stuff[0]}';")
                                            # SERI / UN-SERI check
                                            # SERI
                                            if 'inconsumbale' in temp[2].split(' - '):
                                                #objecto.append(f"""INSERT INTO pi_inventory VALUE ("user_id_here", {', '.join(temp)});""")
                                                objecto.append(f"""SELECT func_it_reward('user_id_here', '{stuff[0]}', '{random.choice(range(stuff[1]))}');""")
                                            # UN-SERI
                                            else:
                                                #objecto.append(f"""UPDATE pi_inventory SET quantity=quantity+{random.choice(range(stuff[1]))} WHERE user_id="user_id_here" AND item_code='{stuff[0]}';""")
                                                objecto.append(f"""SELECT func_ig_reward('user_id_here', '{stuff[0]}', '{random.choice(range(stuff[1]))}');""")
                                stata = f"""UPDATE personal_info SET {', '.join(status)} WHERE id="user_id_here"; """
                                rewards_query = f"{stata} {' '.join(objecto)}"
                        else: rewards_query = ''; bingo_list = []

                        # Insert the mob to DB
                        await _cursor.execute(f"""INSERT INTO environ_npc VALUES (0, 'main', '{mob[0]}', "{name}", '{branch}', {lp}, {str}, {chain}, {speed}, {au_FLAME}, {au_ICE}, {au_DARK}, {au_HOLY}, '{' | '.join(bingo_list)}', '{rewards_query}', '{region}', {mob[2]}, {mob[3]}, {mob[4]}, {mob[5]}, 'n/a', '');""")
                        counter_get = await self.quefe("SELECT MAX(id_counter) FROM environ_npc")
                        await _cursor.execute(f"UPDATE environ_npc SET npc_id='npc.{counter_get[0]}' WHERE id_counter={counter_get[0]};")

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
                self.environ[region]['map'] = map
                
                # ----------- QUESTS initialize ----------                
                try: self.environ[region]['characteristic']['quest'] = data_QUESTS
                except KeyError: print("KEY_ERROR")
            
            print("___WORLD built() done")  

        async def rtzone_refresh():
            #fix_list = await self.quefe("SELECT id FROM personal_info WHERE cur_MOB != 'n/a' OR cur_USER != 'n/a';", type='all')
            #for user_id in fix_list:
            await _cursor.execute(f"UPDATE personal_info SET cur_MOB='n/a', cur_USER='n/a';")
            await _cursor.execute(f"UPDATE environ_mob SET lockon='n/a';")

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

        prote_codes = {'Iris': 'av0',
                        'Zoey': 'av1',
                        'Ardena': 'av2',
                        'Yamabuki': 'av3',
                        'Yamabuki_Cosplay': 'av4',
                        'Yamabuki_NSFW': 'av5',
                        'Myu': 'av6',
                        'Myu_NSFW': 'av7',
                        'Enju': 'av8',
                        'Enju_NSFW': 'av9',
                        'Enju_Cosplay': 'av10',
                        'Shima_Rin': 'av11',
                        'Akari': 'av12',
                        'Akari_NSFW': 'av13',
                        'Akari_Cosplay': 'av14',
                        'RPG_Girl_1': 'av15',
                        'GBF_Female': 'av16',
                        'GBF_Male': 'av17',
                        'GBF_Female_2': 'av18',
                        'Djeeta': 'av19'}

        ##bg_codes = {'LoveRibbon/evening': 'bg0'}
        bg_codes = {'medieval_indoor': 'bg0',
                    'medieval_outdoor': 'bg1',
                    'modern_indoor': 'bg2',
                    'modern_outdoor': 'bg3',
                    'fengfeng': 'bg4',
                    'sleepypang': 'bg5',
                    'rocha_cold': 'bg6',
                    'rocha_crimson': 'bg7',
                    'rocha_gold': 'bg8',
                    'rocha_green': 'bg9'}

        def ImageGen_supporter(char, rawimg):
            img = Image.open(f'C:/Users/DELL/Desktop/bot_cli/data/profile/char/{char}/{rawimg}').convert('RGBA')
            img = img.resize((int(self.prote_lib['form'][0].height/img.height*img.width), self.prote_lib['form'][0].height))
            self.prote_lib[prote_codes[char]].append(img)

        def BackgroundGen_supporter(bg_name, rawimg):
            img = Image.open(f'C:/Users/DELL/Desktop/bot_cli/data/profile/bg/{bg_name}/{rawimg}').convert('RGBA')
            img = img.resize((800, 600))
            img = img.filter(ImageFilter.GaussianBlur(2.6))
            self.prote_lib['bg'][bg_codes[bg_name]].append(img)

        def bg_plugin():
            self.prote_lib['bg'] = {}
            self.prote_lib['bg_stock'] = []
            self.prote_lib['stock_bar'] = []
            self.prote_lib['bg_gif'] = []

            for bg_name, bg_id in bg_codes.items():
                self.prote_lib['bg'][bg_id] = []
                for rawimg in listdir(f'C:/Users/DELL/Desktop/bot_cli/data/profile/bg/{bg_name}'):
                    BackgroundGen_supporter(bg_name, rawimg)
                    #await self.client.loop.run_in_executor(None, ImageGen_supporter, char_name, rawimg)

            img = Image.open(f'C:/Users/DELL/Desktop/bot_cli/data/stock graph/bg_roll.png').convert('RGBA')
            self.prote_lib['bg_stock'].append(img)
            img = Image.open(f'C:/Users/DELL/Desktop/bot_cli/data/stock graph/bar.png').convert('RGBA')
            self.prote_lib['stock_bar'].append(img)

            particle_after = []
            particles = imageio.mimread('C:/Users/DELL/Downloads/gif/train.gif', memtest=False)
            for particle in particles:
                a = Image.fromarray(particle)
                a = a.resize((800, 600))
                a = a.filter(ImageFilter.GaussianBlur(2.6))
                particle_after.append(a)
            self.prote_lib['bg_gif'].append(particle_after)

        def form_plugin():
            self.prote_lib['form'] = []
            img = Image.open('C:/Users/DELL/Desktop/bot_cli/data/profile/form3.png').convert('RGBA')
            self.prote_lib['form'].append(img)
        
        def badge_plugin():
            ranking_badges = {'iron': 'badge_IRON.png', 'bronze': 'badge_BRONZE.png', 'silver': 'badge_SILVER.png', 'gold': 'badge_GOLD.png', 'adamantite': 'badge_ADAMANTITE.png', 'mithryl': 'badge_MITHRYL.png'}
            self.prote_lib['badge'] = {}
            for key, dir in ranking_badges.items():
                badge_img = Image.open(f'C:/Users/DELL/Desktop/bot_cli/data/profile/badges/{dir}').convert('RGBA')
                badge_img = badge_img.resize((int(badge_img.width/1.5), int(badge_img.height/1.5)))
                self.prote_lib['badge'][key] = badge_img

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
            self.prote_lib['font']['stock_region'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/stock graph/CAROBTN.ttf', 31)
            self.prote_lib['font']['stock_region_bar'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/stock graph/CAROBTN.ttf', 15)
            self.prote_lib['font']['stock_region_name'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/stock graph/CAROBTN.ttf', 62)
            

        await self.client.loop.run_in_executor(None, bg_plugin)
        await self.client.loop.run_in_executor(None, form_plugin)
        await self.client.loop.run_in_executor(None, font_plugin)
        await self.client.loop.run_in_executor(None, badge_plugin)

        for char_name, char_id in prote_codes.items():
            self.prote_lib[char_id] = []
            for rawimg in listdir(f'C:/Users/DELL/Desktop/bot_cli/data/profile/char/{char_name}'):
                ImageGen_supporter(char_name, rawimg)
                #await self.client.loop.run_in_executor(None, ImageGen_supporter, char_name, rawimg)


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
            # [0]: Item's name | [1]: Quantity | [2]: Drop rate
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



















