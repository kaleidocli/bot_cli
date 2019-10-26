import random
import asyncio
import concurrent

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors
from tabulate import tabulate

from .avaTools import avaTools
from .avaUtils import avaUtils
from .npcTriggers import npcTrigger



class avaNPC(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.npcTrigger = npcTrigger(self.client)
        self.trigg = {'p0c0i0training': self.npcTrigger.p0c0i0training,
                    'GE_trader': self.npcTrigger.GE_trader,
                    'GE_inspect': self.npcTrigger.GE_inspect}

        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)

        print("|| NPC ---- READY!")



# ================== EVENTS ==================

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     print("|| NPC ---- READY!")



# ================== NPC ==================

    @commands.command()
    @commands.cooldown(1, 13, type=BucketType.user)
    async def npc(self, ctx, *args):
        #if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        if not args:
            npcs = await self.client.quefe(f"SELECT name, description, branch, EVO, illulink, npc_code FROM model_npc WHERE npc_code IN (SELECT DISTINCT entity_code FROM environ_interaction WHERE region=(SELECT cur_PLACE FROM personal_info WHERE id='{ctx.author.id}'));", type='all')

            def makeembed(curp, pages, currentpage):
                npc = npcs[curp]

                temb = discord.Embed(title = f"`{npc[5]}` | **{npc[0].upper()}** {self.utils.smalltext(f'{npc[2].capitalize()} NPC')}", description = f"""```dsconfig
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


        # User's info
        cur_PLACE, cur_X, cur_Y = await self.client.quefe(f"SELECT cur_PLACE, cur_X, cur_Y FROM personal_info WHERE id='{ctx.author.id}';")

        try: npc = await self.client.quefe(f"SELECT name, description, branch, EVO, illulink, npc_code FROM model_npc WHERE npc_code='{args[0]}' OR name LIKE '%{args[0]}%';")
        except IndexError: await ctx.send(f"<:osit:544356212846886924> Missing npc's code"); return

        if not npc: await ctx.send("<:osit:544356212846886924> NPC not found!"); return

        # Relationship's info
        try: value_chem, value_impression, flag = await self.client.quefe(f"SELECT value_chem, value_impression, flag FROM pi_relationship WHERE user_id='{ctx.author.id}' AND target_code='{args[0]}';")
        # E: Relationship not initiated. Init one.
        except TypeError:
            value_chem = 0; value_impression = 0; flag = 'n/a'
            await self.client._cursor.execute(f"INSERT INTO pi_relationship VALUES (0, '{ctx.author.id}', '{args[0]}', {value_chem}, {value_impression}, '{flag}');")

        packs = await self.client.quefe(f"SELECT limit_Ax, limit_Ay, limit_Bx, limit_By FROM environ_interaction WHERE entity_code='{args[0]}' AND limit_flag='{flag}' AND (({value_chem}>=limit_chem AND chem_compasign='>=') OR ({value_chem}<limit_chem AND chem_compasign='<')) AND (({value_impression}>=limit_impression AND imp_compasign='>=') OR ({value_impression}<limit_impression AND imp_compasign='<')) AND region='{cur_PLACE}' AND limit_Ax<={cur_X} AND {cur_X}<limit_Bx AND limit_Ay<={cur_Y} AND {cur_Y}<limit_By ORDER BY limit_Ax DESC, limit_Bx ASC, limit_Ay DESC, limit_By ASC;", type='all')
        # Remove duplicate (?)
        packs = list(set(packs))

        def makeembed_two(items, top, least, pages, currentpage):
            packs, npc = items
            packs = packs[top:least]

            temb = discord.Embed(title = f"`{npc[5]}` | **{npc[0].upper()}** {self.utils.smalltext(f'{npc[2].capitalize()} NPC')}", description = f"""```dsconfig
    {npc[1]}```""", colour = discord.Colour(0x011C3A))
            temb.set_thumbnail(url=random.choice(npc[4].split(' <> ')))

            tinue = True
            while tinue:
                temp = []
                line = ''
                try:
                    for _ in range(4):
                        temp.append(packs.pop(0))
                except IndexError: tinue = False

                for p in temp:
                    line += f"> ||`{p[0]}:{p[1]}`~`{p[2]}:{p[3]}`|| \n"

                try: temb.add_field(name='═══════<:bubble_dot:544354428338044929>═══════', value=line)
                except discordErrors.HTTPException: break

            return temb
            

        await self.tools.pagiMain(ctx, (packs, npc), makeembed_two, item_per_page=8, timeout=60, delete_on_exit=False, pair=True)


    async def interact_engine(self, ctx, pack, intera_kw='talk', args=()):
        cur_PLACE, cur_X, cur_Y, charm, value_chem, value_impression, flag, entity_code, entity_name, illulink = pack

        # if intera_kw == 'inspect': await self.trigg['GE_inspect']([ctx, value_chem, value_impression, flag, entity_code, entity_name, cur_PLACE, cur_X, cur_Y]); return

        # Interaction's info
        #print(f"SELECT entity_code, trigg, data_goods, effect_query, line, limit_chem, fail_line, reward_chem, reward_impression FROM environ_interaction WHERE entity_code='{entity_code}' AND intera_kw='{intera_kw}' AND limit_flag='{flag}' AND (({value_chem}>=limit_chem AND chem_compasign='>=') OR ({value_chem}<limit_chem AND chem_compasign='<')) AND (({value_impression}>=limit_impression AND imp_compasign='>=') OR ({value_impression}<limit_impression AND imp_compasign='<')) AND region='{cur_PLACE}' AND limit_Ax<={cur_X} AND {cur_X}<limit_Bx AND limit_Ay<={cur_Y} AND {cur_Y}<limit_By ORDER BY limit_Ax DESC, limit_Bx ASC, limit_Ay DESC, limit_By ASC, limit_chem DESC, limit_impression DESC LIMIT 1;")
        try: entity_code, trigg, data_goods, effect_query, lines, limit_chem, fail_line, r_chem, r_imp = await self.client.quefe(f"SELECT entity_code, trigg, data_goods, effect_query, line, limit_chem, fail_line, reward_chem, reward_impression FROM environ_interaction WHERE entity_code='{entity_code}' AND intera_kw='{intera_kw}' AND limit_flag='{flag}' AND (({value_chem}>=limit_chem AND chem_compasign='>=') OR ({value_chem}<limit_chem AND chem_compasign='<')) AND (({value_impression}>=limit_impression AND imp_compasign='>=') OR ({value_impression}<limit_impression AND imp_compasign='<')) AND region='{cur_PLACE}' AND limit_Ax<={cur_X} AND {cur_X}<limit_Bx AND limit_Ay<={cur_Y} AND {cur_Y}<limit_By ORDER BY limit_Ax DESC, limit_Bx ASC, limit_Ay DESC, limit_By ASC, limit_chem DESC, limit_impression DESC LIMIT 1;")
        except TypeError: await ctx.message.add_reaction('\U00002754'); return         # Silently ignore         #await ctx.send("<:osit:544356212846886924> Entity not found!"); return

        # Prep
        if not lines: lines = 'Ahem...'

        # TRIGGER !!!!!!!!!!!!!!!!!!!
        if trigg != 'n/a':
            try: illulink = random.choice(illulink.split(' <> '))
            except AttributeError: illulink = ''
            pack = [ctx, data_goods, entity_code, entity_name, illulink, random.choice(lines.split(' ||| '))]
            try: pack.append(args[2:])
            except IndexError: pass

            try: await self.trigg[trigg](pack)
            except KeyError: pass
            return

        async def line_gen(lines, illulink='', first_time=False):

            def embing(entity_code, entity_name, line, illulink, dura=5, left=False):
                # In case <LEFT>
                if left:
                    temb = discord.Embed(title=f"`{entity_code}` <:bubble_dot:544354428338044929> **{entity_name}**", description=f"""*{entity_name} has left*""", colour = 0x36393E)
                    temb.set_thumbnail(url=random.choice(illulink.split(' <> ')))
                    temb.set_footer(text='⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀')
                    return temb, dura, False

                temb = discord.Embed(title=f"`{entity_code}` <:bubble_dot:544354428338044929> **{entity_name}**", description=f"""```css
        {line}```""", colour = 0x36393E)

                temb.set_thumbnail(url=random.choice(illulink.split(' <> ')))
                temb.set_footer(text='⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀')
                if dura < 5: dura = 5

                return temb, dura, True

            # Splitting line
            linu = random.choice(lines.split(' ||| '))
            # Check if line is continous
            if ' >>> ' in linu:
                linu = linu.split(' >>> ')
                linus = []
                for line in linu:
                    dura = round(len(line)/7)
                    linus.append(embing(entity_code, entity_name, line, illulink, dura=dura))
                return linus, dura, True, True
            # Splitting urls with the sets
            line = linu.split(' <> ')
            dura = round(len(line[0])/7)
            # try: illulink = line[1]
            # except IndexError: illulink = ''

            # Carrying on conversation
            if await self.utils.percenter(value_chem - limit_chem, total=100) or first_time:
                linus, dura, checkk = embing(entity_code, entity_name, line[0], illulink, dura=dura)
                return linus, dura, checkk, False
            # Or not...
            else:
                linus, dura, checkk = embing(entity_code, entity_name, line[0], illulink, dura=dura, left=True)
                return linus, dura, checkk, False

        def RUM_check(reaction, user):
            return user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) == "<:bubble_dot:544354428338044929>"

        try: effect_query = effect_query.replace('user_id_here', f"{ctx.author.id}")
        # E: No effect_query
        except AttributeError: pass

        # Rewarding relationship
        r_chem = r_chem.split(' | ')
        rwc = random.choice(r_chem)
        if effect_query: await self.client._cursor.execute(f"UPDATE pi_relationship SET value_chem=value_chem+{int(rwc)}+{round(charm/50)}, value_impression=value_impression+{int(random.choice(r_imp.split(' | ')))} WHERE user_id='{ctx.author.id}' AND target_code='{entity_code}'; {effect_query}")
        else: await self.client._cursor.execute(f"UPDATE pi_relationship SET value_chem=value_chem+{int(rwc)}+{round(charm/50)}, value_impression=value_impression+{int(random.choice(r_imp.split(' | ')))} WHERE user_id='{ctx.author.id}' AND target_code='{entity_code}';")

        # In case pick the fail one
        if rwc == r_chem[0] and int(rwc) != 0:
            lines = fail_line

        temb, dura, checkk, continuous = await line_gen(lines, illulink, first_time=True)

        # CONTINUOUS line
        if continuous:
            emb, dura, checkk = temb.pop(0)
            msg = await ctx.send(embed=emb)
            await msg.add_reaction(':bubble_dot:544354428338044929')

            for peck in temb:
                try:
                    await self.client.wait_for('reaction_add', check=RUM_check, timeout=dura)
                    emb, dura, checkk = peck
                    await msg.edit(embed=emb, delete_after=30)

                except asyncio.TimeoutError:
                    await msg.delete(); return
            return

        msg = await ctx.send(embed=temb)
        await msg.add_reaction(':bubble_dot:544354428338044929')

        while True:
            try:
                await self.client.wait_for('reaction_add', check=RUM_check, timeout=dura)
                temb, dura, checkk, continuous = await line_gen(lines)
                # CONTINUOUS line
                if continuous:
                    emb, dura, checkk = temb.pop(0)
                    msg = await ctx.send(embed=emb)
                    await msg.add_reaction(':bubble_dot:544354428338044929')

                    for peck in temb:
                        try:
                            await self.client.wait_for('reaction_add', check=RUM_check, timeout=dura)
                            emb, dura, checkk = peck
                            await msg.edit(embed=emb, delete_after=30)

                        except asyncio.TimeoutError:
                            await msg.delete(); return
                    return
                # NON-CONTINUOUS
                else:
                    if checkk: await msg.edit(embed=temb)
                    else: await msg.edit(embed=temb, delete_after=5); return

            except asyncio.TimeoutError:
                await msg.delete(); return

    @commands.command(aliases=['in'])
    @commands.cooldown(1, 25, type=BucketType.user)
    async def interact(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        try:
            intera_kw = args[1]
        except IndexError: intera_kw = None

        # User's info
        cur_PLACE, cur_X, cur_Y, charm = await self.client.quefe(f"SELECT cur_PLACE, cur_X, cur_Y, charm FROM personal_info WHERE id='{ctx.author.id}';")

        # NPC / Item
        try:
            int(args[0])
            try: entity_code, entity_name, illulink = await self.client.quefe(f"SELECT item_id, name, illulink FROM pi_inventory WHERE item_id='{args[0]}' AND user_id='n/a' AND existence='GOOD';")
            # E: Item not found --> Silently ignore
            except TypeError: await ctx.message.add_reaction('\U00002754'); return
        except ValueError:
            try:
                entity_code, entity_name, illulink = await self.client.quefe(f"""SELECT npc_code, name, illulink FROM model_npc WHERE npc_code="{args[0]}" OR name LIKE "%{args[0]}%";""")
            # E: NPC not found --> Silently ignore
            except TypeError: await ctx.message.add_reaction('\U00002754'); return
        except IndexError: await ctx.send("<:osit:544356212846886924> Missing NPC's code"); return

        # Relationship's info
        try: value_chem, value_impression, flag = await self.client.quefe(f"SELECT value_chem, value_impression, flag FROM pi_relationship WHERE user_id='{ctx.author.id}' AND target_code='{entity_code}';")
        # E: Relationship not initiated. Init one.
        except TypeError:
            value_chem = 0; value_impression = 0; flag = 'n/a'
            await self.client._cursor.execute(f"INSERT INTO pi_relationship VALUES (0, '{ctx.author.id}', '{entity_code}', {value_chem}, {value_impression}, '{flag}');")


        # BEFORE THE RIDE
        if intera_kw:
            await self.interact_engine(ctx, (cur_PLACE, cur_X, cur_Y, charm, value_chem, value_impression, flag, entity_code, entity_name, illulink), intera_kw=intera_kw, args=args)
            return


        # Interaction's info        (limit_flag is a dummy)
        try: pecks = await self.client.quefe(f"SELECT intera_kw, limit_flag FROM environ_interaction WHERE entity_code='{entity_code}' AND limit_flag='{flag}' AND (({value_chem}>=limit_chem AND chem_compasign='>=') OR ({value_chem}<limit_chem AND chem_compasign='<')) AND (({value_impression}>=limit_impression AND imp_compasign='>=') OR ({value_impression}<limit_impression AND imp_compasign='<')) AND region='{cur_PLACE}' AND limit_Ax<={cur_X} AND {cur_X}<limit_Bx AND limit_Ay<={cur_Y} AND {cur_Y}<limit_By ORDER BY intera_kw ASC;", type='all')
        except TypeError: await ctx.message.add_reaction('\U00002754'); return         # Silently ignore
        packs = list(pecks)

        # INIT ======================
        currentpage = 1
        item_per_page = 8
        pages = int(len(packs)/item_per_page)
        if len(packs)%item_per_page != 0: pages += 1

        # Creating strings ============
        emli = []
        for _ in range(pages):
            stringembed = self.stringembed_intera((packs, [entity_code, entity_name, illulink]), currentpage*item_per_page-item_per_page, currentpage*item_per_page, pages, currentpage)
            emli.append(stringembed)
            currentpage += 1
        print(pages, emli)

        # [ [[em, kw], [em, kw]], [] ]

        # START =======================
        cursor_string = 0
        cursor_micro = 0
        msg = await ctx.send(embed=emli[cursor_string][cursor_micro][0])
        await self.tools.pageButtonAdd(msg, extra=["\U00002b05", "\U000025c0", "\U0001f44b", "\U000025b6", "\U000027a1"], extra_replace=True)

        while True:
            try:
                reaction, _ = await self.tools.pagiButton(check=lambda r, u: r.message.id == msg.id and u.id == ctx.author.id, timeout=60)
                if reaction.emoji == "\U000027a1":
                    if cursor_string < pages - 1: cursor_string += 1
                    else: cursor_string = 0
                    await msg.edit(embed=emli[cursor_string][cursor_micro][0])
                elif reaction.emoji == "\U00002b05":
                    if cursor_string > 0: cursor_string -= 1
                    else: cursor_string = pages - 1
                    await msg.edit(embed=emli[cursor_string][cursor_micro][0])
                elif reaction.emoji == "\U000025b6":
                    if cursor_micro < len(emli[cursor_string]) - 1: cursor_micro += 1
                    else: cursor_micro = 0
                    await msg.edit(embed=emli[cursor_string][cursor_micro][0])
                elif reaction.emoji == "\U000025c0":
                    if cursor_micro > 0: cursor_micro -= 1
                    else: cursor_micro = len(emli[cursor_string]) - 1
                    await msg.edit(embed=emli[cursor_string][cursor_micro][0])
                elif reaction.emoji == "\U0001f44b":
                    await msg.delete()
                    await self.interact_engine(ctx, (cur_PLACE, cur_X, cur_Y, charm, value_chem, value_impression, flag, entity_code, entity_name, illulink), intera_kw=emli[cursor_string][cursor_micro][1], args=args)
                    msg = await ctx.send(embed=emli[cursor_string][cursor_micro][0])
                    await self.tools.pageButtonAdd(msg, extra=["\U00002b05", "\U000025c0", "\U0001f44b", "\U000025b6", "\U000027a1"], extra_replace=True)

            except concurrent.futures.TimeoutError:
                return






    def stringembed_intera(self, items, top, least, pages, currentpage):
        temp = []

        for item in items[0][top:least]:
            temp.append(self.microembed_intera(items, top, least, pages, currentpage, ikw=item[0]))

        return temp

    def microembed_intera(self, items, top, least, pages, currentpage, ikw=''):
        row_len = 4
        packs, npc = items
        packs = packs[top:least]

        temp2 = []
        tinue = True
        while tinue:
            temp = []
            try:
                for _ in range(row_len):
                    kw = packs.pop(0)[0]
                    if kw == ikw: kw = f"[{kw}]"
                    temp.append(kw)
                if temp: temp2.append(temp)
            except IndexError:
                if temp: temp2.append(temp)
                tinue = False

        temb = discord.Embed(title = f"`{npc[0]}` | **{npc[1].upper()}**", description = f"""```ini
{tabulate(temp2, tablefmt='plain')}```""", colour = discord.Colour(0x011C3A))
        temb.set_thumbnail(url=random.choice(npc[2].split(' <> ')))

        return [temb, ikw]




def setup(client):
    client.add_cog(avaNPC(client))
