import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors

import random
import asyncio
from functools import partial

from .avaTools import avaTools
from .avaUtils import avaUtils

class avaService:
    def __init__(self, client):
        self.client = client
        self.__cd_check = self.client.thp.cd_check
        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)

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
            try: goods, environ_name = await self.client.quefe(f"SELECT goods, name FROM environ WHERE environ_code='{cur_PLACE}';")
            ## Lands
            except TypeError:
                goods, environ_name = await self.client.quefe(f"SELECT goods, name FROM pi_land WHERE land_code='{cur_PLACE}';")
                if not goods: await ctx.send("There's not been goods through here, it seems..."); return
            goods = goods.replace(' - ', "', '")
            # Get info
            try:
                item_code, name, description, tags, weight, defend, multiplier, strr, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, aura, illulink, price = await self.client.quefe(f"""SELECT item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, aura, illulink, price FROM model_item WHERE '{raw[0]}' IN ('{goods}') AND  item_code='{raw[0]}';""")

                # Pointer
                if 'magic' in tags: pointer = ':crystal_ball:'
                else: pointer = '<:gun_pistol:508213644375621632>'
                # Aura icon
                aui = {'FLAME': 'https://imgur.com/3UnIPir.png', 'ICE': 'https://imgur.com/7HsDWfj.png', 'HOLY': 'https://imgur.com/lA1qfnf.png', 'DARK': 'https://imgur.com/yEksklA.png'}

                line = f""":scroll: **`『Weight』` ·** {weight} ⠀ ⠀:scroll: **`『Price』` ·** {price}\n\n```"{description}"```\n"""
                
                reembed = discord.Embed(title=f"`{item_code}`|**{' '.join([x for x in name.upper()])}**", colour = discord.Colour(0x011C3A), description=line)
                reembed.add_field(name=":scroll: Basic Status <:broadsword:508214667416698882>", value=f"**`『STR』` ·** {strr}\n**`『INT』` ·** {intt}\n**`『STA』` ·** {sta}\n**`『MULTIPLIER』` ·** {multiplier}\n**`『DEFEND』` ·** {defend}\n**`『SPEED』` ·** {speed}", inline=True)

                try: acc_per = 10//accuracy_randomness
                except ZeroDivisionError: acc_per = 0
                reembed.add_field(name=f":scroll: Projector Status {pointer}", value=f"**`『RANGE』` ·** {range_min} - {range_max}m\n**`『STEALTH』` ·** {stealth}\n**`『FIRING-RATE』` ·** {firing_rate}\n**`『ACCURACY』` ·** {acc_per}%/{accuracy_range}m\n**-------------------**\n**`『ROUND』` ·** {round} \n**`『DMG』` ·** {dmg}", inline=True)

                reembed.set_thumbnail(url=aui[aura])
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

            if not items: await ctx.send(f":x: No result..."); return

            def makeembed(top, least, pages, currentpage):

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
                    line = line + f""" `{item[0]}` {icon} `{item[7]}`|**{item[1]}**\n╟ *"{item[2]}"*\n╟** `『Weight』{item[4]}`** · **`『Price』`<:36pxGold:548661444133126185>`{item[6]}/{item[5]}`**\n**╟╼**`{item[3].replace(' - ', '`·`')}`\n\n"""

                line = line + f"**╚═════════╡**`{currentpage}/{pages}`**╞══════════**"

                reembed = discord.Embed(title = f":shopping_cart: SIEGFIELD's Market of `{cur_PLACE}|{environ_name}`", colour = discord.Colour(0x011C3A), description=line)
                
                if line == "**╔═══════╡**`Total: 0`**╞═══════**\n**╚═════════╡**`0/0`**╞══════════**": return False
                else: return reembed
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
            # pylint: disable=unused-variable
            for curp in range(pages):
                myembed = makeembed(currentpage*5-5, currentpage*5, pages, currentpage)
                emli.append(myembed)
                currentpage += 1
            # pylint: enable=unused-variable
            msg = await ctx.send(embed=emli[cursor])
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
                    break

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
            
        reembed = discord.Embed(title = f"------------- KINUKIZA's MARKET of `{cur_PLACE}`|**{r_name}** -----------", colour = discord.Colour(0x011C3A), description=line)
        temp1 = await ctx.send(embed=reembed)
        await ctx.send('<a:RingingBell:559282950190006282> Syntax: `!buy` `[item_code]` |  Time out: 60s')

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
        def UMCc_check2(m):
            return m.channel == ctx.channel and m.content == 'trade confirm' and m.author == ctx.author

        price = int(items[ig_code][2]*random.choice([0.1, 0.2, 0.5, 1, 2, 5, 10]))
        await ctx.send(f"{ctx.message.author.mention}, the dealer set the price of **<:36pxGold:548661444133126185>{price}** for __each__ item `{ig_code}`|**{items[ig_code][0]}**. \nThat would cost you **<:36pxGold:548661444133126185>{price*quantity}** in total.\n<a:RingingBell:559282950190006282> Proceed? (Key: `trade confirm` | Timeout=10s)")
        try: await self.client.wait_for('message', check=UMCc_check2, timeout=10)
        except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request declined!"); return
        
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
        await ctx.send(f":white_check_mark: Received **{quantity}** item `{ig_code}`|**{items[ig_code][0]}**. Nice trade!")

    @commands.command(aliases=['b'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def bank(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        # Status check
        try: money, cur_X, cur_Y, age, stats = await self.client.quefe(f"SELECT money, cur_X, cur_Y, age, stats FROM personal_info WHERE id='{str(ctx.message.author.id)}' AND stats NOT IN ('ORANGE', 'RED');")
        except TypeError: await ctx.send(f"<:osit:544356212846886924> You need a **GREEN** or **YELLOW** status to perform this command, **{ctx.message.author.name}**."); return

        # Coord check
        if not await self.tools.area_scan(ctx, cur_X, cur_Y): await ctx.send("<:osit:544356212846886924> Banks are only available within **Peace Belt**!"); return

        # Account getting
        try: invs, invs_interst, invest_age, tier = await self.client.quefe(f"SELECT investment, interest, invest_age, tier FROM pi_bank WHERE user_id='{str(ctx.message.author.id)}';")
        # E: User does not have account
        except TypeError:
            # Get confirmation
            def UMCc_check(m):
                return m.channel == ctx.channel and m.content == 'account confirm' and m.author == ctx.author

            await ctx.send(f":bank: Greeting, {ctx.message.author.mention}. It seems that there's no account has your id on it. Perhaps, would you like to open one?\n<a:RingingBell:559282950190006282> *Proceed?* (Key: `account confirm` | Timeout=10s)")
            try: await self.client.wait_for('message', timeout=10, check=UMCc_check)
            except asyncio.TimeoutError: await ctx.send(f":bank: Indeed. Why would mongrels need a bank account..."); return
            
            # Create account
            await self.client._cursor.execute(f"INSERT INTO pi_bank VALUES ('{str(ctx.message.author.id)}', 0, 0, 0.01, '1');")
            await ctx.send(f":white_check_mark: Your account has been successfully created!"); return

        raw = list(args)

        try:
            # INVEST
            if raw[0] == 'invest':
                try:
                    quantity = int(raw[1])
                    if quantity >= money: quantity = money
                    elif quantity < 0: await ctx.send("Don't be stupid <:fufu:605255050289348620>"); return

                    # Update prev investment, then the investment, then the invest_age
                    await self.client._cursor.execute(f"UPDATE pi_bank SET investment=(investment+investment*{invs_interst}*{age - invest_age})+{quantity}, invest_age={age} WHERE user_id='{str(ctx.message.author.id)}';")
                    await self.client._cursor.execute(f"UPDATE personal_info SET money=money-{quantity}, stats=IF(money>=0, 'GREEN', 'YELLOW') WHERE id='{str(ctx.message.author.id)}';")

                    await ctx.send(f":white_check_mark: Added **<:36pxGold:548661444133126185>{quantity}** to your account!"); return

                # E: Quantity not given
                except (IndexError, ValueError): await ctx.send("<:osit:544356212846886924> Please provide the amount you want to invest."); return

            # WITHDRAW
            elif raw[0] == 'withdraw':
                try:
                    if stats == 'YELLOW': await ctx.send("<:osit:544356212846886924> You need a **GREEN** status to withdraw money."); return

                    quantity = int(raw[1])
                    if quantity >= invs: quantity = invs
                    elif quantity < 0: await ctx.send("Don't be stupid <:fufu:605255050289348620>"); return

                    # Update prev investment, then the investment, then the invest_age
                    await self.client._cursor.execute(f"UPDATE pi_bank SET investment=(investment+investment*{invs_interst}*{age - invest_age})-{quantity}, invest_age={age} WHERE user_id='{str(ctx.message.author.id)}';")
                    await self.client._cursor.execute(f"UPDATE personal_info SET money=money+{quantity} WHERE id='{str(ctx.message.author.id)}';")

                    await ctx.send(f":white_check_mark: **<:36pxGold:548661444133126185>{quantity}** has just been withdrawn from your account!"); return
                # E: Quantity not given
                except (IndexError, ValueError): await ctx.send("<:osit:544356212846886924> Please provide the amount you want to withdraw."); return
            
            # TRANSFER
            elif raw[0] == 'transfer':
                try:
                    if stats == 'YELLOW': await ctx.send("<:osit:544356212846886924> You need a **GREEN** status to transfer money."); return
                    
                    # Get quantity
                    for i in raw[1:]:
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
        BEFORE Tax:⠀⠀⠀⠀⠀⠀⠀$ {quantity}
        TAX:⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀x⠀  {tax} %
        -----------------------------
        AFTER Tax:⠀⠀⠀⠀⠀⠀⠀⠀$ {q_atx}```"""

                    def UMCc_check2(m):
                        return m.channel == ctx.channel and m.content == 'transfer confirm' and m.author == ctx.author

                    await ctx.send(f":credit_card: | **{ctx.message.author.name}**⠀⠀>>>⠀⠀**{target.name}**\n{line}<a:RingingBell:559282950190006282> Proceed? (Key: `transfer confirm` | Timeout=15s)")
                    try: await self.client.wait_for('message', timeout=15, chec=UMCc_check2)
                    except asyncio.TimeoutError: await ctx.send(f":credit_card: Aborted!"); return

                    # Transfer
                    if await self.client._cursor.execute(f"UPDATE pi_bank SET investment=investment+{q_atx} WHERE id='{target.id}';") == 0:
                        await ctx.send(f"<:osit:544356212846886924> User does not have a bank account!"); return
                    # Update prev investment, then the investment, then the invest_age
                    await self.client._cursor.execute(f"UPDATE pi_bank SET investment=(investment+investment*{invs_interst}*{age - invest_age})-{quantity}, invest_age={age} WHERE user_id='{str(ctx.message.author.id)}';")

                    await ctx.send(f":credit_card: **<:36pxGold:548661444133126185>{q_atx}** has been successfully added to **{target.name}**'s bank account."); return

                # E: Quantity not given
                except (IndexError, ValueError): await ctx.send("<:osit:544356212846886924> Please provide the amount you want to withdraw."); return

            # LOAN
            elif raw[0] == 'loan':
                try:
                    if stats == 'YELLOW': await ctx.send("<:osit:544356212846886924> You need a **GREEN** status to request a loan."); return
                    stata = 'GREEN'

                    quantity = int(raw[1])
                    if quantity >= invs: 
                        # Check if the loan is off-limit
                        if quantity > invs*3: await ctx.send(f"<:osit:544356212846886924> You cannot loan 3 times your current balance"); return
                        stata = 'YELLOW'
                    elif quantity < 0: await ctx.send("Don't be stupid <:fufu:605255050289348620>"); return

                    # Update prev investment, then the investment, then the invest_age
                    await self.client._cursor.execute(f"UPDATE pi_bank SET investment=(investment+investment*{invs_interst}*{age - invest_age})-{quantity}, invest_age={age} WHERE user_id='{str(ctx.message.author.id)}';")
                    await self.client._cursor.execute(f"UPDATE personal_info SET money=money+{quantity}, stats='{stata}' WHERE id='{str(ctx.message.author.id)}';")

                    await ctx.send(f":white_check_mark: **<:36pxGold:548661444133126185>{quantity}** has just been withdrawn from your account!"); return
                # E: Quantity not given
                except (IndexError, ValueError): await ctx.send("<:osit:544356212846886924> Please provide the amount you want to withdraw."); return                         

            # UPGRADE
            elif raw[0] == 'upgrade':
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
                    if await self.client._cursor.execute(f"UPDATE pi_bank SET tier='{next_tier}', interest={tier_dict[next_tier][1]} WHERE user_id='{str(ctx.message.author.id)}' AND EXISTS (SELECT * FROM pi_degrees WHERE user_id='{str(ctx.message.author.id)}' AND degree='{tier_dict[next_tier][0][0]}' AND major='{tier_dict[next_tier][0][1]}');") == 0:
                        await ctx.send(f":bank: Sorry. Your request to upgrade to tier `{next_tier}` does not meet the criteria."); return
                except KeyError: await ctx.send(f":bank: Your current tier is `{tier}`, which is the highest."); return

                await ctx.send(f":white_check_mark: Upgraded to tier `{next_tier}`!"); return

            # DOWNGRADE
            elif raw[0] == 'downgrade':
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
                    await self.client._cursor.execute(f"UPDATE pi_bank SET tier='{next_tier}', interest={tier_dict[next_tier][1]} WHERE user_id='{str(ctx.message.author.id)}';")
                except KeyError: await ctx.send(f":bank: Your current tier is `{tier}`, which is the lowest to be able to downgrade."); return

                await ctx.send(f":white_check_mark: Downgraded to tier `{next_tier}`!"); return

        # E: args not given
        except IndexError:

            line = f""":bank: `『TIER』` **· `{tier}`** ⠀⠀ ⠀:bank: `『INTEREST』` **· `{invs_interst}`** \n```$ {invs}```"""

            reembed = discord.Embed(title = f"{ctx.message.author.name.upper()}", colour = discord.Colour(0x011C3A), description=line)
            reembed.set_thumbnail(url=ctx.message.author.avatar_url)

            await ctx.send(embed=reembed)

    @commands.command(aliases=['edu'])
    @commands.cooldown(1, 10, type=BucketType.user)
    async def education(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        cur_X, cur_Y = await self.client.quefe(f"SELECT cur_X, cur_Y FROM personal_info WHERE id='{str(ctx.message.author.id)}';")
        if not await self.tools.area_scan(ctx, cur_X, cur_Y): await ctx.send("<:osit:544356212846886924> Educating facilities are only available within **Peace Belt**!"); return

        cmd_tag = 'edu'
        degrees = ['elementary', 'middleschool', 'highschool', 'associate', 'bachelor', 'master', 'doctorate']
        major = ['astrophysic', 'biology', 'chemistry', 'georaphy', 'mathematics', 'physics', 'education', 'archaeology', 'history', 'humanities', 'linguistics', 'literature', 'philosophy', 'psychology', 'management', 'international_bussiness', 'elemology', 'electronics', 'robotics', 'engineering']
 
        try: resp = args[0]
        except IndexError: await ctx.send(f":books: Welcome to **Ascending Sanctuary of Siegfields**. Please, take time and have a look.\n:books: **`{'` ➠ `'.join(degrees)}`**"); return

        # Check if the previous course has been finished yet
        if not await self.__cd_check(ctx.message, cmd_tag, f":books: *Enlightening requires one's most persevere and patience.*"): return

        def UMC_check(m):
            return m.channel == ctx.channel and m.author == ctx.author 

        try:
            temp1 = await ctx.send(f":bulb: ... and what major would you prefer?\n| **`{'` · `'.join(major)}`**")

            try: resp2 = await self.client.wait_for('message', check=UMC_check, timeout=20)
            # E: No respond
            except asyncio.TimeoutError: await ctx.send(":books: May the Olds look upon you..."); return
            # Major check
            if resp2.content.lower() not in major: await ctx.send(f"<:osit:544356212846886924> Invalid major!"); return

            await temp1.delete()

            price, INTT_require, INTT_reward, degree_require, duration = await self.client.quefe(f"SELECT price, INTT_require, INTT_reward, degree_require, duration FROM model_degree WHERE degree='{resp.lower()}';")
            degree_require = degree_require.split(' of ')

            # DEGREE (and MAJOR) check
            query = f"SELECT money, INTT FROM personal_info WHERE EXISTS (SELECT * FROM pi_degrees WHERE user_id='{ctx.author.id}' AND degree='{degree_require[0]}'"

            try:
                try: money, INTT = await self.client.quefe(query + f" AND major='{degree_require[1]}') AND id='{ctx.author.id}';")
                # E: No major required
                except IndexError: money, INTT = await self.client.quefe(query + f") AND id='{ctx.author.id}';")
            # E: Query return NONE
            except TypeError: await ctx.send(f"<:osit:544356212846886924> Your application does not meet the degree/major requirements, **{ctx.message.author.name}**."); return

            # MONEY and INTT check
            if money < price: await ctx.send(f"<:osit:544356212846886924> You need **<:36pxGold:548661444133126185>{price}** to enroll this program!"); return
            if INTT < INTT_require: await ctx.send(f"<:osit:544356212846886924> You need **{INTT_require}**`INT` to enroll this program!"); return
            
            temp2 = await ctx.send(f":books: Program for `{resp.capitalize()} of {resp2.content.capitalize()}`:\n| **Price:** <:36pxGold:548661444133126185>{price}\n| **Duration:** {duration/7200} months\n**Result:** · **`{resp.capitalize()} of {resp2.content.capitalize()}`** · `{INTT_reward}` INT. \n<a:RingingBell:559282950190006282> Do you wish to proceed? (Key: `enroll confirm` | Timeout=15s)")

            def UMCc_check(m):
                return m.channel == ctx.channel and m.author == ctx.author and m.content.lower() == 'enroll confirm'

            try: await self.client.wait_for('message', timeout=15, check=UMCc_check)
            except asyncio.TimeoutError: await ctx.send(f"<:osit:544356212846886924> Assignment session of {ctx.message.author.mention} is closed."); return
            await temp2.delete()

            # Initialize
            try: await self.client._cursor.execute(f"INSERT INTO pi_degrees VALUES ('{ctx.author.id}', '{resp.lower()}', '{resp2.content.lower()}');")
            except AttributeError: await self.client._cursor.execute(f"INSERT INTO pi_degrees VALUES ('{str(ctx.message.author.id)}', '{resp.lower()}', NULL);")
            await self.client._cursor.execute(f"UPDATE personal_info SET INTT={INTT + INTT_reward}, STA=0, money={money - price} WHERE id='{ctx.author.id}';")
            # Cooldown set
            await ctx.send(f":white_check_mark: **<:36pxGold:548661444133126185>{price}** has been deducted from your account.")
            await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.set, f'{cmd_tag}{ctx.author.id}', 'degreeing', ex=duration, nx=True))

        # E: Invalid degree
        except ZeroDivisionError: await ctx.send("<:osit:544356212846886924> Invalid degree!"); return

    @commands.command(aliases=['med'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def medication(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        cur_X, cur_Y, LP, MAX_LP, money = await self.client.quefe(f"SELECT cur_X, cur_Y, LP, MAX_LP, money FROM personal_info WHERE id='{ctx.author.id}'")

        if not await self.tools.area_scan(ctx, cur_X, cur_Y): await ctx.send("<:osit:544356212846886924> Medical treatments are only available within **Peace Belt**!"); return

        reco = MAX_LP - LP
        if reco == 0: await ctx.send(f"<:osit:544356212846886924> **{ctx.author.name}**, your current LP is at max!"); return

        reco_scale = reco//(MAX_LP/100)
        if reco_scale == 0: reco_scale = 1
        
        cost = int(reco*reco_scale)

        def UMCc_check(m):
            return m.channel == ctx.channel and m.content == 'treatment confirm' and m.author == ctx.author

        # Inform
        await ctx.send(f"<:healing_heart:508220588872171522> Dear {ctx.message.author.mention},\n------------\n· Your damaged scale: `{reco_scale}`\n· Your LP requested: `{reco}`\n· Price: <:36pxGold:548661444133126185>`{reco_scale}/LP`\n· Cost: <:36pxGold:548661444133126185>`   {cost}`\n------------\nPlease type `treatment confirm` within 20s to receive the treatment.")
        try: await self.client.wait_for('message', check=UMCc_check, timeout=20)
        except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Treatment is declined!"); return
        if money < cost: await ctx.send("<:osit:544356212846886924> Insufficient balance!"); return

        # Treat
        await self.client._cursor.execute(f"UPDATE personal_info SET money={money - cost}, LP={MAX_LP}")
        await ctx.send(f"<:healing_heart:508220588872171522> **<:36pxGold:548661444133126185>{cost}** has been deducted from your account, **{ctx.message.author.name}**!"); return









def setup(client):
    client.add_cog(avaService(client))
