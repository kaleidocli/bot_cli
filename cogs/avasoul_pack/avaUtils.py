from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import math
import random
import numpy as np
import json
from os import path

import discord

class avaUtils:

    def __init__(self, client):
        """
            Note: Two Nix archive server IDs (637838584996560896 for EC3, 644092524595642388 for EC4)
        """

        self.client = client
        self.smoltext = str.maketrans({'a': 'ᵃ', 'b': 'ᵇ', 'c': 'ᶜ', 'd': 'ᵈ', 'e': 'ᵉ', 'f': 'ᶠ', 'g': 'ᵍ', 'h': 'ʰ', 'i': 'ᶦ',
                                'j': 'ʲ', 'k': 'ᵏ', 'l': 'ˡ', 'm': 'ᵐ', 'n': 'ⁿ', 'o': 'ᵒ', 'p': 'ᵖ', 'q': 'ᵠ', 'r': 'ʳ',
                                's': 'ˢ', 't': 'ᵗ', 'u': 'ᵘ', 'v': 'ᵛ', 'w': 'ʷ', 'x': 'ˣ', 'y': 'ʸ', 'z': 'ᶻ',
                                '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
                                ')': '⁾', '(': '⁽'})
        
        self.nixtext = {}
        self.nixified = False



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

        if total <= 0 or percent <= 0: return False
        if random.randint(0, total) <= percent: return True
        else: return False

    async def space_out(self, text, space=' '):
        return space.join([f"{ch}" for ch in text])

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
        """
            You need to send temp to check the embed
        """

        temp = discord.Embed()
        try:
            temp.set_image(url=illulink)
            return temp
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

    def nixietext(self, text):
        if not self.nixified:
            try:
                with open(path.join('.', '.', '.', 'data', 'nixie_text.json'), mode='r') as nfp:
                    nx = json.load(nfp)
            except json.decoder.JSONDecodeError:
                with open(path.join('.', '.', '.', 'data', 'nixie_text.json'), mode='w') as nfp:
                    nx = {
                            'a': 'nix_lower_a', 'b': 'nix_lower_b', 'c': 'nix_lower_c', 'd': 'nix_lower_d', 'e': 'nix_lower_e', 'f': 'nix_lower_f', 'g': 'nix_lower_g', 'h': 'nix_lower_h', 'i': 'nix_lower_i',
                            'j': 'nix_lower_j', 'k': 'nix_lower_k', 'l': 'nix_lower_l', 'm': 'nix_lower_m', 'n': 'nix_lower_n', 'o': 'nix_lower_o', 'p': 'nix_lower_p', 'q': 'nix_lower_q', 'r': 'nix_lower_r',
                            's': 'nix_lower_s', 't': 'nix_lower_t', 'u': 'nix_lower_u', 'v': 'nix_lower_v', 'w': 'nix_lower_w', 'x': 'nix_lower_x', 'y': 'nix_lower_y', 'z': 'nix_lower_z',
                            'A': 'nix_A', 'B': 'nix_B', 'C': 'nix_C', 'D': 'nix_D', 'E': 'nix_E', 'F': 'nix_F', 'G': 'nix_G', 'H': 'nix_H', 'I': 'nix_I',
                            'J': 'nix_J', 'K': 'nix_K', 'L': 'nix_L', 'M': 'nix_M', 'N': 'nix_N', 'O': 'nix_O', 'P': 'nix_P', 'Q': 'nix_Q', 'R': 'nix_R',
                            'S': 'nix_S', 'T': 'nix_T', 'U': 'nix_U', 'V': 'nix_V', 'W': 'nix_W', 'X': 'nix_X', 'Y': 'nix_Y', 'Z': 'nix_Z',
                            '0': 'nix_0', '1': 'nix_1', '2': 'nix_2', '3': 'nix_3', '4': 'nix_4', '5': 'nix_5', '6': 'nix_6', '7': 'nix_7', '8': 'nix_8', '9': 'nix_9',
                            '!': 'nix_exclamation', '@': 'nix_at', '#': 'nix_hash', '$': 'nix_dollar', '%': 'nix_percent', '^': 'nix_carat', '&': 'nix_ampersand', '*': 'nix_asterisk', '(': 'nix_lparen', ')': 'nix_rparen', '-': 'nix_dash', '+': 'nix_plus', '_': 'nix_underbar', '=': 'nix_equal',
                            '{': 'nix_lcurly', '}': 'nix_rcurly', '[': 'nix_lsquare', ']': 'nix_rsquare', '|': 'nix_pipe', '/': 'nix_slash', '\\': 'nix_backslash', ' ': 'nix_space',
                            ':': 'nix_colon', ';': 'nix_semi', "'": 'nix_singlequote', '"': 'nix_dquote', '>': 'nix_greater', '<': 'nix_less', '?': 'nix_question', ',': 'nix_comma', '.': 'nix_period', '~': 'nix_approx', '`': 'nix_backquote'
                        }

                    emojis = self.nixie_getEmojis()
                    print(emojis)

                    for k, v in nx.items():
                        for e in emojis:
                            if not e: continue
                            print(v, e, str(e))
                            if v == e.name:
                                nx[k] = str(e)

                    print(nx)

                    json.dump(nx, nfp, ensure_ascii=True, indent=4)

            self.nixtext = str.maketrans(nx)
            self.nixified = True

        return text.translate(self.nixtext)

    def nixie_getEmojis(self):
        # Get two archive
        ECs = [] 
        for id in (637838584996560896, 644092524595642388):
            try:
                a = self.client.get_guild(id)
                print(id, a)
                ECs.append(a)
            except TypeError: continue
        # Get emoji
        Em = ()
        for EC in ECs:
            try: Em = Em + EC.emojis
            except AttributeError: continue
        return Em

    def rewardToQueryAndName(self, reward):
        """
            reward     List            (type/code, quantity, percentage)

            Return (itemQuery, statusSubQuery, name)
        """
        status = {
            'money': '<:36pxGold:548661444133126185>',
            'perks': '<:perk:632340885996044298>',
            'merit': '<:merit_badge:620137704662761512>'
        }
        itemQuery = ''
        statusSubQuery = ''
        name = ''

        # Query / Name
        # --- Status
        if reward[0] in status.keys():
            statusSubQuery += f"{reward[0]}={reward[0]}+{reward[1]}"
            name = 'Received (**{}**) {}'.format(reward[1], status[reward[0]])
        # --- Item
        else:
            protoItem = self.client.DBC['model_item'][reward[0]]
            if protoItem.rootTable == 'item':
                itemQuery += f"""SELECT func_it_reward("user_id_here", "{reward[0]}", {reward[1]});"""
            else:
                itemQuery += f"""SELECT func_ig_reward("user_id_here", "{reward[0]}", {reward[1]});"""
            name = '· Received (**{}**) item `{}`| **{}**'.format(reward[1], protoItem.item_code, protoItem.name)

        return (itemQuery, statusSubQuery, name)
