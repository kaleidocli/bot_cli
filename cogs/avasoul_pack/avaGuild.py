import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors
import pymysql.err as mysqlError

import asyncio
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

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


    @commands.Cog.listener()
    async def on_ready(self):
        print("|| Guild Systems ---- READY!")



    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def guild(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        await self.tools.ava_scan(ctx.message)
        raw = list(args)

        name, rank, total_quests = await self.client.quefe(f"SELECT name, rank, total_quests FROM pi_guild WHERE user_id='{ctx.author.id}';")

        try:
            if name == 'n/a' and raw[0] != 'join':
                await ctx.send("<:osit:544356212846886924> You haven't joined any guilds yet!"); return
        except IndexError: await ctx.send("<:osit:544356212846886924> You haven't joined any guilds yet!"); return

        current_place, money = await self.client.quefe(f"SELECT cur_PLACE, money FROM personal_info WHERE id='{ctx.author.id}'")

        try:
            if raw[0] == 'join':
                # Check if user's in the same guild
                if name == current_place:
                    await ctx.send(f"<:osit:544356212846886924> You've already been in that guild, **{ctx.message.author.name}**!"); return
                # ... or in other guilds
                elif name != 'n/a':
                    cost = abs(2000* (int(name.split('.')[1]) - int(current_place.split('.')[1])))
                # ... jor just want to join
                else: cost = 0

                def UMCc_check(m):
                    return m.channel == ctx.channel and m.content == 'joining confirm' and m.author == ctx.author

                await ctx.send(f":scales: **G.U.I.L.D** of `{current_place} | {name}` :scales:\n------------------------------------------------\nJoining will require **<:36pxGold:548661444133126185>{cost}** as a deposit which will be returned when you leave guild if: \n· You don't have any bad records.\n· You're alive.\n· You leave the guild before joining others\n------------------------------------------------\n<a:RingingBell:559282950190006282> **Do you wish to proceed?** (key: `joining confirm` | timeout=20s)")
                try: await self.client.wait_for('message', timeout=20, check=UMCc_check)           
                except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request timed out!"); return

                # Money check
                if money < cost: await ctx.send("<:osit:544356212846886924> Insufficient balance!"); return

                await self.client._cursor.execute(f"UPDATE personal_info SET money={money - cost} WHERE id='{str(ctx.message.author.id)}';")
                await self.client._cursor.execute(f"UPDATE pi_guild SET name='{current_place}', deposit=deposit+{cost} WHERE user_id='{str(ctx.message.author.id)}';")
                await ctx.send(f"<:guild_p:619743808959283201> Welcome, {ctx.message.author.mention}, to our big family all over Pralayr <:guild_p:619743808959283201>\nYou are no longer a lonely, nameless adventurer, but a member of `{current_place} | {name}` guild, a part of **G.U.I.L.D**'s league. Please, newcomer, make yourself at home <3"); return

            elif raw[0] == 'leave':
                name, deposit = await self.client.quefe(f"SELECT name, deposit FROM pi_guild WHERE user_id='{str(ctx.message.author.id)}'")

                def UMCc_check(m):
                    return m.channel == ctx.channel and m.content == 'leaving confirm' and m.author == ctx.author

                await ctx.send(f"<a:RingingBell:559282950190006282> {ctx.message.author.mention}, leaving `{current_place}|{name}` guild? (key: `leaving confirm` | timeout=5s)")
                try: await self.client.wait_for('message', timeout=5, check=UMCc_check)
                except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request timed out!"); return

                await self.client._cursor.execute(f"UPDATE personal_info SET money=money+{deposit} WHERE id='{str(ctx.message.author.id)}';")
                await self.client._cursor.execute(f"UPDATE pi_guild SET name='n/a', deposit=0 WHERE user_id='{str(ctx.message.author.id)}';")
                await ctx.send(f":white_check_mark: Left guild. Deposit of **<:36pxGold:548661444133126185>{deposit}** has been returned"); return

        except IndexError: await ctx.send(f"<:guild_p:619743808959283201> **`{ctx.message.author.name}`'s G.U.I.L.D card** <:guild_p:619743808959283201> \n------------------------------------------------\n**`Guild`** · `{name}`|**{name}**\n**`Rank`** · {rank}\n**`Total quests done`** · {total_quests}"); return

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def quest(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        await self.tools.ava_scan(ctx.message)
        raw = list(args)

        name, rank = await self.client.quefe(f"SELECT name, rank FROM pi_guild WHERE user_id='{ctx.author.id}';")

        try:
            if name == 'n/a':
                await ctx.send("<:osit:544356212846886924> You haven't joined any guilds yet!"); return
        except IndexError: await ctx.send("<:osit:544356212846886924> You haven't joined any guilds yet!"); return

        current_place = await self.client.quefe(f"SELECT cur_PLACE, money FROM personal_info WHERE id='{ctx.author.id}'"); current_place = current_place[0]

        try:
            if raw[0] == 'take':
                # If quest's id given, accept the quest
                try:
                    sample = {'iron': 3, 'bronze': 4, 'silver': 5, 'gold': 6, 'adamantite': 8, 'mithryl': 10}
                    if await self.client._cursor.execute(f"SELECT * FROM pi_quests WHERE user_id='{ctx.author.id}' AND quest_code='{raw[1]}';") >= 1:
                        await ctx.send("<:osit:544356212846886924> Quest has already been taken"); return
                    done_quests = await self.client.quefe(f"SELECT finished_quests FROM pi_quest WHERE user_id='{ctx.author.id}' AND region='{current_place}';")
                    if raw[1] in done_quests[0].split(' - '): await ctx.send("<:osit:544356212846886924> Quest has already been done"); return
                    if await self.client._cursor.execute(f"SELECT COUNT(user_id) FROM pi_quests WHERE user_id='{ctx.author.id}' AND stats='ONGOING'") >= sample[rank]: await ctx.send(f"<:osit:544356212846886924> You cannot handle more than **{sample[rank]}** quests at a time")

                    # QUEST info get
                    try: quest_code, quest_line, quest_name, snap_query, quest_sample, eval_meth, effect_query, reward_query, prerequisite, penalty_query, duration = await self.client.quefe(f"SELECT quest_code, quest_line, name, snap_query, sample, eval_meth, effect_query, reward_query, prerequisite, penalty_query, duration FROM model_quest WHERE quest_code='{raw[1]}' AND region='{current_place}' AND quest_line IN ('main', 'side');")
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
                    if duration == '0':
                        end_point = datetime.now() + timedelta(seconds=duration)
                        end_point = f"'{end_point.strftime('%Y-%m-%d %H:%M:%S')}'"
                    else: end_point = 'NULL'


                    await self.client._cursor.execute(f"""INSERT INTO pi_quests VALUES (0, '{quest_code}', '{ctx.author.id}', "{snap_query}", '{snapshot}', '{quest_sample}', '{eval_meth}', "{effect_query}", "{reward_query}", "{penalty_query}", {end_point}, 'FULL'); {effect_query}""")
                    
                    await ctx.send(f":white_check_mark: {quest_line.capitalize()} quest `{raw[1]}`|**{quest_name}** accepted! Use `quest` to check your progress."); return
                # E: Quest's id not found
                except ValueError: await ctx.send("<:osit:544356212846886924> Quest not found"); return
                # E: Quest's id not given (and current_quest is also empty)
                except IndexError: await ctx.send(f"Take what?"); return

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
                except (TypeError, mysqlError.InternalError): await ctx.send(f"<:osit:544356212846886924> Quest not found, **{ctx.author.name}**")
                snap_query = snap_query.replace('user_id_here', f'{ctx.author.id}')
                reward_query = reward_query.replace('user_id_here', f'{ctx.author.id}')

                # Duration check
                if end_point:
                    if datetime.now() > end_point: await ctx.send(f"<:guild_p:619743808959283201> The quest is out of time, **{ctx.author.name}**!"); return

                if stats == 'DONE': await ctx.send("<:osit:544356212846886924> A quest cannot be claimed twice, scammer... <:fufu:520602319323267082>"); return

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
                        if not (a - int(b)) >= int(c): await ctx.send("<:guild_p:619743808959283201> The quest has not been fulfilled yet"); return
                elif eval_meth == '==':
                    for a, b, c in zip(cur_snapshot, snapshot, quest_sample):
                        print(a, b, c)
                        # DIGIT
                        if c.isdigit():
                            if not (int(a) - int(b)) >= int(c): await ctx.send("<:guild_p:619743808959283201> The quest has not been fulfilled yet"); return
                        # CHAR
                        else:
                            if not a == c: await ctx.send("<:guild_p:619743808959283201> The quest has not been fulfilled yet"); return
                if eval_meth == '<=':
                    for a, b, c in zip(cur_snapshot, snapshot, quest_sample):
                        if not (a - int(b)) <= int(c): await ctx.send("<:guild_p:619743808959283201> The quest has not been fulfilled yet"); return
                elif eval_meth == '>':
                    for a, c in zip(cur_snapshot, quest_sample):
                        if not a >= int(c): await ctx.send("<:guild_p:619743808959283201> The quest has not been fulfilled yet"); return
                elif eval_meth == '<':
                    for a, c in zip(cur_snapshot, quest_sample):
                        if not a <= int(c): await ctx.send("<:guild_p:619743808959283201> The quest has not been fulfilled yet"); return

                # Reward n Affect
                await self.client._cursor.execute(reward_query)
                # Increase pi_guild.total_quests by 1
                # Remove quest
                await self.client._cursor.execute(f"UPDATE pi_guild SET total_quests=total_quests+1 WHERE user_id='{ctx.author.id}'; DELETE FROM pi_quests WHERE user_id='{ctx.author.id}' AND quest_id={raw[1]};")
                # Update finished_quest in pi_quest. If not exist, create one
                if await self.client._cursor.execute(f"UPDATE pi_quest SET finished_quests=CONCAT(finished_quests, ' - {quest_code}') WHERE user_id='{ctx.author.id}' AND region='{current_place}';") == 0:
                    await self.client._cursor.execute(f"INSERT INTO pi_quest VALUE (0, '{ctx.author.id}', '{current_place}', '{quest_code}');")

                """
                # Remove if daily, else keep
                #if quest_line == 'DAILY': 
                #else: await self.client._cursor.execute(f"UPDATE pi_quests SET stats='DONE' WHERE user_id='{ctx.author.id}' AND quest_id={raw[1]};")
                """
                # Inform
                await ctx.send(f"<:guild_p:619743808959283201> Quest completion is confirmed. **{ctx.author.name}**, may the Olds look upon you!")
                # Ranking check
                if await self.client._cursor.execute(f"UPDATE pi_guild SET rank='{self.guild_rank[rank][0]}' WHERE user_id='{str(ctx.message.author.id)}' AND total_quests>={self.guild_rank[rank][1]};") == 1:
                    await ctx.send(f":beginner: Congrats, {ctx.message.author.mention}! You've been promoted to **{self.guild_rank[rank][0].upper()}**!")                         

        except IndexError:
            bundle = await self.client.quefe(f"SELECT quest_id, quest_code, snap_query, snapshot, sample, eval_meth, end_point FROM pi_quests WHERE user_id='{ctx.author.id}' AND stats IN ('ONGOING', 'FULL');", type='all')
            # ONGOING quest check
            if not bundle: await ctx.send(f"<:guild_p:619743808959283201> You have currently no active quest, **{ctx.author.name}**! Try get some and prove yourself."); return
            bundle2 = []
            for pack in bundle:
                tempbu = await self.client.quefe(f"SELECT name, description, quest_line, description FROM model_quest WHERE quest_code='{pack[1]}';", type='all')
                bundle2.append(tempbu[0])

            async def makeembed(top, least, pages, currentpage):
                temb = discord.Embed(title = f"**ACTIVE QUESTS** || {ctx.author.name}", colour = discord.Colour(0x011C3A), description=f'═════════╡**`{currentpage}/{len(bundle)}`**╞═════════')
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
                        if datetime.now() > pack[6]:
                            temb.add_field(name=f"`{pack[0]}`:fire:~~『`{pack[1]}`|**{pack2[0]}**』{pack2[2]} quest~~\n\n> {pack2[3]}\n", value=line)
                        else:
                            delta = relativedelta(pack[6], datetime.now())
                            temb.add_field(name=f"`{pack[0]}` :scroll:『`{pack[1]}`|**{pack2[0]}**』{pack2[2]} quest [`{delta.hours:02d}:{delta.minutes:02d}:{delta.seconds:02d}`]\n\n> {pack2[3]}\n", value=line)
                    else:
                        temb.add_field(name=f"`{pack[0]}` :scroll:『`{pack[1]}`|**{pack2[0]}**』{pack2[2]} quest\n\n> {pack2[3]}\n", value=line)
                return temb
                #else:
                #    await ctx.send("*Nothing but dust here...*")
            
            async def attachreaction(msg):
                await msg.add_reaction("\U00002b05")    #Left
                await msg.add_reaction("\U000027a1")    #Right

            pages = int(len(bundle)/1)
            if len(bundle)%1 != 0: pages += 1
            currentpage = 1
            cursor = 0

            emli = []
            for curp in range(pages):
                myembed = await makeembed(currentpage*1-1, currentpage*1, pages, currentpage)
                emli.append(myembed)
                currentpage += 1

            try: msg = await ctx.send(embed=emli[cursor])
            except IndexError: await ctx.send("<:osit:544356212846886924> Please join a guild..."); return
            if pages > 1: await attachreaction(msg)
            else: return

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
                    break          

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def quests(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        await self.tools.ava_scan(ctx.message)
        raw = list(args)

        name = await self.client.quefe(f"SELECT name FROM pi_guild WHERE user_id='{ctx.author.id}';"); name = name[0]

        try:
            if name == 'n/a':
                await ctx.send("<:osit:544356212846886924> You haven't joined any guilds yet!"); return
        except IndexError: await ctx.send("<:osit:544356212846886924> You haven't joined any guilds yet!"); return

        current_place = await self.client.quefe(f"SELECT cur_PLACE FROM personal_info WHERE id='{ctx.author.id}'"); current_place = current_place[0]

        bundle = await self.client.quefe(f"SELECT quest_code, name, description, quest_line FROM model_quest WHERE region='{current_place}' AND quest_line IN ('main', 'side');", type='all')
        #completed_bundle = await self.client.quefe(f"SELECT quest_code FROM pi_quests WHERE user_id='{ctx.author.id}' AND stats='DONE' AND EXISTS (SELECT * FROM model_quest WHERE model_quest.quest_code=pi_quests.quest_code AND region='{current_place}');")
        completed_bundle = await self.client.quefe(f"SELECT finished_quests FROM pi_quest WHERE user_id='{ctx.author.id}' AND region='{current_place}';")
        try: completed_bundle = completed_bundle[0].split(' - ')
        except (TypeError, AttributeError): completed_bundle = []

        def makeembed(top, least, pages, currentpage):
            line = ''

            line = f"\n```『Total』{len(bundle)}⠀⠀⠀⠀『Done』{len(completed_bundle)}```"
            for pack in bundle[top:least]:
                if pack[0] in completed_bundle: marker = ':page_with_curl:'
                else: marker = ':scroll:'
                line += f"""\n{marker} **`{pack[0]}`**|`{pack[3].capitalize()} quest`\n⠀⠀⠀|**"{pack[1]}"**\n⠀⠀⠀|*"{pack[2]}"*\n"""

            reembed = discord.Embed(title = f"<:guild_p:619743808959283201> `{current_place}`|**Quest Bulletin**", colour = discord.Colour(0x011C3A), description=f"{line}\n⠀⠀⠀⠀")
            reembed.set_footer(text=f"Board {currentpage} of {pages}")
            return reembed
            #else:
            #    await ctx.send("*Nothing but dust here...*")
        
        async def attachreaction(msg):
            await msg.add_reaction("\U00002b05")    #Left
            await msg.add_reaction("\U000027a1")    #Right

        pages = int(len(bundle)/3)
        if len(bundle)%3 != 0: pages += 1
        currentpage = 1
        cursor = 0

        emli = []
        for curp in range(pages):
            myembed = makeembed(currentpage*3-3, currentpage*3, pages, currentpage)
            emli.append(myembed)
            currentpage += 1

        try: msg = await ctx.send(embed=emli[cursor])
        except IndexError: await ctx.send("<:osit:544356212846886924> Please join a guild..."); return
        if pages > 1: await attachreaction(msg)
        else: return

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
                break

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




def setup(client):
    client.add_cog(avaGuild(client))
