from os import listdir, path
from pathlib import Path
from io import BytesIO
import copy
import asyncio
import random
import gc
# import multiprocessing
from functools import partial

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio
import objgraph

from .avaTools import avaTools
from .avaUtils import avaUtils
from utils import checks



class avaAvatar(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.prote_lib = {}
        self.thepoof = 0
        self.bg_dict = {'bg0': 'medieval_indoor',
                    'bg1': 'medieval_outdoor',
                    'bg2': 'modern_indoor',
                    'bg3': 'modern_outdoor',
                    'bg4': 'fengfeng',
                    'bg5': 'sleepypang',
                    'bg6': 'rocha_cold',
                    'bg7': 'rocha_crimson',
                    'bg8': 'rocha_gold',
                    'bg9': 'rocha_green', 
                    'bg10': 'pengzhen_zhang',
                    'bg11': 'persona5',
                    'bg12': 'adrien_girod'}
        self.char_dict = {'av0': 'Iris',
                        'av1': 'Zoey',
                        'av2': 'Ardena',
                        'av3': 'Yamabuki',
                        'av4': 'Yamabuki_Cosplay',
                        'av5': 'Yamabuki_NSFW',
                        'av6': 'Myu',
                        'av7': 'Myu_NSFW',
                        'av8': 'Enju',
                        'av9': 'Enju_NSFW',
                        'av10': 'Enju_Cosplay',
                        'av11': 'Shima_Rin',
                        'av12': 'Akari',
                        'av13': 'Akari_NSFW',
                        'av14': 'Akari_Cosplay',
                        'av15': 'RPG_Girl_1',
                        'av16': 'GBF_Female',
                        'av17': 'GBF_Male',
                        'av18': 'GBF_Female_2',
                        'av19': 'Djeeta',
                        'av20': 'Ricka',
                        'av21': 'Ricka_Cosplay',
                        'av22': 'Ricka_NSFW',
                        'av23': 'set_FURRY',
                        'av24': 'Req_Virgo',
                        'av25': 'Black_Survival',
                        'av26': 'SAO_Sinon',
                        'av27': 'SAO_Lisbeth',
                        'av28': 'SAO_Asuna',
                        'av29': 'P5_Ann',
                        'av30': 'atelier_male',
                        'av31': 'atelier_female',
                        'av32': 'FGO_Artoria'}
        self.font_dict = {'fnt0': 'ERASLGHT.ttf',
                        'fnt1': 'Persona_Non_Grata.ttf',
                        'fnt2': 'Phorssa.ttf',
                        'fnt3': 'DalekPinpointBold.ttf',
                        'fnt4': 'the_unseen.ttf',
                        'fnt5': 'MARSNEVENEKSK_Regular.otf'}

        self.char_dir = {}
        self.client.chardict_meta = {}
        for d in self.char_dict.items():
            self.char_dir[d[0]] = [dir for dir in listdir(path.join('data', 'profile', 'char', self.char_dict[d[0]])) if dir.endswith('.png')]

            try: self.client.chardict_meta[d[0]]['quantity'] = len(self.char_dir[d[0]])     # Avoiding overwrite
            except KeyError: self.client.chardict_meta[d[0]] = {'quantity': len(self.char_dir[d[0]])}

        self.bg_dir = {}
        self.client.bgdict_meta = {}
        for d in self.bg_dict.items():
            self.bg_dir[d[0]] = [dir for dir in listdir(path.join('data', 'profile', 'bg', self.bg_dict[d[0]])) if dir.endswith('.png') or dir.endswith('.jpg')]

            try: self.client.bgdict_meta[d[0]]['quantity'] = len(self.bg_dir[d[0]])     # Avoiding overwrite
            except KeyError: self.client.bgdict_meta[d[0]] = {'quantity': len(self.bg_dir[d[0]])}

        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)

        self.intoLoop(self.prepLoad())

        print("|| Avatar --- READY!")



# ================== EVENTS ==================

    async def prepLoad(self):
        await asyncio.sleep(15)      # Do not remove, or else the data stream would mix with WORLD_BUILDING or avaDungeon
        await self.prote_plugin()

    def intoLoop(self, coro):
        self.client.loop.create_task(coro)

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     await asyncio.sleep(2)      # Do not remove, or else the data stream would mix with WORLD_BUILDING
    #     await self.prote_plugin()



# ================== AVATARS ==================

    @commands.command()
    @checks.check_author()
    async def prote_reload(self, ctx):
        await self.prote_plugin()

    @commands.command()
    @checks.check_author()
    async def avauda(self, ctx):

        # AVATARs
        temp = await self.client.quefe(f"SELECT avatar_id FROM model_avatar", type='all')
        avas = [i[0] for i in temp]

        user_ids = await self.client.quefe("SELECT id FROM personal_info", type='all')
        master_que = ''
        for pack in user_ids:
            await asyncio.sleep(0)
            que = ''
            for ava in avas:
                que = que + f"INSERT INTO pi_avatars (user_id, avatar_id) SELECT '{pack[0]}', '{ava}' WHERE NOT EXISTS (SELECT * FROM pi_avatars WHERE user_id='{pack[0]}' AND avatar_id='{ava}'); "
            master_que = master_que + que
        await self.client._cursor.execute(master_que)

        # BACKGROUNDs
        temp = await self.client.quefe(f"SELECT bg_code FROM model_background", type='all')
        avas = [i[0] for i in temp]

        user_ids = await self.client.quefe("SELECT id FROM personal_info", type='all')
        master_que = ''
        for pack in user_ids:
            await asyncio.sleep(0)
            que = ''
            for ava in avas:
                que = que + f"INSERT INTO pi_backgrounds (user_id, bg_code) SELECT '{pack[0]}', '{ava}' WHERE NOT EXISTS (SELECT * FROM pi_backgrounds WHERE user_id='{pack[0]}' AND bg_code='{ava}'); "
            master_que = master_que + que
        await self.client._cursor.execute(master_que)

        # FONTs
        temp = await self.client.quefe(f"SELECT font_id FROM model_font", type='all')
        avas = [i[0] for i in temp]

        user_ids = await self.client.quefe("SELECT id FROM personal_info", type='all')
        master_que = ''
        for pack in user_ids:
            await asyncio.sleep(0)
            que = ''
            for ava in avas:
                que = que + f"INSERT INTO pi_fonts (user_id, font_id) SELECT '{pack[0]}', '{ava}' WHERE NOT EXISTS (SELECT * FROM pi_fonts WHERE user_id='{pack[0]}' AND font_id='{ava}'); "
            master_que = master_que + que
        await self.client._cursor.execute(master_que)

        await ctx.send(":white_check_mark:")

    @commands.command(aliases=['a'])
    @commands.cooldown(1, 5, type=BucketType.user)
    async def avatar(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        await self.tools.ava_scan(ctx.message, type='all')

        __mode = 'static'

        # Console
        raw = list(args)
        try:
            if raw[0] == 'gif': __mode = 'gif'; user_id = ctx.author.id
            else:
                try:
                    user_id = args[0]
                except IndexError: user_id = ctx.author.id
                except commands.CommandError: await ctx.send("<:osit:544356212846886924> User not found"); return
        except IndexError: user_id = ctx.author.id

        # Colour n Character get
        try: co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death, char_name, bg_code, font_id, blur_rate = await self.client.quefe(f"SELECT co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death, avatar_id, bg_code, font_id, blur_rate FROM cosmetic_preset WHERE user_id='{user_id}' AND stats='CURRENT';")
        except TypeError: await ctx.send(f"<:osit:544356212846886924> User has not incarnated! ({user_id})"); return
        #co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death = ('#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF')

        # STATIC =========
        async def magiking(ctx):

            # Info get
            #pylint: disable=unused-variable
            age, evo, kill, death, money, name, partner_temp, partner = await self.client.quefe(f"SELECT age, evo, LP, STA, money, name, partner AS prtn, (SELECT name FROM personal_info WHERE id=prtn) FROM personal_info WHERE id='{user_id}';")
            if not partner: partner = '---------------------'

            #pylint: enable=unused-variable
            guild_code, rank = await self.client.quefe(f"SELECT guild_code, rank FROM pi_guild WHERE user_id='{user_id}';")

            if guild_code != 'n/a':
                guild_name = await self.client.quefe(f"SELECT guild_name FROM model_guild WHERE guild_code='{guild_code}';"); guild_name = guild_name[0]
            else:
                guild_code = 'None'
                guild_name = 'None'


            form_img = self.prote_lib['form'][0]
            """char_img = random.choice(self.prote_lib[char_name])"""
            char_img = await self.char_generator(char_name)
            #char_img = char_img.resize((int(form_img.height/char_img.height*char_img.width), form_img.height), resample=Image.LANCZOS)
            badge_img = self.prote_lib['badge'][rank.lower()]
            await asyncio.sleep(0)
            #badge_img = badge_img.resize((int(badge_img.width/1.5), int(badge_img.height/1.5)), resample=Image.LANCZOS)
            #bg = self.prote_lib['bg'][0]
            """bg = copy.deepcopy(random.choice(self.prote_lib['bg'][bg_code]))"""
            bg = await self.bg_generator(bg_code, blur_rate=blur_rate)
            #bg = bg.resize((800, 600), resample=Image.LANCZOS)
            #bg = bg.filter(ImageFilter.GaussianBlur(2.6))           # prev(best)=2.6
            name_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
            degree_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
            money_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
            horizontal = Image.new('RGBA', form_img.size, (255, 255, 255, 0))

            # Font Set
            fnt_name = self.prote_lib['font'][font_id]['name']            # Name
            fnt_degree = self.prote_lib['font'][font_id]['guild']        # Degrees
            fnt_age = self.prote_lib['font'][font_id]['age']              # Age
            fnt_kd = self.prote_lib['font'][font_id]['k/d']               # K/D
            fnt_guild = self.prote_lib['font'][font_id]['guild']          # Guild
            fnt_rank = self.prote_lib['font'][font_id]['rank']            # Rank
            fnt_evo = self.prote_lib['font'][font_id]['evo']              # evo
            fnt_money = self.prote_lib['font'][font_id]['money']          # Money
            await asyncio.sleep(0)

            # Get info
            age = str(age).upper()
            if int(age) < 10: age = '0' + age
            evo = str(evo).upper()
            kill = str(kill).upper()
            death = str(death).upper()
            money = str(money).upper()
            guild = f"{guild_code} | {guild_name}"
            rank = rank.upper()
            # Get text canvas
            nb = ImageDraw.Draw(name_box)
            dgb = ImageDraw.Draw(degree_box)
            mnb = ImageDraw.Draw(money_box)
            hori = ImageDraw.Draw(horizontal)
            # Write/Alligning
            nb.text((name_box.width/4, 0), name.upper(), font=fnt_name, fill=co_name)
            dgb.text((name_box.width/2, 0), partner.capitalize(), font=fnt_degree, fill=co_partner)
            mnb.text((0, 0), money, font=fnt_money, fill=co_money)
            await asyncio.sleep(0)
            hori.text((3, 541), age, font=fnt_age, fill=co_age)
            hori.text((730 - hori.textsize(guild, font=fnt_guild)[0], 540), guild, font=fnt_guild, fill=co_guild)
            hori.text((730 - hori.textsize(rank, font=fnt_rank)[0], 555), rank, font=fnt_rank, fill=co_rank)
            hori.text((700 - hori.textsize(evo, font=fnt_evo)[0], 420), evo, font=fnt_evo, fill=co_evo)
            hori.text((525 , 384), death, font=fnt_kd, fill=co_death)
            hori.text((547 , 334), kill, font=fnt_kd, fill=co_kill)
            # Rotating
            name_box = name_box.rotate(90)
            degree_box = degree_box.rotate(90)
            money_box = money_box.rotate(90, center=(400, 0))

            # Middle aligning
            char_midcoordX = 50 + int((398 - char_img.width)/2)
            if char_midcoordX < 0: char_midcoordX = 0

            # Composing
            await asyncio.sleep(0)
            bg.alpha_composite(badge_img, dest=(800 - (badge_img.width + 5), 5))
            bg.alpha_composite(form_img)
            bg.alpha_composite(char_img, dest=(char_midcoordX, 8))            #Prev=56
            bg.alpha_composite(name_box, dest=(0, 38), source=(108, 0))
            bg.alpha_composite(degree_box, dest=(0, 10), source=(45, 0))
            bg.alpha_composite(money_box, dest=(344, 89))
            bg.alpha_composite(horizontal)
            await asyncio.sleep(0)

            output_buffer = BytesIO()
            bg.save(output_buffer, 'png')
            output_buffer.seek(0)

            # Closing???
            bg.close()
            char_img.close()
            name_box.close()
            degree_box.close()
            money_box.close()
            horizontal.close()
            nb = None
            dgb = None
            mnb = None
            hori = None
            gc.collect()
            
        
            #bg.show()
            return output_buffer

        # GIF ============        
        async def gafiking(ctx, in_img, char_img, pos_offset=0, **kwargs):
            """pos_offset: Positive value for lower pos, negative for upper pos"""

            # Info get
            age, evo, kill, death, money, name = kwargs['pack_PI']
            guild_code, rank = kwargs['pack_PG']
            guild_name = kwargs['pack_PI']; guild_name = guild_name

            #img = Image.open('sampleimg.jpg').convert('RGBA')
            form_img = self.prote_lib['form'][0]
            #char_img = char_img.resize((int(form_img.height/char_img.height*char_img.width), form_img.height), resample=Image.LANCZOS)
            badge_img = self.prote_lib['badge'][rank.lower()]
            #badge_img = badge_img.resize((int(badge_img.width/1.5), int(badge_img.height/1.5)), resample=Image.LANCZOS)
            bg = copy.deepcopy(in_img)
            #bg = bg.resize((800, 600), resample=Image.LANCZOS)
            #bg = bg.filter(ImageFilter.GaussianBlur(2.6))           # prev(best)=2.6
            name_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
            degree_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
            money_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
            horizontal = Image.new('RGBA', form_img.size, (255, 255, 255, 0))

            # Font Set
            fnt_name = self.prote_lib['font'][font_id]['name']            # Name
            fnt_degree = self.prote_lib['font'][font_id]['degree']        # Degrees
            fnt_age = self.prote_lib['font'][font_id]['age']              # Age
            fnt_kd = self.prote_lib['font'][font_id]['k/d']               # K/D
            fnt_guild = self.prote_lib['font'][font_id]['guild']          # Guild
            fnt_rank = self.prote_lib['font'][font_id]['rank']            # Rank
            fnt_evo = self.prote_lib['font'][font_id]['evo']              # evo
            fnt_money = self.prote_lib['font'][font_id]['money']          # Money

            await asyncio.sleep(0.02)

            # Get info
            age = str(age).upper()
            if int(age) < 10: age = '0' + age
            evo = str(evo).upper()
            kill = str(kill).upper()
            death = str(death).upper()
            money = str(money).upper()
            guild = f"{guild_code} | {guild_name}"
            rank = rank.upper()
            # Get text canvas
            nb = ImageDraw.Draw(name_box)
            dgb = ImageDraw.Draw(degree_box)
            await asyncio.sleep(0.02)
            mnb = ImageDraw.Draw(money_box)
            hori = ImageDraw.Draw(horizontal)
            # Write/Alligning
            nb.text((name_box.width/4, 0), name.upper(), font=fnt_name, fill=co_name)
            dgb.text((name_box.width/2, 0), guild.capitalize(), font=fnt_degree, fill=co_partner)
            mnb.text((0, 0), money, font=fnt_money, fill=co_money)
            hori.text((3, 541), age, font=fnt_age, fill=co_age)
            hori.text((730 - hori.textsize(guild, font=fnt_guild)[0], 540), guild, font=fnt_guild, fill=co_guild)
            await asyncio.sleep(0.02)
            hori.text((730 - hori.textsize(rank, font=fnt_rank)[0], 555), rank, font=fnt_rank, fill=co_rank)
            hori.text((700 - hori.textsize(evo, font=fnt_evo)[0], 420), evo, font=fnt_evo, fill=co_evo)
            hori.text((525 , 384), death, font=fnt_kd, fill=co_death)
            hori.text((547 , 334), kill, font=fnt_kd, fill=co_kill)
            # Rotating
            name_box = name_box.rotate(90)
            degree_box = degree_box.rotate(90)
            money_box = money_box.rotate(90, center=(400, 0))

            await asyncio.sleep(0.02)

            # Middle aligning
            char_midcoordX = 50 + int((398 - char_img.width)/2)
            if char_midcoordX < 0: char_midcoordX = 0

            # Composing
            bg.alpha_composite(badge_img, dest=(800 - (badge_img.width + 5), 5))
            bg.alpha_composite(form_img)
            await asyncio.sleep(0.07)
            bg.alpha_composite(char_img, dest=(char_midcoordX, 8 + pos_offset))            #Prev=56
            bg.alpha_composite(name_box, dest=(0, 38), source=(108, 0))
            await asyncio.sleep(0.07)
            bg.alpha_composite(degree_box, dest=(0, 10), source=(45, 0))
            bg.alpha_composite(money_box, dest=(344, 89))
            bg.alpha_composite(horizontal)

            output_buffer = BytesIO()
            output_buffer.seek(0)
            bg.save(output_buffer, 'png')
            output_buffer.close()

            #bg.show()
            return bg

        async def cogif(ctx, char_img):

            # INFO prep =============================
            pack_PI = await self.client.quefe(f"SELECT age, evo, kills, deaths, money, name FROM personal_info WHERE id='{user_id}';")
            pack_PG = await self.client.quefe(f"SELECT guild_code, rank FROM pi_guild WHERE user_id='{user_id}';")
            pack_E = await self.client.quefe(f"SELECT guild_name FROM model_guild WHERE guild_code='{pack_PG[0]}';"); pack_E = pack_E[0]

            # PARTICLEs prep ========================
            # particle_after = []
            outImPart = []
            particles = imageio.mimread(path.join('data', 'profile', 'bg_gif', 'train.gif'), memtest=False)
            partilen = len(particles)

            bar = 20                               # Set a maximum particles in ordercli a gif not overload
            if partilen > bar:
                divider = int(partilen/bar)
            else: divider = 1
            modulair = partilen%bar

            # ANIMATION of char_img prep ================
            # ODD amount of particles
            if partilen%2:
                temp = list(range((partilen-2-modulair)//(divider*2)))
                temp2 = list(range((partilen-2-modulair)//(divider*2)))
                temp2.reverse()
                offset_band = [0] + temp + [temp2[0]+1] + temp2
            # Non-odd amount of particles
            else:
                temp = list(range((partilen-1-modulair)//(divider*2)))
                temp2 = list(range((partilen-1-modulair)//(divider*2)))
                temp2.reverse()
                offset_band = [0] + temp + [temp2[0]] + temp2
            
            # GATHERING particles =======================
            print(offset_band, divider, partilen, modulair)
            count = divider
            obpointer = -1
            for particle in particles:
                if count == divider:
                    count = 1
                    offval = offset_band[obpointer]
                    obpointer += 1
                else:
                    # print(count)
                    count += 1
                    continue
                print(f"LOOOPPPPP {obpointer} {offval}")
                a = Image.fromarray(particle)
                a = a.resize((800, 600), resample=Image.LANCZOS)
                a = a.filter(ImageFilter.GaussianBlur(2.6))
 
                # PROCESS and STITCH
                try:
                    #particle = particles[count]
                    #a = Image.fromarray(particle)  

                    #out_img = await gafiking(ctx, a, char_img)
                    out_img = await gafiking(ctx, a, char_img, pos_offset=offval, pack_PI=pack_PI, pack_PG=pack_PG, pack_E=pack_E)
                    await asyncio.sleep(0.1)
                    #outImPart.append(np.asarray(a))
                    outImPart.append(out_img)
                except IndexError: break


            output_buffer = BytesIO()
            #imageio.mimwrite(output_buffer, outImPart)
            outImPart[0].save(output_buffer, save_all=True, format='gif', append_images=outImPart, loop=0)
            for im in outImPart:
                im.close()

            output_buffer.seek(0)
            #return await self.client.loop.run_in_executor(None, self.imgur_client.upload, output_buffer)
            #return output_buffer
            await ctx.send(file=discord.File(fp=output_buffer, filename='profile.gif'))
            output_buffer.close()
        
        if __mode == 'static':
            await ctx.trigger_typing()
            output_buffer = await magiking(ctx)
            await ctx.send(file=discord.File(fp=output_buffer, filename='profile.png'))
            output_buffer.close()
        elif __mode == 'gif':
            await ctx.trigger_typing()
            char_img = await self.char_generator(char_name)
            #output_buffer = await cogif(ctx)         
            #reembed = discord.Embed(colour = discord.Colour(0x011C3A))
            #reembed.set_image(url=output_buffer['link'])
            #await ctx.send(embed=reembed)
            #await ctx.send(file=discord.File(fp=output_buffer, filename='profile.gif'))
            await cogif(ctx, char_img)



# ================== TOOLS/BACKUP ==================

    async def mavatar(self, ctx, *args):

        if not await self.tools.ava_scan(ctx.message, type='life_check'): return
        await self.tools.ava_scan(ctx.message, type='all')

        __mode = 'static'

        # Console
        try:
            if args[0] == 'gif': __mode = 'gif'; user_id = ctx.author.id
            else:
                try:
                    user_id = args[0]
                except IndexError: user_id = ctx.author.id
                except commands.CommandError: await ctx.send("<:osit:544356212846886924> User not found"); return
        except IndexError: user_id = ctx.author.id

        # Colour n Character get
        try: co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death, char_name, bg_code, font_id, blur_rate = await self.client.quefe(f"SELECT co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death, avatar_id, bg_code, font_id, blur_rate FROM cosmetic_preset WHERE user_id='{user_id}' AND stats='CURRENT';")
        except TypeError: await ctx.send(f"<:osit:544356212846886924> User has not incarnated! ({user_id})"); return
        #co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death = ('#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF')

        if __mode == 'static':
            await ctx.trigger_typing()

            # objgraph.show_growth(limit=3) # doctest: +RANDOM_OUTPUT
            output_buffer = await self.magiking(user_id, (co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death, char_name, bg_code, font_id, blur_rate))
            # objgraph.show_growth() # doctest: +RANDOM_OUTPUT

            # objgraph.show_chain(
            #     objgraph.find_backref_chain(
            #         objgraph.by_type('list')[-1],
            #         objgraph.is_proper_module),
            #     filename='chain.png')

            await ctx.send(file=discord.File(fp=output_buffer, filename='profile.png'))
            output_buffer = None
        elif __mode == 'gif':
            await ctx.trigger_typing()
            char_img = await self.char_generator(char_name)
            #output_buffer = await self.cogif(user_id, (co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death, char_name, bg_code, font_id))         
            output_buffer = await self.cogif(user_id, char_img, (co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death, char_name, bg_code, font_id))
            await ctx.send(file=discord.File(fp=output_buffer, filename='profile.gif'))

    async def magiking(self, user_id, pack):

        # co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death, char_name, bg_code, font_id = pack

        # Info get
        #pylint: disable=unused-variable
        age, evo, kill, death, money, name, partner_temp, partner = await self.client.quefe(f"SELECT age, evo, LP, STA, money, name, partner AS prtn, (SELECT name FROM personal_info WHERE id=prtn) FROM personal_info WHERE id='{user_id}';")
        if not partner: partner = '---------------------'
        #pylint: enable=unused-variable
        guild_code, rank = await self.client.quefe(f"SELECT guild_code, rank FROM pi_guild WHERE user_id='{user_id}';")
        if guild_code != 'n/a':
            guild_name = await self.client.quefe(f"SELECT guild_name FROM model_guild WHERE guild_code='{guild_code}';"); guild_name = guild_name[0]
        else:
            guild_code = 'None'
            guild_name = 'None'

        form_img = self.prote_lib['form'][0]
        """char_img = random.choice(self.prote_lib[pack[9]])"""
        char_img = await self.char_generator(pack[9])
        #char_img = char_img.resize((int(form_img.height/char_img.height*char_img.width), form_img.height), resample=Image.LANCZOS)
        badge_img = self.prote_lib['badge'][rank.lower()]
        #badge_img = badge_img.resize((int(badge_img.width/1.5), int(badge_img.height/1.5)), resample=Image.LANCZOS)
        #bg = self.prote_lib['bg'][0]
        """bg = copy.deepcopy(random.choice(self.prote_lib['bg'][pack[10]]))"""
        bg = await self.bg_generator(pack[10], blur_rate=pack[12])
        #bg = bg.resize((800, 600), resample=Image.LANCZOS)
        #bg = bg.filter(ImageFilter.GaussianBlur(2.6))           # prev(best)=2.6

        # # Font Set
        # fnt_name = self.prote_lib['font'][font_id]['name']            # Name
        # fnt_degree = self.prote_lib['font'][font_id]['guild']        # Degrees
        # fnt_age = self.prote_lib['font'][font_id]['age']              # Age
        # fnt_kd = self.prote_lib['font'][font_id]['k/d']               # K/D
        # fnt_guild = self.prote_lib['font'][font_id]['guild']          # Guild
        # fnt_rank = self.prote_lib['font'][font_id]['rank']            # Rank
        # fnt_evo = self.prote_lib['font'][font_id]['evo']              # evo
        # fnt_money = self.prote_lib['font'][font_id]['money']          # Money

        # Get info
        age = str(age).upper()
        if int(age) < 10: age = '0' + age
        evo = str(evo).upper()
        kill = str(kill).upper()
        death = str(death).upper()
        money = str(money).upper()
        guild = f"{guild_code} | {guild_name}"
        rank = rank.upper()
    
        output_buffer = await self.client.loop.run_in_executor(None, partial(self.pillowingAvatar, img=(bg, char_img, form_img, badge_img), pack=pack, pack2=(age, evo, kill, death, money, name, partner_temp, partner, guild_code, rank, guild)))

        # jout = multiprocessing.Queue()
        # myfunc = partial(pillowingAvatar, img=(bg, char_img, form_img, badge_img), pack=pack, pack2=(age, evo, kill, death, money, name, partner_temp, partner, guild_code, rank, guild), font_dict=self.font_dict, jout=jout)
        # j = multiprocessing.Process(target=myfunc)
        # await self.client.loop.run_in_executor(None, j.start)
        # output_buffer = await self.client.loop.run_in_executor(None, jout.get)
        # output_buffer = jout.get()
        # j.kill()

        # jout = None
        # j = None
        # myfunc = None

        # #bg.show()
        # print(f"OOOOOUUUTTT: {output_buffer}")
        return output_buffer
        # jout.put(output_buffer)
     
    async def gafiking(self, user_id, in_img, char_img, pack, pos_offset=0, **kwargs):
        """pos_offset: Positive value for lower pos, negative for upper pos"""

        co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death, char_name, bg_code, font_id = pack

        # Info get
        age, evo, kill, death, money, name = kwargs['pack_PI']
        guild_code, rank = kwargs['pack_PG']
        guild_name = kwargs['pack_PI']; guild_name = guild_name

        #img = Image.open('sampleimg.jpg').convert('RGBA')
        form_img = self.prote_lib['form'][0]
        #char_img = char_img.resize((int(form_img.height/char_img.height*char_img.width), form_img.height), resample=Image.LANCZOS)
        badge_img = self.prote_lib['badge'][rank.lower()]
        #badge_img = badge_img.resize((int(badge_img.width/1.5), int(badge_img.height/1.5)), resample=Image.LANCZOS)
        bg = copy.deepcopy(in_img)
        #bg = bg.resize((800, 600), resample=Image.LANCZOS)
        #bg = bg.filter(ImageFilter.GaussianBlur(2.6))           # prev(best)=2.6
        name_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
        degree_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
        money_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
        horizontal = Image.new('RGBA', form_img.size, (255, 255, 255, 0))

        # Font Set
        fnt_name = self.prote_lib['font'][font_id]['name']            # Name
        fnt_degree = self.prote_lib['font'][font_id]['degree']        # Degrees
        fnt_age = self.prote_lib['font'][font_id]['age']              # Age
        fnt_kd = self.prote_lib['font'][font_id]['k/d']               # K/D
        fnt_guild = self.prote_lib['font'][font_id]['guild']          # Guild
        fnt_rank = self.prote_lib['font'][font_id]['rank']            # Rank
        fnt_evo = self.prote_lib['font'][font_id]['evo']              # evo
        fnt_money = self.prote_lib['font'][font_id]['money']          # Money

        # Get info
        age = str(age).upper()
        if int(age) < 10: age = '0' + age
        evo = str(evo).upper()
        kill = str(kill).upper()
        death = str(death).upper()
        money = str(money).upper()
        guild = f"{guild_code} | {guild_name}"
        rank = rank.upper()
        # Get text canvas
        nb = ImageDraw.Draw(name_box)
        dgb = ImageDraw.Draw(degree_box)
        mnb = ImageDraw.Draw(money_box)
        hori = ImageDraw.Draw(horizontal)
        # Write/Alligning
        nb.text((name_box.width/4, 0), name.upper(), font=fnt_name, fill=co_name)
        dgb.text((name_box.width/2, 0), guild.capitalize(), font=fnt_degree, fill=co_partner)
        mnb.text((0, 0), money, font=fnt_money, fill=co_money)
        hori.text((3, 541), age, font=fnt_age, fill=co_age)
        hori.text((730 - hori.textsize(guild, font=fnt_guild)[0], 540), guild, font=fnt_guild, fill=co_guild)
        hori.text((730 - hori.textsize(rank, font=fnt_rank)[0], 555), rank, font=fnt_rank, fill=co_rank)
        hori.text((700 - hori.textsize(evo, font=fnt_evo)[0], 420), evo, font=fnt_evo, fill=co_evo)
        hori.text((525 , 384), death, font=fnt_kd, fill=co_death)
        hori.text((547 , 334), kill, font=fnt_kd, fill=co_kill)
        # Rotating
        name_box = name_box.rotate(90)
        degree_box = degree_box.rotate(90)
        money_box = money_box.rotate(90, center=(400, 0))

        # Middle aligning
        char_midcoordX = 50 + int((398 - char_img.width)/2)
        if char_midcoordX < 0: char_midcoordX = 0

        # Composing
        bg.alpha_composite(badge_img, dest=(800 - (badge_img.width + 5), 5))
        bg.alpha_composite(form_img)
        bg.alpha_composite(char_img, dest=(char_midcoordX, 8 + pos_offset))            #Prev=56
        bg.alpha_composite(name_box, dest=(0, 38), source=(108, 0))
        bg.alpha_composite(degree_box, dest=(0, 10), source=(45, 0))
        bg.alpha_composite(money_box, dest=(344, 89))
        bg.alpha_composite(horizontal)

        output_buffer = BytesIO()
        bg.save(output_buffer, 'png')
        output_buffer.seek(0)

        # Closing???
        char_img.close()
        name_box.close()
        degree_box.close()
        money_box.close()
        horizontal.close()
        nb = None
        dgb = None
        mnb = None
        hori = None
        gc.collect()

        #bg.show()
        return bg

    async def cogif(self, user_id, char_img, pack):

        # INFO prep =============================
        pack_PI = await self.client.quefe(f"SELECT age, evo, kills, deaths, money, name FROM personal_info WHERE id='{user_id}';")
        pack_PG = await self.client.quefe(f"SELECT guild_code, rank FROM pi_guild WHERE user_id='{user_id}';")
        pack_E = await self.client.quefe(f"SELECT guild_name FROM model_guild WHERE guild_code='{pack_PG[0]}';"); pack_E = pack_E[0]

        # PARTICLEs prep ========================
        # particle_after = []
        outImPart = []
        particles = imageio.mimread('C:/Users/DELL/Downloads/gif/train.gif', memtest=False)
        partilen = len(particles)

        bar = 20                               # Set a maximum particles in ordercli a gif not overload
        if partilen > bar:
            divider = int(partilen/bar)
        else: divider = 1
        modulair = partilen%bar

        # ANIMATION of char_img prep ================
        # ODD amount of particles
        if partilen%2:
            temp = list(range((partilen-2-modulair)//(divider*2)))
            temp2 = list(range((partilen-2-modulair)//(divider*2)))
            temp2.reverse()
            offset_band = [0] + temp + [temp2[0]+1] + temp2
        # Non-odd amount of particles
        else:
            temp = list(range((partilen-1-modulair)//(divider*2)))
            temp2 = list(range((partilen-1-modulair)//(divider*2)))
            temp2.reverse()
            offset_band = [0] + temp + [temp2[0]] + temp2
        
        # GATHERING particles =======================
        print(offset_band, divider, partilen, modulair)
        count = divider
        obpointer = -1
        for particle in particles:
            await asyncio.sleep(0.05)

            if count == divider:
                count = 1
                offval = offset_band[obpointer]
                obpointer += 1
            else:
                # print(count)
                count += 1
                continue
            print(f"LOOOPPPPP {obpointer} {offval}")
            a = Image.fromarray(particle)
            a = a.resize((800, 600), resample=Image.LANCZOS)
            a = a.filter(ImageFilter.GaussianBlur(2.6))

            # PROCESS and STITCH
            try:
                #particle = particles[count]
                #a = Image.fromarray(particle)  

                #out_img = await self.gafiking(user_id, a, char_img)
                out_img = await self.gafiking(user_id, a, char_img, pack, pos_offset=offval, pack_PI=pack_PI, pack_PG=pack_PG, pack_E=pack_E)
                await asyncio.sleep(0.1)
                #outImPart.append(np.asarray(a))
                outImPart.append(out_img)
            except IndexError: break
        
        output_buffer = BytesIO()
        #imageio.mimwrite(output_buffer, outImPart)
        outImPart[0].save(output_buffer, save_all=True, format='gif', append_images=outImPart, loop=0)
        output_buffer.seek(0)
        #return await self.client.loop.run_in_executor(None, self.imgur_client.upload, output_buffer)
        return output_buffer


    async def bg_generator(self, bg_code, blur_rate=2.6):
        # Random FILE name
        bg_path = random.choice(self.bg_dir[bg_code])
        # Get FULL PATH
        bg_path = path.join('data', 'profile', 'bg', self.bg_dict[bg_code], bg_path)
        img = Image.open(bg_path).convert('RGBA')
        img = img.resize((800, 600), resample=Image.LANCZOS)
        img = img.filter(ImageFilter.GaussianBlur(blur_rate))
        return img

    async def char_generator(self, char_code):
        # Random FILE name
        char_path = random.choice(self.char_dir[char_code])
        # Get FULL PATH
        char_path = path.join('data', 'profile', 'char', self.char_dict[char_code], char_path)
        img = Image.open(char_path).convert('RGBA')
        img = img.resize((int(self.prote_lib['form'][0].height/img.height*img.width), self.prote_lib['form'][0].height), resample=Image.LANCZOS)
        return img

    async def prote_plugin(self):
        #def byte_supporter(img, output_buffer, char):
        #    output_buffer = BytesIO()
        #    img.save(output_buffer, 'png')
        #    output_buffer.seek(0)
        #    self.prote_lib[char].append(output_buffer)

        # Cards get
        cards = await self.client.quefe("SELECT hero_code FROM model_hero;", type='all')
        self.prote_lib['card'] = {}
        card_codes = {}
        for card in cards:
            card_codes[card[0]] = card[0]

        # Fonts get
        self.prote_lib['font'] = {}
        fonts = await self.client.quefe(f"SELECT font_id FROM model_font;", type='all')
        for font in fonts:
            assdir_font = path.join('data', 'profile', 'font', self.font_dict[font[0]])
            # print(assdir_font)
            # print(path.abspath('..'))
            self.prote_lib['font'][font[0]] = {}
            self.prote_lib['font'][font[0]]['name'] = ImageFont.truetype(assdir_font, 70)    # Name
            self.prote_lib['font'][font[0]]['degree'] = ImageFont.truetype(assdir_font, 14)  # Degrees
            self.prote_lib['font'][font[0]]['age'] = ImageFont.truetype(assdir_font, 54)     # Age
            self.prote_lib['font'][font[0]]['k/d'] = ImageFont.truetype(assdir_font, 59)    # K/D
            self.prote_lib['font'][font[0]]['evo'] = ImageFont.truetype(assdir_font, 122)    # Evo
            self.prote_lib['font'][font[0]]['guild'] = ImageFont.truetype(assdir_font, 19)   # Guild
            self.prote_lib['font'][font[0]]['rank'] = ImageFont.truetype(assdir_font, 39)    # Rank
            self.prote_lib['font'][font[0]]['money'] = ImageFont.truetype(assdir_font, 53)   # Money

        """
        def ImageGen_supporter(char, rawimg):
            img = Image.open(f'C:/Users/DELL/Desktop/bot_cli/data/profile/char/{char}/{rawimg}').convert('RGBA')
            img = img.resize((int(self.prote_lib['form'][0].height/img.height*img.width), self.prote_lib['form'][0].height), resample=Image.LANCZOS)
            self.prote_lib[prote_codes[char]].append(img)
        """
        """
        def BackgroundGen_supporter(bg_name, rawimg):
            img = Image.open(f'C:/Users/DELL/Desktop/bot_cli/data/profile/bg/{bg_name}/{rawimg}').convert('RGBA')
            img = img.resize((800, 600), resample=Image.LANCZOS)
            img = img.filter(ImageFilter.GaussianBlur(2.6))
            self.prote_lib['bg'][bg_codes[bg_name]].append(img)
        """

        """
        def CardGen_supporter(card_code, rawimg):
            img = Image.open(path.join('data', 'card', rawimg)).convert('RGBA')
            img = img.resize((190, 327), resample=Image.LANCZOS)
            self.prote_lib['card'][card_code].append(img)
        """

        def bg_plugin():
            """
            self.prote_lib['bg'] = {}
            self.prote_lib['bg_stock'] = []
            self.prote_lib['stock_bar'] = []
            """
            self.prote_lib['bg_gif'] = []
            self.prote_lib['bg_deck'] = []

            """"
            for bg_name, bg_id in bg_codes.items():
                self.prote_lib['bg'][bg_id] = []
                for rawimg in listdir(f'C:/Users/DELL/Desktop/bot_cli/data/profile/bg/{bg_name}'):
                    BackgroundGen_supporter(bg_name, rawimg)
                    #await self.client.loop.run_in_executor(None, ImageGen_supporter, char_name, rawimg)
            """
            """
            path.join('data', 'stock graph', 'bg_roll.png')
            img = Image.open(path.join('data', 'stock graph', 'bg_roll.png')).convert('RGBA')
            self.prote_lib['bg_stock'].append(img)
            img = Image.open(path.join('data', 'stock graph', 'bar.png')).convert('RGBA')
            self.prote_lib['stock_bar'].append(img)
            """

            # DECK =====================
            """
            img = Image.open(path.join('data', 'card', 'board600.png')).convert('RGBA')
            img = img.resize((600, 355), resample=Image.LANCZOS)
            self.prote_lib['bg_deck'].append(img)
            """
            """
            particle_after = []
            particles = imageio.mimread('C:/Users/DELL/Downloads/gif/train.gif', memtest=False)
            for particle in particles:
                a = Image.fromarray(particle)
                a = a.resize((800, 600), resample=Image.LANCZOS)
                a = a.filter(ImageFilter.GaussianBlur(2.6))
                particle_after.append(a)
            self.prote_lib['bg_gif'].append(particle_after)
            """

        def form_plugin():
            self.prote_lib['form'] = []
            img = Image.open(path.join('data', 'profile', 'form4.png')).convert('RGBA')
            self.prote_lib['form'].append(img)
        
        def badge_plugin():
            ranking_badges = {'iron': 'badge_IRON.png', 'bronze': 'badge_BRONZE.png', 'silver': 'badge_SILVER.png', 'gold': 'badge_GOLD.png', 'adamantite': 'badge_ADAMANTITE.png', 'mithryl': 'badge_MITHRYL.png'}
            self.prote_lib['badge'] = {}
            for key, dir in ranking_badges.items():
                badge_img = Image.open(path.join('data', 'profile', 'badges', dir)).convert('RGBA')
                badge_img = badge_img.resize((int(badge_img.width/1.5), int(badge_img.height/1.5)), resample=Image.LANCZOS)
                self.prote_lib['badge'][key] = badge_img

        def font_plugin():
            self.prote_lib['font']['stock_region'] = ImageFont.truetype(path.join('data', 'stock graph', 'CAROBTN.ttf'), 31)
            self.prote_lib['font']['stock_region_bar'] = ImageFont.truetype(path.join('data', 'stock graph', 'CAROBTN.ttf'), 15)
            self.prote_lib['font']['stock_region_name'] = ImageFont.truetype(path.join('data', 'stock graph', 'CAROBTN.ttf'), 62)

        #print("HERE")
        await self.client.loop.run_in_executor(None, bg_plugin)
        await self.client.loop.run_in_executor(None, form_plugin)
        await self.client.loop.run_in_executor(None, font_plugin)
        await self.client.loop.run_in_executor(None, badge_plugin)

        """
        for char_name, card_code in card_codes.items():
            self.prote_lib['card'][card_code] = []
            for rawimg in listdir(path.join('data', 'card', char_name)):
                CardGen_supporter(char_name, rawimg)
                #await self.client.loop.run_in_executor(None, ImageGen_supporter, char_name, rawimg)
        """
        """
        for char_name, char_id in prote_codes.items():
            self.prote_lib[char_id] = []
            for rawimg in listdir(f'C:/Users/DELL/Desktop/bot_cli/data/profile/char/{char_name}'):
                ImageGen_supporter(char_name, rawimg)
                #await self.client.loop.run_in_executor(None, ImageGen_supporter, char_name, rawimg)
        """

    def pillowingAvatar(self, img=(), pack=(), pack2=(), jout=None):

        bg, char_img, form_img, badge_img = img
        co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death, char_name, bg_code, font_id = pack
        age, evo, kill, death, money, name, partner_temp, partner, guild_code, rank, guild = pack2
        # fnt_name, fnt_degree, fnt_age, fnt_kd, fnt_guild, fnt_rank, fnt_evo, fnt_money = font

        # font_id = font_dict[font_id]
        # assdir = path.join('data', 'profile', 'font')

        # fnt_name = ImageFont.truetype(path.join(assdir, font_id), 70)    # Name
        # fnt_degree = ImageFont.truetype(path.join(assdir, font_id), 14)  # Degrees
        # fnt_age = ImageFont.truetype(path.join(assdir, font_id), 54)     # Age
        # fnt_kd = ImageFont.truetype(path.join(assdir, font_id), 59)    # K/D
        # fnt_evo = ImageFont.truetype(path.join(assdir, font_id), 122)    # Evo
        # fnt_guild = ImageFont.truetype(path.join(assdir, font_id), 19)   # Guild
        # # fnt_rank = ImageFont.truetype(path.join(assdir, font_id), 39)    # Rank
        # fnt_rank = fnt_guild
        # fnt_money = ImageFont.truetype(path.join(assdir, font_id), 53)   # Money

        fnt_name = self.prote_lib['font'][font_id]['name']            # Name
        fnt_degree = self.prote_lib['font'][font_id]['guild']        # Degrees
        fnt_age = self.prote_lib['font'][font_id]['age']              # Age
        fnt_kd = self.prote_lib['font'][font_id]['k/d']               # K/D
        fnt_guild = self.prote_lib['font'][font_id]['guild']          # Guild
        fnt_rank = self.prote_lib['font'][font_id]['rank']            # Rank
        fnt_evo = self.prote_lib['font'][font_id]['evo']              # evo
        fnt_money = self.prote_lib['font'][font_id]['money']          # Money

        name_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
        degree_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
        money_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
        horizontal = Image.new('RGBA', form_img.size, (255, 255, 255, 0))

        # Get text canvas
        nb = ImageDraw.Draw(name_box)
        dgb = ImageDraw.Draw(degree_box)
        mnb = ImageDraw.Draw(money_box)
        hori = ImageDraw.Draw(horizontal)
        # Write/Alligning
        nb.text((name_box.width/4, 0), name.upper(), font=fnt_name, fill=co_name)
        dgb.text((name_box.width/2, 0), partner.capitalize(), font=fnt_degree, fill=co_partner)
        mnb.text((0, 0), money, font=fnt_money, fill=co_money)
        hori.text((3, 541), age, font=fnt_age, fill=co_age)
        hori.text((730 - hori.textsize(guild, font=fnt_guild)[0], 540), guild, font=fnt_guild, fill=co_guild)
        hori.text((730 - hori.textsize(rank, font=fnt_rank)[0], 555), rank, font=fnt_rank, fill=co_rank)
        hori.text((700 - hori.textsize(evo, font=fnt_evo)[0], 420), evo, font=fnt_evo, fill=co_evo)
        hori.text((525 , 384), death, font=fnt_kd, fill=co_death)
        hori.text((547 , 334), kill, font=fnt_kd, fill=co_kill)
        # Rotating
        name_box = name_box.rotate(90)
        degree_box = degree_box.rotate(90)
        money_box = money_box.rotate(90, center=(400, 0))

        # Middle aligning
        char_midcoordX = 50 + int((398 - char_img.width)/2)
        if char_midcoordX < 0: char_midcoordX = 0

        # Composing
        bg.alpha_composite(badge_img, dest=(800 - (badge_img.width + 5), 5))
        bg.alpha_composite(form_img)
        bg.alpha_composite(char_img, dest=(char_midcoordX, 8))            #Prev=56
        bg.alpha_composite(name_box, dest=(0, 38), source=(108, 0))
        bg.alpha_composite(degree_box, dest=(0, 10), source=(45, 0))
        bg.alpha_composite(money_box, dest=(344, 89))
        bg.alpha_composite(horizontal)

        output_buffer = BytesIO()
        bg.save(output_buffer, 'png')
        output_buffer.seek(0)

        # # Release?
        # bg = None
        # badge_img = None
        # form_img = None
        # char_img = None
        # name_box = None
        # degree_box = None
        # money_box = None
        # horizontal = None
        # nb = None
        # dgb = None
        # mnb = None
        # hori = None
        # gc.collect()

        # Closing???
        bg.close()
        char_img.close()
        name_box.close()
        degree_box.close()
        money_box.close()
        horizontal.close()
        nb = None
        dgb = None
        mnb = None
        hori = None
        gc.collect()

        return output_buffer
        # jout.put(output_buffer)





def setup(client):
    client.add_cog(avaAvatar(client))
