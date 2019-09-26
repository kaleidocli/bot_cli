"""Copied from "Example.py" (https://discordbots.org/api/docs#pylib)"""

import dbl
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

import asyncio
import logging

# from pyngrok import ngrok
from .configs import SConfig


class DiscordBotsOrgAPI(commands.Cog):
    """Handles interactions with the discordbots.org API"""

    def __init__(self, bot):
        # # ngrok
        # ngrok.set_auth_token()
        # temp = ngrok.get_ngrok_process()
        # try: temp.kill()
        # except AttributeError: pass
        # try:
        #     tunnels = ngrok.get_tunnels()
        #     public_url = tunnels[0].public_url
        # except IndexError:
        #     public_url = ngrok.connect()

        self.bot = bot
        self.token = self.bot.myconfig.DBL_token
        self.dblpy = dbl.DBLClient(self.bot, self.token, webhook_path='/dblwebhook', webhook_auth='password', webhook_port=5000)
        self.updating = self.bot.loop.create_task(self.update_stats())

    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count"""
        while not self.bot.is_closed():
            logger.info('Attempting to post server count')
            try:
                await self.dblpy.post_guild_count()
                logger.info('Posted server count ({})'.format(self.dblpy.guild_count()))
            except Exception as e:
                logger.exception('Failed to post server count\n{}: {}'.format(type(e).__name__, e))
            await asyncio.sleep(1800)



    @commands.Cog.listener()
    async def on_ready(self):
        # print(await self.dblpy.get_bot_upvotes())
        pass

    @commands.Cog.listener()
    async def on_dbl_vote(self, d):
        user = self.bot.get_user(int(d['user']))
        
        if not await self.bot._cursor.execute(f"SELECT * FROM personal_info WHERE id='{user.id}';"):
            await user.send(f"Thank you for your support, {user.name} <3 It seems that you don't have a character in Kaleido_Cli, so we cannot reward you. But don't worry we still love you :>"); return

        await self.bot._cursor.execute(f"SELECT func_ig_reward('{user.id}', 'ig85', 1);")
        await user.send(f"Thank you for your supportt, **{user.name}** :heart: An item `ig85`|**Normal Ticket** was sent to your inventory.\nGood luck and have fun, Remnant!"); return

    @commands.Cog.listener()
    async def on_dbl_test(self, d):
        user = self.bot.get_user(int(d['user']))
        
        if not await self.bot._cursor.execute(f"SELECT * FROM personal_info WHERE id='{user.id}';"):
            await user.send(f"Thank you for your support, **{user.name}** :heart: It seems that you don't have a character in Kaleido_Cli, so we cannot reward you. But don't worry we still love you :>"); return

        await self.bot._cursor.execute(f"SELECT func_ig_reward('{user.id}', 'ig85', 1);")
        await user.send(f"Thank you for your supportt, **{user.name}** :heart: An item `ig85`|**Normal Ticket** was sent to your inventory.\nGood luck and have fun, Remnant!"); return



    @commands.command()
    @commands.cooldown(1, 2, type=BucketType.user)
    async def vote(self, ctx):
        await ctx.send(embed=discord.Embed(description=f"**Love me? Love me not?** You can [vote](https://discordbots.org/bot/449278811369111553/vote) me for a slot ticket, yea? Thank you, very much~!", colour = discord.Colour(0x36393E)))




def setup(bot):
    global logger
    logger = logging.getLogger('bot')
    bot.add_cog(DiscordBotsOrgAPI(bot))