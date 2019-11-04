import discord
from discord.ext import commands
from pybooru import Danbooru
from pybooru import Moebooru

import asyncio
import functools
import random

class dan(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.dan_client = Danbooru('danbooru', username='aklei', api_key='PubbhbW6nutC3yiFrBCrZs7S')
        self.yan_client = Moebooru(site_url='https://yande.re', username='aklei', password='111111')
        self.default_tags = ['yuri']

    @commands.command(pass_context=True)
    async def yhen(self, ctx, *args):
        """
        #Checking the nsfw_mode value
        if not self.client.settings[ctx.guild.id]['nsfw_mode']:
            await ctx.channel.send(":no_entry_sign: Please check if the `NSFW` mode is **enabled**.")
            return
        """

        # NSFW channel check
        if not ctx.channel.is_nsfw():
            await ctx.send(":no_entry_sign: NSFW channel only!")
            return

        async def a(msg, post):
            check = '0'
            #REACTION LOOP
            while True:
                #Wait for reaction
                try: reac = await self.client.wait_for('reaction_add', check=lambda r, u: u == ctx.author and r.message.id == msg.id, timeout=60)
                except asyncio.TimeoutError: check = '1'; break
                #Check if reac is not None. If None, check's set to '1', hence quit the REACTION LOOP and return True to the outside loop
                if not reac: check = '1'; break
                #Check if reac's string == <Tag_emoji>. If true, send tags, then continue the REACTION LOOP
                elif str(reac[0].emoji) == '\U0001f4c4':
                    #Send tags
                    tags = f"`{post['tags'].replace(' ', '` `')}`"
                    await self.client.send_message(ctx.message.channel, tags)
                elif str(reac[0].emoji) == '\U0001f512':
                    await msg.add_reaction('\U0001f513')
                    try: a = await self.client.wait_for('reaction_add', check=lambda r, u: r.emoji == '\U0001f513' and u == ctx.author and r.message.id == msg.id, timeout=420)
                    except asyncio.TimeoutError: check = '1'; break
                    if not a: break
                    await msg.add_reaction('\U0001f512')
                #Check if reac's string == <Next_emoji>. If true, quit the REACTION LOOP
                elif str(reac[0].emoji) == '\U000027a1':
                    break
                #else: check = '1'; break

            #If return False, outside loop will continue
            if check == '0': return False
            #If return True, outside loop will be stopped
            else: return True

        raw = list(args)
        if len(raw) > 2: await self.client.send_message(ctx.message.channel, "No more than 2 tags!"); return
        if raw:    
            tag_string = ' '.join(raw)
        else: tag_string = ' '.join(self.default_tags)

        #Get img(s) (This function return a list of x post (x==limit))
        while True:
            try: func = functools.partial(self.yan_client.post_list, limit=100, tags=tag_string, page=random.choice(range(50))); break
            except ConnectionError: pass
        all_posts = await self.client.loop.run_in_executor(None, func)
        msg = None
        
        async def generate():
            try: post = random.choice(all_posts)
            except IndexError: await ctx.channel.send(f":warning: {ctx.message.author.mention}, tags `{' '.join(tag_string)}` not found!"); return
            #Send img
            #await self.client.send_message(ctx.message.channel, f"**Tags:** `{tag_string.replace(' ', '` `')}`")
            hen_box = discord.Embed(
                title = f"**Tags:** `{tag_string.replace(' ', '` `')}`",
                colour = discord.Colour(0x011C3A),
            )
            try:
                hen_box.set_image(url=post['file_url'])
            except KeyError:
                print(f"KEY_ERROR========================\n{post}")
            print(post)
            return hen_box, post
        
        hen_box, post = await generate()
        msg_console = await ctx.channel.send(":keyboard: **CONSOLE**")
        #Add emo to msg_console.
        await msg_console.add_reaction('\U0001f4c4')   #Tag_emoji
        await msg_console.add_reaction('\U000027a1')   #Next_emoji
        await msg_console.add_reaction('\U0001f512')   #Lock_emoji
        #Send hen_box
        msg = await ctx.channel.send(embed=hen_box)

        while True:
            #Wait for the emo loop. If return True, break, else, continue
            check_out = await a(msg_console, post)
            # if check_out: await self.client.delete_message(msg); break
            #else: await self.client.delete_message(msg)
            hen_box, post = await generate()
            await msg.edit(embed=hen_box)


    @commands.command(pass_context=True)
    async def dhen(self, ctx, *args):
        #Checking the nsfw_mode value
        """
        if not self.client.settings[str(ctx.guild.id)]['nsfw_mode']:
            await ctx.channel.send(":no_entry_sign: Please check if the `NSFW` mode is **enabled**.")
            return
        """

        # NSFW channel check
        if not ctx.channel.is_nsfw():
            await ctx.send(":no_entry_sign: NSFW channel only!")
            return

        async def a(msg, posts_list):
            check = '0'
            #REACTION LOOP
            while True:
                #Wait for reaction
                try: reac = await self.client.wait_for('reaction_add', check=lambda r, u: u == ctx.author and r.message.id == msg.id, timeout=60)
                except asyncio.TimeoutError: check = '1'; break
                #Check if reac is not None. If None, check's set to '1', hence quit the REACTION LOOP and return True to the outside loop
                if not reac: check = '1'; break
                #Check if reac's string == <Tag_emoji>. If true, send tags, then continue the REACTION LOOP
                elif str(reac[0].emoji) == '\U0001f4c4':
                    #Send tags
                    tags = f"`{posts_list[0]['tag_string_general'].replace(' ', '` `')}`"
                    await ctx.send(tags)
                elif str(reac[0].emoji) == '\U0001f512':
                    await msg.add_reaction('\U0001f513')
                    try: a = await self.client.wait_for('reaction_add', check=lambda r, u: r.emoji == '\U0001f513' and u == ctx.author and r.message.id == msg.id, timeout=420)
                    except asyncio.TimeoutError: check = '1'; break
                    if not a: break
                    await msg.add_reaction('\U0001f512')
                #Check if reac's string == <Next_emoji>. If true, quit the REACTION LOOP
                elif str(reac[0].emoji) == '\U000027a1':
                    break
                #else: check = '1'; break

            #If return False, outside loop will continue
            if check == '0': return False
            #If return True, outside loop will be stopped
            else: return True

        raw = list(args)
        if len(raw) > 2: await self.client.send_message(ctx.message.channel, "No more than 2 tags!"); return
        if raw:
            tag_string = ' '.join(raw)
        else: tag_string = ' '.join(self.default_tags)

        async def generate():
            #Get img(s) (This function return a list of x post (x==limit))
            func = functools.partial(self.dan_client.post_list, limit=1, tags=tag_string, random=True)
            posts_list = await self.client.loop.run_in_executor(None, func)
            #Send img
            #await self.client.send_message(ctx.message.channel, f"**Tags:** `{tag_string.replace(' ', '` `')}`")
            hen_box = discord.Embed(
                title = f"**Tags:** `{tag_string.replace(' ', '` `')}`",
                colour = discord.Colour(0x011C3A),
            )
            try:
                hen_box.set_image(url=posts_list[0]['file_url'])
            except KeyError: print(f"KEY_ERROR========================\n{posts_list[0]}")
            except IndexError: await ctx.channel.send(f":warning: {ctx.message.author.mention}, tags `{tag_string}` not found!"); return
            print(f"DHEN -------------- {ctx.author.name} in {ctx.guild.name}")
            return hen_box, posts_list

        try: hen_box, posts_list = await generate()
        except TypeError: await ctx.channel.send(f":warning: {ctx.message.author.mention}, tags `{tag_string}` not found!"); return
        msg_console = await ctx.channel.send(":keyboard: **CONSOLE**")
        #Add emo to msg_console.
        await msg_console.add_reaction('\U0001f4c4')   #Tag_emoji
        await msg_console.add_reaction('\U000027a1')   #Next_emoji
        await msg_console.add_reaction('\U0001f512')   #Lock_emoji
        #Send hen_box
        msg = await ctx.channel.send(embed=hen_box)

        while True:
            hen_box, posts_list = await generate()
            #Wait for the emo loop. If return True, break, else, continue
            check_out = await a(msg_console, posts_list)
            if check_out == '1': break
            # if check_out: await self.client.delete_message(msg); break
            await msg.edit(embed=hen_box)

            
    @commands.command(pass_context=True)
    async def ddfadd(self, ctx, *args, aliases=['+d']):

        #Checking the nsfw_mode value
        if not self.client.settings[ctx.guild.id]['nsfw_mode']:
            await ctx.channel.send(":no_entry_sign: Please check if the `NSFW` mode is **enabled**.")
            return

        lenn = self.default_tags
        if args:   
            self.default_tags += list(args)
            #Check if the tags list is longer than 2
            if len(self.default_tags) > 2: self.default_tags = lenn; await self.client.send_message(ctx.message.channel, "No more than 2 tags!"); return
        else: pass
        await self.client.send_message(ctx.message.channel, f"**Default tags:** `{'` `'.join(self.default_tags)}`")

    @commands.command(pass_context=True)
    async def ddfremove(self, ctx, *args, aliases=['-d']):
        
        #Checking the nsfw_mode value
        if not self.client.settings[ctx.guild.id]['nsfw_mode']:
            await ctx.channel.send(":no_entry_sign: Please check if the `NSFW` mode is **enabled**.")
            return

        if args:
            self.default_tags = list(set(self.default_tags) - set(args))
        else: pass
        await self.client.send_message(ctx.message.channel, f"**Default tags:** `{'` `'.join(self.default_tags)}`")

    @commands.command(pass_context=True)
    async def drelevant(self, ctx, *args):

        #Checking the nsfw_mode value
        if not self.client.settings[ctx.guild.id]['nsfw_mode']:
            await ctx.channel.send(":no_entry_sign: Please check if the `NSFW` mode is **enabled**.")
            return

        raw = list(args)
        cate = '0'
        cate_dict = {'0': 'General', '1': 'Artist', '3': 'Copyright', '4': 'Character'}

        try:
            name = raw[0]
            if len(raw) >= 2:
                if raw[1] in ['0', '1', '3', '4']:
                    cate = raw[1]
        except IndexError:
            await self.client.send_message(ctx.message.channel, "Missing args!")
        result = self.dan_client.tag_related(name, category=cate)
        tags = [x[0] for x in result['tags']]
        await self.client.send_message(ctx.message.channel, f"**Search results for <{raw[0]}> by <{cate_dict[cate]}>** \n`{'` `'.join(tags)}`")

def setup(client):
    client.add_cog(dan(client))








