import traceback
import sys
from discord.ext import commands
import discord
from datetime import timedelta, datetime
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

        if isinstance(error, commands.errors.CheckFailure):
            await ctx.channel.send(":no_entry_sign: You wish :>")
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        elif isinstance(error, commands.errors.CommandOnCooldown):
            await ctx.channel.send(f"<a:ghostcat3:531060433927536650> Take a breath, **{ctx.author.name}**. Wait `{timedelta(seconds=int(error.retry_after))}`!", delete_after=5)
            return
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.channel.send(f"<a:ghostcat3:531060433927536650> {error}")
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr); return
        elif isinstance(error, commands.errors.CommandNotFound):
            # traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr); return
            return
        elif isinstance(error.original, asyncio.TimeoutError) or isinstance(error, discord.errors.Forbidden) or isinstance(error.original, concurrent.futures._base.TimeoutError) or isinstance(error.original, TimeoutError):
            return
        elif isinstance(error, commands.errors.NoPrivateMessage):
            await ctx.channel.send(":no_entry_sign: The bot is unable to DM you. Please check again.")
            return
        elif isinstance(error, mysqlError.OperationalError):
            self.client.myLog.debug(f"{' '.join(traceback.format_exception(type(error), error, error.__traceback__))}")
            await self.client.thp.mysqlReload()
            return
        else:
            try:
                try:
                    await self.client.owner.send(f"User `{ctx.author.id}`|**{ctx.author.name}** from `{ctx.channel.id}` of `{ctx.guild.id}`|**{ctx.guild.name}**")
                    await self.client.owner.send(f"""```py
                                                        {' '.join(traceback.format_exception(type(error), error, error.__traceback__))}```""")
                    self.client.myLog.error(f"User {ctx.author.id}|{ctx.author.name} from {ctx.channel.id} of {ctx.guild.id}|{ctx.guild.name}\n{' '.join(traceback.format_exception(type(error), error, error.__traceback__))}")
                except AttributeError:
                    self.client.owner = self.client.get_user(self.client.owner_id)
                    await self.client.owner.send(f"""```py
                                                        {' '.join(traceback.format_exception(type(error), error, error.__traceback__))}```""")
                    self.client.myLog.error(f"{' '.join(traceback.format_exception(type(error), error, error.__traceback__))}")
            except discord.errors.HTTPException: pass
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

        self.errPrinting(error)


    def errPrinting(self, e):
        print("==================================")
        print(e)
        print(type(e))
        print("============= ERROR ==============")


def setup(client):
    client.add_cog(ErrorHandler(client))