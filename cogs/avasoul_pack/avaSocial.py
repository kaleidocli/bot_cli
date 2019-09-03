import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors

import random
import asyncio
from functools import partial
from datetime import datetime

from .avaTools import avaTools
from .avaUtils import avaUtils
from utils import checks

class avaSocial(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.__cd_check = self.client.thp.cd_check
        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)


    @commands.Cog.listener()
    async def on_ready(self):
        print("|| Social ---- READY!")


    # ========================= FAMILY ========================

    @commands.command()
    @commands.cooldown(1, 90, type=BucketType.user)
    async def marry(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        try: target = ctx.message.mentions[0]
        except IndexError: await ctx.send(f":revolving_hearts: Please tell us your love one, **{ctx.message.author.name}**!"); return

        try: name, partner, cur_PLACE = await self.client.quefe(f"SELECT name, partner, cur_PLACE FROM personal_info WHERE id='{ctx.author.id}' AND partner='n/a';")
        except TypeError: await ctx.send(f"<:osit:544356212846886924> Hey no cheating, {ctx.message.author.name}!"); return
        try: t_name, t_partner, t_cur_PLACE = await self.client.quefe(f"SELECT name, partner, cur_PLACE FROM personal_info WHERE id='{target.id}' AND partner='n/a';")
        except TypeError: await ctx.send(f"<:osit:544356212846886924> User has already married, {ctx.message.author.name}!"); return

        if ctx.author == target: await ctx.send(f":revolving_hearts: **I know this is wrong but...**"); await asyncio.sleep(3)
        if cur_PLACE != t_cur_PLACE: await ctx.send(f":revolving_hearts: You two need to be in the same region!"); return

        line = f"""```css
    ...{name.upper()}: "Father. Smith. Warrior. Mother. Maiden. Crone. Stranger. I am his/hers, and s/he is mine, from this day, until the end of my days."
    ...KALEI: "And you, [{t_name}]?"```"""

        line_no = f"""```css
    ...{name.upper()}: "Father. Smith. Warrior. Mother. Maiden. Crone. Stranger. I am his/hers, and s/he is mine, from this day, until the end of my days."
    ...KALEI: "And you, [{t_name}]?"
    ...{t_name.upper()}: "NOPE"```"""

        line_yes = f"""```css
    ...{name.upper()}: "Father. Smith. Warrior. Mother. Maiden. Crone. Stranger. I am his/hers, and s/he is mine, from this day, until the end of my days."
    ...KALEI: "And you, [{t_name}]?"
    ...{t_name.upper()}: "Father. Smith. Warrior. Mother. Maiden. Crone. Stranger. I am his/hers, and s/he is mine, from this day, until the end of my days."```"""

        msg = await ctx.send(line + f" :revolving_hearts: Hey {target.mention}... {ctx.message.author.mention} is asking you to be their partner!")
        
        def RUM_check(reaction, user):
            return user == target and reaction.message.id == msg.id and str(reaction.emoji) == "\U00002764"

        await msg.add_reaction("\U00002764")
        try: await self.client.wait_for('reaction_add', check=RUM_check, timeout=60)
        except asyncio.TimeoutError: await msg.edit(content=line_no); return
        await msg.edit(content=line_yes)

        # Add partner
        await self.client._cursor.execute(f"UPDATE personal_info SET partner='{target.id}' WHERE id='{ctx.author.id}'; UPDATE personal_info SET partner='{str(ctx.message.author.id)}' WHERE id='{target.id}';")

    @commands.command()
    @commands.cooldown(1, 15, type=BucketType.user)
    async def sex(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        cmd_tag = 'sex'
        if not await self.__cd_check(ctx.message, cmd_tag, f"<:fufu:605255050289348620> Calm your lewdness, **{ctx.author.name}**~~"): return

        # User info
        try: LP, max_LP, STA, max_STA, charm, partner, gender = await self.client.quefe(f"SELECT LP, max_LP, STA, max_STA, charm, partner, gender FROM personal_info WHERE id='{ctx.author.id}' AND partner!='n/a';")
        except TypeError: await ctx.send("<:osit:544356212846886924> Get yourself a partner first :>"); return

        # Partner info
        t_LP, t_max_LP, t_STA, t_max_STA, t_charm, t_gender, t_name = await self.client.quefe(f"SELECT LP, max_LP, STA, max_STA, charm, gender, name FROM personal_info WHERE id='{partner}';")
        #tar = self.client.get_user(int(partner))
        tar = await self.client.loop.run_in_executor(None, partial(self.client.get_user, int(partner)))

        # ================== BIRTH
        if await self.utils.percenter(charm+t_charm, total=200) and gender != t_gender:
            await ctx.send(f"||<a:RingingBell:559282950190006282> Name your child. Timeout=30s||\n<:sailu:559155210384048129> Among these dark of the age, a new life has enlighten...\n⠀⠀⠀⠀**{ctx.author.name}** and {tar.mention}, how will you christen your little?\n⠀⠀⠀⠀⠀⠀⠀⠀Won't you do, keep shut and remain silence.")

            def UMCc_check(m):
                return m.channel == ctx.channel and m.author in [tar, ctx.author]

            try: resp = await self.client.wait_for('message', timeout=30, check=UMCc_check)
            except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Life arrived, yet its harbor declined..."); return

            if gender == 'm': father = f"{ctx.author.id}"; mother = f"{tar.id}"
            else: father = f"{ctx.author.id}"; mother = f"{tar.id}"

            # In case of two children is having sex
            if father.startswith('99999999') and mother.startswith('99999999'):
                await ctx.send(f"<:sailu:559155210384048129> The two descendants of players tried, but gods forbade them to have children..."); return

            year, month, day, hour, minute = await self.client.loop.run_in_executor(None, self.utils.time_get)
            # Child will have 9999999 in front of its id
            id = f"99999999{''.join([str(year), str(month), str(day), str(hour), str(minute)])}"
            await self.tools.character_generate(id, resp.content, dob=[year, month, day, hour, minute], resu=False)
            await self.tools.hierarchy_generate(id, guardian_ids=[father, mother], chem_value=0)
            await ctx.send(f"<:sailu:559155210384048129> The whole Pralaeyr welcomes you, **{resp.content}**! May the Olds look upon you, {ctx.author.mention} and **{t_name}**.")

            # DAMAGING
            if gender == 'f':
                LP = await self.tools.division_LP(LP, max_LP, time=8)
                await self.client._cursor.execute(f"UPDATE personal_info SET LP={LP} WHERE id='{ctx.author.id}';")
            else:
                t_LP = await self.tools.division_LP(t_LP, t_max_LP, time=4)
                await self.client._cursor.execute(f"UPDATE personal_info SET LP={t_LP} WHERE id='{partner}';")

        # ================== SEX
        else:
            await ctx.send(f":heart: {tar.mention}, **{ctx.author.name}** is feeling *unsure*.\nType `sure` to make {ctx.author.name} sure, 20 secs left to grab your chance!")

            def UMCc_check(m):
                return m.channel == ctx.channel and m.author == tar

            try: resp = await self.client.wait_for('message', timeout=20, check=UMCc_check)
            except asyncio.TimeoutError: await ctx.send("<:gees:559192536195923999> Neither of them are sure..."); return

            slib = {'mf': ['https://media.giphy.com/media/HocMFeabR7rKU/giphy.gif', 'https://imgur.com/lA3AxJB.gif'],
            'fm': ['https://media.giphy.com/media/HocMFeabR7rKU/giphy.gif'],
            'mm': ['https://media.giphy.com/media/Ta8nU0hjzCB6o/giphy.gif'],
            'ff': ['https://media.giphy.com/media/4Al6v0Mmu20gg/giphy.gif', 'https://media.giphy.com/media/rvOyFjbMz86Mo/giphy.gif']}
            reco_percent = (STA / max_STA + t_STA / t_max_STA) / 2
            
            await ctx.send(embed=discord.Embed(description="""```The two got closer, and closer, and closer, and close--...```""", colour=0xFFE2FF).set_image(url=random.choice(slib[gender+t_gender])))

            await self.client._cursor.execute(f"UPDATE personal_info SET STA=0, LP=IF(id='{ctx.author.id}', {int(LP + LP * reco_percent)}, {int(t_LP + t_LP * reco_percent)}) WHERE id IN ('{ctx.author.id}', '{partner}');")
            await asyncio.sleep(1)
            await self.tools.ava_scan(ctx.message, type='normalize')

        await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.set, f'{cmd_tag}{ctx.author.id}', 'sex', ex=3600, nx=True))

    @commands.command()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def divorce(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return


        partner = await self.client.quefe(f"SELECT partner FROM personal_info WHERE id='{ctx.author.id}';")
        if partner[0] == 'n/a': await ctx.send("<:osit:544356212846886924> As if you have a partner :P"); return
        p2 = await self.client.quefe(f"SELECT name FROM personal_info WHERE id='{partner[0]}';")
        #except TypeError: await ctx.send("<:osit:544356212846886924> As if you have a partner :P"); return
        partner = list(partner); partner.append(p2[0])

        def UMCc_check(m):
            return m.channel == ctx.channel and m.author == ctx.author and m.content == "let's fcking divorce"

        # NAME
        await ctx.send(f":broken_heart: Divorce with **{partner[1]}**?\n||<a:RingingBell:559282950190006282> Timeout=15s · Key=`let's fcking divorce`||")
        try: 
            await self.client.wait_for('message', timeout=15, check=UMCc_check)
        except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Request times out!"); return

        await self.client._cursor.execute(f"UPDATE personal_info SET partner='n/a' WHERE id IN ('{ctx.author.id}', '{partner[0]}'); UPDATE environ_hierarchy SET guardians=REPLACE(guardians, ' ||| {ctx.author.id}', ''), guardians=REPLACE(guardians, '{ctx.author.id} ||| ', '') WHERE guardians LIKE '%{ctx.author.id}%';")
        await ctx.send(":broken_heart: You are now strangers, to each other.")

    @commands.command()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def family(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        # Get info
        id, name, t_id, t_name = await self.client.quefe(f"SELECT id, name, partner AS prtn, (SELECT name FROM personal_info WHERE id=prtn) FROM personal_info WHERE id='{ctx.author.id}';")
        if t_name: target_addon = f" AND guardians LIKE '%{t_id}%'"
        else: target_addon = ''
        children = await self.client.quefe(f"SELECT id, name, gender, age FROM personal_info WHERE id IN (SELECT child_id FROM environ_hierarchy WHERE guardians LIKE '%{id}%' {target_addon});", type='all')
        gengen = {'m': 'Male', 'f': 'Female'}

        def makeembed(top, least, pages, currentpage):
            line = '\n'

            for child in children[top:least]:
                print(children, child)
                line = line + f"""<:sailu:559155210384048129> **{child[1]}** ({child[3]}), {gengen[child[2]]}\n      ╟||`{child[0]}`||\n"""

            if t_name: reembed = discord.Embed(description=line, colour = discord.Colour(0xFFE2FF)).set_thumbnail(url=ctx.author.avatar_url).set_author(name=f"{name.capitalize()} & {t_name.capitalize()}", icon_url='https://imgur.com/jkznAfT.png')
            else: reembed = discord.Embed(description=line, colour = discord.Colour(0xFFE2FF)).set_thumbnail(url=ctx.author.avatar_url).set_author(name=f"{name.capitalize()}... . . .. .   .  .", icon_url='https://imgur.com/jkznAfT.png')
            return reembed
            #else:
            #    await ctx.send("*Nothing but dust here...*")
        
        async def attachreaction(msg):
            await msg.add_reaction("\U000023ee")    #Top-left
            await msg.add_reaction("\U00002b05")    #Left
            await msg.add_reaction("\U000027a1")    #Right
            await msg.add_reaction("\U000023ed")    #Top-right

        try: pages = len(children)//4
        except TypeError:
            if t_name: reembed = discord.Embed(colour = discord.Colour(0xFFE2FF)).set_author(name=f"{name.capitalize()} & {t_name.capitalize()}", icon_url='https://imgur.com/jkznAfT.png')
            else: reembed = discord.Embed(colour = discord.Colour(0xFFE2FF)).set_author(name=f"{name.capitalize()}... . . .. .   .  .", icon_url='https://imgur.com/jkznAfT.png')
            await ctx.send(embed=reembed)
            return
        if len(children)%4 != 0: pages += 1
        currentpage = 1
        cursor = 0

        # pylint: disable=unused-variable
        emli = []
        for curp in range(pages):
            myembed = makeembed(currentpage*4-4, currentpage*4, pages, currentpage)
            emli.append(myembed)
            currentpage += 1
        # pylint: enable=unused-variable

        if not emli: await ctx.send("<:sailu:559155210384048129> No child!"); return
        if pages > 1: 
            await attachreaction(msg)
            msg = await ctx.send(embed=emli[cursor])
        else: msg = await ctx.send(embed=emli[cursor], delete_after=30); return

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
    @commands.cooldown(1, 3, type=BucketType.user)
    async def tell(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        # Check if user is child's guardian
        try:
            child_id, name = await self.client.quefe(f"SELECT child_id, (SELECT name FROM personal_info WHERE id='{args[0]}') FROM environ_hierarchy WHERE child_id='{args[0]}' AND guardians LIKE '%{ctx.author.id}%';")
        except TypeError: await ctx.send("<:osit:544356212846886924> Unable to find *your child's* id"); return

        # Get command
        try: cmd = self.client.get_command(args[1])
        except IndexError: await ctx.send("<:osit:544356212846886924> Missing command name"); return
        if not cmd: await ctx.send("<:osit:544356212846886924> Command not found"); return

        # Cache
        uname = ctx.author.name
        uid = ctx.author.id
        udis = ctx.author.discriminator
        #uava = ctx.author.avatar_url

        # Modify ctx as child's ctx
        # ctx = ctx.author._replace(name=name)
        # ctx = ctx.author._replace(id=int(child_id))
        ctx.author._user._update({'username': name, 'id': child_id, 'discriminator': self.client.user.discriminator, 'avatar': 'n/a', 'bot': False})
        #ctx.author._user.id = int(child_id)
        #ctx.author.id = int(child_id)

        # Invoke
        try: await ctx.invoke(cmd, *args[2:])
        # In case it was trying to DM the child
        except discordErrors.HTTPException: pass
        ctx.author._user._update({'username': uname, 'id': uid, 'discriminator': udis, 'avatar': 'n/a', 'bot': False})








    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def like(self, ctx, *args):
        cmd_tag = 'like'
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        if not await self.__cd_check(ctx.message, cmd_tag, f"<:fufu:508437298808094742> You cannot award more merits at the moment, **{ctx.author.name}**."): return

        # Get target
        try: target = ctx.message.mentions[0]
        except (IndexError, TypeError): await ctx.send(f"<:osit:544356212846886924> Missing the receiver, **{ctx.author.name}**"); return

        if await self.client._cursor.execute(f"UPDATE personal_info SET merit=merit+1 WHERE id='{target.id}';") == 0:
            await ctx.send(f"<:osit:544356212846886924> User has not incarnated, **{ctx.author.name}**!"); return

        await ctx.send(f"<:4_:544354428396896276> **{ctx.author.name}** has given {target.mention} a merit!")
        await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.set, f'{cmd_tag}{ctx.author.id}', 'like', ex=86400, nx=True))

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def dislike(self, ctx, *args):
        cmd_tag = 'dislike'
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        if not await self.__cd_check(ctx.message, cmd_tag, f"<:fufu:508437298808094742> You cannot negate more merits at the moment, **{ctx.author.name}**."): return

        # Get target
        try: target = ctx.message.mentions[0]
        except (IndexError, TypeError): await ctx.send(f"<:osit:544356212846886924> Missing the target, **{ctx.author.name}**"); return

        if await self.client._cursor.execute(f"UPDATE personal_info SET merit=merit-1 WHERE id='{target.id}';") == 0:
            await ctx.send(f"<:osit:544356212846886924> User has not incarnated, **{ctx.author.name}**!"); return

        await ctx.send(f"<:argh:544354429302865932> **{ctx.author.name}** has humiliated {target.mention}!")
        await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.set, f'{cmd_tag}{ctx.author.id}', 'dislike', ex=86400, nx=True))












def setup(client):
    client.add_cog(avaSocial(client))
