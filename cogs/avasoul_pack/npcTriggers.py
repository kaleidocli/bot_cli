import asyncio
import random
from functools import partial

import discord
from discord.ext import commands
import discord.errors as discordErrors

from .avaCombat import avaCombat
from .avaTools import avaTools
from .avaUtils import avaUtils
from . import avaThirdParty

class npcTrigger:
    def __init__(self, client):
        self.client = client
        self.client.thp = avaThirdParty.avaThirdParty(client=self.client)
        self.__cd_check = self.client.thp.cd_check
        self.combat = avaCombat(self.client)
        self.utils = avaUtils(self.client)


    async def p0c0i0training(self, pack):
        """pack = [ctx, data_goods, entity_code]"""
        return

        await pack[0].send(f':checkered_flag: Training session **`NPC|Kaleido Cli` >< `Player|{pack[0].author.name}`** starting in 5 secs...', delete_after=5)
        await asyncio.sleep(5)
        await self.combat.PVE_training(pack[0], dummy_config=['p0', 'Kaleido Cli', 10, 1, 6])

    async def GE_trader(self, pack):
        # [ctx, data_goods, entity_code, entity_name, illulink, line, [args]]
        cmd_tag = f'trade{pack[2]}'

        quantity = 1

        # COOLDOWN
        if not await self.__cd_check(pack[0].message, cmd_tag, f"<:osit:544356212846886924> Busy busy, **{pack[0].author.name}**!"): return

        money = await self.client.quefe(f"SELECT money FROM personal_info WHERE id='{pack[0].author.id}';"); money = money[0]

        # Get cuisine
        #try: cuisine, r_name = await self.client.quefe(f"SELECT cuisine, name FROM environ WHERE environ_code='{cur_PLACE}';")
        #except TypeError:
        #    cuisine, r_name = await self.client.quefe(f"SELECT cuisine, name FROM pi_land WHERE land_code='{cur_PLACE}';")
        #    if not cuisine: await ctx.send("Traders are not through here, it seems..."); return

        # Get menu
        menu = []
        for count in range(2):
            menu.append(random.choice(pack[1].split(' - ')))

        # Get items
        items = {}
        for item in set(menu):
            if item.startswith('ig'): items[item] = await self.client.quefe(f"SELECT name, description, price, tags FROM model_ingredient WHERE ingredient_code='{item}';")
            else: items[item] = await self.client.quefe(f"SELECT name, description, price, tags FROM model_item WHERE item_code='{item}';")

        # MENU
        line = "\n"
        for ig_code in menu:
            line = line + f""" `{ig_code}` <:green_ruby:520092621381697540> **{items[ig_code][0]}**\n| **`Market price`** <:36pxGold:548661444133126185>{items[ig_code][2]}\n++ `{items[ig_code][3].replace(' - ', '` `')}`\n\n"""
            
        reembed = discord.Embed(title = f"`{pack[2]}`|**{pack[3]}**", colour = discord.Colour(0x011C3A), description=f"```{pack[5]}```{line}")
        try: reembed.set_thumbnail(url=pack[4])
        except discordErrors.HTTPException: pass
        temp1 = await pack[0].send(embed=reembed)
        await pack[0].send('<a:RingingBell:559282950190006282> Syntax: `!buy` `[item_code]` |  Time out: 25s')

        await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.set, f'{cmd_tag}{pack[0].author.id}', 'trading', ex=1800, nx=True))
        def UMCc_check(m):
            return m.channel == pack[0].channel and m.content.startswith('!buy') and m.author == pack[0].author

        # First buy
        try:
            raw = await self.client.wait_for('message', check=UMCc_check, timeout=25)
            await temp1.delete()
        except asyncio.TimeoutError: 
            await pack[0].send("<:osit:544356212846886924> Request timed out!")
            await temp1.delete(); return

        raw = raw.content.lower().split(' ')[1:]
        ig_code = raw[0]
        try:
            quantity = int(raw[1])
            if quantity > 5: quantity = 5
            # SCAM :)
            if quantity <= 0: await pack[0].send("Don't be dumb <:fufu:605255050289348620>"); return                
        # E: Quantity not given, or invalidly given
        except (IndexError, TypeError): pass

        # ig_code check    
        if ig_code not in menu: await pack[0].send("<:osit:544356212846886924> The trader does not have this item at the moment. Sorry."); return

        # Reconfirm
        def UMCc_check2(m):
            return m.channel == pack[0].channel and m.content == 'trade confirm' and m.author == pack[0].author

        price = int(items[ig_code][2]*random.choice([0.2, 1, 2, 5]))
        await pack[0].send(f"Yo {pack[0].message.author.mention}! I'll sell ya **<:36pxGold:548661444133126185>{price}** for each item `{ig_code}`|**{items[ig_code][0]}**. \nIn total, the cost will be **<:36pxGold:548661444133126185>{price*quantity}**.\n<a:RingingBell:559282950190006282> Proceed? (Key: `trade confirm` | Timeout=10s)")
        try: await self.client.wait_for('message', check=UMCc_check2, timeout=10)
        except asyncio.TimeoutError: await pack[0].send("<:osit:544356212846886924> Request declined!"); return
        
        try:
            # Money check
            if price*quantity <= money:
                # UN-SERIALIZABLE
                # Increase item_code's quantity
                if ig_code.startswith('ig'): await self.client._cursor.execute(f"SELECT func_ig_reward('{pack[0].author.id}', '{ig_code}', {quantity});")
                else: await self.client._cursor.execute(f"SELECT func_it_reward('{pack[0].author.id}', '{ig_code}', {quantity});")
                #if await self.client._cursor.execute(f"UPDATE pi_inventory SET quantity=quantity+{quantity} WHERE user_id='{str(ctx.message.author.id)}' AND item_code='{ig_code}';") == 0:
                    # E: item_code did not exist. Create one, with given quantity
                #    await self.client._cursor.execute(f"INSERT INTO pi_inventory SELECT 0, {str(ctx.message.author.id)}, ingredient_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, infuse_query, order_query, passive_query, ultima_query, {quantity}, price, dmg, stealth, evo, aura, craft_value, illulink FROM model_ingredient WHERE ingredient_code='{ig_code}';")

                # Deduct money
                await self.client._cursor.execute(f"UPDATE personal_info SET money=money-{price*quantity} WHERE id='{pack[0].author.id}';")

            else: await pack[0].send("<:osit:544356212846886924> Insufficience balance!"); return
        # E: Item_code not found
        except KeyError: await pack[0].send("<:osit:544356212846886924> Item's code not found!"); return


        # Greeting, of course :)
        await pack[0].send(f":white_check_mark: Received **{quantity}** item `{ig_code}`|**{items[ig_code][0]}**. Nice trade!")

    async def GE_inspect(self, pack):
        # ([ctx, value_chem, value_impression, flag, entity_code, entity_name, cur_PLACE, cur_X, cur_Y]

        interas = await self.client.quefe(f"SELECT intera_kw FROM environ_interaction WHERE entity_code='{pack[4]}' AND limit_flag='{pack[3]}' AND (({pack[1]}>=limit_chem AND chem_compasign='>=') OR ({pack[1]}<limit_chem AND chem_compasign='<')) AND (({pack[2]}>=limit_impression AND imp_compasign='>=') OR ({pack[2]}<limit_impression AND imp_compasign='<')) AND region='{pack[6]}' AND limit_Ax<={pack[7]} AND {pack[7]}<limit_Bx AND limit_Ay<={pack[8]} AND {pack[8]}<limit_By ORDER BY limit_Ax DESC, limit_Bx ASC, limit_Ay DESC, limit_By ASC, limit_chem DESC, limit_impression DESC;", type='all')

        if not interas: await pack[0].send(":x: There's nothing you can do now, unfortunately..."); return

        await pack[0].send(f":moyai: Few actions you can perform...\n\t**`{'`** · **`'.join([x[0] for x in interas])}`**")


