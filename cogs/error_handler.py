import traceback
import sys
from discord.ext import commands
import discord
from datetime import timedelta




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
        print(error)
        print(type(error))
        print("ERROR=============================")
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.channel.send(":no_entry_sign: You wish :>")
        elif isinstance(error, commands.errors.CommandOnCooldown):
            await ctx.channel.send(f"<a:ghostcat3:531060433927536650> Take a breath, **{ctx.author.name}**. Wait `{timedelta(seconds=int(error.retry_after))}`!", delete_after=5)
            #await ctx.channel.send(f"<:fufu:508437298808094742> Etou... **{ctx.author.name}**? Can you not shut the fuck up for **`{timedelta(seconds=int(error.retry_after))}`**.", delete_after=5)
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.channel.send(f"<a:ghostcat3:531060433927536650> {error}")
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(client):
    client.add_cog(ErrorHandler(client))