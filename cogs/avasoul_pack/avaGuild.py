import random
import asyncio
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors
import pymysql.err as mysqlError

from .avaTools import avaTools
from .avaUtils import avaUtils



class avaGuild(commands.Cog):

    def __init__(self, client):
        self.client = client

        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)

        self.guild_rank = {'iron': ['bronze', 20],
                            'bronze': ['silver', 100],
                            'silver': ['gold', 220],
                            'gold': ['adamantite', 490], 
                            'adamantite': ['mithryl', 755], 
                            'mithryl': ['n/a', 980]}

        self.guild_rank_image = {'iron': 'https://imgur.com/8Udallk.png',
                                'bronze': 'https://imgur.com/9k4fYPm.png',
                                'silver': 'https://imgur.com/eVlDR59.png',
                                'gold': 'https://imgur.com/E7d64Rh.png',
                                'adamantite': 'https://imgur.com/86OFaqJ.png',
                                'mithryl': 'https://imgur.com/IybhU0l.png'}

        print("|| Guild Systems ---- READY!")



# ================== EVENTS ==================

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     print("|| Guild Systems ---- READY!")



# ================== GUILD ==================

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def guild(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        await self.tools.ava_scan(ctx.message)

        # DISPLAY guild
        if not args:
            # GET personal guild info
            try: guild_code, rank, total_quests = await self.client.quefe(f"SELECT guild_code, rank, total_quests FROM pi_guild WHERE user_id='{ctx.author.id}' AND guild_code<>'n/a';")
            except TypeError: await ctx.send("<:osit:544356212846886924> You haven't joined any guilds yet! Simply use command `guild join` to a local guild."); return

            # GE guild's info
            guild_name, description, region = await self.client.quefe(f"SELECT guild_name, description, region FROM model_guild WHERE guild_code='{guild_code}';")

            temb = discord.Embed(description=f"""```http
    {description}```""", colour=0x36393E)
            temb.set_author(name="―――――――――――――――――――――――――――――――――――", icon_url=ctx.author.avatar_url)
            temb.add_field(name=f"<:guild_p:619743808959283201> `{guild_code}`|**{guild_name}**", value=f"╟`Region` · **{region}**", inline=True)
            temb.add_field(name=f":bookmark: {ctx.author.name}'s info", value=f"╟`Quests done` · **{total_quests}**", inline=True)
            temb.set_thumbnail(url=self.guild_rank_image[rank])
            await ctx.send(embed=temb)
            return

        if args[0] == 'join':
            # GET personal info
            current_place, money = await self.client.quefe(f"SELECT cur_PLACE, money FROM personal_info WHERE id='{ctx.author.id}'")

            # GET personal guild info
            p_guild_code = await self.client.quefe(f"SELECT guild_code FROM pi_guild WHERE user_id='{ctx.author.id}';"); p_guild_code = p_guild_code[0]

            # GET guild info
            try:
                # guild_code given..
                try: guild_code, guild_name, entry_fee = await self.client.quefe(f"SELECT guild_code, guild_name, entry_fee FROM model_guild WHERE guild_code='{args[1]}' AND region='{current_place}';")
                # .. or not, then search by region of currentplace
                except IndexError: guild_code, guild_name, entry_fee = await self.client.quefe(f"SELECT guild_code, guild_name, entry_fee FROM model_guild WHERE region='{current_place}';")
            # E: Guild not found
            except TypeError: await ctx.send("<:osit:544356212846886924> There aren't any guild available in your current region, it seems..."); return

            # Check if user's in the same guild
            if guild_code == p_guild_code:
                await ctx.send(f"<:osit:544356212846886924> You've already been in that guild, **{ctx.author.name}**!"); return
            # ... or in other guilds
            elif p_guild_code != 'n/a':
                await ctx.send(f"<:osit:544356212846886924> You've already been in another guild, **{ctx.author.name}**!"); return
            # ... jor just want to join
            else: cost = entry_fee

            await ctx.send(f":scales: **G.U.I.L.D** of `{current_place} | {guild_code}` :scales:\n------------------------------------------------\nJoining will require **<:36pxGold:548661444133126185>{cost}** as a deposit which will be returned when you leave guild if: \n· You don't have any bad records.\n· You're alive.\n· You leave the guild before joining others\n------------------------------------------------\n<a:RingingBell:559282950190006282> **Do you wish to proceed?** (key: `joining confirm` | timeout=20s)")
            try: await self.client.wait_for('message', timeout=20, check=lambda m: m.channel == ctx.channel and m.content == 'joining confirm' and m.author == ctx.author)           
            except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request timed out!"); return

            # Money check
            if money < cost: await ctx.send("<:osit:544356212846886924> Insufficient balance!"); return

            await self.client._cursor.execute(f"UPDATE personal_info SET money={money - cost} WHERE id='{ctx.author.id}';")
            await self.client._cursor.execute(f"UPDATE pi_guild SET guild_code='{guild_code}', deposit=deposit+{cost} WHERE user_id='{ctx.author.id}';")
            await ctx.send(f"<:guild_p:619743808959283201> Welcome, {ctx.message.author.mention}, to our big family all over Pralayr <:guild_p:619743808959283201>\nYou are no longer a lonely, nameless adventurer, but a member of `{current_place} | {guild_code}` guild, a part of **G.U.I.L.D**'s league. Please, newcomer, make yourself at home <3"); return

        elif args[0] == 'leave':
            # GET personal guild info
            try: guild_code, deposit, guild_name = await self.client.quefe(f"SELECT p.guild_code, p.deposit, m.guild_name FROM pi_guild p, model_guild m WHERE p.user_id='{ctx.author.id}' AND p.guild_code<>'n/a' AND m.guild_code=p.guild_code;")
            except TypeError: await ctx.send("<:osit:544356212846886924> You haven't joined any guild yet!"); return

            await ctx.send(f"<a:RingingBell:559282950190006282> {ctx.message.author.mention}, leaving `{guild_code}| {guild_name}` guild? (key: `leaving confirm` | timeout=5s)")
            try: await self.client.wait_for('message', timeout=5, check=lambda m: m.channel == ctx.channel and m.content == 'leaving confirm' and m.author == ctx.author)
            except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request timed out!"); return

            await self.client._cursor.execute(f"UPDATE personal_info SET money=money+{deposit} WHERE id='{ctx.author.id}';")
            await self.client._cursor.execute(f"UPDATE pi_guild SET guild_code='n/a', deposit=0 WHERE user_id='{ctx.author.id}';")
            await ctx.send(f":white_check_mark: Left guild. Deposit of **<:36pxGold:548661444133126185>{deposit}** has been returned"); return

    @commands.command(aliases=['q'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def quest(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        await self.tools.ava_scan(ctx.message)
        raw = list(args)

        name, rank = await self.client.quefe(f"SELECT guild_code, rank FROM pi_guild WHERE user_id='{ctx.author.id}';")

        try:
            if name == 'n/a':
                await ctx.send("<:osit:544356212846886924> You haven't joined any guilds yet!"); return
        except IndexError: await ctx.send("<:osit:544356212846886924> You haven't joined any guild yet! Simply use command `guild join` to a local guild."); return

        current_place = await self.client.quefe(f"SELECT cur_PLACE, money FROM personal_info WHERE id='{ctx.author.id}'"); current_place = current_place[0]

        try:
            if raw[0] == 'take':
                # If quest's id given, accept the quest
                try:
                    sample = {'iron': 3, 'bronze': 4, 'silver': 5, 'gold': 6, 'adamantite': 8, 'mithryl': 10}
                    if await self.client._cursor.execute(f"SELECT * FROM pi_quests WHERE user_id='{ctx.author.id}' AND quest_code='{raw[1]}';") >= 1:
                        await ctx.send("<:osit:544356212846886924> Quest has already been taken"); return
                    done_quests, qpool, qpool_guild = await self.client.quefe(f"SELECT pi_quest.`finished_quests`, pi_quest.`quest_pool`, model_guild.`quest_pool` FROM pi_quest, model_guild, pi_guild WHERE pi_quest.`user_id`='{ctx.author.id}' AND pi_guild.`user_id`=pi_quest.`user_id` AND model_guild.`guild_code`=pi_guild.`guild_code`;")
                    try: done_quests = self.finQuest_coder(done_quests)
                    except AttributeError: done_quests = []
                    try: qpool = qpool.split(' - ')
                    except AttributeError: qpool = []
                    try: qpool_guild = qpool_guild.split(' - ')
                    except AttributeError: qpool_guild = []
                    if raw[1] in done_quests: await ctx.send("<:osit:544356212846886924> Quest has already been finished."); return
                    elif raw[1] not in qpool and raw[1] not in qpool_guild: await ctx.send("<:osit:544356212846886924> Quest not found."); return
                    if await self.client._cursor.execute(f"SELECT user_id FROM pi_quests WHERE user_id='{ctx.author.id}' AND stats in ('ONGOING', 'FULL')") >= sample[rank]: await ctx.send(f"<:osit:544356212846886924> Your rank isn't high enough to handle more than **{sample[rank]}** quests at a time"); return

                    # QUEST info get
                    try: quest_code, quest_line, quest_name, snap_query, quest_sample, eval_meth, effect_query, reward_query, prerequisite, penalty_query, duration = await self.client.quefe(f"SELECT quest_code, quest_line, name, snap_query, sample, eval_meth, effect_query, reward_query, prerequisite, penalty_query, duration FROM model_quest WHERE quest_code='{raw[1]}' AND region='{current_place}' AND quest_line IN ('main', 'side', 'hidden');")
                    except TypeError: await ctx.send("<:osit:544356212846886924> Quest not found!"); return
                    try:
                        if await self.client._cursor.execute(prerequisite.replace('user_id_here', str(ctx.author.id))) == 0: await ctx.send("<:osit:544356212846886924> Prerequisite is not met!"); return
                    # E: Query's empty
                    except mysqlError.InternalError: pass
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
                    if duration != 0:
                        end_point = datetime.now() + timedelta(seconds=duration)
                        end_point = f"'{end_point.strftime('%Y-%m-%d %H:%M:%S')}'"
                    else: end_point = 'NULL'


                    await self.client._cursor.execute(f"""INSERT INTO pi_quests VALUES (0, '{quest_code}', '{ctx.author.id}', "{snap_query}", '{snapshot}', '{quest_sample}', '{eval_meth}', "{effect_query}", "{reward_query}", "{penalty_query}", {end_point}, 'FULL'); {effect_query}""")

                    await ctx.send(f":white_check_mark: {quest_line.capitalize()} quest `{raw[1]}`|**{quest_name}** accepted! Use `quest` to check your progress."); return
                # E: Quest's id not found
                except ValueError: await ctx.send("<:osit:544356212846886924> Quest not found"); return
                # E: Quest's id not given (and current_quest is also empty)
                except IndexError: await ctx.send(f"<:osit:544356212846886924> Please provide a quest code, which can be found in command `quests`."); return

            elif raw[0] == 'leave': 
                try:
                    try:
                        quest_code, penalty_query = await self.client.quefe(f"SELECT quest_code, penalty_query FROM pi_quests WHERE quest_id='{raw[1]}';")
                    except mysqlError.InternalError: await ctx.send("<:osit:544356212846886924> Invalid quest id"); return
                    region, quest_line, name = await self.client.quefe(f"SELECT region, quest_line, name FROM model_quest WHERE quest_code='{quest_code}';")
                    # Region check
                    if region != current_place and quest_line != 'DAILY': await ctx.send(f"<:guild_p:619743808959283201> You need to be in `{region}` in order to leave {quest_line} quest `{quest_code}`|**{name}**"); return
                except TypeError: await ctx.send("<:osit:544356212846886924> You have not taken this quest yet!"); return

                if await self.client._cursor.execute(f"DELETE FROM pi_quests WHERE user_id='{ctx.author.id}' AND quest_id={raw[1]} AND stats!='ONGOING'") == 0: await ctx.send(f"<:osit:544356212846886924> You cannot leave a completed quest"); return
                penalty_query = penalty_query.replace('user_id_here', str(ctx.author.id))
                if penalty_query: await self.client._cursor.execute(penalty_query)
                await ctx.send(f"<:guild_p:619743808959283201> Left {quest_line} quest `{quest_code}`|`{name}` (id.`{raw[1]}`)"); return

            elif raw[0] == 'claim':
                # Check if the quest is ONGOING     |      Get stuff too :>
                try: snapshot, snap_query, quest_sample, stats, eval_meth, reward_query, quest_line, quest_code, end_point = await self.client.quefe(f"SELECT snapshot, snap_query, sample, stats, eval_meth, reward_query, (SELECT quest_line FROM model_quest WHERE quest_code=pi_quests.quest_code), quest_code, end_point FROM pi_quests WHERE quest_id={raw[1]} AND user_id='{ctx.author.id}';")
                except (TypeError, mysqlError.InternalError): await ctx.send(f"<:osit:544356212846886924> Quest not found, **{ctx.author.name}**"); return
                snap_query = snap_query.replace('user_id_here', f'{ctx.author.id}')
                reward_query = reward_query.replace('user_id_here', f'{ctx.author.id}')

                # Duration check
                if end_point:
                    if datetime.now() > end_point: await ctx.send(f"<:guild_p:619743808959283201> The quest is expired, **{ctx.author.name}**!"); return

                if stats == 'DONE': await ctx.send("<:osit:544356212846886924> Main and side quests can only be done once."); return

                # Get current snapshot
                temp = snap_query.split(' || ')
                quest_sample = quest_sample.split(' || ')
                snapshot = snapshot.split(' || ')
                cur_snapshot = []
                for sque in temp:
                    a = await self.client.quefe(sque)
                    try: cur_snapshot.append(a[0])
                    except TypeError: cur_snapshot.append('0')

                # Evaluating
                if eval_meth == '>=':
                    for a, b, c in zip(cur_snapshot, snapshot, quest_sample):
                        if not (int(a) - int(b)) >= int(c): await ctx.send("<:guild_p:619743808959283201> The quest has not been fulfilled yet"); return
                elif eval_meth == '==':
                    for a, b, c in zip(cur_snapshot, snapshot, quest_sample):
                        # DIGIT
                        if c.isdigit():
                            if not (int(a) - int(b)) >= int(c): await ctx.send("<:guild_p:619743808959283201> The quest has not been fulfilled yet"); return
                        # CHAR
                        else:
                            if not a == c: await ctx.send("<:guild_p:619743808959283201> The quest has not been fulfilled yet"); return
                if eval_meth == '<=':
                    for a, b, c in zip(cur_snapshot, snapshot, quest_sample):
                        if not (int(a) - int(b)) <= int(c): await ctx.send("<:guild_p:619743808959283201> The quest has not been fulfilled yet"); return
                elif eval_meth == '>':
                    for a, c in zip(cur_snapshot, quest_sample):
                        if not int(a) >= int(c): await ctx.send("<:guild_p:619743808959283201> The quest has not been fulfilled yet"); return
                elif eval_meth == '<':
                    for a, c in zip(cur_snapshot, quest_sample):
                        if not int(a) <= int(c): await ctx.send("<:guild_p:619743808959283201> The quest has not been fulfilled yet"); return

                # Reward n Affect
                await self.client._cursor.execute(reward_query)
                # Increase pi_guild.total_quests by 1
                # Remove quest
                await self.client._cursor.execute(f"UPDATE pi_guild SET total_quests=total_quests+1 WHERE user_id='{ctx.author.id}'; DELETE FROM pi_quests WHERE user_id='{ctx.author.id}' AND quest_id={raw[1]};")
                # Update finished_quest in pi_quest. If not exist, create one
                fnqs = await self.client.quefe(f"SELECT finished_quests FROM pi_quest WHERE user_id='{ctx.author.id}' AND region='{current_place}';")
                try:
                    fnqs = self.finQuest_coder(fnqs)
                    try:
                        fnqs[quest_code] = int(fnqs[quest_code]) + 1
                    except KeyError:
                        fnqs[quest_code] = 1
                    await self.client._cursor.execute(f"UPDATE pi_quest SET finished_quests='{self.finQuest_coder(fnqs ,decode=False)}' WHERE user_id='{ctx.author.id}' AND region='{current_place}';")
                except AttributeError:
                    await self.client._cursor.execute(f"INSERT INTO pi_quest VALUE (0, '{ctx.author.id}', '{current_place}', '', '{quest_code} | 1');")


                """
                # Remove if daily, else keep
                #if quest_line == 'DAILY': 
                #else: await self.client._cursor.execute(f"UPDATE pi_quests SET stats='DONE' WHERE user_id='{ctx.author.id}' AND quest_id={raw[1]};")
                """
                # Inform
                await ctx.send(f"<:guild_p:619743808959283201> **Quest completed!**. **{ctx.author.name}**, may the Olds look upon you...")
                # Ranking check
                if await self.client._cursor.execute(f"UPDATE pi_guild SET rank='{self.guild_rank[rank][0]}' WHERE user_id='{ctx.author.id}' AND total_quests>={self.guild_rank[rank][1]};") == 1:
                    await ctx.send(f":beginner: Congrats, {ctx.message.author.mention}! You've been promoted to **{self.guild_rank[rank][0].upper()}**!")                         

        except IndexError:
            bundle = await self.client.quefe(f"SELECT quest_id, quest_code, snap_query, snapshot, sample, eval_meth, end_point FROM pi_quests WHERE user_id='{ctx.author.id}' AND stats IN ('ONGOING', 'FULL');", type='all')
            # ONGOING quest check
            if not bundle: await ctx.send(f"<:guild_p:619743808959283201> You have currently no active quest, **{ctx.author.name}**. Check for some in command `quests`!"); return
            bundle2 = []
            for pack in bundle:
                tempbu = await self.client.quefe(f"SELECT name, description, quest_line, description FROM model_quest WHERE quest_code='{pack[1]}';", type='all')
                bundle2.append(tempbu[0])

            async def makeembed(bbb, top, least, pages, currentpage):
                bundle, bundle2 = bbb
                temb = discord.Embed(colour = discord.Colour(0xA37C05))
                for pack, pack2 in zip(bundle[top:least], bundle2[top:least]):
                    # Get current snapshot
                    eval_meth = pack[5]
                    temp = pack[2].split(' || ')
                    quest_sample = pack[4].split(' || ')
                    snapshot = pack[3].split(' || ')
                    cur_snapshot = []
                    for sque in temp:
                        a = await self.client.quefe(sque)
                        try: cur_snapshot.append(a[0])
                        except TypeError: cur_snapshot.append('0')

                    line = ''

                    # Create cur_snapshot-sample pack
                    if eval_meth == '>=':
                        for a, b, c in zip(cur_snapshot, snapshot, quest_sample):
                            try: rate = int(((int(a) - int(b))/int(c))*10)
                            except ZeroDivisionError: rate = 0
                            if rate > 10: rate = 10
                            elif rate < -10: rate = 0
                            line = line + f"\n╟{'◈'*rate + '◇'*(10-rate)}╢ ||({int(a) - int(b)}·**{c}**)||"
                    elif eval_meth == '==':
                        for a, b, c in zip(cur_snapshot, snapshot, quest_sample):
                            # DIGIT
                            try:
                                difference = int(a) - int(b)
                                try: rate = int(difference/int(c)*10)
                                except ZeroDivisionError: rate = 0
                            # CHAR
                            except ValueError:
                                if a == c:
                                    difference = 1
                                    rate = 10
                                else:
                                    difference = 0
                                    rate = 0
                            if rate > 10: rate = 10
                            elif rate < -10: rate = 0
                            line = line + f"\n╟{'◈'*rate + '◇'*(10-rate)}╢ ||({difference}·**{c}**)||"
                    elif eval_meth == '<=':
                        for a, b, c in zip(cur_snapshot, snapshot, quest_sample):
                            try: rate = int(((int(a) - int(b))/int(c))*10)
                            except ZeroDivisionError: rate = 0
                            if rate > 10: rate = 10
                            elif rate < -10: rate = 0
                            line = line + f"\n╟{'◈'*rate + '◇'*(10-rate)}╢ ||({int(a) - int(b)}·**{c}**)||"
                    elif eval_meth == '>':
                        for a, c in zip(cur_snapshot, quest_sample):
                            try: rate = int((int(a)/int(c))*10)
                            except ZeroDivisionError: rate = 0
                            if rate > 10: rate = 10
                            elif rate < -10: rate = 0
                            line = line + f"\n╟{'◈'*rate + '◇'*(10-rate)}╢ ||({int(a) - int(b)}·**{c}**)||"
                    elif eval_meth == '<':
                        for a, c in zip(cur_snapshot, quest_sample):
                            try: rate = int((int(a)/int(c))*10)
                            except ZeroDivisionError: rate = 0
                            if rate > 10: rate = 10
                            elif rate < -10: rate = 0
                            line = line + f"\n╟{'◈'*rate + '◇'*(10-rate)}╢ ||({int(a) - int(b)}·**{c}**)||"

                    if pack[6]:
                        if len(pack2[3]) > 100:
                            pack2 = list(pack2)
                            pack2[3] = pack2[3][:400] + '...'   # prev=151
                        if datetime.now() > pack[6]:
                            temb.add_field(
                                            name=f"═ `{pack[0]}` \🔥 {pack2[2].upper()} quest \🔥 ══════════\n", 
                                            value=f""">>> 🔥 ~~『`{pack[1]}`| **{pack2[0]}**』~~ 🔥```http
{pack2[3]}```{line}""")
                            # temb.add_field(name=f"`{pack[0]}`:fire: ~~『`{pack[1]}`|**{pack2[0]}**』{pack2[2]} quest~~\n\n> {pack2[3]}\n", value=line)
                        else:
                            delta = relativedelta(pack[6], datetime.now())
                            temb.add_field(
                                            name=f"═ `{pack[0]}` \📜 {pack2[2].upper()} quest \⏱ [`{delta.hours:02d}:{delta.minutes:02d}:{delta.seconds:02d}`]\n", 
                                            value=f""">>> 『`{pack[1]}`| **{pack2[0]}**』```http
{pack2[3]}```{line}""")
                            # temb.add_field(name=f"`{pack[0]}` :scroll:『`{pack[1]}`|**{pack2[0]}**』{pack2[2]} quest [`{delta.hours:02d}:{delta.minutes:02d}:{delta.seconds:02d}`]\n\n> {pack2[3]}\n", value=line)
                    else:
                        temb.add_field(
                                        name=f"═ `{pack[0]}` \📜 {pack2[2].upper()} quest \📜 ══════════\n", 
                                        value=f""">>> 『`{pack[1]}`| **{pack2[0]}**』 ```http
{pack2[3]}```{line}""")
                temb.set_footer(text=f'Quest {currentpage} of {len(bundle)}', icon_url=ctx.author.avatar_url)
                return temb
                #else:
                #    await ctx.send("*Nothing but dust here...*")

            await self.tools.pagiMain(ctx, (bundle, bundle2), makeembed, timeout=20, item_per_page=1, pair=True)

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def quests(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        await self.tools.ava_scan(ctx.message)

        name = await self.client.quefe(f"SELECT guild_code FROM pi_guild WHERE user_id='{ctx.author.id}';"); name = name[0]

        try:
            if name == 'n/a':
                await ctx.send("<:osit:544356212846886924> You haven't joined any guilds yet!"); return
        except IndexError: await ctx.send("<:osit:544356212846886924> You haven't joined any guilds yet!"); return

        current_place = await self.client.quefe(f"SELECT cur_PLACE FROM personal_info WHERE id='{ctx.author.id}'"); current_place = current_place[0]

        try:
            completed_bundle, qpool, qpool_guild = await self.client.quefe(f"SELECT pi_quest.`finished_quests`, pi_quest.`quest_pool`, model_guild.`quest_pool` FROM pi_quest, model_guild, pi_guild WHERE pi_quest.`user_id`='{ctx.author.id}' AND pi_guild.`user_id`=pi_quest.`user_id` AND model_guild.`guild_code`=pi_guild.`guild_code`;")
        except TypeError:
            await self.client.quefe(f"INSERT INTO pi_quest VALUES (0, {ctx.author.id}, '{current_place}', NULL, NULL);")
            completed_bundle, qpool, qpool_guild = await self.client.quefe(f"SELECT pi_quest.`finished_quests`, pi_quest.`quest_pool`, model_guild.`quest_pool` FROM pi_quest, model_guild, pi_guild WHERE pi_quest.`user_id`='{ctx.author.id}' AND pi_guild.`user_id`=pi_quest.`user_id` AND model_guild.`guild_code`=pi_guild.`guild_code`;")
        try:
            # completed_bundle = completed_bundle.split(' - ')
            completed_bundle = self.finQuest_coder(completed_bundle)
        except AttributeError: completed_bundle = {}
        try: qpool = qpool.split(' - ')
        except AttributeError: qpool = []
        try: qpool_guild = qpool_guild.split(' - ')
        except AttributeError: qpool_guild = []
        full_qpool = list(set(qpool + qpool_guild))
        bundle = await self.client.quefe(f"""SELECT quest_code, name, description, quest_line FROM model_quest WHERE region='{current_place}' AND quest_line IN ('main', 'side') AND quest_code IN ('{"' - '".join(full_qpool)}');""", type='all')
        bundle = self.bundleQuest_sort(bundle, completed_bundle)

        def makeembed(items, top, least, pages, currentpage):
            line = ''
            bundle, completed_bundle = items
            completed_quantity = 0
            for _, v in completed_bundle.items():
                completed_quantity += int(v)

            line = f"""```css
[Total].{len(bundle)}⠀⠀⠀⠀[Available].{completed_quantity}```"""
            reembed = discord.Embed(title = f"<:guild_p:619743808959283201> `{current_place}`|**QUEST BULLETTIN**", colour = discord.Colour(0xA37C05), description=f"{line}")

            for pack in bundle[top:least]:
                if pack[0] in completed_bundle: marker = '📃'
                else: marker = '📜'

                reembed.add_field(name=f'═ \{marker} `{pack[3].upper()} quest` \{marker} ══════════', value=f""">>> **`{pack[0]}`**| **『{pack[1]}"』**\n```http
{pack[2]}```
                """)


            reembed.set_footer(text=f"Board {currentpage} of {pages}")
            return reembed
            #else:
            #    await ctx.send("*Nothing but dust here...*")

        await self.tools.pagiMain(ctx, (bundle, completed_bundle), makeembed, timeout=60, item_per_page=2, pair=True)

    @commands.command(aliases=['pp'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def party(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        raw = list(args)
        
        try:
            if raw[0] in ['create', 'make']:
                # Check if user has already join a party
                try:
                    party_id, role = await self.client.quefe(f"SELECT party_id, role FROM pi_party WHERE user_id='{ctx.author.id}';")
                    await ctx.send(f":fleur_de_lis: You've already been a *{role.lower()}* of party `{party_id}`."); return
                except TypeError: pass

                # Create party_id
                count = 0; party_id = 0
                for i in str(ctx.author.id):
                    if count == 3: party_id += int(i); count = 1
                    else: party_id += int(i)*int(i); count += 1

                # Max member
                try: 
                    mxmem = int(raw[1])
                    if mxmem >= 10: mxmem = 10
                except (IndexError, TypeError): mxmem = 3

                # Privacy
                try:
                    if raw[2].lower() not in ['public', 'private']: privac = 'PUBLIC'
                except IndexError: privac = 'PUBLIC'

                try:
                    await self.client._cursor.execute(f"INSERT INTO environ_party VALUES ('{party_id}', 'Party of {ctx.author.name}', '{privac}', 1, {mxmem}, 'PASSIVE', 100); INSERT INTO pi_party VALUES ('{ctx.author.id}', '{party_id}', 'LEADER');")
                except mysqlError.IntegrityError:
                    await self.client._cursor.execute(f"INSERT INTO environ_party VALUES ('{party_id+1}', 'Party of {ctx.author.name}', '{privac}', 1, {mxmem}); INSERT INTO pi_party VALUES ('{ctx.author.id}', '{party_id}', 'LEADER');")
                await ctx.send(embed=discord.Embed(description=f":fleur_de_lis: Party `{party_id}`|**Party of {ctx.author.name}** is created. Good hunt, remnants!", colour=0xF4A400)); return

            elif raw[0] == 'leave':
                # Check if user has joined a party
                try: party_id, role = await self.client.quefe(f"SELECT party_id, role FROM pi_party WHERE user_id='{ctx.author.id}';")
                except TypeError: await ctx.send(f":fleur_de_lis: You have no party."); return

                # Leave     ||      Party members check
                if role.lower() == 'leader': await ctx.send(":fleur_de_lis: Leaders cannot abandon their comrades! If one's that coward, they'd use `party dismiss`."); return
                await self.client._cursor.execute(f"DELETE FROM pi_party WHERE user_id='{ctx.author.id}' AND party_id='{party_id}'; UPDATE environ_party SET member=member-1 WHERE party_id='{party_id}'; DELETE FROM environ_party WHERE party_id='{party_id}' AND quantity<=0;")

                await ctx.send(embed=discord.Embed(description=f":fleur_de_lis: Left party `{party_id}` as a {role}", colour=0xF4A400)); return

            elif raw[0] in ['dismiss', 'disband']:
                # Check if user has joined a party
                try: party_id, role = await self.client.quefe(f"SELECT party_id, role FROM pi_party WHERE user_id='{ctx.author.id}';")
                except TypeError: await ctx.send(f":fleur_de_lis: You have no party."); return

                # Leader check
                if role.lower() != 'leader': await ctx.send(f":fleur_de_lis: Only leaders can do this!"); return

                def UMC_check(m):
                    return m.channel == ctx.channel and m.author == ctx.author and m.content == 'dismiss confirm'

                await ctx.send(":fleur_de_lis: Dismissing the party will force other members to leave it too.\n<a:RingingBell:559282950190006282> Are you sure? (Key=`dismiss confirm` | Timeout=10s)")
                try: await self.client.wait_for('message', timeout=10, check=UMC_check)
                except asyncio.TimeoutError: await ctx.send(f"<:osit:544356212846886924> Request time-out!"); return

                await self.client._cursor.execute(f"DELETE FROM pi_party WHERE party_id='{party_id}'; DELETE FROM environ_party WHERE party_id='{party_id}';")
                await ctx.send(":white_check_mark: Dismissed! May the Olds look upon you..."); return

            elif raw[0] in ['member', 'mem', 'status']:
                users = await self.client.quefe(f"SELECT user_id, role FROM pi_party WHERE party_id=(SELECT party_id FROM pi_party WHERE user_id='{ctx.author.id}');", type='all')
                line = ''
                marker = {'MEMBER': ':fleur_de_lis:', 'LEADER': '<:fleurdelis:543234110559092756>'}
                try:
                    for user in users:
                        LP, MAX_LP, STA, MAX_STA, cur_X, cur_Y, cur_PLACE, merit, name = await self.client.quefe(f"SELECT LP, MAX_LP, STA, MAX_STA, cur_X, cur_Y, cur_PLACE, merit, name FROM personal_info WHERE id='{user[0]}';")
                        line = line + f"╬ **{name}**[{merit}] {marker[user[1]]} `{cur_X:.3f}`·`{cur_Y:.3f}`·`{cur_PLACE}`|**`LP`**`{int(LP/MAX_LP*100)}%`·**`STA`**`{int(STA/MAX_STA*100)}%`\n"
                except IndexError: await ctx.send(":fleur_de_lis: You have no party."); return
                await ctx.send(embed=discord.Embed(description=line, colour=0xF4A400))

            elif raw[0] == 'invite':
                # Check if user has joined a party
                try: party_id, role = await self.client.quefe(f"SELECT party_id, role FROM pi_party WHERE user_id='{ctx.author.id}';")
                except TypeError: await ctx.send(f":fleur_de_lis: You have no party."); return

                # Leader check
                if role.lower() != 'leader': await ctx.send(f":fleur_de_lis: Only leaders can do this!"); return

                try: user = ctx.message.mentions[0]
                # E: No mentioning
                except IndexError: await ctx.send(":fleur_de_lis: Please mention someone..."); return

                if user.id == ctx.author.id: await ctx.send("Don't be dumb <:fufu:520602319323267082>"); return

                try:
                    stats, cur_MOB, cur_USER = await self.client.quefe(f"SELECT stats, cur_MOB, cur_USER FROM personal_info WHERE id='{user.id}';")
                    if stats == 'DEATH': await ctx.send(f"<:osit:544356212846886924> The dead can't speak."); return
                    if cur_MOB != 'n/a' or cur_USER != 'n/a': await ctx.send(f"<:osit:544356212846886924> The player is in combat!"); return
                # User not incarnate
                except TypeError: await ctx.send(f"<:osit:544356212846886924> User has not incarnated yet, **{ctx.author.name}**"); return

                try:
                    tparty_id, trole = await self.client.quefe(f"SELECT party_id, role FROM pi_party WHERE user_id='{user.id}';")
                    await ctx.send(f":fleur_de_lis: User has already been a {trole.lower()} of party `{tparty_id}`!"); return
                except TypeError: pass

                msg = await ctx.send(f":fleur_de_lis: Hey {user.mention}, you received a party `{party_id}` invitation from **{ctx.author.name}**!\n<a:RingingBell:559282950190006282> React :white_check_mark: to accept! (Timeout=30s)")
        
                def RUM_check(reaction, u):
                    return u == user and reaction.message.id == msg.id and str(reaction.emoji) == "\U00002705"

                await msg.add_reaction("\U00002705")
                try: await self.client.wait_for('reaction_add', check=RUM_check, timeout=30)
                except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Invitation's declined!"); return

                if await self.client._cursor.execute(f"UPDATE environ_party SET member=member+1 WHERE party_id='{party_id}' AND member<=max_member;") == 0:
                    await ctx.send(f":fleur_de_lis: Party has reached maximum members"); return
                await self.client._cursor.execute(f"INSERT INTO pi_party VALUES ('{user.id}', '{party_id}', 'MEMBER');")
                await ctx.send(f":fleur_de_lis: {ctx.author.mention}, meet your new comrade of party `{party_id}` - {user.mention}."); return

            elif raw[0] == 'kick':
                # Check if user has joined a party
                try: party_id, role = await self.client.quefe(f"SELECT party_id, role FROM pi_party WHERE user_id='{ctx.author.id}';")
                except TypeError: await ctx.send(f":fleur_de_lis: You have no party."); return

                # Leader check
                if role.lower() != 'leader': await ctx.send(f":fleur_de_lis: Only leaders can do this!"); return

                try: user = ctx.message.mentions[0]
                # E: No mentioning
                except IndexError: 
                    try: 
                        int(raw[1])
                        user.id = str(raw[1])
                    except ValueError: await ctx.send("<:osit:544356212846886924> Invalid id!"); return
                    except IndexError: await ctx.send(":fleur_de_lis: Please mention someone..."); return

                if int(user.id) == ctx.author.id: await ctx.send("Don't be dumb <:fufu:520602319323267082>"); return

                if await self.client._cursor.execute(f"SELECT stats FROM personal_info WHERE id='{user.id}';") == 0:
                    await ctx.send(f"<:osit:544356212846886924> User has not incarnated yet, **{ctx.author.name}**"); return

                if await self.client._cursor.execute(f"SELECT role FROM pi_party WHERE user_id='{user.id}' AND party_id='{party_id}';") == 0:
                    await ctx.send(":fleur_de_lis: The user is not in your party."); return

                await self.client._cursor.execute(f"DELETE FROM pi_party WHERE user_id='{user.id}' AND party_id='{party_id}';")
                if await self.client._cursor.execute(f"UPDATE environ_party SET member=member-1 WHERE party_id='{party_id}' AND member>1;") == 0:
                    await self.client._cursor.execute(f"DELETE FROM environ_party WHERE party_id='{party_id}' AND member=1;")
                    await ctx.send(f":fleur_de_lis: User **{user.name}** is kicked and party {party_id} is deleted."); return
                await ctx.send(f":fleur_de_lis: User **{user.name}** is kicked."); return

            elif raw[0] == 'rally':
                try: party_id, role = await self.client.quefe(f"SELECT party_id, role FROM pi_party WHERE user_id='{ctx.author.id}';")
                except TypeError: await ctx.send(f":fleur_de_lis: You have no party."); return

                # LEADER
                if role == 'LEADER':
                    # Get party info
                    rally, RP = await self.client.quefe(f"SELECT rally, RP FROM environ_party WHERE party_id='{party_id}';")
                    if rally == 'ACTIVE': await ctx.send(f":fleur_de_lis: Your party has already rallied, **{ctx.author.name}**!"); return
                    elif RP < 200: await ctx.send(f":fleur_de_lis: Your party's **RP** is **{RP}**, which is lower than **200 RP** required."); return

                    msg = await ctx.send(f":fleur_de_lis: Rallying in 15 secs and **all** members in this region will be teleported to your coordinates. \n<a:RingingBell:559282950190006282> React :x: to *cancel*.")

                    def RUM_check(reaction, u):
                        return u == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) == "\U0000274c"

                    await msg.add_reaction("\U0000274c")
                    try: 
                        await self.client.wait_for('reaction_add', check=RUM_check, timeout=15)
                        await msg.edit(content=":fleur_de_lis: Rally cancelled!"); return
                    except asyncio.TimeoutError: await msg.delete()

                    users = await self.client.quefe(f"SELECT user_id FROM pi_party WHERE party_id='{party_id}' AND user_id!={ctx.author.id};", type='all')
                    
                    cur_X, cur_Y, cur_PLACE, STA = await self.client.quefe(f"SELECT cur_X, cur_Y, cur_PLACE, STA FROM personal_info WHERE id='{ctx.author.id}';")
                    # Teleporting
                    tele_count = 0
                    for user_id in users:
                        if await self.client._cursor.execute(f"UPDATE personal_info SET cur_X={cur_X}, cur_Y={cur_Y}, STA=MAX_STA WHERE id='{user_id[0]}' AND cur_PLACE='{cur_PLACE}';"): tele_count += 1
                    
                    if tele_count == 0: await ctx.send(":fleur_de_lis: *oof*... No one gave a :poop:"); return

                    duration = 300
                    await ctx.send(f"<a:WindFlag_SMALL:543592541929472010> {tele_count} answers to the battle-cry. For `{duration}` secs, **TO THE LEADER!**")

                    # Update rallier/party
                    await self.client._cursor.execute(f"UPDATE personal_info SET STA=MAX_STA WHERE id='{ctx.author.id}'; UPDATE environ_party SET rally='ACTIVE', RP={int(RP/2)} WHERE party_id='{party_id}';")
                    await asyncio.sleep(duration)
                    await self.client._cursor.execute(f"UPDATE environ_party SET rally='PASSIVE' WHERE party_id='{party_id}';"); await ctx.send(":fleur_de_lis: Rally stop!"); return

                # MEMBER
                elif role == 'MEMBER':
                    # Get party's info
                    rally, RP = await self.client.quefe(f"SELECT rally, RP FROM environ_party WHERE party_id='{party_id}';")
                    if rally == 'PASSIVE': await ctx.send(f":fleur_de_lis: Leader has not called for you, **{ctx.author.name}**!"); return
                    elif RP < 200: await ctx.send(f":fleur_de_lis: Your party's **RP** is **{RP}**, which is lower than **200 RP** required."); return

                    # Get leader's info
                    leader_id = await self.client.quefe(f"SELECT user_id FROM pi_party WHERE party_id='{party_id}' AND role='LEADER';")
                    try: cur_X, cur_Y, cur_PLACE = await self.client.quefe(f"SELECT cur_X, cur_Y, cur_PLACE FROM personal_info WHERE id='{ctx.author.id}' AND stats!='DEAD' AND cur_PLACE==(SELECT cur_PLACE FROM personal_info WHERE id='{ctx.author.id}');")
                    except TypeError: await ctx.send("Your leader is not *available* <:fufu:520602319323267082>"); return

                    await self.client._cursor.execute(f"UPDATE personal_info SET cur_X={cur_X}, cur_Y={cur_Y}, STA=STA+IF(id='{leader_id}', 5, 0) WHERE id IN ('{leader_id}', '{ctx.author.id}');")
                    await ctx.send(f"<a:WindFlag_SMALL:543592541929472010> Joined the leader at **`{cur_X}`** · **`{cur_Y}`** · **`{cur_PLACE}`**!!"); return
                    


        except IndexError:
            marker = {'MEMBER': ':fleur_de_lis:', 'LEADER': '<:fleurdelis:543234110559092756>'}
            try: party_id, role = await self.client.quefe(f"SELECT party_id, role FROM pi_party WHERE user_id='{ctx.author.id}';")
            except TypeError: await ctx.send(f"<:osit:544356212846886924> You've not joined any parties yet, **{ctx.author.name}**!"); return

            await ctx.send(embed=discord.Embed(description=f"{marker[role]} Currently in party `{party_id}` as a {role.lower()}.", colour=0xF4A400)); return



# ================== FEATURES ==================

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def art(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        arts = await self.client.quefe(f"SELECT art_code, art_name, art_type, description, value, tier, tier_cost, upgrade_increment, illulink FROM pi_arts WHERE user_id='{ctx.author.id}';", type='all')
        
        async def makeembed(arts, curp, dummy, pages, currentpage):
            d = arts[curp]

            if not d[5]: uplus = ''
            else: uplus = f"+{d[5]}"

            value_in = ''
            if d[3]: value_in = d[3].replace('value_in', str(d[4]))

            reembed = discord.Embed(title = f"{d[2].upper()} <:skill_icon:624779119019950100> `{d[0]}`|**{d[1]}** {uplus}", description = f"""```{value_in}```""", colour = discord.Colour(0x011C3A))
            reembed.set_footer(text=f">> Require {(float(d[6])*(float(d[5]) + 1)):.0f} for next tier (+{d[7]})")
            if d[8]: reembed.set_image(url=random.choice(d[8].split(" || ")))
            return reembed

        await self.tools.pagiMain(ctx, arts, makeembed, item_per_page=1)

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def arts(self, ctx, *args):

        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        allowed_arts = await self.client.quefe(f"SELECT arts FROM model_guild WHERE guild_code=(SELECT guild_code FROM pi_guild WHERE user_id='{ctx.author.id}');")
        allowed_arts = allowed_arts[0].split(' || ')
        aa = [a.split(' - ') for a in allowed_arts]
        tempaa = [a[0] for a in aa]
        arts = await self.client.quefe(f"""SELECT art_code, art_name, art_type, description, value, tier, tier_cost, upgrade_increment, illulink FROM model_arts WHERE art_code IN ('{"', '".join(tempaa)}');""", type='all')
        
        async def makeembed(arts, curp, dummy, pages, currentpage):
            d = arts[curp]
            r = aa[curp][1]

            if not d[5]: uplus = ''
            else: uplus = f"+{d[5]}"

            value_in = ''
            if d[3]: value_in = d[3].replace('value_in', str(d[4]))

            reembed = discord.Embed(title = f"<:skill_icon:624779119019950100> {d[2].upper()} · `{d[0]}`|**{d[1]}** {uplus}", description = f"""```{value_in}```""", colour = discord.Colour(0x011C3A))
            reembed.set_footer(text=f">> Require {(float(d[6])*(float(d[5]) + 1)):.0f} for next tier (+{d[7]})")
            reembed.set_thumbnail(url=self.guild_rank_image[r])
            if d[8]: reembed.set_image(url=random.choice(d[8].split(" || ")))
            return reembed

        await self.tools.pagiMain(ctx, arts, makeembed, timeout=60, item_per_page=1)        

    @commands.command()
    @commands.cooldown(1, 3, type=BucketType.user)
    async def learn(self, ctx, *args):

        # UPGRADE
        try:
            art_code, art_name, art_type, value, upgrade_increment, tier_cost, tier = await self.client.quefe(f"SELECT art_code, art_name, art_type, value, upgrade_increment, tier_cost, tier FROM pi_arts WHERE user_id='{ctx.author.id}' AND art_code='{args[0]}';")
            merit_cost = (tier+1)*tier_cost

            msg = await ctx.send(f"<:skill_icon:624779119019950100> Upgrading {art_type} will cost <:merit_badge:620137704662761512>{merit_cost}. Continue?\n> `{art_code}`|**{art_name}** [**`{value} ⇛ {value + upgrade_increment}`**]")
            await msg.add_reaction("\U00002705")
            try: await self.client.wait_for('reaction_add', timeout=20, check=lambda reaction, user: user.id == ctx.author.id and reaction.message.id == msg.id)
            except asyncio.TimeoutError: return

            if not await self.client._cursor.execute(f"UPDATE personal_info SET merit=merit-{merit_cost} WHERE id='{ctx.author.id}' AND merit>={merit_cost};"):
                await ctx.send(f"<:osit:544356212846886924> Unsufficient merits!"); return

            await self.client._cursor.execute(f"UPDATE pi_arts SET value=value+{upgrade_increment}, tier=tier+1 WHERE user_id='{ctx.author.id}' AND art_code='{art_code}';")
            await ctx.send(f"<:skill_icon:624779119019950100> {art_type.capitalize()} `{art_code}`|**{art_name}** upgraded!"); return

        # LEARN
        except TypeError: 
            try: art_code, art_name, art_type, tier_cost, illulink, rank = await self.client.quefe(f"SELECT art_code, art_name, art_type, tier_cost, illulink, (SELECT rank FROM pi_guild WHERE user_id='{ctx.author.id}') FROM model_arts WHERE user_id='{ctx.author.id}' AND art_code='{args[0]}' AND NOT EXISTS (SELECT * FROM pi_arts WHERE art_code='{args[0]}');")
            except TypeError: await ctx.send(f"<:osit:544356212846886924> Unable to learn such art."); return

            # GUILD check / ACCOUNT check
            if not rank: await ctx.send(f"<:osit:544356212846886924> Please join a guild, **{ctx.author.name}**."); return

            # Rank check
            if await self.client._cursor.execute(f"SELECT * FROM model_guild WHERE arts LIKE '%{art_code} - {rank[0]}%';"):
                await ctx.send(f"<:osit:544356212846886924> Your rank isn't high enough for this art. **{ctx.author.name}**!"); return

            if not await self.client._cursor.execute(f"UPDATE personal_info SET merit=merit-{merit_cost} WHERE id='{ctx.author.id}' AND merit>={merit_cost};"):
                await ctx.send(f"<:osit:544356212846886924> Unsufficient merits!"); return

            await ctx.send(embed=discord.Embed(title=f"<:skill_icon:624779119019950100> {art_type} · `{art_code}`|**{art_name}**").set_image(url=illulink))
            await self.client._cursor.execute(f"SELECT func_aa_reward('{ctx.author.id}', '{art_code}', 1);")

        except IndexError: pass



# ================== TOOLS ==================

    def finQuest_coder(self, value, decode=True):
        """
            decode: {'quest': 'quantity', ..}
            encode: 'qs1 | 1 - qs3 | 4'    
        """

        # DECODE
        if decode:
            out = {}
            for q in value.split(' - '):
                q = q.split(' | ')
                # Increase from a duplicate
                try:
                    out[q[0]] = str(int(out[q[0]]) + int(q[1]))
                # Value doesn't have ' | '
                except IndexError:
                    try:
                        out[q[0]] = str(int(out[q[0]]) + 1)
                    except KeyError:
                        out[q[0]] = '1'
                # No duplicate --> create new
                except KeyError:
                    try:
                        out[q[0]] = q[1]
                    except IndexError: out[q[0]] = '1'
            return out

        # ENCODE
        else:
            temp = []
            for k, v in value.items():
                temp.append(f"{k} | {v}")
            return ' - '.join(temp)

    def bundleQuest_sort(self, bundle, finQuests, cursor=0):

        # Keep two types splitted, in order to retain the order after sort
        done = []
        notdone = []

        for qc in bundle:
            if qc[cursor] in finQuests: done.append(qc)
            else: notdone.append(qc)

        return notdone + done




def setup(client):
    client.add_cog(avaGuild(client))
