import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio

from os import listdir, path
from pathlib import Path
from io import BytesIO
import copy
import asyncio
import random

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
                    'bg10': 'pengzhen_zhang'}
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
                        'av28': 'SAO_Asuna'}


        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)



    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(2)      # Do not remove, or else the data stream would mix with WORLD_BUILDING
        await self.prote_plugin()



    async def bg_generator(self, bg_code):
        bg_path = random.choice(listdir(path.join(Path(__file__).parent.parent.parent, 'data', 'profile', 'bg', self.bg_dict[bg_code])))
        bg_path = path.join(Path(__file__).parent.parent.parent, 'data', 'profile', 'bg', self.bg_dict[bg_code], bg_path)
        img = Image.open(bg_path).convert('RGBA')
        img = img.resize((800, 600))
        img = img.filter(ImageFilter.GaussianBlur(2.6))
        return img

    async def char_generator(self, char_code):
        char_path = random.choice(listdir(path.join(Path(__file__).parent.parent.parent, 'data', 'profile', 'char', self.char_dict[char_code])))
        char_path = path.join(Path(__file__).parent.parent.parent, 'data', 'profile', 'char', self.char_dict[char_code], char_path)
        img = Image.open(char_path).convert('RGBA')
        img = img.resize((int(self.prote_lib['form'][0].height/img.height*img.width), self.prote_lib['form'][0].height))
        return img

    async def prote_plugin(self):
        #def byte_supporter(img, output_buffer, char):
        #    output_buffer = BytesIO()
        #    img.save(output_buffer, 'png')
        #    output_buffer.seek(0)
        #    self.prote_lib[char].append(output_buffer)
        """
        prote_codes = {'Iris': 'av0',
                        'Zoey': 'av1',
                        'Ardena': 'av2',
                        'Yamabuki': 'av3',
                        'Yamabuki_Cosplay': 'av4',
                        'Yamabuki_NSFW': 'av5',
                        'Myu': 'av6',
                        'Myu_NSFW': 'av7',
                        'Enju': 'av8',
                        'Enju_NSFW': 'av9',
                        'Enju_Cosplay': 'av10',
                        'Shima_Rin': 'av11',
                        'Akari': 'av12',
                        'Akari_NSFW': 'av13',
                        'Akari_Cosplay': 'av14',
                        'RPG_Girl_1': 'av15',
                        'GBF_Female': 'av16',
                        'GBF_Male': 'av17',
                        'GBF_Female_2': 'av18',
                        'Djeeta': 'av19',
                        'Ricka': 'av20',
                        'Ricka_Cosplay': 'av21',
                        'Ricka_NSFW': 'av22',
                        'set_FURRY': 'av23'}

        ##bg_codes = {'LoveRibbon/evening': 'bg0'}
        bg_codes = {'medieval_indoor': 'bg0',
                    'medieval_outdoor': 'bg1',
                    'modern_indoor': 'bg2',
                    'modern_outdoor': 'bg3',
                    'fengfeng': 'bg4',
                    'sleepypang': 'bg5',
                    'rocha_cold': 'bg6',
                    'rocha_crimson': 'bg7',
                    'rocha_gold': 'bg8',
                    'rocha_green': 'bg9'}
        """

        # Cards get
        cards = await self.client.quefe("SELECT hero_code FROM model_hero;", type='all')
        self.prote_lib['card'] = {}
        card_codes = {}
        for card in cards:
            card_codes[card[0]] = card[0]

        """
        def ImageGen_supporter(char, rawimg):
            img = Image.open(f'C:/Users/DELL/Desktop/bot_cli/data/profile/char/{char}/{rawimg}').convert('RGBA')
            img = img.resize((int(self.prote_lib['form'][0].height/img.height*img.width), self.prote_lib['form'][0].height))
            self.prote_lib[prote_codes[char]].append(img)
        """
        """
        def BackgroundGen_supporter(bg_name, rawimg):
            img = Image.open(f'C:/Users/DELL/Desktop/bot_cli/data/profile/bg/{bg_name}/{rawimg}').convert('RGBA')
            img = img.resize((800, 600))
            img = img.filter(ImageFilter.GaussianBlur(2.6))
            self.prote_lib['bg'][bg_codes[bg_name]].append(img)
        """

        def CardGen_supporter(card_code, rawimg):
            img = Image.open(f'C:/Users/DELL/Desktop/bot_cli/data/card/{card_code}/{rawimg}').convert('RGBA')
            img = img.resize((190, 327))
            self.prote_lib['card'][card_code].append(img)

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
            img = Image.open(f'C:/Users/DELL/Desktop/bot_cli/data/stock graph/bg_roll.png').convert('RGBA')
            self.prote_lib['bg_stock'].append(img)
            img = Image.open(f'C:/Users/DELL/Desktop/bot_cli/data/stock graph/bar.png').convert('RGBA')
            self.prote_lib['stock_bar'].append(img)
            """

            # DECK =====================
            """
            img = Image.open(f'C:/Users/DELL/Desktop/bot_cli/data/card/board600.png').convert('RGBA')
            img = img.resize((600, 355))
            self.prote_lib['bg_deck'].append(img)
            """
            """
            particle_after = []
            particles = imageio.mimread('C:/Users/DELL/Downloads/gif/train.gif', memtest=False)
            for particle in particles:
                a = Image.fromarray(particle)
                a = a.resize((800, 600))
                a = a.filter(ImageFilter.GaussianBlur(2.6))
                particle_after.append(a)
            self.prote_lib['bg_gif'].append(particle_after)
            """

        def form_plugin():
            self.prote_lib['form'] = []
            img = Image.open('C:/Users/DELL/Desktop/bot_cli/data/profile/form4.png').convert('RGBA')
            self.prote_lib['form'].append(img)
        
        def badge_plugin():
            ranking_badges = {'iron': 'badge_IRON.png', 'bronze': 'badge_BRONZE.png', 'silver': 'badge_SILVER.png', 'gold': 'badge_GOLD.png', 'adamantite': 'badge_ADAMANTITE.png', 'mithryl': 'badge_MITHRYL.png'}
            self.prote_lib['badge'] = {}
            for key, dir in ranking_badges.items():
                badge_img = Image.open(f'C:/Users/DELL/Desktop/bot_cli/data/profile/badges/{dir}').convert('RGBA')
                badge_img = badge_img.resize((int(badge_img.width/1.5), int(badge_img.height/1.5)))
                self.prote_lib['badge'][key] = badge_img

        def font_plugin():
            self.prote_lib['font'] = {}
            self.prote_lib['font']['name'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/profile/ERASLGHT.ttf', 70)    # Name
            self.prote_lib['font']['degree'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/profile/ERASLGHT.ttf', 14)  # Degrees
            self.prote_lib['font']['age'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/profile/ERASLGHT.ttf', 54)     # Age
            self.prote_lib['font']['k/d'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/profile/ERASLGHT.ttf', 59)    # K/D
            self.prote_lib['font']['evo'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/profile/ERASLGHT.ttf', 122)    # Evo
            self.prote_lib['font']['guild'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/profile/ERASLGHT.ttf', 19)   # Guild
            self.prote_lib['font']['rank'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/profile/ERASLGHT.ttf', 39)    # Rank
            self.prote_lib['font']['money'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/profile/ERASLGHT.ttf', 53)   # Money
            self.prote_lib['font']['stock_region'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/stock graph/CAROBTN.ttf', 31)
            self.prote_lib['font']['stock_region_bar'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/stock graph/CAROBTN.ttf', 15)
            self.prote_lib['font']['stock_region_name'] = ImageFont.truetype('C:/Users/DELL/Desktop/bot_cli/data/stock graph/CAROBTN.ttf', 62)

        #print("HERE")
        await self.client.loop.run_in_executor(None, bg_plugin)
        await self.client.loop.run_in_executor(None, form_plugin)
        await self.client.loop.run_in_executor(None, font_plugin)
        await self.client.loop.run_in_executor(None, badge_plugin)

        """
        for char_name, card_code in card_codes.items():
            self.prote_lib['card'][card_code] = []
            for rawimg in listdir(f'C:/Users/DELL/Desktop/bot_cli/data/card/{char_name}'):
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
        print("|| Avatar ---- READY!")


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
            que = ''
            for ava in avas:
                que = que + f"INSERT INTO pi_backgrounds (user_id, bg_code) SELECT '{pack[0]}', '{ava}' WHERE NOT EXISTS (SELECT * FROM pi_backgrounds WHERE user_id='{pack[0]}' AND bg_code='{ava}'); "
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
        try: co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death, char_name, bg_code = await self.client.quefe(f"SELECT co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death, avatar_id, bg_code FROM cosmetic_preset WHERE user_id='{user_id}' AND stats='CURRENT';")
        except TypeError: await ctx.send(f"<:osit:544356212846886924> User has not incarnated! ({user_id})"); return
        #co_name, co_partner, co_money, co_age, co_guild, co_rank, co_evo, co_kill, co_death = ('#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF')

        # STATIC =========
        async def magiking(ctx):

            # Info get
            #pylint: disable=unused-variable
            age, evo, kill, death, money, name, partner_temp, partner = await self.client.quefe(f"SELECT age, evo, LP, STA, money, name, partner AS prtn, (SELECT name FROM personal_info WHERE id=prtn) FROM personal_info WHERE id='{user_id}';")
            if not partner: partner = '---------------------'
            #pylint: enable=unused-variable
            guild_region, rank = await self.client.quefe(f"SELECT name, rank FROM pi_guild WHERE user_id='{user_id}';")
            g_region_name = await self.client.quefe(f"SELECT name FROM environ WHERE environ_code='{guild_region}';"); g_region_name = g_region_name[0]

            form_img = self.prote_lib['form'][0]
            """char_img = random.choice(self.prote_lib[char_name])"""
            char_img = await self.char_generator(char_name)
            #char_img = char_img.resize((int(form_img.height/char_img.height*char_img.width), form_img.height))
            badge_img = self.prote_lib['badge'][rank.lower()]
            #badge_img = badge_img.resize((int(badge_img.width/1.5), int(badge_img.height/1.5)))
            #bg = self.prote_lib['bg'][0]
            """bg = copy.deepcopy(random.choice(self.prote_lib['bg'][bg_code]))"""
            bg = await self.bg_generator(bg_code)
            #bg = bg.resize((800, 600))
            #bg = bg.filter(ImageFilter.GaussianBlur(2.6))           # prev(best)=2.6
            name_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
            degree_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
            money_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
            horizontal = Image.new('RGBA', form_img.size, (255, 255, 255, 0))

            # Font Set
            fnt_name = self.prote_lib['font']['name']            # Name
            fnt_degree = self.prote_lib['font']['guild']        # Degrees
            fnt_age = self.prote_lib['font']['age']              # Age
            fnt_kd = self.prote_lib['font']['k/d']               # K/D
            fnt_guild = self.prote_lib['font']['guild']          # Guild
            fnt_rank = self.prote_lib['font']['rank']            # Rank
            fnt_evo = self.prote_lib['font']['evo']              # evo
            fnt_money = self.prote_lib['font']['money']          # Money

            # Get info
            age = str(age).upper()
            if int(age) < 10: age = '0' + age
            evo = str(evo).upper()
            kill = str(kill).upper()
            death = str(death).upper()
            money = str(money).upper()
            guild = f"{guild_region} | {g_region_name}"
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
        
            #bg.show()
            return output_buffer

        # GIF ============        
        async def gafiking(ctx, in_img, char_img, pos_offset=0, **kwargs):
            """pos_offset: Positive value for lower pos, negative for upper pos"""

            # Info get
            age, evo, kill, death, money, name = kwargs['pack_PI']
            guild_region, rank = kwargs['pack_PG']
            g_region_name = kwargs['pack_PI']; g_region_name = g_region_name

            #img = Image.open('sampleimg.jpg').convert('RGBA')
            form_img = self.prote_lib['form'][0]
            #char_img = char_img.resize((int(form_img.height/char_img.height*char_img.width), form_img.height))
            badge_img = self.prote_lib['badge'][rank.lower()]
            #badge_img = badge_img.resize((int(badge_img.width/1.5), int(badge_img.height/1.5)))
            bg = copy.deepcopy(in_img)
            #bg = bg.resize((800, 600))
            #bg = bg.filter(ImageFilter.GaussianBlur(2.6))           # prev(best)=2.6
            name_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
            degree_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
            money_box = Image.new('RGBA', form_img.size, (255, 255, 255, 0))
            horizontal = Image.new('RGBA', form_img.size, (255, 255, 255, 0))

            # Font Set
            fnt_name = self.prote_lib['font']['name']            # Name
            fnt_degree = self.prote_lib['font']['degree']        # Degrees
            fnt_age = self.prote_lib['font']['age']              # Age
            fnt_kd = self.prote_lib['font']['k/d']               # K/D
            fnt_guild = self.prote_lib['font']['guild']          # Guild
            fnt_rank = self.prote_lib['font']['rank']            # Rank
            fnt_evo = self.prote_lib['font']['evo']              # evo
            fnt_money = self.prote_lib['font']['money']          # Money

            # Get info
            age = str(age).upper()
            if int(age) < 10: age = '0' + age
            evo = str(evo).upper()
            kill = str(kill).upper()
            death = str(death).upper()
            money = str(money).upper()
            guild = f"{guild_region} | {g_region_name}"
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

            #bg.show()
            return bg

        async def cogif(ctx, char_img):

            # INFO prep =============================
            pack_PI = await self.client.quefe(f"SELECT age, evo, kills, deaths, money, name FROM personal_info WHERE id='{user_id}';")
            pack_PG = await self.client.quefe(f"SELECT name, rank FROM pi_guild WHERE user_id='{user_id}';")
            pack_E = await self.client.quefe(f"SELECT name FROM environ WHERE environ_code='{pack_PG[0]}';"); pack_E = pack_E[0]

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
                # await asyncio.sleep(0.05)

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
                a = a.resize((800, 600))
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
            output_buffer.seek(0)
            #return await self.client.loop.run_in_executor(None, self.imgur_client.upload, output_buffer)
            #return output_buffer
            await ctx.send(file=discord.File(fp=output_buffer, filename='profile.gif'))
        
        if __mode == 'static':
            await ctx.trigger_typing()
            output_buffer = await magiking(ctx)
            await ctx.send(file=discord.File(fp=output_buffer, filename='profile.png'))
        elif __mode == 'gif':
            await ctx.trigger_typing()
            char_img = await self.char_generator(char_name)
            #output_buffer = await cogif(ctx)         
            #reembed = discord.Embed(colour = discord.Colour(0x011C3A))
            #reembed.set_image(url=output_buffer['link'])
            #await ctx.send(embed=reembed)
            #await ctx.send(file=discord.File(fp=output_buffer, filename='profile.gif'))
            await cogif(ctx, char_img)





def setup(client):
    client.add_cog(avaAvatar(client))
