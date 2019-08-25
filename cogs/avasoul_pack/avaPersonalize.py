from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import asyncio
import random
from functools import partial

from .avaTools import avaTools
from .avaUtils import avaUtils

class avaPersonalize:
    def __init__(self, client):
        self.client = client
        self.__cd_check = self.client.thp.cd_check
        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)


    def on_ready(self):
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

        cur_X, cur_Y, LP, MAX_LP, money = await self.client.quefe(f"SELECT cur_X, cur_Y, LP, MAX_LP, money FROM personal_info WHERE id='{str(ctx.message.author.id)}'")

        if not await self.tools.area_scan(ctx, cur_X, cur_Y): await ctx.send("<:osit:544356212846886924> Medical treatments are only available within **Peace Belt**!"); return

        reco = MAX_LP - LP
        if reco == 0: await ctx.send(f"<:osit:544356212846886924> **{ctx.message.author.name}**, your current LP is at max!"); return

        reco_scale = reco//(MAX_LP/20)
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




def setup(client):
    client.add_cog(avaPersonalize(client))
