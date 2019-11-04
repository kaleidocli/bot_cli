import random
import asyncio
from functools import partial

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors

from .avaTools import avaTools
from .avaUtils import avaUtils



class avaCommercial(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.__cd_check = self.client.thp.cd_check
        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)
        self.aui = aui = {'FLAME': 'https://imgur.com/3UnIPir.png', 'ICE': 'https://imgur.com/7HsDWfj.png', 'HOLY': 'https://imgur.com/lA1qfnf.png', 'DARK': 'https://imgur.com/yEksklA.png'}

        print("|| Commercial --- READY!")



# ================== EVENTS ==================

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     print("|| Commercial --- READY!")



# ================== COMMERCIAL ==================

    # SYS
    @commands.command(aliases=['s'])
    @commands.cooldown(1, 5, type=BucketType.user)    
    async def shop(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        cur_PLACE, cur_X, cur_Y = await self.client.quefe(f"SELECT cur_PLACE, cur_X, cur_Y FROM personal_info WHERE id='{str(ctx.message.author.id)}';")
        if not await self.tools.area_scan(ctx, cur_X, cur_Y): await ctx.send("<:osit:544356212846886924> Shops are only available within **Peace Belt**!"); return

        # INSPECT ===============
        raw = list(args)
        try:
            # Get goods
            ## Regions
            try: goods, environ_name, seller = await self.client.quefe(f"SELECT goods, name, seller FROM environ WHERE environ_code='{cur_PLACE}';")
            ## Lands
            except TypeError:
                goods, environ_name, seller = await self.client.quefe(f"SELECT goods, name, seller FROM pi_land WHERE land_code='{cur_PLACE}';")
                if not goods: await ctx.send("There's not been goods through here, it seems..."); return
            goods = goods.replace(' - ', "', '")
            # Get info
            try:
                item_code, name, description, tags, weight, defend, multiplier, strr, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, aura, illulink, price = await self.client.quefe(f"""SELECT item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, aura, illulink, price FROM model_item WHERE '{raw[0]}' IN ('{goods}') AND  item_code='{raw[0]}';""")

                # Pointer
                if 'magic' in tags: pointer = ':crystal_ball:'
                else: pointer = '<:gun_pistol:508213644375621632>'

                line = f""":scroll: **`『Weight』` ·** {weight} ⠀ ⠀:scroll: **`『Price』` ·** {price}\n\n```"{description}"```\n"""
                
                reembed = discord.Embed(title=f"`{item_code}`| **{' '.join([x for x in name.upper()])}**", colour = discord.Colour(0x011C3A), description=line)
                reembed.add_field(name=":scroll: Basic Status <:broadsword:508214667416698882>", value=f"**`『STR』` ·** {strr}\n**`『INT』` ·** {intt}\n**`『STA』` ·** {sta}\n**`『MULTIPLIER』` ·** {multiplier}\n**`『DEFEND』` ·** {defend}\n**`『SPEED』` ·** {speed}", inline=True)

                try: acc_per = 10//accuracy_randomness
                except ZeroDivisionError: acc_per = 0
                reembed.add_field(name=f":scroll: Projector Status {pointer}", value=f"**`『RANGE』` ·** {range_min} - {range_max}m\n**`『STEALTH』` ·** {stealth}\n**`『FIRING-RATE』` ·** {firing_rate}\n**`『ACCURACY』` ·** {acc_per}/{accuracy_range}m\n**-------------------**\n**`『ROUND』` ·** {round} \n**`『DMG』` ·** {dmg}", inline=True)

                reembed.set_thumbnail(url=self.aui[aura])
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
            items = await self.client.quefe(f"""SELECT item_code, name, description, tags, weight, quantity, price, aura FROM model_item WHERE item_code IN ('{goods}') {lk_query};""", type='all')

            if not items: await ctx.send(f":spider_web::spider_web: Empty result... :spider_web::spider_web:"); return

            def makeembed(items, top, least, pages, currentpage):

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
                    elif 'blueprint' in item[3]:
                        icon = '<:blueprint512:557713942508470272>'
                    line = line + f""" `{item[0]}` {icon} [`{item[7]}`| **{item[1]}**]\n> *"{item[2]}"*\n╟** `『Weight』{item[4]}`** · **`『Price』`<:36pxGold:548661444133126185>`{item[6]:,}/{item[5]}`**\n**╟╼**`{item[3].replace(' - ', '`·`')}`\n\n"""

                line = line + f"**╚═════════╡**`{currentpage}/{pages}`**╞══════════**"

                reembed = discord.Embed(title = f"<:shl_1:636090807316905994><:shl_2:636090807266574356> `{cur_PLACE}`| **{seller}** <:shl_7:636090806901538817><:shl_8:636090807140745216>", colour = discord.Colour(0x011C3A), description=line)
                
                if line == "**╔═══════╡**`Total: 0`**╞═══════**\n**╚═════════╡**`0/0`**╞══════════**": return False
                else: return reembed
                #else:
                #    await ctx.send("*Nothing but dust here...*")

            await self.tools.pagiMain(ctx, items, makeembed, timeout=45, item_per_page=4)

        await browse()

    @commands.command()
    @commands.cooldown(2, 900, type=BucketType.user)
    async def trader(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        cmd_tag = 'trade'

        cur_PLACE, cur_X, cur_Y, money = await self.client.quefe(f"SELECT cur_PLACE, cur_X, cur_Y, money FROM personal_info WHERE id='{str(ctx.message.author.id)}';")

        if not await self.tools.area_scan(ctx, cur_X, cur_Y): await ctx.send("<:osit:544356212846886924> Traders aren't availablie outside of **Peace Belt**!"); return
        raw = list(args); quantity = 1

        # COOLDOWN
        if not await self.__cd_check(ctx.message, cmd_tag, f"The storm is coming so they ran away."): return

        # Get cuisine
        try: cuisine, r_name = await self.client.quefe(f"SELECT cuisine, name FROM environ WHERE environ_code='{cur_PLACE}';")
        except TypeError:
            cuisine, r_name = await self.client.quefe(f"SELECT cuisine, name FROM pi_land WHERE land_code='{cur_PLACE}';")
            if not cuisine: await ctx.send("Traders are not through here, it seems..."); return

        # Get menu
        menu = []
        # pylint: disable=unused-variable
        for count in range(5):
            menu.append(random.choice(cuisine.split(' - ')))
        # pylint: enable=unused-variable
        # Get items
        items = {}
        for item in set(menu):
            items[item] = await self.client.quefe(f"SELECT name, description, price, tags FROM model_ingredient WHERE ingredient_code='{item}';")

        # MENU
        line = "\n"
        for ig_code in menu:
            line = line + f""" `{ig_code}` <:green_ruby:520092621381697540> **{items[ig_code][0]}**\n| **`Market price`** <:36pxGold:548661444133126185>{items[ig_code][2]}\n++ `{items[ig_code][3].replace(' - ', '` `')}`\n\n"""
            
        reembed = discord.Embed(title = f"------------- KINUKIZA's MARKET of `{cur_PLACE}`| **{r_name}** -----------", colour = discord.Colour(0x011C3A), description=line)
        temp1 = await ctx.send(embed=reembed)
        await ctx.send('<a:RingingBell:559282950190006282> Syntax: `!buy` `[item_code]` `[quantity]` |  Time out: 60s')

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
            if quantity <= 0: await ctx.send("Don't be dumb <:fufu:605255050289348620>"); return                
        # E: Quantity not given, or invalidly given
        except (IndexError, TypeError): pass

        # ig_code check    
        if ig_code not in menu: await ctx.send("<:osit:544356212846886924> The trader does not have this item at the moment. Sorry."); return

        # Reconfirm
        price = int(items[ig_code][2]*random.choice([0.1, 0.2, 0.5, 1, 2, 5, 0.75, 10]))
        deposit = (price*quantity)//5
        msgdeal = await ctx.send(f"<a:RingingBell:559282950190006282> {ctx.message.author.mention}, please react upon accepting the following deal:\n>>> **<:36pxGold:548661444133126185>{price}** per item [`{ig_code}`| **{items[ig_code][0]}**], meaning **<:36pxGold:548661444133126185>{price*quantity}** in total.\nDeposit would be <:36pxGold:548661444133126185>**{deposit}**")
        await msgdeal.add_reaction('\U0001f44c')
        try: await self.client.wait_for('reaction_add', check=lambda r, u: str(r.emoji) == '\U0001f44c' and u == ctx.author, timeout=10)
        except asyncio.TimeoutError:
            await self.client._cursor.execute(f"UPDATE personal_info SET money=money-IF(money >= {deposit}, {deposit}, money) WHERE id='{ctx.author.id}';")
            await ctx.send(f"<:osit:544356212846886924> The request is declined, and you lost a deposit of <:36pxGold:548661444133126185>**{deposit}**."); return
        
        try:
            # Money check
            if price*quantity <= money:
                # UN-SERIALIZABLE
                # Increase item_code's quantity
                await self.client._cursor.execute(f"SELECT func_ig_reward('{ctx.author.id}', '{ig_code}', {quantity});")
                #if await self.client._cursor.execute(f"UPDATE pi_inventory SET quantity=quantity+{quantity} WHERE user_id='{str(ctx.message.author.id)}' AND item_code='{ig_code}';") == 0:
                    # E: item_code did not exist. Create one, with given quantity
                #    await self.client._cursor.execute(f"INSERT INTO pi_inventory SELECT 0, {str(ctx.message.author.id)}, ingredient_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, infuse_query, order_query, passive_query, ultima_query, {quantity}, price, dmg, stealth, evo, aura, craft_value, illulink FROM model_ingredient WHERE ingredient_code='{ig_code}';")

                # Deduct money
                await self.client._cursor.execute(f"UPDATE personal_info SET money=money-{price*quantity} WHERE id='{str(ctx.message.author.id)}';")

            else: await ctx.send("<:osit:544356212846886924> Insufficience balance!"); return
        # E: Item_code not found
        except KeyError: await ctx.send("<:osit:544356212846886924> Item's code not found!"); return


        # Greeting, of course :)
        await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.set, f'{cmd_tag}{ctx.author.id}', 'trading', ex=2700, nx=True))
        await ctx.send(f":white_check_mark: Received **{quantity}** item [`{ig_code}`| **{items[ig_code][0]}**]. Nice trade!")

    @commands.command(aliases=['b'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def bank(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        target = ctx.author
        key = ''
        value = []

        # GET thing
        for a in args:
            if a.startswith('<@'):
                try:
                    target = ctx.message.mentions[0]
                except IndexError: continue
            elif not a.isdigit() and not key:
                key = a
            else:
                value.append(a)
        args = value

        # TARGET ==============================
        # Partner
        if target != ctx.author and key != 'transfer':

            # Info get / Partner check
            try: money, cur_X, cur_Y, age, t_age, stats = await self.client.quefe(f"SELECT money, cur_X, cur_Y, age, (SELECT age FROM personal_info WHERE id='{target.id}'), stats FROM personal_info WHERE id='{ctx.author.id}' AND partner='{target.id}';")
            except TypeError: await ctx.send(f"<:osit:544356212846886924> You're not **{target.name}**'s partner!"); return

            # Coord check
            if not await self.tools.area_scan(ctx, cur_X, cur_Y): await ctx.send("<:osit:544356212846886924> Banks are only available within **Peace Belt**!"); return

            # Account getting
            try: invs, invs_interst, invest_age, tier = await self.client.quefe(f"SELECT investment, interest, invest_age, tier FROM pi_bank WHERE user_id='{target.id}';")
            # E: User does not have account
            except TypeError: await ctx.send(f"<:osit:544356212846886924> Your partner does not have a bank account!"); return
        # Player
        else:
            target = ctx.author

            # Status check
            try:
                money, cur_X, cur_Y, age, stats = await self.client.quefe(f"SELECT money, cur_X, cur_Y, age, stats FROM personal_info WHERE id='{ctx.author.id}' AND stats NOT IN ('ORANGE', 'RED');")
                t_age = age
            except TypeError: await ctx.send(f"<:osit:544356212846886924> You need a **GREEN** or **YELLOW** status to perform this command, **{ctx.author.name}**."); return

            # Coord check
            if not await self.tools.area_scan(ctx, cur_X, cur_Y): await ctx.send("<:osit:544356212846886924> Banks are only available within **Peace Belt**!"); return

            # Account getting
            try: invs, invs_interst, invest_age, tier = await self.client.quefe(f"SELECT investment, interest, invest_age, tier FROM pi_bank WHERE user_id='{target.id}';")
            # E: User does not have account
            except TypeError:

                await ctx.send(f":bank: Greeting, {ctx.author.mention}. It seems that there's no account has your id on it. Perhaps, would you like to open one?\n<a:RingingBell:559282950190006282> *Proceed?* (Key: `account confirm` | Timeout=10s)")
                try: await self.client.wait_for('message', timeout=10, check=lambda m: m.channel == ctx.channel and m.content == 'account confirm' and m.author == ctx.author)
                except asyncio.TimeoutError: await ctx.send(f":bank: Indeed. Why would mongrels need a bank account..."); return
                
                # Create account
                await self.client._cursor.execute(f"INSERT INTO pi_bank VALUES ('{ctx.author.id}', 0, 0, 0.01, '1');")
                await ctx.send(f":white_check_mark: Your account has been successfully created!"); return


        if key:
            # INVEST
            if key == 'invest':
                try:
                    quantity = int(args[0])
                    if quantity >= money: quantity = money
                    elif quantity < 0: await ctx.send("Don't be stupid <:fufu:605255050289348620>"); return

                    # Update prev investment, then the investment, then the invest_age
                    await self.client._cursor.execute(f"UPDATE pi_bank SET investment=(investment+investment*{invs_interst}*{t_age - invest_age})+{quantity}, invest_age={t_age} WHERE user_id='{target.id}';")
                    await self.client._cursor.execute(f"UPDATE personal_info SET money=money-{quantity}, stats=IF(money>=0, 'GREEN', 'YELLOW') WHERE id='{target.id}';")

                    await ctx.send(f":white_check_mark: Added **<:36pxGold:548661444133126185>{quantity:,}** to {target.name}'s account!"); return

                # E: Quantity not given
                except (IndexError, ValueError): await ctx.send("<:osit:544356212846886924> Please provide the amount you want to invest."); return

            # WITHDRAW
            elif key == 'withdraw':
                try:
                    if stats == 'YELLOW': await ctx.send("<:osit:544356212846886924> You need a **GREEN** status to withdraw money."); return

                    quantity = int(args[0])
                    if quantity >= invs: quantity = invs
                    elif quantity < 0: await ctx.send("Don't be stupid <:fufu:605255050289348620>"); return

                    # Update prev investment, then the investment, then the invest_age
                    await self.client._cursor.execute(f"UPDATE pi_bank SET investment=(investment+investment*{invs_interst}*{t_age - invest_age})-{quantity}, invest_age={t_age} WHERE user_id='{target.id}'; UPDATE personal_info SET money=money+{quantity} WHERE id='{ctx.author.id}';")

                    await ctx.send(f":white_check_mark: **<:36pxGold:548661444133126185>{quantity:,}** has just been withdrawn from {target.name}'s account!"); return
                # E: Quantity not given
                except (IndexError, ValueError): await ctx.send("<:osit:544356212846886924> Please provide the amount you want to withdraw."); return

            # TRANSFER
            elif key == 'transfer':
                try:
                    if stats == 'YELLOW': await ctx.send("<:osit:544356212846886924> You need a **GREEN** status to transfer money."); return
                    
                    # Get quantity
                    for i in args[1:]:
                        try: quantity = int(i)
                        except ValueError: continue
                        if quantity >= invs: quantity = invs
                        elif quantity < 0: await ctx.send("Don't be stupid <:fufu:605255050289348620>"); return

                    # Get target
                    target = ctx.message.mentions[0]
                    if not target: await ctx.send("<:osit:544356212846886924> Please provide a receiver"); return

                    # Tax and shiet
                    tax = 40 - int(tier)*5
                    try: q_atx = int(quantity/100*(100-tax))
                    except NameError: await ctx.send("<:osit:544356212846886924> Please provide the amount of money"); return

                    line = f"""```clean
        BEFORE Tax:⠀⠀⠀⠀⠀⠀⠀$ {quantity:,}
        TAX:⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀x⠀  {tax} %
        -----------------------------
        AFTER Tax:⠀⠀⠀⠀⠀⠀⠀⠀$ {q_atx:,}```"""

                    def UMCc_check2(m):
                        return m.channel == ctx.channel and m.content == 'transfer confirm' and m.author == ctx.author

                    await ctx.send(f":credit_card: | **{ctx.author.name}**⠀⠀>>>⠀⠀**{target.name}**\n{line}<a:RingingBell:559282950190006282> Proceed? (Key: `transfer confirm` | Timeout=15s)")
                    try: await self.client.wait_for('message', timeout=15, check=UMCc_check2)
                    except asyncio.TimeoutError: await ctx.send(f":credit_card: Aborted!"); return

                    # Transfer
                    if await self.client._cursor.execute(f"UPDATE pi_bank SET investment=investment+{q_atx} WHERE id='{target.id}';") == 0:
                        await ctx.send(f"<:osit:544356212846886924> User does not have a bank account!"); return
                    # Update prev investment, then the investment, then the invest_age
                    await self.client._cursor.execute(f"UPDATE pi_bank SET investment=(investment+investment*{invs_interst}*{age - invest_age})-{quantity}, invest_age={age} WHERE user_id='{ctx.author.id}';")

                    await ctx.send(f":credit_card: **<:36pxGold:548661444133126185>{q_atx:,}** has been successfully added to **{target.name}**'s bank account."); return

                # E: Quantity not given
                except (IndexError, ValueError): await ctx.send("<:osit:544356212846886924> Please provide the amount you want to withdraw."); return

            # UPGRADE
            elif key == 'upgrade':
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
                    if await self.client._cursor.execute(f"UPDATE pi_bank SET tier='{next_tier}', interest={tier_dict[next_tier][1]} WHERE user_id='{ctx.author.id}' AND EXISTS (SELECT * FROM pi_degrees WHERE user_id='{ctx.author.id}' AND degree='{tier_dict[next_tier][0][0]}' AND major='{tier_dict[next_tier][0][1]}');") == 0:
                        await ctx.send(f":bank: Sorry. Your request to upgrade to tier `{next_tier}` does not meet the criteria."); return
                except KeyError: await ctx.send(f":bank: Your current tier is `{tier}`, which is the highest."); return

                await ctx.send(f":white_check_mark: Upgraded to tier `{next_tier}`!"); return

            # DOWNGRADE
            elif key == 'downgrade':
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
                    await self.client._cursor.execute(f"UPDATE pi_bank SET tier='{next_tier}', interest={tier_dict[next_tier][1]} WHERE user_id='{ctx.author.id}';")
                except KeyError: await ctx.send(f":bank: Your current tier is `{tier}`, which is the lowest to be able to downgrade."); return

                await ctx.send(f":white_check_mark: Downgraded to tier `{next_tier}`!"); return

        else:

            line = f""":bank: `『TIER』` **· `{tier}`** ⠀⠀ ⠀:bank: `『INTEREST』` **· `{invs_interst}`** \n```http
$ {invs:,}```"""

            reembed = discord.Embed(title = f"{target.name.upper()}", colour = discord.Colour(0x011C3A), description=line)
            reembed.set_thumbnail(url=target.avatar_url)

            await ctx.send(embed=reembed)


    # SELF
    @commands.command(aliases=['i', 'inv'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def inventory(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        # INSPECT ================
        raw = list(args)
        try:
            # Get info
            try:
                item_code, name, description, tags, weight, defend, multiplier, strr, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, evo, aura, illulink, price = await self.client.quefe(f"""SELECT item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, evo, aura, illulink, price FROM pi_inventory WHERE existence='GOOD' AND item_id='{int(raw[0])}' AND user_id='{ctx.author.id}';""")
                if evo != 0: evo_plus = f"+{evo}"
                else: evo_plus = ''

                # Pointer
                if 'magic' in tags: pointer = ':crystal_ball:'
                else: pointer = '<:gun_pistol:508213644375621632>'

                line = f""":scroll: **`『Weight』` ·** {weight} ⠀ ⠀:scroll: **`『Price』` ·** {price}\n```"{description}"```\n"""
                
                reembed = discord.Embed(title=f"`{item_code}`|**{' '.join([x for x in name.upper()])}** {evo_plus}", colour = discord.Colour(0x011C3A), description=line)
                reembed.add_field(name=":scroll: Basic Status <:broadsword:508214667416698882>", value=f"**`『STR』` ·** {strr}\n**`『INT』` ·** {intt}\n**`『STA』` ·** {sta}\n**`『MULTIPLIER』` ·** {multiplier}\n**`『DEFEND』` ·** {defend}\n**`『SPEED』` ·** {speed}", inline=True)

                try: acc_per = 10//accuracy_randomness
                except ZeroDivisionError: acc_per = 0
                reembed.add_field(name=f":scroll: Projector Status {pointer}", value=f"**`『RANGE』` ·** {range_min} - {range_max}m\n**`『STEALTH』` ·** {stealth}\n**`『FIRING-RATE』` ·** {firing_rate}\n**`『ACCURACY』` ·** {acc_per}/{accuracy_range}m\n**-------------------**\n**`『ROUND』` ·** {round} \n**`『DMG』` ·** {dmg}", inline=True)

                reembed.set_thumbnail(url=self.aui[aura])
                if illulink != 'n/a': reembed.set_image(url=illulink)

                await ctx.send(embed=reembed, delete_after=30); return
            # Tags given, instead of item_id
            except (TypeError, ValueError): pass
        # E: No args given
        except IndexError: pass

        # PEEK ===================
        try:
            target = ctx.message.mentions[0]
            partner_q = f" AND EXISTS (SELECT * FROM personal_info WHERE id='{ctx.author.id}' AND partner='{target.id}') "
            peeking = True
        except IndexError:
            target = ctx.author
            partner_q = ''
            peeking = False

        # TAKE ===================
        if peeking and ('take' in args):
            # Get info
            item_id = ''
            for kw in args:
                if kw.startswith('<@') or kw == 'take': continue
                else: item_id = kw; break
            if not item_id: await ctx.send("<:osit:544356212846886924> Please provide an item's id!")

            # Get item's info
            if not await self.client._cursor.execute(f"UPDATE pi_inventory SET user_id='{ctx.author.id}' WHERE item_id='{item_id}' AND user_id='{target.id}' AND EXISTS (SELECT id FROM personal_info WHERE id='{ctx.author.id}' AND partner='{target.id}');"):
                await ctx.send("<:osit:544356212846886924> Either the targeted user's not your partner, or the item doesn't exist"); return

        # SEARCH =================
        lk_query = ''; sublk_price = ''; sublk_tag = ''
        for lkkey in raw:
            # Filter
            # Mention
            if lkkey.startswith('<@'): continue

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
            if peeking: items = await self.client.quefe(f"""SELECT item_id, item_code, name, description, tags, weight, quantity, price, aura, '{target.name}', '{target.avatar_url}' FROM pi_inventory WHERE existence='GOOD' AND user_id='{target.id}' {lk_query} {partner_q};""", type='all')
            else: items = await self.client.quefe(f"""SELECT item_id, item_code, name, description, tags, weight, quantity, price, aura, '', '' FROM pi_inventory WHERE existence='GOOD' AND user_id='{target.id}' {lk_query} {partner_q};""", type='all')

            try:
                items = list(items)
                items.sort(key=lambda v: v[1])
            except IndexError: await ctx.send(f":spider_web::spider_web: Empty result... :spider_web::spider_web:"); return

            def makeembed(items, top, least, pages, currentpage):
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
                    elif 'blueprint' in item[4]:
                        icon = '<:blueprint512:557713942508470272>'
                    else: icon = ':tools:'
                    line = line + f""" `{item[0]}` {icon} [`{item[1]}`| **{item[2]}**] [{item[6]}]\n> *"{item[3]}"*\n**╟ `『Weight』{item[5]}`** · **`『Price』`<:36pxGold:548661444133126185>`{item[7]:,}`**\n**╟╼**`{item[4].replace(' - ', '`·`')}`\n\n"""
                            
                line = line + f"**╚═══════╡**`{currentpage}/{pages}`**╞═══════**" 

                reembed = discord.Embed(title = f"<:shl_3:636090807266574346><:shl_1:636090807316905994><:shl_4:636090807237214209> **I N V E N T O R Y** <:shl_5:636090807127900180><:shl_7:636090806901538817><:shl_6:636090807019110401>", colour = discord.Colour(0x011C3A), description=line)
                if items[0][9]: reembed.set_footer(text=f"From {items[0][9]} with love", icon_url=items[0][10])
                return reembed
                #else:
                #    await ctx.send("*Nothing but dust here...*")

            await self.tools.pagiMain(ctx, items, makeembed, item_per_page=4)

        await browse()

    @commands.command(aliases=['u'])
    @commands.cooldown(1, 2, type=BucketType.user)
    async def use(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        raw = list(args)
        slots = {"r": 'right_hand', "l": "left_hand"}

        target_id = str(ctx.author.id); target_name = ctx.author.name
        item_id = ''
        quantity = 1
        handle = 'r'

        # INFO get =========================================================

        for a in args:
            # Number
            if a.isdigit():
                # Item_ID
                if not item_id: item_id = a

                # QUANTITY
                else:
                    quantity = int(a)
                
            # Char
            else:
                # TARGET/mob
                if a.startswith('mob.') or a.startswith('boss.'):
                    target_id = a; target_name = a

                # TARGET/player
                elif ctx.message.mentions:
                    target_id = str(ctx.message.mentions[0].id)
                    target_name = ctx.message.mentions[0].name

                # Handle
                else: handle = a


        # EXECUTE ===========================================================

        # Slot Self-switching
        if not args:
            # Switch
            mw, sw = await self.client.quefe(f"SELECT right_hand, {slots['l']} FROM personal_info WHERE id='{ctx.author.id}';")
            await self.client._cursor.execute(f"UPDATE personal_info SET right_hand='{sw}', {slots['l']}='{mw}' WHERE id='{ctx.author.id}';")

            # Get line
            sw_name = await self.client.quefe(f"SELECT name FROM pi_inventory WHERE existence='GOOD' AND user_id='{ctx.author.id}' AND item_id='{sw}';")
            if sw_name: line_1 = f"[`{sw}`| **{sw_name[0]}**] ➠ `right_hand`"
            else: line_1 = '`right_hand` is left empty'
            mw_name = await self.client.quefe(f"SELECT name FROM pi_inventory WHERE existence='GOOD' AND user_id='{ctx.author.id}' AND item_id='{mw}';")
            if mw_name: line_2 = f"[`{mw}`| **{mw_name[0]}*]* ➠ `{slots['l']}`"
            else: line_2 = f"`{slots['l']}` is left empty"
            # Inform :)
            await ctx.send(f":twisted_rightwards_arrows: {line_1} \n:twisted_rightwards_arrows: {line_2} "); return

        # Equipment (slot)
        elif handle not in slots:
            item_id = await self.client.quefe(f"SELECT item_id FROM pi_equipment WHERE user_id='{ctx.author.id}' AND slot_name='{handle}' AND slot_type='belt';")

            # Invoke
            try:
                await ctx.invoke(self.client.get_command('use'), *(item_id[0], target_id, str(quantity)))
            except discordErrors.HTTPException: pass
            # E: Slot name not found
            except TypeError: await ctx.send(f"<:osit:544356212846886924> Pocket name not found!")

        # Item ID
        elif item_id:
            ##Get weapon info
            try: w_name, w_tags, w_eq, w_code = await self.client.quefe(f"SELECT name, tags, effect_query, item_code FROM pi_inventory WHERE existence='GOOD' AND user_id='{ctx.author.id}' AND item_id='{raw[0]}';")
            except TypeError: await ctx.send(f"<:osit:544356212846886924> Item not found!"); return

            # Sharable check (share-able)
            if target_id != str(ctx.author.id) and 'sharable' not in w_tags: await ctx.send("<:osit:544356212846886924> This item cannot be used on other entity"); return

            # CONSUMABLE (Supply / Ingredient) ======================
            if 'supply' in w_tags or 'ingredient' in w_tags:
                
                # Effect_query check
                if not w_eq: await ctx.send(":white_check_mark: Tried to use, but no effect received."); return

                # Prepair query
                w_eq = w_eq.replace("user_id_here", target_id)
                af_query = ''
                for time in range(quantity):
                    # Affect
                    af_query = af_query + w_eq

                ## Adjusting things with quantity
                await self.client._cursor.execute(f"SELECT func_i_delete('{ctx.author.id}', '{w_code}', {quantity}); " + af_query)
                await self.tools.ava_scan(ctx.message, type='normalize', target_id=target_id)
                await ctx.send(f":white_check_mark: Used {quantity} [`{item_id}`| **{w_name}**] on **{target_name}**")     

            # INCONSUMABLE ===========================================
            else:

                ##Get slot_name
                try: slot_name = slots[handle]
                except IndexError: slot_name = slots['r']
                except KeyError: await ctx.send(f":grey_question: There are `2` weapon slots available: `r` Main Weapon | `l` Secondary Weapon"); return

                ##Get weapon
                weapon = await self.client.quefe(f"SELECT {slot_name} FROM personal_info WHERE id='{str(ctx.message.author.id)}';"); weapon = weapon[0]

                ##Equip
                if item_id != weapon:
                    await self.client._cursor.execute(f"UPDATE personal_info SET {slot_name}='{item_id}' WHERE id='{str(ctx.message.author.id)}';")
                    # Inform, of course :)
                    await ctx.send(f":fist: Equipped [`{item_id}`| **{w_name}**] to `{slot_name}` slot!"); return
                ###Already equip    -----> Unequip
                else:
                    await self.client._cursor.execute(f"UPDATE personal_info SET {slot_name}=(SELECT item_id FROM pi_inventory WHERE user_id='{ctx.author.id}' AND item_code='ar13') WHERE id='{ctx.author.id}'")
                    await ctx.send(f":raised_hand: Unequipped item [`{w_code}`| **{w_name}**] from `{slot_name}` slot!")
                    return


    # P2P
    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)    
    async def buy(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        cur_X, cur_Y, money, cur_PLACE = await self.client.quefe(f"SELECT cur_X, cur_Y, money, cur_PLACE FROM personal_info WHERE id='{str(ctx.message.author.id)}';")

        if not await self.tools.area_scan(ctx, cur_X, cur_Y): await ctx.send("<:osit:544356212846886924> You can only buy stuff within **Peace Belt**!"); return
        #await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.set, f'{cmd_tag}{str(ctx.message.author.id)}', 'working', ex=duration, nx=True))

        raw = list(args); quantity = 1

        try: item_code = raw[0]
        except IndexError: await ctx.send(f"<:osit:544356212846886924> Please provide item's code, **{ctx.message.author.name}**"); return

        try: 
            quantity = int(raw[1])

            # SCAM :)
            if quantity <= 0: await ctx.send("**Heyyyyyyyyy scammer-!**"); return

        # E: Quantity not given, or invalidly given
        except (IndexError, TypeError, ValueError): pass
        
        # Get goods
        if cur_PLACE.startswith('land.'): goods = await self.client.quefe(f"SELECT goods FROM pi_land WHERE land_code='{cur_PLACE}';")
        else: goods = await self.client.quefe(f"SELECT goods FROM environ WHERE environ_code='{cur_PLACE}';")

        if not goods: await ctx.send("<:osit:544356212846886924> Nothing to buy here..."); return

        # GET ITEM INFO
        try:
            name, tags, i_price, i_quantity = await self.client.quefe(f"""SELECT name, tags, price, quantity FROM model_item WHERE item_code='{item_code}' AND item_code IN ('{goods[0].replace(' - ', "', '")}');""")
            i_tags = tags.split(' - ')
        # E: Item code not found
        except TypeError: await ctx.send("<:osit:544356212846886924> Item_code/Item_id not found!"); return

        # TWO TYPES of obj: Serializable-obj and Unserializable obj
        # Validation
        #if isinstance(self.data['item'][item_code], ingredient): await ctx.send(f"<:osit:544356212846886924> You cannot use this command to obtain the given item, {str(ctx.message.author.id)}. Use `-trade` instead"); return

        # Money check
        if i_price*quantity > money: await ctx.send("<:osit:544356212846886924> Insufficience balance!"); return

        # Deduct money
        await self.client._cursor.execute(f"UPDATE personal_info SET money=money-{i_price*quantity} WHERE id='{str(ctx.message.author.id)}';")

        # Get the real quantity (according to the model_item's quantity)
        quantity = quantity*i_quantity

        # Greeting, of course :)
        await ctx.send(f":white_check_mark: `{quantity}` item **{name}** is successfully added to your inventory! Thank you for shoping!")

        # INCONSUMABLE
        # pylint: disable=unused-variable
        if 'inconsumable' in i_tags:
            # Create item in inventory. Ignore the given quantity please :>
            #await self.client._cursor.execute(f"INSERT INTO pi_inventory SELECT 0, '{str(ctx.message.author.id)}', item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, infuse_query, order_query, passive_query, ultima_query, quantity, price, dmg, stealth, evo, aura, craft_value, illulink FROM model_item WHERE item_code='{item_code}';")
            for i in range(quantity):
                await self.client._cursor.execute(f"SELECT func_it_reward('{ctx.author.id}', '{item_code}', 1);")
            # (MODEL FOR QUERY RECORD-TRANSFERING) ------- await self.client._cursor.execute(f"INSERT INTO pi_inventory SELECT 0, {str(ctx.message.author.id)}, item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, quantity, price, dmg, stealth FROM model_item WHERE item_code='{item_code}';")
        # pylint: enable=unused-variable
        # CONSUMABLE
        else:
            await self.client._cursor.execute(f"SELECT func_it_reward('{ctx.author.id}', '{item_code}', {quantity});")
            # Increase item_code's quantity
            #if await self.client._cursor.execute(f"UPDATE pi_inventory SET quantity=quantity+{quantity} WHERE user_id='{str(ctx.message.author.id)}' AND item_code='{item_code}';") == 0:
            #    # E: item_code did not exist. Create one, with given quantity
            #    await self.client._cursor.execute(f"INSERT INTO pi_inventory SELECT 0, '{str(ctx.message.author.id)}', item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, infuse_query, order_query, passive_query, ultima_query, {quantity}, price, dmg, stealth, evo, aura, craft_value, illulink FROM model_item WHERE item_code='{item_code}';")

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
            try: w_tags, w_name, w_quantity, w_code = await self.client.quefe(f"SELECT tags, name, quantity, item_code FROM pi_inventory WHERE existence='GOOD' AND user_id='{ctx.author.id}' AND item_id='{item_id}' AND quantity>={quantity};")
            except TypeError: await ctx.send("<:osit:544356212846886924> You don't have enough of this item."); return

            # Tradable check
            if 'untradable' in w_tags: await ctx.send(f"<:osit:544356212846886924> You cannot trade this item, **{ctx.message.author.name}**. It's *untradable*, look at its tags."); return

            msg = await ctx.send(f"**{ctx.author.name}** wants to sell you **{quantity}** [`{w_code}`| **{w_name}**] for <:36pxGold:548661444133126185>{price:,}. Accept, {receiver.mention}?")
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
            await ctx.send(f":white_check_mark: You've been given `{quantity}` [`{w_code}`| **{w_name}**], {receiver.mention}!"); return

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

        try: w_name, w_price, w_quantity, w_tags = await self.client.quefe(f"SELECT name, price, quantity, tags FROM pi_inventory WHERE existence='GOOD' AND user_id='{ctx.author.id}' AND item_id='{item_id}' AND quantity>={quantity};")
        # E: Item_id not found
        except TypeError: await ctx.send("<:osit:544356212846886924> You don't have enough of this item."); return
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

        await ctx.send(f":white_check_mark: You received **<:36pxGold:548661444133126185>{receive:,}** from selling {quantity} [`{item_id}`| **{w_name}**], **{ctx.message.author.name}**!")

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





def setup(client):
    client.add_cog(avaCommercial(client))
