import traceback
import sys
from discord.ext import commands
import discord
from datetime import timedelta
import asyncio
import concurrent
from pymysql import err as mysqlError




class ErrorHandler(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.client.realready = True

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""
        print("==================================")
        print(error)
        print(type(error))
        print("============= ERROR ==============")
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.channel.send(":no_entry_sign: You wish :>")
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr); return
        elif isinstance(error, commands.errors.CommandOnCooldown):
            await ctx.channel.send(f"<a:ghostcat3:531060433927536650> Take a breath, **{ctx.author.name}**. Wait `{timedelta(seconds=int(error.retry_after))}`!", delete_after=5)
            #await ctx.channel.send(f"<:fufu:508437298808094742> Etou... **{ctx.author.name}**? Can you not shut the fuck up for **`{timedelta(seconds=int(error.retry_after))}`**.", delete_after=5)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr); return
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.channel.send(f"<a:ghostcat3:531060433927536650> {error}")
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr); return
        elif isinstance(error, commands.errors.CommandNotFound):
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr); return
        elif isinstance(error, asyncio.TimeoutError) or isinstance(error, discord.errors.Forbidden):
            return
        elif isinstance(error, mysqlError.OperationalError):
            await self.client.thp.mysqlReload()
        else:
            try:
                try:
                    await self.client.owner.send(f"User `{ctx.author.id}`|**{ctx.author.name}** from `{ctx.channel.id}` of `{ctx.guild.id}`|**{ctx.guild.name}**")
                    await self.client.owner.send(f"""```py
                                                        {' '.join(traceback.format_exception(type(error), error, error.__traceback__))}```""")
                except AttributeError:
                    self.client.owner = self.client.get_user(self.client.owner_id)
                    await self.client.owner.send(f"""```py
                                                        {' '.join(traceback.format_exception(type(error), error, error.__traceback__))}```""")
            except discord.errors.HTTPException: pass
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr); return


def setup(client):
    client.add_cog(ErrorHandler(client))