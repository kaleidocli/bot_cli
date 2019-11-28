import random
import asyncio
import concurrent

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors
from tabulate import tabulate



class avaNPC(commands.Cog):

    def __init__(self, client):
        from .avaTools import avaTools
        from .avaUtils import avaUtils
        from .npcTriggers import npcTrigger

        self.client = client
        self.npcTrigger = npcTrigger(self.client)
        self.trigg = {'p0c0i0training': self.npcTrigger.p0c0i0training,
                    'GE_trader': self.npcTrigger.GE_trader,
                    'GE_inspect': self.npcTrigger.GE_inspect}

        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)

        self.client.DBC['model_NPC'] = {}
        self.client.DBC['model_conversation'] = {}
        self.cacheMethod = {
            'model_NPC': self.cacheNPC,
            'model_conversation': self.cacheConversation
        }

        print("|| NPC ---- READY!")



# ================== EVENTS ==================

    @commands.Cog.listener()
    async def on_ready(self):
        await self.reloadSetup()

    async def reloadSetup(self):
        await self.cacheAll()



# ================== NPC ==================

    @commands.command()
    @commands.cooldown(1, 13, type=BucketType.user)
    async def npc(self, ctx, *args):
        #if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        # LIST ==========================================
        if not args:
            npcs = await self.client.quefe(f"SELECT name, description, branch, EVO, illulink, npc_code FROM model_npc WHERE npc_code IN (SELECT DISTINCT entity_code FROM environ_interaction WHERE region=(SELECT cur_PLACE FROM personal_info WHERE id='{ctx.author.id}'));", type='all')

            def makeembed(curp, pages, currentpage):
                npc = npcs[curp]

                temb = discord.Embed(title = f"`{npc[5]}`| **{npc[0].upper()}** {self.utils.smalltext(f'{npc[2].capitalize()} NPC')}", description = f"""```dsconfig
        {npc[1]}```""", colour = discord.Colour(0x011C3A))
                temb.set_image(url=random.choice(npc[4].split(' <> ')))

                return temb, npc[5]

            pages = len(npcs)
            currentpage = 1
            cursor = 0

            emli = []
            for curp in range(pages):
                micro_embed = makeembed(curp, pages, currentpage)
                emli.append(micro_embed)
                currentpage += 1

            if pages > 1:
                msg = await ctx.send(embed=emli[cursor][0])
                #Top-left   #Left   #Pick   #Right   #Top-right
                await self.tools.pageButtonAdd(msg, reaction=["\U000023ee", "\U00002b05", "\U0001f44b", "\U000027a1", "\U000023ed"])
            elif not pages:
                await ctx.send("<:osit:544356212846886924> No NPC found in this region."); return
            else:
                msg = await ctx.send(embed=emli[cursor][0], delete_after=25); return

            while True:
                try:
                    reaction, _ = await self.tools.pagiButton(timeout=20, check=lambda r, u: u == ctx.author)
                    if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                        cursor += 1
                        await msg.edit(embed=emli[cursor][0])
                    elif reaction.emoji == "\U00002b05" and cursor > 0:
                        cursor -= 1
                        await msg.edit(embed=emli[cursor][0])
                    elif reaction.emoji == '\U0001f44b':
                        await ctx.invoke(self.interact, emli[cursor][1])
                        return
                    elif reaction.emoji == "\U000023ee" and cursor != 0:
                        cursor = 0
                        await msg.edit(embed=emli[cursor][0])
                    elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                        cursor = pages - 1
                        await msg.edit(embed=emli[cursor][0])
                except asyncio.TimeoutError:
                    await msg.delete(); return


        # SPECIFIC ========================================
        # User's info
        # cur_PLACE, cur_X, cur_Y = await self.client.quefe(f"SELECT cur_PLACE, cur_X, cur_Y FROM personal_info WHERE id='{ctx.author.id}';")

        try:
            npc = await self.dbcGetNPC(args[0])
            if not npc:
                for n in self.client.DBC['model_NPC'].values():
                    if n.check(name=args[0]):
                        npc = n
                        break
            if not npc: await ctx.send("<:osit:544356212846886924> NPC not found!"); return
            # npc = await self.client.quefe(f"SELECT name, description, branch, EVO, illulink, npc_code FROM model_npc WHERE npc_code='{args[0]}' OR name LIKE '%{args[0]}%';")
        except IndexError:
            await ctx.send(f"<:osit:544356212846886924> Missing NPC's code"); return

        # Relationship's info
        try:
            value_1, value_2, value_3 = await self.client.quefe(f"SELECT value_1, value_2, value_3 FROM pi_flag WHERE user_id='{ctx.author.id}' AND flag_code='intera.{npc.npc_code}';")
        # E: Relationship not initiated. Init one.
        except TypeError:
            value_1 = 0; value_2 = 0; value_3 = ''
            # await self.client._cursor.execute(f"INSERT INTO pi_relationship VALUES (0, '{ctx.author.id}', '{args[0]}', {limit_chem}, {limit_impression}, '{flag}');")
            await self.client._cursor.execute(f"SELECT func_flag_reward('{ctx.author.id}', 'intera.{npc.npc_code}', {value_1}, {value_2}, '{value_3}');")

        # packs = await self.client.quefe(f"SELECT limit_Ax, limit_Ay, limit_Bx, limit_By FROM environ_interaction WHERE entity_code='{args[0]}' AND limit_flag='{flag}' AND (({limit_chem}>=limit_chem AND chem_compasign='>=') OR ({limit_chem}<limit_chem AND chem_compasign='<')) AND (({limit_impression}>=limit_impression AND imp_compasign='>=') OR ({limit_impression}<limit_impression AND imp_compasign='<')) AND region='{cur_PLACE}' AND limit_Ax<={cur_X} AND {cur_X}<limit_Bx AND limit_Ay<={cur_Y} AND {cur_Y}<limit_By ORDER BY limit_Ax DESC, limit_Bx ASC, limit_Ay DESC, limit_By ASC;", type='all')
        packs = await self.client.quefe(f"""
            SELECT e.limit_Ax, e.limit_Ay, e.limit_Bx, e.limit_By FROM environ_interaction e, pi_flag f, personal_info pf
            WHERE
            (
                e.entity_code="{npc.npc_code}"
                AND e.region=pf.cur_PLACE
                AND pf.id="{ctx.author.id}"
            )
            AND
            (
                (
                    e.limit_flag='n/a'
                    OR
                    (
                        f.user_id="{ctx.author.id}"
                        AND e.limit_flag=f.flag_code
                    )
                )
                OR
                (
                    ((e.limit_chem=">=" AND f.value_1>=e.limit_chem) OR (e.limit_chem="<" AND f.value_1<e.limit_chem)) 
                    AND ((e.limit_impression=">=" AND f.value_2>=e.limit_impression) OR (e.limit_impression="<" AND f.value_2<e.limit_impression))
                )
            )
            ORDER BY e.limit_Ax ASC, e.limit_Ay ASC;
        """, type='all')
        # Remove duplicate (?)
        packs = list(set(packs))

        def makeembed_two(items, top, least, pages, currentpage):
            packs, npc = items
            packs = packs[top:least]

            temb = discord.Embed(title = f"`{npc.npc_code}`| **{npc.name.upper()}** {self.utils.smalltext(f'{npc.branch.capitalize()} NPC')}", description = f"""```dsconfig
    {npc.description}```""", colour = discord.Colour(0x011C3A))
            temb.set_thumbnail(url=random.choice(npc.illulink))

            tinue = True
            while tinue:
                temp = []
                line = ''
                try:
                    for _ in range(4):
                        temp.append(packs.pop(0))
                    if not packs: tinue = False
                except IndexError: tinue = False

                for p in temp:
                    line += f"> ||`{p[0]}:{p[1]}`~`{p[2]}:{p[3]}`|| \n"

                try: temb.add_field(name='═══════<:bubble_dot:544354428338044929>═══════', value=line)
                except discordErrors.HTTPException: break

            return temb
            

        await self.tools.pagiMain(ctx, (packs, npc), makeembed_two, item_per_page=8, timeout=60, delete_on_exit=False, pair=True)

    @commands.command(aliases=['meet'])
    @commands.cooldown(1, 25, type=BucketType.user)
    async def interact(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        try:
            intera_kw = args[1]
        except IndexError: intera_kw = None

        # NPC / Item
        try:
            int(args[0])        # Please don't, don't don't remove this
            try: entity_code, entity_name, illulink = await self.client.quefe(f"SELECT item_id, name, illulink FROM pi_inventory WHERE item_id='{args[0]}' AND user_id='n/a' AND existence='GOOD';")
            # E: Item not found --> Silently ignore
            except TypeError: await ctx.message.add_reaction('\U00002754'); return
        except ValueError:
            npc = await self.dbcGetNPC(args[0])
            if not npc:
                for n in self.client.DBC['model_NPC'].values():
                    if n.check(name=args[0]):
                        npc = n
                        break
            if not npc: await ctx.message.add_reaction('\U00002754'); return
            entity_code = npc.npc_code          # entity_code is for interact_engine.   (and trigg also)
            entity_name = npc.name              # entity_name and illulink is for trigg
            illulink = random.choice(npc.illulink)
            # try:
            #     entity_code, entity_name, illulink = await self.client.quefe(f"""SELECT npc_code, name, illulink FROM model_npc WHERE npc_code="{args[0]}" OR name LIKE "%{args[0]}%";""")
            # # E: NPC not found --> Silently ignore
            # except TypeError: await ctx.message.add_reaction('\U00002754'); return
        except IndexError: await ctx.send("<:osit:544356212846886924> Entity not found!"); return

        # # Relationship's info
        # try:
        #     limit_chem, limit_impression, flag = await self.client.quefe(f"SELECT limit_chem, limit_impression, flag FROM pi_relationship WHERE user_id='{ctx.author.id}' AND target_code='{entity_code}';")
        # # E: Relationship not initiated. Init one.
        # except TypeError:
        #     limit_chem = 0; limit_impression = 0; flag = 'n/a'
        #     await self.client._cursor.execute(f"INSERT INTO pi_relationship VALUES (0, '{ctx.author.id}', '{entity_code}', {limit_chem}, {limit_impression}, '{flag}');")


        # BEFORE THE RIDE
        if intera_kw:
            await self.interact_engine(ctx, (entity_code, entity_name, illulink), intera_kw=intera_kw, args=args)
            return


        # Interaction's info        (limit_flag is a dummy)
        try:
            # pecks = await self.client.quefe(f"SELECT intera_kw, limit_flag FROM environ_interaction WHERE entity_code='{entity_code}' AND limit_flag='{flag}' AND (({limit_chem}>=limit_chem AND chem_compasign='>=') OR ({limit_chem}<limit_chem AND chem_compasign='<')) AND (({limit_impression}>=limit_impression AND imp_compasign='>=') OR ({limit_impression}<limit_impression AND imp_compasign='<')) AND region='{cur_PLACE}' AND limit_Ax<={cur_X} AND {cur_X}<limit_Bx AND limit_Ay<={cur_Y} AND {cur_Y}<limit_By ORDER BY intera_kw ASC;", type='all')
            pecks = await self.client.quefe(f"""
                SELECT e.trigg, e.data_goods, e.effect_query, e.line, e.reward_chem, e.reward_impression, pf.charm, e.intera_kw FROM environ_interaction e, pi_flag f, personal_info pf
                WHERE
                (
                    e.entity_code="{entity_code}"
                    AND pf.id="{ctx.author.id}"
                    AND e.region=pf.cur_PLACE AND e.limit_Ax<=pf.cur_X AND pf.cur_X<e.limit_Bx AND e.limit_Ay<=pf.cur_Y AND pf.cur_Y<e.limit_By
                )
                AND
                (
                    (
                        e.limit_flag='n/a'
                        OR 
                        (
                            e.limit_flag=f.flag_code
                            AND f.user_id="{ctx.author.id}"
                        )
                    )
                    AND
                    (
                        ((e.limit_chem=">=" AND f.value_1>=e.limit_chem) OR (e.limit_chem="<" AND f.value_1<e.limit_chem)) 
                        AND ((e.limit_impression=">=" AND f.value_2>=e.limit_impression) OR (e.limit_impression="<" AND f.value_2<e.limit_impression))
                    )
                )
                ORDER BY e.intera_kw ASC;
            """, type='all')

            if not pecks: await ctx.message.add_reaction('\U00002754'); return

            pecks = list(set(pecks))
            packs = []
            pack_dict = {}

            for p in pecks:
                packs.append((p[7], ''))
                pack_dict[p[7]] = p
        except TypeError:
            await ctx.message.add_reaction('\U00002754'); return         # Silently ignore

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
                    await self.interact_engine(ctx, (entity_code, entity_name, illulink), intera_kw=emli[cursor_string][cursor_micro][1], args=args, intera_pack=pack_dict[emli[cursor_string][cursor_micro][1]])
                    msg = await ctx.send(embed=emli[cursor_string][cursor_micro][0])
                    await self.tools.pageButtonAdd(msg, extra=["\U00002b05", "\U000025c0", "\U0001f44b", "\U000025b6", "\U000027a1"], extra_replace=True)

            except concurrent.futures.TimeoutError:
                return





# ================== ADMIN ==================








# ================== TOOLS ==================


    async def turn_embing(self, pack, asker):
        """
            pack:   (author, (line1, line2,), illulink)

            Return embs ((emb, dura), (emb, dura),..)    
        """
        author_code, lines, illulink = pack
        embs = []

        # ASKER
        if author_code == 'self':
            for line in lines:
                # Prep
                line = line.replace('user_name_here', asker.name)

                # Embing
                temb = discord.Embed(description=f"""```css
    {line}```""", colour = 0x36393E)
                temb.set_thumbnail(url=asker.avatar_url)
                if illulink: temb.set_image(url=illulink)
                temb.set_footer(text=f"{asker.name}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", icon_url='https://imgur.com/VmpsPi6.png')
                # temb.set_footer(text='⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀')

                # Dura
                dura = len(line)//7
                if dura < 7: dura = 7

                embs.append((temb, dura))

        # NPC / NARRATOR
        else:
            author = await self.dbcGetNPC(author_code)
            if not author:
                await self.client.owner.send(f"<!> Corrupted conv_code `{author_code}`")
                return
        
            for line in lines:
                # Prep
                line = line.replace('user_name_here', asker.name)

                # Embing
                if not author.narrator:
                    temb = discord.Embed(description=f"""```css
    {line}```""", colour = 0x36393E)
                else:
                    temb = discord.Embed(description=line, colour = 0x36393E)
                if author.illulink: temb.set_thumbnail(url=random.choice(author.illulink))
                if illulink: temb.set_image(url=illulink)
                temb.set_footer(text=f"{author.npc_code} | {author.name}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", icon_url='https://imgur.com/VmpsPi6.png')
                # temb.set_footer(text='⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀')

                # Dura
                dura = len(line)//7
                if dura < 5: dura = 5

                embs.append((temb, dura))

        return embs

    async def interact_engine(self, ctx, pack, intera_kw='talk', args=(), intera_pack=(), conv_code_in=''):
        # cur_PLACE, cur_X, cur_Y, charm, limit_chem, limit_impression, flag, entity_code, entity_name, illulink = pack
        entity_code, entity_name, illulink = pack

        # INFO Interaction ===============================
        try:
            if intera_pack:
                trigg, data_goods, effect_query, lines, r_chem, r_imp, charm, _ = intera_pack
            else:
                trigg, data_goods, effect_query, lines, r_chem, r_imp, charm = await self.client.quefe(f"""
                    SELECT e.trigg, e.data_goods, e.effect_query, e.line, e.reward_chem, e.reward_impression, pf.charm FROM environ_interaction e, pi_flag f, personal_info pf
                    WHERE
                    (
                        e.entity_code="{entity_code}"
                        AND pf.id="{ctx.author.id}"
                        AND e.region=pf.cur_PLACE AND e.limit_Ax<=pf.cur_X AND pf.cur_X<e.limit_Bx AND e.limit_Ay<=pf.cur_Y AND pf.cur_Y<e.limit_By
                        AND e.intera_kw='{intera_kw}'
                    )
                    AND
                    (
                        (
                            e.limit_flag='n/a'
                            OR 
                            (
                                e.limit_flag=f.flag_code
                                AND f.user_id="{ctx.author.id}"
                            )
                        )
                        AND
                        (
                            ((e.limit_chem=">=" AND f.value_1>=e.limit_chem) OR (e.limit_chem="<" AND f.value_1<e.limit_chem)) 
                            AND ((e.limit_impression=">=" AND f.value_2>=e.limit_impression) OR (e.limit_impression="<" AND f.value_2<e.limit_impression))
                        )
                    )
                    ORDER BY e.limit_Ax DESC, e.limit_Ay DESC LIMIT 1;
                """)
            # entity_code, trigg, data_goods, effect_query, lines, r_chem, r_imp = await self.client.quefe(f"""
            # SELECT entity_code, trigg, data_goods, effect_query, line, reward_chem, reward_impression 
            # FROM environ_interaction 
            # WHERE 
            # entity_code='{entity_code}' AND intera_kw='{intera_kw}' AND limit_flag='{flag}' 
            # AND (({limit_chem}>=limit_chem AND chem_compasign='>=') OR ({limit_chem}<limit_chem AND chem_compasign='<')) 
            # AND (({limit_impression}>=limit_impression AND imp_compasign='>=') OR ({limit_impression}<limit_impression AND imp_compasign='<')) 
            # AND region='{cur_PLACE}' AND limit_Ax<={cur_X} AND {cur_X}<limit_Bx AND limit_Ay<={cur_Y} AND {cur_Y}<limit_By
            # ORDER BY limit_Ax DESC, limit_Bx ASC, limit_Ay DESC, limit_By ASC, limit_chem DESC, limit_impression DESC LIMIT 1;""")
        except TypeError:
            await ctx.message.add_reaction('\U00002754'); return         # Silently ignore         #await ctx.send("<:osit:544356212846886924> Entity not found!"); return

        # Prep
        if conv_code_in: conv_code = conv_code_in
        elif lines: conv_code = random.choice(lines.split(' - '))

        # TRIGGER ========================================
        if trigg != 'n/a':
            try: illulink = random.choice(illulink.split(' <> '))
            except AttributeError: illulink = ''
            pack = [ctx, data_goods, entity_code, entity_name, illulink, random.choice(lines.split(' ||| '))]
            try: pack.append(args[2:])
            except IndexError: pass

            try: await self.trigg[trigg](pack)
            except KeyError: pass
            return

        # TURN embing =====================================
        embs = []
        try:
            conv = await self.dbcGetConversation(conv_code)
            if not conv:
                await self.client.owner.send(f"<!> Corrupted conv_code `{conv_code}` in intera_kw `{intera_kw}` of NPC `{entity_code}`")
                return
            for l in conv.line:
                embs = embs + await self.turn_embing(l, ctx.author)
            if not embs: return
        except KeyError:
            await self.client.owner.send(f"<!> Corrupted conv_code `{conv_code}` in intera_kw `{intera_kw}` of NPC `{entity_code}`")
            return

        # START ===========================================
        count = 1
        msg = None
        switch = None
        for e in embs:
            if not msg:
                msg = await ctx.send(embed=e[0])
                await msg.add_reaction(':bubble_dot:544354428338044929')
            else:
                await msg.edit(embed=e[0])

            try:
                if conv.type == 'CHOICE' and count == len(embs):
                    await msg.add_reaction(':tick_yes:515012376962138112')
                    await msg.add_reaction(':tick_no:515012452635770882')                    

                    reaction, _ = await self.tools.pagiButton(check=lambda r, u: u == ctx.author and r.message.id == msg.id, timeout=e[1])
                    try:
                        if str(reaction.emoji) == ':tick_yes:515012376962138112':
                            switch = random.choice(conv.node_1)
                        else:
                            switch = random.choice(conv.node_2)
                    except IndexError: return
                else:
                    await self.tools.pagiButton(check=lambda r, u: u == ctx.author and r.message.id == msg.id, timeout=e[1])
            except concurrent.futures.TimeoutError:
                await msg.delete()
                return

            count += 1

        # EFFECT ========================================
        if not effect_query: effect_query = ''
        # Interaction
        try:
            effect_query = effect_query.replace('user_id_here', f"{ctx.author.id}")
        except AttributeError: pass
        # Conv
        try:
            effect_query += conv.effect_query
        except TypeError: pass

        # Rewarding relationship
        try:
            r_chem = r_chem.split(' | ')
            rwc = random.choice(r_chem)
        except AttributeError:
            rwc = 0
        if entity_code.startswith('p'):
            if effect_query:
                # await self.client._cursor.execute(f"UPDATE pi_relationship SET limit_chem=limit_chem+{int(rwc)}+{round(charm/50)}, limit_impression=limit_impression+{int(random.choice(r_imp.split(' | ')))} WHERE user_id='{ctx.author.id}' AND target_code='{entity_code}'; {effect_query}")
                await self.client._cursor.execute(f"SELECT func_flag_reward('{ctx.author.id}', 'intera.{entity_code}', {int(rwc)}+{round(charm/50)}, {int(random.choice(r_imp.split(' | ')))}, ''); {effect_query}")
            else:
                await self.client._cursor.execute(f"SELECT func_flag_reward('{ctx.author.id}', 'intera.{entity_code}', {int(rwc)}+{round(charm/50)}, {int(random.choice(r_imp.split(' | ')))}, '');")
        else:
            if effect_query: await self.client._cursor.execute(effect_query)

        # SWITCH to next CONV =========================
        if switch: await self.interact_engine(ctx, pack, intera_kw=intera_kw, args=args, intera_pack=intera_pack, conv_code_in=switch)



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

        temb = discord.Embed(title = f"`{npc[0]}`| **{npc[1].upper()}**", description = f"""```ini
{tabulate(temp2, tablefmt='plain')}```""", colour = discord.Colour(0x011C3A))
        temb.set_thumbnail(url=random.choice(npc[2].split(' <> ')))

        return [temb, ikw]


    async def cacheAll(self):
        for v in self.cacheMethod.values():
            await v()

    async def cacheNPC(self):
        self.client.DBC['model_NPC'] = await self.cacheNPC_tool()
        self.client.DBC['model_NPC']['narrator'] = c_NPC(None, narrator=True)

    async def cacheConversation(self):
        self.client.DBC['model_conversation'] = await self.cacheConversation_tool()

    async def cacheNPC_tool(self):
        temp = {}

        res = await self.client.quefe("SELECT npc_code, name, description, branch, evo, lp, str, chain, speed, au_FLAME, au_ICE, au_HOLY, au_DARK, rewards, illulink FROM model_NPC;", type='all')
        for r in res:
            await asyncio.sleep(0)
            temp[r[0]] = c_NPC(r)

        return temp

    async def cacheConversation_tool(self):
        temp = {}

        res = await self.client.quefe("SELECT ordera, conv_code, type, line, node_1, node_2, effect_query FROM model_converstation;", type='all')
        for r in res:
            await asyncio.sleep(0)
            temp[r[1]] = c_Conversation(r)

        return temp

    async def dbcGetConversation(self, conv_code):
        try:
            return self.client.DBC['model_conversation'][conv_code]
        except KeyError:
            res = await self.client.quefe(f"SELECT ordera, conv_code, type, line, node_1, node_2, effect_query FROM model_converstation WHERE conv_code='{conv_code}';")
            try:
                self.client.DBC['model_conversation'][conv_code] = c_Conversation(res[0])
                return self.client.DBC['model_conversation'][conv_code]
            except TypeError: return False

    async def dbcGetNPC(self, npc_code):
        try:
            return self.client.DBC['model_conversation'][npc_code]
        except KeyError:
            res = await self.client.quefe(f"SELECT npc_code, name, description, branch, evo, lp, str, chain, speed, au_FLAME, au_ICE, au_HOLY, au_DARK, rewards, illulink FROM model_NPC WHERE npc_code='{npc_code}';")
            try:
                self.client.DBC['model_NPC'][npc_code] = c_NPC(res[0])
                return self.client.DBC['model_NPC'][npc_code]
            except TypeError: return False




def setup(client):
    client.add_cog(avaNPC(client))







# ================== THING ==================

class c_NPC:
    def __init__(self, pack, narrator=False):
        """
        npc_code, name, description, branch, evo, lp, strr, chain, speed, au_FLAME, au_ICE, au_HOLY, au_DARK, rewards, illulink = pack
        """
        self.narrator = narrator
        if not narrator: self.npc_code, self.name, self.description, self.branch, self.evo, self.lp, self.strr, self.chain, self.speed, self.au_FLAME, self.au_ICE, self.au_HOLY, self.au_DARK, self.rewards, self.illulink = pack
        else: self.npc_code, self.name, self.description, self.branch, self.evo, self.lp, self.strr, self.chain, self.speed, self.au_FLAME, self.au_ICE, self.au_HOLY, self.au_DARK, self.rewards, self.illulink = ('n/a', 'n/a', 'n/a', 'n/a', 1, 1, 1, 1, 1, 1, 1, 1, 1, '', '')
        self.illulink = self.illulink.split(' <> ')
        self.search_name = self.name.lower()

    def check(self, npc_code='', name=''):
        if npc_code and npc_code == self.npc_code: return True
        if name and name in self.search_name: return True
        return False


class c_Conversation:
    def __init__(self, pack):
        """
        ordera, conv_code, type, line, node_1, node_2, effect_query

        <TURN> in a <conversation> is a series of lines that has the same speaker
        """

        self.ordera, self.conv_code, self.type, lines, self.node_1, self.node_2, self.effect_query = pack

        # Partial conv split
        self.line = []
        for il in lines.split(' ||| '):
            # Turns of conv       (author, (line1, line2,), illulink)
            a = il.split(' --- ')
            if len(a) < 3: a.append('')
            elif a[2] == 'n/a': a[2] = ''
            # Line
            a[1] = tuple(a[1].split(' >>> '))
            self.line.append(tuple(a))

        # Multi-node
        try: self.node_1 = self.node_1.split(' - ')
        except AttributeError: self.node_1 = []
        try: self.node_2 = self.node_2.split(' - ')
        except AttributeError: self.node_2 = []
