from discord.ext import commands

def check_author():
    def inner(ctx):
        return ctx.author.id == 214128381762076672
    return commands.check(inner)

