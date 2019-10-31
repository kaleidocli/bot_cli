import asyncio
import random
import math
from copy import deepcopy
from datetime import datetime
from dateutil.relativedelta import relativedelta

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors

from .avaTools import avaTools
from .avaUtils import avaUtils
from utils import checks



class avaDungeon(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.dSessionSocket = {}
        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)

        self.intoLoop(self.prepLoad())

        print("|| Dungeon --- READY!")

    async def prepLoad(self):
        await asyncio.sleep(60)      #prev=5        # Do not remove, or else the data stream would mix with avaAvatar or WORLD_BUILDING
        self.mobdict = await self.mobdictLoad()
        self.dungeondict = await self.dungeondictLoad()
        self.checkpointdict = await self.checkpointdictLoad()
        self.itemdict = await self.itemdictLoad()

    def intoLoop(self, coro):
        self.client.loop.create_task(coro)



# ================== EVENTS ==================

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     await asyncio.sleep(1)
    #     self.mobdict = await self.mobdictLoad()
    #     self.dungeondict = await self.dungeondictLoad()
    #     self.checkpointdict = await self.checkpointdictLoad()
    #     self.itemdict = await self.itemdictLoad()

    #     print("|| Dungeon ---- READY!")



# ================== DUNGEON ==================

    @commands.command()
    @commands.cooldown(1, 2, type=BucketType.user)
    async def dungeons(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        current_place = await self.client.quefe(f"SELECT cur_PLACE FROM personal_info WHERE id='{ctx.author.id}';")
        temp_dungeons = []

        # Filter by region
        for k, v in self.dungeondict.items():
            if v.region != current_place[0]: continue
            temp_dungeons.append(v)

        if not temp_dungeons: await ctx.send("<:osit:544356212846886924> There is no dungeon in this region it seems..."); return
        
        async def makeembed(curp, pages, currentpage):
            d = temp_dungeons[curp]

            reembed = discord.Embed(title = f":map: `{d.dungeon_code}`|**{d.dungeon_name}**", description = f"""```{d.description}```""", colour = discord.Colour(0x011C3A))
            reembed.add_field(name="<:map_icon:619739576805621760> Georaphy", value=f"╟`Region` · **`{d.region}`**\n╟`Length` · **{d.length}m**", inline=True)
            reembed.add_field(name="<:merit_badge:620137704662761512> Fee/Reward", value=f"╟`Fee` · <:36pxGold:548661444133126185>**{d.price}**\n╟`Merit` · <:merit_badge:620137704662761512>**{d.merit_per_meter}**/m", inline=True)
            try: reembed.set_image(url=d.illulink)
            except: pass
            return reembed
        
        async def attachreaction(msg):
            await msg.add_reaction("\U000023ee")    #Top-left
            await msg.add_reaction("\U00002b05")    #Left
            await msg.add_reaction("\U000027a1")    #Right
            await msg.add_reaction("\U000023ed")    #Top-right
            await msg.add_reaction("\U0001f50e")    #Top-right

        pages = len(temp_dungeons)
        currentpage = 1
        cursor = 0

        emli = []
        for curp in range(pages):
            myembed = await makeembed(curp, pages, currentpage)
            emli.append(myembed)
            currentpage += 1

        msg = await ctx.send(embed=emli[cursor])
        if pages > 1: await attachreaction(msg)
        else: return

        while True:
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=20, check=lambda reaction, user: user.id == ctx.author.id and reaction.message.id == msg.id)
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

    @commands.command(aliases=['dng'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def dungeon(self, ctx, *args):

        # CHOICE ===================================
        try:
            if args[0] == 'enter':
                if not await self.tools.ava_scan(ctx.message, type='life_check'): return

                # Check args
                try: temp = self.dungeondict[args[1]]
                except IndexError: await ctx.send("<:osit:544356212846886924> Missing `dungeon_code`!"); return
                except KeyError: await ctx.send("<:osit:544356212846886924> Unknown `dungeon_code`."); return

                # Check if user is currently in another session. If is, suggest to make new one
                try:
                    try:
                        cur_dun = self.dSessionSocket[ctx.author.id]
                        delta = relativedelta(datetime.now(), cur_dun.start_point)
                        msg = await ctx.send(f"<:guild_p:619743808959283201> You're currently in `{cur_dun.dungeon.dungeon_code}`|**{cur_dun.dungeon.dungeon_name}**.\n╟Distance · `{cur_dun.timeline[-1].distance}`\n╟Duration · `{delta.hours:02d}:{delta.minutes:02d}:{delta.seconds:02d}`\nAbort this dungeon and continue?")
                    except KeyError:
                        distance, start_point, dungeon_code = await self.client.quefe(f"SELECT distance, start_point, dungeon_code FROM pi_dungeoncheckpoint WHERE user_id='{ctx.author.id}';")
                        delta = relativedelta(datetime.now(), start_point)
                        msg = await ctx.send(f"<:guild_p:619743808959283201> You're currently in dungeon **`{dungeon_code}`**.\n╟Distance · `{distance}`\n╟Duration · `{delta.hours:02d}:{delta.minutes:02d}:{delta.seconds:02d}`\nContinue?")
                    await msg.add_reaction('\U00002705')
                    try: await self.client.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author, timeout=15)
                    except asyncio.TimeoutError: return

                # E: Already have a session, or session's timeline is empty
                except (TypeError, IndexError): pass

                # Get user info
                money, lp, strr = await self.client.quefe(f"SELECT money, lp, STR FROM personal_info WHERE id='{ctx.author.id}';")
                if money < temp.price: await ctx.send(f"<:osit:544356212846886924> You need <:36pxGold:548661444133126185>{temp.price} as entry fee to enter this dungeon, {ctx.author.mention}!"); return
 
                msg = await ctx.send(f"<:guild_p:619743808959283201> A snapshot of your character will be transmitted into dungeon `{temp.dungeon_code}`|**{temp.dungeon_name}**, and will not be saved until next checkpoint.\n<a:RingingBell:559282950190006282> Entry fee is <:36pxGold:548661444133126185>{temp.price}. Do you wish to continue?")
                await msg.add_reaction("\U00002705")
                try: await self.client.wait_for('reaction_add', timeout=15, check=lambda r, u: u.id == ctx.author.id and r.message.id == msg.id)
                except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Entry request is cancelled."); return

                self.dSessionSocket[ctx.author.id] = dSession(self.client, ctx, self.mobdict, self.dungeondict, temp, self.checkpointdict, pdb_pack=(lp, strr, strr, 0, 0, 0))
                # Update user      ||       Purge user's abdundant session (if available)
                await self.client._cursor.execute(f"UPDATE personal_info SET money=money-{temp.price} WHERE id='{ctx.author.id}'; DELETE FROM pi_dungeoncheckpoint WHERE user_id='{ctx.author.id}';")
                await ctx.send(f"<:guild_p:619743808959283201> Your snapshot has been transmitted into `{temp.dungeon_code}`|**{temp.dungeon_name}**! May the Olds look upon you...")
                return
            
            elif args[0] == 'use':
                # SESSION check/get
                try:
                    try: ses = self.dSessionSocket[ctx.author.id]
                    except KeyError:
                        # Check db session // Load session if possible
                        lp, attack, defense, money, merit, dungeon_code, distance, checkpoints, start_point = await self.client.quefe(f"SELECT lp, attack, defense, money, merit, dungeon_code, distance, checkpoints, start_point FROM pi_dungeoncheckpoint WHERE user_id='{ctx.author.id}';")
                        ses = dSession(self.client, ctx, self.mobdict, self.dungeondict, self.dungeondict[dungeon_code], self.checkpointdict, cp_pack=(lp, attack, defense, money, merit), cp_pack2=(distance,), start_point=start_point)
                        if checkpoints:
                            ses.checkpoint = True
                            ses.checkpoints = deepcopy(checkpoints.split(' || '))
                        self.dSessionSocket[ctx.author.id] = ses
                except TypeError: await ctx.send(f"<:osit:544356212846886924> You are not in any dungeon at the moment."); return

                try: item = ses.timeline[-1].player.inventory.pop(0)
                except IndexError: await ctx.send(f"<:osit:544356212846886924> Empty inventory."); return

                ses.timeline[-1].player.lp += item.di_lp
                ses.timeline[-1].player.attack = ses.timeline[-1].player.base_attack + item.di_attack
                ses.timeline[-1].player.defense = ses.timeline[-1].player.base_defense + item.di_defense

                await ctx.send(f"<a:shakin_box:625467655759069184> Used `{item.di_name}`")
                return

            elif args[0] == 'discard':
                # SESSION check/get
                try:
                    try: ses = self.dSessionSocket[ctx.author.id]
                    except KeyError:
                        # Check db session // Load session if possible
                        lp, attack, defense, money, merit, dungeon_code, distance, checkpoints, start_point = await self.client.quefe(f"SELECT lp, attack, defense, money, merit, dungeon_code, distance, checkpoints, start_point FROM pi_dungeoncheckpoint WHERE user_id='{ctx.author.id}';")
                        ses = dSession(self.client, ctx, self.mobdict, self.dungeondict, self.dungeondict[dungeon_code], self.checkpointdict, cp_pack=(lp, attack, defense, money, merit), cp_pack2=(distance,), start_point=start_point)
                        if checkpoints:
                            ses.checkpoint = True
                            ses.checkpoints = deepcopy(checkpoints.split(' || '))
                        self.dSessionSocket[ctx.author.id] = ses
                except TypeError: await ctx.send(f"<:osit:544356212846886924> You are not in any dungeon at the moment."); return

                # Either discard first item or random item
                try:
                    # First
                    if random.choice([True, False]):
                        item = ses.timeline[-1].player.inventory.pop(0)
                    # Random
                    else:
                        item = ses.timeline[-1].player.inventory.pop(random.choice(range(len(ses.timeline[-1].player.inventory))))
                except IndexError: await ctx.send(f"<:osit:544356212846886924> Empty inventory."); return

                await ctx.send(f":outbox_tray: Discarded `{item.di_name}`"); return


            else: return
        except IndexError: pass

        # SESSION get ===================================
        try:
            # Check cache session
            try: your_session = self.dSessionSocket[ctx.author.id]
            except KeyError:
                # Check db session // Load session if possible
                lp, attack, defense, money, merit, dungeon_code, distance, checkpoints, start_point = await self.client.quefe(f"SELECT lp, attack, defense, money, merit, dungeon_code, distance, checkpoints, start_point FROM pi_dungeoncheckpoint WHERE user_id='{ctx.author.id}';")
                your_session = dSession(self.client, ctx, self.mobdict, self.dungeondict, self.dungeondict[dungeon_code], self.checkpointdict, cp_pack=(lp, attack, defense, money, merit), cp_pack2=(distance,), start_point=start_point)
                if checkpoints:
                    your_session.checkpoint = True
                    your_session.checkpoints = deepcopy(checkpoints.split(' || '))
                self.dSessionSocket[ctx.author.id] = your_session
        except TypeError: await ctx.send("<:osit:544356212846886924> You haven't enter any dungeon yet. Please use `dungeon enter [dungeon_code]`."); return

        # Lock check (and lock ON) =======================
        if not your_session.lock: your_session.lock = True
        else: await ctx.send(f"<:osit:544356212846886924> Please finish your current event!"); return
        your_session.ctx = ctx

        # Checkpoint check ===============================
        if your_session.checkpoint:
            msg = await ctx.send(f"Leaving the checkpoint area, {ctx.author.mention}?", delete_after=5)
            await msg.add_reaction('\U00002705')
            
            try: await self.client.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author, timeout=5)
            except asyncio.TimeoutError:
                your_session.lock = False
                return

            # Change checkpoint status
            your_session.checkpoint = False

        res = await your_session.updateTimeline() 

        # In case dead
        try:
            if res == 'dead': self.sessionDel(ctx)
        except TypeError: pass

        # Lock OFF
        your_session.lock = False

    @commands.command(aliases=['cp'])
    @commands.cooldown(1, 2, type=BucketType.user)
    async def checkpoint(self, ctx, *args):

        # SESSION check/get
        try:
            try: ses = self.dSessionSocket[ctx.author.id]
            except KeyError:
                # Check db session // Load session if possible
                lp, attack, defense, money, merit, dungeon_code, distance, checkpoints, start_point = await self.client.quefe(f"SELECT lp, attack, defense, money, merit, dungeon_code, distance, checkpoints, start_point FROM pi_dungeoncheckpoint WHERE user_id='{ctx.author.id}';")
                ses = dSession(self.client, ctx, self.mobdict, self.dungeondict, self.dungeondict[dungeon_code], self.checkpointdict, cp_pack=(lp, attack, defense, money, merit), cp_pack2=(distance,), start_point=start_point)
                if checkpoints:
                    ses.checkpoint = True
                    ses.checkpoints = deepcopy(checkpoints.split(' || '))
                self.dSessionSocket[ctx.author.id] = ses
        except TypeError: await ctx.send(f"<:osit:544356212846886924> You are not in any dungeon at the moment."); return

        # GENERAL ==========================
        if not args:

            # Checkpoint check/get
            try:
                cp = self.checkpointdict[ses.checkpoints[-1]]
            except IndexError: await ctx.send(f"<:osit:544356212846886924> You are not in a checkpoint area at the moment."); return

            await ctx.send(embed=discord.Embed(title=f"Checkpoint#{cp.cp_tier} | **{cp.cp_name}**", description=f"```{cp.cp_description}```").set_thumbnail(url='https://imgur.com/ER8IFx3.gif'))
            return

        # RETURN ===========================
        if args[0] == 'return':
            # Checkpoint check/get
            try:
                cp = self.checkpointdict[ses.checkpoints[-1]]
            except IndexError: await ctx.send(f"<:osit:544356212846886924> You are not in a checkpoint area at the moment."); return

            delta = relativedelta(datetime.now(), ses.start_point)
            new_player = ses.timeline[-1].player
            after_money = int(new_player.money/100*cp.cp_tax_money)
            after_merit = int(new_player.merit/100*cp.cp_tax_merit)
            msg = await ctx.send(f"<:guild_p:619743808959283201> {ctx.author.mention}, you're currently in `{ses.dungeon.dungeon_code}`|**{ses.dungeon.dungeon_name}**.\n> <:racing:622958702873280537>`{ses.timeline[-1].distance}m`\n> :stopwatch:`{delta.hours:02d}:{delta.minutes:02d}:{delta.seconds:02d}`\n> <:healing_heart:508220588872171522>`{new_player.lp}` · <:star_sword:622955471854370826>`{new_player.attack}` · <:star_shield:622955471640199198>`{new_player.defense}` · <:36pxGold:548661444133126185>`{after_money}` (-{100 - cp.cp_tax_money}%) · <:merit_badge:620137704662761512>`{after_merit}` (-{100 - cp.cp_tax_merit}%)\n**Return?**")
            await msg.add_reaction('\U00002705')
            try: await self.client.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author, timeout=15)
            except asyncio.TimeoutError: await ctx.send("<:guild_p:619743808959283201> Returning request is aborted!"); return
            
            await asyncio.sleep(0.1)
            self.sessionDel(ctx)
            await ctx.send(f"<:guild_p:619743808959283201> Welcome back, {ctx.author.mention}! Money and merit are also rewarded to your profile!")
            await self.client._cursor.execute(f"UPDATE personal_info SET money=money+{after_money}, merit=merit+{after_merit} WHERE id='{ctx.author.id}'; DELETE FROM pi_dungeoncheckpoint WHERE user_id='{ctx.author.id}';")
            return

        # SHOP ===============================
        elif args[0] == 'shop':
            # Checkpoint check/get
            try:
                cp = self.checkpointdict[ses.checkpoints[-1]]
            except IndexError: await ctx.send(f"<:osit:544356212846886924> You are not in a checkpoint area at the moment."); return

            try: items = cp.cp_shop.split(' || ')
            except IndexError: await ctx.send(f":x: Shop is unavailable in this checkpoint"); return


            def makeembed(top, least, pages, currentpage):
                line = ''

                for item in items[top:least]:
                    if self.itemdict[item].di_merit: price = f'<:merit_badge:620137704662761512>{self.itemdict[item].di_merit}'
                    else: price = f'<:36pxGold:548661444133126185>{self.itemdict[item].di_money}'
                    line = line + f"""\n> <a:shakin_box:625467655759069184> `{self.itemdict[item].di_code}`|**{self.itemdict[item].di_name}** ||{price}||\n> *"{self.itemdict[item].di_description}"*\n"""

                reembed = discord.Embed(title = f"SHOP ✩ **{cp.cp_name}**", colour = discord.Colour(0x011C3A), description=line)
                return reembed
                #else:
                #    await ctx.send("*Nothing but dust here...*")
            
            async def attachreaction(msg):
                await msg.add_reaction("\U000023ee")    #Top-left
                await msg.add_reaction("\U00002b05")    #Left
                await msg.add_reaction("\U000027a1")    #Right
                await msg.add_reaction("\U000023ed")    #Top-right

            pages = int(len(items)/3)
            if len(items)%3 != 0: pages += 1
            currentpage = 1
            cursor = 0

            emli = []
            for curp in range(pages):
                myembed = makeembed(currentpage*3-3, currentpage*3, pages, currentpage)
                emli.append(myembed)
                currentpage += 1

            if pages > 1:
                msg = await ctx.send(embed=emli[cursor])
                await attachreaction(msg)
            else: 
                msg = await ctx.send(embed=emli[cursor], delete_after=15)
                return

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
                    await msg.delete(); return

        # BUY ================================
        elif args[0] == 'buy':
            # Checkpoint check/get
            try:
                cp = self.checkpointdict[ses.checkpoints[-1]]
            except IndexError: await ctx.send(f"<:osit:544356212846886924> You are not in a checkpoint area at the moment."); return

            if ses.shop: await ctx.send(f"<:osit:544356212846886924> You've already shopped here!"); return
            new_player = ses.timeline[-1].player
            
            # Money check (and change)   ||   Args check
            try:
                if self.itemdict[args[1]].di_money:
                    if ses.timeline[-1].player.money < self.itemdict[args[1]].di_money: await ctx.send(f"<:osit:544356212846886924> Not enough money!"); return
                    else: ses.timeline[-1].player.money -= self.itemdict[args[1]].di_money
                elif self.itemdict[args[1]].di_merit:
                    if ses.timeline[-1].player.merit < self.itemdict[args[1]].di_merit: await ctx.send(f"<:osit:544356212846886924> Not enough merit!"); return
                    else: ses.timeline[-1].player.merit -= self.itemdict[args[1]].di_merit
            # E: No di_code given
            except IndexError: await ctx.send(f"<:osit:544356212846886924> Please provide the item code."); return
            # E: Item not found
            except KeyError: await ctx.send(f"<:osit:544356212846886924> The shop of this checkpoint doesn't have this item."); return

            # Plug into inventory
            ses.timeline[-1].player.inventory.append(self.itemdict[args[1]])

            # Inform
            await ctx.send(f":inbox_tray: Here's your `{self.itemdict[args[1]].di_name}`. Thank you for visitting!"); return



# ================== TOOLS ==================

    def sessionDel(self, ctx):
        try:
            del self.dSessionSocket[ctx.author.id]
        except KeyError: pass

    async def mobdictLoad(self):
        mobdict = {}
        packs = await self.client.quefe(f"SELECT mob_code, mob_name, description, lp, attack, defense, merit, reward FROM model_dungeonmob;", type='all')

        for pack in packs:
            mobdict[pack[0]] = dMob(pack)

        return mobdict

    async def dungeondictLoad(self):
        dungeondict = {}
        packs = await self.client.quefe(f"SELECT dungeon_code, dungeon_name, description, length, merit_per_meter, price, region, illulink FROM model_dungeon;", type='all')

        for pack in packs:
            dungeondict[pack[0]] = dDungeon(pack)

        return dungeondict

    async def checkpointdictLoad(self):
        checkpointdict = {}
        packs = await self.client.quefe(f"SELECT cp_code, cp_name, cp_description, cp_tier, cp_shop, cp_tax_money, cp_tax_merit, cp_line FROM model_dungeoncheckpoint;", type='all')

        for pack in packs:
            checkpointdict[pack[0]] = dCheckpoint(pack)

        return checkpointdict

    async def itemdictLoad(self):
        itemdict = {}
        packs = await self.client.quefe(f"SELECT di_code, di_name, description, di_lp, di_attack, di_defense, di_money, di_merit, di_line FROM model_dungeonitem;", type='all')

        for pack in packs:
            itemdict[pack[0]] = dItem(pack)

        return itemdict





def setup(client):
    client.add_cog(avaDungeon(client))





# ================== OPERATIONing CLASS ==================

class dSession:

    def __init__(self, client, ctx, mobdict, dungeondict, dungeon, checkpointdict, start_point=None, pdb_pack=None, cp_pack=None, cp_pack2=None):
        self.client = client
        self.ctx = ctx
        self.mobdict = mobdict
        self.dungeon = dungeon
        self.dungeondict = dungeondict
        self.checkpointdict = checkpointdict
        self.pdb_pack = pdb_pack
        self.cp_pack = cp_pack
        self.cp_pack2 = cp_pack2
        self.lock = False
        self.checkpoint = False
        self.shop = False
        self.checkpoints = []       # Visited checkpoints
        self.timeline = []
        if start_point: self.start_point = start_point
        else: self.start_point = datetime.now()

        # Init timeline
        self.timeline.append(dEnvironment(dPlayer(self.ctx.author, self.client, pdb_pack=self.pdb_pack, cp_pack=self.cp_pack), None, cp_pack=self.cp_pack2))

    async def updateTimeline(self, event_in=None, player_in=None):

        # Generate event
        if not event_in: event = await self.eventGenerator()
        else: event = event_in

        # RUN event
        if player_in: result = await self.eventEngine(event, player_in=player_in)
        else: result = await self.eventEngine(event, player_in=self.timeline[-1].player)

        # Check if dead
        try:
            if result == 'dead': return 'dead'
        except TypeError: pass

        # NAIVE
        if isinstance(result, dPlayer):
            # Inner recur
            if event_in: return result
            # Out-most
            else: new_player = result
        else:
            new_player = self.timeline[-1].player

        # INNER dive, but DO NOT archive the snapshot YET
        if isinstance(result, modelEvent):
            # Inner recur
            if event_in: return await self.updateTimeline(event_in=result, player_in=player_in)
            # Out-most recur
            else:
                inner_pack = await self.updateTimeline(event_in=result, player_in=new_player.fullcopy())

                # New player (?)
                if isinstance(inner_pack, dPlayer):
                    new_player = inner_pack
                
                # Check if dead
                try: 
                    if inner_pack == 'dead':
                        await self.ctx.send(f":skull: {self.ctx.author.mention}. You. DIED.")
                        return 'dead'
                    try: 
                        if new_player.lp <= 0:
                            await self.ctx.send(f":skull: {self.ctx.author.mention}. You. DIED.")
                            return 'dead'
                    except NameError: pass
                except TypeError: pass

        # Archive at the end
        if not event_in:

            # Create a snapshot
            snapshot = dEnvironment(new_player, event, distance=self.timeline[-1].distance)

            # Archive
            self.timeline.append(snapshot)

            # Inform
            try:
                if new_player.inventory: inv = f" · <a:shakin_box:625467655759069184>`{new_player.inventory[0].di_code}|{new_player.inventory[0].di_name}`"
                else: inv = ''
                msg = await self.ctx.send(f"> <:racing:622958702873280537>`{self.timeline[-1].distance}m` ||{new_player.user.mention}||╢ <:healing_heart:508220588872171522>`{new_player.lp}` · <:star_sword:622955471854370826>`{new_player.attack}` · <:star_shield:622955471640199198>`{new_player.defense}` · <:36pxGold:548661444133126185>`{new_player.money}` · <:merit_badge:620137704662761512>`{new_player.merit:.1f}`{inv}", delete_after=15)
            # E: Faux-player
            except AttributeError:
                if new_player.inventory: inv = f" · <a:shakin_box:625467655759069184>`{new_player.inventory[0].di_code}|{new_player.inventory[0].di_name}`"
                else: inv = ''
                msg = await self.ctx.send(f"> <:racing:622958702873280537>`{self.timeline[-1].distance}m` ||**{new_player.user.name}**||╢ <:healing_heart:508220588872171522>`{new_player.lp}` · <:star_sword:622955471854370826>`{new_player.attack}` · <:star_shield:622955471640199198>`{new_player.defense}` · <:36pxGold:548661444133126185>`{new_player.money}` · <:merit_badge:620137704662761512>`{new_player.merit:.1f}`{inv}", delete_after=15)

            await asyncio.sleep(0.8)
            await msg.add_reaction('a:arrow_right_ani:626231269105205288')
            
            # Continue
            try:
                await self.client.wait_for('reaction_add', check=lambda reaction, user: user == self.ctx.author and str(reaction.emoji) == '<a:arrow_right_ani:626231269105205288>', timeout=11)
                resu = await self.updateTimeline()
                return resu
            # Stop
            except asyncio.TimeoutError:
                return False

    async def eventEngine(self, event, player_in=None):
        # Prep
        line_in = random.choice(event.line)

        # Handling types
        # NAIVE ===============
        if event.type == 'naive':
            # Update distance, only when event is <NAIVE>
            if self.timeline[-1].direction == 'forward':
                self.timeline[-1].distance += 1
                player_in.merit += self.dungeon.merit_per_meter
            elif self.timeline[-1].distance:
                self.timeline[-1].distance -= 1
                player_in.merit -= self.dungeon.merit_per_meter

            if event.illulink:
                await self.ctx.send(line_in, embed=discord.Embed().set_image(url=event.illulink), delete_after=11)
            else:
                await self.ctx.send(line_in, delete_after=11)
            return False

        # CHOICE ==============
        elif event.type == 'choice':
            # Update distance, only when event is <NAIVE>
            if self.timeline[-1].direction == 'forward':
                player_in.merit += self.dungeon.merit_per_meter
            elif self.timeline[-1].distance:
                player_in.merit -= self.dungeon.merit_per_meter

            msg = await self.ctx.send(line_in, delete_after=11)

            await msg.add_reaction('\U00002705')
            await msg.add_reaction('\U0000274c')
            if not event.duration: dura = 15
            else: dura = event.duration
            try: r, u = await self.client.wait_for('reaction_add', check=lambda reaction, user: user == self.ctx.author and str(reaction.emoji) in ('\U00002705', '\U0000274c'), timeout=dura)

            # No --> node2
            except asyncio.TimeoutError:
                if event.node2: return await self.eventGenerator(event_code=random.choice(event.node2))
                else: return False

            # No --> node2
            if str(r.emoji) == '\U0000274c':
                if event.node2: return await self.eventGenerator(event_code=random.choice(event.node2))
                else: return False

            # Yes --> node1
            else:
                if event.node1: return await self.eventGenerator(event_code=random.choice(event.node1))
                else: return False

        # DEAD ================
        elif event.type == 'dead':
            await self.ctx.send(line_in, delete_after=11)
            return 'dead'



        # HURT ================
        elif event.type == 'hurt':
            if event.illulink:
                await self.ctx.send(line_in, embed=discord.Embed().set_image(url=event.illulink), delete_after=11)
            else:
                await self.ctx.send(line_in, delete_after=11)
            # Damage GET
            temp = event.value
            if not temp: temp = ['0']

            return player_in.updatePlayer(('takeDamage', temp))

        # REWARD ================
        elif event.type == 'reward':
            if event.illulink:
                await self.ctx.send(line_in, embed=discord.Embed().set_image(url=event.illulink), delete_after=11)
            else:
                await self.ctx.send(line_in, delete_after=11)
            # Reward GET
            temp = event.value
            if not temp: temp = ['0']

            return player_in.updatePlayer(('getReward', temp))

        # BATTLE ===============
        elif event.type == 'battle':
            mob_in = self.mobdict[random.choice(event.value)]
            player_in, result, mob_name = event.eventBattle(player_in, mob_in)
            if result:
                await self.ctx.send(f"{line_in}\nAnd WON against a **{mob_name}**!", delete_after=11)
                player_in.merit += mob_in.merit
            else:
                await self.ctx.send(f"{line_in}\nAnd LOST to a **{mob_name}**...", delete_after=11)
            return player_in

        # CHECKPOINT ===============
        elif event.type == 'checkpoint':
            # If checkpoint has already been visited
            cp_in = random.choice(event.value)
            if cp_in in self.checkpoints: await self.ctx.send(f"You found a checkpoint, but looks like it's been abandoned for a while...", delete_after=11); return player_in

            self.checkpoint = True
            self.checkpoints.append(self.checkpointdict[cp_in].cp_code)
            
            # Save into database
            if not await self.client._cursor.execute(f"UPDATE pi_dungeoncheckpoint SET distance={self.timeline[-1].distance}, lp={player_in.lp}, attack={player_in.base_attack}, defense={player_in.base_defense}, money={player_in.money}, merit={player_in.merit}, checkpoints='{' || '.join(self.checkpoints)}' WHERE user_id='{self.ctx.author.id}';"):
                await self.client._cursor.execute(f"INSERT INTO pi_dungeoncheckpoint VALUES (0, '{self.ctx.author.id}', '{self.dungeon.dungeon_code}', {self.timeline[-1].distance}, {player_in.lp}, {player_in.attack}, {player_in.defense}, {player_in.money}, {player_in.merit}, '{' || '.join(self.checkpoints)}', '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}');")

            await self.ctx.send(f"<:guild_p:619743808959283201> You've found an active checkpoint! All `checkpoint` commands are now enabled!", delete_after=11); return player_in

    async def eventGenerator(self, event_code=None):
        """Generate modelEvent object"""

        # GET Event info
        # Tail
        if event_code:
            code, type, line, node1, node2, vsPlayerEvent, value, illulink, duration = await self.client.quefe(f"SELECT event_code, event_type, event_line, node1, node2, event_vsPlayer, event_value, illulink, event_duration FROM model_dungeonevent WHERE event_code='{event_code}';")
        # Head
        else:
            try: code, type, line, node1, node2, vsPlayerEvent, value, illulink, duration = await self.client.quefe(f"SELECT event_code, event_type, event_line, node1, node2, event_vsPlayer, event_value, illulink, event_duration FROM model_dungeonevent WHERE node_type='head' AND range_min <= {self.timeline[-1].distance} AND {self.timeline[-1].distance} <= range_max ORDER BY RAND() LIMIT 1;")
            except IndexError: code, type, line, node1, node2, vsPlayerEvent, value, illulink, duration = await self.client.quefe(f"SELECT event_code, event_type, event_line, node1, node2, event_vsPlayer, event_value, illulink, event_duration FROM model_dungeonevent WHERE node_type='head' AND range_min <= 0 AND 0 <= range_max ORDER BY RAND() LIMIT 1;")

        return modelEvent(code, type, line, node1, node2, vsPlayerEvent, duration, value=value, illulink=illulink)

class dEnvironment:

    def __init__(self, player, event, distance=0, cp_pack=None):
        self.event = event
        self.player = player.fullcopy()
        if not cp_pack: self.distance = distance
        else: self.distance = cp_pack[0]
        self.direction = 'forward'

class modelEvent:

    def __init__(self, code, type, line, node1, node2, vsPlayerEvent, duration, value='', illulink=''):
        self.code = code
        self.type = type
        self.line = line.split(' || ')
        try: self.node1 = node1.split(' - ')
        except AttributeError: self.node1 = None
        try: self.node2 = node2.split(' - ')
        except AttributeError: self.node2 = None
        self.vsPlayerEvent = vsPlayerEvent          # List/Tuple
        try: self.value = value.split(' || ')
        except AttributeError: self.value = []
        self.illulink = illulink
        self.duration = duration



    def eventBattle(self, player, mob):
        p_attack = player.attack - mob.defense
        m_attack = mob.attack - player.defense

        try: 
            p_hit = player.lp//m_attack
        except ZeroDivisionError:
            return player, True, mob.mob_name
        try:
            m_hit = mob.lp//p_attack
        except ZeroDivisionError:
            return player, True, mob.mob_name

        print(p_hit, m_hit)
        # PLAYER lose
        if m_hit >= p_hit:
            player.lp -= m_attack*m_hit
            return player, False, mob.mob_name
        else:
            player.lp -= m_attack*m_hit
            return player, True, mob.mob_name



# ================== ENTITIES ==================

class dDungeon:

    def __init__(self, pack):
        self.dungeon_code, self.dungeon_name, self.description, self.length, self.merit_per_meter, self.price, self.region, self.illulink = pack

class dCheckpoint:

    def __init__(self, pack):
        self.cp_code, self.cp_name, self.cp_description, self.cp_tier, self.cp_shop, self.cp_tax_money, self.cp_tax_merit, self.cp_line = pack
        try: self.cp_line = self.cp_line.split(' || ')
        except AttributeError: pass

class dItem:

    def __init__(self, pack):
        self.di_code, self.di_name, self.di_description, self.di_lp, self.di_attack, self.di_defense, self.di_money, self.di_merit, self.di_line = pack

class dPlayer:

    def __init__(self, user, client, lp=100, money=0, pdb_pack=None, cp_pack=None):
        self.client = client
        self.user = user
        # From cache
        if not cp_pack:
            self.lp, self.attack, self.defense, self.base_attack, self.base_defense, self.merit = pdb_pack
            # Construct
            if not self.attack and not self.defense:
                self.base_attack = math.ceil(self.base_attack)
                self.base_defense = self.base_attack
                self.attack = self.base_attack
                self.defense = self.base_defense
            self.money = money
        # From db
        else:
            self.lp, self.base_attack, self.base_defense, self.money, self.merit = cp_pack
            self.attack = self.base_attack
            self.defense = self.base_defense
        self.effect = []
        self.inventory = []
        self.event_dict = {'takeDamage': self.player_takeDamage,
                            'getReward': self.player_getReward}



    def updatePlayer(self, *args):
        for event in args:
            self.event_dict[event[0]](event[1])

        # return self.fullcopy()
        return self

    def fullcopy(self):
        temp = dPlayer(self.user, lp=self.lp, client=self.client, money=self.money, pdb_pack=(self.lp, self.attack, self.defense, self.base_attack, self.base_defense, self.merit))
        temp.effect = deepcopy(self.effect)
        temp.inventory = deepcopy(self.inventory)
        return temp



    def player_takeDamage(self, damage):
        for value in damage:
            try: self.lp -= int(value)
            except TypeError: pass

    def player_getReward(self, reward):
        for value in reward:
            # Money
            try:
                self.money += int(value)
            # Item ????
            except: pass

class dMob:
    
    def __init__(self, pack):
        self.mob_code, self.mob_name, self.description, self.lp, self.attack, self.defense, self.merit, self.reward = pack
