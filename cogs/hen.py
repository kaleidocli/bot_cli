import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import random
import asyncio
from os import listdir
import nekos


class allhen(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.nhen_type = ''


    @commands.command()
    @commands.cooldown(1, 10, type=BucketType.channel)
    async def hen(self, ctx, *args):

        # NSFW channel check
        if not ctx.channel.is_nsfw():
            await ctx.send(":no_entry_sign: NSFW channel only!")
            return

        hen_dir = {'bdsm': 'D:/____ Green Corner ____/The Artworks/Fraud/Sinatio/Rape + Humi + BDSM/BDSM/All',
                    'tentacles': 'D:/____ Green Corner ____/The Artworks/Fraud/Sinatio/Tentacles/All',
                    'bestiality': 'D:/____ Green Corner ____/The Artworks/Fraud/Sinatio/Bestiality/All',
                    'milking': 'D:/____ Green Corner ____/The Artworks/Fraud/Sinatio/Milking/All',
                    'mix': 'D:/____ Green Corner ____/The Artworks/Fraud/Sinatio/AMix/All',
                    'bukake': 'D:/____ Green Corner ____/The Artworks/Fraud/The AFTERMATH/TUMblr/bukkakeholocaust.tumblr.com',
                    'cos_1': 'D:/____ Green Corner ____/The Artworks/Fraud/The AFTERMATH/TUMblr/donshofer',
                    'swimsuit': 'D:/____ Green Corner ____/The Artworks/Fraud/The AFTERMATH/TUMblr/yuttaro3'}
        raw = list(args)
        tags_list = list(hen_dir.keys())
        
        #Check if there's a input tag. If not, pick a random one from tags_list
        if raw:
            #Check if raw[0] is in hen_dir's keys dict
            if raw[0] not in tags_list: await ctx.send(f"Please use one of the following tags: `{'` `'.join(tags_list)}`"); return
        else:
            raw.append(random.choice(tags_list))

        #Function to get hen_fname list (require raw[0] and hen_dir)
        def hfname_get():
            return listdir(hen_dir[raw[0]])
        hen_fname = await self.client.loop.run_in_executor(None, hfname_get)

        def RUM_check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == "\U0001F3D3"

        # First package
        fff = discord.File(f"{hen_dir[raw[0]]}/{random.choice(hen_fname)}", filename='package.png')
        eee = discord.Embed()
        eee.set_image(url="attachment://package.png")

        bmsg = await ctx.send(f"""```✔✔✔ || {raw[0]}```""")
        emsg = await ctx.send(file=fff, embed=eee)
        await bmsg.add_reaction('\U0001F3D3')

        while True:

            # REload
            fff = discord.File(f"{hen_dir[raw[0]]}/{random.choice(hen_fname)}", filename='package.png')
            eee = discord.Embed()
            eee.set_image(url="attachment://package.png")

            try: 
                await self.client.wait_for('reaction_add', check=RUM_check, timeout=60)
            except asyncio.TimeoutError:
                await emsg.delete()
                await bmsg.edit(content=f"""```✘✘✘ || {raw[0]}```""")
                return

            await emsg.delete()
            emsg = await ctx.send(file=fff, embed=eee)
        
    @commands.command()
    @commands.cooldown(1, 10, type=BucketType.channel)
    async def nhen(self, ctx, *args):
        raw = list(args)

        # NSFW channel check
        if not ctx.channel.is_nsfw():
            await ctx.send(":no_entry_sign: NSFW channel only!")
            return

        if raw:
            def RUM_check(reaction, user):
                return user == ctx.author and str(reaction.emoji) == "\U0001F3D3"

            try:
                while True:
                    bmsg = await ctx.send(ctx.message.channel, nekos.img(raw[0]))
                    await bmsg.add_reaction('\U0001F3D3')

                    try: await self.client.wait_for('reaction_add', check=RUM_check, timeout=60)
                    except asyncio.TimeoutError: break
            except:
                await ctx.send(f":interrobang: Tag `{raw[0]}`` not found!")
        else:
            await ctx.send(":warning: Please give a correct tag.")



def setup(client):
    client.add_cog(allhen(client))












