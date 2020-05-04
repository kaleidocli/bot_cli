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



class avaActivity(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.__cd_check = self.client.thp.cd_check
        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)
        print("|| Activity --- Ready!")



# ================== EVENTS ==================

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     print("|| Activity --- Ready!")



# ================== ACTIVITIES ==================

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

                await ctx.send(f":briefcase: **{ctx.author.name}** assigns as `{raw[0]}`|**{jname}** for `{(duration/60):.0f}` min(s). The guild will pay you **<:36pxGold:548661444133126185>{reward}** in advance!")
                await self.client._cursor.execute(f"UPDATE personal_info SET STA={STA - sta}, money={money + reward} WHERE id='{ctx.author.id}'")
            # E: Unpack on empty query, due to degree not found
            except TypeError: await ctx.send(f""":briefcase: You need `{"', '".join(requirement.split(' - '))}` degree to apply for this job!"""); return
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
                line = line + f"""`{job_code}`| **{name.capitalize()}** ∙ *"{description}"*\n**<:36pxGold:548661444133126185>{reward}** | `{duration}`**s** | STA-`{sta}` | **Require:** `{requirement.replace(' - ', '` `')}`\n\n"""
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

            # Get mob's info / user's info
            try:
                mob_code, STR, STA, INT, w_str, w_mul = await self.client.quefe(f""" 
                    SELECT m.mob_code, pi.STR, pi.STA, pi.INTT, pii.str, pii.multiplier
                    FROM model_mob m
                        INNER JOIN personal_info pi ON pi.id='{ctx.author.id}'
                        INNER JOIN environ_diversity e ON e.environ_code=pi.cur_PLACE
                        INNER JOIN pi_inventory pii ON pii.item_id=pi.right_hand
                    WHERE m.mob_code=e.mob_code AND e.mob_code='{args[0]}'
                    LIMIT 1;
                """)
            except TypeError:
                await ctx.send(f"<:osit:544356212846886924> This mob (`{args[0]}`) is not in your current region! You can check for mob's code by using command `mobs`.")
                return
            except IndexError:
                await ctx.send(f"<:osit:544356212846886924> Please provide **mob's code**! You can check for mob's code by using command `mobs`.")
                return

            try:
                mobProto = self.client.DBC['model_mob'][mob_code]
            except KeyError:
                await ctx.send(f"<:osit:544356212846886924> Invalid **mob's code**! You can check for mob's code by using command `mobs`.")
                return

            # Check # 1
            if mobProto.branch == 'boss':
                await ctx.send(f"<:osit:544356212846886924> Unable to use command `hunt` on a boss! Cheeky you, eh?")
                return

            # Check # 2
            if not STA:
                await ctx.send(f"Go *get some food*, **{ctx.message.author.name}** <:fufu:605255050289348620> We cannot start a hunt with you exhausted like that."); return

            # Calc hunt quantity        # staPerMob = ((STR + str) / 2) * (mul + rand(0.3, 0.7, 1.1, 1.4, 1.7, 2))
                                        # numMob = STA / staPerMob
                                        # if numMob > 100:                    # (max numMob = 100)
                                        #       STA += staPerMob * (numMob - 100)
                                        #       numMob = 100
            staPerMob = round(mobProto.lp / (((STR+w_str)/2) * (w_mul+random.choice((0.7, 1.1, 1.4, 1.7, 2)))))
            if staPerMob < 1:
                staPerMob = 1
            numMob = round(STA / staPerMob)

            if numMob > 100:
                numMob = 100
                staCost = round(staPerMob * numMob)
            else:
                staCost = STA
            if numMob <= 0:
                numMob = 0

            # Calc duration             # duraPerMob = 1800                # (30mins/mob  |  max dura = 180,000s = 50hr ~ 2.08days  |  min dura = 1.04day)
                                        # duration = (numMob/2 * duraPerMob) + (numMob/2 * duraPerMob) / INT
            duraPerMob = 100
            duration = (numMob / 2 * duraPerMob) + ((numMob / 2 * duraPerMob) / INT if not (INT < 1) else (numMob / 2 * duraPerMob))

            # Reward generating         # rewardQuantity = round(rewardQuantity / 100 * randint(0, 100 + percentage))
                                        # if rewardQuantity <= 0: ...
            objecto = []    # Item reward
            statuso = []     # Status reward
            bingo_list = [] # Reward's name
            for rw in mobProto.rewards:
                rewardQuantity = int(rw[1])
                rewardQuantity = round(rewardQuantity / 100 * random.randint(0, 100 + int(rw[2]))) * numMob

                if rewardQuantity < 1:      # The following checks are hunt only, does not apply to other command like melee or range
                    continue
                if rw[0] in ('perks', 'merit'):
                    continue

                formattedReward = self.utils.rewardToQueryAndName((rw[0], rewardQuantity, int(rw[2])))
                # Item
                if formattedReward[0]:
                    objecto.append(formattedReward[0])
                # Status
                if formattedReward[1]:
                    statuso.append(formattedReward[1])
                # Name
                if formattedReward[2]:
                    bingo_list.append(formattedReward[2])

            # Reward's query and name
            reward_query = ' '.join(objecto)
            if statuso:
                reward_query += f"""UPDATE personal_info SET {(', '.join(statuso))} WHERE id="user_id_here";"""
            if bingo_list:
                rewards = '\n> ··'
                rewards += '\n> ··'.join(bingo_list)
            else:
                rewards = '\n> The hunt returned with empty hand :('

            # Reward prep + Party reward (if available)
            if reward_query:
                tem_que = reward_query
                reward_query = reward_query.replace('user_id_here', f"{ctx.author.id}")
                # Party
                comrades = await self.client.quefe(f"SELECT user_id FROM pi_party WHERE party_id=(SELECT party_id FROM pi_party WHERE user_id='{ctx.author.id}') AND user_id <> '{ctx.author.id}';", type='all')
                if comrades:
                    for comrade in comrades:
                        reward_query = reward_query + tem_que.replace('user_id_here', f"{comrade[0]}")
                        rewards = rewards + f"\nAnd **{len(comrades)}** comrades of yours will receive the same."

            # Reformatting rewards
            rewards = """**Hunted:** ({}) `{}`| **{}**\n**Reward:** {}""".format(numMob, mobProto.mob_code, mobProto.name, rewards)

            # End_point calc
            end_point = datetime.now() + timedelta(seconds=duration)
            end_point = end_point.strftime('%Y-%m-%d %H:%M:%S')

            # Insert
            if await self.client._cursor.execute(f"""UPDATE pi_hunt SET stats='ONGOING', end_point='{end_point}', reward_query='{reward_query}', rewards='{rewards}' WHERE user_id='{ctx.author.id}';""") == 0:
                await self.client._cursor.execute(f"""INSERT INTO pi_hunt VALUES ('{ctx.author.id}', '{end_point}', 'ONGOING', '{rewards}', "{reward_query}");""")
            await self.client._cursor.execute(f"UPDATE personal_info SET STA=STA-{staCost} WHERE id='{ctx.author.id}';")
            await ctx.send(f":cowboy: Hang tight, **{ctx.author.name}**! The hunt will last for **`{timedelta(seconds=duration)}`**."); return

        else:

            # Two points comparison
            delta = relativedelta(end_point, datetime.now())

            # Check
            if datetime.now() < end_point:
                await ctx.send(f":cowboy: The hunters are on their journey, **{ctx.author.name}**! Come back after **`{delta.hours:02d}:{delta.minutes:02d}:{delta.seconds:02d}`**"); return

            # Rewarding
            if final_rq:
                await self.client._cursor.execute(final_rq)
            await self.client._cursor.execute(f"UPDATE pi_hunt SET stats='DONE' WHERE user_id='{ctx.author.id}';")
            await ctx.send(f":cowboy: Congrats on your return, **{ctx.author.mention}**!", embed=discord.Embed(description=final_rw)); return

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

    @commands.command(aliases=['edu'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def education(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        cur_X, cur_Y = await self.client.quefe(f"SELECT cur_X, cur_Y FROM personal_info WHERE id='{str(ctx.message.author.id)}';")
        if not await self.tools.area_scan(ctx, cur_X, cur_Y): await ctx.send("<:osit:544356212846886924> Educating facilities are only available within **Peace Belt**!"); return

        cmd_tag = 'edu'
        degrees = ['elementary', 'middleschool', 'highschool', 'associate', 'bachelor', 'master', 'doctorate']
        major = ['astrophysic', 'biology', 'chemistry', 'georaphy', 'mathematics', 'physics', 'education', 'archaeology', 'history', 'humanities', 'linguistics', 'literature', 'philosophy', 'psychology', 'management', 'international_bussiness', 'elemology', 'electronics', 'robotics', 'engineering']
 
        # INFO
        try:
            if args[0] == 'degree':
                await ctx.send(f"""> `{'` ➠ `'.join(degrees)}`""")
                return
            elif args[0] == 'major':
                await ctx.send(f"`{'` · `'.join(major)}`")
                return
        except IndexError:
            await ctx.send(f"Welcome to :books: **Ascending Sanctuary of Siegfields**.\n╟`education degree` to view all degree.\n╟`education major` to view all majors."); return

        # Check if the previous course has been finished yet
        if not await self.__cd_check(ctx.message, cmd_tag, f":books: *Enlightening requires one's most persevere and patience.*"): return

        # MAJOR
        try:
            if args[1] not in major: await ctx.send(f"<:osit:544356212846886924> Major not found!"); return
        except IndexError: await ctx.send(f"<:osit:544356212846886924> Missing `major` argument!"); return

        # DEGREE
        try: price, INTT_require, INTT_reward, degree_require, duration = await self.client.quefe(f"SELECT price, INTT_require, INTT_reward, degree_require, duration FROM model_degree WHERE degree='{args[0].lower()}';")
        except TypeError: await ctx.send(f"<:osit:544356212846886924> Degree not found!"); return
        degree_require = degree_require.split(' of ')

        # DEGREE (and MAJOR) prequisite check
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
        
        temp2 = await ctx.send(f">>> :books: Program for `{args[0].capitalize()} of {args[1].capitalize()}`:\n| **Price:** <:36pxGold:548661444133126185>{price}\n| **Duration:** {duration/7200} months\n**Result:** · **`{args[0].capitalize()} of {args[1].capitalize()}`** · `{INTT_reward}` INT. \n<a:RingingBell:559282950190006282> Do you wish to proceed? (Key: `enroll confirm` | Timeout=15s)")

        def UMCc_check(m):
            return m.channel == ctx.channel and m.author == ctx.author and m.content.lower() == 'enroll confirm'

        try: await self.client.wait_for('message', timeout=15, check=UMCc_check)
        except asyncio.TimeoutError: await ctx.send(f"<:osit:544356212846886924> Assignment session of {ctx.message.author.mention} is closed."); return
        await temp2.delete()

        # Initialize
        try: await self.client._cursor.execute(f"INSERT INTO pi_degrees VALUES (0, '{ctx.author.id}', '{args[0].lower()}', '{args[1].lower()}');")
        except AttributeError: await self.client._cursor.execute(f"INSERT INTO pi_degrees VALUES (0, '{str(ctx.message.author.id)}', '{args[0].lower()}', NULL);")
        await self.client._cursor.execute(f"UPDATE personal_info SET INTT={INTT + INTT_reward}, STA=0, money={money - price} WHERE id='{ctx.author.id}';")
        # Cooldown set
        await ctx.send(f":white_check_mark: **<:36pxGold:548661444133126185>{price}** has been deducted from your account.")
        await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.set, f'{cmd_tag}{ctx.author.id}', 'degreeing', ex=duration, nx=True))

    @commands.command(aliases=['med'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def medication(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        cur_X, cur_Y, LP, MAX_LP, money = await self.client.quefe(f"SELECT cur_X, cur_Y, LP, MAX_LP, money FROM personal_info WHERE id='{ctx.author.id}'")

        if not await self.tools.area_scan(ctx, cur_X, cur_Y): await ctx.send("<:osit:544356212846886924> Medical treatments are only available within **Peace Belt**!"); return

        reco = MAX_LP - LP
        if reco == 0: await ctx.send(f"<:osit:544356212846886924> **{ctx.author.name}**, your current LP is at max!"); return

        reco_scale = reco/(MAX_LP/25)
        if reco_scale == 0: reco_scale = 0.1
        
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
    client.add_cog(avaActivity(client))
