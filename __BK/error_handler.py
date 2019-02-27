import traceback
import sys
from discord.ext import commands
import discord
from datetime import timedelta


class ErrorHandler:
    def __init__(self, client):
        self.client = client

    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""
        print(error)
        print(type(error))
        print("ERROR=============================")
        if isinstance(error, commands.errors.CheckFailure):
            await self.client.send_message(ctx.message.channel, "**You have no permission!**")
        elif isinstance(error, commands.errors.CommandOnCooldown):
            await self.client.send_message(ctx.message.channel, f"Hey! Wait after `{timedelta(seconds=int(error.retry_after))}` secs please!")
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(client):
    client.add_cog(ErrorHandler(client))