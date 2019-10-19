import asyncio
import random

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors

from .avaTools import avaTools
from .avaUtils import avaUtils



class avaHelper(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.__cd_check = self.client.thp.cd_check
        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)

        self.helper_title = '**G U I D E**⠀⠀|⠀⠀**R P G  C O M M A N D S**'
        self.helper_description = f"""
                                 ```ini
[help <cmd>] to inspect a command.
[tutorial] to being your journey.```
                                ╟ **Confuse?** Use **`concept`** for conceptual questions!
                                ╟ **Still confuse?** Join [our support camp!]({self.client.support_server_invite})

                                ╟ **『LORE』**
>>>                               ⠀⠀ You - a *Remnant* as many others - woke up in the middle of an unreal world, where reality mixed with fantasy, where space and time were torn apart into *regions*.
                                ⠀⠀Since the Seraph, human have fought their way to reunite their race and pointed their swords at the pit and summit of Pralaeyr.
                                ⠀⠀"To fight the darkness of the fantasy and to free the human race from the Pralaeyr", firsts of the Remnants have sworn.
                                """
        self.helper_thumbnail = ['https://imgur.com/EQsptpa.png', 'https://imgur.com/KBOW82t.png']
        self.helper_banners = ["https://imgur.com/D1Ld5A7.gif", "https://imgur.com/e8cIazx.gif"]
        self.helper_preface = None
        self.helper_prefaceEmbs = None

        self.concept_title = '**C O N C E P T S**⠀⠀|⠀⠀**R P G  W I K I**'
        self.concept_description = f"""
                ```dsconfig
Definition? Mechanism? Lore? Yaaa```
                                **『YOU. ARE. CONFUSED...』**
                                ⠀⠀We understand that this bot confuse *the hell* out of you.
                                ⠀⠀Apparently, command `help` only shows you how to use this bot, not to understand the mechanic behind it. 
                                ⠀⠀So, here it is. Bon apetite.

                                **『.. SO. ARE. WE.』**
                                ⠀Even us as Cli's devs, we cannot express everything in this helper.
                                ⠀So, if you don't mind, please take a visit to [our support server]({self.client.support_server_invite})!
                                """
        self.concept_thumbnail = 'https://imgur.com/ZneprKF.gif'
        self.concept_banner = 'https://imgur.com/4ixM0TR.png'
        self.concept_preface = None
        self.concept_prefaceEmbs = None

        self.helper_preface = ''; self.helper_prefaceEmbs = ''; self.concept_preface = ''; self.concept_prefaceEmbs = ''
        self.intoLoop(self.prepLoad())

        print("|| Helper --- READY!")

    async def prepLoad(self):
        self.helper_preface = await self.helperPerface_load()
        self.helper_prefaceEmbs = await self.helper_ember()
        self.concept_preface = await self.conceptPerface_load()
        self.concept_prefaceEmbs = await self.concept_ember()

    def intoLoop(self, coro):
        self.client.loop.create_task(coro)



# ================== EVENTS ==================

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     pass
    #     self.helper_preface = await self.helperPerface_load()
    #     self.helper_prefaceEmbs = await self.helper_ember()
    #     self.concept_preface = await self.conceptPerface_load()
    #     self.concept_prefaceEmbs = await self.concept_ember()
    #     print("|| Helper --- READY!")



# ================== HELPER ==================

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def help(self, ctx, *args):
        raw = list(args)
        temb_socket = self.helper_prefaceEmbs

        if not raw:

            async def browse():
                async def attachreaction(msg):
                    await msg.add_reaction("\U000023ee")    #Top-left
                    await msg.add_reaction("\U00002b05")    #Left
                    await msg.add_reaction("\U000027a1")    #Right
                    await msg.add_reaction("\U000023ed")    #Top-right

                cursor = 0
                emli = temb_socket
                pages = len(self.helper_preface)
                msg = await ctx.send(embed=emli[cursor])
                await attachreaction(msg)

                while True:
                    try:
                        reaction, user = await self.tools.pagiButton(check=lambda r, u: r.message.id == msg.id and u.id == ctx.author.id, timeout=60)
                        if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                            cursor += 1
                            await msg.edit(embed=emli[cursor])
                        elif reaction.emoji == "\U00002b05" and cursor > 0:
                            cursor -= 1
                            await msg.edit(embed=emli[cursor])
                        elif reaction.emoji == "\U000023ee" and cursor != 0:
                            cursor = 0
                            await msg.edit(embed=emli[cursor])
                        elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                            cursor = pages - 1
                            await msg.edit(embed=emli[cursor])
                    except asyncio.TimeoutError:
                        await msg.delete(); return

            await browse(); return

        # Search
        try: command, aliases, syntax, description, tags, requirement = await self.client.quefe(f"SELECT command, aliases, syntax, description, tags, requirement FROM sys_command WHERE command='{raw[0]}';")
        # E: No result. Instead try to search for familiar
        except TypeError:
            packs = await self.client.quefe(f"SELECT command FROM sys_command WHERE command LIKE '%{raw[0]}%' OR aliases LIKE '%{raw[0]}%';", type='all')
            # E: No familiar found
            if not packs: await ctx.send(":x: Commands not found"); return

            line = ''
            for pack in packs:
                line = line + f"""
· {pack[0]}"""
            temb = discord.Embed(title=':mag_right:⠀⠀You were saying...', description=f"```{line}```", colour = discord.Colour(0xB1F1FA))
            await ctx.send(embed=temb); return


        if requirement == 'n/a': temp_des = ''
        else: temp_des = f"⠀|⠀{requirement}"

        temb = discord.Embed(
                    title=f"**{command.upper()}** {temp_des}",
                    description='⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀',
                    colour = discord.Colour(0xB1F1FA))
        temb.add_field(name='**『Syntax』**', value=f"{syntax}\n⠀", inline=True)
        temb.add_field(name='**『Aliases』**', value=f"{aliases}\n⠀", inline=True)
        temb.add_field(name='**『Description』**', value=f"{description}", inline=False)
        temb.set_footer(text=f"<{tags.replace(' - ', '> <')}>", icon_url=random.choice(self.helper_thumbnail))

        await ctx.send(embed=temb)

    @commands.command(aliases=['cc'])
    @commands.cooldown(1, 3, type=BucketType.user)
    async def concept(self, ctx, *args):
        raw = list(args)
        temb_socket = self.concept_prefaceEmbs

        if not raw:

            async def browse():
                async def attachreaction(msg):
                    await msg.add_reaction("\U000023ee")    #Top-left
                    await msg.add_reaction("\U00002b05")    #Left
                    await msg.add_reaction("\U000027a1")    #Right
                    await msg.add_reaction("\U000023ed")    #Top-right

                cursor = 0
                emli = temb_socket
                pages = len(self.concept_preface)
                msg = await ctx.send(embed=emli[cursor])
                await attachreaction(msg)

                while True:
                    try:
                        reaction, user = await self.tools.pagiButton(check=lambda r, u: r.message.id == msg.id and u.id == ctx.author.id, timeout=60)
                        if reaction.emoji == "\U000027a1" and cursor < pages - 1:
                            cursor += 1
                            await msg.edit(embed=emli[cursor])
                        elif reaction.emoji == "\U00002b05" and cursor > 0:
                            cursor -= 1
                            await msg.edit(embed=emli[cursor])
                        elif reaction.emoji == "\U000023ee" and cursor != 0:
                            cursor = 0
                            await msg.edit(embed=emli[cursor])
                        elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
                            cursor = pages - 1
                            await msg.edit(embed=emli[cursor])
                    except asyncio.TimeoutError:
                        await msg.delete(); return

            await browse(); return

        # Search
        try: concept, description, tags, typee, illulink = await self.client.quefe(f"SELECT concept, description, tags, type, illulink FROM sys_concept WHERE concept='{raw[0]}';")
        # E: No result. Instead try to search for familiar
        except TypeError:
            packs = await self.client.quefe(f"SELECT concept FROM sys_concept WHERE concept LIKE '%{raw[0]}%' OR tags LIKE '%{raw[0]}%';", type='all')
            # E: No familiar found
            if not packs: await ctx.send(":x: Concept not found"); return

            line = ''
            for pack in packs:
                line = line + f"""
· {pack[0]}"""
            temb = discord.Embed(title=':mag_right:⠀⠀You were saying...', description=f"```{line}```", colour = discord.Colour(0xB1F1FA))
            await ctx.send(embed=temb); return

        temb = discord.Embed(
                    title=f"**{concept.upper()}**⠀⠀|⠀⠀{typee}",
                    description=f'{description}',
                    colour = discord.Colour(0xB1F1FA))
        temb.set_thumbnail(url=self.concept_thumbnail)
        temb.set_footer(text=f"<{tags.replace(' - ', '> <')}>", icon_url='https://imgur.com/TW9dmXy.png')
        if illulink: temb.set_image(url=illulink)

        await ctx.send(embed=temb)



# ================== MISC ==================

    @commands.command()
    async def invite(self, ctx):
        #await ctx.send("Hey use this to invite me -> https://discordapp.com/api/oauth2/authorize?client_id=449278811369111553&permissions=238157120&scope=bot")
        temb = discord.Embed(description=f"""[===== Support Server =====]({self.client.support_server_invite})\n◈ Before inviting this bot, you must acknowledge and accept the following:\n· High-ratio shutdown session, with random length and for **no reason**.\n| Any DM-ed complaints relevant to the incident will result in a ban.\nHowever, compensation with evidences will be responsed and should be sent in *support server*.\nTrying to DM twice on the above problem will result in a ban.\nDM abusing will result in a *boop*.
                                    \n· Buggy gameplay, low latency.\n| Any bot-abusing activities will result in a ban.\nHowever, *bot-breaking* is encouraged, and any bugs should be reported in *support server/Bug-report*
                                    \n· Violation in data, balance and activities of the players.\n| This is a testing bot. Have fun testing this <:fufu:508437298808094742>
                                    \n[===== Invite =====](https://discordapp.com/api/oauth2/authorize?client_id=449278811369111553&permissions=590732609&scope=bot)""")
        await ctx.send(embed=temb)

    @commands.command()
    async def source(self, ctx, *args):
        await ctx.send('https://github.com/kaleidocli/bot_cli')



# ================== TOOLS ==================

    async def helperPerface_load(self):
        await asyncio.sleep(3)
        cats = await self.client.quefe("SELECT DISTINCT category FROM sys_command WHERE category<>'n/a' ORDER BY category ASC;", type='all')
        packs = await self.client.quefe("SELECT category, command, short_description FROM sys_command WHERE category<>'n/a' ORDER BY command ASC;", type='all')
        a = []
        for cat in cats:
            d = {}
            for pack in packs:
                if pack[0] != cat[0]: continue

                d[pack[1]] = pack[2]
            a.append([await self.utils.space_out(cat[0].upper()), d])
        return a

    async def helper_ember(self):
        temb_socket = []
        temball = discord.Embed(
            title = self.helper_title,
            description = self.helper_description,
            colour = discord.Colour(0x527D8F)
        )

        temball.set_thumbnail(url=random.choice(self.helper_thumbnail))
        temball.set_image(url=random.choice(self.helper_banners))
        temball.set_footer(text=f"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀")
        temb_socket.append(temball)

        pages = len(self.helper_preface)
        count = 1
        thre = '▱'*(pages-1)
        for stuff in self.helper_preface:
            line = ''
            for k, v in stuff[1].items():
                line = line + f"> **`{k}`**\n╚╡{v}\n"
            tembeach = discord.Embed(
                description = f"""
                ```{stuff[0]}```
                {line}""",
                colour = discord.Colour(0x527D8F)
            )
            tembeach.set_thumbnail(url=random.choice(self.helper_thumbnail))
            tembeach.set_author(name=f"\n{thre.replace('▱', '▰', count)}"); count += 1
            temb_socket.append(tembeach)

        return temb_socket

    async def conceptPerface_load(self):
        await asyncio.sleep(3)
        cats = await self.client.quefe("SELECT DISTINCT type FROM sys_concept WHERE type<>'n/a' ORDER BY type ASC;", type='all')
        packs = await self.client.quefe("SELECT type, concept, short_description FROM sys_concept WHERE type<>'n/a' ORDER BY concept ASC;", type='all')
        a = []
        for cat in cats:
            d = {}
            for pack in packs:
                if pack[0] != cat[0]: continue

                d[pack[1]] = pack[2]
            a.append([await self.utils.space_out(cat[0].upper()), d])
        return a

    async def concept_ember(self):
        temb_socket = []

        temball = discord.Embed(
            title = self.concept_title,
            description = self.concept_description,
                            colour = discord.Colour(0x527D8F)
        )
        temball.set_thumbnail(url=self.concept_thumbnail)
        temball.set_footer(text=f"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀")
        temball.set_image(url=self.concept_banner)
        temb_socket.append(temball)

        pages = len(self.concept_preface)
        count = 1
        thre = '▱'*(pages-1)
        for stuff in self.concept_preface:
            line = ''
            for k, v in stuff[1].items():
                line = line + f"> **`{k}`**\n╚╡{v}\n"
            tembeach = discord.Embed(
                description = f"""
                ```{stuff[0]}```
                {line}""",
                colour = discord.Colour(0x527D8F)
            )
            tembeach.set_thumbnail(url=self.concept_thumbnail)
            tembeach.set_author(name=f"\n{thre.replace('▱', '▰', count)}"); count += 1
            temb_socket.append(tembeach)

        return temb_socket





def setup(client):
    client.add_cog(avaHelper(client))
