from io import BytesIO
import asyncio
from functools import partial
from datetime import datetime, timedelta

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors
from PIL import Image, ImageDraw

from utils import checks



class avaPersonalUtils(commands.Cog):

    def __init__(self, client):
        from .avaTools import avaTools
        from .avaUtils import avaUtils

        self.client = client
        self.__cd_check = self.client.thp.cd_check
        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)

        print("|| PersonalUtils --- READY!")






# ================== EVENTS ==================

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     print("|| PersonalUtils --- READY!")






# ================== UTILS ==================

    @commands.command(aliases=['scan', 'rad'])
    @commands.cooldown(1, 30, type=BucketType.user)
    async def radar(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        cur_X, cur_Y = await self.client.quefe(f"SELECT cur_X, cur_Y FROM personal_info WHERE id='{str(ctx.message.author.id)}';")
        xrange = 0.1; yrange = 0.1
        try: 
            # Check if the range is off-limit
            # Get xrange
            if float(args[0])/1000 <= xrange: xrange = float(args[0])/1000
            # Get yrange
            try:
                if float(args[1])/1000 <= yrange: yrange = float(args[1])/1000
            except IndexError: yrange = xrange
        except (IndexError, ValueError): pass

        # Pacing through the required field
        coords_list = await self.client.quefe(f"SELECT cur_X, cur_Y FROM personal_info WHERE {cur_X - xrange}<=cur_X AND cur_X<={cur_X + xrange} AND {cur_Y - yrange}<=cur_Y AND cur_Y<={cur_Y + yrange};", type='all')
        coords_list = list(coords_list)
        # Remove user's own id
        coords_list.remove((cur_X, cur_Y))

        if not coords_list: await ctx.send(f":satellite: No sign of life in `{xrange*1000}m x {yrange*1000}m` square radius around us..."); return

        img = Image.new('RGB', (100, 100))
        cvs = ImageDraw.Draw(img)
        for coords in coords_list:
            real_X = (cur_X - coords[0])*1000
            if real_X >= 0: real_X = 50 - real_X
            else: real_X = 50 + real_X
            real_Y = (cur_Y - coords[1])*1000
            if real_Y >= 0: real_Y = 50 - real_Y
            else: real_Y = 50 + real_Y

            cvs.point([(real_X, real_Y), (real_X+1, real_Y), (real_X, real_Y+1), (real_X+1, real_Y+1)], fill=(156, 230, 133, 0))

        output_buffer = BytesIO()
        img.save(output_buffer, 'png')
        output_buffer.seek(0)

        f = discord.File(fp=output_buffer, filename='radar.png')
        #await ctx.send(file=)

        def makeembed(top, least, pages, currentpage):
            line = ""; swi = True

            for coords in coords_list[top:least]:
                if swi: line = line + f"\n╠ **`{coords[0]:.3f}`** · **`{coords[1]:.3f}`**"; swi = False
                else: line = line + f"⠀⠀⠀╠ **`{coords[0]:.3f}`** · **`{coords[1]:.3f}`**"; swi = True

            reembed = discord.Embed(title = f":satellite: [{xrange*2*1000}m x {yrange*2*1000}m] square radius, with user as the center", colour = discord.Colour(0x011C3A), description=line)
            reembed.set_footer(text=f"{len(coords_list)} detected | List {currentpage} of {pages}")
            reembed.set_thumbnail(url="attachment://radar.png")
            return reembed
            #else:
            #    await ctx.send("*Nothing but dust here...*")
        
        async def attachreaction(msg):
            await msg.add_reaction("\U000023ee")    #Top-left
            await msg.add_reaction("\U00002b05")    #Left
            await msg.add_reaction("\U000027a1")    #Right
            await msg.add_reaction("\U000023ed")    #Top-right

        pages = len(coords_list)//10
        if len(coords_list)%10 != 0: pages += 1
        currentpage = 1
        cursor = 0

        emli = []
        for _ in range(pages):
            myembed = makeembed(currentpage*10-10, currentpage*10, pages, currentpage)
            emli.append(myembed)
            currentpage += 1

        msg = await ctx.send(file=f, embed=emli[cursor], delete_after=30)
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
                return

    @commands.command(aliases=['tele'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def teleport(self, ctx, *args):
        try: cur_PLACE, cur_X, cur_Y, stats = await self.client.quefe(f"SELECT cur_PLACE, cur_X, cur_Y, stats FROM personal_info WHERE id='{ctx.author.id}';")
        except TypeError: return

        if stats == 'DEAD':
            if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        # COORD
        if not args:
            if cur_PLACE.startswith('region.') or cur_PLACE.startswith('area.'): r_name = await self.client.quefe(f"SELECT name FROM environ WHERE environ_code='{cur_PLACE}';")
            else: r_name = await self.client.quefe(f"SELECT name FROM pi_land WHERE land_code='{cur_PLACE}';")
            await ctx.send(f":map: **`{cur_X:.3f}`** · **`{cur_Y:.3f}`** · `{cur_PLACE}`|**{r_name[0]}** · {ctx.message.author.mention}", delete_after=5); return

        try:
            x = int(args[0])/1000; y = int(args[1])/1000

            # Region INFO
            if cur_PLACE.startswith('region.') or cur_PLACE.startswith('area.'): r_name, border_X, border_Y = await self.client.quefe(f"SELECT name, border_X, border_Y FROM environ WHERE environ_code='{cur_PLACE}'")
            # Land INFO
            elif cur_PLACE.startswith('land.'):
                try: r_name, border_X, border_Y = await self.client.quefe(f"SELECT name, border_X, border_Y FROM pi_land WHERE land_code='{cur_PLACE}'")
                except TypeError: await ctx.send(f"**`{cur_PLACE}`**... is no where to be found! <:yeee:636045188153868309>"); return
            else:
                await ctx.send(f"**`{cur_PLACE}`**... is no where to be found! <:yeee:636045188153868309>"); return

            if len(args[0]) <= 5 and len(args[1]) <= 5:
                if x > border_X: x = border_X
                if y > border_Y: y = border_Y
                if x < 0: x = -1
                if y < 0: y = -1
                # Check if <distance> is provided
                try:
                    distance = int(args[2])
                    prior_x = x; prior_y = y
                    x, y = await self.utils.distance_tools(cur_X, cur_Y, x, y, distance=distance, type='d-c')
                    # Coord check
                    if x > border_X: x = border_X
                    if y > border_Y: y = border_Y
                    if x < 0: x = 0
                    if y < 0: y = 0
                except (IndexError, ValueError): pass
                
                # Procede teleportation
                await self.tools.tele_procedure(cur_PLACE, str(ctx.author.id), x, y)

                # Informmmm :>
                try: await ctx.send(f"<:dual_cyan_arrow:543662534612353044>`{distance}m`<:dual_cyan_arrow:543662534612353044> toward **`{prior_x:.3f}`** · **`{prior_y:.3f}`**\n:map: Now you're at **`{x:.3f}`** · **`{y:.3f}`** · `{cur_PLACE}`|**{r_name}**!", delete_after=5)
                except NameError: await ctx.send(f":map: [{cur_X:.3f}, {cur_Y:.3f}] <:dual_cyan_arrow:543662534612353044> **`{x:.3f}`** · **`{y:.3f}`** · `{cur_PLACE}`|**{r_name}**!", delete_after=5)
            else: await ctx.send(f"<:osit:544356212846886924> Please use 5-digit coordinates!"); return
        except IndexError:
            #await ctx.send(f"<:osit:544356212846886924> Out of map's range!"); return
            # ONE coord only
            if args[0].isdigit():
                args = (args[0], args[0])
                try:
                    x = int(args[0])/1000; y = int(args[1])/1000

                    # Region INFO
                    if cur_PLACE.startswith('region.') or cur_PLACE.startswith('area.'): r_name, border_X, border_Y = await self.client.quefe(f"SELECT name, border_X, border_Y FROM environ WHERE environ_code='{cur_PLACE}'")
                    # Land INFO
                    elif cur_PLACE.startswith('land.'):
                        try: r_name, border_X, border_Y = await self.client.quefe(f"SELECT name, border_X, border_Y FROM pi_land WHERE land_code='{cur_PLACE}'")
                        except TypeError: await ctx.send(f"**`{cur_PLACE}`**... is no where to be found! <:yeee:636045188153868309>"); return
                    else: await ctx.send(f"**`{cur_PLACE}`**... is no where to be found! <:yeee:636045188153868309>"); return

                    if len(args[0]) <= 5 and len(args[1]) <= 5:
                        if x > border_X: x = border_X
                        if y > border_Y: y = border_Y
                        if x < 0: x = -1
                        if y < 0: y = -1
                        # Check if <distance> is provided
                        try:
                            distance = int(args[2])
                            prior_x = x; prior_y = y
                            x, y = await self.utils.distance_tools(cur_X, cur_Y, x, y, distance=distance, type='d-c')
                            # Coord check
                            if x > border_X: x = border_X
                            if y > border_Y: y = border_Y
                            if x < 0: x = 0
                            if y < 0: y = 0
                        except (IndexError, ValueError): pass
                        
                        # Procede teleportation
                        await self.tools.tele_procedure(cur_PLACE, str(ctx.author.id), x, y)

                        # Informmmm :>
                        try: await ctx.send(f"<:dual_cyan_arrow:543662534612353044>`{distance}m`<:dual_cyan_arrow:543662534612353044> toward **`{prior_x:.3f}`** · **`{prior_y:.3f}`**\n:map: Now you're at **`{x:.3f}`** · **`{y:.3f}`** · `{cur_PLACE}`|**{r_name}**!", delete_after=5)
                        except NameError: await ctx.send(f":map: [{cur_X:.3f}, {cur_Y:.3f}] <:dual_cyan_arrow:543662534612353044> **`{x:.3f}`** · **`{y:.3f}`** · `{cur_PLACE}`|**{r_name}**!", delete_after=5)
                    else: await ctx.send(f"<:osit:544356212846886924> Please use 5-digit coordinates!"); return
                except IndexError: await ctx.send(f"<:osit:544356212846886924> Out of map's range!"); return


        # PLACE
        except (KeyError, ValueError):
            if cur_PLACE == args[0]: await ctx.send("<:osit:544356212846886924> You're already there :|"); return

            # Get info of cur_PLACE
            if cur_PLACE.startswith('land.'): port, PB = await self.client.quefe(f"SELECT port, PB FROM pi_land WHERE land_code='{cur_PLACE}'")
            else: port, PB = await self.client.quefe(f"SELECT port, PB FROM environ WHERE environ_code='{cur_PLACE}'")
            # Prep info
            port = port.split(' | ')
            PB = [b.split(' - ') for b in PB.split(' | ')]

            # Destination info
            # REGION
            if args[0].startswith('region.'):
                # cur_PLACE port check
                if 'alre' not in port and args[0] not in port: await ctx.send(f"<:yeee:636045188153868309> Unable to reach the destination from your current location."); return

                # cur_PLACE PB check
                for b in PB:
                    if not (cur_X >= float(b[0]) and cur_Y >= float(b[1]) and cur_X <= float(b[2]) and cur_Y <= float(b[3])):
                        await ctx.send(f"<:osit:544356212846886924> Please `teleport` to the nearest Peace Belt and try again."); return

                try: r_name, border_X, border_Y, pass_query, pass_note = await self.client.quefe(f"SELECT name, border_X, border_Y, pass_query, pass_note FROM environ WHERE environ_code='{args[0]}'")
                except TypeError: await ctx.send(f"**`{args[0]}`**... is no where to be found! <:yeee:636045188153868309>"); return
            # AREA
            elif args[0].startswith('area.'):
                # cur_PLACE port check
                if 'alar' not in port and args[0] not in port: await ctx.send(f"<:yeee:636045188153868309> Unable to reach the destination from your current location."); return

                try:
                    r_name, border_X, border_Y, pass_query, pass_note = await self.client.quefe(f"SELECT name, border_X, border_Y, pass_query, pass_note FROM environ WHERE environ_code='{args[0]}'")
                except TypeError: await ctx.send(f"**`{args[0]}`**... is no where to be found! <:yeee:636045188153868309>"); return
            # LAND
            else:
                # cur_PLACE port check
                if 'alre' not in port and args[0] not in port: await ctx.send(f"<:yeee:636045188153868309> Unable to reach the destination from your current location."); return

                # cur_PLACE PB check
                for b in PB:
                    if not (cur_X >= float(b[0]) and cur_Y >= float(b[1]) and cur_X <= float(b[2]) and cur_Y <= float(b[3])):
                        await ctx.send(f"<:osit:544356212846886924> Please `teleport` to the nearest Peace Belt and try again."); return

                try:
                    r_name, border_X, border_Y, pass_query, pass_note = await self.client.quefe(f"SELECT name, border_X, border_Y, pass_query, pass_note FROM pi_land WHERE land_code='{args[0]}'")
                except TypeError: await ctx.send(f"**`{args[0]}`**... is no where to be found! <:yeee:636045188153868309>"); return

            # Destination's pass check
            if pass_query:
                if await self.client._cursor.execute(pass_query.replace('user_id_here', str(ctx.author.id)).replace('cur_X_here', str(cur_X)).replace('cur_Y_here', str(cur_Y)).replace('cur_PLACE_here', str(cur_PLACE))) == 0:
                    await ctx.send(f"<:osit:544356212846886924> Condition of destination is not met!\n>>> ⠀{pass_note}"); return


            await self.client._cursor.execute(f"UPDATE personal_info SET cur_PLACE='{args[0]}' WHERE id='{ctx.author.id}';")
            await ctx.send(f":round_pushpin: Successfully move to `{args[0]}`|**{r_name}**!", delete_after=5); return

    @commands.command(aliases=['md'])
    async def measure_distance(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        cur_X, cur_Y = await self.client.quefe(f"SELECT cur_X, cur_Y FROM personal_info WHERE id='{str(ctx.message.author.id)}';")

        try:
            distance = await self.utils.distance_tools(cur_X, cur_Y, int(args[0])/1000, int(args[1])/1000)
            await ctx.send(f":straight_ruler\n::triangular_ruler: Result: **`{distance}m`**")
        except IndexError: pass

    @commands.command()
    async def daily(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        # CAKE
        if not args:
            cmd_tag = 'daily'
            if not await self.__cd_check(ctx.message, cmd_tag, f"<:fufu:605255050289348620> Oops. It's not your birthday yet, **{ctx.author.name}**."): return

            await self.client._cursor.execute(f"SELECT func_ig_reward('{ctx.author.id}', 'ig77', 1);")
            await ctx.send(f":cake: Happy birthday! Here's a `ig77`|**Cake**!")
            await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.set, f'{cmd_tag}{ctx.author.id}', 'working', ex=82800, nx=True))

        # QUEST
        elif args[0] == 'quest':
            cmd_tag = 'dailyquest'
            if not await self.__cd_check(ctx.message, cmd_tag, f"<:fufu:605255050289348620> Once a day, **{ctx.author.name}**. Don't push yourself too hard ~!"): return
            
            # Get personal guild info
            try: guild_code, rank = await self.client.quefe(f"SELECT guild_code, rank FROM pi_guild WHERE user_id='{ctx.author.id}';")
            except TypeError: await ctx.send("<:osit:544356212846886924> You haven't joined any guild yet!"); return

            current_place = await self.client.quefe(f"SELECT cur_PLACE, money FROM personal_info WHERE id='{ctx.author.id}'"); current_place = current_place[0]

            sample = {'iron': 3, 'bronze': 4, 'silver': 5, 'gold': 6, 'adamantite': 8, 'mithryl': 10}
            if await self.client._cursor.execute(f"SELECT user_id FROM pi_quests WHERE user_id='{ctx.author.id}' AND stats in ('ONGOING', 'FULL');") >= sample[rank]: await ctx.send(f"<:osit:544356212846886924> You cannot handle more than **{sample[rank]}** quests at a time")

            # QUEST info get
            try: quest_code, quest_line, quest_name, snap_query, quest_sample, eval_meth, effect_query, reward_query, penalty_query, duration = await self.client.quefe(f"SELECT quest_code, quest_line, name, snap_query, sample, eval_meth, effect_query, reward_query, penalty_query, duration FROM model_quest WHERE region='{current_place}' AND quest_line='daily' ORDER BY RAND() LIMIT 1;")
            except TypeError: await ctx.send(f":european_castle: No daily quest available in current region."); return

            snap_query = snap_query.replace('user_id_here', f'{ctx.author.id}')
            effect_query = effect_query.replace('user_id_here', f'{ctx.author.id}')            

            temp = snap_query.split(' || ')
            temp2 = []
            for que in temp:
                a = await self.client.quefe(que)
                try: temp2.append(str(a[0]))
                except TypeError: temp2.append('0')
            snapshot = ' || '.join(temp2)


            # End_point calc from duration
            if duration:
                end_point = datetime.now() + timedelta(seconds=duration)
                end_point = end_point.strftime('%Y-%m-%d %H:%M:%S')
            else: end_point = ''


            await self.client._cursor.execute(f"""INSERT INTO pi_quests VALUES (0, '{quest_code}', '{ctx.author.id}', "{snap_query}", '{snapshot}', '{quest_sample}', '{eval_meth}', "{effect_query}", "{reward_query}", "{penalty_query}", '{end_point}', 'FULL'); {effect_query}""")
            
            await ctx.send(f":white_check_mark: {quest_line.capitalize()} quest `{quest_code}`|**{quest_name}** accepted! Use `quest` to check your progress.")
            await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.set, f'{cmd_tag}{ctx.author.id}', 'dailyquest', ex=duration, nx=True))

    @commands.command()
    @commands.cooldown(1, 360, type=BucketType.user)
    async def delete(self, ctx, *args):
        # Get party_id
        my_party = await self.client.quefe(f"SELECT party_id FROM pi_party WHERE user_id='{ctx.author.id}' AND role='LEADER';", type='all')
        if my_party: my_party = [a[0] for a in my_party]
        else: my_party = ['ansna']

        query = f"""
                    DELETE FROM cosmetic_preset WHERE user_id='{ctx.author.id}';|||
                    DELETE FROM pi_arts WHERE user_id='{ctx.author.id}';|||
                    DELETE FROM pi_avatars WHERE user_id='{ctx.author.id}';|||
                    DELETE FROM pi_backgrounds WHERE user_id='{ctx.author.id}';|||
                    DELETE FROM pi_fonts WHERE user_id='{ctx.author.id}';|||
                    DELETE FROM pi_bank WHERE user_id='{ctx.author.id}';|||
                    DELETE FROM pi_deck WHERE user_id='{ctx.author.id}';|||
                    DELETE FROM pi_degrees WHERE user_id='{ctx.author.id}';|||
                    DELETE FROM pi_dungeoncheckpoint WHERE user_id='{ctx.author.id}';|||
                    DELETE FROM pi_equipment WHERE user_id='{ctx.author.id}';|||
                    DELETE FROM environ_party WHERE party_id = (SELECT party_id FROM pi_party WHERE user_id='{ctx.author.id}' AND role='LEADER');|||
                    DELETE FROM pi_party WHERE party_id IN ('{"' '".join(my_party[0])}') OR (user_id='{ctx.author.id}' AND role='MEMBER');|||
                    DELETE FROM pi_guild WHERE user_id='{ctx.author.id}';|||
                    DELETE FROM pi_hero WHERE user_id='{ctx.author.id}';|||
                    DELETE FROM pi_hunt WHERE user_id='{ctx.author.id}';|||
                    DELETE FROM pi_inventory WHERE user_id='{ctx.author.id}';|||
                    DELETE FROM pi_order WHERE land_code IN (SELECT land_code FROM pi_land WHERE user_id='{ctx.author.id}');|||
                    DELETE FROM pi_tax WHERE land_code IN (SELECT land_code FROM pi_land WHERE user_id='{ctx.author.id}');|||
                    DELETE FROM pi_unit WHERE land_code IN (SELECT land_code FROM pi_land WHERE user_id='{ctx.author.id}');|||
                    DELETE FROM pi_land WHERE user_id='{ctx.author.id}';|||
                    DELETE FROM pi_mobs_collection WHERE user_id='{ctx.author.id}';|||
                    DELETE FROM pi_quest WHERE user_id='{ctx.author.id}';|||
                    DELETE FROM pi_quests WHERE user_id='{ctx.author.id}';|||
                    DELETE FROM pi_relationship WHERE user_id='{ctx.author.id}';|||
                    DELETE FROM pi_rest WHERE user_id='{ctx.author.id}';
                """
        
        await ctx.send(f"<a:RingingBell:559282950190006282> {ctx.author.name}, lease type `deletion confirm` to proceed.")

        try: await self.client.wait_for('message', timeout=15, check=lambda m: m.channel == ctx.channel and m.author == ctx.author and m.content.lower() == 'deletion confirm')
        except asyncio.TimeoutError: await ctx.send(f"<:osit:544356212846886924> Requested time-out!"); return

        self.client.ignore_list.append(ctx.author.id)
        await ctx.send(f":white_check_mark: Deletion may take a while... Sayonara, {ctx.author.name}, thank you for your journey!")

        for q in query.split('|||'):
            await asyncio.sleep(1)
            try: await self.client._cursor.execute(q)
            except:
                await self.client.owner.send(q)
                self.client.ignore_list.remove(ctx.author.id)
                return

        # PERSONAL_INFO
        await self.client._cursor.execute(f"""
            UPDATE personal_info SET partner='n/a' WHERE partner='{ctx.author.id}';
            DELETE FROM personal_info WHERE id='{ctx.author.id}';
                                            """)

        self.client.ignore_list.remove(ctx.author.id)

    @commands.command()
    @commands.cooldown(1, 20, type=BucketType.user)
    async def mail(self, ctx, *args):
        pi = await self.client.DBC['dbcf']['dbcf_getPersonalInfo'](self, str(ctx.author.id))
        search_kw = ''
        if not pi: await ctx.send(f"You don't have a *character*, **{ctx.author.name}**. You can use command `incarnate` to create one, and `tutorial` for... tutorial <:yeee:636045188153868309>")

        try:
            if args[0].isdigit(): line = await self.mail_widget(ctx, pi, 'read', args[0:10])
            elif len(args) == 1: search_kw = args[0]
            else: line = await self.mail_widget(ctx, pi, args[0], args[1:11])
            # Read
            if isinstance(line, discord.embeds.Embed): await ctx.send(embed=line)
            elif line != False: await ctx.send(f":envelope: Done{line}!")
        except IndexError: pass

        # NORMAL ==============================
        # Prep item     ||     (ordera, sender, content)
        read_item, unread_item, pin_item, trash_item = await self.mail_dataGet(pi, search_kw=search_kw)

        # Makeembeds
        def makeembed_read(items, top, least, pages, currentpage):
            line = ''; count = 1; field_count = 0
            reembed = discord.Embed(title=f':mailbox_with_no_mail: READ MAIL', description=line, colour = discord.Colour(0xA37C05))

            for item in items[top:least]:
                line = line + f"""{item[0]}. {item[1]}:: {item[2][:12]}\n"""
                if count == 10:
                    if not field_count:
                        line2 = f"『Total』{len(items)}/200 mails"
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
                    line2 = f"『Total』{len(items)}/200 mails"
                else:
                    line2 = f"『Page』{currentpage}/{pages}"
                reembed.add_field(name=line2, value=f"""```Asciidoc
{line}```""")
                if not field_count: reembed.add_field(name=f"『Page』{currentpage}/{pages}", value=f"""```⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀```""")
            return reembed

        def makeembed_unread(items, top, least, pages, currentpage):
            line = ''; count = 1; field_count = 0
            reembed = discord.Embed(title=f':mailbox_with_mail: UNREAD MAIL', description=line, colour = discord.Colour(0xA37C05))

            for item in items[top:least]:
                line = line + f"""{item[0]}. {item[1]}:: {item[2][:12]}\n"""
                if count == 10:
                    if not field_count:
                        line2 = f"『Total』{len(items)}/100 mails"
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
                    line2 = f"『Total』{len(items)}/100 mails"
                else:
                    line2 = f"『Page』{currentpage}/{pages}"
                reembed.add_field(name=line2, value=f"""```Asciidoc
{line}```""")
                if not field_count: reembed.add_field(name=f"『Page』{currentpage}/{pages}", value=f"""```⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀```""")
            return reembed

        def makeembed_pin(items, top, least, pages, currentpage):
            line = ''; count = 1; field_count = 0
            reembed = discord.Embed(title=f':pushpin: PINNED MAIL', description=line, colour = discord.Colour(0xA37C05))

            for item in items[top:least]:
                line = line + f"""{item[0]}. {item[1]}:: {item[2][:12]}\n"""
                if count == 10:
                    if not field_count:
                        line2 = f"『Total』{len(items)}/50 mails"
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
                    line2 = f"『Total』{len(items)}/50 mails"
                else:
                    line2 = f"『Page』{currentpage}/{pages}"
                reembed.add_field(name=line2, value=f"""```Asciidoc
{line}```""")
                if not field_count: reembed.add_field(name=f"『Page』{currentpage}/{pages}", value=f"""```⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀```""")
            return reembed

        def makeembed_trash(items, top, least, pages, currentpage):
            line = ''; count = 1; field_count = 0
            reembed = discord.Embed(title=f':wastebasket: TRASH MAIL', description=line, colour = discord.Colour(0xA37C05))

            for item in items[top:least]:
                line = line + f"""{item[0]}. {item[1]}:: {item[2][:12]}\n"""
                if count == 10:
                    if not field_count:
                        line2 = f"『Total』{len(items)}/100 mails"
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
                    line2 = f"『Total』{len(items)}/100 mails"
                else:
                    line2 = f"『Page』{currentpage}/{pages}"
                reembed.add_field(name=line2, value=f"""```Asciidoc
{line}```""")
                if not field_count: reembed.add_field(name=f"『Page』{currentpage}/{pages}", value=f"""```⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀```""")
            return reembed

        def makeembed_UI(items, top, least, pages, currentpage):
            """
                user_name, len_of_unreadMail, tag_DM
            """
            line = ''

            line += f":bookmark: DM-tag `{'` `'.join(items[2])}`"
            if items[1]: line += f"\n:envelope_with_arrow: You have *{items[1]}* new mails!"
            reembed = discord.Embed(title=f":mailbox_closed: {items[0]}'s mailbox", description=line, colour = discord.Colour(0xA37C05))
            return reembed

        resp = None
        while True:
            if not resp: resp = await self.tools.pagiMainMulti(ctx, ((makeembed_UI, (ctx.author.name, len(pi.mailBox.unreadMail), pi.mailBox.tag), 1, False, None), (makeembed_unread, unread_item, 20, False, None), (makeembed_read, read_item, 20, False, None), (makeembed_pin, pin_item, 10, False, None), (makeembed_trash, trash_item, 20, False, None)), timeout=60, extra_button=["\U000023ee", "\U00002b05", "\U00002195", "\U000027a1", "\U000023ed", "\U0001f5d1", "\U0000267b", "\U0001f441"], extra_resp={"\U0001f5d1": 'delete', "\U0000267b": 'recover', "\U0001f441": 'read'})
            else: resp = await self.tools.pagiMainMulti(ctx, ((makeembed_UI, (ctx.author.name, len(pi.mailBox.unreadMail), pi.mailBox.tag), 1, False, None), (makeembed_unread, unread_item, 20, False, None), (makeembed_read, read_item, 20, False, None), (makeembed_pin, pin_item, 10, False, None), (makeembed_trash, trash_item, 20, False, None)), timeout=60, extra_button=["\U000023ee", "\U00002b05", "\U00002195", "\U000027a1", "\U000023ed", "\U0001f5d1", "\U0000267b", "\U0001f441"], extra_resp={"\U0001f5d1": 'delete', "\U0000267b": 'recover', "\U0001f441": 'read'}, emli=resp[1][0], cursor=resp[1][3], emli_cursor=resp[2][0])
            try:
                line = await self.mail_widget(ctx, pi, resp[2][1], None)
                # Read
                if isinstance(line, discord.embeds.Embed):
                    await ctx.send(embed=line)
                elif line != False: await ctx.send(f":envelope: Done{line}!")
                read_item, unread_item, pin_item, trash_item = await self.mail_dataGet(pi, search_kw=search_kw)
            except ValueError: continue
            except TypeError: return

            await resp[0].delete()






# ================== TOOLS ==================

    async def mail_widget(self, ctx, pi, name, value):
        line = ''

        if not value:
            await ctx.send(f"<a:RingingBell:559282950190006282> Please type in mail's IDs to {name} ||(split by single space)||:", delete_after=20)
            try:
                value = await self.client.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=20)
                value = value.content.split(' ')
            except asyncio.TimeoutError: return False

        if name == 'read':
            # Read
            if len(value) == 1:
                try: m = await pi.mailBox.getMail(self.client, value[0])
                except KeyError: return False
                return discord.Embed(description=f"""
                            ```Asciidoc
From:: {m.sender}```{m.content}\n||Tag: `{'` `'.join(m.tag)}`||
                                                    """, colour = discord.Colour(0xA37C05))
            # Mark as read
            else:
                f = await pi.mailBox.setRead(self.client, ctx.author.id, value)
                if f: line = f", except mail id. `{'`, `'.join(f)}`"
                return line
        elif name == 'delete':
            f = await pi.mailBox.moveToTrash(self.client, ctx.author.id, value)
            if f: line = f", except mail id. `{'`, `'.join(f)}`"
            return line
        elif name == 'recover':
            f = await pi.mailBox.recoverTrash(self.client, ctx.author.id, value)
            if f: line = f", except mail id. `{'`, `'.join(f)}`"
            return line
        elif name == 'pin':
            f = await pi.mailBox.moveToPin(self.client, ctx.author.id, value)
            if f: line = f", except mail id. `{'`, `'.join(f)}`"
            return line
        else: return (name,) + value

    async def mail_dataGet(self, pi, search_kw=''):
        read_item = []; unread_item = [] ; pin_item = []; trash_item = []
        for k in pi.mailBox.rmEntry:
            await asyncio.sleep(0)
            v = pi.mailBox.readMail[k]
            if search_kw and search_kw not in self.client.DBC['model_mail'][v]: continue
            read_item.append((k, self.client.DBC['model_mail'][v].sender, self.client.DBC['model_mail'][v].content))
        for k in pi.mailBox.urmEntry:
            await asyncio.sleep(0)
            v = pi.mailBox.unreadMail[k]
            if search_kw and search_kw not in self.client.DBC['model_mail'][v]: continue
            unread_item.append((k, self.client.DBC['model_mail'][v].sender, self.client.DBC['model_mail'][v].content))
        for k in pi.mailBox.pEntry:
            await asyncio.sleep(0)
            v = pi.mailBox.pin[k]
            if search_kw and search_kw not in self.client.DBC['model_mail'][v]: continue
            pin_item.append((k, self.client.DBC['model_mail'][v].sender, self.client.DBC['model_mail'][v].content))
        for k in pi.mailBox.tEntry:
            await asyncio.sleep(0)
            v = pi.mailBox.trash[k]
            if search_kw and search_kw not in self.client.DBC['model_mail'][v]: continue
            trash_item.append((k, self.client.DBC['model_mail'][v].sender, self.client.DBC['model_mail'][v].content))

        return read_item, unread_item, pin_item, trash_item





# ================== ADMIN ==================

    @commands.command()
    @checks.check_author()
    async def sendmail(self, ctx, *args):
        """
            0: user_id
            1: mail_code
        """

        try:
            await self.client.DBC['dbcf']['dbcf_sendMail'](args[0], args[1])
        except discordErrors.Forbidden: return
        except KeyError:
            await ctx.send(":x: Mail_code not found!"); return
        except AttributeError:
            await ctx.send(":x: User not found!"); return



def setup(client):
    client.add_cog(avaPersonalUtils(client))
