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
        print("|| Dungeon ---- READY!")



    @commands.command()
    @commands.cooldown(1, 2, type=BucketType.user)
    async def dungeon(self, ctx, *args):
        your_session = self.sessionGet(ctx)
        your_session.ctx = ctx
        res = await your_session.updateTimeline() 

        # In case dead
        try:
            if res == 'dead': self.sessionDel(ctx)
        except TypeError: pass



    def sessionGet(self, ctx):
        try: return self.dSessionSocket[ctx.author.id]
        except KeyError:
            temp = dSession(self.client, ctx)
            self.dSessionSocket[ctx.author.id] = temp
            return temp

    def sessionDel(self, ctx):
        try:
            del self.dSessionSocket[ctx.author.id]
        except KeyError: pass




def setup(client):
    client.add_cog(avaDungeon(client))






class dSession:

    def __init__(self, client, ctx):
        self.client = client
        self.ctx = ctx
        self.timeline = []

    async def updateTimeline(self, event_in=None, player_in=None):
        print("UPDDAAAAAAAAAAAAAAAA", event_in)

        # Generate event
        if not event_in: event = await self.eventGenerator()
        else: event = event_in
        # Timeline check
        if not self.timeline:
            self.timeline.append(dEnvironment(dPlayer(self.ctx.author), event))

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
                    if inner_pack == 'dead': return 'dead'
                    try: 
                        if new_player.lp <= 0: return 'dead'
                    except NameError: pass
                except TypeError: pass

        # Archive at the end
        if not event_in:

            # Update distance
            self.timeline[-1].distance += 1

            # Create a snapshot
            snapshot = dEnvironment(new_player, event, distance=self.timeline[-1].distance)

            # Archive
            self.timeline.append(snapshot)

            # Inform
            await self.ctx.send(f"> `LP: {new_player.lp}` · ${new_player.money} · `Distance: {self.timeline[-1].distance}m`", delete_after=15)

            return False





    async def eventEngine(self, event, player_in=None):
        print('EVENT ENNNNGGGGGGGGGGINE', player_in)
        # Type Handling
        # CHOICE ==============
        if event.type == 'choice':
            msg = await self.ctx.send(event.line, delete_after=16)

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
            await self.ctx.send(event.line, delete_after=16)
            return 'dead'



        # HURT ================
        elif event.type == 'hurt':
            if event.illulink:
                await self.ctx.send(event.line, embed=discord.Embed().set_image(url=event.illulink), delete_after=16)
            else:
                await self.ctx.send(event.line, delete_after=16)
            # Damage GET
            temp = event.value
            if not temp: temp = ['0']

            return player_in.updatePlayer(('takeDamage', temp))

        # HURT ================
        elif event.type == 'reward':
            if event.illulink:
                await self.ctx.send(event.line, embed=discord.Embed().set_image(url=event.illulink), delete_after=16)
            else:
                await self.ctx.send(event.line, delete_after=16)
            # Reward GET
            temp = event.value
            if not temp: temp = ['0']

            return player_in.updatePlayer(('getReward', temp))

        if event.illulink:
            await self.ctx.send(event.line, embed=discord.Embed().set_image(url=event.illulink), delete_after=16)
        else:
            await self.ctx.send(event.line, delete_after=16)
        return False

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




class dPlayer:

    def __init__(self, player, lp=100, money=0):
        self.player = player
        self.lp = lp
        self.money = money
        self.effect = []
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
        temp = dPlayer(self.player, lp=self.lp, money=self.money)
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












