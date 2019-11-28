from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import asyncio
import random
from functools import partial
import re

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors
import pymysql.err as mysqlError



class avaPersonal(commands.Cog):

    def __init__(self, client):

        from .avaTools import avaTools
        from .avaUtils import avaUtils

        self.client = client
        self.__cd_check = self.client.thp.cd_check
        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)

        self.evo_func = {
            'lp': self.lp_calc,
            'sta': self.sta_calc,
            'str': self.str_calc,
            'int': self.int_calc,
            'flame': self.flame_calc,
            'ice': self.ice_calc,
            'holy': self.holy_calc,
            'dark': self.dark_calc,
            'charm': self.charm_calc
            }

        self.aui = {'FLAME': 'https://imgur.com/3UnIPir.png', 'ICE': 'https://imgur.com/7HsDWfj.png', 'HOLY': 'https://imgur.com/lA1qfnf.png', 'DARK': 'https://imgur.com/yEksklA.png'}

        print("|| Personal --- READY!")



# ================== EVENTS ==================

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     print("|| Personal --- READY!")



# ================== INFO/AVATAR ==================

    @commands.command(aliases=['begin', 'start'])
    @commands.cooldown(1, 6, type=BucketType.user)
    async def incarnate(self, ctx, *args):
        id = str(ctx.author.id); name = ctx.author.name
        cmd_tag = 'incarnate'
        if not await self.__cd_check(ctx.message, cmd_tag, f"<:fufu:605255050289348620> You're not dead long enough, **{ctx.author.name}**."): return

        # Create a living entity (creator-only)
        if args:
            if str(ctx.author.id) == '214128381762076672':
                try: id = str(ctx.message.mentions[0].id); name = ctx.mentions[0].name
                except IndexError: id = ' '.join(args); name = id
            else: await ctx.send(":no_entry_sign: You wish :>"); return
            
        resu = await self.client.quefe(f"SELECT stats FROM personal_info WHERE id='{id}'")
        try:
            if resu[0] != 'DEAD':
                await ctx.send(f"<:osit:544356212846886924> You've already incarnated!"); return
        except TypeError: pass
        
        year, month, day, hour, minute = await self.client.loop.run_in_executor(None, self.utils.time_get)

        # Prompt question
        if not resu:
            try: re_race, re_gender, re_name = await self.tools.incarnateData_collect(ctx, self.aui)
            except TypeError: await ctx.send(f"<:osit:544356212846886924> Session is cancelled, **{ctx.author.name}**!"); return
        else: re_race = None; re_gender = None; re_name = None

        bump = await self.tools.character_generate(id, name, dob=[year, month, day, hour, minute], resu=resu, info_pack=[re_race, re_gender, re_name])
        if not bump:
            await ctx.send(f">>> {self.utils.nixietext(f'Welcome to the Pralayer!')}")
            await ctx.send(f">>> This bot is hard, {ctx.author.mention}! So I'll personally advise you using `tutorial 1` to at least know what to do with this bot.\nAfter that, you can check `faq` for some extra info.", embed=discord.Embed().set_image(url='https://imgur.com/e8cIazx.gif'))
            await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.set, f'{cmd_tag}{ctx.author.id}', 'working', ex=82800, nx=True))
        elif bump == 3:
            await ctx.send(f"<:osit:544356212846886924> You've already incarnated!"); return
        else: await ctx.send(f":white_check_mark: {ctx.author.mention} has successfully re-incarnated. **WELCOME BACK!**")

    @commands.command(aliases=['p'])
    @commands.cooldown(1, 4, type=BucketType.user)
    async def profile(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        await self.tools.ava_scan(ctx.message, type='all')
        await self.tools.ava_scan(ctx.message, type='normalize')

        try:
            id = args[0]
            _vmode = 'INDIRECT'
        except IndexError: id = str(ctx.message.author.id); _vmode = 'DIRECT'
        
        # Data get and paraphrase
        # pylint: disable=unused-variable
        try: name, age, gender, money, merit, right_hand, left_hand, combat_HANDLING, STA, MAX_STA, LP, MAX_LP, STR, INTT, partner, evo, charm, au_FLAME, au_ICE, au_HOLY, au_DARK, perks = await self.client.quefe(f"SELECT name, age, gender, money, merit, right_hand, left_hand, combat_HANDLING, STA, MAX_STA, LP, MAX_LP, STR, INTT, partner, evo, charm, au_FLAME, au_ICE, au_HOLY, au_DARK, perks FROM personal_info WHERE id='{id}' OR name LIKE '%{id}%';")
        except TypeError: await ctx.send("<:osit:544356212846886924> User has not incarnated!"); return
        # pylint: enable=unused-variable
        if str(ctx.message.author.id) not in ['214128381762076672', partner, f'{ctx.author.id}']: await ctx.send("<:osit:544356212846886924> You have to be user's *partner* or *guardians* to view their status!"); return

        # pockets = await self.client.quefe(f"SELECT slot_name, item_id FROM pi_equipment WHERE user_id='{ctx.author.id}' AND slot_type='belt' ORDER BY slot_id ASC LIMIT 3;")
        # pocket_line = ''
        # for pocket in pockets:
        #     pocket_line = pocket_line + f"\n**`{pocket[0]}`**: `{pocket[1]}`"

        if right_hand != 'n/a':
            rh_name = await self.client.quefe(f"SELECT name FROM pi_inventory WHERE existence='GOOD' AND (item_id='{right_hand}' OR item_code='{right_hand}') AND user_id='{str(ctx.message.author.id)}';")
            try: right_hand = f"[`{right_hand}`| **{rh_name[0]}**]"
            except TypeError:
                if right_hand == 'ar13': await self.client._cursor.execute(f"SELECT func_it_reward('{ctx.author.id}', 'ar13', 1);"); rh_name = "Fist"
                else:
                    right_hand, rh_name = await self.client.quefe(f"SELECT item_id, name FROM pi_inventory WHERE user_id='{ctx.author.id}' AND item_code='ar13'")
                    await self.client._cursor.execute(f"UPDATE personal_info SET right_hand='{right_hand}' WHERE id='{ctx.author.id}';")
                right_hand = f"[`{right_hand}`| **{rh_name[0]}**]"
        if left_hand != 'n/a': 
            lh_name = await self.client.quefe(f"SELECT name FROM pi_inventory WHERE existence='GOOD' AND (item_code='{left_hand}' OR item_id='{left_hand}') AND user_id='{str(ctx.message.author.id)}';")
            try: left_hand = f"[`{left_hand}`| **{lh_name[0]}**]"
            except TypeError:
                if left_hand == 'ar13': await self.client._cursor.execute(f"SELECT func_it_reward('{ctx.author.id}', 'ar13', 1);"); lh_name = "Fist"
                else:
                    left_hand, lh_name = await self.client.quefe(f"SELECT item_id, name FROM pi_inventory WHERE user_id='{ctx.author.id}' AND item_code='ar13'")
                    await self.client._cursor.execute(f"UPDATE personal_info SET left_hand='ar13' WHERE id='{ctx.author.id}';"); lh_name = "ar13"
                left_hand = f"`[{left_hand}`| **{lh_name[0]}**]"
        if combat_HANDLING == 'right':
            right_hand = f"__{right_hand}__"
        elif combat_HANDLING == 'left':
            left_hand = f"__{left_hand}__"
        else:
            right_hand = f"__{right_hand}__"
            left_hand = f"__{left_hand}__"

        lmao = {'f': '<:Offgirl_Heart:620029339148484611>', 'm': '<:Offboy_Heart:620029339194490912>'}
        # handling = {'right': '<:right_hand:521197677346553861> Right',
        #             'left': '<:left_hand:521197732162043922> Left',
        #             'both': '<:right_hand:521197677346553861><:left_hand:521197732162043922> Both'}
        # Status

        # LINE LP ==================
        # Calc <LP per block>, <blocks of LP>, <partial block of LP>
        per_LP = (MAX_LP/6)
        block_LP = int(LP/per_LP)
        if block_LP > 6: block_LP = 6
        blockp_LP = (LP/per_LP - int(LP/per_LP))*100
        # Construct line
        LP_line = '<:hp_block:619947505290969138>'*block_LP
        if blockp_LP > 75: LP_line = LP_line + '<:hp_block_34:619947505223991296>'
        elif blockp_LP > 50: LP_line = LP_line + '<:hp_block_24:619947504808755211>'
        elif blockp_LP > 25: LP_line = LP_line + '<:hp_block_14:619947504854630442>'
        # Check if there's partial
        if blockp_LP: LP_line = LP_line + '<:emtpy_block:619947505299226654>'*(6 - block_LP - 1)
        else: LP_line = LP_line + '<:emtpy_block:619947505299226654>'*(6 - block_LP)

        # LINE LP ==================
        # Calc <LP per block>, <blocks of LP>, <partial block of LP>
        per_STA = (MAX_STA/6)
        block_STA = int(STA/per_STA)
        if block_STA > 6: block_STA = 6
        blockp_STA = (STA/per_STA - int(STA/per_STA))*100
        # Construct line
        STA_line = '<:sta_block:619947505248894976>'*block_STA
        if blockp_STA > 75: STA_line = STA_line + '<:sta_block_34:619947504997367850>'
        elif blockp_STA > 50: STA_line = STA_line + '<:sta_block_24:619947505181917196>'
        elif blockp_STA > 25: STA_line = STA_line + '<:sta_block_14:619947505269866516>'
        # Check if there's partial
        if blockp_STA: STA_line = STA_line + '<:emtpy_block:619947505299226654>'*(6 - block_STA - 1)
        else: STA_line = STA_line + '<:emtpy_block:619947505299226654>'*(6 - block_STA)

        #line = f"""{LP_line}"""

        #box = f"\n░░░░ **{name}** | {lmao[gender].capitalize()}, {age} ░░░░\n╟**`Money`** · <:36pxGold:548661444133126185>{money}\n╟**`Merit`** · {merit}\n╟**`Degrees`** · `{degrees}`\n━━━━━╾ {combat_HANDLING.capitalize()} hand ╼━━━━\n╟**`RIGHT`** · {right_hand}\n╟**`LEFT`** · {left_hand}\n━━━━━╾ **`EVO`** {evo} ╼━━━━━━\n**·** `STA` {STA}/{MAX_STA}\n**·** `LP` {LP}/{MAX_LP}\n**·** `STR` {STR}\n**·** `INT` {INTT}"
        box = discord.Embed(title = f"{age} {lmao[gender].capitalize()} | **{name}** ||<:merit_badge:620137704662761512>`{merit}` <:perk:632340885996044298>`{perks}`||", colour = discord.Colour(0x36393F))
        box.add_field(name=f"`LP` · **{LP:,}**/{MAX_LP:,}", value=f"""{LP_line}""", inline=True)
        box.add_field(name='⠀', value='⠀', inline=True)
        box.add_field(name=f"`STA` · **{STA:,}**/{MAX_STA:,}", value=f"""{STA_line}""", inline=True)
        box.add_field(name=f'>>> **`EVO`** · {evo}\n**`STR`** · {STR}\n**`INT`** · {INTT}\n**`CHARM`** · {charm}', value=f"<:right_hand:521197677346553861>{right_hand}", inline=True)
        box.add_field(name='⠀', value='⠀', inline=True)
        box.add_field(name=f'>>> **`FLAME`** · {au_FLAME}\n**`ICE`** · {au_ICE}\n**`HOLY`** · {au_HOLY}\n**`DARK`** · {au_DARK}', value=f"<:left_hand:521197732162043922>{left_hand}", inline=True)
        # box.add_field(name=f'>>> **`merit`** · {merit}{pocket_line}', value=f"{handling[combat_HANDLING]}", inline=True)
        box.set_thumbnail(url=ctx.author.avatar_url)
        # box.set_footer(text=f'', icon_url='https://imgur.com/jkznAfT')

        await ctx.send(embed=box, delete_after=10)
        # await ctx.author.send(embed=box)
        # await ctx.send(":incoming_envelope: **Bang!** <a:blob_snu:531060438142812190> *From Cli with love*")

    # pylint: disable=unused-variable
    @commands.command(aliases=['wb'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def wardrobe(self, ctx, *args):

        raw = list(args)
        mode = 'av'

        try:
            if raw[0] == 'save':
                # Naming
                try: pname = await self.utils.inj_filter(' '.join(args[1:]))
                except IndexError: pname = 'Untitled'

                # Quantity limit check
                if await self.client._cursor.execute(f"SELECT COUNT(preset_id) FROM cosmetic_preset WHERE user_id='{ctx.author.id}' AND stats NOT IN ('CURRENT', 'DEFAULT');") >= 3: await ctx.send(f"<:osit:544356212846886924> You cannot have more than three presets at a time, {str(ctx.message.author.id)}"); return

                await self.client._cursor.execute(f"INSERT INTO cosmetic_preset(user_id, name, stats, avatar_id, bg_code, font_id, blur_rate, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death) SELECT '{ctx.author.id}', '{pname}', 'PRESET', avatar_id, bg_code, font_id, blur_rate, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death FROM cosmetic_preset WHERE user_id='{ctx.author.id}' AND stats='CURRENT';")

                await ctx.send(f":white_check_mark: Created preset **{pname}**. Use `wardrobe presets` to check its *id*."); return

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
                        avatar_id, bg_code, font_id, blur_rate, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death = await self.client.quefe(f"SELECT avatar_id, bg_code, font_id, blur_rate, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death FROM cosmetic_preset WHERE user_id='{ctx.author.id}' AND stats='DEFAULT';")
                    else:
                        avatar_id, bg_code, font_id, blur_rate, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death = await self.client.quefe(f"SELECT avatar_id, bg_code, font_id, blur_rate, co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death FROM cosmetic_preset WHERE user_id='{str(ctx.message.author.id)}' AND preset_id='{raw[1]}';")
                # E: Preset's id not found
                except (IndexError, TypeError): await ctx.send("<:osit:544356212846886924> Preset's id not found!"); return

                # UPDATE current
                await self.client._cursor.execute(f"UPDATE cosmetic_preset SET user_id='{str(ctx.message.author.id)}', name='current of {ctx.message.author.name}', stats='CURRENT', avatar_id='{avatar_id}', bg_code='{bg_code}', font_id='{font_id}', blur_rate={blur_rate}, co_name='{co_name}', co_partner='{co_partner}', co_money='{co_money}', co_age='{co_age}', co_guild='{co_guild}', co_rank='{co_rank}', co_evo='{co_evo}', co_kill='{co_kill}', co_death='{co_death}' WHERE user_id='{str(ctx.message.author.id)}' AND stats='CURRENT';")
                await ctx.send(":white_check_mark: Preset's loaded!"); return
            
            elif raw[0] == 'presets':
                line = ""

                presets = await self.client.quefe(f"SELECT preset_id, name, avatar_id FROM cosmetic_preset WHERE user_id='{str(ctx.message.author.id)}' AND stats NOT IN ('DEFAULT', 'CURRENT');", type='all')

                if not presets: await ctx.send(f"You have not created any presets yet **{ctx.message.author.name}**"); return

                for preset in presets:
                    line = line + f"\n `{preset[0]}` :bust_in_silhouette: **{preset[1]}** |< {preset[2]} >|"

                await ctx.send(f":gear: Your list of presets, {ctx.message.author.mention}\n----------------------{line}"); return

            elif raw[0] in ['av', 'avatar']:
                raise IndexError

            elif raw[0] in ['background', 'bg']:
                mode = 'bg'
                raise IndexError

            elif raw[0] in ['font', 'fnt']:
                mode = 'fnt'
                raise ZeroDivisionError

            else:
                # COLOUR / BLUR
                try:
                    # BLUR
                    if raw[0] == 'blur':
                        try:
                            if raw[1] == 'default':
                                blur_in = 2.6
                            else:
                                blur_in = round(float(''.join(raw[1:6])), 1)
                                # Prep
                                if blur_in < 0: blur_in = 0
                                elif blur_in > 10: blur_in = 10

                            await self.client._cursor.execute(f"UPDATE cosmetic_preset SET blur_rate={blur_in} WHERE user_id='{ctx.author.id}' AND stats='CURRENT';")
                            await ctx.send(f":white_check_mark: Blurriness was changed to **`{blur_in}`**"); return
                        except ValueError:
                            await ctx.send("<:osit:544356212846886924> Invalid blurriness!"); return

                    # COLOUR
                    if raw[1] == 'default':
                        coattri = {'name': 'co_name', 'age': 'co_age', 'money': 'co_money', 'partner': 'co_partner', 'guild': 'co_guild', 'rank': 'co_rank', 'evo': 'co_evo', 'lp': 'co_kill', 'sta': 'co_death'}
                        await self.client._cursor.execute(f"UPDATE cosmetic_preset SET {coattri[raw[0]]}=(SELECT {coattri[raw[0]]} FROM cosmetic_preset WHERE stats='DEFAULT' AND user_id='{ctx.author.id}') WHERE user_id='{ctx.author.id}' AND stats='CURRENT';")
                        await ctx.send(f":white_check_mark: Attribute's colour was reset to default."); return

                    if not re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', raw[1]):
                        await ctx.send("<:osit:544356212846886924> Please use **hexa-decimal** colour code! (e.g. `#FFFFFF`)\n:moyai: You can get them here --> https://htmlcolorcodes.com/"); return
                    
                    coattri = {'name': 'co_name', 'age': 'co_age', 'money': 'co_money', 'partner': 'co_partner', 'guild': 'co_guild', 'rank': 'co_rank', 'evo': 'co_evo', 'lp': 'co_kill', 'sta': 'co_death'}

                    try:
                        await self.client._cursor.execute(f"UPDATE cosmetic_preset SET {coattri[raw[0]]}='{raw[1]}' WHERE user_id='{ctx.author.id}' AND stats='CURRENT';")
                        await ctx.send(f":white_check_mark: Attribute's colour was changed to **`{raw[1]}`**."); return
                    # E: Attributes not found
                    except KeyError: await ctx.send(f":moyai: Please use the following attributes: **`{'`** · **`'.join(list(coattri.keys()))}` · **`blur`**"); return

                # Avatar/Background/Font
                # E: Color not given
                except IndexError:
                    if raw[0].startswith('av'):
                        try:
                            if await self.client._cursor.execute(f"UPDATE cosmetic_preset SET avatar_id='{raw[0]}' WHERE user_id='{ctx.author.id}' AND stats='CURRENT' AND EXISTS (SELECT * FROM pi_avatars WHERE user_id='{ctx.author.id}' AND avatar_id='{raw[0]}');") == 0:
                                await ctx.send(f"<:osit:544356212846886924> You don't own this avatar, **{ctx.author.name}**!"); return
                            await ctx.send(f":white_check_mark: Changed to `{raw[0]}`"); return
                        except mysqlError.IntegrityError: await ctx.send(f"<:osit:544356212846886924> Avatar not found!"); return
                    elif raw[0].startswith('fnt'):
                        try: 
                            if await self.client._cursor.execute(f"UPDATE cosmetic_preset SET font_id='{raw[0]}' WHERE user_id='{ctx.author.id}' AND stats='CURRENT' AND EXISTS (SELECT * FROM pi_fonts WHERE user_id='{ctx.author.id}' AND font_id='{raw[0]}');") == 0:
                                await ctx.send(f"<:osit:544356212846886924> You don't own this font, **{ctx.author.name}**!"); return
                            await ctx.send(f":white_check_mark: Changed to `{raw[0]}`"); return
                        except mysqlError.IntegrityError: await ctx.send(f"<:osit:544356212846886924> Font not found!"); return 
                    else:
                        try: 
                            a = await self.client.quefe(f"SELECT * FROM pi_backgrounds WHERE user_id='{ctx.author.id}' AND bg_code='{raw[0]}';")
                            print(raw[0])
                            print(a)
                            if await self.client._cursor.execute(f"UPDATE cosmetic_preset SET bg_code='{raw[0]}' WHERE user_id='{ctx.author.id}' AND stats='CURRENT' AND EXISTS (SELECT * FROM pi_backgrounds WHERE user_id='{ctx.author.id}' AND bg_code='{raw[0]}');") == 0:

                                await ctx.send(f"<:osit:544356212846886924> You don't own this background, **{ctx.author.name}**!"); return
                            await ctx.send(f":white_check_mark: Changed to `{raw[0]}`"); return
                        except mysqlError.IntegrityError: await ctx.send(f"<:osit:544356212846886924> Background not found!"); return

        # AVATARs
        # E: No avatar given
        except IndexError:
            # Search query
            search_q = ''
            try:
                temp = []
                count = 0
                for k in raw[1:]:
                    k = k.lower()

                    # Light inject-filter
                    k = k.replace("'", '_')
                    k = k.replace('"', '_')

                    temp.append(f" (tag LIKE '{k}%' OR tag LIKE '%{k}' OR tag LIKE '% {k} %') ")
                    count += 1
                    if count == 3: break    # limited to 3 keywords
                if temp: search_q = f"AND {' AND '.join(temp)}"
            except IndexError: pass

            if mode == 'av':
                items2 = await self.client.quefe(f"SELECT avatar_id, name, description FROM model_avatar WHERE avatar_id IN (SELECT avatar_id FROM pi_avatars WHERE user_id='{ctx.author.id}') {search_q} ORDER BY ordera ASC;", type='all')
                if not items2: await ctx.send(f":x: No result..."); return

                items = []
                for item in items2:
                    items.append(item + (self.client.chardict_meta[item[0]], self.utils.smalltext))

                def makeembed(items, top, least, pages, currentpage):
                    line = '' 

                    for item in items[top:least]:
                        
                        line = line + f"""\n`{item[0]}` · **{item[1]}** {item[4](str(item[3]['quantity']))}\n⠀⠀⠀| *"{item[2]}"*"""

                    reembed = discord.Embed(title = f"<a:blob_trashcan:531060436163100697> **{ctx.author.name}**'s avatars", colour = discord.Colour(0x011C3A), description=line)
                    reembed.set_footer(text=f"Total: {len(items)} | Closet {currentpage} of {pages}")
                    return reembed
                    #else:
                    #    await ctx.send("*Nothing but dust here...*")
                
                await self.tools.pagiMain(ctx, items, makeembed)

            else:
                items2 = await self.client.quefe(f"SELECT bg_code, name, description FROM model_background WHERE bg_code IN (SELECT bg_code FROM pi_backgrounds WHERE user_id='{ctx.author.id}') {search_q} ORDER BY ordera ASC;", type='all')
                if not items2: await ctx.send(f":x: No result..."); return

                items = []
                for item in items2:
                    items.append(item + (self.client.bgdict_meta[item[0]], self.utils.smalltext))

                def makeembed(items, top, least, pages, currentpage):
                    line = '' 

                    for item in items[top:least]:
                        
                        line = line + f"""\n`{item[0]}` · **{item[1]}** {item[4](str(item[3]['quantity']))}\n⠀⠀⠀| *"{item[2]}"*"""

                    reembed = discord.Embed(title = f"<a:blob_trashcan:531060436163100697> **{ctx.author.name}**'s backgrounds", colour = discord.Colour(0x011C3A), description=line)
                    reembed.set_footer(text=f"Total: {len(items)} | Closet {currentpage} of {pages}")
                    return reembed
                    #else:
                    #    await ctx.send("*Nothing but dust here...*")
                
                await self.tools.pagiMain(ctx, items, makeembed)

        # FONTs
        except ZeroDivisionError:
            # Search query
            search_q = ''
            try:
                temp = []
                count = 0
                for k in raw[1:]:
                    k = k.lower()

                    # Light inject-filter
                    k = k.replace("'", '_')
                    k = k.replace('"', '_')

                    temp.append(f" (tag LIKE '{k}%' OR tag LIKE '%{k}' OR tag LIKE '% {k} %') ")
                    count += 1
                    if count == 3: break    # limited to 3 keywords
                if temp: search_q = f"AND {' AND '.join(temp)}"
            except IndexError: pass

            items2 = await self.client.quefe(f"SELECT font_id, name, description FROM model_font WHERE font_id IN (SELECT font_id FROM pi_fonts WHERE user_id='{ctx.author.id}') {search_q} ORDER BY ordera ASC;", type='all')
            if not items2: await ctx.send(f":x: No result..."); return

            items = []
            for item in items2:
                items.append(item)

            def makeembed(items, top, least, pages, currentpage):
                line = '' 

                for item in items[top:least]:
                    
                    line = line + f"""\n`{item[0]}` · **{item[1]}**\n⠀⠀⠀| *"{item[2]}"*"""

                reembed = discord.Embed(title = f"<a:blob_trashcan:531060436163100697> **{ctx.author.name}**'s backgrounds", colour = discord.Colour(0x011C3A), description=line)
                reembed.set_footer(text=f"Total: {len(items)} | Closet {currentpage} of {pages}")
                return reembed
                #else:
                #    await ctx.send("*Nothing but dust here...*")
            
            await self.tools.pagiMain(ctx, items, makeembed)



# ================== FUNC ==================

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def rename(self, ctx, *name):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        
        if not name: await ctx.send("<:osit:544356212846886924> `rename [name]`"); return
        name = ' '.join(name)
        if len(name) > 21: await ctx.send("<:osit:544356212846886924> Names can only contain 21 characters."); return

        name = await self.utils.inj_filter(name)

        await self.client.quefe(f"UPDATE personal_info SET name='{name}' WHERE id='{ctx.author.id}';")
        await ctx.send(f":white_check_mark: Your name's changed to **{name}**.")

    @commands.command(aliases=['evo'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def evolve(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        perks, evo, LP, max_LP, max_STA, strr, intt, au_FLAME, au_ICE, au_HOLY, au_DARK, charm = await self.client.quefe(f"SELECT perks, EVO, LP, max_LP, max_STA, STR, INTT, au_FLAME, au_ICE, au_HOLY, au_DARK, charm FROM personal_info WHERE id='{ctx.author.id}';")

        raw = list(args)

        try:
            if raw[0].isdigit():
                raise IndexError

            if raw[0] == 'transfuse':
                if evo < 6: await ctx.send(f"<:osit:544356212846886924> Your evolution has to be more than 6 to proceed transfusion!"); return
                if perks == 0: await ctx.send(f"<:osit:544356212846886924> You have no perks."); return
                try: target = ctx.message.mentions[0]
                except IndexError: await ctx.send("<:osit:544356212846886924> Please mention the one you want!"); return

                t_evo = await self.client.quefe(f"SELECT EVO FROM personal_info WHERE id='{target.id}';")
                if not t_evo: await ctx.send("<:osit:544356212846886924> User has not incarnated yet!"); return

                rate = abs(evo - t_evo)
                if rate == 10: rate = 0
                if rate > 10: rate = 10
                if await self.utils.percenter(9 - rate):
                    await ctx.send("<:zapp:524893958115950603> Transfusion succeeded!")
                    await self.client._cursor.execute(f"UPDATE personal_info SET perks=perks-1 WHERE id='{ctx.author.id}'; UPDATE personal_info SET EVO=EVO+1 WHERE id='{target.id}';"); return
                else:
                    try: loss = round(LP/(10 - rate))
                    except ZeroDivisionError: loss = 1

                    await ctx.send(f"<:osit:544356212846886924> Transfusion failed! You've lost **{loss} LP**, **{ctx.author.name}** and **{target.name}**.")
                    await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-{loss} WHERE id='{ctx.author.id}' OR id='{target.name}';"); return

            elif raw[0] == 'mutate':
                msg = await ctx.send(f"<:zapp:524893958115950603> All your basic status will *randomly change*. You may even die.\n<a:RingingBell:559282950190006282> **ARE**. **YOU**. **SURE**?")

                await msg.add_reaction("\U00002705")

                try: await self.client.wait_for('reaction_add', timeout=20, check=lambda reaction, user: user.id == ctx.author.id and reaction.message.id == msg.id)
                except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request decline!"); return

                LP, MAX_LP, STA, STR, INT = await self.client.quefe(f"SELECT LP, MAX_LP, STA, STR, INT FROM personal_info WHERE id='{ctx.author.id}';")
                await self.client._cursor.execute(f"UPDATE personal_info SET perks=perks-1, LP={random.randint(0, LP*2)}, MAX_LP={random.randint(0, MAX_LP*2)}, STA={random.randint(0, STA*2)}, STR={random.randint(0, int(STR*2))}, INT={random.randint(0, int(INT*2))} WHERE id='{ctx.author.id}';")
                await ctx.send("<:osit:544356212846886924> Mutation done! Check your profile immidiately..."); return

            elif raw[0] == 'reset':
                evo_return = self.perk_calc(0, addition=evo)
                msg = await ctx.send(f"{ctx.author.mention}, resetting from <:zapp:524893958115950603>{evo} to <:zapp:524893958115950603>0.\nYou will fully receive your <:perk:632340885996044298>{evo_return}. Continue?")

                await msg.add_reaction("\U00002705")

                try: await self.client.wait_for('reaction_add', timeout=20, check=lambda reaction, user: user.id == ctx.author.id and reaction.message.id == msg.id)
                except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request decline!"); return

                await self.client._cursor.execute(f"UPDATE personal_info SET charm={random.randint(5, 20)}, perks=perks+{evo_return}, EVO=0, STR=0.5, INTT=0, MAX_STA=100, STA=MAX_STA, MAX_LP=1000, LP=MAX_LP, au_FLAME=0, au_ICE=0, au_HOLY=0, au_DARK=0 WHERE id='{ctx.author.id}';")
                await ctx.send(":white_check_mark: Done")
                return

            # EVOLVING =================================
            try:
                evos = int(raw[1])
                if not evos: evos = 1
                elif evos > 50: evos = 50
            except (IndexError, TypeError): evos = 1

            evo_dict = {
                'lp': [f"UPDATE personal_info SET MAX_LP=MAX_LP+value_in_here, EVO=EVO+{evos}, perks=perks-perk_cost_here WHERE id='user_id_here' AND perks >= perk_cost_here;", max_LP],
                'sta': [f"UPDATE personal_info SET MAX_STA=MAX_STA+value_in_here, EVO=EVO+{evos}, perks=perks-perk_cost_here WHERE id='user_id_here' AND perks >= perk_cost_here;", max_STA],
                'str': [f"UPDATE personal_info SET STR=STR+value_in_here, EVO=EVO+{evos}, perks=perks-perk_cost_here WHERE id='user_id_here' AND perks >= perk_cost_here;", strr],
                'int': [f"UPDATE personal_info SET INTT=INTT+value_in_here, EVO=EVO+{evos}, perks=perks-perk_cost_here WHERE id='user_id_here' AND perks >= perk_cost_here;", intt],
                'flame': [f"UPDATE personal_info SET au_FLAME=au_FLAME+value_in_here, EVO=EVO+{evos}, perks=perks-perk_cost_here WHERE id='user_id_here' AND perks >= perk_cost_here;", au_FLAME],
                'ice': [f"UPDATE personal_info SET au_ICE=au_ICE+value_in_here, EVO=EVO+{evos}, perks=perks-perk_cost_here WHERE id='user_id_here' AND perks >= perk_cost_here;", au_ICE],
                'holy': [f"UPDATE personal_info SET au_HOLY=au_HOLY+value_in_here, EVO=EVO+{evos}, perks=perks-perk_cost_here WHERE id='user_id_here' AND perks >= perk_cost_here;", au_HOLY],
                'dark': [f"UPDATE personal_info SET au_DARK=au_DARK+value_in_here, EVO=EVO+{evos}, perks=perks-perk_cost_here WHERE id='user_id_here' AND perks >= perk_cost_here;", au_DARK],
                'charm': [f"UPDATE personal_info SET charm=charm+value_in_here, EVO=EVO+{evos}, perks=perks-perk_cost_here WHERE id='user_id_here' AND perks >= perk_cost_here;", charm]
                }

            if await self.client._cursor.execute(evo_dict[raw[0].lower()][0].replace('user_id_here', str(ctx.author.id)).replace('value_in_here', str(self.compound_calc(evos, self.evo_func[raw[0]], evo_dict[raw[0].lower()][1]))).replace('perk_cost_here', str(self.perk_calc(evo, addition=evos)))) == 0:
                await ctx.send("<:osit:544356212846886924> Not enough perks!"); return

            await ctx.send("<:zapp:524893958115950603> Done. You may use `profile` to check."); return

        # E: Attributes not found
        except KeyError:
            await ctx.send("<:osit:544356212846886924> Invalid attribute!"); return

        # E: Attri not given
        except IndexError:
            try:
                evos = int(raw[0])
                if not evos: evos = 1
                elif evos > 50: evos = 50
            except (IndexError, TypeError): evos = 1

            p_max_LP = self.compound_calc(evos, self.evo_func['lp'], max_LP)
            p_max_STA = self.compound_calc(evos, self.evo_func['sta'], max_STA)
            p_strr = self.compound_calc(evos, self.evo_func['str'], strr)
            p_intt = self.compound_calc(evos, self.evo_func['sta'], intt)
            p_FLAME = self.compound_calc(evos, self.evo_func['flame'], au_FLAME)
            p_ICE = self.compound_calc(evos, self.evo_func['ice'], au_ICE)
            p_HOLY = self.compound_calc(evos, self.evo_func['holy'], au_HOLY)
            p_DARK = self.compound_calc(evos, self.evo_func['dark'], au_DARK)
            p_charm = self.compound_calc(evos, self.evo_func['charm'], charm)

            left_collumn = f"""**`LP`**⠀⠀⠀{max_LP:,} ▸ **{(max_LP + p_max_LP):,}** (+{p_max_LP:,})
                **`STA`**⠀⠀{max_STA:,} ▸ **{(max_STA + p_max_STA):,}** (+{p_max_STA:,})
                **`STR`**⠀⠀{strr:,} ▸ **{(strr + p_strr):,}** (+{p_strr:,})
                **`INT`**⠀⠀{intt:,} ▸ **{(intt + p_intt)}** (+{p_intt:,})
            """

            right_collumn = f"""**`FLAME`**⠀{au_FLAME} ▸ **{au_FLAME + p_FLAME}** (+{p_FLAME})
                **`ICE`**⠀⠀⠀{au_ICE} ▸ **{au_ICE + p_ICE}** (+{p_ICE})
                **`HOLY`**⠀⠀{au_HOLY} ▸ **{au_HOLY + p_HOLY}** (+{p_HOLY})
                **`DARK`**⠀⠀{au_DARK} ▸ **{au_DARK + p_DARK}** (+{p_DARK})
                **`CHARM`**⠀{charm} ▸ **{charm + p_charm}** (+{p_charm})
            """

            vemb = discord.Embed(colour=0x011C3A)
            vemb.add_field(name=f"<:zapp:524893958115950603> **Evolution:** {evo:,} ▸ **{(evo+evos):,}**", value=f">>> {left_collumn}", inline=True)
            perk_cost = self.perk_calc(evo, addition=evos)
            if perks >= perk_cost: temp = f"**{perks:,}**/**{perk_cost:,}**"
            else: temp = f"{perks:,}/**{perk_cost:,}**"
            vemb.add_field(name=f"<:perk:632340885996044298> **Perk cost:** {temp}", value=f">>> {right_collumn}", inline=True)
            # vemb.set_thumbnail(url=ctx.author.avatar_url)
            vemb.set_footer(text="Use <evolve [attribute] {times}> to upgrade an attribute", icon_url=ctx.author.avatar_url)

            await ctx.send(embed=vemb, delete_after=30); return

    @commands.command()
    @commands.cooldown(1, 3, type=BucketType.user)
    async def pocket(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        # POCKETS ==========================================
        if not args:
            items = await self.client.quefe(f"SELECT slot_id, slot_name, item_id FROM pi_equipment WHERE user_Id='{ctx.author.id}';", type='all')

            def makeembed(items, top, least, pages, currentpage):
                line = '' 

                for item in items[top:least]:
                    line = line + f"""\n[`{item[0]}`| **{item[1]}**] == `{item[2]}`"""

                reembed = discord.Embed(title = f"<:armor_p:619743809286438929> Pocket of **{ctx.author.name}**", colour = discord.Colour(0x011C3A), description=line)
                reembed.set_footer(text=f"Total: {len(items)} | Closet {currentpage} of {pages}")
                return reembed
                #else:
                #    await ctx.send("*Nothing but dust here...*")
            
            await self.tools.pagiMain(ctx, items, makeembed)

            return


        # RENAME ===========================================
        if args[0] == 'rename':
            # Handle
            try: handle = args[1].lower()
            except IndexError: await ctx.send(f"<:osit:544356212846886924> Missing pocket's name or ID"); return

            # Name
            try: name = args[2].lower()[:13]
            except IndexError: await ctx.send(f"<:osit:544356212846886924> Missing name to rename"); return            

            # SLOT_ID
            if handle.isdigit():
                temp = f"AND slot_id={handle}"

            # SLOT_NAME
            else:
                temp = f"AND slot_name LIKE '%{handle}%'"

            if await self.client._cursor.execute(f"UPDATE pi_equipment SET slot_name='{name}' WHERE user_id='{ctx.author.id}' {temp};") == 0:
                await ctx.send(f"<:osit:544356212846886924> Pocket name or ID not found"); return
            await ctx.send(f"<:armor_p:619743809286438929> Renamed `{handle}` to **`{name}`**! (Limited to 12 chars)"); return



        # EQUIPMENT (w/ item_id, handle) ===================
        # Handle
        try: handle = args[0]
        except IndexError: await ctx.send(f"<:osit:544356212846886924> Missing pocket's name or ID"); return

        # Item ID
        try: item_id = args[1]
        except IndexError: await ctx.send(f"<:osit:544356212846886924> Missing item ID"); return

        # SLOT_ID
        if handle.isdigit():
            temp = f"AND slot_id={handle}"

        # SLOT_NAME
        else:
            temp = f"AND slot_name LIKE '%{handle}%'"

        if await self.client._cursor.execute(f"UPDATE pi_equipment SET item_id='{item_id}' WHERE user_id='{ctx.author.id}' AND item_id<>'{item_id}' {temp};") == 0:
            await self.client._cursor.execute(f"UPDATE pi_equipment SET item_id='n/a' WHERE user_id='{ctx.author.id}' AND item_id='{item_id}' {temp};")
            await ctx.send(f"<:armor_p:619743809286438929> Item `{item_id}` is put out of pocket `{handle}`"); return
        else: await ctx.send(f"<:armor_p:619743809286438929> Item `{item_id}` is put in pocket `{handle}`"); return

    @commands.command()
    @commands.cooldown(1, 3, type=BucketType.user)
    async def degrees(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        degrees = await self.client.quefe(f"SELECT degree, major FROM pi_degrees WHERE user_id='{ctx.author.id}';", type='all')
        line = ''

        for d in degrees:
            line = line + f" `{d[0]} of {d[1]}` **|**"

        await ctx.send(line, delete_after=20)



# ================== TOOLS ==================

    def compound_calc(self, itertime, func, value):
        """Func has to return what they're passed"""

        i = 1
        surplus = 0
        while i <= itertime:
            surplus += func(value + surplus)
            i += 1

        if isinstance(surplus, float): surplus = round(surplus, 2)
        return surplus

    def perk_calc(self, evo, addition=1):
        """Calculate the NEXT EVO of the given evo"""

        return int(sum([i**2.713 for i in range(evo+1, evo+addition+1)]))

    def lp_calc(self, value):
        v = int(round(float(value)/100*2))
        if v > 400: return 150
        elif v > 300: return 125
        elif v > 200: return 100
        elif v > 100: return 50
        else: return v
        
    def sta_calc(self, value):
        v = int(round(float(value)/100*5))
        if v > 400: return 120
        elif v > 300: return 85
        elif v > 200: return 50
        elif v > 100: return 25
        else: return v

    def str_calc(self, value):
        return 0.1

    def int_calc(self, value):
        return 0.1

    def flame_calc(self, value):
        return 0.1

    def ice_calc(self, value):
        return 0.1

    def holy_calc(self, value):
        return 0.1

    def dark_calc(self, value):
        return 0.1

    def charm_calc(self, value):
        return 1

    @commands.command()
    async def test_incarnate(self, ctx):
        try:
            r, g, n = await self.tools.incarnateData_collect(ctx, self.aui)
        except TypeError: await ctx.send(f"<:osit:544356212846886924> Session is cancelled, **{ctx.author.name}**!"); return
        # await ctx.send(f"{r} {g} {n}")
        await ctx.send(f">>> **{ctx.author.mention}, welcome to The Pralayer!**\nThis world is hard and complex, thus you will need every help you can.\nFor now, my advice is using `tutorial 1` to at least know what to do with this bot.", embed=discord.Embed().set_image(url='https://imgur.com/e8cIazx.gif'))



def setup(client):
    client.add_cog(avaPersonal(client))
