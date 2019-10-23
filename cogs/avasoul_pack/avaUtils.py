from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import math
import random
import numpy as np

import discord

class avaUtils:

    def __init__(self, client):
        self.client = client
        self.smoltext = str.maketrans({'a': 'ᵃ', 'b': 'ᵇ', 'c': 'ᶜ', 'd': 'ᵈ', 'e': 'ᵉ', 'f': 'ᶠ', 'g': 'ᵍ', 'h': 'ʰ', 'i': 'ᶦ',
                                'j': 'ʲ', 'k': 'ᵏ', 'l': 'ˡ', 'm': 'ᵐ', 'n': 'ⁿ', 'o': 'ᵒ', 'p': 'ᵖ', 'q': 'ᵠ', 'r': 'ʳ',
                                's': 'ˢ', 't': 'ᵗ', 'u': 'ᵘ', 'v': 'ᵛ', 'w': 'ʷ', 'x': 'ˣ', 'y': 'ʸ', 'z': 'ᶻ',
                                '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'})

    def time_get(self):
        day = 1; month = 1; year = 1
        delta = relativedelta(datetime.now(), self.client.STONE)
        #print(f"DELTA: {delta.days} | {delta.months} | {delta.years}")

        if not delta.months: delta.months = 1
        # Year
        year = (delta.days+(delta.months*30))+(360*delta.years)
        # Month
        try: month = int(delta.hours/2)
        except: pass
        secs_temp = delta.seconds + 60*delta.minutes + 3600*(delta.hours%2)
        # Day
        day = int(secs_temp/240)
        # Hour
        if secs_temp <= 240:
            hour = int(secs_temp/10)
        elif secs_temp > 240:
            hour = int((secs_temp%240)/10)
        # Minute
        if secs_temp <= 10:
            minute = int(secs_temp/0.16)
        elif secs_temp > 10:
            minute = int((secs_temp%10)/0.16)

        if not year: year = 1
        if not month: month = 1
        
        return year, month, day, hour, minute

    async def converter(self, type, *args):
        if type == 'sec_to_hms':
            hour = args[0]//3600
            if hour != 0: 
                secleft = args[0]%3600
                min = secleft//60
            else:
                secleft = args[0]
                min = secleft//60
            if min != 0:
                sec = secleft%60
            else:
                sec = secleft
            return (hour, min, sec)

    async def distance_tools(self, x1, y1, x2, y2, distance=0, type='c-d'):
        """| Tools\n
           x1, y1, x2, y2, distance: float\n
           (x1, y1: user's coord)\n
           return: distance"""

        if type == 'c-d':
            dist_x = abs(x1 - x2); dist_y = abs(y1 - y2)

            return int(math.sqrt(dist_x*dist_x + dist_y*dist_y)*1000)

        elif type == 'd-c':
            dist_x = abs(x1 - x2); dist_y = abs(y1 - y2)
            # Distance from A to B      |      distance --> Distance from A to C
            full_dist = math.sqrt(dist_x*dist_x + dist_y*dist_y)*1000

            # Thales thingy
            small_dist_x = (distance*dist_x)/full_dist
            small_dist_y = (distance*dist_y)/full_dist

            # Calc coord, then return
            if x1 >= x2: C_x = x1 - small_dist_x
            else: C_x = x1 + small_dist_x
            if y1 >= y2: C_y = y1 - small_dist_y
            else: C_y = y1 + small_dist_y
            
            return C_x, C_y #round(C_x, 3) , round(C_y, 3)

    async def percenter(self, percent, total=10, anti=False, anti_limit=90):
        # Anti-100%
        if anti:
            if percent > anti_limit: percent = anti_limit

        total = range(total)
        if len(total) <= 0 or percent <= 0: return False
        if random.choice(total) <= percent: return True
        else: return False

    async def space_out(self, text):
        return ' '.join([f"{ch} " for ch in text])

    async def inj_filter(self, text):
        text = text.replace("'", ' ')
        text = text.replace("=", ' ')
        text = text.replace("`", ' ')
        text = text.replace("\"", ' ')
        text = text.replace(";", ' ')
        text = text.replace("DROP ", "DR0P ")
        text = text.replace("TRUNCATE ", 'TRUNKATE ')
        text = text.replace("DELETE ", 'DELELE ')
        text = text.replace("UPDATE ", "UPDOTE ")
        return text

    async def realty_calc(self, inipr, taim, averange):
        temp = []
        for self.client.thp._cursor in averange:
            init_price = inipr
            print(taim, init_price)
            if taim[0] % 10 == 0:
                if (taim[2] + self.client.thp._cursor) % 10 == 0: init_price *= 10
                else: init_price /= 10
            elif taim[0] % 7 == 0:
                if (taim[2] + self.client.thp._cursor) % 7 == 0: init_price *= 7
                else: init_price /= 7
            elif taim[0] % 5 == 0:
                if (taim[2] + self.client.thp._cursor) % 5 == 0: init_price *= 5
                else: init_price /= 5
            elif taim[0] % 3 == 0:
                if (taim[2] + self.client.thp._cursor) % 3 == 0: init_price *= 3
                else: init_price /= 3
            elif taim[0] % 2 == 0:
                if (taim[2] + self.client.thp._cursor) % 2 == 0: init_price *= 2
                else: init_price /= 2

            if (taim[2] + self.client.thp._cursor) % 10 == 0:
                if taim[0] % 10 == 0: init_price /= 10
                else: init_price *= 10
            elif (taim[2] + self.client.thp._cursor) % 7 == 0:
                if taim[0] % 7 == 0: init_price /= 7
                else: init_price *= 7
            elif (taim[2] + self.client.thp._cursor) % 5 == 0:
                if taim[0] % 5 == 0: init_price /= 5
                else: init_price *= 5
            elif (taim[2] + self.client.thp._cursor) % 3 == 0:
                if taim[0] % 3 == 0: init_price /= 3
                else: init_price *= 3
            elif (taim[2] + self.client.thp._cursor) % 2 == 0:
                if taim[0] % 2 == 0: init_price /= 2
                else: init_price *= 2

            temp.append(init_price)
        print("RAW Realty Sess", temp)
        return int(np.mean(temp))

    async def illulink_check(self, illulink):
        temp = discord.Embed()
        try:
            temp.set_image(url=illulink)
            return illulink
        except discord.errors.HTTPException: return False

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    def smalltext(self, text):
        """
        ᵗᵘʳⁿˢ ʸᵒᵘʳ ᵗᵉˣᵗ ᶦⁿᵗᵒ ˢᵐᵃˡˡ ᵗᵉˣᵗ \n
        Credit: (GitHub) XuaTheGrate \n
        Source: https://github.com/XuaTheGrate/Abyss/blob/master/cogs/shit.py#L14-L17
        """
        return text.lower().translate(self.smoltext)



    # Obsolete from JSON ver
    """def objectize(self, dict, type, *args): 
        if type[0] == 'weapon':
            if type[1] == 'melee':
                return weapon((dict['name'], dict['id'], dict['description'], dict['tags'], dict['price'], dict['weight'], dict['defend'], dict['multiplier'], dict['str'], dict['sta'], dict['speed'], dict), 'melee')
            elif type[1] == 'range_weapon':
                return weapon((dict['name'], dict['id'], dict['description'], dict['tags'], dict['price'], dict['weight'], dict['defend'], dict['round'], dict['str'], dict['int'], dict['sta'], dict['accuracy'], dict['range'], dict['firing_rate'], dict['stealth'], dict), 'range_weapon')
        elif type[0] == 'ammunition':
            return ammunition((dict['name'], dict['id'], dict['description'], dict['tags'], dict['price'], dict['dmg'], dict['speed'], dict))
        elif type[0] == 'supply':
            return item((dict['name'], dict['id'], dict['description'], dict['tags'], dict['price'], dict), args[0])
        elif type[0] == 'ingredient':
            return ingredient((dict['name'], dict['id'], dict['description'], dict['tags'], dict['price'], dict), args[0])
    """

# Obsolete from JSON ver
"""
class mob:
    def __init__(self, whole_pack):
        self.name = whole_pack['name']
        self.lp = whole_pack['lp']
        self.str = whole_pack['str']
        self.speed = whole_pack['speed']
        self.drop = whole_pack['drop']
        self.branch = whole_pack['branch']
        self.chain = whole_pack['chain']

    def attack(self):
        mmoves = [random.choice(['a', 'd', 'b']) for move in range(self.chain)]
        
        # Decoding moves, as well as checking the moves. Get the counter_move
        counter_mmove = []
        for move in mmoves:
            if move == 'a': counter_mmove.append('d')
            elif move == 'd': counter_mmove.append('b')
            elif move == 'b': counter_mmove.append('a')

        dmg = self.str
        return dmg, mmoves, counter_mmove

    #def defend(self, )

    def drop_item(self):
        drops = []
        for item in list(self.drop.keys()):
            # [0]: Item's name | [1]: Quantity | [2]: Drop rate
            ###Randoming pick
            if random.choice(range(self.drop[item][2])) == 0:
                ###Randoming quantity
                drops.append([self.drop[item][0], random.choice(range(self.drop[item][1]))])
        return drops
            
class item:
    def __init__(self, package, func):
        self.name, self.id, self.description, self.tags, self.price, self.bkdict = package
        self.func = func

class ingredient:
    def __init__(self, package, func):
        self.name, self.id, self.description, self.tags, self.price, self.bkdict = package
        self.func = func

class weapon:
    def __init__(self, package, type, func=None, upgrade=None):
        # Unpack guidance
        if type == 'melee': self.name, self.id, self.description, self.tags, self.price, self.weight, self.defend, self.multiplier, self.str, self.sta, self.speed, self.bkdict = package
        elif type == 'range_weapon': self.name, self.id, self.description, self.tags, self.price, self.weight, self.defend, self.round, self.str, self.int, self.sta, self.accuracy, self.range, self.firing_rate, self.stealth, self.bkdict = package

        self.func = func
        self.upgrade = upgrade

class ammunition:
    def __init__(self, package):
        self.name, self.id, self.description, self.tags, self.price, self.dmg, self.speed, self.bkdict = package
"""
