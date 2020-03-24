import json
from functools import partial
from io import BytesIO
from datetime import datetime
import os
import sys
import asyncio

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors
import pymysql.err as mysqlError
import psutil

from utils import checks



class avaAdmin(commands.Cog):
    def __init__(self, client):
        from .avaTools import avaTools
        from .avaUtils import avaUtils

        self.client = client

        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)

        print("|| Admin --- Ready!")



    # ================== EVENTS ==================

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     print("|| Admin --- Ready!")

    #@commands.command(pass_context=True)
    #@checks.check_author()
    #async def milestime(self, ctx):
    #    self.client.STONE = datetime.now()
    #    self.data_updating()



    # ================== SYSTEM WIDE ==================
    @commands.command()
    @checks.check_author()
    async def user_block(self, ctx, *args):
        try: self.client.ignore_list.append(ctx.message.mentions[0])
        except IndexError: return

        await ctx.send(":white_check_mark:")

    @commands.command()
    @checks.check_author()
    async def fetch_invite(self, ctx, *args):
        cns = self.client.get_guild(int(args[0])).channels
        for c in cns:
            try:
                ivi = await c.create_invite(max_uses=2)
                await ctx.send(ivi)
                return
            except discordErrors.NotFound: pass
            except discordErrors.Forbidden: pass
        await ctx.send(":x: Unable to create invitation.")



    # ================== GAME MANAGER ==================
    # MEGA
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

    # UDA
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
            await self.client._cursor.execute(f"UPDATE environ_mob e INNER JOIN model_mob m ON m.mob_code='{code[0]}' SET e.name=m.name, e.description=m.description, e.lp=m.lp, e.str=m.str, e.chain=m.chain, e.speed=m.speed, e.au_FLAME=m.au_FLAME, e.au_ICE=m.au_ICE, e.au_HOLY=m.au_HOLY, e.au_DARK=m.au_DARK, e.effect=m.effect, e.illulink=m.illulink WHERE e.mob_code='{code[0]}';")

        await ctx.send(":white_check_mark:")

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    @checks.check_author()
    async def world_rebuild(self, ctx, *args):
        try:
            if args[0] == 'truncate': truncate = True
            else: truncate = False
        except IndexError: truncate = False

        # TRUNCATE
        if truncate: await self.client._cursor.execute("TRUNCATE environ_mob;")

        await self.tools.world_built()

        await ctx.send(":white_check_mark:")

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    @checks.check_author()
    async def world_build(self, ctx, *args):
        await self.tools.world_built()
        await ctx.send(":white_check_mark:")

    # MISC
    @commands.command()
    @checks.check_author()
    async def view_item(self, ctx, *args):

        item_code, name, description, tags, weight, defend, multiplier, strr, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, aura, illulink, price = await self.client.quefe(f"""SELECT item_code, name, description, tags, weight, defend, multiplier, str, intt, sta, speed, round, accuracy_randomness, accuracy_range, range_min, range_max, firing_rate, dmg, stealth, aura, illulink, price FROM pi_inventory WHERE item_id='{args[0]}';""")

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



    # ================== SYS MANIP ==================

    @commands.command()
    @checks.check_author()
    async def megasql(self, ctx, *, args):
        if str(ctx.author.id) != '214128381762076672': await ctx.send("SHOO SHOO!"); return
        ret = await self.client._cursor.execute(args)
        await ctx.send(ret)

    @commands.command()
    @checks.check_author()
    async def megareload(self, ctx, *args):
        temp = []
        name = ''
        try:
            for n in args[0].split('.'):
                if n == 'c': temp.append('cogs'); continue
                elif n == 'a': temp.append('avasoul_pack'); continue
                temp.append(n)
            name = '.'.join(temp)
        except IndexError: await ctx.send(":x: Missing cog's name"); return

        self.client.reload_extension(name)
        
        # Prep =====================
        cog = self.client.get_cog(name.split('.')[-1])
        try: await cog.reloadSetup()
        except AttributeError: pass

        await ctx.send(":white_check_mark:")

    @commands.command()
    @checks.check_author()
    async def megarecache(self, ctx, *args):
        """
            Use the exact name of the database (model_npc, etc.)
            In order to use this in a cog, that cog must have:
                - <cacheMethod> dict
                - a cache function correspond to a DBC's name in the <cacheMethod> dict.    (e.g. {'model_NPC': self.cacheNPC})
                - a <cacheAll> function
            For example, please refer to cogs.avasoul_pack.avaNPC
        """

        temp = []
        name = ''
        try:
            for n in args[0].split('.'):
                if n == 'c': temp.append('cogs'); continue
                elif n == 'a': temp.append('avasoul_pack'); continue
                temp.append(n)
            name = '.'.join(temp)
        except IndexError: await ctx.send(":x: Missing cog's name (Note: No `c.a`, only `name` (e.g. `avaPersonal`, NOT `c.a.avaPersonal`))"); return

        cog = self.client.get_cog(name)
        print(name, cog)
        try:
            if args[1] == 'all':
                await cog.cacheAll()
            else:
                await cog.cacheMethod[args[1]]()
        except AttributeError: await ctx.send(":x: Cog not found. (Note: No `c.a`, only `name` (e.g. `avaPersonal`, NOT `c.a.avaPersonal`))"); return
        except IndexError: await ctx.send(":x: Missing database name"); return
        except KeyError: await ctx.send(":x: DB not found"); return
        # except AttributeError: await ctx.send(":x: Unknown cog"); return

        await ctx.send(":white_check_mark:")

    @commands.command()
    @checks.check_author()
    async def megarestart(self, ctx, *args):
        await ctx.send(f"<a:dukwalk:589872260651679746> **Okai!**")
        os.system("python C:/Users/DELL/Desktop/bot_cli/aaaa.py")
        exit()
        # await client.logout()

    @commands.command()
    @checks.check_author()
    async def leave_guild(self, ctx):
        await ctx.send("Okay.......")
        await ctx.guild.leave()

    @commands.command()
    @checks.check_author()
    async def shutdown(self, ctx):
        await ctx.send(f":wave: Bot's successfully shut down by {ctx.message.author}!")
        exit()



    # ================= MISC ====================
    @commands.command()
    @checks.check_author()
    async def statas(self, ctx, *args):
        mem = psutil.virtual_memory()

        temb = discord.Embed(title=f"<a:ramspin:629918889496805376> {self.bytes2human(mem.used)}/{self.bytes2human(mem.total)} ({round(mem.used/mem.total*100)}%)", colour = discord.Colour(0xB1F1FA))

        await ctx.send(embed=temb)

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

    @commands.command()
    @checks.check_author()
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
    async def delele(self, ctx, *args):
        """Delete message"""
        try:
            msg = await ctx.channel.fetch_message(int(args[0]))
            await msg.delete()
        # E: Invalid args
        except ValueError: await ctx.send(":warning: Invalid **`message id`**"); return
        # E: Msg not found
        except discordErrors.NotFound: await ctx.send(":warning: Message not found!"); return
        # E: No permission
        except discordErrors.Forbidden: await ctx.send("No you can't <:fufu:508437298808094742>"); return

    @commands.command()
    @checks.check_author()
    @commands.cooldown(1, 5, type=BucketType.guild)
    async def countline(self, ctx, *args):
        # dir_main = os.path.dirname(os.path.realpath(__file__))
        dirs = ['cogs', 'data']
        length = 0
        len_img = 0

        async def walkthrough(dir_path, pack, prev=''):
            """
                length, len_img = pack
            """
            dir_path = os.path.join(prev, dir_path)
            for f in os.listdir(dir_path):
                await asyncio.sleep(0)
                if '.' not in f and f not in dirs:
                    pack = await walkthrough(f, pack, prev=dir_path)

                if f.endswith(".py"):
                    with open(os.path.join(dir_path, f), 'r', encoding="utf8") as b:
                        lines = b.readlines()
                        pack[0] += len(lines)
                elif f.endswith('.png') or f.endswith('.jpg'):
                    pack[1] += 1
                else:
                    continue
            return pack

        for dir_path in dirs:
            pack = await walkthrough(dir_path, [length, len_img])
            length, len_img = tuple(pack)

        await ctx.send(f"> <a:ramspin:629918889496805376> **`{length}` lines** of code\n> <a:ramspin:629918889496805376> **`{len_img}`** image files!")

    @commands.command()
    @checks.check_author()
    async def command_info(self, ctx, *args):
        try:
            await ctx.send("> Located in `{}`".format(self.client.get_command(args[0]).cog.qualified_name))
        except IndexError: await ctx.send(":x: Missing command's name"); return
        except AttributeError: await ctx.send(":x: Command not found!"); return



    # ================== TOOLS ==================

    def bytes2human(self, n):
        # http://code.activestate.com/recipes/578019
        # >>> bytes2human(10000)
        # '9.8K'
        # >>> bytes2human(100001221)
        # '95.4M'
        symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
        prefix = {}
        for i, s in enumerate(symbols):
            prefix[s] = 1 << (i + 1) * 10
        for s in reversed(symbols):
            if n >= prefix[s]:
                value = float(n) / prefix[s]
                return '%.1f%s' % (value, s)
        return "%sB" % n

    def data_updating(self, update_kw):
        if update_kw == 'time_pack':
            time_pack = (self.client.STONE.year, self.client.STONE.month, self.client.STONE.day, self.client.STONE.hour, self.client.STONE.minute)
            with open('data/time.json', 'w') as f:
                json.dump(time_pack, f, indent=4)






def setup(client):
    client.add_cog(avaAdmin(client))
