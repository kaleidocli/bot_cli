import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from .avaTools import avaTools
from .avaUtils import avaUtils

class avaTrivia:
    def __init__(self, client):
        self.client = client

        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)



    async def on_ready(self):
        print("|| Trivia ---- READY!")



    @commands.command(aliases=['skt'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def sekaitime(self, ctx):
        year, month, day, hour, minute = await self.client.loop.run_in_executor(None, self.utils.time_get)
        calendar_format = {'month': {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}}
        a = ['st', 'nd', 'rd']
        if day%10 in [1, 2, 3]:
            postfix = a[(day%10) - 1]
        else: postfix = 'th'
        await ctx.send(f"__=====__ `{hour:02d}:{minute:02d}` :calendar_spiral: {calendar_format['month'][month]} {day}{postfix}, {year} __=====__")

    @commands.command(aliases=['worldinfo'])
    @commands.cooldown(1, 30, type=BucketType.user)
    async def sekaiinfo(self, ctx):
        users = await self.client.quefe(f"SELECT COUNT(id) FROM personal_info;")
        races = await self.client.quefe(f"SELECT COUNT(race_code) FROM model_race;")
        c_quests = await self.client.quefe(f"SELECT COUNT(user_id) FROM pi_quests;")
        quests = await self.client.quefe(f"SELECT COUNT(quest_code) FROM model_quest;")
        animals = await self.client.quefe(f"SELECT COUNT(ani_code) FROM model_animal;")
        c_mobs = await self.client.quefe(f"SELECT COUNT(id_counter) FROM environ_mob;")
        mobs = await self.client.quefe(f"SELECT COUNT(mob_code) FROM environ_diversity;")
        formulas = await self.client.quefe(f"SELECT COUNT(formula_code) FROM model_formula;")
        ingredients = await self.client.quefe(f"SELECT COUNT(ingredient_code) FROM model_ingredient;")
        items = await self.client.quefe(f"SELECT COUNT(item_code) FROM model_item;")
        p_items = await self.client.quefe(f"SELECT COUNT(item_id) FROM pi_inventory;")

        year, month, day, hour, minute = await self.client.loop.run_in_executor(None, self.utils.time_get)

        reembed = discord.Embed(title='**T H E  P R A L A E Y R**', description=f"```Structured by 5 different regions, Pralaeyr has lasted for {year} years, {month} months, {day} days, {hour} hours and {minute} minutes```", colour = discord.Colour(0x011C3A))
        reembed.add_field(name=":couple: Population", value=f"· `{users[0]}`, with `{races[0]}` different races.")
        reembed.add_field(name=":smiling_imp: Mobs and Animals", value=f"· `{c_mobs[0]}` alive mobs, with `{mobs[0]}` different kind of mobs.\n· `{animals[0]}` kind of animals.")
        reembed.add_field(name=":package: Items and Ingredients", value=f"· `{p_items[0]}` current items, with `{ingredients[0]}` kind of ingredients and `{items[0]}` kind of items.")
        reembed.add_field(name=":tools: Formulas and Quests", value=f"· `{formulas[0]}` formulas.\n· `{c_quests[0]}` current quests, with `{quests[0]}` different kind of quests.")

        await ctx.send(embed=reembed)

    @commands.command(aliases=['richest'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def toprich(self, ctx):
        ret = await self.client.quefe(f"SELECT name, age, money FROM personal_info ORDER BY money DESC LIMIT 10", type='all')

        line = ''; count = 0
        for u in ret:
            count += 1
            line = line + f"{count} | **{u[0]}** ({u[1]}) with <:36pxGold:548661444133126185> **{u[2]}**\n"

        await ctx.send(embed=discord.Embed(description=line, colour=0xFFC26F))

    @commands.command(aliases=['topmerit', 'honorest'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def tophonor(self, ctx):
        ret = await self.client.quefe(f"SELECT name, age, merit FROM personal_info ORDER BY merit DESC LIMIT 10", type='all')

        line = ''; count = 0
        for u in ret:
            count += 1
            line = line + f"{count} | **{u[0]}** ({u[1]}) with a merit **{u[2]}**\n"

        await ctx.send(embed=discord.Embed(description=line, colour=0xFFC26F))

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def topkill(self, ctx):
        ret = await self.client.quefe(f"SELECT name, EVO, kills FROM personal_info ORDER BY kills DESC LIMIT 10", type='all')

        line = ''; count = 0
        for u in ret:
            count += 1
            line = line + f"{count} | **{u[0]}** (`EVO-{u[1]}`) with **{u[2]}** kills\n"

        await ctx.send(embed=discord.Embed(description=line, colour=0xFFC26F))

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def topdeath(self, ctx):
        ret = await self.client.quefe(f"SELECT name, EVO, deaths FROM personal_info ORDER BY deaths DESC LIMIT 10", type='all')

        line = ''; count = 0
        for u in ret:
            count += 1
            line = line + f"{count} | **{u[0]}** (`EVO-{u[1]}`) with **{u[2]}** deaths\n"

        await ctx.send(embed=discord.Embed(description=line, colour=0xFFC26F))

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def topwin(self, ctx):
        ret = await self.client.quefe(f"SELECT (SELECT name FROM personal_info WHERE id=user_id), duel_win, duel_lost FROM misc_status ORDER BY duel_win DESC LIMIT 10", type='all')

        line = ''; count = 0
        for u in ret:
            count += 1
            line = line + f"{count} | **{u[0]}** have won **{u[1]}** duels and lost **{u[2]}** duels\n"

        await ctx.send(embed=discord.Embed(description=line, colour=0xFFC26F))



def setup(client):
    client.add_cog(avaTrivia(client))
