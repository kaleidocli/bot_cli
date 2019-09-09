import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors

import asyncio
import random

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
⠀| [help <command>] for more info.
⠀| [tutorial] if you are beginner.```
                                ╟ **NEW?** Use **`incarnate`** right away!
                                ╟ Already incarnated? [Join the Pralaeyr!](https://discord.gg/NGtXxXj)

                                ╟ **『LORE』**
                                ⠀⠀You - a Remnant as many others - woke up in the middle of an unreal world, where reality mixed with fantasy, where space and time were torn apart into *regions*.
                                ⠀⠀Since the Seraph, human have fought their way to reunite its race and called themselves, **"United Regions of The Pralaeyr"**, later pointed their swords at the pit and the summit of Pralaeyr.
                                ⠀⠀"To fight the darkness of the fantasy and to free the human race from the Pralaeyr", firsts of the Remnants have sworn.
                                """
        self.helper_thumbnail = 'https://imgur.com/EQsptpa.png'
        self.helper_banners = ["https://imgur.com/D1Ld5A7.gif", "https://imgur.com/e8cIazx.gif"]
        self.helper_preface = None
        self.helper_prefaceEmbs = None

        self.concept_title = '**C O N C E P T S**⠀⠀|⠀⠀**R P G  W I K I**'
        self.concept_description = """
                ```dsconfig
Definition? Mechanism? Lore? Yaaa```
                                **『YOU. ARE. CONFUSED...』**
                                \tYou walk into our worlds, you are confused. You might have known the commands, but you could have not fully embraced the nature of it.
                                \tThis may be your guidance to the basis of this world, or may it let you acknowledge the furthest corner of the system.
                                \tYour choice, to learn more or to stay still. May the Olds look upon you

                                **『.. SO. ARE. WE.』**
                                We, the devs, might not be able to please your curiosity, since... we sometimes cannot remember all of what the Pralaeyr can do!
                                May it be a mistake, or may it be not enough, if you don't mind, please come to our support server! https://discord.gg/4wJHCBp
                                """
        self.concept_thumbnail = 'https://imgur.com/ZneprKF.png'
        self.concept_banner = 'https://imgur.com/4ixM0TR.png'
        self.concept_preface = None
        self.concept_prefaceEmbs = None




    @commands.Cog.listener()
    async def on_ready(self):
        self.helper_preface = await self.helperPerface_load()
        self.helper_prefaceEmbs = await self.helper_ember()
        self.concept_preface = await self.conceptPerface_load()
        self.concept_prefaceEmbs = await self.concept_ember()
        print("|| Helper --- READY!")




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

                def UM_check(reaction, user):
                    return user.id == ctx.author.id and reaction.message.id == msg.id

                while True:
                    try:
                        reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=UM_check)
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
        temb.set_footer(text=f"<{tags.replace(' - ', '> <')}>", icon_url='https://imgur.com/EQsptpa.png')

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

                def UM_check(reaction, user):
                    return user.id == ctx.author.id and reaction.message.id == msg.id

                while True:
                    try:
                        reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=UM_check)
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
                        await msg.delete(); return

            await browse(); return

        # Search
        try: concept, description, tags, typee = await self.client.quefe(f"SELECT concept, description, tags, type FROM sys_concept WHERE concept='{raw[0]}';")
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

        await ctx.send(embed=temb)





    async def helperPerface_load(self):
        await asyncio.sleep(3)
        cats = await self.client.quefe("SELECT DISTINCT category FROM sys_command WHERE category<>'n/a';", type='all')
        packs = await self.client.quefe("SELECT category, command, short_description FROM sys_command WHERE category<>'n/a';", type='all')
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
            colour = discord.Colour(0xB1F1FA)
        )

        temball.set_thumbnail(url=self.helper_thumbnail)
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
                colour = discord.Colour(0xB1F1FA)
            )
            tembeach.set_thumbnail(url=self.helper_thumbnail)
            tembeach.set_author(name=f"\n{thre.replace('▱', '▰', count)}"); count += 1
            temb_socket.append(tembeach)

        return temb_socket

    async def conceptPerface_load(self):
        await asyncio.sleep(3)
        cats = await self.client.quefe("SELECT DISTINCT type FROM sys_concept WHERE type<>'n/a';", type='all')
        packs = await self.client.quefe("SELECT type, concept, short_description FROM sys_concept WHERE type<>'n/a';", type='all')
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
                            colour = discord.Colour(0xB1F1FA)
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
                colour = discord.Colour(0xB1F1FA)
            )
            tembeach.set_thumbnail(url=self.concept_thumbnail)
            tembeach.set_author(name=f"\n{thre.replace('▱', '▰', count)}"); count += 1
            temb_socket.append(tembeach)

        return temb_socket








def setup(client):
    client.add_cog(avaHelper(client))

