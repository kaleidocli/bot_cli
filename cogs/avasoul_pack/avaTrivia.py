import asyncio
import concurrent
import random
from functools import partial
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors

from .avaTools import avaTools
from .avaUtils import avaUtils



class avaTrivia(commands.Cog):

    def __init__(self, client):
        self.client = client

        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)

        self.topCommands = {'rich': self.toprich,
                            'pvp': self.toppvp,
                            'death': self.topdeath,
                            'merit': self.topmerit,
                            'duel': self.topduel,
                            'hunter': self.tophunter}

        self.biome = {'SAVANNA': 'https://imgur.com/qc1NNIu.png',
                    'JUNGLE': 'https://imgur.com/3j786qW.png',
                    'DESERT': 'https://imgur.com/U0wtRU7.png',
                    'RUIN': 'https://imgur.com/O8rHzCR.png',
                    'FROST': 'https://imgur.com/rjwiDU4.png',
                    'MOUNTAIN': 'https://imgur.com/cxwSH7m.png',
                    'OCEAN': 'https://imgur.com/fQFO2b4.png'}
        self.mob_icon = {'mob': '<:mhw_bonewhite:626450002952323072>',
                        'boss': '<:mhw_bonegold:626450069188640771>'}
        self.effect_icon = {'poison': '<:mhw_poison:626533532898033664>',
                            'paralysis': '<:mhw_paralysis:626533532642312193>',
                            'sleep': '<:mhw_sleep:626533532956622858>',
                            'stun': '<:mhw_stun:626533532948365322>',
                            'bleed': '<:mhw_bleeding:626533532696707103>'}

        print("|| Trivia ---- READY!")



# ================== EVENTS ==================

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     print("|| Trivia ---- READY!")



# ================== TRIVIA SYS ==================

    @commands.command(aliases=['skt'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def sekaitime(self, ctx):
        year, month, day, hour, minute = await self.client.loop.run_in_executor(None, self.utils.time_get)
        calendar_format = {'month': {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}}
        a = ['st', 'nd', 'rd']
        if day%10 in [1, 2, 3]:
            postfix = a[(day%10) - 1]
        else: postfix = 'th'
        await ctx.send(f"__=====__ `{hour:02d}:{minute:02d}` :calendar_spiral: {calendar_format['month'][month]} {day}{postfix}, {year} __=====__")

    @commands.command(aliases=['worldinfo'])
    @commands.cooldown(1, 30, type=BucketType.user)
    async def sekaiinfo(self, ctx):
        users = await self.client.quefe(f"SELECT COUNT(id) FROM personal_info;")
        races = await self.client.quefe(f"SELECT COUNT(race_code) FROM model_race;")
        c_quests = await self.client.quefe(f"SELECT COUNT(user_id) FROM pi_quests;")
        quests = await self.client.quefe(f"SELECT COUNT(quest_code) FROM model_quest;")
        animals = await self.client.quefe(f"SELECT COUNT(ani_code) FROM model_animal;")
        c_mobs = await self.client.quefe(f"SELECT COUNT(id_counter) FROM environ_mob;")
        mobs = await self.client.quefe(f"SELECT COUNT(mob_code) FROM environ_diversity;")
        formulas = await self.client.quefe(f"SELECT COUNT(formula_code) FROM model_formula;")
        ingredients = await self.client.quefe(f"SELECT COUNT(ingredient_code) FROM model_ingredient;")
        items = await self.client.quefe(f"SELECT COUNT(item_code) FROM model_item;")
        p_items = await self.client.quefe(f"SELECT COUNT(item_id) FROM pi_inventory;")

        year, month, day, hour, minute = await self.client.loop.run_in_executor(None, self.utils.time_get)

        reembed = discord.Embed(title='**T H E  P R A L A E Y R**', description=f"```Structured by 5 different regions, Pralaeyr has lasted for {year} years, {month} months, {day} days, {hour} hours and {minute} minutes```", colour = discord.Colour(0x011C3A))
        reembed.add_field(name=":couple: Population", value=f"· `{users[0]}`, with `{races[0]}` different races.")
        reembed.add_field(name=":smiling_imp: Mobs and Animals", value=f"· `{c_mobs[0]}` alive mobs, with `{mobs[0]}` different kind of mobs.\n· `{animals[0]}` kind of animals.")
        reembed.add_field(name=":package: Items and Ingredients", value=f"· `{p_items[0]}` current items, with `{ingredients[0]}` kind of ingredients and `{items[0]}` kind of items.")
        reembed.add_field(name=":tools: Formulas and Quests", value=f"· `{formulas[0]}` formulas.\n· `{c_quests[0]}` current quests, with `{quests[0]}` different kind of quests.")

        await ctx.send(embed=reembed)

    @commands.command(aliases=['regions'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def maps(self, ctx, *args):
        # Get cur_PLACE
        cur_PLACE = await self.client.quefe(f"SELECT cur_PLACE FROM personal_info WHERE id='{ctx.author.id}';")
        regions = await self.client.quefe(f"SELECT environ_code, name, description, illulink, border_X, border_Y, biome, land_slot, cuisine, goods, port FROM environ WHERE type='REGION' ORDER BY ord ASC;", type='all')

        async def makeembed(curp, pages, currentpage):
            region = regions[curp]
            players = await self.client._cursor.execute(f"SELECT * FROM personal_info WHERE cur_PLACE='{region[0]}';")
            mobs = await self.client._cursor.execute(f"SELECT * FROM environ_mob WHERE region='{region[0]}';")

            reembed = discord.Embed(title = f":map: `{region[0]}`|**{region[1]}**", description = f"""```dsconfig
    {region[2]}```""", colour = discord.Colour(0x011C3A))
            reembed.add_field(name=":bar_chart: Entities", value=f"╟`Players` · **{players}**\n╟`Mobs` · **{mobs}**", inline=True)
            reembed.add_field(name=":bar_chart: Terrain", value=f"╟`Area` · {region[4]}m x {region[5]}m\n╟`Land` · **{region[7]}** slots\n╟`Biomes` · *{region[6].replace(' - ', '*, *')}*", inline=True)
            reembed.set_thumbnail(url=self.biome[region[6].split(' - ')[0]])
            if region[3]: reembed.set_image(url=region[3])
            return reembed, region[0]
            #else:
            #    await ctx.send("*Nothing but dust here...*")

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
        if pages > 1:
            #Top-left   #Left   #Pick   #Right   #Top-right   #Top-right
            await self.tools.pageButtonAdd(msg, reaction=["\U000023ee", "\U00002b05", "\U0001f44b", "\U000027a1", "\U000023ed", "\U0001f50e"])
        else: return
        await asyncio.sleep(1)

        while True:
            try:
                reaction, user = await self.tools.pagiButton(timeout=20, check=lambda r, u: u == ctx.author)
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

                    try: m = await self.client.wait_for('message', timeout=15, check=lambda m: m.channel == ctx.channel and m.author == ctx.author)
                    except asyncio.TimeoutError: await ctx.send(f"<:osit:544356212846886924> Requested time-out!"); return

                    for em in emli:
                        if em[1] == m.content: tembed = em[0]; break
                    await temsg.delete()
                    try: await msg.edit(embed=tembed)
                    except NameError: await ctx.send("<:osit:544356212846886924> Region not found :<"); continue
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == '\U0001f44b':
                    for r in regions:
                        if r[0] == emli[cursor][1]:
                            await self.map_engine(ctx, pack=(r[0], r[1], r[3], r[10]))
                            return
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

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def map(self, ctx, *args):
        # Get cur_PLACE
        cur_PLACE = await self.client.quefe(f"SELECT cur_PLACE FROM personal_info WHERE id='{ctx.author.id}';")
        try:
            cur_PLACE = cur_PLACE[0]
        except (TypeError, IndexError):
            cur_PLACE = 'region.0'
        region = await self.client.quefe(f"SELECT environ_code, name, description, illulink, border_X, border_Y, biome, land_slot, cuisine, goods, port FROM environ WHERE environ_code='{cur_PLACE}';")

        # Get map info
        if region[10]: bundle = await self.client.quefe(f"""SELECT environ_code, name, pass_note FROM environ WHERE environ_code IN ('{"', '".join(region[10].split(' | '))}') ORDER BY environ_code ASC;""", type='all')


        # FIRST ==============
        async def makeembed_2():
            line = ''; swi = 0
            players = await self.client._cursor.execute(f"SELECT * FROM personal_info WHERE cur_PLACE='{region[0]}';")
            mobs = await self.client._cursor.execute(f"SELECT * FROM environ_mob WHERE region='{region[0]}';")
            mob_types = await self.client.quefe(f"SELECT mob_code, quantity FROM environ_diversity WHERE environ_code='{region[0]}';", type='all')
            npcs = await self.client._cursor.execute(f"SELECT DISTINCT entity_code FROM environ_interaction WHERE region='{region[0]}' AND entity_code LIKE 'p%';")
            try: shop_quantity = len(region[9].split(' - '))
            except AttributeError: shop_quantity = 0
            try: trader_quantity = len(region[8].split(' - '))
            except AttributeError: trader_quantity = 0

            for m in mob_types:
                if swi == 0: line = line + f"╟**`{m[0]}`**`[{m[1]}]`"; swi += 2
                elif swi < 4: line = line + f"⠀·⠀**`{m[0]}`**`[{m[1]}]`"; swi += 1
                elif swi == 4: line = line + f"\n╟**`{m[0]}`**`[{m[1]}]`"; swi = 2

            reembed = discord.Embed(title = f":map: `{region[0]}`|**{region[1]}**", description = f"""```dsconfig
    {region[2]}```""", colour = discord.Colour(0x011C3A))
            reembed.add_field(name=":bar_chart: Entities", value=f"╟`Players` · **{players}**\n╟`Mobs` · **{mobs}**\n╟`NPCs` · **{npcs}**", inline=True)
            reembed.add_field(name=":bar_chart: Terrain", value=f"╟`Area` · {region[4]}m x {region[5]}m\n╟`Land` · **{region[7]}** slots\n╟`Biomes` · *{region[6].replace(' - ', '*, *')}*", inline=True)
            reembed.add_field(name=":scales: Economy", value=f"╟`Shop` · Selling **{shop_quantity}** items\n╟`Traders` · Selling **{trader_quantity}** ingredients", inline=True)
            if line: reembed.add_field(name=f":smiling_imp: Diversity ({len(mob_types)})", value=line, inline=True)
            reembed.set_thumbnail(url=self.biome[region[6].split(' - ')[0]])
            if region[3]: reembed.set_image(url=region[3])
            return reembed

        # PORT ============
        def makeembed(items, top, least, pages, currentpage):
            """environ_code, name, illulink, port = pack"""
            bundle = items
            descr = ''

            # Mapping
            if bundle:
                for b in bundle[top:least]:
                    if not b[2]: pass_note = ''
                    else: pass_note = f"||{self.utils.smalltext(b[2])}||"
                    descr += f"<:wooden_door:636068648985034753> `{b[0]}`|**{b[1]}**\n> {pass_note}\n"

            reembed = discord.Embed(title=f"""{len(bundle)} portals in this map:""", description=descr, colour = discord.Colour(0x011C3A))

            return reembed

        pages = len(bundle)
        if not pages: pages = 1
        item_per_page = 4
        currentpage = 1
        cursor = 0

        emli = []
        emli.append(await makeembed_2())
        for _ in range(pages):
            emli.append(makeembed(bundle, currentpage*item_per_page-item_per_page, currentpage*item_per_page, pages, currentpage))
            currentpage += 1

        msg = await ctx.send(embed=emli[cursor])
        await self.tools.pageButtonAdd(msg)

        # Button-ing
        while True:
            try:
                reaction, user = await self.tools.pagiButton(check=lambda r, u: r.message.id == msg.id and u.id == ctx.author.id, timeout=60)
                cursor = await self.tools.pageTurner(msg, reaction, user, (cursor, pages, emli))
            except concurrent.futures.TimeoutError:
                pass


    async def map_engine(self, ctx, pack=None):
        """environ_code, name, illulink, port = pack"""

        if pack[3]:
            bundle = await self.client.quefe(f"""SELECT environ_code, name, pass_note FROM environ WHERE environ_code IN ('{"', '".join(pack[3].split(' | '))}') ORDER BY environ_code ASC;""", type='all')

        def makeembed(items, top, least, pages, currentpage):
            bundle, pack = items
            descr = ''

            # Mapping
            if bundle:
                for b in bundle[top:least]:
                    if not b[2]: pass_note = ''
                    else: pass_note = f"||{self.utils.smalltext(b[2])}||"
                    descr += f"<:wooden_door:636068648985034753> `{b[0]}`|**{b[1]}** {pass_note}\n"

            reembed = discord.Embed(description=f"""```ini
[{pack[0]}] {pack[1]}```{descr}""", colour = discord.Colour(0x011C3A))
            if pack[2]: reembed.set_thumbnail(url=pack[2])

            return reembed

        if bundle: await self.tools.pagiMain(ctx, (bundle, pack), makeembed, pair=True, item_per_page=4, timeout=20)
        else: await self.tools.pagiMain(ctx, (bundle, pack), makeembed, pair=True, item_per_page=4, timeout=20, pair_sample=1)

    @commands.command()
    @commands.cooldown(1, 2, type=BucketType.user)
    async def pralaeyr(self, ctx):
        await ctx.send("https://media.discordapp.net/attachments/381963689470984203/546796245994307595/map_description.png")

    @commands.command()
    @commands.cooldown(1, 2, type=BucketType.user)
    async def mobs(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        mobs = await self.client.quefe(f"SELECT mob_code, name, description, branch, evo, lp, str, chain, speed, au_FLAME, au_ICE, au_HOLY, au_DARK, illulink, effect, attack_type, defense_physic, defense_magic FROM model_mob WHERE mob_code IN (SELECT mob_code FROM environ_diversity WHERE environ_code=(SELECT cur_PLACE FROM personal_info WHERE id='{ctx.author.id}'));", type='all')
        try:
            mobs = list(mobs)
            mobs.sort(key=lambda v: v[3], reverse=True)
        except IndexError: await ctx.send(f":x: There's no mob in this region it seems..."); return

        async def makeembed(curp, pages, currentpage):
            mob = mobs[curp]

            # Visualize effects
            try:
                effect = '> '
                for ep in mob[14].split(' || '):
                    ep = ep.split(' - ')
                    effect += f"{self.effect_icon[ep[0]]}`{ep[2]}%` "
            except (IndexError, KeyError):
                effect = '----------------------'

            box = discord.Embed(title=f"{self.mob_icon[mob[3]]} `{mob[0]}`|**{mob[1]}**", description=f"```{mob[2]}```", colour = discord.Colour(0x36393F))
            box.add_field(name=f'>>> **`LP`** · {mob[5]}\n**`STR`** · {mob[6]}\n**`CHAIN`** · {mob[7]}\n**`SPEED`** · {mob[8]}\n**`DEFPY`** · {mob[16]}', value=effect)
            box.add_field(name=f'>>> **`FLAME`** · {mob[9]}\n**`ICE`** · {mob[10]}\n**`HOLY`** · {mob[11]}\n**`DARK`** · {mob[12]}\n**`DEFMA`** · {mob[17]}', value=f"> `EVO.{mob[4]}`")

            if mob[12]: box.set_thumbnail(url=mob[13])
            return box
        
        async def attachreaction(msg):
            await msg.add_reaction("\U000023ee")    #Top-left
            await msg.add_reaction("\U00002b05")    #Left
            await msg.add_reaction("\U000027a1")    #Right
            await msg.add_reaction("\U000023ed")    #Top-right

        pages = len(mobs)
        currentpage = 1
        cursor = 0

        emli = []
        for curp in range(pages):
            myembed = await makeembed(curp, pages, currentpage)
            emli.append(myembed)
            currentpage += 1

        msg = await ctx.send(embed=emli[cursor])
        if pages > 1: await attachreaction(msg)
        else: return

        while True:
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=20, check=lambda reaction, user: user.id == ctx.author.id and reaction.message.id == msg.id)
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



# ================== PLAYERS ==================

    @commands.command(aliases=['leaderboard'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def top(self, ctx, *args):

        if not args:
            await ctx.send(f":military_medal: Available Leaderboards: `{'` · `'.join(list(self.topCommands.keys()))}`"); return

        try:
            await self.topCommands[args[0]](ctx)
        except KeyError: await ctx.send("<:osit:544356212846886924> Leaderboard not found."); return

    async def toprich(self, ctx):
        ret = await self.client.quefe(f"SELECT name, age, money FROM personal_info ORDER BY money DESC LIMIT 10", type='all')

        line = ''; count = 0
        for u in ret:
            count += 1
            line = line + f"{count} | **{u[0]}** ({u[1]}) with <:36pxGold:548661444133126185> **{u[2]}**\n"

        await ctx.send(embed=discord.Embed(title=":military_medal: Top 10 richest Remnants!", description=line, colour=0xFFC26F))

    async def topmerit(self, ctx):
        ret = await self.client.quefe(f"SELECT name, age, merit FROM personal_info ORDER BY merit DESC LIMIT 10", type='all')

        line = ''; count = 0
        for u in ret:
            count += 1
            line = line + f"{count} | **{u[0]}** ({u[1]}) with a merit **{u[2]}**\n"

        await ctx.send(embed=discord.Embed(title=":military_medal: Top 10 honorable Remnants!", description=line, colour=0xFFC26F))

    async def toppvp(self, ctx):
        ret = await self.client.quefe(f"SELECT name, EVO, kills FROM personal_info ORDER BY kills DESC LIMIT 10", type='all')

        line = ''; count = 0
        for u in ret:
            count += 1
            line = line + f"{count} | **{u[0]}** (`EVO-{u[1]}`) with **{u[2]}** kills\n"

        await ctx.send(embed=discord.Embed(title=":military_medal: Top 10 player killers!", description=line, colour=0xFFC26F))

    async def topdeath(self, ctx):
        ret = await self.client.quefe(f"SELECT name, EVO, deaths FROM personal_info ORDER BY deaths DESC LIMIT 10", type='all')

        line = ''; count = 0
        for u in ret:
            count += 1
            line = line + f"{count} | **{u[0]}** (`EVO-{u[1]}`) with **{u[2]}** deaths\n"

        await ctx.send(embed=discord.Embed(title=":military_medal: Top 10 highest death rate!", description=line, colour=0xFFC26F))

    async def topduel(self, ctx):
        ret = await self.client.quefe(f"SELECT (SELECT name FROM personal_info WHERE id=user_id), duel_win, duel_lost FROM misc_status ORDER BY duel_win DESC LIMIT 10", type='all')

        line = ''; count = 0
        for u in ret:
            count += 1
            line = line + f"{count} | **{u[0]}** have won **{u[1]}** duels and lost **{u[2]}** duels\n"

        await ctx.send(embed=discord.Embed(title=":military_medal: Top 10 card duelists!", description=line, colour=0xFFC26F))

    async def tophunter(self, ctx):
        ret = await self.client.quefe(f"SELECT (SELECT name FROM personal_info WHERE id=user_id), mob, boss FROM pi_mobs_collection ORDER BY mob DESC, boss DESC LIMIT 10", type='all')
        curuser = await self.client.quefe(f"SELECT user_id, mob, boss FROM pi_mobs_collection WHERE user_id='{ctx.author.id}';")

        line = ''; count = 0
        for u in ret:
            count += 1
            line = line + f"{count} | **{u[0]}** have slayed **{u[1]}** monsters and raided **{u[2]}** bosses.\n"

        if curuser: line = line + f"⠀\n> **{ctx.author.name}**, you've slayed **{curuser[1]}** monsters and raided **{curuser[2]}** bosses!"

        await ctx.send(embed=discord.Embed(title=":military_medal: Top 10 monster hunters of current region!", description=line, colour=0xFFC26F))



# ================== PERSONAL ==================

    @commands.command(aliases=['noti'])
    @commands.cooldown(1, 10, type=BucketType.user)
    async def notification(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        on_cd = []; off_cd = []; interas = []

        # COMMANDs
        for cmd, cmd_tag in zip(['daily', 'daily quest', 'work', 'trader', 'merge', 'sex'], ['daily', 'dailyquest', 'work', 'trade', 'merge', 'sex']):
            time = await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.ttl, f"{cmd_tag}{ctx.author.id}"))
            try:
                # On cooldown
                if time == None or time <= 0:
                    off_cd.append(f"<:exclamation_yellow:626639669995503616> Command **`{cmd}`**")
                # Off cooldown
                else:
                    on_cd.append(f"\n:stopwatch: Command **`{cmd}`**: `{timedelta(seconds=int(time))}`")
            # Off cooldown
            except TypeError:
                on_cd.append(f"\n:stopwatch: Command **`{cmd}`**: `{timedelta(seconds=int(time))}`")

        # INTERACTIONs
        tee = await self.client.quefe(f"SELECT target_code, flag FROM pi_relationship WHERE user_id='{ctx.author.id}' AND flag<>'n/a'", type='all')
        for t in tee:
            temp = await self.client.quefe(f"SELECT npc_code, name FROM model_npc WHERE npc_code='{t[0]}';")
            temp2all = await self.client.quefe(f"SELECT limit_Ax, limit_Ay, limit_Bx, limit_By FROM environ_interaction WHERE limit_flag='{t[1]}' AND entity_code='{t[0]}';", type='all')
            for temp2 in temp2all:
                interas.append(f"\n<:exclamation_cyan:626639669836382218> NPC `{temp[0]}`|**{temp[1]}** at ||`{temp2[0]:.3f}:{temp2[1]:.3f}` ~ `{temp2[2]:.3f}:{temp2[3]:.3f}`||")

        # HUNT
        try:
            end_point = await self.client.quefe(f"SELECT end_point FROM pi_hunt WHERE user_id='{ctx.author.id}' AND stats='ONGOING';")
            delta = relativedelta(end_point[0], datetime.now())
            # Still in progress
            if datetime.now() < end_point[0]: on_cd.append(f"\n:stopwatch: Command **`hunt`**: `{delta.hours:02d}:{delta.minutes:02d}:{delta.seconds:02d}`")
            # Done, but not collected
            else: off_cd.append(f"<:exclamation_yellow:626639669995503616> Command **`hunt`**: Fisnished")
        except TypeError:
            off_cd.append(f"<:exclamation_yellow:626639669995503616> Command **`hunt`**: Ready to go")

        await ctx.send(f""">>> {chr(10).join(off_cd)} {' '.join(on_cd)} {' '.join(interas)}""")








# ================== REAL MISC ==================
    @commands.command()
    async def swear(self, ctx, *args):
        args = list(args)
        resp = ''; resp2 = ''
        swears = {'vn': ['địt', 'đĩ', 'đụ', 'cặc', 'cằc', 'đéo', 'cứt', 'lồn', 'nứng', 'vãi', 'lồn má', 'đĩ lồn', 'tét lồn', 'dí lồn', 'địt mẹ', 'lồn trâu', 'lồn voi', 'lồn ngựa', 'con mẹ', 'bú', 'mút cặc'],
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

        args = ' '.join(args).lower().split(' ')

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




def setup(client):
    client.add_cog(avaTrivia(client))
