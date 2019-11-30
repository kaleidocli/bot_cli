import random
import asyncio
from functools import partial

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors

from utils import checks



class avaWorkshop(commands.Cog):

    def __init__(self, client):
        from .avaTools import avaTools
        from .avaUtils import avaUtils


        self.client = client
        self.__cd_check = self.client.thp.cd_check
        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)

        self.client.DBC['model_formula'] = {}
        self.cacheMethod = {
            'model_formula': self.cacheFormula
        }        



# ================== EVENTS ==================

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(8)
        await self.reloadSetup()
        print("|| Workshop --- READY!")

    async def reloadSetup(self):
        await self.cacheAll()



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
                w_name, w_evo, w_weight, w_defend, w_multiplier, w_str, w_intt, w_sta, w_speed, w_acc_randomness, w_acc_range, w_r_min, w_r_max, w_firing_rate, w_dmg, w_stealth, w_price = await self.client.quefe(f"SELECT name, evo, weight, defend, multiplier, str, intt, sta, speed, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, price FROM pi_inventory WHERE existence='GOOD' AND user_id='{ctx.author.id}' AND item_id='{raw[0]}';")
                t_w_name, t_w_evo, t_w_weight, t_w_defend, t_w_multiplier, t_w_str, t_w_intt, t_w_sta, t_w_speed, t_w_acc_randomness, t_w_acc_range, t_w_r_min, t_w_r_max, t_w_firing_rate, t_w_dmg, t_w_stealth, t_w_price = await self.client.quefe(f"SELECT name, evo, weight, defend, multiplier, str, intt, sta, speed, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, price FROM pi_inventory WHERE existence='GOOD' AND user_id='{ctx.author.id}' AND item_id='{raw[1]}';")
            # E: Item's not found
            except TypeError: await ctx.send("<:osit:544356212846886924> Item's not found!"); return
            # E: Not enough args
            except IndexError: await ctx.send("<:osit:544356212846886924> You need two items in order to merge!"); return

            # Degrees
            degrees = await self.client.quefe(f"SELECT degree FROM pi_degrees WHERE user_id='{str(ctx.message.author.id)}' AND major='engineering';")
            try: degrees = set(degrees)
            # E: No engineering degree
            except TypeError: degrees = ()

            # Price
            price = ((w_evo + t_w_evo)//2*1000)//(1 + len(degrees))
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
            try: W_multiplier = round(random.uniform(0, (w_multiplier + t_w_multiplier)/10*9), 1)
            except IndexError: W_multiplier = 0
            try: W_str = round(random.uniform(0, (w_str + t_w_str)/10*9), 1)
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

            W_evo = (w_evo + t_w_evo)//2

            # Insert
            await self.client._cursor.execute(f"UPDATE pi_inventory SET weight={W_weight}, multiplier={W_multiplier}, str={W_str}, intt={W_intt}, sta={W_sta}, speed={W_speed}, accuracy_randomness={W_acc_randomness}, accuracy_range={W_acc_range}, range_min={W_r_min}, range_max={W_r_max}, dmg={W_dmg}, stealth={W_stealth}, evo={W_evo}, price={w_price} WHERE user_id='{str(ctx.message.author.id)}' AND item_id='{raw[0]}';")
            await self.client._cursor.execute(f"UPDATE pi_inventory SET weight={W_weight}, multiplier={W_multiplier}, str={W_str}, intt={W_intt}, sta={W_sta}, speed={W_speed}, accuracy_randomness={W_acc_randomness}, accuracy_range={W_acc_range}, range_min={W_r_min}, range_max={W_r_max}, dmg={W_dmg}, stealth={W_stealth}, evo={W_evo}, price={t_w_price} WHERE user_id='{str(ctx.message.author.id)}' AND item_id='{raw[1]}';")

            # Inform :>
            await ctx.send(f":white_check_mark: Merged `{raw[0]}`|**{w_name}** with `{raw[1]}`|**{t_w_name}**!")
            await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.set, f'{cmd_tag}{str(ctx.message.author.id)}', 'merging', ex=7200, nx=True))

        # E: Not enough args
        except ZeroDivisionError: await ctx.send("<:osit:544356212846886924> How could you even merge something with its own?!"); return

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def craft(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        try:
            quantity = args[1]
            if quantity > 10: quantity = 10
        except IndexError: quantity = 1

        # Get FORMULA
        try:
            # check_query, effect_query, info_msg = await self.client.quefe(f"SELECT check_query, effect_query, info_msg FROM model_formula WHERE formula_value={total_cv};")
            formula = await self.dbcGetFormula(args[0])
            if not formula: await ctx.send("<:osit:544356212846886924> Unknown formula_code. Use `formula` for a list of formulas."); return
        except IndexError: await ctx.send(":tools: Missing formula_code. Use `formula` for a list of formulas."); return

        # Check ingredient
        missing = []
        for ingre in formula.formula_value:
            await asyncio.sleep(0)
            if not await self.client._cursor.execute(f"SELECT quantity FROM pi_inventory WHERE user_id='{ctx.author.id}' AND item_code='{ingre[0]}' AND quantity>={ingre[1]*quantity};"):
                missing.append(f"· {ingre[1]*quantity} [{ingre[0]}]")
        if missing:
            missing_line = "\n".join(missing)
            await ctx.send(embed=discord.Embed(colour=discord.Colour(0x011C3A)).add_field(name=f":tools: Insufficience in **{len(missing)}** items:", value=f"""```ini
{missing_line}```"""))
            return

        # Custom checks
        if formula.check_query:
            check_query = formula.check_query.replace('user_id_here', f"{ctx.author.id}").replace('quantity_here', f"{quantity}")
            if self.client._cursor.execute(check_query) == 0: await ctx.send(f":tools: Oops! {formula.info_msg[1]} :<"); return

        effect_query = formula.effect_query.replace('user_id_here', f"{ctx.author.id}")

        # Take effect (reward, effect, etc.)
        for _ in range(quantity):
            await asyncio.sleep(0)
            if await self.client._cursor.execute(effect_query) == 0: await ctx.send(f":tools: Oops! {formula.info_msg[1]} :<"); return
        
        # Inform
        await ctx.send(f":tools: {formula.info_msg[0]} **Successfully crafted!**")

    @commands.command(aliases=['fml'])
    @commands.cooldown(1, 7, type=BucketType.user)
    async def formula(self, ctx, *args):
        formus = None

        # FORMULA
        try:
            if args[0] not in ['in', 'out']:
                _mode = 'in'
                args = args[0:6]
            else:
                _mode = args[0]
                args = args[1:7]

            # Formulas' code
            if args[0].startswith('fm'):
                try:
                    # formula_code, name, formula_value, description, tags, kit = await self.client.quefe(f"SELECT formula_code, name, formula_value, description, tags, kit FROM model_formula WHERE formula_code='{args[0]}';")
                    formula = await self.dbcGetFormula(args[0])
                    if not formula: await ctx.send(":tools: Formula not found!"); return
                except KeyError: await ctx.send(":tools: Formula not found!"); return
            
                temb = discord.Embed(title=f":tools: `{formula.formula_code}`|**{formula.name}**", description=f"""```{formula.description}```""", colour=discord.Colour(0x011C3A))
                temb.add_field(name=f'╟ REQUIREMENT (kit:{formula.kit})', value=f"╟ `{'` · `'.join(formula.ingre_tag)}` >>> `{'` · `'.join(formula.produ_tag)}`", inline=True)

                await ctx.send(embed=temb)

            # Formulas' tag
            elif args[0].startswith('ar') or args[0].startswith('it') or args[0].startswith('ig') or args[0].startswith('bp') or args[0].startswith('am'):
                # formus = await self.client.quefe(f"SELECT formula_code, name FROM model_formula WHERE tags LIKE '%{await self.utils.inj_filter(' '.join(args))}%';", type='all')
                if _mode == 'in':
                    formus = []
                    for f in self.client.DBC['model_formula'].values():
                        await asyncio.sleep(0)
                        if set(args).issubset(f.ingre_tag): formus.append(f)
                else:
                    for f in self.client.DBC['model_formula'].values():
                        await asyncio.sleep(0)
                        if set(args).issubset(f.produ_tag): formus.append(f)
                raise IndexError

            # Formulas' name
            else:
                # formus = await self.client.quefe(f"SELECT formula_code, name FROM model_formula WHERE name LIKE '%{await self.utils.inj_filter(' '.join(args))}%';", type='all')
                formus = []
                for f in self.client.DBC['model_formula'].values():
                    await asyncio.sleep(0)
                    if await self.utils.inj_filter(' '.join(args)) in f.name: formus.append(f)
                raise IndexError


        except IndexError:

            if formus == None:
                # formus = await self.client.quefe(f"SELECT formula_code, name FROM model_formula;", type='all')
                formus = tuple(self.client.DBC['model_formula'].values())

            def makeembed(items, top, least, pages, currentpage):
                line = ''; count = 1; field_count = 0

                reembed = discord.Embed(colour = discord.Colour(0x011C3A))
                for formu in items[top:least]:
                    line = line + f"╟ {formu.formula_code}:: {formu.name}\n"
                    if count == 6:
                        if not field_count:
                            line2 = f"『Total』{len(items)}"
                            field_count += 1
                        else:
                            line2 = f"『Page』{currentpage}/{pages}"
                            field_count = 0
                        reembed.add_field(name=line2, value=f"""```Asciidoc
{line}```""")
                        count = 1; line = ''
                        continue
                    else:
                        count += 1
                if line:
                    if not field_count:
                        line2 = f"『Total』{len(items)}"
                    else:
                        line2 = f"『Page』{currentpage}/{pages}"
                    reembed.add_field(name=line2, value=f"""```Asciidoc
{line}```""")
                    if not field_count: reembed.add_field(name=f"『Page』{currentpage}/{pages}", value=f"""```⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀```""")

                return reembed
                #else:
                #    await ctx.send("*Nothing but dust here...*")
            
            await self.tools.pagiMain(ctx, formus, makeembed, item_per_page=12, delete_on_exit=False)



# ================== ADMIN ==================

    @commands.command()
    @checks.check_author()
    async def refreshFormula(self, ctx, *args):
        count = 0

        for formula_code in args:
            try:
                del self.client.DBC['model_formula'][formula_code]
            # except IndexError: await ctx.send(f":x: Missing conv_code"); return
            # except KeyError: await ctx.send(f":x: Unknown conv_code"); return
            except (IndexError, KeyError): continue

            count += 1
            await self.dbcGetFormula(formula_code)

        await ctx.send(f":white_check_mark: Reloaded `{count}` formulas.")



# ================== TOOLS ==================

    async def cacheAll(self):
        for v in self.cacheMethod.values():
            await v()

    async def cacheFormula(self):
        self.client.DBC['model_formula'] = await self.cacheFormula_tool()

    async def cacheFormula_tool(self):
        temp = {}

        res = await self.client.quefe("SELECT formula_code, name, formula_value, description, tags, kit, check_query, effect_query, info_msg FROM model_formula;", type='all')
        for r in res:
            await asyncio.sleep(0)
            temp[r[0]] = c_Formula(r)

        return temp

    async def dbcGetFormula(self, formula_code):
        try:
            return self.client.DBC['model_formula'][formula_code]
        except KeyError:
            res = await self.client.quefe(f"SELECT formula_code, name, formula_value, description, tags, kit, check_query, effect_query, info_msg FROM model_formula WHERE formula_code='{formula_code}';")
            try:
                self.client.DBC['model_formula'][formula_code] = c_Formula(res[0])
                return self.client.DBC['model_formula'][formula_code]
            except TypeError: return False





def setup(client):
    client.add_cog(avaWorkshop(client))








class c_Formula:
    def __init__(self, pack):
        self.formula_code, self.name, formuva, self.description, tags, self.kit, self.check_query, self.effect_query, self.info_msg = pack

        self.formula_value = []
        for v in formuva.split(' | '):
            v = v.split(' - ')
            self.formula_value.append(tuple(v, int(v)))
        self.formula_value = tuple(self.formula_value)

        tags = tags.split(' >>> ')
        try: self.ingre_tag = tags[0].split(' - ')
        except IndexError: self.ingre_tag = []
        try: self.produ_tag = tags[1].split(' - ')
        except IndexError: self.produ_tag = []

        try: self.info_msg = self.info_msg.split(' || ')
        except AttributeError: self.info_msg = ['', '']
        if len(self.info_msg) < 2: self.info_msg.append('')
