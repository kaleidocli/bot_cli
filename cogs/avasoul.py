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
from functools import partial
import numpy as np
import aiomysql
import redis
import pymysql.err as mysqlError

from .avasoul_pack import avaThirdParty
from .avasoul_pack.avaTools import avaTools
from .avasoul_pack.avaUtils import avaUtils
from utils import checks

class avasoul:
    def __init__(self, client):
        self.client = client
        self.client.thp = avaThirdParty.avaThirdParty(client=self.client)
        self.__cd_check = self.client.thp.cd_check
        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)
        self.client.quefe = self.tools.quefe

        self.ava_dict = {}
        self.prote_lib = {}
        self.jobs_dict = {}
        self.data_ARSENAL = {}; self.data_SUPPLY = {}; self.data_AMMU = {}
        self.data = {}
        self.environ = {}
        self.thepoof = 0

        self.biome = {'SAVANNA': 'https://imgur.com/qc1NNIu.png',
                    'JUNGLE': 'https://imgur.com/3j786qW.png',
                    'DESERT': 'https://imgur.com/U0wtRU7.png',
                    'RUIN': 'https://imgur.com/O8rHzCR.png',
                    'FROST': 'https://imgur.com/rjwiDU4.png',
                    'MOUNTAIN': 'https://imgur.com/cxwSH7m.png',
                    'OCEAN': 'https://imgur.com/fQFO2b4.png'}

    async def on_ready(self):
        await self.data_plugin()


    @commands.command()
    async def incarnate(self, ctx, *args):
        id = str(ctx.author.id); name = ctx.author.name

        # Create a living entity (creator-only)
        if args:
            if str(ctx.author.id) == '214128381762076672':
                try: id = str(ctx.mentions[0].id); name = ctx.mentions[0].name
                except IndexError: id = ' '.join(args); name = id
            else: await ctx.send(":no_entry_sign: You wish :>"); return
            
        resu = await self.client.quefe(f"SELECT stats FROM personal_info WHERE id='{id}'")
        try:
            if resu[0] != 'DEAD':
                await ctx.send(f"<:osit:544356212846886924> You've already incarnate!"); return
        except TypeError: pass
        
        year, month, day, hour, minute = await self.client.loop.run_in_executor(None, self.utils.time_get)
        bump = await self.tools.character_generate(id, name, dob=[year, month, day, hour, minute], resu=resu)
        if not bump:
            await ctx.send(f"{ctx.author.mention}", embed=discord.Embed().set_image(url='https://imgur.com/e8cIazx.gif'))
        else: await ctx.send(f":white_check_mark: {ctx.author.mention} has successfully re-incarnated. **WELCOME BACK!**")         

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
        
        await ctx.send("<a:RingingBell:559282950190006282> Please type `deletion confirm` to proceed.")

        def UMCc_check(m):
            return m.channel == ctx.channel and m.author == ctx.author and m.content.lower() == 'deletion confirm'

        try: await self.client.wait_for('message', timeout=15, check=UMCc_check)
        except asyncio.TimeoutError: await ctx.send(f"<:osit:544356212846886924> Requested time-out!"); return
        
        await self.client._cursor.execute(query)
        await ctx.send(f":white_check_mark: *Sayonara, {ctx.author.name}!* May the Olds look upon you..."); return

    @commands.command(aliases=['p'])
    async def profile(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        await self.tools.ava_scan(ctx.message, type='all')

        try:
            id = args[0]
            _vmode = 'INDIRECT'
        except IndexError: id = str(ctx.message.author.id); _vmode = 'DIRECT'
        
        # Data get and paraphrase
        # pylint: disable=unused-variable
        try: name, age, gender, money, merit, right_hand, left_hand, combat_HANDLING, STA, MAX_STA, LP, MAX_LP, STR, INTT, partner, evo = await self.client.quefe(f"SELECT name, age, gender, money, merit, right_hand, left_hand, combat_HANDLING, STA, MAX_STA, LP, MAX_LP, STR, INTT, partner, evo FROM personal_info WHERE id='{id}' OR name LIKE '%{id}%';")
        except TypeError: await ctx.send("<:osit:544356212846886924> User has not incarnated!"); return
        # pylint: enable=unused-variable
        if str(ctx.message.author.id) not in ['214128381762076672', partner, f'{ctx.author.id}']: await ctx.send("<:osit:544356212846886924> You have to be user's *partner*, *mother* or *father* to view their status!"); return

        degrees = '` `'.join(await self.client.quefe(f"SELECT degree FROM pi_degrees WHERE user_id='{id}';"))
        
        if right_hand != 'n/a':
            rh_name = await self.client.quefe(f"SELECT name FROM pi_inventory WHERE existence='GOOD' AND (item_id='{right_hand}' OR item_code='{right_hand}') AND user_id='{str(ctx.message.author.id)}';")
            try: right_hand = f"`{right_hand}`|**{rh_name[0]}**"
            except TypeError:
                if right_hand == 'ar13': await self.client._cursor.execute(f"SELECT func_it_reward('{ctx.author.id}', 'ar13', 1);"); rh_name = "ar13"
                else: await self.client._cursor.execute(f"UPDATE personal_info SET right_hand='ar13' WHERE id='{ctx.author.id}';"); rh_name = "ar13"
        if left_hand != 'n/a': 
            lh_name = await self.client.quefe(f"SELECT name FROM pi_inventory WHERE existence='GOOD' AND (item_code='{left_hand}' OR item_id='{left_hand}') AND user_id='{str(ctx.message.author.id)}';")
            try: left_hand = f"`{left_hand}`|**{lh_name[0]}**"
            except TypeError:
                if left_hand == 'ar13': await self.client._cursor.execute(f"SELECT func_it_reward('{ctx.author.id}', 'ar13', 1);"); lh_name = "ar13"
                else: await self.client._cursor.execute(f"UPDATE personal_info SET left_hand='ar13' WHERE id='{ctx.author.id}';"); lh_name = "ar13"

        lmao = {'f': 'female', 'm': 'male'}
        # Status
        box = f"\n░░░░ **{name}** | {lmao[gender].capitalize()}, {age} ░░░░\n╟**`Money`** · <:36pxGold:548661444133126185>{money}\n╟**`Merit`** · {merit}\n╟**`Degrees`** · `{degrees}`\n━━━━━╾ {combat_HANDLING.capitalize()} hand ╼━━━━\n╟**`RIGHT`** · {right_hand}\n╟**`LEFT`** · {left_hand}\n━━━━━╾ **`EVO`** {evo} ╼━━━━━━\n**·** `STA` {STA}/{MAX_STA}\n**·** `LP` {LP}/{MAX_LP}\n**·** `STR` {STR}\n**·** `INT` {INTT}"
        await ctx.author.send(box)
        await ctx.send(":incoming_envelope: **Bang!** <a:blob_snu:531060438142812190> *From Cli with love*")

    @commands.command(aliases=['guide'])
    @commands.cooldown(1, 7, type=BucketType.user)
    async def help(self, ctx, *args):
        raw = list(args); temb_socket = []
        #prefixes = {336642139381301249: 'cli '}

        #try: prefix = prefixes[ctx.guild.id]
        #except KeyError: prefix = '>'

        #prefix = 'cli '
        if not raw:
            temball = discord.Embed(
                title = '**G U I D E**⠀⠀|⠀⠀**R P G  C O M M A N D S**',
                description = f"""
                                 ```ini
⠀| [help <command>] for more info.
⠀| [tutorial] if you are beginner.```
                                ╟ **NEW?** Use **`incarnate`** right away!
                                ╟ Already incarnated? [Join the Pralaeyr!](https://discord.gg/NGtXxXj)

                                ╟ **『LORE』**
                                ⠀⠀You - a Remnant as many others - woke up in the middle of an unreal world, where reality mixed with fantasy, where space and time were torn apart into *regions*.
                                ⠀⠀Since the Seraph, human have fought their way to reunite its race and called themselves, **"United Regions of The Pralaeyr"**, later pointed their swords at the pit and the summit of Pralaeyr.
                                ⠀⠀"To fight the darkness of the fantasy and to free the human race from the Pralaeyr", firsts of the Remnants have sworn.
                                """,
                colour = discord.Colour(0xB1F1FA)
            )
            #**『How to understand?』**
            #**>** **`[..]`**: Compulsory argument **`{{..}}`**: Optional argument
            #**>** **`REQUIREMENTS`** are placed next to the command's name. These are not compulsory, but worth consideration when invoked.
            #**>** **`TAGS`** are placed at the very end.
            #**>** To inspect a command: `guide [command]`
            temball.set_thumbnail(url='https://imgur.com/EQsptpa.png')
            alk = random.choice(["https://imgur.com/D1Ld5A7.gif", "https://imgur.com/e8cIazx.gif"])
            temball.set_image(url=alk)
            temball.set_footer(text=f"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀")
            temb_socket.append(temball)

            tembs = [['P E R S O N A L  I N F O', {"profile": 'DM you your status', 'avatar': 'Display your avatar', 'incarnate': 'Create a character', 'rename': 'Renaming your character'}],
                    ['A C T I O N S', {'teleport': 'Teleport', 'use': 'Equip items. Consume items. Switch weapons slot', 'interact': 'Interact to NPCs'}],
                    ['I N F O R M A T I O N', {'works': 'View all jobs', 'maps': 'View all regions', 'formulas': 'Some model formulas for crafting', 'quests': 'View all quests available in region', 'npc': 'Show NPCs'}],
                    ['T R A N S F O R M I N G', {'evolve': 'Evolve/Upgrade your status', 'medication': 'Healing', 'wardrobe': 'Manipulating elements of your avatar card'}],
                    ['A C T I V I T I E S', {'daily': 'Daily cakes', 'work': 'Sign up for a job', 'rest': 'Resting for STA', 'wake': 'Waking from rest'}],
                    ['M A N I P U L A T I N G', {'infuse': 'Infusing two items', 'merge': 'Merging two items', 'craft': 'Crafting items'}],
                    ['L I F E', {'guild': '<GUILD> master command', 'bank': '<BANK> master command', 'quest': '<QUEST> master command', 'party': '<PARTY> master command', 'education': 'Learning a new degree', 'marry': 'Marry someone', 'divorce': 'Divorce your partner', 'like': 'Give merit', 'dislike': 'Decrease merit'}],
                    ['C O M M E R C I A L', {'shop': "View region's shop", 'buy': 'Buy items from shop', 'inventory': 'View your inventory', 'trader': 'View/Buy what the traders sell', 'sell': 'Sell items', 'give': 'Give money to a player'}],
                    ['C O M B A T', {'attack': 'Attack someone/something. Change pose', 'aim': 'Shoot someone/something. Change pose'}],
                    ['S T A T I S T I C S', {'sekaitime': 'View current time of Pralaeyr', 'worldinfo': 'Info of Pralaeyr', 'toprich': 'Top 10 richest', 'topmerit': 'Top 10 merit', 'topkill': 'Top 10 PVP', 'topdeath': 'Top 10 awkward deaths', 'topwin': 'Top 10 dueling winners'}],
                    ['T O O L S', {'radar': 'Scan map for players', 'mdist': 'Calculate distance'}]]
            for stuff in tembs:
                line = ''
                for k, v in stuff[1].items():
                    line = line + f"╔**`{k}`**\n╚╡{v}\n"
                tembeach = discord.Embed(
                    description = f"""
                    ```ini
[ {stuff[0]} ]```
    ━━━━━━━━━━━━━
                    {line}""",
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
        try: command, aliases, syntax, description, tags, requirement = await self.client.quefe(f"SELECT command, aliases, syntax, description, tags, requirement FROM sys_command WHERE command='{raw[0]}';")
        # E: No result. Instead try to search for familiar
        except TypeError:
            packs = await self.client.quefe(f"SELECT command FROM sys_command WHERE command LIKE '%{raw[0]}%' OR aliases LIKE '%{raw[0]}%';", type='all')
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
        try: concept, description, tags, typee = await self.client.quefe(f"SELECT concept, description, tags, type FROM sys_concept WHERE concept='{raw[0]}';")
        # E: No result. Instead try to search for familiar
        except TypeError:
            packs = await self.client.quefe(f"SELECT concept FROM sys_concept WHERE concept LIKE '%{raw[0]}%' OR tags LIKE '%{raw[0]}%';", type='all')
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

    # pylint: disable=unused-variable
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
                if await self.client._cursor.execute(f"SELECT * FROM cosmetic_preset WHERE user_id='{str(ctx.message.author.id)}' AND stats='CURRENT';") >= 3: await ctx.send(f"<:osit:544356212846886924> You cannot have more than three presets at a time, {str(ctx.message.author.id)}")

                await self.client._cursor.execute(f"INSERT INTO cosmetic_preset(user_id, name, stats, avatar_id, bg_code, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death) SELECT {str(ctx.message.author.id)}, '{pname}', 'PRESET', avatar_id, bg_code, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death FROM cosmetic_preset WHERE user_id='{str(ctx.message.author.id)}' AND stats='CURRENT';")

                await ctx.send(f":white_check_mark: Created preset **{pname}**. Use `-wardrobe presets` to check its *id*."); return

            elif raw[0] == 'delete':
                try:
                    if await self.client._cursor.execute(f"DELETE FROM cosmetic_preset WHERE preset_id='{raw[1]}' AND user_id='{ctx.author.id}' AND stats!='DEFAULT';") == 0:
                        await ctx.send("<:osit:544356212846886924> Preset's id not found!"); return
                # E: Preset's id not given
                except IndexError: await ctx.send("<:osit:544356212846886924> Please provide the id!"); return

                await ctx.send(f":white_check_mark: Preset id `{raw[1]}` was deleted."); return
            
            elif raw[0] == 'load':
                # GET preset
                try: 
                    if raw[1] == 'default':
                        avatar_id, bg_code, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death = await self.client.quefe(f"SELECT avatar_id, bg_code, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death FROM cosmetic_preset WHERE user_id='{str(ctx.message.author.id)}' AND stats='DEFAULT';")
                    else:
                        avatar_id, bg_code, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death = await self.client.quefe(f"SELECT avatar_id, bg_code, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death FROM cosmetic_preset WHERE user_id='{str(ctx.message.author.id)}' AND preset_id='{raw[1]}';")
                # E: Preset's id not found
                except (IndexError, TypeError): await ctx.send("<:osit:544356212846886924> Preset's id not found!"); return

                # UPDATE current
                await self.client._cursor.execute(f"UPDATE cosmetic_preset SET user_id='{str(ctx.message.author.id)}', name='current of {ctx.message.author.name}', stats='CURRENT', avatar_id='{avatar_id}', bg_code='{bg_code}', co_name='{co_name}', co_partner='{co_partner}', co_money='{co_money}', co_age='{co_age}', co_guild='{co_guild}', co_rank='{co_rank}', co_evo='{co_evo}', co_kill='{co_kill}', co_death='{co_death}' WHERE user_id='{str(ctx.message.author.id)}' AND stats='CURRENT';")
                await ctx.send(":white_check_mark: Preset's loaded!"); return
            
            elif raw[0] == 'presets':
                line = ""

                presets = await self.client.quefe(f"SELECT preset_id, name, avatar_id FROM cosmetic_preset WHERE user_id='{str(ctx.message.author.id)}' AND stats NOT IN ('DEFAULT', 'CURRENT');", type='all')

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
                        await self.client._cursor.execute(f"UPDATE cosmetic_preset SET {coattri[raw[0]]}='{raw[1]}' WHERE user_id='{str(ctx.message.author.id)}' AND stats='CURRENT';")
                        await ctx.send(f":white_check_mark: Attribute's colour was changed to **`{raw[1]}`**."); return
                    # E: Attributes not found
                    except KeyError: await ctx.send(f":moyai: Please use the following attributes: **`{'`** **`'.join(list(coattri.keys()))}`**"); return

                # AVATAR
                # E: Color not given
                except IndexError:
                    if raw[0].startswith('av'):
                        try:
                            if await self.client._cursor.execute(f"UPDATE cosmetic_preset SET avatar_id='{raw[0]}' WHERE user_id='{ctx.author.id}' AND stats='CURRENT' AND EXISTS (SELECT * FROM pi_avatars WHERE user_id='{ctx.author.id}' AND avatar_id='{raw[0]}');") == 0:
                                await ctx.send(f"<:osit:544356212846886924> You don't own this avatar, **{ctx.author.name}**!"); return
                            await ctx.send(f":white_check_mark: Changed to `{raw[0]}`"); return
                        except mysqlError.IntegrityError: await ctx.send(f"<:osit:544356212846886924> Avatar not found!"); return
                    else:
                        try: 
                            if await self.client._cursor.execute(f"UPDATE cosmetic_preset SET bg_code='{raw[0]}' WHERE user_id='{ctx.author.id}' AND stats='CURRENT' AND EXISTS (SELECT * FROM pi_backgrounds WHERE user_id='{ctx.author.id}' AND bg_code='{raw[0]}');") == 0:
                                await ctx.send(f"<:osit:544356212846886924> You don't own this avatar, **{ctx.author.name}**!"); return
                            await ctx.send(f":white_check_mark: Changed to `{raw[0]}`"); return
                        except mysqlError.IntegrityError: await ctx.send(f"<:osit:544356212846886924> Background not found!"); return

        # AVATARs
        # E: No avatar given
        except IndexError:
            line = ''

            async def browse():
                if not args:
                    items2 = await self.client.quefe(f"SELECT avatar_id FROM pi_avatars WHERE user_id='{ctx.author.id}';", type='all')
                    if not items2: await ctx.send(f":x: No result..."); return

                    items = []
                    for item in items2:
                        ava_id, name, description = await self.client.quefe(f"SELECT avatar_id, name, description FROM model_avatar WHERE avatar_id='{item[0]}';")
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
                    items2 = await self.client.quefe(f"SELECT bg_code FROM pi_backgrounds WHERE user_id='{ctx.author.id}';", type='all')
                    if not items2: await ctx.send(f":x: No result..."); return

                    items = []
                    for item in items2:
                        ava_id, name, description = await self.client.quefe(f"SELECT bg_code, name, description FROM model_background WHERE bg_code='{item[0]}';")
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
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        if not await self.__cd_check(ctx.message, cmd_tag, f"<:fufu:605255050289348620> Oops. It's not your birthday yet, **{ctx.author.name}**."): return

        await self.client._cursor.execute(f"SELECT func_ig_reward('{ctx.author.id}', 'ig77', 1);")
        await ctx.send(f":cake: Happy birthday! Here's a `ig77`|**Cake**!")
        await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.set, f'{cmd_tag}{ctx.author.id}', 'working', ex=86400, nx=True))

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def rename(self, ctx, *, name):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        
        if not name: await ctx.send("<:osit:544356212846886924> `rename [name]`"); return
        if len(name) > 21: await ctx.send("<:osit:544356212846886924> Names can only contain 21 characters."); return

        name = await self.utils.inj_filter(name)

        await self.client.quefe(f"UPDATE personal_info SET name='{name}' WHERE id='{ctx.author.id}';")
        await ctx.send(f":white_check_mark: Your name's changed to **{name}**.")

    @commands.command()
    @commands.cooldown(1, 2, type=BucketType.user)
    async def pralaeyr(self, ctx):
        await ctx.send("https://media.discordapp.net/attachments/381963689470984203/546796245994307595/map_description.png")

    @commands.command(aliases=['tut'])
    @commands.cooldown(1, 3, type=BucketType.user)
    async def tutorial(self, ctx, *args):

        #if args: await self.tut_basic_status(ctx, box=args[0])
        #else: await self.tut_basic_status(ctx)

        try:
            bundle = await self.client.quefe(f"SELECT line, timeout, trg, illulink FROM sys_tutorial WHERE tutorial_code='{args[0]}' ORDER BY ordera ASC;", type='all')
            if not bundle: await ctx.send(":x: Tutorial's id not found"); return
        except IndexError:
            await ctx.send("<:9_:544354429055533068> Please use `tutorial 1` or `tutorial 2`"); return
        #await ctx.send(f"{ctx.author.mention}, let's move to a more silent place like in DM!")
        for pack in bundle:
            try: trg = pack[2].split(' || ')
            except AttributeError: trg = []
            await self.engine_waitor(ctx, pack[0], t=pack[1], keylist=trg, DM=True, illulink=pack[3])





    # pylint: enable=unused-variable



# ================ KINGDOM =================

    @commands.command(aliases=['kingdom'])
    @commands.cooldown(1, 7, type=BucketType.user)
    async def land(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        raw = list(args)

        try:
            if raw[0] == 'create':
                # User's info
                cur_PLACE, money, merit = await self.client.quefe(f"SELECT cur_PLACE, money, merit FROM personal_info WHERE id='{ctx.author.id}';")

                if await self.client._cursor.execute(f"SELECT * FROM pi_land WHERE user_id='{ctx.author.id}' AND region='{cur_PLACE}';"): await ctx.send("<:osit:544356212846886924> You can only have 1 land per region"); return
                #try: money_lim = round(10000+(10000/(lands_quantity/10)))
                #except ZeroDivisionError: money_lim = 10000
                #merit_lim = 10*(lands_quantity+1)
                #if not merit_lim: merit_lim = 20
                money_lim = 10000
                merit_lim = 20

                # Region's info
                land_slot, r_biome, r_name = await self.client.quefe(f"SELECT land_slot, biome, name FROM environ WHERE environ_code='{cur_PLACE}';")

                # Checks
                if money < money_lim: await ctx.send(f":crown: You need at least **<:36pxGold:548661444133126185>{money_lim}** to found a land in `{cur_PLACE}`|**{r_name}**"); return
                elif merit < merit_lim: await ctx.send(f":crown: You need at least **{merit_lim} merits** to found a land in `{cur_PLACE}`|**{r_name}**"); return
                elif land_slot == 0: await ctx.send(f":crown: All slots are full in `{cur_PLACE}`|**{r_name}**. You may try to buy from other players."); return

                # Biome get
                biome = random.choice(r_biome.split(' - '))

                def UMCc_check(m):
                    return m.channel == ctx.channel and m.author == ctx.author

                # NAME
                msg = await ctx.send(":crown: Shall speak your wish, the name is asked?\n||<a:RingingBell:559282950190006282> Timeout=30s · Please give a name||")
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
                msg = await ctx.send(f":crown: This territory of yours, how would you rule?\n<a:RingingBell:559282950190006282> Timeout=30s || **May your choice be thorough**, reversion is unable: **`{'` · `'.join(govs.keys())}`**")
                try:
                    resp = await self.client.wait_for('message', timeout=30, check=UMCc_check2)
                    l_gov = resp.content.upper()
                    await msg.delete()
                except asyncio.TimeoutError:
                    l_gov = random.choice(govs.keys())
                    await msg.delete()

                def UMCc_check3(m):
                    return m.channel == ctx.channel and m.author == ctx.author and m.content == 'founding confirm'
                
                msg = await ctx.send(f":crown: Then **{l_name}** it is - a **{l_gov.capitalize()}** government - in the middle of `{biome.capitalize()}` biome.\n<a:RingingBell:559282950190006282> Proceed? (Key=`founding confirm`||Timeout=30s)")
                try:
                    resp = await self.client.wait_for('message', timeout=30, check=UMCc_check3)
                    await msg.delete()
                except asyncio.TimeoutError: 
                    await ctx.send(f":crown: Looks like you're not a decisive person heh? Come back later.")
                    await msg.delete(); return

                latest = await self.client.quefe(f"SELECT land_id FROM pi_land ORDER BY land_id DESC LIMIT 1;")

                await self.client._cursor.execute(f"INSERT INTO pi_land VALUES ({latest[0]+1}, 'land.{latest[0]+1}', '{ctx.author.id}', '{cur_PLACE}', '{biome}', '{l_name}', 'Property of {ctx.author.name}', '{l_gov}', 'lel', 1, 1, {money_lim}, 1000, {govs[l_gov][2]}, 1, 1, 1000, {govs[l_gov][0]}, {govs[l_gov][1]}, 1000, 0, 0, 0.01, 0.01, '', '', 'n/a', ''); UPDATE personal_info SET money=money-{money_lim} WHERE id='{ctx.author.id}'; INSERT INTO pi_tax VALUES ('land.{latest[0]+1}', 50, 50, 50, 50)")
                await ctx.send(':crown: Bless you on the road to glory...')
      
            elif raw[0] in ['chart', 'board']:
                cur_PLACE = await self.client.quefe(f"SELECT cur_PLACE FROM personal_info WHERE id='{ctx.author.id}';"); cur_PLACE = cur_PLACE[0]
                r_name, r_plprice = await self.client.quefe(f"SELECT name, plot_price FROM environ WHERE environ_code='{cur_PLACE}';")

                await ctx.trigger_typing()
                # Time
                taim = await self.client.loop.run_in_executor(None, self.utils.time_get)                  # year, month, day, hour, minute        

                resus = []
                for self.client._cursor in [-1, -2, -3, -4, -5]:
                    tatem = list(taim)
                    tatem[2] += self.client._cursor

                    resu = await self.utils.realty_calc(r_plprice, tatem, [-2, -1, 0, 1, 2])
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

            elif raw[0] == 'guard':
                try: hero_id, hero_name = await self.client.quefe(f"SELECT hero_id, name FROM pi_hero WHERE hero_id={raw[2]} AND user_id='{ctx.author.id}';")
                except TypeError: await ctx.send("<:osit:544356212846886924> Hero's id not found"); return
                except mysqlError.ProgrammingError: await ctx.send("<:osit:544356212846886924> Invalid hero's id!"); return

                if not await self.client._cursor.execute(f"UPDATE pi_land SET hero_id='{hero_id}' WHERE user_id='{ctx.author.id}' AND hero_id='n/a';"):
                    await self.client._cursor.execute(f"UPDATE pi_land SET hero_id='n/a' WHERE user_id='{ctx.author.id}' AND hero_id='{hero_id}';")
                    await ctx.send(f":crown: Resigned hero `{hero_id}`|**{hero_name}** from land `{raw[1]}`"); return
                await ctx.send(f":crown: Set hero `{hero_id}`|**{hero_name}** as land `{raw[1]}`'s guardian!"); return

            else:
                land_code = raw[0]

                if raw[1] == 'description':
                    try: desc = await self.utils.inj_filter(' '.join(raw[2:18]))
                    except IndexError: await ctx.send("<:osit:544356212846886924> Missing content of description!"); return

                    if not await self.client._cursor.execute(f"UPDATE pi_land SET description='{desc}' WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';"):
                        await ctx.send(f"<:osit:544356212846886924> You don't own this land, **{ctx.author.name}**"); return
                    await ctx.send(":white_check_mark: Done")

                elif raw[1] == 'currency':
                    try: currency = await self.utils.inj_filter(' '.join(raw[2:6]))
                    except IndexError: await ctx.send("<:osit:544356212846886924> Missing currency name!"); return

                    if not await self.client._cursor.execute(f"UPDATE pi_land SET currency='{currency}' WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';"):
                        await ctx.send(f"<:osit:544356212846886924> You don't own this land, **{ctx.author.name}**"); return
                    await ctx.send(":white_check_mark: Done")

                elif raw[1] in ['image', 'illustration']:
                    try:
                        illulink = await self.utils.illulink_check(' '.join(raw[2:]))
                        if not illulink: await ctx.send("<:osit:544356212846886924> Invalid link!"); return
                    except IndexError: await ctx.send("<:osit:544356212846886924> Missing link!"); return

                    if not await self.client._cursor.execute(f"UPDATE pi_land SET illulink='{illulink}' WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';"):
                        await ctx.send(f"<:osit:544356212846886924> You don't own this land, **{ctx.author.name}**"); return
                    await ctx.send(":white_check_mark: Done")

                elif raw[1] == 'shop':
                    # Land info
                    try: l_goods, l_region, l_name = await self.client.quefe(f"SELECT goods, region, name FROM pi_land WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';")
                    except TypeError: await ctx.send(f"<:osit:544356212846886924> You don't own this land, **{ctx.author.name}**"); return
                    
                    # Region info
                    goods, name = await self.client.quefe(f"SELECT goods, name FROM environ WHERE environ_code='{l_region}';")
                    l_goods = l_goods.split(' - ')
                    try: l_goods = l_goods.remove('')
                    except ValueError: pass

                    try:
                        if raw[2] not in goods.split(' - '): await ctx.send(f"<:osit:544356212846886924> The anchoring region - `{l_region}`|**{name}** - only accepts **`{goods.replace(' - ', '` · `')}`**"); return
                    except IndexError: await ctx.send(f"<:osit:544356212846886924> Missing item's code"); return

                    if not l_goods: l_goods = []

                    if raw[2] in l_goods:
                        l_goods.remove(raw[2])
                        await self.client._cursor.execute(f"UPDATE pi_land SET goods='{' - '.join(l_goods)}' WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';;")
                        await ctx.send(f":crown: Removed `{raw[2]}` from shops in `{land_code}`|**{l_name}**"); return
                    else:
                        l_goods.append(raw[2])
                        await self.client._cursor.execute(f"UPDATE pi_land SET goods='{' - '.join(l_goods)}' WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';;")
                        await ctx.send(f":crown: Added `{raw[2]}` to shops in `{land_code}`|**{l_name}**"); return

                elif raw[1] == 'trader':
                    # Land info
                    try: l_cuisine, l_region, l_name = await self.client.quefe(f"SELECT cuisine, region, name FROM pi_land WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';")
                    except TypeError: await ctx.send(f"<:osit:544356212846886924> You don't own this land, **{ctx.author.name}**"); return
                    
                    # Region info
                    cuisine, name = await self.client.quefe(f"SELECT cuisine, name FROM environ WHERE environ_code='{l_region}';")
                    l_cuisine = l_cuisine.split(' - ')
                    try: l_cuisine = l_cuisine.remove('')
                    except ValueError: pass

                    try:
                        if raw[2] not in cuisine.split(' - '): await ctx.send(f"<:osit:544356212846886924> The anchoring region - `{l_region}`|**{name}** - only accepts **`{cuisine.replace(' - ', '` · `')}`**"); return
                    except IndexError: await ctx.send(f"<:osit:544356212846886924> Missing item's code"); return

                    if not l_cuisine: l_cuisine = []

                    if raw[2] in l_cuisine:
                        l_cuisine.remove(raw[2])
                        await self.client._cursor.execute(f"UPDATE pi_land SET cuisine='{' - '.join(l_cuisine)}' WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';;")
                        await ctx.send(f":crown: Removed `{raw[2]}` from traders in `{land_code}`|**{l_name}**"); return
                    else:
                        l_cuisine.append(raw[2])
                        await self.client._cursor.execute(f"UPDATE pi_land SET cuisine='{' - '.join(l_cuisine)}' WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';;")
                        await ctx.send(f":crown: Added `{raw[2]}` to traders in `{land_code}`|**{l_name}**"); return


        except IndexError:
            try: region = f"AND region='{args[0]}'"
            except IndexError: region = ''

            # TAXXXXXXXXXXX
            await self.client._cursor.execute(f"UPDATE pi_land pl INNER JOIN pi_tax px ON px.land_code=pl.land_code SET pl.treasury=pl.treasury+pl.GDP/100*px.tax_treasury*(SELECT DATEDIFF(NOW(), px.last_point)), pl.resource=pl.resource+pl.GDP/100*px.tax_resource*(SELECT DATEDIFF(NOW(), px.last_point)), pl.v_HAPPY=pl.v_HAPPY+pl.GDE/100*px.tax_HAPPY*(SELECT DATEDIFF(NOW(), px.last_point)), pl.faith=pl.faith+pl.GDE/100*px.tax_faith*(SELECT DATEDIFF(NOW(), px.last_point)), px.last_point=NOW() WHERE pl.user_id='{ctx.author.id}'")

            lands = await self.client.quefe(f"SELECT land_code, name, description, biome, region, currency, government, population, treasury, resource, faith, v_plot, v_plot_total, v_productive, v_HAPPY, v_HEALTH, v_CULTURE, illulink, border_X, border_Y, GDP, GDE, hero_id FROM pi_land WHERE user_id='{ctx.author.id}' {region};", type='all')

            if not lands: await ctx.send(":crown: You have no lands :>")

            def makeembed(curp, pages, currentpage):
                land = lands[curp]

                reembed = discord.Embed(title = f":crown: `{land[6]}` · `{land[0]}` | **{land[1].capitalize()}**", description = f"""```dsconfig
        {land[2]}```""", colour = discord.Colour(0x011C3A))
                reembed.add_field(name=":scales: Property", value=f"╟`Region` · **{land[4]}**\n╟`Population` · **{land[7]}**\n╟`Plots` · {land[11]}/**{land[12]}**\n╟`Area` · **`{land[18]:.2f} x {land[19]:.2f}`**\n╟`Guardian` · **{land[22]}**")
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
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        # User's info
        cur_PLACE = await self.client.quefe(f"SELECT cur_PLACE FROM personal_info WHERE id='{ctx.author.id}';")

        # Info
        total_lands = await self.client._cursor.execute(f"SELECT * FROM pi_land WHERE user_id='{ctx.author.id}';")
        lands = await self.client._cursor.execute(f"SELECT * FROM pi_land WHERE user_id='{ctx.author.id}' AND region='{cur_PLACE[0]}';")
        dem = await self.client._cursor.execute(f"SELECT * FROM pi_land WHERE user_id='{ctx.author.id}' AND government='DEMOCRACY';")
        fas = await self.client._cursor.execute(f"SELECT * FROM pi_land WHERE user_id='{ctx.author.id}' AND government='FASCISM';")
        com = await self.client._cursor.execute(f"SELECT * FROM pi_land WHERE user_id='{ctx.author.id}' AND government='COMMUNISM';")

        await ctx.send(f":crown: **{ctx.author.name.upper()}**'s\n════╦═════════════\n**Local**  ║  **{lands}**  lands\n**Total**  ║  **{total_lands}**  lands\n`DEMOCRACY`  ║   **{dem}**  lands\n`FASCISM`      ║   **{fas}**  lands\n`COMMUNISM`  ║   **{com}**  lands\n═══════╩══════════", delete_after=20)

    @commands.command()
    @commands.cooldown(1, 300, type=BucketType.user)
    async def expand(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        raw = list(args)

        # User's info
        charm = await self.client.quefe(f"SELECT charm FROM personal_info WHERE id='{ctx.author.id}';")

        # Land's info
        try: gov, plot_total, treasury, name, resource, region = await self.client.quefe(f"SELECT government, v_plot_total, treasury, name, resource, region FROM pi_land WHERE user_id='{ctx.author.id}' AND land_code='{raw[0]}';")
        except IndexError: await ctx.send("<:osit:544356212846886924> Missing land's code"); return
        except TypeError: await ctx.send(f"<:osit:544356212846886924> You don't own this land, {ctx.author.name}"); return
        
        # Get init price
        init_price = await self.client.quefe(f"SELECT plot_price FROM environ WHERE environ_code='{region}';")
        temppr = init_price[0]

        # Quantity control
        try: quantity = int(raw[1])
        except (IndexError, ValueError): quantity = 1

        # Time
        taim = await self.client.loop.run_in_executor(None, self.utils.time_get)                  # year, month, day, hour, minute

        # Preparing
        if gov != 'FASCISM': init_price = init_price[0] + (10 * plot_total - 10 * charm[0])
        else: init_price = init_price[0]
        final_price = await self.utils.realty_calc(init_price, taim, [-2, -1, 0, 1, 2])
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
        await self.client._cursor.execute(f"UPDATE pi_land SET v_plot=v_plot+{quantity}, v_plot_total=v_plot_total+{quantity}, treasury=treasury-{final_price}, resource=resource+{resource}, {border}={border}+{0.01*quantity} WHERE land_code='{raw[0]}' AND user_id='{ctx.author.id}'; UPDATE environ SET land_slot=land_slot-{quantity} WHERE environ_code='{region}';")

    @commands.command()
    @commands.cooldown(1, 600, type=BucketType.user)
    async def shrink(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        raw = list(args)

        # Land's info
        try: gov, name, resource, region = await self.client.quefe(f"SELECT government, name, resource, region FROM pi_land WHERE user_id='{ctx.author.id}' AND land_code='{raw[0]}';")
        except ValueError: await ctx.send("<:osit:544356212846886924> Invalid land's id"); return
        except IndexError: await ctx.send("<:osit:544356212846886924> Missing land's id"); return
        except TypeError: await ctx.send(f"<:osit:544356212846886924> You don't own this land, {ctx.author.name}"); return
        
        # Get init price
        init_price = await self.client.quefe(f"SELECT plot_price FROM environ WHERE environ_code='{region}';")
        temppr = init_price[0]

        # Quantity control
        try: quantity = int(raw[1])
        except (IndexError, ValueError): quantity = 1

        # Time
        taim = await self.client.loop.run_in_executor(None, self.utils.time_get)                  # year, month, day, hour, minute

        # Preparing
        init_price = init_price[0]
        final_price = await self.utils.realty_calc(init_price, taim, [-2, -1, 0, 1, 2])
        final_price *= quantity
        if gov == 'DEMOCRACY': resource = round(resource/5)
        else: resource = round(resource/10)

        # NAME
        await ctx.send(f":crown: Selling **{quantity}** plots in `{raw[0]}`|**{name}** of `{region}`:\n╟`Original price` · <:36pxGold:548661444133126185> **{temppr}**/plot\n=====================\n╟`Receive` · <:36pxGold:548661444133126185> **{final_price}**\n╟`Resource lost` · {resource}")

        await self.client._cursor.execute(f"UPDATE pi_land SET v_plot=v_plot-{quantity}, v_plot_total=v_plot_total-{quantity}, treasury=treasury-{final_price}, resource=resource-{resource} WHERE land_code='{raw[0]}' AND user_id='{ctx.author.id}'; UPDATE environ SET land_slot=land_slot-{quantity} WHERE environ_code='{region}';")



    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def unit(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        raw = list(args)

        # ADJUSTING
        try:
            try: unit_id = int(raw[0])
            except ValueError: land_cq = f" AND land_code='{args[0]}'"; raise IndexError
            except IndexError: land_cq = ''; raise IndexError

            if raw[1] == 'description':
                try: desc = await self.utils.inj_filter(' '.join(raw[2:18]))
                except IndexError: await ctx.send("<:osit:544356212846886924> Missing content of description!"); return

                if not await self.client._cursor.execute(f"UPDATE pi_unit SET description='{desc}' WHERE unit_id={unit_id} AND land_code IN (SELECT land_code FROM pi_land WHERE user_id='{ctx.author.id}');"):
                    await ctx.send(f"<:osit:544356212846886924> You don't own this land, **{ctx.author.name}**"); return
                await ctx.send(":white_check_mark: Done")

            elif raw[1] == 'name':
                try: name = await self.utils.inj_filter(' '.join(raw[2:6]))
                except IndexError: await ctx.send("<:osit:544356212846886924> Missing unit's name!"); return

                if not await self.client._cursor.execute(f"UPDATE pi_unit SET name='{name}' WHERE unit_id={unit_id} AND land_code IN (SELECT land_code FROM pi_land WHERE user_id='{ctx.author.id}');"):
                    await ctx.send(f"<:osit:544356212846886924> You don't own this land, **{ctx.author.name}**"); return
                await ctx.send(":white_check_mark: Done")

            elif raw[1] in ['image', 'illustration']:
                try:
                    illulink = await self.utils.illulink_check(' '.join(raw[2:]))
                    if not illulink: await ctx.send("<:osit:544356212846886924> Invalid link!"); return
                except IndexError: await ctx.send("<:osit:544356212846886924> Missing link!"); return

                if not await self.client._cursor.execute(f"UPDATE pi_unit SET illulink='{illulink}' WHERE unit_id={unit_id} AND land_code IN (SELECT land_code FROM pi_land WHERE user_id='{ctx.author.id}');"):
                    await ctx.send(f"<:osit:544356212846886924> You don't own this land, **{ctx.author.name}**"); return
                await ctx.send(":white_check_mark: Done")
        
        # ALL UNIT
        except IndexError:
            # Land check
            lands = await self.client.quefe(f"SELECT land_code, name FROM pi_land WHERE user_id='{ctx.author.id}' {land_cq};", type='all')

            troops = []
            for land in lands:
                troops.append(await self.client.quefe(f"SELECT v_treasury, v_resource, v_faith, unit_id, name, description, entity, str, intt, sta, speed, stealth, as_NAVAL, as_AIR, as_LAND, as_MIRACLE, as_FAITH, as_ARCH, as_BIO, as_TECH, illulink, '{land[0]}', '{land[1]}', max_sta FROM pi_unit WHERE land_code='{land[0]}';", type='all'))
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

    @commands.command(aliases=['units'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def wikiunit(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        troops = await self.client.quefe(f"SELECT v_treasury, v_resource, v_faith, unit_code, name, description, entity, str, intt, sta, speed, stealth, as_NAVAL, as_AIR, as_LAND, as_MIRACLE, as_FAITH, as_ARCH, as_BIO, as_TECH, illulink FROM model_unit;", type='all')

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
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        
        # UNIT info
        try: u1_id = int(args[0])
        except IndexError: await ctx.send("<:osit:544356212846886924> Missing *first* unit's id"); return
        except ValueError: await ctx.send("<:osit:544356212846886924> Invalid unit's id!"); return

        try: u2_id = int(args[1])
        except IndexError: await ctx.send("<:osit:544356212846886924> Missing *second* unit's id"); return
        except ValueError: await ctx.send("<:osit:544356212846886924> Invalid unit's id!"); return

        # LAND list
        lands = await self.client.quefe(f"SELECT land_code FROM pi_land WHERE user_id='{ctx.author.id}';", type='all')
        try: lands = lands[0]
        except IndexError: await ctx.send("<:osit:544356212846886924> You have no land"); return
        lands_1 = "', '".join(lands)
        lands_2 = f" AND m.land_code IN ({lands_1})"
        lands_1 = f" AND p.land_code IN ({lands_1})"

        def UMCc_check(m):
            return m.channel == ctx.channel and m.author == ctx.author and m.content == 'union confirm'

        # NAME
        await ctx.send(f":crown: {ctx.author.mention} requrest to union unit `{u2_id}` to unit `{u1_id}`, which will disband the prior. Proceed?\n||<a:RingingBell:559282950190006282> Timeout=15s · Key=`union confirm`||")
        try: 
            await self.client.wait_for('message', timeout=15, check=UMCc_check)
        except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request times out!"); return


        # UNION
        a = await self.client._cursor.execute(f"""UPDATE pi_unit p INNER JOIN pi_unit m ON m.unit_id={u2_id} {lands_2}
                                        SET p.entity=p.entity+quantity_in*m.entity, p.max_entity=p.max_entity+quantity_in*m.entity, p.evo=p.evo+m.evo, p.str=p.str+m.str, p.intt=p.intt+m.intt, p.sta=p.sta+m.sta, p.speed=p.speed+m.speed, p.stealth=p.stealth+m.stealth, p.as_NAVAL=p.as_NAVAL+m.as_NAVAL, p.as_AIR=p.as_AIR+m.as_AIR, p.as_LAND=p.as_LAND+m.as_LAND, p.as_MIRACLE=p.as_MIRACLE+m.as_MIRACLE, p.as_FAITH=p.as_FAITH+m.as_FAITH, p.as_ARCH=p.as_ARCH+m.as_ARCH, p.as_BIO=p.as_BIO+m.as_BIO, p.as_TECH=p.as_TECH+m.as_TECH, p.v_treasury=p.v_treasury+m.v_treasury, p.v_resource=p.v_resource+m.v_resource, p.v_faith=p.v_faith+m.v_faith, p.v_plot=p.v_plot+m.v_plot
                                        WHERE p.unit_id={u1_id} {lands_1};""")

        if not a: await ctx.send("<:osit:544356212846886924> You don't own one of those units!"); return

        await self.client._cursor.execute(f"DELETE FROM pi_unit WHERE unit_id={u2_id};")

        await ctx.send(":crown: The deed is done. Result can be checked!")

    @commands.command()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def order(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        raw = list(args)

        # ============ INFO GET =============
        ## ITEM ======
        try:
            __swi = 'id'
            try: i_name, item_code, i_quantity, i_tags, i_id = await self.client.quefe(f"SELECT name, item_code, quantity, tags, item_id FROM pi_inventory WHERE existence='GOOD' AND user_id='{ctx.author.id}' AND item_id={int(raw[1])} AND quantity>0;")
            except ValueError: i_name, item_code, i_quantity, i_tags, i_id = await self.client.quefe(f"SELECT name, item_code, quantity, tags, item_id FROM pi_inventory WHERE existence='GOOD' AND user_id='{ctx.author.id}' AND item_code='{raw[1]}' AND quantity>0;")
        except IndexError: await ctx.send(f":crown: Please provide `item_id`, **{ctx.author.name}**."); return
        except TypeError:
            ## INFRASTRUCTURE ======
            if raw[1].startswith('u'):
                try:
                    i_name, item_code, i_quantity, i_tags = await self.client.quefe(f"SELECT name, unit_code, entity, tags FROM model_unit WHERE unit_code='{raw[1]}';")
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
        try: o_itc, description, o_urc, o_itq, o_urintt, o_ursta, o_urasp, o_enr, o_lpl, o_lbre, o_lpol, o_ltr, o_lres, o_lfa, o_dura, o_re, o_req = await self.client.quefe(f"SELECT item_code, description, unit_required_code, item_quantity, unit_required_intt, unit_required_sta, unit_required_aspect, entity_required, land_plot, land_biome_restricted, land_pollution, land_treasury, land_resource, land_faith, duration, reward, reward_query FROM model_order WHERE item_code='{item_code}' AND item_quantity={quantity};")
        except TypeError: await ctx.send(f"<:osit:544356212846886924> You tried giving {quantity} `{item_code}`|**{i_name}** to them, but nothing happened..."); return

        # Unit's info       ||      For checking entity, intt, asp...
        try: land_code, u_name, entity, intt, asp, u_sta = await self.client.quefe(f"SELECT land_code, name, entity, intt, {o_urasp}, sta FROM pi_unit WHERE unit_id={raw[0]};")
        except ValueError: await ctx.send(f"<:osit:544356212846886924> Invalid `unit's id`!"); return
        except TypeError: await ctx.send(f":crown: You don't own this unit, **{ctx.author.name}**!"); return
        except IndexError: await ctx.send(f":crown: Please provide `unit's id`, **{ctx.author.name}**."); return

        # Land's info
        try: l_biome, l_name, l_plot, l_productive, l_HAPPY, l_HEALTH, l_CULTURE, l_gov, l_treasury, l_resource, l_faith, currency = await self.client.quefe(f"SELECT biome, name, v_plot, v_productive, v_HAPPY, v_HEALTH, v_CULTURE, government, treasury, resource, faith, currency FROM pi_land WHERE land_code='{land_code}' AND user_id='{ctx.author.id}';")
        except TypeError: await ctx.send(f":crown: You don't own this unit, **{ctx.author.name}**!"); return

        # Unit_required's info      ||      Mainly for checking entity_quantity
        if o_urc == 'n/a':
            uu_rq = 0
            uu_name = 'n/a'
            uu_id = 0
        else:
            try: uu_rq, uu_name, uu_id = await self.client.quefe(f"SELECT entity, name, unit_id FROM pi_unit WHERE land_code='{land_code}' AND unit_code='{o_urc}';")
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
            xtra = ''
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
        await self.client._cursor.execute(cost_query)

    @commands.command()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def orders(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        land_dict = {}
        lands = await self.client.quefe(f"SELECT land_code, name FROM pi_land WHERE user_id='{ctx.author.id}';", type='all')
        if not lands: await ctx.send(f"<:osit:544356212846886924> You have no land, **{ctx.author.name}**"); return
        for land in lands:
            land_dict[f"{land[0]}"] = land[1]

        orders = await self.client.quefe(f"""SELECT order_id, unit_id, land_code, description, end_point FROM pi_order WHERE land_code IN ('{"' '".join(land_dict.keys())}');""", type='all')

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

        # pylint disable=unused-variable
        emli = []
        for curp in range(pages):
            myembed = makeembed(currentpage*4-4, currentpage*4, pages, currentpage)
            emli.append(myembed)
            currentpage += 1
        # pylint enable=unused-variable

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
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        # Order's info
        try: 
            end_point, rewards, reward_query, land_code, description = await self.client.quefe(f"SELECT end_point, rewards, reward_query, land_code, description FROM pi_order WHERE order_id={int(args[0])};")
        except ValueError: await ctx.send("<:osit:544356212846886924> Invalid `order_id`!"); return
        except IndexError: await ctx.send("<:osit:544356212846886924> Missing `order_id`"); return
        except TypeError: await ctx.send("<:osit:544356212846886924> Order's not found!"); return

        # Order's check
        if await self.client._cursor.execute(f"SELECT * FROM pi_land WHERE user_id='{ctx.author.id}' AND land_code='{land_code}';") == 0: await ctx.send("<:osit:544356212846886924> Order's not found!"); return

        delta = relativedelta(end_point, datetime.now())
        if datetime.now() < end_point: await ctx.send(f":cowboy: *{description}* **`{delta.hours:02d}:{delta.minutes:02d}:{delta.seconds:02d}`** to go!"); return

        await ctx.send(f":crown: **Order's done!** You've received...\n{rewards}", delete_after=20)

        await self.client._cursor.execute(f"{reward_query} DELETE FROM pi_order WHERE order_id={args[0]}")


    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def tax(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
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
            if await self.client._cursor.execute(f"UPDATE pi_tax SET {sec[args[1]][0]}={args[2]}, {sec[args[1]][1]}=100-{args[2]} WHERE land_code='{land_code}' AND EXISTS (SELECT * FROM pi_land WHERE land_code='{land_code}');") == 0:
                await ctx.send(f"<:osit:544356212846886924> You don't own this land, **{ctx.author.name}**"); return
            await ctx.send(f":crown: **{args[1].capitalize()} tax** is set to **{args[2]}%**, and also changes **{sec[args[1]][2].capitalize()} tax**.")
        
        # Tax board
        except IndexError:
            # TAX info
            taxes = await self.client.quefe(f"SELECT land_code, tax_treasury, tax_resource, tax_HAPPY, tax_faith FROM pi_tax WHERE land_code IN (SELECT land_code FROM pi_land WHERE user_id='{ctx.author.id}');", type='all')
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


    @commands.command(aliases=['cmd'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def command(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        # UNIT info
        try: entity, strr, intt, sta, max_sta, speed, stealth, as_NAVAL, as_AIR, as_LAND, as_MIRACLE, name = await self.client.quefe(f"SELECT entity, str, intt, sta, max_sta, speed, stealth, as_NAVAL, as_AIR, as_LAND, as_MIRACLE, name FROM pi_unit WHERE unit_id='{args[0]}' AND land_code IN (SELECT land_code FROM pi_land WHERE user_id='{ctx.author.id}') AND sta >= max_sta/10;")
        except mysqlError.ProgrammingError: await ctx.send("<:osit:544356212846886924> You have no land"); return
        except TypeError: await ctx.send("<:osit:544356212846886924> The unit needs its stamina at 10% of max"); return
        except IndexError: await ctx.send("<:osit:544356212846886924> Command who? You're missing your unit's id!"); return

        try:
            if args[1] != 'attack': return
        except IndexError: await ctx.send("<:__:544354428338044929> What is it, m'lord?"); return

        # UNIT TARGET info
        try: t_entity, t_strr, t_intt, t_speed, t_stealth, t_as_NAVAL, t_as_AIR, t_as_LAND, t_as_MIRACLE, t_name, t_land_code, t_biome = await self.client.quefe(f"SELECT entity, str, intt, speed, stealth, as_NAVAL, as_AIR, as_LAND, as_MIRACLE, name, land_code AS lc, (SELECT biome FROM pi_land WHERE land_code=lc) FROM pi_unit WHERE unit_id='{args[2]}' AND entity > 0;")
        except mysqlError.ProgrammingError: await ctx.send("<:osit:544356212846886924> You have no land"); return t_land_code
        except TypeError: await ctx.send("<:osit:544356212846886924> Unit does not exist here"); return   

        # DMG CALC ========================

        biomate = {'SAVANNA': [as_LAND, t_as_LAND], 'JUNGLE': [as_MIRACLE, t_as_MIRACLE], 'RUIN': [as_AIR, t_as_LAND], 'DESERT': [as_AIR, t_as_MIRACLE], 'OCEAN': [as_NAVAL, t_as_NAVAL], 'MOUNTAIN': [as_LAND, as_AIR], 'FROST': [as_AIR, as_NAVAL], 'VOLCANUS': [as_MIRACLE, t_as_AIR]}

        ### PLAYER
        if intt < 0:
            if await self.utils.percenter(abs(intt)): raw_dmg = int(strr * entity / 10)
            else: raw_dmg = strr * entity
        else:
            if await self.utils.percenter(abs(intt)): raw_dmg = strr * entity * 10
            else: raw_dmg = strr * entity

        if not await self.utils.percenter(stealth):
            raw_dmg += raw_dmg * speed
            raw_dmg += raw_dmg * (biomate[t_biome][0] - biomate[t_biome][1])

        ### OPPO
        if t_intt < 0:
            if await self.utils.percenter(abs(t_intt)): t_raw_dmg = int(t_strr * t_entity / 10)
            else: t_raw_dmg = t_strr * t_entity
        else:
            if await self.utils.percenter(abs(t_intt)): t_raw_dmg = t_strr * t_entity * 10
            else: t_raw_dmg = t_strr * t_entity

        if not await self.utils.percenter(t_stealth):
            t_raw_dmg += t_raw_dmg * t_speed
            t_raw_dmg += t_raw_dmg * (biomate[t_biome][1] - biomate[t_biome][0])

        # WIN CALC =========================
        el = entity - t_raw_dmg
        t_el = t_entity - raw_dmg

        await self.client._cursor.execute(f"UPDATE pi_unit SET entity=IF(unit_id='{args[0]}', {el}, {t_el}), sta=IF(unit_id='{args[0]}', {sta - int(max_sta/10)}, {t_el}) WHERE unit_id IN ({args[0]}, {args[2]});")
        msg = await ctx.send(f"<a:WindFlag_SMALL:543592541929472010> Under the name of our lord - **{ctx.author.name}**"); await asyncio.sleep(1.5)
        await msg.edit(content="<a:WindFlag_SMALL:543592541929472010> Point our swords to the enemy!"); await asyncio.sleep(1.5)
        await msg.edit(content="<a:WindFlag_SMALL:543592541929472010> **UUUUU-RRRAAAAAAAAAAAAA-!**"); await asyncio.sleep(1.5)
        await msg.edit(content=f"<a:WindFlag_SMALL:543592541929472010> `{args[0]}`|**{name}** dealt **{raw_dmg} DMG** to `{args[0]}`|**{name}** and received **{t_raw_dmg} DMG**.\n╟ `{args[0]}`|**{name}** · `{el} troops`\n╟ `{args[2]}`|**{t_name}** · `{t_el} troops`\n||`━━━ There is no winner in war ━━━`||")

        #try:
        #    hit = t_entity/raw_dmg
        #    if hit < 0: hit = 0
        #except ZeroDivisionError: hit = 0

        #try:
        #    t_hit = entity/t_raw_dmg
        #    if hit < 0: t_hit = 0
        #except ZeroDivisionError: t_hit = 0

        
        






# ================ HERO CARD =================  

    @commands.command(aliases=['wikicard'])
    @commands.cooldown(1, 4, type=BucketType.user)
    async def wikihero(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        # ALL, with search
        try:
            if args[0] == 'search':
                ks = await self.utils.inj_filter(args[0])
                try: heros = await self.client.quefe(f"SELECT hero_code, name, illulink WHERE hero_code='{ks}' OR name LIKE '%{ks}%' FROM model_hero;", type='all')
                except IndexError: await ctx.send("<:osit:544356212846886924> Missing searching key"); return

                def makeembed(curp, pages, currentpage):
                    hero = heros[curp]

                    reembed = discord.Embed(title=f"━━━ `{hero[0]}` | **{hero[1]}** ━━━", color=0x36393E) #description=f"```{description}```"
                    reembed.set_image(url=hero[2])

                    return reembed

                async def attachreaction(msg):
                    await msg.add_reaction("\U000023ee")    #Top-left
                    await msg.add_reaction("\U00002b05")    #Left
                    await msg.add_reaction("\U000027a1")    #Right
                    await msg.add_reaction("\U000023ed")    #Top-right

                pages = len(heros)
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

        # ALL, with NO search
        except IndexError:
            if not args:
                heros = await self.client.quefe(f"SELECT hero_code, name, illulink FROM model_hero;", type='all')

                def makeembed(curp, pages, currentpage):
                    hero = heros[curp]

                    reembed = discord.Embed(title=f"━━━ `{hero[0]}` | **{hero[1]}** ━━━", color=0x36393E) #description=f"```{description}```"
                    reembed.set_image(url=hero[2])

                    return reembed

                async def attachreaction(msg):
                    await msg.add_reaction("\U000023ee")    #Top-left
                    await msg.add_reaction("\U00002b05")    #Left
                    await msg.add_reaction("\U000027a1")    #Right
                    await msg.add_reaction("\U000023ed")    #Top-right

                pages = len(heros)
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

        # SPECIFIC, with search
        try: hero_code, name, illulink = await self.client.quefe(f"SELECT hero_code, name, illulink FROM model_hero WHERE hero_code='{args[0]}' OR name LIKE '%{args[0]}%' LIMIT 1;")
        except TypeError: await ctx.send(f"<:osit:544356212846886924> Hero not found!"); return
        except IndexError: await ctx.send("<:osit:544356212846886924> Missing hero's code or name"); return

        temb = discord.Embed(title=f"━━━ `{hero_code}` | **{name}** ━━━", color=0x36393E) #description=f"```{description}```"
        temb.set_image(url=illulink)

        await ctx.send(embed=temb)

    @commands.command()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def summon(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        # CAKE check
        if await self.client._cursor.execute(f"SELECT * FROM pi_inventory WHERE user_id='214128381762076672' AND item_code='ig77' AND existence='GOOD' AND quantity>=3;") == 0: await ctx.send("<a:yy32:555244228217798673> The ritual to summon heroes requires... a `ig77`|**Cake**"); return
        await self.client._cursor.execute(f"SELECT func_i_delete('{ctx.author.id}', 'ig77', 1);")
        #hero_code, rare_rate, name = await self.client.quefe(f"SELECT hero_code, rare_rate, name FROM model_hero AS r1 JOIN (SELECT CEIL(RAND() * (SELECT MAX(counter) FROM model_hero)) AS counter) AS r2 WHERE r1.counter >= r2.counter ORDER BY r1.counter ASC LIMIT 1")
        bundle = await self.client.quefe(f"SELECT hero_code, rare_rate, name FROM model_hero", type='all')
        hero_code, rare_rate, name = random.choice(bundle)
        if await self.utils.percenter(rare_rate, total=100):
            lines = ['<a:yy32:555244228217798673> The alighted wind, them comes a wall. \n⠀⠀⠀⠀Four cardinal gates close, thus from the crown, comes three-forked road that leads to Seraph.',
                    "<a:yy32:555244228217798673> Let silver and steel be the essence.\n⠀⠀⠀⠀Let stone and the archduke of contracts be this foundation. \n⠀⠀⠀⠀⠀⠀Let the moment be declared; thy flesh shall bonded within thee, and fate shall be with thy sword.",
                    f"<a:yy32:555244228217798673> Shall thy oath weilded by thee, shall thy will be reckoned by thee - utter guardian of the Olds, \n⠀⠀⠀⠀⠀⠀crush the Chaos and come forth to Pralaeyr, \n⠀⠀⠀⠀⠀⠀⠀⠀**{name.capitalize()}**!"]
            
            msg = await ctx.send(lines[0])
            for line in lines[1:]:
                await asyncio.sleep(10); await msg.edit(content=line)

            await self.client._cursor.execute(f"SET @p0='{ctx.author.id}'; SET @p1='{hero_code}'; SELECT `func_hr_reward`(@p0, @p1) AS `func_hr_reward`;")

        else: await asyncio.sleep(5); await ctx.send(f"<a:yy32:555244228217798673> Ritual failed...")

    @commands.command(aliases=['card'])
    @commands.cooldown(1, 4, type=BucketType.user)
    async def collection(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        # ALL, with search
        try:
            if args[0] == 'search':
                ks = await self.utils.inj_filter(args[1])
                try: heros = await self.client.quefe(f"SELECT hero_id, name, illulink WHERE hero_code='{ks}' OR name LIKE '%{ks}%' OR hero_id='{ks}' FROM pi_hero WHERE user_id='{ctx.author.id}' AND existence='GOOD';", type='all')
                except IndexError: await ctx.send("<:osit:544356212846886924> Missing searching key"); return
                pages = len(heros)

                def makeembed(curp, pages, currentpage):
                    hero = heros[curp]

                    reembed = discord.Embed(title=f"━━━ `{hero[0]}` | **{hero[1]}** ━━━", color=0x36393E) #description=f"```{description}```"
                    reembed.set_image(url=hero[2])
                    reembed.set_author(name=f"{ctx.author.name} | {curp+1}·{pages}", icon_url=ctx.author.avatar_url)

                    return reembed

                async def attachreaction(msg):
                    await msg.add_reaction("\U000023ee")    #Top-left
                    await msg.add_reaction("\U00002b05")    #Left
                    await msg.add_reaction("\U000027a1")    #Right
                    await msg.add_reaction("\U000023ed")    #Top-right

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

        # ALL, with NO search
        except IndexError:
            if not args:
                heros = await self.client.quefe(f"SELECT hero_id, name, illulink FROM pi_hero WHERE user_id='{ctx.author.id}' AND existence='GOOD';", type='all')

                if not heros: await ctx.send("<:osit:544356212846886924> You have no hero. Use `summon` to summon one."); return

                def makeembed(curp, pages, currentpage):
                    hero = heros[curp]

                    reembed = discord.Embed(title=f"━━━ `{hero[0]}` | **{hero[1]}** ━━━", color=0x36393E) #description=f"```{description}```"
                    reembed.set_image(url=hero[2])
                    reembed.set_author(name=f"{ctx.author.name} | {curp+1}·{pages}", icon_url=ctx.author.avatar_url)

                    return reembed

                async def attachreaction(msg):
                    await msg.add_reaction("\U000023ee")    #Top-left
                    await msg.add_reaction("\U00002b05")    #Left
                    await msg.add_reaction("\U000027a1")    #Right
                    await msg.add_reaction("\U000023ed")    #Top-right

                pages = len(heros)
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

        # SPECIFIC, with search
        try: hero_code, name, illulink = await self.client.quefe(f"SELECT hero_code, name, illulink FROM pi_hero WHERE hero_id='{int(args[0])}' OR name LIKE '%{args[0]}%' LIMIT 1;")
        except TypeError: await ctx.send(f"<:osit:544356212846886924> Hero not found!"); return
        except IndexError: await ctx.send("<:osit:544356212846886924> Missing hero's id or name"); return
        except ValueError: await ctx.send("<:osit:544356212846886924> Invalid hero's id")

        temb = discord.Embed(title=f"━━━ `{hero_code}` | `{args[0]}` | **{name}** ━━━", color=0x36393E) #description=f"```{description}```"
        temb.set_image(url=illulink)

        await ctx.send(embed=temb)

    @commands.command()
    @commands.cooldown(1, 3, type=BucketType.user)
    async def deck(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        try:
            if args[0] == 'create':
                deck_q = await self.client.quefe(f"SELECT COUNT(deck_id) FROM pi_deck WHERE user_id='{ctx.author.id}';"); deck_q = deck_q[0]
                # Decks quantity check
                if deck_q >= 3: await ctx.send("<:osit:544356212846886924> You cannot maintain more than 3 decks at a time."); return

                if deck_q == 0: await self.client._cursor.execute(f"INSERT INTO pi_deck VALUES (0, 'Untitled', '{ctx.author.id}', 'MAIN', NULL, NULL, NULL, NULL, NULL, NULL);")
                else: await self.client._cursor.execute(f"INSERT INTO pi_deck VALUES (0, 'Untitled', '{ctx.author.id}', 'NORMAL', NULL, NULL, NULL, NULL, NULL, NULL);")

                await ctx.send("<a:yy32:555244228217798673> Deck created!"); return

            elif args[0] == 'lock':
                if await self.client._cursor.execute(f"UPDATE pi_deck SET type=IF(type='MAIN', 'NORMAL', type), type=IF(deck_id='{args[1]}', 'MAIN', type) WHERE (deck_id='{args[1]}' OR type='MAIN') AND user_id='{ctx.author.id}';"):
                    await ctx.send(f"<a:yy32:555244228217798673> Deck `{args[1]}` is locked as main deck!"); return
                else: await ctx.send(f"<:osit:544356212846886924> Deck not found!"); return

            # DECK show
            else:
                try: name, slot_1, slot_2, slot_3 = await self.client.quefe(f"SELECT name, slot_1, slot_2, slot_3 FROM pi_deck WHERE user_id='{ctx.author.id}' AND deck_id={int(args[0])};")
                except TypeError: await ctx.send("<:osit:544356212846886924> Deck not found!"); return
                except ValueError: await ctx.send("<:osit:544356212846886924> Invalid deck's id!"); return

                async def threegik():
                    margin = 24
                    bg = copy.deepcopy(self.prote_lib['bg_deck'][0])

                    for slot in [slot_1, slot_2, slot_3]:
                        try:
                            try:
                                slot = slot.split(' || ')
                                img = self.prote_lib['card'][slot[1]][0]
                                bg.alpha_composite(img, dest=(margin, 14))
                            except AttributeError: pass
                            finally:
                                try: margin += img.width
                                except UnboundLocalError: margin += 190
                        except IndexError:
                            margin += img.width

                    output_buffer = BytesIO()
                    bg.save(output_buffer, 'png')
                    output_buffer.seek(0)
                    return output_buffer

                output_buffer = await threegik()
                await ctx.send(file=discord.File(fp=output_buffer, filename='deck.png'), content=f"{ctx.author.mention} || **{name.capitalize()}**")

        except IndexError:
            decks = await self.client.quefe(f"SELECT deck_id, name, type, slot_1, slot_2, slot_3 FROM pi_deck WHERE user_id='{ctx.author.id}';", type='all')
            if not decks: await ctx.send("<:osit:544356212846886924> You have no deck. Use `deck create` to make one."); return

            def makeembed(top, least, pages, currentpage):
                reembed = discord.Embed(colour = discord.Colour(0x011C3A))

                for deck in decks[top:least]:
                    deck = list(deck)
                    try: deck[3] = deck[3].replace(' || ', '·')
                    except AttributeError: pass
                    try: deck[4] = deck[4].replace(' || ', '·')
                    except AttributeError: pass
                    try: deck[5] = deck[5].replace(' || ', '·')
                    except AttributeError: pass
                    if deck[2] == 'MAIN': reembed.add_field(name=f"<:purple_key:547600983073751042> **`{deck[0]}`|{deck[1]}**", value=f"╟➀ `{deck[3]}`\n╟➁ `{deck[4]}`\n╟➂ `{deck[5]}`")
                    else: reembed.add_field(name=f"╟ `{deck[0]}`|{deck[1]}", value=f"╟➀ `{deck[3]}`\n╟➁ `{deck[4]}`\n╟➂ `{deck[5]}`")    

                return reembed
                #else:
                #    await ctx.send("*Nothing but dust here...*")
            
            async def attachreaction(msg):
                await msg.add_reaction("\U000023ee")    #Top-left
                await msg.add_reaction("\U00002b05")    #Left
                await msg.add_reaction("\U000027a1")    #Right
                await msg.add_reaction("\U000023ed")    #Top-right

            pages = len(decks)//3
            if len(decks)%3 != 0: pages += 1
            currentpage = 1
            cursor = 0

            emli = []
            for curp in range(pages):
                myembed = makeembed(currentpage*3-3, currentpage*3, pages, currentpage)
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

    @commands.command()
    @commands.cooldown(1, 4, type=BucketType.user)
    async def put(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        dalen = len(args)
        sd = {'1': 'slot_1', '2': 'slot_2', '3': 'slot_3'}

        # DECK PICKED, SLOT AUTO
        if dalen == 2:
            # Get hero's info
            try: hero_id, hero_code, name = await self.client.quefe(f"SELECT hero_id, hero_code, name FROM pi_hero WHERE hero_id={int(args[1])} AND user_id='{ctx.author.id}';")
            # E: Hero not found
            except TypeError: await ctx.send("<:osit:544356212846886924> Hero not found!"); return
            except ValueError: await ctx.send("<:osit:544356212846886924> Invalid hero's id!"); return

            # Deck info
            try: sl = await self.client.quefe(f"SELECT slot_1, slot_2, slot_3 FROM pi_deck WHERE user_id='{ctx.author.id}' AND deck_id={int(args[0])};")
            except ValueError: await ctx.send("<:osit:544356212846886924> Invalid deck's id!"); return

            # IN deck      --  Remove
            try:
                slot = sd[f"{sl.index(f'{hero_id} || {hero_code}')+1}"]
                await self.client._cursor.execute(f"UPDATE pi_deck SET {slot}=NULL WHERE user_id='{ctx.author.id}' AND deck_id={args[0]};")
                await ctx.send(f"<a:yy32:555244228217798673> Successfully remove `{hero_id}`|**{name}** from deck **{args[0]}**") ; return
            # NOT IN deck  --  Put in
            except (ValueError, AttributeError):
                # Search for NULL slot
                try:
                    slot = sd[f"{sl.index(None)+1}"]
                    await self.client._cursor.execute(f"UPDATE pi_deck SET {slot}='{hero_id} || {hero_code}' WHERE user_id='{ctx.author.id}' AND deck_id={args[0]};")
                    await ctx.send(f"<a:yy32:555244228217798673> Successfully put `{hero_id}`|**{name}** in deck **{args[0]}**"); return
                # E: NULL not found --> Deck's full
                except ValueError: await ctx.send("<:osit:544356212846886924> Deck's full!"); return

        # DECK PICKED, SLOT PICKED
        elif dalen == 3:
            # Get hero's info
            try: hero_id, hero_code, name = await self.client.quefe(f"SELECT hero_id, hero_code, name FROM pi_hero WHERE hero_id='{args[2]}';")
            # E: Hero not found
            except TypeError: await ctx.send("<:osit:544356212846886924> Hero not found!"); return

            # PUT
            try:
                # Clearance of duplicate
                if not await self.client._cursor.execute(f"UPDATE pi_deck SET slot_1=IF(slot_1='{hero_id} || {hero_code}', NULL, slot_1), slot_2=IF(slot_2='{hero_id} || {hero_code}', NULL, slot_2), slot_3=IF(slot_3='{hero_id} || {hero_code}', NULL, slot_3), {sd[args[1]]}=IF({sd[args[1]]}='{hero_id} || {hero_code}', {sd[args[1]]},'{hero_id} || {hero_code}') WHERE user_id='{ctx.author.id}' AND deck_id={int(args[0])};"):
                    await self.client._cursor.execute(f"UPDATE pi_deck SET {sd[args[1]]}=NULL WHERE user_id='{ctx.author.id}' AND deck_id={args[0]}")
                    await ctx.send(f"<a:yy32:555244228217798673> Successfully remove `{hero_id}`|**{name}** from deck **{args[0]}**") ; return
            except KeyError: await ctx.send("<:osit:544356212846886924> Invalid slot!") ; return
            except ValueError: await ctx.send("<:osit:544356212846886924> Invalid deck's id!"); return
            
            await ctx.send(f"<a:yy32:555244228217798673> Successfully put `{hero_id}`|**{name}** in deck **{args[0]}**"); return

        else: await ctx.send("<:osit:544356212846886924> Missing... everything")

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def duel(self, ctx, *args):
        cmd_tag = 'duel'
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        if not await self.__cd_check(ctx.message, cmd_tag, f"Curb your enthusiasm, **{ctx.author.name}**!"): return

        # Money
        try: money = int(args[0])
        except IndexError: money = 1
        except ValueError: await ctx.send(f"<:osit:544356212846886924> Invalid `money` value!"); return

        async def fuldek(user):
            # DECK get
            try: slot_1, slot_2, slot_3 = await self.client.quefe(f"SELECT slot_1, slot_2, slot_3 FROM pi_deck WHERE user_id='{user.id}' AND type='MAIN';")
            # E: No deck found
            except TypeError: await ctx.send(f"<:osit:544356212846886924> You have no deck, **{user.name}**. Use `deck create` to make one."); return False

            # CARDS get
            cdict = {}; counter = -3
            for slot in [slot_1, slot_2, slot_3]:
                try: hid = slot.split(' || ')[0]
                # E: Slot is None
                except AttributeError: cdict[counter] = None; counter += 1; continue
                cdict[hid] = await self.client.quefe(f"""SELECT lp, str, chain, speed, au_FLAME, au_ICE, au_HOLY, au_DARK, name FROM pi_hero WHERE user_id='{user.id}' AND hero_id="{hid}";""")
                counter += 1

            return cdict

        # HOST info
        user_deck = await fuldek(ctx.author)
        if not user_deck: return

        # DUEL inform
        key = (f'duel <@{ctx.author.id}>', f'duel <@!{ctx.author.id}>')
        def UCc_check(m):
            return m.channel == ctx.channel and m.content in key #and m.author != ctx.author
        await ctx.send(f"<a:yy32:555244228217798673> **{ctx.author.name}** is offering a card duel, with a bet of <:36pxGold:548661444133126185>**{money}**\n|| Type **`duel @{str(ctx.author)}`** to accept!")
        await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.set, f'{cmd_tag}{ctx.author.id}', 'working', ex=180, nx=True))

        # Opponent await. Opponent's DECK info
        try:
            while True:
                msg = await self.client.wait_for('message', timeout=30, check=UCc_check)
                op_deck = await fuldek(msg.author)
                print(op_deck)
                if op_deck: break
                else: return
        except asyncio.TimeoutError: await ctx.send(f"<:osit:544356212846886924> It seems no one give a poop about you, {ctx.author.mention}..."); return
        
        # Calc battle between two card
        async def single_battle(uc, oc, uc_chainer, oc_chainer):
            """Battle between two cards"""
            # lp, str, chain, speed, au_FLAME, au_ICE, au_HOLY, au_DARK, name

            # Preparing
            au_catalyst = uc[4] - oc[4] + uc[5] - oc[5] + uc[6] - oc[6] + uc[7] - oc[7]             # User over Opponent
            if not uc_chainer: uc_chainer = 1
            if not oc_chainer: oc_chainer = 1
            
            # OC and UC hits calc
            if not random.choice(range(round(uc[3] + 1))):
                try:
                    uc_hit = uc[0] / ((uc[1] + au_catalyst) * uc_chainer * 2)
                    if uc_hit < 0: uc_hit = 0
                # E: No hit
                except ZeroDivisionError: uc_hit = 0
            else:
                try:
                    uc_hit = uc[0] / ((uc[1] + au_catalyst) * uc_chainer)
                    if uc_hit < 0: uc_hit = 0
                # E: No hit
                except ZeroDivisionError: uc_hit = 0
            
            if not random.choice(range(round(oc[3] + 1))):
                try:
                    oc_hit = oc[0] / ((oc[1] + au_catalyst) * oc_chainer * 2)
                    if oc_hit < 0: oc_hit = 0
                # E: No hit
                except ZeroDivisionError: oc_hit = 0
            else:
                try:
                    oc_hit = oc[0] / ((oc[1] + au_catalyst) * oc_chainer)
                    if oc_hit < 0: oc_hit = 0
                # E: No hit
                except ZeroDivisionError: oc_hit = 0

            if uc_hit == oc_hit: return 'draw', 0
            elif uc_hit > oc_hit: return 'uc', int(uc_hit)
            else: return 'oc', int(oc_hit)


        # ================== BATTLE            ||              # lp, str, chain, speed, au_FLAME, au_ICE, au_HOLY, au_DARK, name
        uc_chainer = None; oc_chainer = None; stone = 0
        line = "<a:fiba1:556737887186452491><a:fiba2:556739826012127254> <a:pressVS:556740703032573953> <a:riba2:556740559805349888><a:riba1:556740559763406852>"
        mmm = await ctx.send(line)
        line = f"**{ctx.author.name.upper()}** <a:pressVS:556740703032573953> **{msg.author.name.upper()}**"
        await asyncio.sleep(1.5)        # A fireball takes 1.5s to finish
        await mmm.edit(content=line)

        for (uc_hid, uc), (oc_hid, oc) in zip(user_deck.items(), op_deck.items()):

            # NONE Handler
            if uc == None and oc == None:
                line = line + f"\n╟ Nothing happended..."
                uc_chainer = 0; oc_chainer = 0
                await mmm.edit(content=line); await asyncio.sleep(random.choice([2, 3, 4]))
                continue
            elif uc == None:
                line = line + f"\n╟ `{oc_hid}|`**{oc[8]}** simply did nothing and win!"; stone -= 1
                if oc_chainer == None: oc_chainer = oc[2]
                try: oc_chainer = (oc[2] + oc_chainer) / abs(oc[2] - oc_chainer)
                except ZeroDivisionError: oc_chainer = oc[2] + oc_chainer
                uc_chainer = 0
                await mmm.edit(content=line); await asyncio.sleep(random.choice([2, 3, 4]))
                continue
            elif oc == None:
                line = line + f"\n╟ `{uc_hid}|`**{uc[8]}** simply did nothing and win!"; stone += 1
                if uc_chainer == None: uc_chainer = uc[2]
                try: uc_chainer = (uc[2] + uc_chainer) / abs(uc[2] - uc_chainer)
                except ZeroDivisionError: uc_chainer = uc[2] + uc_chainer
                oc_chainer = 0
                await mmm.edit(content=line); await asyncio.sleep(random.choice([2, 3, 4]))
                continue

            # Chainer calc
            if uc_chainer == None: uc_chainer = uc[2]
            else:
                try: uc_chainer = (uc[2] + uc_chainer) / abs(uc[2] - uc_chainer)
                except ZeroDivisionError: uc_chainer = uc[2] + uc_chainer
            if oc_chainer == None: oc_chainer = oc[2]
            else:
                try: oc_chainer = (oc[2] + oc_chainer) / abs(oc[2] - oc_chainer)
                except ZeroDivisionError: oc_chainer = oc[2] + oc_chainer

            # Winner calc
            ret, hit = await single_battle(uc, oc, uc_chainer, oc_chainer)
            if ret == 'draw': line = line + f"\n╟ `{uc_hid}|`**`{uc[8]}`** and `{oc_hid}|`**`{oc[8]}`** secretly flee away"
            elif ret == 'uc': line = line + f"\n╟ `{uc_hid}|`**`{uc[8]}`** has killed ~~`{oc_hid}|`**`{oc[8]}`**~~ after **{hit}** hits!"; stone += 1
            elif ret == 'oc': line = line + f"\n╟ `{oc_hid}|`**`{oc[8]}`** has killed ~~`{uc_hid}|`**`{uc[8]}`**~~ after **{hit}** hits!"; stone -= 1

            # Inform
            await mmm.edit(content=line); await asyncio.sleep(random.choice([2, 3, 4]))

        # WINNER WINNER whatever...
        if not stone: line = line + f"\n**━━━━ DRAW! ━━━━**"; await mmm.edit(content=line); return
        elif stone > 0: line = line + f"\n**━━━ {ctx.author.name.upper()} WIN ━━━**"; winner = ctx.author.id; loser = msg.author.id
        elif stone < 0: line = line + f"\n**━━━ {msg.author.name.upper()} WIN ━━━**"; winner = msg.author.id; loser = ctx.author.id
        await mmm.edit(content=line)

        await self.client._cursor.execute(f"UPDATE personal_info SET money=money-IF(money>={money}, {money}, 0), LP=LP-IF(money<{money}, money-{money}, 0) WHERE id='{loser}'; UPDATE personal_info SET money=money+{money} WHERE id='{winner}';")
        if not await self.client._cursor.execute(f"UPDATE misc_status SET duel_win=duel_win+1 WHERE user_id='{winner}';"):
            await self.client._cursor.execute(f"INSERT INTO misc_status VALUES ('{winner}', 1, 0)")
        if not await self.client._cursor.execute(f"UPDATE misc_status SET duel_lost=duel_lost+1 WHERE user_id='{loser}';"):
            await self.client._cursor.execute(f"INSERT INTO misc_status VALUES ('{loser}', 0, 1)")

    @commands.command()
    @commands.cooldown(1, 2, type=BucketType.user)
    async def dispose(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        try: hero_id, hero_code, name = await self.client.quefe(f"SELECT hero_id, hero_code, name FROM pi_hero WHERE hero_id='{args[0]}';")
        except TypeError: await ctx.send("<:osit:544356212846886924> Hero's not found!"); return

        await ctx.send(f"<a:yy32:555244228217798673> Disposed `{hero_id}`|**{name}**!")
        await self.client._cursor.execute(f"UPDATE pi_deck SET slot_1=IF(slot_1='{hero_id} || {hero_code}', NULL, slot_1), slot_2=IF(slot_2='{hero_id} || {hero_code}', NULL, slot_2), slot_3=IF(slot_3='{hero_id} || {hero_code}', NULL, slot_3) WHERE user_id='{ctx.author.id}'; UPDATE pi_hero SET existence='BAD' WHERE hero_id='{hero_id}' AND user_id='{ctx.author.id}'; UPDATE pi_land SET hero_id='n/a' WHERE user_id='{ctx.author.id}' AND hero_id='{hero_id}';")







##########################



##########################

#    @commands.command(aliases=['>cast'])
#    @commands.cooldown(1, 60, type=BucketType.user)
#    async def avacast(self, ctx, *args):

##########################





# ============= TACTICAL ==============

    @commands.command(aliases=['scan', 'rad'])
    @commands.cooldown(1, 30, type=BucketType.user)
    async def radar(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        cur_X, cur_Y = await self.client.quefe(f"SELECT cur_X, cur_Y FROM personal_info WHERE id='{str(ctx.message.author.id)}';")
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
        coords_list = await self.client.quefe(f"SELECT cur_X, cur_Y FROM personal_info WHERE {cur_X - xrange}<=cur_X AND cur_X<={cur_X + xrange} AND {cur_Y - yrange}<=cur_Y AND cur_Y<={cur_Y + yrange};", type='all')
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
        cur_PLACE, cur_X, cur_Y, stats = await self.client.quefe(f"SELECT cur_PLACE, cur_X, cur_Y, stats FROM personal_info WHERE id='{ctx.author.id}';")

        if stats == 'DEAD': await self.tools.ava_scan(ctx.message, type='life_check')

        # COORD
        if not args:
            if cur_PLACE.startswith('region.'): r_name = await self.client.quefe(f"SELECT name FROM environ WHERE environ_code='{cur_PLACE}';")
            else: r_name = await self.client.quefe(f"SELECT name FROM pi_land WHERE land_code='{cur_PLACE}';")
            await ctx.send(f":map: **`{cur_X:.3f}`** · **`{cur_Y:.3f}`** · `{cur_PLACE}`|**{r_name[0]}** · {ctx.message.author.mention}", delete_after=5); return

        try:
            x = int(args[0])/1000; y = int(args[1])/1000

            # Region INFO
            if cur_PLACE.startswith('region.'): r_name, border_X, border_Y = await self.client.quefe(f"SELECT name, border_X, border_Y FROM environ WHERE environ_code='{cur_PLACE}'")
            # Land INFO
            else:
                try: r_name, border_X, border_Y = await self.client.quefe(f"SELECT name, border_X, border_Y FROM pi_land WHERE land_code='{cur_PLACE}'")
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
                    x, y = await self.utils.distance_tools(cur_X, cur_Y, x, y, distance=distance, type='d-c')
                    # Coord check
                    if x > border_X: x = border_X
                    if y > border_Y: y = border_Y
                    if x < 0: x = 0
                    if y < 0: y = 0
                except (IndexError, ValueError): pass
                
                # Procede teleportation
                await self.tools.tele_procedure(cur_PLACE, str(ctx.author.id), x, y)

                # Informmmm :>
                try: await ctx.send(f"<:dual_cyan_arrow:543662534612353044>`{distance}m`<:dual_cyan_arrow:543662534612353044> toward **`{prior_x:.3f}`** · **`{prior_y:.3f}`**\n:map: Now you're at **`{x:.3f}`** · **`{y:.3f}`** · `{cur_PLACE}`|**{r_name}**!", delete_after=5)
                except NameError: await ctx.send(f":map: [{cur_X:.3f}, {cur_Y:.3f}] <:dual_cyan_arrow:543662534612353044> **`{x:.3f}`** · **`{y:.3f}`** · `{cur_PLACE}`|**{r_name}**!", delete_after=5)
            else: await ctx.send(f"<:osit:544356212846886924> Please use 5-digit coordinates!"); return
        except IndexError:
            #await ctx.send(f"<:osit:544356212846886924> Out of map's range!"); return
            # ONE coord only
            if args[0].isdigit():
                args = (args[0], args[0])
                try:
                    x = int(args[0])/1000; y = int(args[1])/1000

                    # Region INFO
                    if cur_PLACE.startswith('region.'): r_name, border_X, border_Y = await self.client.quefe(f"SELECT name, border_X, border_Y FROM environ WHERE environ_code='{cur_PLACE}'")
                    # Land INFO
                    else:
                        try: r_name, border_X, border_Y = await self.client.quefe(f"SELECT name, border_X, border_Y FROM pi_land WHERE land_code='{cur_PLACE}'")
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
                            x, y = await self.utils.distance_tools(cur_X, cur_Y, x, y, distance=distance, type='d-c')
                            # Coord check
                            if x > border_X: x = border_X
                            if y > border_Y: y = border_Y
                            if x < 0: x = 0
                            if y < 0: y = 0
                        except (IndexError, ValueError): pass
                        
                        # Procede teleportation
                        await self.tools.tele_procedure(cur_PLACE, str(ctx.author.id), x, y)

                        # Informmmm :>
                        try: await ctx.send(f"<:dual_cyan_arrow:543662534612353044>`{distance}m`<:dual_cyan_arrow:543662534612353044> toward **`{prior_x:.3f}`** · **`{prior_y:.3f}`**\n:map: Now you're at **`{x:.3f}`** · **`{y:.3f}`** · `{cur_PLACE}`|**{r_name}**!", delete_after=5)
                        except NameError: await ctx.send(f":map: [{cur_X:.3f}, {cur_Y:.3f}] <:dual_cyan_arrow:543662534612353044> **`{x:.3f}`** · **`{y:.3f}`** · `{cur_PLACE}`|**{r_name}**!", delete_after=5)
                    else: await ctx.send(f"<:osit:544356212846886924> Please use 5-digit coordinates!"); return
                except IndexError: await ctx.send(f"<:osit:544356212846886924> Out of map's range!"); return


        # PLACE
        except (KeyError, ValueError):
            if cur_PLACE == args[0]: await ctx.send("<:osit:544356212846886924> You're already there :|")

            # Region INFO
            if args[0].startswith('region.'): r_name, border_X, border_Y, pass_query = await self.client.quefe(f"SELECT name, border_X, border_Y, pass_query FROM environ WHERE environ_code='{args[0]}'")
            # Land INFO
            else:
                try: r_name, border_X, border_Y = await self.client.quefe(f"SELECT name, border_X, border_Y FROM pi_land WHERE land_code='{args[0]}'")
                except TypeError: await ctx.send(f"**{args[0]}**... There is no such place here, perhap it's from another era?"); return

            # Region's pass check
            if pass_query:
                a = await self.client._cursor.execute(pass_query.replace('user_id_here', str(ctx.author.id)))
                print(a)
                if await self.client._cursor.execute(pass_query.replace('user_id_here', str(ctx.author.id))) == 0:
                    await ctx.send(f"<:osit:544356212846886924> The requirements to join this region is not met!"); return

            if cur_X <= 1 and cur_Y <=1:
                await self.client._cursor.execute(f"UPDATE personal_info SET cur_PLACE='{args[0]}' WHERE id='{ctx.author.id}';")
                await ctx.send(f":round_pushpin: Successfully move to `{args[0]}`|**{r_name}**!", delete_after=5)
            else: await ctx.send(f"<:osit:544356212846886924> You can only travel between regions inside **Peace Belt**!"); return

    @commands.command(aliases=['md'])
    async def measure_distance(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        cur_X, cur_Y = await self.client.quefe(f"SELECT cur_X, cur_Y FROM personal_info WHERE id='{str(ctx.message.author.id)}';")

        try:
            distance = await self.utils.distance_tools(cur_X, cur_Y, int(args[0])/1000, int(args[1])/1000)
            await ctx.send(f":straight_ruler\n::triangular_ruler: Result: **`{distance}m`**")
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





# ================ TUTORIAL MODULES ======================

    async def engine_roller(self, ctx, tut_code, headers, box='direct'):
        if box == 'direct': box = ctx.author
        else: box = ctx.channel

        text = await self.client.quefe(f"""SELECT tut_head, tut_text FROM sys_tut WHERE tut_code='{tut_code}' AND tut_head IN ('{"', '".join(headers)}');""", type='all')
        # Re-arrange
        h = []
        for he in headers:
            for t in text:
                if he == t[0]: h.append(t[1])

        msg = await box.send(embed=discord.Embed(description=h[0], color=0x36393E))
        await msg.add_reaction('\U00002705')

        def RUM_check(reaction, user):
            return user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) == '\U00002705'
        try: await self.client.wait_for('reaction_add', check=RUM_check, timeout=60)
        except asyncio.TimeoutError: await box.send("<:osit:544356212846886924> Request timeout!"); return False

        for head in h[1:]:
            await msg.edit(embed=discord.Embed(description=head, color=0x36393E))

            try: await self.client.wait_for('reaction_add', check=RUM_check, timeout=60)
            except asyncio.TimeoutError: await box.send("<:osit:544356212846886924> Request timeout!"); return False


    async def tut_basic_status(self, ctx, box='indirect'):
        """Talking about status"""

        await self.engine_roller(ctx, 'basic_status', ['intro_1', 'lp', 'sta', 'degree', 'evo'], box=box)


    async def engine_waitor(self, ctx, line, t=20, keylist=[], DM=False, illulink=None):

        if DM: await ctx.author.send(embed=discord.Embed(description=line, colour=0x527D8F).set_image(url=illulink))
        else: await ctx.send(embed=discord.Embed(description=line).set_image(url=illulink))

        def UMCc_check(m):
            if keylist: return m.author == ctx.author and m.content in keylist
            return m.author == ctx.author

        try: await self.client.wait_for('message', check=UMCc_check, timeout=t); return True
        except asyncio.TimeoutError: return False








# ============= DATA MANIPULATION =================


    async def data_plugin(self):

        # TIME get
        with open('data/time.json') as f:
            try:
                time_pack = json.load(f)
            except IndexError: print("ERROR at <data_plugin(__TIME__)>")
        self.client.STONE = datetime(time_pack[0], time_pack[1], time_pack[2], hour=time_pack[3], minute=time_pack[4])

        # Obsolete from JSON ver
        # JOBS get
        with open('data/jobs.json') as f:
            try:
                self.jobs_dict = json.load(f)
            except IndexError: print("ERROR at <data_plugin(__JOBS__)>")


        # ARSENAL Inventories get
        """with open('data/arsenal.json') as f:
            try:
                self.data_ARSENAL = json.load(f)
            except IndexError: print("ERROR at <data_plugin(__ARSENAL__)>")
        for id in list(self.data_ARSENAL.keys()):
            self.data_ARSENAL[id] = self.objectize(self.data_ARSENAL[id], ['weapon', self.data_ARSENAL[id]['tags'][1]])
        print('___ARSENAL plugin() done')"""


        # AMUNNITION Inventories get
        """with open('data/ammunition.json') as f:
            try:
                self.data_AMMU = json.load(f)
            except IndexError: print("ERROR at <data_plugin(__AMMU__)>")
        for id in list(self.data_AMMU.keys()):
            self.data_AMMU[id] = self.objectize(self.data_AMMU[id], ['ammunition'])
        print('___AMMU plugin() done')"""


        # SUPPLY Inventories get        
        """with open('data/supply.json') as f:
            try:
                self.data_SUPPLY = json.load(f)
            except IndexError: print("ERROR at <data_plugin(__SUPPLY__)>")
        supfunc_dict = {'it0': [self.heal, '0'], 'it1': [self.heal, '1'], 'it2': [self.heal, '2'], 'it3': [self.recovery, '0'], 'it4': [self.recovery, '1'], 'it5': [self.recovery, '2']}                
        for id in list(self.data_SUPPLY.keys()):
            self.data_SUPPLY[id] = self.objectize(self.data_SUPPLY[id], ['supply'], supfunc_dict[id])
        print('___SUPPLY plugin() done')"""


        # INGREDIENT
        """data_INGREDIENT = {}
        with open('data/ingredient.json') as f:
            try:
                data_INGREDIENT = json.load(f)
            except IndexError: print("ERROR at <data_plugin(__INGREDIENT__)>")
        igfunc_dict = {'ig0': [self.recovery_bit, 10], 'ig1': [self.recovery_bit, 10], 'ig2': [self.recovery_bit, 30]}                                
        for id in list(data_INGREDIENT.keys()):
            data_INGREDIENT[id] = self.objectize(data_INGREDIENT[id], ['ingredient'], igfunc_dict[id])
        print('___INGREDIENT plugin() done')"""


        # QUESTS
        data_QUESTS = {}
        with open('data/quests.json') as f:
            try:
                data_QUESTS = json.load(f)
            except IndexError: print("ERROR at <data_plugin(__QUESTS__)>")
        print('___QUESTS plugin() done')


        # ENTITIES
        """data_ENTITY = {}
        with open('data/living_entities.json') as f:
            try:
                data_ENTITY = json.load(f)
            except IndexError: print("ERROR at <data_plugin(__ENTITY__)>")
        print('___ENTITY plugin() done')"""


        # REGION    
        """data_REGION = {}  
        with open('data/region.json') as f:
            try:
                data_REGION = json.load(f)
            except IndexError: print("ERROR at <data_plugin(__REGION__)>")
        print('___REGION plugin() done')"""        


        # ENTITY and INGREDIENT are dictionaries to look up, not to be used
        """self.data = {'item': {**self.data_ARSENAL, **self.data_SUPPLY, **self.data_AMMU}, 'entity': data_ENTITY, 'ingredient': data_INGREDIENT}
        self.environ = data_REGION"""

        async def world_built():
            regions = await self.client.quefe("SELECT environ_code FROM environ", type='all')

            for region in regions:
                region = region[0]
                
                # ----------- MOB/BOSS/NPC initialize ------------
                mobs = await self.client.quefe(f"SELECT mob_code, quantity, limit_Ax, limit_Ay, limit_Bx, limit_By FROM environ_diversity WHERE environ_code='{region}';", type='all')

                for mob in mobs:
                    mob = list(mob)
                    # MOB
                    if mob[0].startswith('mb'):
                        # Quantity of kind in a diversity check
                        qk = await self.client.quefe(f"SELECT COUNT(*) FROM environ_mob WHERE mob_code='{mob[0]}' AND region='{region}';")

                        if qk[0] == mob[1]: continue
                        elif qk[0] < mob[1]: mob[1] -= qk[0]
                        
                        # Get the <mob> prototype
                        name, branch, lp, str, chain, speed, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY = await self.client.quefe(f"SELECT name, branch, lp, str, chain, speed, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY FROM model_mob WHERE mob_code='{mob[0]}';")
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
                                        temp = await self.client.quefe(f"SELECT * FROM model_item WHERE item_code='{stuff[0]}';")
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
                            await self.client._cursor.execute(f"""INSERT INTO environ_mob VALUES (0, 'mob', '{mob[0]}', "{name}", '{branch}', {lp}, {str}, {chain}, {speed}, {au_FLAME}, {au_ICE}, {au_DARK}, {au_HOLY}, '{' | '.join(bingo_list)}', '{rewards_query}', '{region}', {mob[2]}, {mob[3]}, {mob[4]}, {mob[5]}, 'n/a');""")
                            counter_get = await self.client.quefe("SELECT MAX(id_counter) FROM environ_mob")
                            await self.client._cursor.execute(f"UPDATE environ_mob SET mob_id='mob.{counter_get[0]}' WHERE id_counter={counter_get[0]};")
                    
                    # NPC
                    elif mob[0].startswith('p'):
                        # Quantity of kind in a diversity check
                        qk = await self.client.quefe(f"SELECT COUNT(*) FROM environ_npc WHERE npc_code='{mob[0]}' AND region='{region}';")
                        if qk[0] == mob[1]: continue
                        elif qk[0] < mob[1]: mob[1] -= qk[0]
                        
                        # Get the <mob> prototype
                        name, branch, lp, str, chain, speed, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY = await self.client.quefe(f"SELECT name, branch, lp, str, chain, speed, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY FROM model_npc WHERE npc_code='{mob[0]}';")
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
                                            temp = await self.client.quefe(f"SELECT * FROM model_item WHERE item_code='{stuff[0]}';")
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
                        await self.client._cursor.execute(f"""INSERT INTO environ_npc VALUES (0, 'main', '{mob[0]}', "{name}", '{branch}', {lp}, {str}, {chain}, {speed}, {au_FLAME}, {au_ICE}, {au_DARK}, {au_HOLY}, '{' | '.join(bingo_list)}', '{rewards_query}', '{region}', {mob[2]}, {mob[3]}, {mob[4]}, {mob[5]}, 'n/a', '');""")
                        counter_get = await self.client.quefe("SELECT MAX(id_counter) FROM environ_npc")
                        await self.client._cursor.execute(f"UPDATE environ_npc SET npc_id='npc.{counter_get[0]}' WHERE id_counter={counter_get[0]};")

                # ----------- MAP initialize -------------
                # Obsolete since JSON ver
                """
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
                """
                
                # ----------- QUESTS initialize ----------
                # Obsolete since JSON ver
                """           
                try: self.environ[region]['characteristic']['quest'] = data_QUESTS
                except KeyError: print("KEY_ERROR")
                """
            
            print("___WORLD built() done")  

        async def rtzone_refresh():
            #fix_list = await self.client.quefe("SELECT id FROM personal_info WHERE cur_MOB != 'n/a' OR cur_USER != 'n/a';", type='all')
            #for user_id in fix_list:
            await self.client._cursor.execute(f"UPDATE personal_info SET cur_MOB='n/a', cur_USER='n/a';")
            await self.client._cursor.execute(f"UPDATE environ_mob SET lockon='n/a';")

        await world_built()
        await rtzone_refresh()


    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    @checks.check_author()
    async def ituda(self, ctx, *args):

        codes = await self.client.quefe(f"SELECT item_code FROM pi_inventory WHERE item_code LIKE 'it%' OR item_code LIKE 'ar%' OR item_code LIKE 'am%';", type='all')

        for code in codes:
            await self.client._cursor.execute(f"UPDATE pi_inventory p INNER JOIN model_item m ON m.item_code='{code[0]}' SET p.tags=m.tags, p.weight=m.weight, p.defend=m.defend, p.multiplier=p.multiplier, p.str=m.str, p.intt=m.intt, p.sta=m.sta, p.speed=m.speed, p.round=m.round, p.accuracy_randomness=m.accuracy_randomness, p.accuracy_range=m.accuracy_range, p.range_min=m.range_min, p.range_max=m.range_max, p.firing_rate=m.firing_rate, p.reload_query=m.reload_query, p.effect_query=m.effect_query, p.infuse_query=m.infuse_query, p.passive_query=m.passive_query, p.ultima_query=m.ultima_query, p.price=m.price, p.dmg=m.dmg, p.stealth=m.stealth, p.evo=m.evo, p.aura=m.aura, p.craft_value=m.craft_value, p.illulink=m.illulink WHERE p.item_code='{code[0]}';")

        await ctx.send(":white_check_mark:")



    """
    async def correctDefaultFist(self):
        users = await self.client.quefe("SELECT id FROM personal_info WHERE right_hand='ar13' OR left_hand='ar13';", type='all')
        print(users)
        for user in users:
            iid = await self.client.quefe(f"SELECT item_id FROM pi_inventory WHERE user_id='{user[0]}' AND item_code='ar13';")
            if not iid:
                await self.client._cursor.execute(f"SELECT func_it_reward('{user[0]}', 'ar13', 1);")
                iid = await self.client.quefe(f"SELECT item_id FROM pi_inventory WHERE user_id='{user[0]}' AND item_code='ar13';")
            await self.client._cursor.execute(f"UPDATE personal_info SET right_hand='{iid[0]}', left_hand='{iid[0]}' WHERE id='{user[0]}';")
    """

    """
    async def correctPCMArt(self):
        users = await self.client.quefe("SELECT user_id FROM pi_arts WHERE user_id NOT IN (SELECT user_id FROM pi_arts WHERE art_type='general');", type='all')
        print(users)
        for user in users:
            await self.client._cursor.execute(f"INSERT INTO pi_arts VALUES ('{user[0]}', 'general', 'passive_chain', 5);")
    """

def setup(client):
    client.add_cog(avasoul(client))



















