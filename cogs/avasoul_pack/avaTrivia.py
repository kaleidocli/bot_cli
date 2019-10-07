import asyncio
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

    @commands.command(aliases=['map'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def regions(self, ctx, *args):
        cur_PLACE = await self.client.quefe(f"SELECT cur_PLACE FROM personal_info WHERE id='{ctx.author.id}';")
        regions = await self.client.quefe(f"SELECT environ_code, name, description, illulink, border_X, border_Y, biome, land_slot, cuisine, goods FROM environ ORDER BY ord ASC;", type='all')

        async def makeembed(curp, pages, currentpage):
            region = regions[curp]; line = ''; swi = 0
            players = await self.client._cursor.execute(f"SELECT * FROM personal_info WHERE cur_PLACE='{region[0]}';")
            mobs = await self.client._cursor.execute(f"SELECT * FROM environ_mob WHERE region='{region[0]}';")
            mob_types = await self.client.quefe(f"SELECT mob_code, quantity FROM environ_diversity WHERE environ_code='{region[0]}';", type='all')

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

    @commands.command()
    @commands.cooldown(1, 2, type=BucketType.user)
    async def pralaeyr(self, ctx):
        await ctx.send("https://media.discordapp.net/attachments/381963689470984203/546796245994307595/map_description.png")

    @commands.command()
    @commands.cooldown(1, 2, type=BucketType.user)
    async def mobs(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        mobs = await self.client.quefe(f"SELECT mob_code, name, description, branch, evo, lp, str, chain, speed, au_FLAME, au_ICE, au_HOLY, au_DARK, illulink, effect FROM model_mob WHERE mob_code IN (SELECT mob_code FROM environ_diversity WHERE environ_code=(SELECT cur_PLACE FROM personal_info WHERE id='{ctx.author.id}'));", type='all')
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
            box.add_field(name=f'>>> **`LP`** · {mob[5]}\n**`STR`** · {mob[6]}\n**`CHAIN`** · {mob[7]}\n**`SPEED`** · {mob[8]}', value=effect)
            box.add_field(name=f'>>> **`FLAME`** · {mob[9]}\n**`ICE`** · {mob[10]}\n**`HOLY`** · {mob[11]}\n**`DARK`** · {mob[12]}', value=f"> `EVO.{mob[4]}`")

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

    @commands.command(aliases=['richest'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def toprich(self, ctx):
        ret = await self.client.quefe(f"SELECT name, age, money FROM personal_info ORDER BY money DESC LIMIT 10", type='all')

        line = ''; count = 0
        for u in ret:
            count += 1
            line = line + f"{count} | **{u[0]}** ({u[1]}) with <:36pxGold:548661444133126185> **{u[2]}**\n"

        await ctx.send(embed=discord.Embed(description=line, colour=0xFFC26F))

    @commands.command(aliases=['topmerit', 'honorest'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def tophonor(self, ctx):
        ret = await self.client.quefe(f"SELECT name, age, merit FROM personal_info ORDER BY merit DESC LIMIT 10", type='all')

        line = ''; count = 0
        for u in ret:
            count += 1
            line = line + f"{count} | **{u[0]}** ({u[1]}) with a merit **{u[2]}**\n"

        await ctx.send(embed=discord.Embed(description=line, colour=0xFFC26F))

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def topkill(self, ctx):
        ret = await self.client.quefe(f"SELECT name, EVO, kills FROM personal_info ORDER BY kills DESC LIMIT 10", type='all')

        line = ''; count = 0
        for u in ret:
            count += 1
            line = line + f"{count} | **{u[0]}** (`EVO-{u[1]}`) with **{u[2]}** kills\n"

        await ctx.send(embed=discord.Embed(description=line, colour=0xFFC26F))

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def topdeath(self, ctx):
        ret = await self.client.quefe(f"SELECT name, EVO, deaths FROM personal_info ORDER BY deaths DESC LIMIT 10", type='all')

        line = ''; count = 0
        for u in ret:
            count += 1
            line = line + f"{count} | **{u[0]}** (`EVO-{u[1]}`) with **{u[2]}** deaths\n"

        await ctx.send(embed=discord.Embed(description=line, colour=0xFFC26F))

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def topwin(self, ctx):
        ret = await self.client.quefe(f"SELECT (SELECT name FROM personal_info WHERE id=user_id), duel_win, duel_lost FROM misc_status ORDER BY duel_win DESC LIMIT 10", type='all')

        line = ''; count = 0
        for u in ret:
            count += 1
            line = line + f"{count} | **{u[0]}** have won **{u[1]}** duels and lost **{u[2]}** duels\n"

        await ctx.send(embed=discord.Embed(description=line, colour=0xFFC26F))



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





def setup(client):
    client.add_cog(avaTrivia(client))
