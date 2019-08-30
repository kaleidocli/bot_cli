import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors

import random
import asyncio
from functools import partial
from datetime import datetime

from .avaTools import avaTools
from .avaUtils import avaUtils

class avaSocial:
    def __init__(self, client):
        self.client = client
        self.__cd_check = self.client.thp.cd_check
        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)


    # ========================= FAMILY ========================

    @commands.command()
    @commands.cooldown(1, 90, type=BucketType.user)
    async def marry(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        try: target = ctx.message.mentions[0]
        except IndexError: await ctx.send(f":revolving_hearts: Please tell us your love one, **{ctx.message.author.name}**!"); return

        try: name, partner, cur_PLACE = await self.client.quefe(f"SELECT name, partner, cur_PLACE FROM personal_info WHERE id='{ctx.author.id}' AND partner='n/a';")
        except TypeError: await ctx.send(f"<:osit:544356212846886924> Hey no cheating, {ctx.message.author.name}!"); return
        try: t_name, t_partner, t_cur_PLACE = await self.client.quefe(f"SELECT name, partner, cur_PLACE FROM personal_info WHERE id='{target.id}' AND partner='n/a';")
        except TypeError: await ctx.send(f"<:osit:544356212846886924> User has already married, {ctx.message.author.name}!"); return

        if ctx.author == target: await ctx.send(f":revolving_hearts: **I know this is wrong but...**"); await asyncio.sleep(3)
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
        await self.client._cursor.execute(f"UPDATE personal_info SET partner='{target.id}' WHERE id='{ctx.author.id}'; UPDATE personal_info SET partner='{str(ctx.message.author.id)}' WHERE id='{target.id}';")

    @commands.command(aliases=['unsure'])
    @commands.cooldown(1, 15, type=BucketType.user)
    async def sex(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        cmd_tag = 'sex'
        if not await self.__cd_check(ctx.message, cmd_tag, f"<:fufu:508437298808094742> Calm your lewdness, **{ctx.author.name}**~~"): return

        # User info
        try: LP, max_LP, STA, max_STA, charm, partner, gender = await self.client.quefe(f"SELECT LP, max_LP, STA, max_STA, charm, partner, gender FROM personal_info WHERE id='{ctx.author.id}' AND partner!='n/a';")
        except TypeError: await ctx.send("<:osit:544356212846886924> Get yourself a partner first :>"); return

        # Partner info
        t_LP, t_max_LP, t_STA, t_max_STA, t_charm, t_gender, t_name = await self.client.quefe(f"SELECT LP, max_LP, STA, max_STA, charm, gender, name FROM personal_info WHERE id='{partner}';")
        #tar = self.client.get_user(int(partner))
        tar = await self.client.loop.run_in_executor(None, partial(self.client.get_user, int(partner)))

        # ================== BIRTH
        if await self.utils.percenter(charm+t_charm, total=200) and gender != t_gender:
            await ctx.send(f"||<a:RingingBell:559282950190006282> Name your child. Timeout=30s||\n<:sailu:559155210384048129> Among these dark of the age, a new life has enlighten...\n⠀⠀⠀⠀**{ctx.author.name}** and {tar.mention}, how will you christen your little?\n⠀⠀⠀⠀⠀⠀⠀⠀Won't you do, keep shut and remain silence.")

            def UMCc_check(m):
                return m.channel == ctx.channel and m.author in [tar, ctx.author]

            try: resp = await self.client.wait_for('message', timeout=30, check=UMCc_check)
            except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Life arrived, yet no place for it to harbor..."); return

            if gender == 'm': father = f"{ctx.author.id}"; mother = f"{tar.id}"
            else: father = f"{ctx.author.id}"; mother = f"{tar.id}"            

            year, month, day, hour, minute = await self.client.loop.run_in_executor(None, self.utils.time_get)
            id = f"{''.join([str(year), str(month), str(day), str(hour), str(minute)])}{datetime.now().microsecond}"
            await self.tools.character_generate(id, resp.content, dob=[year, month, day, hour, minute], resu=False)
            await self.tools.hierarchy_generate(id, father_id=father, mother_id=mother, guardian_id='n/a', chem_value=0)
            await ctx.send(f"<:sailu:559155210384048129> The whole Pralaeyr welcomes you, **{resp.content}**! May the Olds look upon you, {ctx.author.mention} and **{t_name}**.")

            # DAMAGING
            if gender == 'f':
                LP = await self.tools.division_LP(LP, max_LP, time=8)
                await self.client._cursor.execute(f"UPDATE personal_info SET LP={LP} WHERE id='{ctx.author.id}';")
            else:
                t_LP = await self.tools.division_LP(t_LP, t_max_LP, time=8)
                await self.client._cursor.execute(f"UPDATE personal_info SET LP={t_LP} WHERE id='{partner}';")

        # ================== SEX
        else:
            await ctx.send(f":heart: {tar.mention}, **{ctx.author.name}** is feeling *unsure*.\nType `sure` to make {ctx.author.name} sure, 20 secs left to grab your chance!")

            def UMCc_check(m):
                return m.channel == ctx.channel and m.author == tar

            try: resp = await self.client.wait_for('message', timeout=20, check=UMCc_check)
            except asyncio.TimeoutError: await ctx.send("<:gees:559192536195923999> Neither of them are sure..."); return

            slib = {'mf': ['https://media.giphy.com/media/HocMFeabR7rKU/giphy.gif', 'https://imgur.com/lA3AxJB.gif'],
            'fm': ['https://media.giphy.com/media/HocMFeabR7rKU/giphy.gif'],
            'mm': ['https://media.giphy.com/media/Ta8nU0hjzCB6o/giphy.gif'],
            'ff': ['https://media.giphy.com/media/4Al6v0Mmu20gg/giphy.gif', 'https://media.giphy.com/media/rvOyFjbMz86Mo/giphy.gif']}
            reco_percent = (STA / max_STA + t_STA / t_max_STA) / 2
            
            await ctx.send(embed=discord.Embed(description="""```The two got closer, and closer, and closer, and close--...```""", colour=0xFFE2FF).set_image(url=random.choice(slib[gender+t_gender])), delete_after=10)

            await self.client._cursor.execute(f"UPDATE personal_info SET STA=0, LP=IF(id='{ctx.author.id}', {int(LP + LP * reco_percent)}, {int(t_LP + t_LP * reco_percent)}) WHERE id IN ('{ctx.author.id}', '{partner}');")
            await self.tools.ava_scan(ctx.message, type='life_check')

        await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.set, f'{cmd_tag}{ctx.author.id}', 'sex', ex=3600, nx=True))

    @commands.command()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def divorce(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return


        partner = await self.client.quefe(f"SELECT partner FROM personal_info WHERE id='{ctx.author.id}';")
        if partner[0] == 'n/a': await ctx.send("<:osit:544356212846886924> As if you have a partner :P"); return
        p2 = await self.client.quefe(f"SELECT name FROM personal_info WHERE id='{partner[0]}';")
        #except TypeError: await ctx.send("<:osit:544356212846886924> As if you have a partner :P"); return
        partner = list(partner); partner.append(p2[0])

        def UMCc_check(m):
            return m.channel == ctx.channel and m.author == ctx.author and m.content == "let's fcking divorce"

        # NAME
        await ctx.send(f":broken_heart: Divorce with **{partner[1]}**?\n||<a:RingingBell:559282950190006282> Timeout=15s · Key=`let's fcking divorce`||")
        try: 
            await self.client.wait_for('message', timeout=15, check=UMCc_check)
        except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request times out!"); return

        await self.client._cursor.execute(f"UPDATE personal_info SET partner='n/a' WHERE id IN ('{ctx.author.id}', '{partner[0]}'); UPDATE environ_hierarchy SET father_id=IF(father_id='{ctx.author.id}', 'n/a', father_id), mother_id=IF(mother_id='{ctx.author.id}', 'n/a', mother_id), guardian_id=IF(guardian_id='{ctx.author.id}', 'n/a', guardian_id) WHERE '{ctx.author.id}' IN (father_id, mother_id, guardian_id);")
        await ctx.send(":broken_heart: You are now strangers, to each other.")

    @commands.command()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def family(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        # Get info
        id, name, t_id, t_name = await self.client.quefe(f"SELECT id, name, partner AS prtn, (SELECT name FROM personal_info WHERE id=prtn) FROM personal_info WHERE id='{ctx.author.id}';")
        if t_name: target_addon = f" AND '{t_id}' IN (mother_id, father_id, guardian_id)"
        else: target_addon = ''
        children = await self.client.quefe(f"SELECT id, name, gender, age FROM personal_info WHERE id IN (SELECT child_id FROM environ_hierarchy WHERE '{id}' IN (mother_id, father_id, guardian_id) {target_addon});", type='all')
        gengen = {'m': 'Male', 'f': 'Female'}

        def makeembed(top, least, pages, currentpage):
            line = '\n'

            for child in children[top:least]:
                print(children, child)
                line = line + f"""<:sailu:559155210384048129> **{child[1]}** ({child[3]}), {gengen[child[2]]}\n      ╟||`{child[0]}`||\n"""

            if t_name: reembed = discord.Embed(description=line, colour = discord.Colour(0xFFE2FF)).set_thumbnail(url=ctx.author.avatar_url).set_author(name=f"{name.capitalize()} & {t_name.capitalize()}", icon_url='https://imgur.com/jkznAfT.png')
            else: reembed = discord.Embed(description=line, colour = discord.Colour(0xFFE2FF)).set_thumbnail(url=ctx.author.avatar_url).set_author(name=f"{name.capitalize()}... . . .. .   .  .", icon_url='https://imgur.com/jkznAfT.png')
            return reembed
            #else:
            #    await ctx.send("*Nothing but dust here...*")
        
        async def attachreaction(msg):
            await msg.add_reaction("\U000023ee")    #Top-left
            await msg.add_reaction("\U00002b05")    #Left
            await msg.add_reaction("\U000027a1")    #Right
            await msg.add_reaction("\U000023ed")    #Top-right

        try: pages = len(children)//4
        except TypeError:
            if t_name: reembed = discord.Embed(colour = discord.Colour(0xFFE2FF)).set_author(name=f"{name.capitalize()} & {t_name.capitalize()}", icon_url='https://imgur.com/jkznAfT.png')
            else: reembed = discord.Embed(colour = discord.Colour(0xFFE2FF)).set_author(name=f"{name.capitalize()}... . . .. .   .  .", icon_url='https://imgur.com/jkznAfT.png')
            await ctx.send(embed=reembed)
            return
        if len(children)%4 != 0: pages += 1
        currentpage = 1
        cursor = 0

        # pylint: disable=unused-variable
        emli = []
        for curp in range(pages):
            myembed = makeembed(currentpage*4-4, currentpage*4, pages, currentpage)
            emli.append(myembed)
            currentpage += 1
        # pylint: enable=unused-variable

        if not emli: await ctx.send(":crown: No child!"); return
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



    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def like(self, ctx, *args):
        cmd_tag = 'like'
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        if not await self.__cd_check(ctx.message, cmd_tag, f"<:fufu:508437298808094742> You cannot award more merits at the moment, **{ctx.author.name}**."): return

        # Get target
        try: target = ctx.message.mentions[0]
        except (IndexError, TypeError): await ctx.send(f"<:osit:544356212846886924> Missing the receiver, **{ctx.author.name}**"); return

        if await self.client._cursor.execute(f"UPDATE personal_info SET merit=merit+1 WHERE id='{target.id}';") == 0:
            await ctx.send(f"<:osit:544356212846886924> User has not incarnated, **{ctx.author.name}**!"); return

        await ctx.send(f"<:4_:544354428396896276> **{ctx.author.name}** has given {target.mention} a merit!")
        await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.set, f'{cmd_tag}{ctx.author.id}', 'like', ex=86400, nx=True))

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def dislike(self, ctx, *args):
        cmd_tag = 'dislike'
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        if not await self.__cd_check(ctx.message, cmd_tag, f"<:fufu:508437298808094742> You cannot negate more merits at the moment, **{ctx.author.name}**."): return

        # Get target
        try: target = ctx.message.mentions[0]
        except (IndexError, TypeError): await ctx.send(f"<:osit:544356212846886924> Missing the target, **{ctx.author.name}**"); return

        if await self.client._cursor.execute(f"UPDATE personal_info SET merit=merit-1 WHERE id='{target.id}';") == 0:
            await ctx.send(f"<:osit:544356212846886924> User has not incarnated, **{ctx.author.name}**!"); return

        await ctx.send(f"<:argh:544354429302865932> **{ctx.author.name}** has humiliated {target.mention}!")
        await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.set, f'{cmd_tag}{ctx.author.id}', 'dislike', ex=86400, nx=True))




    # =========================== COMMERCIAL ===========================

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def sell(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
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
                t_cur_X, t_cur_Y, t_cur_PLACE, t_money = await self.client.quefe(f"SELECT cur_X, cur_Y, cur_PLACE, money FROM personal_info WHERE id='{receiver.id}';")
                cur_X, cur_Y, cur_PLACE = await self.client.quefe(f"SELECT cur_X, cur_Y, cur_PLACE FROM personal_info WHERE id='{ctx.author.id}';")
            # E: Id not found
            except TypeError: await ctx.send("<:osit:544356212846886924> User don't have an ava!"); return

            # Get item's info
            try: w_tags, w_name, w_quantity, w_code = await self.client.quefe(f"SELECT tags, name, quantity, item_code FROM pi_inventory WHERE existence='GOOD' AND user_id='{ctx.author.id}' AND item_id='{item_id}';")
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
            if await self.utils.distance_tools(cur_X, cur_Y, t_cur_X, t_cur_Y) > 50:
                await ctx.send(f"<:osit:544356212846886924> You need to be within **50 m** range of the receiver, **{ctx.author.name}**!"); return

            # INCONSUMABLE
            if 'inconsumable' in w_tags:
                await self.client._cursor.execute(f"UPDATE pi_inventory SET user_id='{receiver.id}' WHERE item_id='{item_id}';")
            
            # CONSUMABLE
            else:
                # Quantity given
                try:
                    quantity = int(raw[1])
                    # SCAM :)
                    if quantity <= 0: await ctx.send("**Heyyyyyyyyy scammer-!**"); return
                    if w_code.startswith('ig'): await self.client._cursor.execute(f"SELECT func_ig_reward('{receiver.id}', '{w_code}', {quantity}); SELECT func_i_delete('{ctx.author.id}', '{w_code}', {quantity});")
                    else: await self.client._cursor.execute(f"SELECT func_it_reward('{receiver.id}', '{w_code}', {quantity}); SELECT func_i_delete('{ctx.author.id}', '{w_code}', {quantity});")
                    # Quantity check
                    #if int(raw[1]) >= w_quantity:
                    #    quantity = w_quantity
                    #    # Check if receiver has already had the item
                    #    if w_code.startswith('ig'): await self.client._cursor.execute(f"SELECT func_ig_reward('{receiver.id}', '{w_code}', {quantity}); UPDATE pi_inventory SET existence='BAD' WHERE user_id='{ctx.author.id}' AND item_code='{w_code}';")
                    #    else: await self.client._cursor.execute(f"SELECT func_it_reward('{receiver.id}', '{w_code}', {quantity}); UPDATE pi_inventory SET existence='BAD' WHERE user_id='{ctx.author.id}' AND item_code='{w_code}';")

                    #else:
                    #    quantity = int(raw[1])
                    #    # SCAM :)
                    #    if quantity <= 0: await ctx.send("**Heyyyyyyyyy scammer-!**"); return
                    #    # Check if receiver has already had the item
                    #    if w_code.startswith('ig'): await self.client._cursor.execute(f"SELECT func_ig_reward('{receiver.id}', '{w_code}', {quantity}); UPDATE pi_inventory SET quantity=quantity-{quantity} WHERE user_id='{ctx.author.id}' AND item_code='{w_code}';")
                    #    else: await self.client._cursor.execute(f"SELECT func_ig_reward('{receiver.id}', '{w_code}', {quantity}); UPDATE pi_inventory SET quantity=quantity-{quantity} WHERE user_id='{ctx.author.id}' AND item_code='{w_code}';")
                # Quantity NOT given
                except (ValueError, IndexError): 
                    quantity = 1
                    # Check if receiver has already had the item
                    if w_code.startswith('ig'): await self.client._cursor.execute(f"SELECT func_ig_reward('{receiver.id}', '{w_code}', {quantity}); SELECT func_i_delete('{ctx.author.id}', '{w_code}', {quantity});")
                    else: await self.client._cursor.execute(f"SELECT func_it_reward('{receiver.id}', '{w_code}', {quantity}); SELECT func_i_delete('{ctx.author.id}', '{w_code}', {quantity});")

            # Inform, of course :>
            await ctx.send(f":white_check_mark: You've been given `{quantity}` `{w_code}`|**{w_name}**, {receiver.mention}!"); return

        except commands.CommandError:
            try: quantity = int(raw[1])
            except (IndexError, ValueError): quantity = 1

        # BOT SELL ==================================
        try: right_hand, left_hand = await self.client.quefe(f"SELECT right_hand, left_hand FROM personal_info WHERE id='{ctx.author.id}' AND cur_X<1 AND cur_Y<1;")
        # E: Out of PB
        except TypeError: await ctx.send("<:osit:544356212846886924> You think you can find customers outside of **Peace Belt**??"); return

        quantity = 1
        try: quantity = int(raw[1])
        except (IndexError, ValueError): pass

        # SCAM :)
        if quantity <= 0: await ctx.send("**Heyyyyyyyyy scammer-!**"); return  

        try: w_name, w_price, w_quantity, w_tags = await self.client.quefe(f"SELECT name, price, quantity, tags FROM pi_inventory WHERE existence='GOOD' AND user_id='{ctx.author.id}' AND item_id='{item_id}';")
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
        await self.client._cursor.execute(receive_query + quantity_query)

        await ctx.send(f":white_check_mark: You received **<:36pxGold:548661444133126185>{receive}** from selling {quantity} `{item_id}`|**{w_name}**, **{ctx.message.author.name}**!")

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def give(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        raw = list(args)

        # Receiver check
        try:
            receiver = await commands.UserConverter().convert(ctx, raw[1])
            try:
                t_cur_X, t_cur_Y, t_cur_PLACE, t_partner = await self.client.quefe(f"SELECT cur_X, cur_Y, cur_PLACE, partner FROM personal_info WHERE id='{receiver.id}';")
                cur_X, cur_Y, cur_PLACE, money, partner = await self.client.quefe(f"SELECT cur_X, cur_Y, cur_PLACE, money, partner FROM personal_info WHERE id='{ctx.author.id}';")
            # E: Id not found
            except TypeError: await ctx.send("<:osit:544356212846886924> User don't have an ava!"); return
        except (commands.CommandError, IndexError): await ctx.send(f"<:osit:544356212846886924> Please provide a receiver, **{ctx.author.name}**!"); return

        try: package = int(raw[0])
        except (IndexError, ValueError): await ctx.send(f"<:osit:544356212846886924> Please provide an amount of money you want to give"); return

        # Distance check
        if cur_PLACE != t_cur_PLACE:
            if not (partner == str(receiver.id) and not t_partner == str(ctx.author.id)):
                await ctx.send(f"<:osit:544356212846886924> You need to be in the same region with the receiver, **{ctx.author.name}**!"); return
        if await self.utils.distance_tools(cur_X, cur_Y, t_cur_X, t_cur_Y) > 50:
            if not (partner == str(receiver.id) and t_partner == str(ctx.author.id)):
                await ctx.send(f"<:osit:544356212846886924> You need to be within **50 m** range of the receiver, **{ctx.author.name}**!"); return

        # Money check
        try:
            if package > money: await ctx.send("<:osit:544356212846886924> Insufficient balance!"); return
            # SCAM :)
            if package <= 0: await ctx.send("**Heyyyyyyyyy scammer-!**"); return
        except ValueError: await ctx.send("<:osit:544356212846886924> Invalid syntax!"); return
            
        # Transfer
        await self.client._cursor.execute(f"UPDATE personal_info SET money=money+IF(id='{ctx.author.id}', -{package}, {package}) WHERE id IN ('{ctx.author.id}', '{receiver.id}');")
        await ctx.send(f":white_check_mark: You've been given **<:36pxGold:548661444133126185>{raw[0]}**, {receiver.mention}!")

    @commands.cooldown(1, 10, type=BucketType.user)
    async def trade(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        raw = list(args)

        # Receiver check
        try: 
            receiver = ctx.message.mentions[0]
            try: 
                t_cur_X, t_cur_Y, t_cur_PLACE, t_money = await self.client._cursor.execute(f"SELECT cur_X, cur_Y, cur_PLACE, money FROM personal_info WHERE id='{receiver.id}';")
                cur_X, cur_Y, cur_PLACE = await self.client._cursor.execute(f"SELECT cur_X, cur_Y, cur_PLACE FROM personal_info WHERE id='{str(ctx.message.author.id)}';")
            # E: Id not found
            except TypeError: await ctx.send("<:osit:544356212846886924> User don't have an ava!"); return
        except IndexError: await ctx.send(f"<:osit:544356212846886924> Please provide a receiver, **{ctx.message.author.name}**!"); return

        # Distance check
        if cur_PLACE != t_cur_PLACE:
            await ctx.send(f"<:osit:544356212846886924> You need to be in the same region with the receiver, **{ctx.message.author.name}**!"); return
        if await self.utils.distance_tools(cur_X, cur_Y, t_cur_X, t_cur_Y, int(args[0])/1000, int(args[1])/1000) > 50:
            await ctx.send(f"<:osit:544356212846886924> You need to be within **50 m** range of the receiver, **{ctx.message.author.name}**!"); return

        # Get item's info
        try: w_tags, w_name, w_quantity, w_code = await self.client.quefe(f"SELECT tags, name, quantity, item_code FROM pi_inventory WHERE existence='GOOD' AND user_id='{str(ctx.message.author.id)}' AND item_id='{raw[0]}';")
        except TypeError: await ctx.send("<:osit:544356212846886924> You don't own this item!"); return

        if 'untradable' in w_tags: await ctx.send(f"<:osit:544356212846886924> You cannot trade this item, **{ctx.message.author.name}**. It's *untradable*, look at its tags."); return

        # INCONSUMABLE
        if 'inconsumable' in w_tags:
            await self.client._cursor.execute(f"UPDATE pi_inventory SET user_id='{receiver.id}' WHERE item_id='{raw[0]}';")
        
        # CONSUMABLE
        else:
            # Quantity given
            try:
                # Quantity check
                if int(raw[1]) >= w_quantity:
                    quantity = w_quantity
                    # Check if receiver has already had the item
                    if await self.client._cursor.execute(f"UPDATE pi_inventory SET quantity=quantity+{quantity} WHERE user_id='{receiver.id}' AND item_code='{w_code}';") == 0:
                        await self.client._cursor.execute(f"UPDATE pi_inventory SET user_id='{receiver.id}' WHERE item_id='{raw[0]}';")

                else:
                    quantity = int(raw[1])
                    # SCAM :)
                    if quantity <= 0: await ctx.send("**Heyyyyyyyyy scammer-!**"); return
                    # Check if receiver has already had the item
                    if await self.client._cursor.execute(f"UPDATE pi_inventory SET quantity=quantity+{quantity} WHERE user_id='{receiver.id}' AND item_code='{w_code}';") == 0:
                        await self.client._cursor.execute(f"INSERT INTO pi_inventory SELECT 0, '{receiver.id}', item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, order_query, passive_query, ultima_query, {quantity}, price, dmg, stealth, aura, craft_value, illulink FROM pi_inventory WHERE existence='GOOD' AND item_id='{w_code}' AND user_id='{str(ctx.message.author.id)}';")
            # Quantit NOT given
            except (ValueError, IndexError): 
                quantity = 1
                # Check if receiver has already had the item
                if await self.client._cursor.execute(f"UPDATE pi_inventory SET quantity=quantity+{quantity} WHERE user_id='{receiver.id}' AND item_code='{w_code}';") == 0:
                    await self.client._cursor.execute(f"INSERT INTO pi_inventory SELECT 0, '{receiver.id}', item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, order_query, passive_query, ultima_query, {quantity}, price, dmg, stealth, aura, craft_value, illulink FROM pi_inventory WHERE existence='GOOD' AND item_id='{w_code}' AND user_id='{str(ctx.message.author.id)}';")

        # Inform, of course :>
        await ctx.send(f":white_check_mark: You've been given `{quantity}` `{w_code}`|**{w_name}**, {ctx.message.author.mention}!")










def setup(client):
    client.add_cog(avaSocial(client))
