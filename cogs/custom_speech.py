import discord
from discord.ext import commands
import discord.errors as discordErrors
import json
import asyncio


class custom_speech(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.custom_speech = {}
        
    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.loop.run_in_executor(None, self.custom_speech_plugin)

    @commands.Cog.listener()
    async def on_message(self, message):
        #custom_speech
        try:
            if message.content.lower().startswith('clii '): await message.channel.send(self.custom_speech[str(message.guild.id)][message.content[5:].lower()])
        except:
            pass

    @commands.command(pass_context=True)
    async def cp_add(self, ctx, *args):
        a_in = []
        temp_dict = {}

        for word in args:
            a_in.append(word)
        print(a_in)
        if '==' not in a_in:
            await self.client.say(":no_entry_sign: Please use the right syntax.")
            pass
            #with open("custom_speech/custom_speech.txt", 'a', encoding='utf-8-sig') as f:
        else:
            try:    
                #Update <channel_id> dict (if exist), parse <key/value> dict into it
                self.custom_speech[ctx.message.server.id][' '.join(a_in[:int(a_in.index('=='))]).lower()] = ' '.join(a_in[int(a_in.index('==') + 1):])
            except KeyError:
                #Create <key/value> dict
                temp_dict[' '.join(a_in[:int(a_in.index('=='))]).lower()] = ' '.join(a_in[int(a_in.index('==') + 1):])
                #Create <channel_id> dict, parse <key/value> dict into it
                self.custom_speech[ctx.message.server.id] = temp_dict
            #Update the .json
            with open('custom_speech/custom_speech.json', 'w') as f:
                json.dump(self.custom_speech, f, indent=4)

            await self.client.say(":white_check_mark: Successfully added!")

    @commands.command(pass_context=True)
    async def cp_list(self, ctx):
        cp_keylist = list(self.custom_speech[str(ctx.guild.id)].keys())

        def makeembed(top, least, pages, currentpage):
            line = ''

            if str(ctx.guild.id) in self.custom_speech:
                line = "**-------------------- oo --------------------**\n" 
                for i in cp_keylist[top:least]:
                    line = line + f"∙ {i} == `{self.custom_speech[str(ctx.guild.id)][i][:80]}`\n"
                line = line + "**-------------------- oo --------------------**" 
            reembed = discord.Embed(title = f"`{ctx.guild.name}`'s custom tags", colour = discord.Colour(0x011C3A), description=line)
            reembed.set_footer(text=f"Page {currentpage} of {pages}")
            return reembed
            #else:
            #    await client.say("*Nothing but dust here...*")
        


        async def attachreaction(msg):
            await msg.add_reaction("\U000023ee")    #Top-left
            await msg.add_reaction("\U00002b05")    #Left
            await msg.add_reaction("\U000027a1")    #Right
            await msg.add_reaction("\U000023ed")    #Top-right

        pages = int(len(cp_keylist)/5)
        if len(cp_keylist)%5 != 0: pages += 1
        currentpage = 1
        cursor = 0

        emli = []
        for curp in range(pages):
            myembed = makeembed(currentpage*5-5, currentpage*5, pages, currentpage)
            emli.append(myembed)
            currentpage += 1

        msg = await ctx.send(embed=emli[cursor])
        if pages > 1: await attachreaction(msg)
        else: return

        def UM_check(reaction, user):
            return user.id == ctx.author.id and reaction.message.id == msg.id

        while True:
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=15, check=UM_check)
                if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                    cursor += 1
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U00002b05" and cursor > 0:
                    cursor -= 1
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U000023ee" and cursor != 0:
                    cursor = 0
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
                elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                    cursor = pages - 1
                    await msg.edit(embed=emli[cursor])
                    try: await msg.remove_reaction(reaction.emoji, user)
                    except discordErrors.Forbidden: pass
            except asyncio.TimeoutError:
                break

    @commands.command(pass_context=True)
    async def cp_del(self, ctx, *args):
        del_key = ' '.join(args)

        if ctx.message.server.id in self.custom_speech:                              #Check if the <server_id> is in the dict
            try: 
                del self.custom_speech[ctx.message.server.id][del_key]               #Delete <del_key> from custom_speech
                with open('custom_speech/custom_speech.json', 'w') as f:        #Update the .json
                    json.dump(self.custom_speech, f, indent=4)
                await self.client.say(":wastebasket: Key deleted!")
            except KeyError: await self.client.say(f":no_entry_sign: Item <{del_key}> not found. Please retry.")
        else:
            await self.client.say(f"This server `{ctx.message.server.name}` does not have any custom speech!")
            pass


    def custom_speech_plugin(self):
        with open('custom_speech/custom_speech.json') as f:
            try:
                self.custom_speech = json.load(f)
            except: print("ERROR at <custom_speec_plugin()>")

def setup(client):
    client.add_cog(custom_speech(client))








