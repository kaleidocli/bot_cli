import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors

import asyncio
import random
from copy import deepcopy

from .avaTools import avaTools
from .avaUtils import avaUtils
from utils import checks

class avaDungeon(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.dSessionSocket = {}
        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)



    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(1)
        self.mobdict = await self.mobdictLoad()
        self.dungeondict = await self.dungeondictLoad()

        print("|| Dungeon ---- READY!")



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


    @commands.command()
    @commands.cooldown(1, 2, type=BucketType.user)
    async def dungeon(self, ctx, *args):

        # Check ===============
        try:
            if args[0] == 'enter':
                if not await self.tools.ava_scan(ctx.message, type='life_check'): return

                try: temp = self.dungeondict[args[1]]
                except IndexError: await ctx.send("<:osit:544356212846886924> Missing `dungeon_code`!"); return
                except KeyError: await ctx.send("<:osit:544356212846886924> Unknown `dungeon_code`."); return
                temp.price = 0

                money, lp, merit = await self.client.quefe(f"SELECT money, lp, merit FROM personal_info WHERE id='{ctx.author.id}';")
                if money < temp.price: await ctx.send(f"<:osit:544356212846886924> You need <:36pxGold:548661444133126185>{temp.price} as entry fee to enter this dungeon, {ctx.author.mention}!"); return
 
                msg = await ctx.send(f"<:guild_p:619743808959283201> A snapshot of your character will transmitted into dungeon `{temp.dungeon_code}`|**{temp.dungeon_name}**. That snapshot will not be saved until next checkpoint.\n<a:RingingBell:559282950190006282> Entry fee is <:36pxGold:548661444133126185>{temp.price}. Do you wish to continue?")
                await msg.add_reaction("\U00002705")
                try: await self.client.wait_for('reaction_add', timeout=15, check=lambda r, u: u.id == ctx.author.id and r.message.id == msg.id)
                except asyncio.TimeoutError: await ctx.send("<:osit:544356212846886924> Entry request is aborted."); return

                self.dSessionSocket[ctx.author.id] = dSession(self.client, ctx, self.mobdict, self.dungeondict, temp, pdb_pack=(lp, merit))
                await self.client._cursor.execute(f"UPDATE personal_info SET money=money-{temp.price} WHERE id='{ctx.author.id}';")
                await ctx.send(f"<:guild_p:619743808959283201> Your snapshot has been transmitted into `{temp.dungeon_code}`|**{temp.dungeon_name}**! May the Olds look upon you...")
                return
            else: return
        except IndexError: pass

        try: your_session = self.dSessionSocket[ctx.author.id]
        except KeyError: await ctx.send("<:osit:544356212846886924> You haven't enter any dungeon yet. Please use `dungeon enter [dungeon_code]`."); return

        your_session.ctx = ctx
        res = await your_session.updateTimeline() 

        # In case dead
        try:
            if res == 'dead': self.sessionDel(ctx)
        except TypeError: pass




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




def setup(client):
    client.add_cog(avaDungeon(client))






class dSession:

    def __init__(self, client, ctx, mobdict, dungeondict, dungeon, pdb_pack=None):
        self.client = client
        self.ctx = ctx
        self.mobdict = mobdict
        self.dungeon = dungeon
        self.dungeondict = dungeondict
        self.pdb_pack = pdb_pack
        self.timeline = []

    async def updateTimeline(self, event_in=None, player_in=None):
        print("UPDDAAAAAAAAAAAAAAAA", event_in)

        # Generate event
        if not event_in: event = await self.eventGenerator()
        else: event = event_in
        # Timeline check
        if not self.timeline:
            self.timeline.append(dEnvironment(dPlayer(self.ctx.author, self.client, pdb_pack=self.pdb_pack), event))

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
        print("NEW_PLAYERRRRRRRR: ", new_player, result)

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
            await self.ctx.send(f"> `LP: {new_player.lp}` · `ATK/DEF: {new_player.attack}/{new_player.defense}` · `Distance: {self.timeline[-1].distance}m`\n> <:36pxGold:548661444133126185>{new_player.money} <:merit_badge:620137704662761512>{new_player.merit}", delete_after=15)

            return False





    async def eventEngine(self, event, player_in=None):
        print('EVENT ENNNNGGGGGGGGGGINE', player_in)
        # Type Handling

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
                await self.ctx.send(event.line, embed=discord.Embed().set_image(url=event.illulink), delete_after=11)
            else:
                await self.ctx.send(event.line, delete_after=11)
            return False

        # CHOICE ==============
        elif event.type == 'choice':
            msg = await self.ctx.send(event.line, delete_after=11)

            def R_check(reaction, user):
                return user == self.ctx.author and str(reaction.emoji) in ('\U00002705', '\U0000274c')

            await msg.add_reaction('\U00002705')
            await msg.add_reaction('\U0000274c')
            if not event.duration: dura = 15
            else: dura = event.duration
            try: r, u = await self.client.wait_for('reaction_add', check=R_check, timeout=dura)

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
            await self.ctx.send(event.line, delete_after=11)
            return 'dead'



        # HURT ================
        elif event.type == 'hurt':
            if event.illulink:
                await self.ctx.send(event.line, embed=discord.Embed().set_image(url=event.illulink), delete_after=11)
            else:
                await self.ctx.send(event.line, delete_after=11)
            # Damage GET
            temp = event.value
            if not temp: temp = ['0']

            return player_in.updatePlayer(('takeDamage', temp))

        # REWARD ================
        elif event.type == 'reward':
            if event.illulink:
                await self.ctx.send(event.line, embed=discord.Embed().set_image(url=event.illulink), delete_after=11)
            else:
                await self.ctx.send(event.line, delete_after=11)
            # Reward GET
            temp = event.value
            if not temp: temp = ['0']

            return player_in.updatePlayer(('getReward', temp))

        # BATTLE ===============
        elif event.type == 'battle':
            mob_in = random.choice(self.mobdict[event.value])
            player_in, result = event.eventBattle(player_in, mob_in)
            if result:
                await self.ctx.send(f"{event.line}\nAnd WON!", delete_after=11)
                player_in.merit += mob_in.merit
            else:
                await self.ctx.send(f"{event.line}\nAnd LOST...", delete_after=11)
            return player_in


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

    def __init__(self, player, event, distance=0):
        self.event = event
        self.player = player.fullcopy()
        self.distance = distance
        self.direction = 'forward'


class dDungeon:

    def __init__(self, pack):
        self.dungeon_code, self.dungeon_name, self.description, self.length, self.merit_per_meter, self.price, self.region, self.illulink = pack




class dPlayer:

    def __init__(self, user, client, lp=100, money=0, pdb_pack=None):
        self.client = client
        self.user = user
        self.lp, self.merit = pdb_pack
        self.attack = 0
        self.defense = 0
        self.money = money
        self.effect = []
        self.tube = []
        self.event_dict = {'takeDamage': self.player_takeDamage,
                            'getReward': self.player_getReward}



    def updatePlayer(self, *args):
        print("Update PLAYER")
        for event in args:
            print(event, args)
            self.event_dict[event[0]](event[1])

        # return self.fullcopy()
        return self

    def fullcopy(self):
        temp = dPlayer(self.user, lp=self.lp, client=self.client, money=self.money, pdb_pack=(self.lp, self.merit))
        temp.effect = deepcopy(self.effect)
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




class modelEvent:

    def __init__(self, code, type, line, node1, node2, vsPlayerEvent, duration, value='', illulink=''):
        self.code = code
        self.type = type
        self.line = line
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

        p_hit = player.lp//m_attack
        m_hit = mob.lp//p_attack

        # PLAYER lose
        if m_hit <= p_hit:
            player.lp -= m_attack*m_hit
            return player, False
        else:
            player.lp -= m_attack*m_hit
            return player, True        












