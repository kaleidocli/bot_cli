import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors
import pymysql.err as mysqlError

from functools import partial
import asyncio
import random
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from .avaTools import avaTools
from .avaUtils import avaUtils

class avaActivity:
    def __init__(self, client):
        self.client = client
        self.__cd_check = self.client.thp.cd_check
        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)


    
    @commands.command(aliases=['job'])
    @commands.cooldown(1, 10, type=BucketType.user)
    async def work(self, ctx, *args):
        cmd_tag = 'work'
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        if not await self.__cd_check(ctx.message, cmd_tag, f"**{ctx.author.name}**, you are working."): return
        raw = list(args)

        try: 
            requirement, duration, reward, sta, jname = await self.client.quefe(f"SELECT requirement, duration, reward, sta, name FROM model_job WHERE job_code='{raw[0]}';")
            try:
                reli = requirement.split(' - '); full_cheq = ''
                for ree in reli:
                    ree = ree.split(' of ')
                    cheq = f"degree='{ree[0]}'"
                    try: cheq = cheq + f" AND major='{ree[1]}'"
                    except IndexError: pass

                    full_cheq = full_cheq + f" AND EXISTS (SELECT * FROM pi_degrees WHERE user_id='{ctx.author.id}' AND {cheq})"

                STA, money = await self.client.quefe(f"""SELECT STA, money FROM personal_info WHERE id='{ctx.author.id}' {full_cheq};""")
                if STA < sta: await ctx.send(f"Grab something to *eat*, **{ctx.author.name}** <:fufu:605255050289348620> You can't do anything with such STA."); return

                await ctx.send(f":briefcase: **{ctx.author.name}** wants to be `{raw[0]}`|**{jname}** for `{int(duration/240)}` days. We'll prepay you **<:36pxGold:548661444133126185>{reward}**!")
                await self.client._cursor.execute(f"UPDATE personal_info SET STA={STA - sta}, money={money + reward} WHERE id='{ctx.author.id}'")
            # E: Unpack on empty query, due to degree not found
            except TypeError: await ctx.send(f""":briefcase: You need `{"', '".join(requirement.split(' - '))}` to apply for this job!"""); return
        except IndexError: await ctx.send(":briefcase: Please choose a job! You can use `works` check what you can do"); return
        # E: Unpack on empty query, due to job_code not found
        except TypeError: await ctx.send(":x: Job's code not found!"); return

        await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.set, f'{cmd_tag}{ctx.author.id}', 'working', ex=duration, nx=True))

    @commands.command(aliases=['jobs'])
    @commands.cooldown(1, 10, type=BucketType.user)
    async def works(self, ctx, *args):

        search_query = ''
        for search in args:
            try:
                try:
                    if int(search): kww = 'sta'
                    else: kww = 'sta'
                except ValueError:
                    if search.startswith('$'): kww = 'reward'
                    elif search.endswith('s'): kww = 'duration'
                    else: kww = 'requirement'

                if search_query: search_query += "AND"
                else: search_query += "WHERE"; first = kww

                if kww == 'requirement': search_query += f" requirement LIKE '%{search.capitalize()}%' "
                else: search_query += f" {kww}>={search} "
            # E: Invalid search
            except (AttributeError, IndexError): pass
        
        if search_query: search_query += f" ORDER BY {first} ASC"

        try:
            job_list = await self.client.quefe(f"SELECT job_code, name, description, requirement, duration, reward, sta FROM model_job {search_query};", type='all')
            if not job_list: await ctx.send("<:osit:544356212846886924> No result..."); return
        # E: Invalid syntax 
        except mysqlError.ProgrammingError: await ctx.send("<:osit:544356212846886924> **Invalid syntax.** For filtering, please use `[keyword]==[value]`"); return 
        # E: Invalid syx
        except mysqlError.InternalError: await ctx.send("<:osit:544356212846886924> **Invalid keywors.** Please use `reward`, `duration`, `requirement`, `sta`"); return

        def makeembed(top, least, pages, currentpage):
            line = ''

            line = "**-------------------- oo --------------------**\n" 
            for pack in job_list[top:least]:
                job_code, name, description, requirement, duration, reward, sta = pack
                line = line + f"""`{job_code}` ∙ **{name.capitalize()}**\n*"{description}"*\n**<:36pxGold:548661444133126185>{reward}** | `{duration}`**s** | STA-`{sta}` | **Require:** `{requirement.replace(' - ', '` `')}`\n\n"""
            line = line + "**-------------------- oo --------------------**" 

            reembed = discord.Embed(title = f"JOBS", colour = discord.Colour(0x011C3A), description=line)
            reembed.set_footer(text=f"Page {currentpage} of {pages}")
            return reembed
            #else:
            #    await ctx.send("*Nothing but dust here...*")
        
        async def attachreaction(msg):
            await msg.add_reaction("\U000023ee")    #Top-left
            await msg.add_reaction("\U00002b05")    #Left
            await msg.add_reaction("\U000027a1")    #Right
            await msg.add_reaction("\U000023ed")    #Top-right

        pages = len(job_list)//5
        if len(job_list)%5 != 0: pages += 1
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
        else: msg = await ctx.send(embed=emli[cursor], delete_after=21); return

        def UM_check(reaction, user):
            return user.id == ctx.message.author.id and reaction.message.id == msg.id

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
                await msg.delete(); return

    @commands.command()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def hunt(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        try: end_point, stats, final_rq, final_rw = await self.client.quefe(f"SELECT end_point, stats, reward_query, rewards FROM pi_hunt WHERE user_id='{ctx.author.id}';")
        except TypeError: stats = 'DONE'

        if stats == 'DONE':
            raw = list(args)

            STR, INTT, STA = await self.client.quefe(f"SELECT STR, INTT, STA FROM personal_info WHERE id='{ctx.author.id}';")

            # Get hunt limitation
            try:
                limit = int(raw[0])
                if limit >= STA: limit = STA - 1
            except (IndexError, ValueError): limit = STA - 1

            if limit <= 0: await ctx.send(f"Go *get some food*, **{ctx.message.author.name}** <:fufu:605255050289348620> We cannot start a hunt with you exhausted like that."); return

            # Get animals based on INTT
            anis = await self.client.quefe(f"SELECT ani_code, str, sta, aggro, rewards, reward_query FROM model_animal WHERE intt<={INTT};", type='all')


            # Reward generating
            rewards = '\n'; reward_query = ''
            while STA > limit:
                # Get target
                target = random.choice(anis)

                # Decrease STA
                STA -= target[2]

                # Rate calc
                rate = STR - target[1]
                if rate > 1: rate = target[3]//rate
                elif rate < 1:
                    rate = round(target[3]*abs(rate))
                    if rate == 1: rate = 2
                elif rate == 1: rate = target[3]

                # Decide if session is success
                if random.choice(range(rate)) != 0: continue

                rewards = rewards + f"★ {target[4]}\n"
                reward_query = reward_query + f" {target[5]}"

            # Reward_query preparing
            if reward_query:
                tem_que = reward_query
                reward_query = reward_query.replace('user_id_here', f"{ctx.author.id}")
                comrades = await self.client.quefe(f"SELECT user_id FROM pi_party WHERE party_id=(SELECT party_id FROM pi_party WHERE user_id='{ctx.author.id}');", type='all')
                for comrade in comrades:
                    reward_query = reward_query + tem_que.replace('user_id_here', f"{comrade[0]}")
                if comrades: rewards = rewards + f"And **{len(comrades)}** comrades of yours will receive the same."

            # Duration calc     |      End_point calc
            duration = 60*limit//STR
            end_point = datetime.now() + timedelta(seconds=duration)
            end_point = end_point.strftime('%Y-%m-%d %H:%M:%S')

            # Insert
            if await self.client._cursor.execute(f"""UPDATE pi_hunt SET stats='ONGOING', end_point='{end_point}', reward_query="{reward_query}", rewards='{rewards}' WHERE user_id='{ctx.author.id}';""") == 0:
                await self.client._cursor.execute(f"""INSERT INTO pi_hunt VALUES ('{ctx.author.id}', '{end_point}', 'ONGOING', '{rewards}', "{reward_query}");""")
            await self.client._cursor.execute(f"UPDATE personal_info SET STA=STA-{limit} WHERE id='{ctx.author.id}';")
            await ctx.send(f":cowboy: Hang tight, **{ctx.author.name}**! The hunt will end after **`{timedelta(seconds=duration)}`**."); return

        else:

            # Two points comparison
            delta = relativedelta(end_point, datetime.now())
            if datetime.now() < end_point: await ctx.send(f":cowboy: Hold right there, {ctx.message.author.name}! Come back after **`{delta.hours:02d}:{delta.minutes:02d}:{delta.seconds:02d}`**"); return

            # Rewarding
            if final_rq:
                await self.client._cursor.execute(final_rq)
            await self.client._cursor.execute(f"UPDATE pi_hunt SET stats='DONE' WHERE user_id='{ctx.author.id}';")
            await ctx.send(f":cowboy: Congrats, **{ctx.message.author.name}**. You've finished your hunt!{final_rw}"); return








def setup(client):
    client.add_cog(avaActivity(client))
