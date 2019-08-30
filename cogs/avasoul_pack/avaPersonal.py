import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import asyncio
import random
from functools import partial

from .avaTools import avaTools
from .avaUtils import avaUtils

class avaPersonal:
    def __init__(self, client):
        self.client = client
        self.__cd_check = self.client.thp.cd_check
        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)


    async def on_ready(self):
        print("|| Personalize --- READY!")



    @commands.command(aliases=['sleep'])
    @commands.cooldown(3, 60, type=BucketType.user)
    async def rest(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        cur_X, cur_Y= await self.client.quefe(f"SELECT cur_X, cur_Y FROM personal_info WHERE id='{ctx.author.id}';")
        if not await self.tools.area_scan(ctx, cur_X, cur_Y): await ctx.send("<:osit:544356212846886924> No you cannot rest outside of **Peace Belt**!"); return

        try:
            stats, rest_point = await self.client.quefe(f"SELECT stats, rest_point FROM pi_rest WHERE user_id='{ctx.author.id}';")
            if stats == 'REST': await ctx.send(f"<:osit:544356212846886924> You're already resting, **{ctx.author.name}**."); return 
        except TypeError: pass

        rest_point = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if await self.client._cursor.execute(f"UPDATE pi_rest SET stats='REST', rest_point='{rest_point}' WHERE user_id='{ctx.author.id}'; UPDATE personal_info SET STA=0 WHERE id='{ctx.author.id}';") == 0:
            await self.client._cursor.execute(f"INSERT INTO pi_rest VALUES ('{ctx.author.id}', 'REST', '{rest_point}'); UPDATE personal_info SET STA=0 WHERE id='{ctx.author.id}';")

        await ctx.send(f"<:zzzz:544354429315579905> Rested at `{rest_point}`"); return

    @commands.command(aliases=['awake'])
    @commands.cooldown(3, 60, type=BucketType.user)
    async def wake(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        cur_X, cur_Y, charm, MAX_STA, MAX_LP, LP = await self.client.quefe(f"SELECT cur_X, cur_Y, charm, MAX_STA, MAX_LP, LP FROM personal_info WHERE id='{ctx.author.id}';")
        if not await self.tools.area_scan(ctx, cur_X, cur_Y): await ctx.send("<:osit:544356212846886924> No you cannot rest outside of **Peace Belt**!"); return

        rest_point = await self.client.quefe(f"SELECT rest_point FROM pi_rest WHERE user_id='{ctx.author.id}' AND stats='REST';")
        try: rest_point = rest_point[0]
        except TypeError: await ctx.send(f"<:osit:544356212846886924> You're not sleeping, **{ctx.author.name}**"); return

        delta = relativedelta(datetime.now(), rest_point)
        reco_rate = LP/(MAX_LP/2)
        if reco_rate < 0.25: reco_rate = 0.25

        duration = delta.minutes+(delta.hours*60)+(delta.days*1440)
        sta_receive = round(reco_rate*(duration/(charm/60)))
        if sta_receive > MAX_STA: sta_receive = MAX_STA

        msg = await ctx.send(f"<a:RingingBell:559282950190006282> You've rested for `{duration}` minutes, **{ctx.author.name}**. Get **{sta_receive} STA**?")
        def UM_check(reaction, user):
            return user.id == ctx.author.id and reaction.message.id == msg.id and reaction.emoji == '\U00002600'

        await msg.add_reaction("\U00002600")
        try: await self.client.wait_for('reaction_add', timeout=10, check=UM_check)
        except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request timed out."); return

        await self.client._cursor.execute(f"UPDATE personal_info SET STA={sta_receive} WHERE id='{ctx.author.id}'; UPDATE pi_rest SET stats='AWAKE' WHERE user_id='{ctx.author.id}';")
        await ctx.send(f":sunrise_over_mountains: Beneath piles of cotton growling an annoying voice... *Groaaarrr!* Good.. morning? You've recovered **{sta_receive}**`STA`!"); return

    @commands.command(aliases=['evo'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def evolve(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        perks, evo, LP = await self.client.quefe(f"SELECT perks, EVO, LP FROM personal_info WHERE id='{ctx.author.id}';")

        raw = list(args)


        evo_dict = {'lp': f"UPDATE personal_info SET MAX_LP=MAX_LP+ROUND(MAX_LP/100*5), EVO=EVO+1, perks=perks-1 WHERE id='{ctx.author.id}' AND perks>0;",
                    'sta': f"UPDATE personal_info SET MAX_STA=MAX_STA+ROUND(MAX_STA/100*10), EVO=EVO+1, perks=perks-1 WHERE id='{str(ctx.message.author.id)}' AND perks>0;",
                    'str': f"UPDATE personal_info SET STR=STR+0.1, EVO=EVO+1, perks=perks-1 WHERE id='{str(ctx.message.author.id)}' AND perks>0;",
                    'int': f"UPDATE personal_info SET INTT=INTT+0.1, EVO=EVO+1, perks=perks-1 WHERE id='{str(ctx.message.author.id)}' AND perks>0;",
                    'flame': f"UPDATE personal_info SET au_FLAME=au_FLAME+0.05, EVO=EVO+1, perks=perks-1 WHERE id='{str(ctx.message.author.id)}' AND perks>0;",
                    'ice': f"UPDATE personal_info SET au_ICE=au_ICE+0.05, EVO=EVO+1, perks=perks-1 WHERE id='{str(ctx.message.author.id)}' AND perks>0;",
                    'holy': f"UPDATE personal_info SET au_HOLY=au_HOLY+0.05, EVO=EVO+1, perks=perks-1 WHERE id='{str(ctx.message.author.id)}' AND perks>0;",
                    'dark': f"UPDATE personal_info SET au_DARK=au_DARK+0.05, EVO=EVO+1, perks=perks-1 WHERE id='{str(ctx.message.author.id)}' AND perks>0;",
                    'charm': f"UPDATE personal_info SET charm=charm+1, perks=perks-1 WHERE id='{str(ctx.message.author.id)}' AND perks>0;"}

        try:
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

                def UM_check(reaction, user):
                    return user.id == ctx.author.id and reaction.message.id == msg.id

                try: await self.client.wait_for('reaction_add', timeout=20, check=UM_check)
                except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request decline!"); return

                LP, MAX_LP, STA, STR, INT = await self.client.quefe(f"SELECT LP, MAX_LP, STA, STR, INT FROM personal_info WHERE id='{ctx.author.id}';")
                await self.client._cursor.execute(f"UPDATE personal_info SET perks=perks-1, LP={random.randint(0, LP*2)}, MAX_LP={random.randint(0, MAX_LP*2)}, STA={random.randint(0, STA*2)}, STR={random.randint(0, round(STR*2))}, INT={random.randint(0, round(INT*2))} WHERE id='{ctx.author.id}';")
                await ctx.send("<:osit:544356212846886924> Mutation succeed! Check your profile immidiately..."); return


            if await self.client._cursor.execute(evo_dict[raw[0].lower()]) == 0: await ctx.send("<:osit:544356212846886924> Not enough perks!"); return

        # E: Attributes not found
        except KeyError: await ctx.send("<:osit:544356212846886924> Invalid attribute!"); return

        # E: Attri not given
        except IndexError: await ctx.send(f"<:zapp:524893958115950603> Perks can be spent on your attributes:\n________________________\n**|** `LP` · +5% MAX_LP \n**|** `STA` · +10% MAX_STA \n**|** `STR` · +0.1 STR\n**|** `INT` · +0.1 INT\n**|** `FLAME` · +0.05 aura \n**|** `ICE` · +0.05 aura \n**|** `HOLY` · +0.05 aura \n**|** `DARK` · +0.05 aura\n**|** `CHARM` · +0.01 CHARM \n________________________\n**Your perks:** {perks}\n**Your evolution:** {evo}"); return

        await ctx.send("<:zapp:524893958115950603> Done. You may use `profile` to check.")

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
        except (IndexError, TypeError): pass
        
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

    @commands.command(aliases=['i'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def inventory(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        cur_PLACE  = await self.client.quefe(f"SELECT cur_PLACE FROM personal_info WHERE id='{str(ctx.message.author.id)}';")
        cur_PLACE = cur_PLACE[0]

        # INSPECT ===============
        raw = list(args)
        try:
            # Get info
            try: 
                item_code, name, description, tags, weight, defend, multiplier, strr, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, evo, aura, illulink, price = await self.client.quefe(f"""SELECT item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, evo, aura, illulink, price FROM pi_inventory WHERE existence='GOOD' AND item_id='{raw[0]}';""")
                if evo != 0: evo_plus = f"+{evo}"
                else: evo_plus = ''

                # Pointer
                if 'magic' in tags: pointer = ':crystal_ball:'
                else: pointer = '<:gun_pistol:508213644375621632>'
                # Aura icon
                aui = {'FLAME': 'https://imgur.com/3UnIPir.png', 'ICE': 'https://imgur.com/7HsDWfj.png', 'HOLY': 'https://imgur.com/lA1qfnf.png', 'DARK': 'https://imgur.com/yEksklA.png'}

                line = f""":scroll: **`『Weight』` ·** {weight} ⠀ ⠀:scroll: **`『Price』` ·** {price}\n```"{description}"```\n"""
                
                reembed = discord.Embed(title=f"`{item_code}`|**{' '.join([x for x in name.upper()])}** {evo_plus}", colour = discord.Colour(0x011C3A), description=line)
                reembed.add_field(name=":scroll: Basic Status <:broadsword:508214667416698882>", value=f"**`『STR』` ·** {strr}\n**`『INT』` ·** {intt}\n**`『STA』` ·** {sta}\n**`『MULTIPLIER』` ·** {multiplier}\n**`『DEFEND』` ·** {defend}\n**`『SPEED』` ·** {speed}", inline=True)

                try: acc_per = 10//accuracy_randomness
                except ZeroDivisionError: acc_per = 0
                reembed.add_field(name=f":scroll: Projector Status {pointer}", value=f"**`『RANGE』` ·** {range_min} - {range_max}m\n**`『STEALTH』` ·** {stealth}\n**`『FIRING-RATE』` ·** {firing_rate}\n**`『ACCURACY』` ·** {acc_per}%/{accuracy_range}m\n**-------------------**\n**`『ROUND』` ·** {round} \n**`『DMG』` ·** {dmg}", inline=True)

                reembed.set_thumbnail(url=aui[aura])
                if illulink != 'n/a': reembed.set_image(url=illulink)

                await ctx.send(embed=reembed, delete_after=30); return
            # Tags given, instead of item_id
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

        async def browse():
            items = await self.client.quefe(f"""SELECT item_id, item_code, name, description, tags, weight, quantity, price, aura FROM pi_inventory WHERE existence='GOOD' AND user_id='{str(ctx.message.author.id)}' {lk_query};""", type='all')

            if not items: await ctx.send(f":x: No result..."); return

            def makeembed(top, least, pages, currentpage):
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
                    line = line + f""" `{item[0]}` {icon} `{item[1]}`| **{item[2]}** [{item[6]}]\n╟ *"{item[3]}"*\n**╟ `『Weight』{item[5]}`** · **`『Price』`<:36pxGold:548661444133126185>`{item[7]}`**\n**╟╼**`{item[4].replace(' - ', '`·`')}`\n\n"""
                            
                line = line + f"**╚═════════╡**`{currentpage}/{pages}`**╞══════════**" 

                reembed = discord.Embed(title = f"░░░░░<:mili_bag:507144828874915860> **I N V E N T O R Y** <:mili_bag:507144828874915860>░░░░░", colour = discord.Colour(0x011C3A), description=line)
                return reembed
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
            if pages > 1:
                msg = await ctx.send(embed=emli[cursor])
                await attachreaction(msg)
            else: 
                msg = await ctx.send(embed=emli[cursor], delete_after=15)
                return

            def UM_check(reaction, user):
                return user.id == ctx.author.id and reaction.message.id == msg.id

            while True:
                try:
                    reaction, user = await self.client.wait_for('reaction_add', timeout=15, check=UM_check)
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

        await browse()

    @commands.command(aliases=['u'])
    @commands.cooldown(1, 2, type=BucketType.user)
    async def use(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        raw = list(args)
        slots = {"a": 'right_hand', "b": "left_hand"}

        try:
            # Filter
            int(raw[0])

            # INCONSUMABLE
            try:
                ##Get weapon info
                try: w_name, w_tags, w_eq, w_weight, w_code = await self.client.quefe(f"SELECT name, tags, effect_query, weight, item_code FROM pi_inventory WHERE existence='GOOD' AND user_id='{ctx.author.id}' AND item_id='{raw[0]}';")
                except TypeError: await ctx.send(f"<:osit:544356212846886924> You don't own this item! (id.`{raw[0]}`)"); return

                if 'supply' in w_tags or 'ingredient' in w_tags: raise ZeroDivisionError

                ##Get slot_name
                try: slot_name = slots[raw[1]]
                except IndexError: slot_name = slots['a']
                except KeyError: await ctx.send(f"<:osit:544356212846886924> Slots not found, **{ctx.message.author.name}**!\n:grey_question: There are `2` weapon slots available: `0` Main Weapon | `1` Secondary Weapon"); return
                ##Get weapon
                weapon = await self.client.quefe(f"SELECT {slot_name} FROM personal_info WHERE id='{str(ctx.message.author.id)}';"); weapon = weapon[0]

                ##Equip
                if raw[0] != weapon:
                    await self.client._cursor.execute(f"UPDATE personal_info SET {slot_name}='{raw[0]}' WHERE id='{str(ctx.message.author.id)}';")
                    # Inform, of course :)
                    await ctx.send(f":white_check_mark: Equipped item `{raw[0]}`|**{w_name}** to `{slot_name}` slot!"); return
                ###Already equip    -----> Unequip
                else:
                    await self.client._cursor.execute(f"UPDATE personal_info SET {slot_name}=(SELECT item_id FROM pi_inventory WHERE user_id='{ctx.author.id}' AND item_code='ar13') WHERE id='{ctx.author.id}'")
                    await ctx.send(f":white_check_mark: Unequipped item `{raw[0]}`|**{w_name}** from *{slot_name}* slot!")
                    return
            # CONSUMABLE (Supply / Ingredient)
            except ZeroDivisionError:
                
                # Effect_query check
                if not w_eq: await ctx.send(":white_check_mark: Tried to use, but no effect received."); return

                ## Get quantity
                try:
                    target_id = str(ctx.message.author.id)
                    quantity = int(raw[1])
                    # SCAM :)
                    if quantity <= 0: await ctx.send("**Heyyyyyyyyy scammer-!**"); return
                    #if w_quantity <= quantity: 
                        #quantity = w_quantity
                        #quantity_query = f"UPDATE pi_inventory SET existence='BAD' WHERE item_id={raw[0]} AND user_id='{target_id}';"
                    #else:
                    #    quantity_query = f"UPDATE pi_inventory SET quantity=quantity-{quantity} WHERE item_id='{raw[0]}' AND user_id='{target_id}';"
                    quantity_query = f"SELECT func_i_delete('{target_id}', '{w_code}', {quantity});"

                ## E: No quantity given
                except IndexError:
                    target_id = str(ctx.message.author.id)
                    quantity = 1
                    #if w_quantity <= quantity: 
                    #    quantity = w_quantity
                    #    quantity_query = f"UPDATE pi_inventory SET existence='BAD' WHERE item_id={raw[0]} AND user_id='{target_id}';"
                    #else:
                    #    quantity_query = f"UPDATE pi_inventory SET quantity=quantity-{quantity} WHERE item_id='{raw[0]}' AND user_id='{target_id}';"
                    quantity_query = f"SELECT func_i_delete('{target_id}', '{w_code}', {quantity});"

                ## E: Invalid type of quantity argument
                except TypeError:
                    ## Get target_id
                    try: target_id = str(ctx.message.mentions[0].id)
                    ## E: No mention
                    except IndexError: target_id = str(ctx.author.id)
                    quantity = 1
                    #if w_quantity <= quantity:
                    #    quantity = w_quantity
                    #    quantity_query = f"UPDATE pi_inventory SET existence='BAD' WHERE item_id={raw[0]} AND user_id='{target_id}';"
                    #else:
                    #    quantity_query = f"UPDATE pi_inventory SET quantity=quantity-{quantity} WHERE item_id='{raw[0]}' AND user_id='{target_id}';"
                    quantity_query = f"SELECT func_i_delete('{target_id}', '{w_code}', {quantity});"

                # Get target info
                try: t_name, t_STA, t_MAX_STA = await self.client.quefe(f"SELECT name, STA, MAX_STA FROM personal_info WHERE id='{target_id}';")
                except TypeError: await ctx.send("<:osit:544356212846886924> Target has not incarnated")
                # Prepair query
                w_eq = w_eq.replace("user_id_here", target_id)
                af_query = ''
                # pylint: disable=unused-variable
                for time in range(quantity):
                    # Affect
                    af_query = af_query + w_eq
                # pylint: enable=unused-variable
                # Weight check :">
                ex_query = ''
                if t_STA > t_MAX_STA:
                    # Weigh on the commander. Please don't change
                    ex_query = f"UPDATE personal_info SET weight=weight+{random.choice([0, 0.1, 0.2, 0.5, 1, 1.2, 1.5, 2])*w_weight*quantity} WHERE id='{str(ctx.message.author.id)}';"

                ## Adjusting things with quantity
                await self.client._cursor.execute(quantity_query + af_query + ex_query)
                await self.tools.ava_scan(ctx.message, type='normalize', target_id=target_id)
                #print(quantity_query + af_query + ex_query)
                await ctx.send(f":white_check_mark: Used {quantity} `{raw[0]}`|**{w_name}** on **{t_name}**")                

        # E: Slot not given            
        except IndexError:
            # Switch
            mw, sw = await self.client.quefe(f"SELECT right_hand, {slots['b']} FROM personal_info WHERE id='{str(ctx.message.author.id)}';")
            await self.client._cursor.execute(f"UPDATE personal_info SET right_hand='{sw}', {slots['b']}='{mw}' WHERE id='{str(ctx.message.author.id)}';")

            # Get line
            sw_name = await self.client.quefe(f"SELECT name FROM pi_inventory WHERE existence='GOOD' AND user_id='{str(ctx.message.author.id)}' AND item_id='{sw}';")
            if sw_name: line_1 = f"`{sw}`|**{sw_name}** ➠ **right_hand**"
            else: line_1 = '**right_hand** is left empty'
            mw_name = await self.client.quefe(f"SELECT name FROM pi_inventory WHERE existence='GOOD' AND user_id='{str(ctx.message.author.id)}' AND item_id='{mw}';")
            if mw_name: line_2 = f"`{mw}`|**{mw_name}** ➠ **{slots['b']}**'"
            else: line_2 = f"**{slots['b']}** is left empty"
            # Inform :)
            await ctx.send(f":twisted_rightwards_arrows: {line_1} **|** {line_2} "); return
    
        # E: <item_code> OR <slot> given, instead of <item_id>
        except ValueError:

            # SLOT SWITCHING
            try:
                # Switch
                mw, sw = await self.client.quefe(f"SELECT right_hand, {slots[raw[0]]} FROM personal_info WHERE id='{str(ctx.message.author.id)}';")
                await self.client._cursor.execute(f"UPDATE personal_info SET right_hand='{sw}', {slots['b']}='{mw}' WHERE id='{str(ctx.message.author.id)}';")

                # Get line
                sw_name = await self.client.quefe(f"SELECT name FROM pi_inventory WHERE existence='GOOD' AND user_id='{str(ctx.message.author.id)}' AND item_id='{sw}';")
                if sw_name: line_1 = f"`{sw}`|**{sw_name}** ➠ **right_hand**"
                else: line_1 = '**right_hand** is left empty'
                mw_name = await self.client.quefe(f"SELECT name FROM pi_inventory WHERE existence='GOOD' AND user_id='{str(ctx.message.author.id)}' AND item_id='{mw}';")
                if mw_name: line_2 = f"`{mw}`|**{mw_name}** ➠ **{slots[raw[0]]}**'"
                else: line_2 = f"**{slots[raw[0]]}** is left empty"
                # Inform :)
                await ctx.send(f":twisted_rightwards_arrows: {line_1} **|** {line_2} "); return
            # E: Slot not found
            except KeyError: pass




def setup(client):
    client.add_cog(avaPersonal(client))
