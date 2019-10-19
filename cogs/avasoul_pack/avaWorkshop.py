import random
import asyncio
from functools import partial

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors

from .avaTools import avaTools
from .avaUtils import avaUtils



class avaWorkshop(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.__cd_check = self.client.thp.cd_check
        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)

        print("|| Workshop --- READY!")



# ================== EVENTS ==================

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     print("|| Workshop --- READY!")



# ================== WORKSHOP ==================

    @commands.command()
    @commands.cooldown(1, 60, type=BucketType.user)
    async def infuse(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        raw = list(args)

        try:
            # Item's info get
            try:
                w_name, w_evo = await self.client.quefe(f"SELECT name, evo FROM pi_inventory WHERE existence='GOOD' AND user_id='{str(ctx.message.author.id)}' AND item_id='{raw[0]}';")
                t_w_quantity, t_w_infuse_query, t_w_evo = await self.client.quefe(f"SELECT quantity, infuse_query, evo FROM pi_inventory WHERE existence='GOOD' AND user_id='{str(ctx.message.author.id)}' AND item_id='{raw[1]}';")
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
                inflv_dict = {3: ('elementary', 'elemology'), 
                            10: ('middleschool', 'elemology'),
                            15: ('highschool', 'elemology'),
                            20: ('associate', 'elemology'), 
                            25: ('bachelor', 'elemology'),
                            30: ('master', 'elemology'),
                            40: ('doctorate', 'elemology')}
                if w_evo > 40: detemp = f" AND degree='{inflv_dict[40][0]}' AND major='{inflv_dict[40][1]}'"
                elif w_evo > 30: detemp = f" AND degree='{inflv_dict[30][0]}' AND major='{inflv_dict[30][1]}'"
                elif w_evo > 25: detemp = f" AND degree='{inflv_dict[25][0]}' AND major='{inflv_dict[25][1]}'"
                elif w_evo > 20: detemp = f" AND degree='{inflv_dict[20][0]}' AND major='{inflv_dict[20][1]}'"
                elif w_evo > 15: detemp = f" AND degree='{inflv_dict[15][0]}' AND major='{inflv_dict[15][1]}'"
                elif w_evo > 10: detemp = f" AND degree='{inflv_dict[10][0]}' AND major='{inflv_dict[10][1]}'"
                elif w_evo > 3: detemp = f" AND degree='{inflv_dict[3][0]}' AND major='{inflv_dict[3][1]}'"
                else: detemp = ''
                d_check = f"AND EXISTS (SELECT * FROM pi_degrees WHERE user_id='{str(ctx.message.author.id)}' {detemp});"
            except KeyError: d_check = ''

            # Preparing
            t_w_infuse_query = t_w_infuse_query.replace('user_id_here', str(ctx.message.author.id)).replace('item_id_here', raw[0])
            if d_check and t_w_infuse_query.endswith(';'):
                t_w_infuse_query = t_w_infuse_query[:-1]

            # INFUSE
            if await self.client._cursor.execute(f"{t_w_infuse_query} {d_check};") == 0: await ctx.send(f"<:osit:544356212846886924> You cannot infuse EVO`{w_evo}` item with your current status."); return

            # Remove
            await self.client._cursor.execute(f"SELECT func_i_delete('{ctx.author.id}', '{raw[1]}', {quantity});")
            # if quantity == t_w_quantity: await self.client._cursor.execute(f"UPDATE pi_inventory SET existence='BAD' WHERE user_id='{ctx.author.id}' AND item_id='{raw[1]}';")
            # else: await self.client._cursor.execute(f"UPDATE pi_inventory SET quantity=quantity-{quantity} WHERE user_id='{str(ctx.message.author.id)}' AND item_id='{raw[1]}';")

            # Inform :>
            await ctx.send(f":white_check_mark: Infusion with `{raw[0]}`|**{w_name}** was a success. The other item has been destroyed."); return

        # E: Not enough args
        except IndexError: await ctx.send("<:osit:544356212846886924> What? You think you can infuse thing out of nowhere?"); return

    @commands.command()
    @commands.cooldown(1, 60, type=BucketType.user)
    async def merge(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        cmd_tag = 'merge'
        raw = list(args)

        # Check if the previous course has been finished yet
        if not await self.__cd_check(ctx.message, cmd_tag, "No."): return

        try:
            # Item's info get
            try:
                w_name, w_evo, w_weight, w_defend, w_multiplier, w_str, w_intt, w_sta, w_speed, w_acc_randomness, w_acc_range, w_r_min, w_r_max, w_firing_rate, w_dmg, w_stealth, w_price = await self.client.quefe(f"SELECT name, evo, weight, defend, multiplier, str, intt, sta, speed, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, price FROM pi_inventory WHERE existence='GOOD' AND user_id='{str(ctx.message.author.id)}' AND item_id='{raw[0]}';")
                t_w_name, t_w_evo, t_w_weight, t_w_defend, t_w_multiplier, t_w_str, t_w_intt, t_w_sta, t_w_speed, t_w_acc_randomness, t_w_acc_range, t_w_r_min, t_w_r_max, t_w_firing_rate, t_w_dmg, t_w_stealth, t_w_price = await self.client.quefe(f"SELECT name, evo, weight, defend, multiplier, str, intt, sta, speed, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, price FROM pi_inventory WHERE existence='GOOD' AND user_id='{str(ctx.message.author.id)}' AND item_id='{raw[1]}';")
            # E: Item's not found
            except TypeError: await ctx.send("<:osit:544356212846886924> Item's not found!"); return

            # Degrees
            degrees = await self.client.quefe(f"SELECT degree FROM pi_degrees WHERE user_id='{str(ctx.message.author.id)}' AND major='engineering';")
            try: degrees = set(degrees)
            # E: No engineering degree
            except TypeError: degrees = ()

            # Price
            price = (abs(w_evo - t_w_evo)*1000)//(1 + len(degrees))
            if price < 1: price = 1

            await ctx.send(f":tools: Merging these two items will cost you **<:36pxGold:548661444133126185>{price}**.\n<a:RingingBell:559282950190006282> Proceed? (Key: `merging confirm` | Timeout=20s)")
            try: await self.client.wait_for('message', timeout=20, check=lambda m: m.channel == ctx.channel and m.content == 'merging confirm' and m.author == ctx.author)
            except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request timeout!"); return

            # Deduct money
            if await self.client._cursor.execute(f"UPDATE personal_info SET money=money-{price} WHERE id = '{ctx.author.id}' AND money >= {price};") == 0:
                await ctx.send("<:osit:544356212846886924> Insufficient balance!"); return

            # MERGE
            try: W_weight = round(random.uniform(0, (w_weight + t_w_weight)/2), 1)
            except IndexError: W_weight = 0
            try: W_multiplier = round(random.uniform(0, (w_multiplier + t_w_multiplier)/10*8), 1)
            except IndexError: W_multiplier = 0
            try: W_str = round(random.uniform(0, (w_str + t_w_str)/10*8), 1)
            except IndexError: W_str = 0
            try: W_intt = round(random.uniform(0, (w_intt + t_w_intt)/10*7.5), 1)
            except IndexError: W_intt = 0
            try: W_sta = round(random.uniform(0, w_sta + t_w_sta), 1)
            except IndexError: W_sta = 0
            try: W_speed = round(random.uniform(0, w_speed + t_w_speed), 1)
            except IndexError: W_speed = 0
            try: W_acc_randomness = round(random.choice(range(int(w_acc_randomness + t_w_acc_randomness))), 1)
            except IndexError: W_acc_randomness = 0
            try: W_acc_range = round(random.choice(range(int(w_acc_range + t_w_acc_range))), 1)
            except IndexError: W_acc_range = 0
            try: W_r_min = round(random.choice(range(int(w_r_min + t_w_r_min))), 1)
            except IndexError: W_r_min = 0
            try: W_r_max = round(random.choice(range(int(w_r_max + t_w_r_max))), 1)
            except IndexError: W_r_max = 0
            try: W_dmg = round(random.choice(range((w_dmg + t_w_dmg)//10*7+1)), 1)
            except IndexError: W_dmg = 0
            try: W_stealth = round(random.choice(range(int(w_stealth + t_w_stealth))), 1)
            except IndexError: W_stealth = 0
            w_price = int(w_price - w_price//100*35)
            t_w_price = int(t_w_price - t_w_price//100*35)

            if not int(w_evo): w_evo = 1
            else: w_evo = int(w_evo)
            if not int(t_w_evo): t_w_evo = 1
            else: t_w_evo = int(t_w_evo)

            W_evo = w_evo + t_w_evo

            # Insert
            await self.client._cursor.execute(f"UPDATE pi_inventory SET weight={W_weight}, multiplier={W_multiplier}, str={W_str}, intt={W_intt}, sta={W_sta}, speed={W_speed}, accuracy_randomness={W_acc_randomness}, accuracy_range={W_acc_range}, range_min={W_r_min}, range_max={W_r_max}, dmg={W_dmg}, stealth={W_stealth}, evo={W_evo}, price={w_price} WHERE user_id='{str(ctx.message.author.id)}' AND item_id='{raw[0]}';")
            await self.client._cursor.execute(f"UPDATE pi_inventory SET weight={W_weight}, multiplier={W_multiplier}, str={W_str}, intt={W_intt}, sta={W_sta}, speed={W_speed}, accuracy_randomness={W_acc_randomness}, accuracy_range={W_acc_range}, range_min={W_r_min}, range_max={W_r_max}, dmg={W_dmg}, stealth={W_stealth}, evo={W_evo}, price={t_w_price} WHERE user_id='{str(ctx.message.author.id)}' AND item_id='{raw[1]}';")

            # Inform :>
            await ctx.send(f":white_check_mark: Merged `{raw[0]}`|**{w_name}** with `{raw[1]}`|**{t_w_name}**!")
            await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.set, f'{cmd_tag}{str(ctx.message.author.id)}', 'merging', ex=7200, nx=True))

        # E: Not enough args
        except ZeroDivisionError: await ctx.send("<:osit:544356212846886924> How could you even merge something with its own?!"); return

    @commands.command()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def craft(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

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
            craft_value = await self.client.quefe(f"SELECT craft_value FROM pi_inventory WHERE existence='GOOD' AND user_id='{ctx.author.id}' AND item_id={item_id} AND quantity>={quantity};")

            # Calculate each pack
            try: pack_values.append(craft_value[0]*quantity)
            except TypeError: await ctx.send(f"<:osit:544356212846886924> You don't have **{quantity}** item `{item_id}`. Please check your *item's id* or *its quantity*."); return
        # Calculate total craft_value
        total_cv = sum(pack_values)

        # Get FORMULA
        try: check_query, effect_query, info_msg = await self.client.quefe(f"SELECT check_query, effect_query, info_msg FROM model_formula WHERE formula_value={total_cv};")
        except TypeError: await ctx.send(":tools: Oops! You tried but nothing happened :<"); return

        info_msg = info_msg.split(' || ')
        if check_query:
            check_query = check_query.replace('user_id_here', f"{ctx.author.id}")
            if self.client._cursor.execute(check_query) == 0: await ctx.send(f":tools: Oops! {info_msg[1]} :<"); return

        effect_query = effect_query.replace('user_id_here', f"{ctx.author.id}")

        # Take effect (reward, effect, etc.)
        if await self.client._cursor.execute(effect_query) == 0: await ctx.send(f":tools: Oops! {info_msg[1]} :<"); return
        
        # Inform
        await ctx.send(f":tools: {info_msg[0]} **Successfully crafted!**")

    @commands.command(aliases=['fml'])
    @commands.cooldown(1, 10, type=BucketType.user)
    async def formula(self, ctx, *args):

        # FORMULA
        try:
            # Formulas' code
            if args[0].startswith('fm'):
                try: formula_code, name, formula_value, description, tags, kit = await self.client.quefe(f"SELECT formula_code, name, formula_value, description, tags, kit FROM model_formula WHERE formula_code='{args[0]}';")
                except TypeError: await ctx.send(":tools: Formula not found!"); return
            
                temb = discord.Embed(title=f":tools: `{formula_code}`|**{name}**", description=f"""```{description}```""", colour = discord.Colour(0x011C3A))
                temb.add_field(name=f'╟ K I T [{formula_value}]', value=f'╟ {kit}', inline=True)
                temb.add_field(name=f'╟ T A G S', value=f"╟ `{tags.replace(' - ', '` · `')}`", inline=True)

                await ctx.send(embed=temb, delete_after=15)

            # Formulas' tag
            elif args[0].startswith('ar') or args[0].startswith('it') or args[0].startswith('ig') or args[0].startswith('bp') or args[0].startswith('am'):
                formus = await self.client.quefe(f"SELECT formula_code, name FROM model_formula WHERE tags LIKE '%{await self.utils.inj_filter(' '.join(args))}%';", type='all')

                def makeembed(top, least, pages, currentpage):
                    line = ''; count = 1

                    reembed = discord.Embed(colour = discord.Colour(0x011C3A))

                    for formu in formus[top:least]:
                        if count == 6:
                            reembed.add_field(name="---------", value=line)
                            count = 1; line = ''
                        else:
                            line = line + f"╟ `{formu[0]}`|**{formu[1]}**\n"
                            count += 1
                        if count < 6: reembed.add_field(name="---------", value=line)

                    reembed.set_footer(text=f"------ {currentpage}/{pages} ------")
                    return reembed
                    #else:
                    #    await ctx.send("*Nothing but dust here...*")
                
                async def attachreaction(msg):
                    await msg.add_reaction("\U000023ee")    #Top-left
                    await msg.add_reaction("\U00002b05")    #Left
                    await msg.add_reaction("\U000027a1")    #Right
                    await msg.add_reaction("\U000023ed")    #Top-right

                pages = len(formus)//9
                if len(formus)%9 != 0: pages += 1
                currentpage = 1
                cursor = 0

                emli = []
                # pylint: disable=unused-variable
                for curp in range(pages):
                    myembed = makeembed(currentpage*9-9, currentpage*9, pages, currentpage)
                    emli.append(myembed)
                    currentpage += 1
                # pylint: enable=unused-variable
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

            # Formulas' name
            else:
                formus = await self.client.quefe(f"SELECT formula_code, name FROM model_formula WHERE name LIKE '%{await self.utils.inj_filter(' '.join(args))}%';", type='all')
                print(formus)

                def makeembed(top, least, pages, currentpage):
                    line = ''; count = 1

                    reembed = discord.Embed(colour = discord.Colour(0x011C3A))

                    for formu in formus[top:least]:
                        if count == 6:
                            reembed.add_field(name="---------", value=line)
                            count = 1; line = ''
                        else:
                            line = line + f"╟ `{formu[0]}`|**{formu[1]}**\n"
                            count += 1
                        if count < 6: reembed.add_field(name="---------", value=line)

                    reembed.set_footer(text=f"------ {currentpage}/{pages} ------")
                    return reembed
                    #else:
                    #    await ctx.send("*Nothing but dust here...*")
                
                async def attachreaction(msg):
                    await msg.add_reaction("\U000023ee")    #Top-left
                    await msg.add_reaction("\U00002b05")    #Left
                    await msg.add_reaction("\U000027a1")    #Right
                    await msg.add_reaction("\U000023ed")    #Top-right

                pages = len(formus)//9
                if len(formus)%9 != 0: pages += 1
                currentpage = 1
                cursor = 0

                emli = []
                # pylint: disable=unused-variable
                for curp in range(pages):
                    myembed = makeembed(currentpage*6-6, currentpage*9, pages, currentpage)
                    emli.append(myembed)
                    currentpage += 1
                # pylint: enable=unused-variable
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


        except IndexError:

            formus = await self.client.quefe(f"SELECT formula_code, name FROM model_formula;", type='all')

            def makeembed(top, least, pages, currentpage):
                line = ''; count = 1

                reembed = discord.Embed(colour = discord.Colour(0x011C3A))
                for formu in formus[top:least]:
                    if count == 6:
                        reembed.add_field(name="---------", value=line)
                        count = 1; line = ''
                    else:
                        line = line + f"╟ `{formu[0]}`|**{formu[1]}**\n"
                        count += 1
                    if count < 6 and line: reembed.add_field(name="---------", value=line)

                reembed.set_footer(text=f"------ {currentpage}/{pages} ------")
                return reembed
                #else:
                #    await ctx.send("*Nothing but dust here...*")
            
            async def attachreaction(msg):
                await msg.add_reaction("\U000023ee")    #Top-left
                await msg.add_reaction("\U00002b05")    #Left
                await msg.add_reaction("\U000027a1")    #Right
                await msg.add_reaction("\U000023ed")    #Top-right

            pages = len(formus)//9
            if len(formus)%9 != 0: pages += 1
            currentpage = 1
            cursor = 0

            emli = []
            for curp in range(pages):
                myembed = makeembed(currentpage*9-9, currentpage*9, pages, currentpage)
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





def setup(client):
    client.add_cog(avaWorkshop(client))
    