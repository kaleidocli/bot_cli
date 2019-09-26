import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import pymysql.err as mysqlError

import json
from functools import partial
from io import BytesIO
from datetime import datetime

from utils import checks
from .avaTools import avaTools
from .avaUtils import avaUtils

class avaAdmin(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.utils = avaUtils(self.client)

    @commands.Cog.listener()
    async def on_ready(self):
        print("|| Admin --- Ready!")



    def data_updating(self, update_kw):
        if update_kw == 'time_pack':
            time_pack = (self.client.STONE.year, self.client.STONE.month, self.client.STONE.day, self.client.STONE.hour, self.client.STONE.minute)
            with open('data/time.json', 'w') as f:
                json.dump(time_pack, f, indent=4)



    #@commands.command(pass_context=True)
    #@checks.check_author()
    #async def milestime(self, ctx):
    #    self.client.STONE = datetime.now()
    #    self.data_updating()

    @commands.command()
    @checks.check_author()
    async def megagive(self, ctx, *args):
        try: target = await commands.MemberConverter().convert(ctx, args[0])
        except commands.CommandError: await ctx.send("Invalid `user`"); return
        except IndexError: await ctx.send("Missing `user`"); return

        try: money = int(args[1])
        except IndexError: await ctx.send('Missing `money`'); return
        except ValueError: await ctx.send('Invalid `money`'); return

        if await self.client._cursor.execute(f"UPDATE personal_info SET money=money+{money} WHERE id='{target.id}';") == 0:
            await ctx.send(f"User **{target.name}** has not incarnted"); return
        
        await ctx.send(f":white_check_mark: Under the name of almighty Aknalumos, **<:36pxGold:548661444133126185>{money}** has been given to **{target.name}**!"); return

    @commands.command()
    @checks.check_author()
    async def megatao(self, ctx, *args):
        try: target = await commands.MemberConverter().convert(ctx, args[0])
        except commands.CommandError: await ctx.send("Invalid `user`"); return
        except IndexError: await ctx.send("Missing `user`"); return

        try: item_code = args[1]
        except IndexError: await ctx.send("Missing `item_code`"); return

        try: quantity = int(args[2])
        except (ValueError, IndexError): quantity = 1

        if item_code.startswith('ig'):
            t = await self.client._cursor.execute(f"SELECT func_ig_reward('{target.id}', '{item_code}', {quantity}); ")
        elif item_code.startswith('it') or item_code.startswith('ar') or item_code.startswith('am') or item_code.startswith('bp'):
            t = await self.client._cursor.execute(f"SELECT func_it_reward('{target.id}', '{item_code}', {quantity}); ")
        elif item_code.startswith('if'):
            try: land_code = args[3]
            except IndexError: await ctx.send("Missing `land_code`"); return
            t = await self.client._cursor.execute(f"SELECT func_if_reward('{land_code}', '{item_code}', {quantity}); ")
        
        if not t: await ctx.send(":x:"); print(t); return
        await ctx.send(f":white_check_mark: Given {quantity} `{item_code}` to **{target.name}**")

    @commands.command()
    @checks.check_author()
    async def megafreeze(self, ctx, *args):
        try:
            target_id = ctx.message.mentions[0].id
            cmd_tag = args[1]
            if cmd_tag.startswith('<@'): cmd_tag = args[0]
        except (IndexError, TypeError): await ctx.send(":warning: Missing stuff!"); return

        if await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.delete, f'{cmd_tag}{target_id}')) == 0: await ctx.send(':x:')
        else: await ctx.send(':white_check_mark:')

    @commands.command()
    @checks.check_author()
    async def megakill(self, ctx, *args):
        if not args: await ctx.send(":warning: Missing user!"); return
        try: 
            target_id = ctx.message.mentions[0].id
            target_name = ctx.message.mentions[0].mention
        except (IndexError, TypeError):
            target_id = args[0]
            target_name = args[0]

        query = f"""DELETE FROM pi_degrees WHERE user_id='{target_id}';
                    DELETE FROM pi_guild WHERE user_id='{target_id}';
                    DELETE FROM cosmetic_preset WHERE user_id='{target_id}';
                    DELETE FROM pi_arts WHERE user_id='{target_id}';
                    UPDATE pi_inventory SET existence='BAD' WHERE user_id='{target_id}';
                    UPDATE pi_land SET user_id='BAD' WHERE user_id='{target_id}';
                    DELETE FROM pi_bank WHERE user_id='{target_id}';
                    DELETE FROM pi_avatars WHERE user_id='{target_id}';
                    DELETE FROM pi_hunt WHERE user_id='{target_id}';
                    DELETE FROM pi_mobs_collection WHERE user_id='{target_id}';
                    DELETE FROM pi_rest WHERE user_id='{target_id}';
                    DELETE FROM pi_quests WHERE user_id='{target_id}';
                    DELETE FROM personal_info WHERE id='{target_id}';"""

        if await self.client._cursor.execute(query) == 0:
            await ctx.send(':warning: User has not incarnated'); return
        await ctx.send(f":white_check_mark: Slashed {target_name} into half. Bai ya~")

    @commands.command()
    @checks.check_author()
    async def megasql(self, ctx, *, args):
        if str(ctx.author.id) != '214128381762076672': await ctx.send("SHOO SHOO!"); return
        ret = await self.client._cursor.execute(args)
        await ctx.send(ret)

    @commands.command(hidden=True)
    @checks.check_author()
    async def sql(self, ctx, *, query):

        query = self.utils.cleanup_code(query)

        #is_multistatement = query.count(';') > 1
        #if is_multistatement:
        #    # fetch does not support multiple statements
        #    strategy = self.client._cursor.fetchall
        #else:
        strategy = self.client._cursor.fetchall

        try:
            if not await self.client._cursor.execute(query): await ctx.send(":x: No effect")
        except mysqlError.ProgrammingError: await ctx.send(":x: Invalid syntax!"); return
        try:
            results = await strategy()
        except Exception as e:
            return await ctx.send(f'```py\n{format.format_exception(e)}\n```')

        #rows = len(results)
        #if is_multistatement or rows == 0:
        #    return await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

        #headers = list(results[0].keys())
        try: col = len(results[0])
        except TypeError: await ctx.send(':x:'); return

        table = format.TabularData()
        table.set_columns(['-']*col)
        table.add_rows(list(r) for r in results)
        render = table.render()

        fmt = f'```\n{render}\n```'
        if len(fmt) > 2000:
            fp = BytesIO(fmt.encode('utf-8'))
            await ctx.send('Too many results...', file=discord.File(fp, 'results.txt'))
        else:
            await ctx.send(fmt)

    @commands.command(pass_context=True)
    async def get_imgur(self, ctx, *args):
        if args:
            if '.png' not in args[0] or '.jpg' not in args[0] or '.jpeg' not in args[0] or '.gif' not in args[0]:
                await ctx.send(f"<:osit:544356212846886924> {ctx.message.author.mention}, invalid link!"); return
            else: source = args[0]
        else:
            package = ctx.message.attachments
            if package: source = package[0]['proxy_url']
            else: return

        resp = await self.client.loop.run_in_executor(None, self.client.thp.imgur_client.upload_from_url, source)
        reembed = discord.Embed(description=f"{resp['link']}", colour = discord.Colour(0x011C3A))
        reembed.set_image(url=resp['link'])
        await ctx.send(embed=reembed)

    @commands.command()
    @checks.check_author()
    async def avaava_giveitem(self, ctx, *args):
        raw = list(args)

        try:
            storage = raw[0]
            item_code = raw[1]
            try: quantity = int(raw[2])
            except IndexError: quantity = 1
        except IndexError: await ctx.send(f"<:osit:544356212846886924> Args missing")

        # GET ITEM INFO
        try:
            if storage == 'it': 
                tags = await self.client.quefe(f"""SELECT name, tags, price, quantity FROM model_item WHERE item_code='{item_code}';""")
                i_tags = tags[0].split(' - ')
        # E: Item code not found
        except TypeError: await ctx.send("<:osit:544356212846886924> Item_code/Item_id not found!"); return

        # ITEM
        if storage == 'it':
            # CONSUMABLE
            if 'consumable' in i_tags:
                # Create item in inventory. Ignore the given quantity please :>
                await self.client._cursor.execute(f"INSERT INTO pi_inventory SELECT 0, '{str(ctx.message.author.id)}', item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, infuse_query, order_query, passive_query, ultima_query, quantity, price, dmg, stealth, evo, aura, craft_value, illulink FROM model_item WHERE item_code='{item_code}';")
                # (MODEL FOR QUERY RECORD-TRANSFERING) ------- await self.client._cursor.execute(f"INSERT INTO pi_inventory SELECT 0, {str(ctx.message.author.id)}, item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, quantity, price, dmg, stealth FROM model_item WHERE item_code='{item_code}';")

            # INCONSUMABLE
            else:
                # Increase item_code's quantity
                if await self.client._cursor.execute(f"UPDATE pi_inventory SET quantity=quantity+{quantity} WHERE user_id='{str(ctx.message.author.id)}' AND item_code='{item_code}';") == 0:
                    # E: item_code did not exist. Create one, with given quantity
                    await self.client._cursor.execute(f"INSERT INTO pi_inventory SELECT 0, '{str(ctx.message.author.id)}', item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, infuse_query, order_query, passive_query, ultima_query, {quantity}, price, dmg, stealth, evo, aura, craft_value, illulink FROM model_item WHERE item_code='{item_code}';")

        # INGREDIENT
        elif storage == 'ig':
            # UN-SERIALIZABLE
            # Increase item_code's quantity
            if await self.client._cursor.execute(f"UPDATE pi_inventory SET quantity=quantity+{quantity} WHERE user_id='{str(ctx.message.author.id)}' AND item_code='{item_code}';") == 0:
                # E: item_code did not exist. Create one, with given quantity
                await self.client._cursor.execute(f"INSERT INTO pi_inventory SELECT 0, {str(ctx.message.author.id)}, ingredient_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, reload_query, effect_query, infuse_query, order_query, passive_query, ultima_query, quantity, price, dmg, stealth, evo, aura, craft_value, illulink FROM model_ingredient WHERE ingredient_code='{item_code}';")

        await ctx.send(":white_check_mark: Done.")

    @commands.command()
    @checks.check_author()
    async def todo(self, ctx, *args):
        if not args:
            bundle = await self.client.quefe("SELECT taime, content, id FROM tz_todo", type='all')
            line = '\n'

            try:
                for pack in bundle:
                    line = line + f"**━{pack[2]}━━━━━{pack[0]}━━━**\n{pack[1]}\n"
            except TypeError:
                line = line + f"**━{bundle[2]}━━━━━{bundle[0]}━━━**\n{bundle[1]}\n"

            reembed = discord.Embed(description=line, color=discord.Colour(0xB1F1FA))
            await ctx.send(embed=reembed, delete_after=20); return

        if args[0] in ['create', 'add', 'make']:
            content = ' '.join(args[1:])
            create_point = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            await self.client._cursor.execute(f"INSERT INTO tz_todo VALUES (0, '{content}', '{create_point}')")
            await ctx.send(":white_check_mark: Done"); return
        elif args[0] == 'delete':
            try: 
                if await self.client._cursor.execute(f"DELETE FROM tz_todo WHERE id='{args[1]}';") == 0:
                    await ctx.send("Id not found"); return
            except IndexError: await ctx.send("Hey you, I need an id."); return
            await ctx.send(f"Deleted todo `{args[1]}`")

    @commands.command()
    @checks.check_author()
    async def viewitem(self, ctx, *args):

        item_code, name, description, tags, weight, defend, multiplier, strr, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, aura, illulink, price = await self.client.quefe(f"""SELECT item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, aura, illulink, price FROM model_item WHERE item_code='{args[0]}';""")

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
        reembed.add_field(name=f":scroll: Projector Status {pointer}", value=f"**`『RANGE』` ·** {range_min} - {range_max}m\n**`『STEALTH』` ·** {stealth}\n**`『FIRING-RATE』` ·** {firing_rate}\n**`『ACCURACY』` ·** {acc_per}/{accuracy_range}m\n**-------------------**\n**`『ROUND』` ·** {round} \n**`『DMG』` ·** {dmg}", inline=True)

        reembed.set_thumbnail(url=aui[aura])
        if illulink != 'n/a': reembed.set_image(url=illulink)

        await ctx.send(embed=reembed); return




    # UPDATING command ===================================

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    @checks.check_author()
    async def ituda(self, ctx, *args):

        codes = await self.client.quefe(f"SELECT item_code FROM pi_inventory WHERE item_code LIKE 'it%' OR item_code LIKE 'ar%' OR item_code LIKE 'am%';", type='all')

        for code in codes:
            await self.client._cursor.execute(f"UPDATE pi_inventory p INNER JOIN model_item m ON m.item_code='{code[0]}' SET p.tags=m.tags, p.weight=m.weight, p.defend=m.defend, p.multiplier=p.multiplier, p.str=m.str, p.intt=m.intt, p.sta=m.sta, p.speed=m.speed, p.round=m.round, p.accuracy_randomness=m.accuracy_randomness, p.accuracy_range=m.accuracy_range, p.range_min=m.range_min, p.range_max=m.range_max, p.firing_rate=m.firing_rate, p.reload_query=m.reload_query, p.effect_query=m.effect_query, p.infuse_query=m.infuse_query, p.passive_query=m.passive_query, p.ultima_query=m.ultima_query, p.price=m.price, p.dmg=m.dmg, p.stealth=m.stealth, p.evo=m.evo, p.aura=m.aura, p.craft_value=m.craft_value, p.illulink=m.illulink WHERE p.item_code='{code[0]}';")

        await ctx.send(":white_check_mark:")

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    @checks.check_author()
    async def mobuda(self, ctx, *args):

        codes = await self.client.quefe(f"SELECT DISTINCT mob_code FROM model_mob;", type='all')

        for code in codes:
            await self.client._cursor.execute(f"UPDATE environ_mob e INNER JOIN model_mob m ON m.mob_code='{code[0]}' SET e.name=m.name, e.description=m.description, e.lp=m.lp, e.str=m.str, e.chain=m.chain, e.speed=m.speed, e.au_FLAME=m.au_FLAME, e.au_ICE=m.au_ICE, e.au_HOLY=m.au_HOLY, e.au_DARK=m.au_DARK, e.effect=m.effect, e.rewards=m.rewards, e.illulink=m.illulink WHERE e.mob_code='{code[0]}';")

        await ctx.send(":white_check_mark:")


def setup(client):
    client.add_cog(avaAdmin(client))
