import random
import asyncio
from functools import partial

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors
import redis.exceptions as redisErrors

from .avaTools import avaTools
from .avaUtils import avaUtils
from utils import checks



class avaCombat(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)
        self.moveIcon_dict = {'b': '<:sword_burst:615587572717977613>',
                            'q': '<:sword_quick:615587572478902436>',
                            'a': '<:sword_art:615587572386889728>'}
        self.pcmIcon_dict = {'a': '<:wsword_aggressive:615587572420313104>',
                            'd': '<:wsword_defensive:615587572491485364>',
                            'e': '<:wsword_evasive:615587572835549223>'}
        self.effect_icon = {'poison': '<:mhw_poison:626533532898033664>',
                            'paralysis': '<:mhw_paralysis:626533532642312193>',
                            'sleep': '<:mhw_sleep:626533532956622858>',
                            'stun': '<:mhw_stun:626533532948365322>',
                            'bleed': '<:mhw_bleeding:626533532696707103>'}

        print("|| Combat ---- READY!")



# ================== EVENTS ==================

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     print("|| Combat ---- READY!")



# ================== COMBAT ==================
    # CE [effect_tag, value, percentage, strikes_to_live, time_to_live_addition]
    # ============= !< BATTLE >! ==================
    # 
    # Combat Environment (CE)
    # ---------------- CE should be called IN at the beggining of each attack, then put OUT after each one --------------------
    # [aggressive], [defensive], [evasive], [ultimate], [raw_pcm]
    # [lock], 
    #
    # <!> CONCEPTS
    # ---- WEAPON ----
    # ATK -----> STR and Multiplier for base dmg, Weight for crit
    # DEF -----> DEF for base defense, Speed for against stamina attack

    @commands.command(aliases=['mle'])
    @commands.cooldown(1, 3, type=BucketType.user)
    async def melee(self, ctx, *args):
        """ -avaattack [moves] [target]
            -avaattack [moves]              
            <!> ONE target of each creature type at a time. Mobs always come first, then user. Therefore you can't fight an user while fighting a mob
            <!> DO NOT lock on current_enemy at the beginning. Do it at the end."""
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        raw = list(args); __mode = 'PVP'
        # E: Moves not given
        #if not raw: await ctx.send(f"<:osit:544356212846886924> **{ctx.author.name}**, please make your moves!"); return

        # Get user's info (always put last, for the sake of efficience)         |        as well as checking coord
        try: name, cur_PLACE, cur_X, cur_Y = await self.client.quefe(f"SELECT name, cur_PLACE, cur_X, cur_Y FROM personal_info WHERE id='{str(ctx.message.author.id)}' AND cur_X>1 AND cur_Y>1;")
        # E: User in PB
        except TypeError: await ctx.send("<:osit:544356212846886924> You can't fight inside **Peace Belt**!"); return

        # CE - IN
        CE, CE_ttl = await self.tools.redio_map(f"CE{ctx.author.id}", mode='get', getttl=True)
        if not CE:
            CE = await self.CE_maker('')
            CE_ttl = 0
        CE['effect'] = self.CE_effect_encoder(CE['effect'])

        # INPUT CHECK =========================================
        target = None; target_id = None; raw_move = None

        for copo in raw:
            # PVP   |    USING MENTION
            if copo.startswith('<@'):
                target = ctx.message.mentions[0]; target_id = str(target.id)
                __bmode = 'DIRECT'
                # CE - Processing/lock
                CE['lock'] = target_id

            # PVE   |    USING MOB'S ID
            elif copo.startswith('mob.') or copo.startswith('boss'):
                # If there's no current_enemy   |   # If there is, and the target is the current_enemy
                # if CE:
                # if 'lock' in CE:
                if copo == 'boss':
                    try:
                        target = await self.client.quefe(f"SELECT mob_id FROM environ_mob WHERE branch='boss' AND region='{cur_PLACE}' AND {cur_X} > limit_Ax AND {cur_Y} > limit_Ay AND {cur_X} < limit_Bx AND {cur_Y} < limit_By;")
                        target = target[0]; __mode = 'PVE'; target_id = target
                    except TypeError: await ctx.send("<:osit:544356212846886924> There's no boss around your area..."); return
                    # CE - Processing/lock
                    try: CE['lock'] = target_id
                    except NameError: pass
                else:
                    target = copo; __mode = 'PVE'; target_id = target
                    # CE - Processing/lock
                    try: CE['lock'] = target_id
                    except NameError: pass
                # If there is, but the target IS NOT the current_enemy
                #elif copo != CE['lock']:
                #    await ctx.send(f"<:osit:544356212846886924> Please finish your current fight with the `{CE['lock']}`!"); return



            # PVP   |    USING USER'S ID
            else:
                try:
                    try:
                        target = await self.client.get_user(int(copo))
                        if not target: await ctx.send("<:osit:544356212846886924> User's not found"); return
                        target_id = target.id
                        # CE - Processing/lock
                        CE['lock'] = target_id
                    except (discordErrors.NotFound, discordErrors.HTTPException, TypeError): await ctx.send("<:osit:544356212846886924> Invalid user's id!"); return
                    __mode = 'PVP'
                    __bmode = 'INDIRECT'
                # MOVES     |      acabcbabbba
                except ValueError:
                    raw_move = copo

        # In case target is not given, current_enemy is used
        if not target:
            try:
                # Mobs first. If there's no mob in current_enemy, then randomly pick one
                if CE['lock'] == 'n/a':
                    target = random.choice(await self.client.quefe(f"SELECT mob_id FROM environ_mob WHERE region='{cur_PLACE}' AND {cur_X} > limit_Ax AND {cur_Y} > limit_Ay AND {cur_X} < limit_Bx AND {cur_Y} < limit_By;", type='all'))[0]
                    target_id = target
                    __mode = 'PVE'
                    # CE - Processing/lock
                    CE['lock'] = target_id
                # Lock - PLAYER             ||          Always DIRECT
                elif CE['lock'].isdigit():
                    try:
                        target = await self.client.get_user(int(CE['lock']))
                        # Target not found, then switch to random mob
                        if not target:
                            raise KeyError
                        target_id = target.id
                    # Target not found, then switch to random mob
                    except (discordErrors.NotFound, discordErrors.HTTPException, TypeError):
                        raise KeyError
                    __mode = 'PVP'
                # Lock - MOB
                else:
                    target = CE['lock']
                    target_id = target
                    __mode = 'PVE'
            # E: CE not init
            except (KeyError, TypeError):
                CE = {}
                target = random.choice(await self.client.quefe(f"SELECT mob_id FROM environ_mob WHERE region='{cur_PLACE}' AND {cur_X} > limit_Ax AND {cur_Y} > limit_Ay AND {cur_X} < limit_Bx AND {cur_Y} < limit_By;", type='all'))[0]
                target_id = target
                __mode = 'PVE'
                # CE - Processing/lock
                CE['lock'] = target_id

        # tCE - IN
        tCE, tCE_ttl = await self.tools.redio_map(f"CE{ctx.author.id}", mode='get', getttl=True)
        if not tCE:
            tCE = await self.CE_maker('')
            tCE_ttl = 0
        tCE['effect'] = self.CE_effect_encoder(tCE['effect'])


        # TARGET CHECK =========================================


        # Checking the length of moves
        moves_to_check = await self.client.quefe(f"SELECT value FROM pi_arts WHERE user_id='{str(ctx.message.author.id)}' AND art_type='ability' AND art_code='aa0';")
        if not raw_move: raw_move = random.choices(['b', 'q', 'a'], k=moves_to_check[0])
        if len(raw_move) > moves_to_check[0]:
            await ctx.send(f"<:osit:544356212846886924> Your current movement limit is `{len(raw_move)}`, **{ctx.message.author.name}**!"); return



        # PVP use target, with personal_info =============================

        if __mode == 'PVP':
            await self.PVP_melee(ctx.message, target, raw_move, bmode=__mode, CE=CE, CE_ttl=CE_ttl, tCE=tCE, tCE_ttl=tCE_ttl)
        elif __mode == 'PVE':
            await self.PVE_melee(ctx.message, target_id, raw_move, CE=CE, CE_ttl=CE_ttl)
        else: print("<<<<< Non PVP nor PVE >>>>>>>")

    @commands.command(aliases=['rng'])
    @commands.cooldown(1, 10, type=BucketType.user)
    async def range(self, ctx, *args):

        # >Aim <coord_X> <coord_Y> <shots(optional)>      |      >Aim <@user/mob_name> <shots(optional)>       |          >Aim (defaul - shot=1)
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        raw = list(args)
        # E: Moves not given
        if not raw: await ctx.send(f"<:osit:544356212846886924> **{ctx.author.name}**, please make your moves!"); return

        __mode = 'PVP'
        shots = 1
        target = ''


        # USER's info/weapon GET ==============================================

        # Get info     |      as well as checking coord
        try: user_id, INTT, cur_PLACE, cur_X, cur_Y, cur_MOB, main_weapon, combat_HANDLING, STA, LP, AFlame, AIce, ADark, AHoly = await self.client.quefe(f"SELECT id, INTT, cur_PLACE, cur_X, cur_Y, cur_MOB, IF(combat_HANDLING IN ('both', 'right'), right_hand, left_hand), combat_HANDLING, STA, LP, au_FLAME, au_ICE, au_DARK, au_HOLY FROM personal_info WHERE id='{str(ctx.message.author.id)}' AND cur_X>1 AND cur_Y>1;")
        # E: User in PB
        except TypeError: await ctx.send("<:osit:544356212846886924> You can't fight inside **Peace Belt**!"); return

        # Get weapon's info
        w_round, w_firing_rate, w_sta, w_rmin, w_rmax, w_accu_randomness, w_accu_range, w_stealth, w_aura, w_tags, w_dmg, w_speed, w_int = await self.client.quefe(f"SELECT round, firing_rate, sta, range_min, range_max, accuracy_randomness, accuracy_range, stealth, aura, tags, dmg, speed, intt FROM pi_inventory WHERE existence='GOOD' AND item_id='{main_weapon}';")
        w_tags = w_tags.split(' - ')
        if 'magic' in w_tags: _style = 'MAGIC'
        else: _style = 'PHYSIC'


        # INPUT Read ===================================================

        # CE - IN
        CE, CE_ttl = await self.tools.redio_map(f"CE{ctx.author.id}", mode='get', getttl=True)
        if not CE:
            CE = await self.CE_maker('')
            CE_ttl = 0
        CE['effect'] = self.CE_effect_encoder(CE['effect'])

        for copo in raw:

            # PVE | MOB get/mob_id
            if copo.startswith('mob.') or copo.startswith('boss'):
                # If there's no current_enemy   |   # If there is, and the target is the current_enemy
                if CE:
                    if CE['lock'] == 'n/a' or copo == CE['lock']:
                        if copo == 'boss': 
                            target = await self.client.quefe(f"SELECT mob_id FROM environ_mob WHERE branch='boss' AND region='{cur_PLACE}';")
                            target = target[0]; __mode = 'PVE'; target_id = target
                            # CE - Processing/lock
                            CE['lock'] = target_id
                        else:
                            target = copo; __mode = 'PVE'; target_id = target
                            # CE - Processing/lock
                            CE['lock'] = target_id

            # PVP | USER get/@mention
            elif copo.startswith('<@'):
                # Get user
                target = ctx.message.mentions[0]; target_id = str(target.id)
                __bmode = 'DIRECT'
                # CE - Processing/lock
                CE['lock'] = target_id
            
            # PVP | USER get/id   (str is digit AND len(str)>15)
            elif copo.isdigit() and len(copo) > 15:

                try:
                    target = await self.client.get_user(int(copo))
                    if not target: await ctx.send("<:osit:544356212846886924> User's not found"); return
                    target_id = target.id
                    # CE - Processing/lock
                    CE['lock'] = target_id
                except (discordErrors.NotFound, discordErrors.HTTPException, TypeError): await ctx.send("<:osit:544356212846886924> Invalid user's id!"); return
                __bmode = 'INDIRECT'

            # PVP | USER get/coords
            elif ':' in copo:
                XYpair = copo.split(':')

                # Verify the coords
                X = int(XYpair[0])/1000; Y = int(XYpair[1])/1000
                if X > 50 and Y > 50: await ctx.send("<:osit:544356212846886924> Please use 5-digit or lower coordinates!")  
                #if len(str(int(raw[0]))) >= 5 and len(raw[1]) >= 5:await ctx.send("<:osit:544356212846886924> Please use 5-digit or lower coordinates!")  


                # Get USER from COORD. If there are many users, randomly pick one.
                try:
                    target_id = random.choice(await self.client.quefe(f"SELECT id FROM personal_info WHERE cur_X={X} AND cur_Y={Y} AND cur_PLACE='{cur_PLACE}';", type='all'))
                    target_id = target_id[0]
                    target = await self.client.get_user(int(target_id))
                    __bmode = 'DIRECT'
                    if not ctx.message.server.get_member(target_id): __bmode = 'INDIRECT'
                    if not target: await ctx.send(f"There's noone at **x:`{X:.3f}` y:`{Y:.3f}`** in {cur_PLACE}!"); return
                # E: Query's empty, since noone's at the given coord
                except IndexError: await ctx.send(f"There's noone at **x:`{X:.3f}` y:`{Y:.3f}`** in {cur_PLACE}!"); return

                # CE - Processing/lock
                CE['lock'] = target_id

            # Shots GET
            elif copo.isdigit():
                shots = int(copo)

        """
        ### ALL ELEMENT GET     (target, coord, shots) 
        try:
            target = ''
            # @User, shots provided
            if raw[0].startswith('<@'):
                # Get user
                target = ctx.message.mentions[0]; target_id = str(target.id)
                __bmode = 'DIRECT'
                # Get shots (if available and possible)
                try: 
                    shots = int(raw[1])
                    if _style == 'MAGIC':
                        try: amount = int(raw[2])
                        except IndexError: amount = 1
                except IndexError: amount = 1
                except TypeError: amount = 1

            # Coord, shots provided     (if raw[0] is a mob_name, raise TypeError       |      if raw[0] provided as <shots>, but raw[1] is not provided, raise IndexError)
            elif len(str(int(raw[0]))) <= 5 and len(raw[1]) <= 5 and _style == 'PHYSIC':
                print("OKAI HERE")
                X = int(raw[0])/1000; Y = int(raw[1])/1000

                # Get USER from COORD. If there are many users, randomly pick one.
                try:
                    target_id = random.choice(await self.client.quefe(f"SELECT id FROM personal_info WHERE cur_X={X} AND cur_Y={Y} AND cur_PLACE='{cur_PLACE}';", type='all'))
                    target_id = target_id[0]
                    target = await self.client.get_user(int(target_id))
                    __bmode = 'DIRECT'
                    if not ctx.message.server.get_member(target_id): __bmode = 'INDIRECT'
                    if not target: await ctx.send(f"There's noone at **x:`{X:.3f}` y:`{Y:.3f}`** in {cur_PLACE}!"); return
                # E: Query's empty, since noone's at the given coord
                except IndexError: await ctx.send(f"There's noone at **x:`{X:.3f}` y:`{Y:.3f}`** in {cur_PLACE}!"); return
                
                # Get shots (if available and possible)
                try: 
                    shots = int(raw[2])
                except IndexError: pass
                except TypeError: pass

            # Shots AND amount given.     |      Or coords, shots (and amount) given                     --------> MAGIC
            elif _style == 'MAGIC':
                print('YO HERE')
                # Coords, shots (and amount)
                try:
                    X = int(raw[0])/1000; Y = int(raw[1])/1000; shots = int(raw[2])

                    # Get USER from COORD. If there are many users, randomly pick one.
                    try: 
                        target_id = random.choice(await self.client.quefe(f"SELECT id FROM personal_info WHERE cur_X={X} AND cur_Y={Y} AND cur_PLACE='{cur_PLACE}';", type='all'))
                        target_id = target_id[0]
                        target = await self.client.get_user(int(target_id))
                        __bmode = 'DIRECT'
                        if not ctx.message.server.get_member(target_id): __bmode = 'INDIRECT'
                        if not target: await ctx.send(f"There's noone at **x:`{X:.3f}` y:`{Y:.3f}`** in {cur_PLACE}!"); return
                    # E: Query's empty, since noone's at the given coord
                    except (IndexError, TypeError): await ctx.send(f"There's noone at **x:`{X:.3f}` y:`{Y:.3f}`** in {cur_PLACE}!"); return

                    try: amount = int(raw[3])
                    except (IndexError, TypeError): amount = 1
                # Shots AND amount
                except (IndexError, TypeError):
                    shots = int(raw[0]); amount = int(raw[1])
                    raise IndexError

        # Mob_id, shots provided
        except (TypeError, ValueError):
            print("HEREEE")
            # If there's no current_enemy   |   # If there is, and the target is the current_enemy
            if cur_MOB == 'n/a' or raw[0] == cur_MOB:
                target = raw[0]; target_id = target
                __mode = 'PVE'
                # Get shots (if available and possible)
                try: 
                    shots = int(raw[1])
                    # try MAGIC
                    try: amount = int(raw[2])
                    except IndexError: amount = 1
                except (IndexError, TypeError): amount = 1 
            # If there is, but the target IS NOT the current_enemy
            elif raw[0] != cur_MOB:
                await ctx.send(f"<:osit:544356212846886924> Please finish your current fight with `{cur_MOB}`!"); return
        """

        # Target not found
        if not target:
            # Mobs first. If there's no mob in current_enemy, then randomly pick one
            try:
                if CE['lock'] == 'n/a':
                    target = random.choice(await self.client.quefe(f"SELECT mob_id FROM environ_mob WHERE region='{cur_PLACE}' AND {cur_X} > limit_Ax AND {cur_Y} > limit_Ay AND {cur_X} < limit_Bx AND {cur_Y} < limit_By;", type='all'))[0]
                    target_id = target
                    __mode = 'PVE'
                    # CE - Processing/lock
                    CE['lock'] = target_id
                else:
                    target = CE['lock']
                    target_id = target
                    __mode = 'PVE'
            # E: CE not init
            except KeyError:
                target = random.choice(await self.client.quefe(f"SELECT mob_id FROM environ_mob WHERE region='{cur_PLACE}' AND {cur_X} > limit_Ax AND {cur_Y} > limit_Ay AND {cur_X} < limit_Bx AND {cur_Y} < limit_By;", type='all'))[0]
                target_id = target
                __mode = 'PVE'
                # CE - Processing/lock
                CE['lock'] = target_id


        # tCE - IN
        if __mode == 'PVP':
            tCE, tCE_ttl = await self.tools.redio_map(f"CE{ctx.author.id}", mode='get', getttl=True)
            if not CE:
                tCE = await self.CE_maker('')
                tCE_ttl = 0
            tCE['effect'] = self.CE_effect_encoder(tCE['effect'])

        # CHECK misc =======================================================
        if shots > w_firing_rate: await ctx.send(f"<:osit:544356212846886924> **{ctx.message.author.name}**, your weapon cannot perform `{shots}` shots in a row!"); return


        # TARGET's INFO ====================================================
        # (as well as init some variables)

        # Check if target has a ava
        if __mode == 'PVP': 
            # Check if target has a ava     |      GET TARGET's INFO
            try: t_cur_X, t_cur_Y, t_combat_HANDLING, t_right_hand, t_left_hand = await self.client.quefe(f"SELECT cur_X, cur_Y, combat_HANDLING, right_hand, left_hand FROM personal_info WHERE id='{target_id}' AND cur_PLACE='{cur_PLACE}';")
            # E: Invalid target, or target's not in the same region
            except TypeError:
                await ctx.send("<:osit:544356212846886924> Target don't have an ava, or you and the target are not in the same region!"); return

        elif __mode == 'PVE':
            # Check if target is a valid mob       |       GET TARGET's INFO
            try: t_Ax, t_Ay, t_Bx, t_By, t_name, t_AFlame, t_AIce, t_ADark, t_AHoly = await self.client.quefe(f"SELECT limit_Ax, limit_Ay, limit_Bx, limit_By, name, au_FLAME, au_ICE, au_DARK, au_HOLY FROM environ_MOB WHERE mob_id='{target_id}';")
            # E: Invalid target, or target's not in the same region
            except TypeError: await ctx.send(f"<:osit:544356212846886924> Unable to locate `{target_id}` in your surrounding, {ctx.author.mention}!"); return

        # DISTANCE get/check
        if __mode == 'PVP': 
            distance = await self.utils.distance_tools(cur_X, cur_Y, t_cur_X, t_cur_Y)
            if distance > w_rmax or distance < w_rmin: await ctx.send(f"<:osit:544356212846886924> **{ctx.message.author.name}**, the target is out of your weapon's range!"); return
        elif __mode == 'PVE':
            distance = 1                    # There is NO distance in a PVE battle, therefore the accuracy will always be at its lowest



        # AMMO's info GET ===========================================================
        try:
            a_name, a_tags, a_speed, a_rlquery, a_dmg, a_quantity, a_weight = await self.client.quefe(f"SELECT name, tags, speed, reload_query, dmg, quantity, weight FROM pi_inventory WHERE existence='GOOD' AND item_code='{w_round}' AND user_id='{user_id}';")
            a_tags = a_tags.split(' - ')
        # E: Ammu not found (OUT-OF-AMMO, am5, am6, etc.)
        except TypeError: 
            if w_round not in ['am5', 'am6'] :
                a_name = await self.client.quefe(f"SELECT name FROM model_item WHERE item_code='{w_round}';")
                await ctx.send(f"<:osit:544356212846886924> {ctx.message.author.mention}, OUT OF AMMO --> `{w_round} | {a_name}`"); return
            else:
                a_name, a_tags, a_speed, a_rlquery, a_dmg, a_weight = await self.client.quefe(f"SELECT name, tags, speed, reload_query, dmg, weight FROM model_item WHERE item_code='{w_round}';")



        # SHOTS pre-processed calc  ||  Reload ====================================================
        ################## MAGIC
        if w_round == 'am5':                    # LP -------------------- If kamikaze, halt them
            if LP <= shots*w_dmg:
                await ctx.send(f"<:osit:544356212846886924> **{ctx.message.author.name}**, please don't kill yourself..."); return
            else:
                a_rlquery = a_rlquery.replace('quantity_here', str(shots*w_dmg)).replace('user_id_here', user_id)
                await self.client._cursor.execute(a_rlquery)
        elif w_round == 'am6':                  # STA -------------------- If kamikaze, take the rest of the STA, split it into shots. Then decrease STA
            if STA <= shots*w_dmg:
                w_dmg = STA//shots
                a_rlquery = a_rlquery.replace('quantity_here', str(shots*w_dmg)).replace('user_id_here', user_id)
                await self.client._cursor.execute(a_rlquery)
            else:
                a_rlquery = a_rlquery.replace('quantity_here', str(shots*w_dmg)).replace('user_id_here', user_id)
                await self.client._cursor.execute(a_rlquery)            
        ################## PHYSIC
        else:
            if a_quantity <= shots:
                shots = a_quantity
                await self.client._cursor.execute(f"UPDATE pi_inventory SET existence='BAD' WHERE item_code='{w_round}' AND user_id='{user_id}';")
            else:
                a_rlquery = a_rlquery.replace('quantity_here', str(shots)).replace('user_id_here', user_id)
                await self.client._cursor.execute(a_rlquery)

        # STAMINA damaging for Physic W
        if _style == 'PHYSIC':
            if shots*w_sta < STA:
                if w_sta >= 100:
                    await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-20 WHERE id='{user_id}';")
                else: 
                    await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-10 WHERE id='{user_id}';")
            else:
                shots = STA//w_sta

        
        # SHOOTING =======================================================
        # RANDOMNESS | Take HANDLING into account, then re-calc
        if combat_HANDLING != 'both':
            w_accu_randomness = w_accu_randomness//2 + (INTT*4+w_int)//5
        if w_accu_randomness < 1: w_accu_randomness = 1 + (INTT*4+w_int)//5

        # CE - Processing
        # SHOTS are evaluated with probability and user's CE (PCM:Attack) (More attack -> Less accuracy)
        try:
            if CE: w_accu_randomness = w_accu_randomness - w_accu_randomness/20*float(CE['aggressive'])
        # E: Temporary CE ('lockon' only)
        except KeyError: pass

        numerator = random.choice(range(100+int(w_accu_randomness)))
        if distance > w_accu_range: denominator = 100*(distance/w_accu_range)
        else: denominator = 100*(distance/w_accu_range)
        # Check if numerator > denominator
        if numerator > denominator: shots = shots
        else: shots = int(shots/denominator*numerator)

        # tCE - Processing
        # SHOTS are evaluated with probability and user's CE (PCM:Attack) (More attack -> Less accuracy)
        try:
            if tCE and await self.utils.percenter(int(tCE['evasive']), total=100, anti=True):
                shots -= int(tCE['evasive'])
        # E: Temporary CE ('lockon' only)
        except (KeyError, UnboundLocalError): pass

        # Inform MISS (to user and target)
        if shots == 0: 
            await ctx.send(f":interrobang: **MISS...** again, {ctx.author.mention}?")

            if __bmode == 'INDIRECT' and __mode == 'PVP': await target.send(f":sos: **Someone** is trying to hurt you, {target.mention}!")
            return


        # PVP use target, with ava_dict =================================

        # PVE use target_id, with environ_mob ============================


        if __mode == 'PVP':
            await self.PVP_range(shots, ctx.message, _style, __mode, aDict={'a_dmg': a_dmg, 'a_weight': a_weight, 'w_aura': w_aura, 'w_speed': w_speed, 'w_stealth': w_stealth}, tDict={'target': target, 'target_id': target_id, 't_name': t_name, 't_combat_HANDLING': t_combat_HANDLING, 't_left_hand': t_left_hand, 't_right_hand': t_right_hand, 'au_FLAME': t_AFlame, 'au_ICE': t_AIce, 'au_DARK': t_ADark, 'au_HOLY': t_AHoly}, uDict={'au_FLAME': AFlame, 'au_ICE': AIce, 'au_DARK': ADark, 'au_HOLY': AHoly}, CE=CE, tCE=tCE)
        elif __mode == 'PVE':
            await self.PVE_range(shots, ctx.message, _style, aDict={'a_dmg': a_dmg, 'w_aura': w_aura}, tDict={'target_id': target_id, 't_name': t_name, 'au_FLAME': t_AFlame, 'au_ICE': t_AIce, 'au_DARK': t_ADark, 'au_HOLY': t_AHoly}, uDict={'au_FLAME': AFlame, 'au_ICE': AIce, 'au_DARK': ADark, 'au_HOLY': AHoly}, CE=CE)
        else: print("<<<<< OH SHIET >>>>>>>")

    @commands.command()
    @commands.cooldown(1, 3, type=BucketType.user)
    async def pose(self, ctx, *args):
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        raw = list(args)

        # CE - IN
        CE, CE_ttl = await self.tools.redio_map(f"CE{ctx.author.id}", mode='get', getttl=True)
        try: CE['effect'] = self.CE_effect_encoder(CE['effect'])
        except (TypeError, KeyError): pass

        # POSE ==========================================
        try:
            note = {'both': ['<:right_hand:521197677346553861><:left_hand:521197732162043922>', '**BOTH hand** · Attack rely on right-hand, defense rely on left-hand weapon'],
            'right': ['<:right_hand:521197677346553861>', '**RIGHT hand** · Defense and attack rely on right-hand weapon'], 
            'left': ['<:left_hand:521197732162043922>', '**LEFT hand** · Defense and attack rely on left-hand weapon']}

            await ctx.send(f'{note[raw[0]][0]} Changed to **{raw[0].upper()} hand** pose')
            await self.client._cursor.execute(f"UPDATE personal_info SET combat_HANDLING='{raw[0].lower()}' WHERE id='{ctx.author.id}';")
            return
        # E: Pose not given --> Show current pose and PCM
        except IndexError:
            vpcm = ''

            # Get pose
            curPose = await self.client.quefe(f"SELECT combat_HANDLING FROM personal_info WHERE id='{ctx.author.id}';")

            temb = discord.Embed(title=f"{note[curPose[0]][0]} {note[curPose[0]][1]}", color=0x36393F)

            # PCM
            if CE:
                # if 'raw_pcm' in CE:
                # Visualize raw_PCM
                for m in CE['raw_pcm']:
                    vpcm += self.pcmIcon_dict[m]

                # Effect display
                effect_line = ''
                try:
                    for e_pack in CE['effect']:
                        effect_line += self.effect_icon[e_pack[0]]
                except KeyError: pass
                
                temb.add_field(name=f"╟ `Time` · {CE_ttl}", value=f"\n╟ `Lockon` · **{CE['lock']}**\n╟ `Ultimate` · **{CE['ultimate']}%**\n> {effect_line}⠀")
                temb.add_field(name=f">>> {vpcm}⠀", value=f"╟ `Aggressive` · **{float(CE['aggressive']):.2f}**\n╟ `Defensive` · **{float(CE['defensive']):.2f}**\n╟ `Evasive` · **{float(CE['evasive']):.2f}**")

            await ctx.send(embed=temb, delete_after=10)
            return
        # E: PCM given, not pose
        except KeyError: pass

        # Passive Combat Movement (PCM) =================
        # If no CE
        if not CE:
            pcmLimit = await self.client.quefe(f"SELECT value FROM pi_arts WHERE user_id='{ctx.author.id}' AND art_type='ability' AND art_code='aa1';")
            if len(args[0]) > pcmLimit[0]: await ctx.send(f"<:osit:544356212846886924> Your current PCM (PassiveCombatMovement) limit is `{pcmLimit[0]}`, **{ctx.author.name}**!"); return

            CE = await self.CE_maker(args[0])
            if not CE: await ctx.send("<:osit:544356212846886924> Invalid PCM (PassiveCombatMovement)!"); return

            # CE - OUT
            try:
                CE['effect'] = self.CE_effect_encoder(CE['effect'], mode='encode')          # Encode back to string
                await self.tools.redio_map(f"CE{ctx.author.id}", dict=CE, ttl=20)
            except redisErrors.DataError: return
            await ctx.invoke(self.pose)

        # If CE
        else: await ctx.send(f"<:osit:544356212846886924> PCM will expire after :stopwatch:**`{CE_ttl}s`**", delete_after=5); return



# ================== TOOLs ==================
    # CE [effect_tag, value, percentage, strikes_to_live, time_to_live_addition]

    async def PVE_melee(self, MSG, target_id, raw_move, CE=None, CE_ttl=0):

        # GET User info=======================
        name, evo, STR, STA, user_id, cur_PLACE, cur_X, cur_Y, charm, combat_HANDLING, right_hand, left_hand = await self.client.quefe(f"SELECT name, evo, STR, STA, id, cur_PLACE, cur_X, cur_Y, charm, combat_HANDLING, right_hand, left_hand FROM personal_info WHERE id='{MSG.author.id}';")

        # GET user's weapon
        if combat_HANDLING == 'both':
            w_defend, w_speed, wd_weight = await self.client.quefe(f"SELECT defend, speed, weight FROM pi_inventory WHERE existence='GOOD' AND (item_id='{left_hand}' OR item_code='{left_hand}') AND user_id='{user_id}'")
            w_str, w_multiplier, w_weight, w_sta = await self.client.quefe(f"SELECT str, multiplier, weight, sta FROM pi_inventory WHERE existence='GOOD' AND (item_id='{right_hand}' OR item_code='{right_hand}') AND user_id='{user_id}'")
            w_sta += wd_weight/100
        elif combat_HANDLING == 'right':
            w_str, w_defend, w_speed, w_multiplier, w_weight, w_sta = await self.client.quefe(f"SELECT str, defend, speed, multiplier, weight, sta FROM pi_inventory WHERE existence='GOOD' AND (item_id='{right_hand}' OR item_code='{right_hand}') AND user_id='{user_id}'")
            w_speed *= 1.2
            w_multiplier += 1
            w_defend *= 2
        elif combat_HANDLING == 'left':
            w_str, w_defend, w_speed, w_multiplier, w_weight, w_sta = await self.client.quefe(f"SELECT str, defend, speed, multiplier, weight, sta FROM pi_inventory WHERE existence='GOOD' AND (item_id='{left_hand}' OR item_code='{left_hand}') AND user_id='{user_id}'")
            w_speed *= 1.2
            w_multiplier += 1
            w_defend *= 2


        # GET Mob info =======================
        try:
            t_name, t_speed, t_str, t_chain, t_lp, t_illulink, t_effect, t_lockon_max, t_defpy, t_branch = await self.client.quefe(f"SELECT name, speed, str, chain, LP, illulink, effect, lockon_max, defense_physic, branch FROM environ_mob WHERE mob_id='{target_id}' AND region='{cur_PLACE}' AND {cur_X} > limit_Ax AND {cur_Y} > limit_Ay AND {cur_X} < limit_Bx AND {cur_Y} < limit_By;")
        # If mob not found (either mistyping or outdated lock), set lock to 'n/a'
        except TypeError:
            try:
                target_id = random.choice(await self.client.quefe(f"SELECT mob_id FROM environ_mob WHERE region='{cur_PLACE}' AND {cur_X} > limit_Ax AND {cur_Y} > limit_Ay AND {cur_X} < limit_Bx AND {cur_Y} < limit_By;", type='all'))
                target_id = target_id[0]
                t_name, t_speed, t_str, t_chain, t_lp, t_illulink, t_effect, t_defpy, t_branch = await self.client.quefe(f"SELECT name, speed, str, chain, LP, illulink, effect, defense_physic, branch FROM environ_mob WHERE mob_id='{target_id}' AND region='{cur_PLACE}' AND {cur_X} > limit_Ax AND {cur_Y} > limit_Ay AND {cur_X} < limit_Bx AND {cur_Y} < limit_By;")
                CE['lock'] = target_id
            except IndexError:
                await MSG.channel.send(f"<:osit:544356212846886924> Unable to locate `{target_id}` in your surrounding, {MSG.author.mention}!"); return


        # Delete user's attack msg
        try: await MSG.delete()
        except discordErrors.Forbidden: pass


        def turn_decrease(effect):
            effect[3] = str(int(effect[3]) - 1)
            return effect


        async def conclusing(dmg):
            # REFRESHING ===========================================
            LP, STA = await self.client.quefe(f"SELECT LP, STA FROM personal_info WHERE id='{MSG.author.id}';")

            if not await self.tools.ava_scan(MSG, type='life_check'):
                # If query effect zero row
                if await self.client._cursor.execute(f"UPDATE pi_mobs_collection SET {t_branch}={t_branch}-1 WHERE user_id='{t_branch}' AND region='{cur_PLACE}';") == 0:
                    await self.client._cursor.execute(f"INSERT INTO pi_mobs_collection (user_id, region, {t_branch}) VALUES ('{user_id}', '{cur_PLACE}', -1);")
                return False
            if t_lp <= 0:
                await MSG.channel.send(f"<:tumbstone:544353849264177172> **{t_name}** is dead.")
                
                # Add one to the collection
                type = await vanishing()

                # If query effect zero row
                if await self.client._cursor.execute(f"UPDATE pi_mobs_collection SET {type}={type}+1 WHERE user_id='{user_id}' AND region='{cur_PLACE}';") == 0:
                    await self.client._cursor.execute(f"INSERT INTO pi_mobs_collection (user_id, region, {type}) VALUES ('{user_id}', '{cur_PLACE}', 1);")

                # Erase the current_enemy lock on off the target_id

                await self.client._cursor.execute(f"UPDATE personal_info SET cur_MOB='n/a' WHERE id='{user_id}';")
                return False

            # Effect display
            effect_line = ''
            try:
                for e_pack in CE['effect']:
                    effect_line += self.effect_icon[e_pack[0]]
                if effect_line: effect_line = "〖" + effect_line + "〗"
            except KeyError: pass

            msg = f"╔═══════════\n╟:heartpulse:`{LP}` :muscle:`{STA}`⠀⠀|〖**{MSG.author.mention}**〗{effect_line}\n╟:heartpulse:`{t_lp-dmg:.0f}`⠀⠀⠀⠀⠀⠀⠀⠀|〖**{t_name}**〗\n╚═══════════"
            return msg

        async def vanishing():
            # Looting
            mob_code, rewards, reward_query, region, t_Ax, t_Ay, t_Bx, t_By = await self.client.quefe(f"SELECT mob_code, rewards, reward_query, region, limit_Ax, limit_Ay, limit_Bx, limit_By FROM environ_mob WHERE mob_id='{target_id}';")
            try:
                mems = await self.client.quefe(f"SELECT user_id FROM pi_party WHERE party_id=(SELECT party_id FROM pi_party WHERE user_id='{MSG.author.id}');", type='all')
                if len(mems) > 1:
                    for mem in mems:
                        if mem[0] != str(ctx.author.id): reward_query_party = reward_query.replace('perks=perks+', f'perks=perks+(1/ABS(evo-{evo})+1)*').replace('merit=merit+', f'merit=merit+(1/ABS(evo-{evo})+1)*')
                        else: reward_query_party = reward_query
                        await self.client._cursor.execute(reward_query_party.replace('user_id_here', mem[0]))
                    await MSG.channel.send(f"<:chest:507096413411213312> Congrats **{MSG.author.mention}**, you and {len(mems) - 1} other party members received **{rewards.replace(' | ', '** and **')}** from **「`{target_id}` | {t_name}」**!")
                else:
                    await self.client._cursor.execute(reward_query.replace('user_id_here', str(MSG.author.id)))
                    await MSG.channel.send(f"<:chest:507096413411213312> Congrats **{MSG.author.mention}**, you've received **{rewards.replace(' | ', '** and **')}** from **「`{target_id}` | {t_name}」**!")
            except:
                await self.client._cursor.execute(reward_query.replace('user_id_here', str(MSG.author.id)))
                await MSG.channel.send(f"<:chest:507096413411213312> Congrats **{MSG.author.mention}**, you've received **{rewards.replace(' | ', '** and **')}** from **「`{target_id}` | {t_name}」**!")

            

            # ==================================
            # Get the <mob> prototype
            name, branch, lp, strr, chain, speed, attack_type, defense_physic, defense_magic, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY, skills, effect, t_evo, description, lockon_max, illulink = await self.client.quefe(f"SELECT name, branch, lp, str, chain, speed, attack_type, defense_physic, defense_magic, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY, skills, effect, evo, description, lockon_max, illulink FROM model_mob WHERE mob_code='{mob_code}';")
            rewards = rewards.split(' | ')

            # Generating rewards
            status = []; objecto = []; bingo_list = []
            for reward in rewards:
                stuff = reward.split(' - ')
                # Gacha
                if await self.utils.percenter(int(stuff[2])):

                    # Stats reward
                    if stuff[0] in ['money', 'perks']:
                        if stuff[0] == 'money': bingo_list.append(f"<:36pxGold:548661444133126185>{stuff[1]}")
                        elif stuff[0] == 'perks': bingo_list.append(f"<:perk:632340885996044298>{stuff[1]}")

                        status.append(f"{stuff[0]}={stuff[0]}+{int(stuff[1])}")
                    # ... other shit
                    else: 
                        # Get item/weapon's info
                        objecto.append(f"""SELECT func_it_reward("user_id_here", "{stuff[0]}", {stuff[1]}); SELECT func_ig_reward("user_id_here", "{stuff[0]}", {stuff[1]});""")
                        bingo_list.append(f"item `{stuff[0]}`")

            # Merit calc
            merrire = t_evo - evo + 1
            if merrire < 0: merrire = 0
            else:
                if target_id.startswith('boss'): merrire = int(merrire/2*10)
            stata = f"""UPDATE personal_info SET {', '.join(status)}, merit=merit+{merrire} WHERE id="user_id_here"; """
            rewards_query = f"{stata} {' '.join(objecto)}"

            # Remove the old mob from DB
            await self.client._cursor.execute(f"DELETE FROM environ_mob WHERE mob_id='{target_id}';")

            # Insert the mob to DB
            await self.client._cursor.execute(f"""INSERT INTO environ_mob VALUES (0, 'mob', '{mob_code}', "{name}", "{description}", '{branch}', {lp}, {strr}, {chain}, {speed}, '{attack_type}', {defense_physic}, {defense_magic}, {au_FLAME}, {au_ICE}, {au_HOLY}, {au_DARK}, '{skills}', '{effect}', '{' | '.join(bingo_list)}', '{rewards_query}', '{region}', {t_Ax}, {t_Ay}, {t_Bx}, {t_By}, '{lockon_max}', "{illulink}", '');""")
            counter_get = await self.client.quefe("SELECT MAX(id_counter) FROM environ_mob")
            await self.client._cursor.execute(f"UPDATE environ_mob SET mob_id='mob.{counter_get[0]}' WHERE id_counter={counter_get[0]};")

            return branch

        async def dmg_calc(raw_move, ttl_plus=0):
            bonus = []
            icon_sequence = ''

            # Event: EVADE/mob
            try: evas = float(CE['evasive'])
            except KeyError: evas = 0
            if await self.utils.percenter(t_speed, total=int(100 + evas)):
                bonus.append('evade')
                return 0, 0, 0, bonus, icon_sequence, int(ttl_plus)

            # Invoke the moves
            count = 0
            m_burst = 0
            m_quick = 0
            m_art = 0
            for c in raw_move:
                if c == 'b':
                    ttl_plus += 1.8
                    m_burst += 1.25 + count
                elif c == 'q':
                    ttl_plus += 0.2
                    m_burst += 0.25 + count
                    m_quick += 1 + count
                elif c == 'a':
                    ttl_plus += 2.5
                    m_burst += 0.75 + count
                    m_art += 2*count*5
                else: await MSG.channel.send("<:osit:544356212846886924> Invalid move!")
                icon_sequence += self.moveIcon_dict[c]
                count += 0.2

            # Damage Calc
            diff_var = 1 - 0.04*abs(STR-w_str)
            if diff_var < 0: diff_var = 0.001
            dmg = round(((STR*2+w_str)/3)*w_multiplier*m_burst*diff_var)
            dmg_q = round(((STR+w_str*2)/3)*w_multiplier*m_quick*diff_var*(w_weight/100))
            # Damage Calc 2 (Nerf)
            counter_def = t_defpy - dmg_q
            if counter_def > 0: dmg -= counter_def      # Even if (dmg_q > t_defpy), do not stack dmg_q with dmg (dmg is FORBIDEN to increase).
            if dmg < 0: CE['effect'].append('stun')     # If dmg cannot surpass t_defpy, receives STUN effect.
            # Crit
            try:
                if not random.choice(range(int(w_weight/10))): dmg = dmg + dmg/10*w_weight
            except IndexError: pass

            # CE - Processing
            try:
                # Event: Burst
                dmg += int(dmg/100*float(CE['aggressive']))
            except (TypeError, KeyError): pass

            # USER's Effect Processing
            for effect in CE['effect']:
                # STUN
                if effect[0] == 'stun':
                    dmg = 0
                    dmg_q = 0
                    m_art = 0
                    icon_sequence = ''
                    return dmg, dmg_q, m_art, bonus, icon_sequence, int(ttl_plus)
                # PARALYSIS
                elif effect[0] == 'paralysis':
                    dmg = 0
                    dmg_q = 0
                    m_art = 0
                    icon_sequence = ''
                    ttl_plus = int(ttl_plus) + int(effect[4])
                    return dmg, dmg_q, m_art, bonus, icon_sequence, ttl_plus
                # BLEED
                elif effect[0] == 'bleed':
                    effect[2] = int(effect[2])*m_burst
                    ttl_plus = int(ttl_plus) + int(effect[4])
                    return dmg, dmg_q, m_art, bonus, icon_sequence, ttl_plus
                # SLEEP
                elif effect[0] == 'sleep':
                    dmg = 0
                    dmg_q = 0
                    m_art = 0
                    icon_sequence = ''
                    ttl_plus = int(ttl_plus) + int(effect[4])
                    CE['ultimate'] = 0
                    return dmg, dmg_q, m_art, bonus, icon_sequence, ttl_plus


            return dmg, dmg_q, m_art, bonus, icon_sequence, int(ttl_plus)

        async def t_dmg_calc(t_move, w_defend):
            bonus = []
            icon_sequence = ''

            # Invoke the moves
            count = 0
            m_burst = 0
            m_quick = 0
            for c in t_move:
                if c == 'b': m_burst += 1.25 + count
                elif c == 'q':
                    m_burst += 0.75 + count
                    m_quick += 0.25 + count
                elif c == 'a': m_burst += 1
                icon_sequence += self.moveIcon_dict[c]
                count += 0.2

            # Damage Calc
            t_dmg = round(t_str*m_burst)
            try: t_dmg_q = round(t_str*m_quick/w_speed)
            except ZeroDivisionError: t_dmg_q = round(t_str*m_quick)

            # CE - Processing
            try:
                # Event: EVADE/player
                if await self.utils.percenter(float(CE['evasive'] - t_speed), total=100):
                    t_dmg = 0
                    CE['ultimate'] += 15
                    bonus.append('evade')
                # Event: DEFEND/player
                w_defend += int(w_defend/100*float(CE['defensive']))
            except (TypeError, KeyError): pass

            # USER's Effect Processing
            for effect in CE['effect']:
                # BLEED
                if effect[0] == 'bleed':
                    m_burst += int(effect[2])
                    return t_dmg, t_dmg_q, bonus, icon_sequence
                # POISON
                elif effect[0] == 'poison':
                    m_burst += int(effect[2])
                    m_quick = int(effect[2])*m_quick
                    return t_dmg, t_dmg_q, bonus, icon_sequence

            # Take DEF/user into account
            t_dmg = round(t_dmg / 200 * (200 - w_defend))
            t_dmg_q = round(t_dmg_q / 200 * (w_defend))
            if t_dmg < 1: t_dmg = 1

            return t_dmg, t_dmg_q, bonus, icon_sequence

        async def battle():
            # ------- USER's EFFECT
            # Turn adjusting (Decrease/End)
            CE['effect'] = [turn_decrease(effect) for effect in CE['effect'] if effect[3] != '0']

            # Effect add
            if t_effect:
                t_effects = self.CE_effect_encoder(t_effect)

                for e_pack in t_effects:
                    if await self.utils.percenter(int(e_pack[2]), total=100, anti_limit=90):
                        try: CE['effect'].append(e_pack)
                        except KeyError: CE['effect'] = [e_pack]


            # ------------ USER PHASE   |   User deal DMG
            # STA filter
            if len(raw_move)*w_sta <= STA:
                if w_sta >= 100: await self.client._cursor.execute(f"UPDATE personal_info SET STA=STA-2 WHERE id='{MSG.author.id}';")
                else: await self.client._cursor.execute(f"UPDATE personal_info SET STA=STA-1 WHERE id='{MSG.author.id}';")
            else: await MSG.channel.send(f"<:osit:544356212846886924> {MSG.author.mention}, your STA is not enough for a `{len(raw_move)}`-chain melee move!"); return

            # Calc dmg
            ttl_plus = 10
            dmg, dmg_q, m_art, bonus, icon_sequence, ttl_plus = await dmg_calc(raw_move, ttl_plus=ttl_plus)

            # Take effect
            await self.client._cursor.execute(f"UPDATE environ_mob SET lp=lp-{dmg} WHERE mob_id='{target_id}'; ")
            try: CE['ultimate'] = float(CE['ultimate']) + m_art
            except (TypeError, KeyError): pass

            # Inform
            uEmbed = discord.Embed(color=0xCDEE6E)
            uEmbed.add_field(name=f":dagger: **{name}**  ⋙**[{dmg}]**⋙**「`{target_id}` | {t_name}」**", value=f":dagger: {icon_sequence}")
            await MSG.channel.send(embed=uEmbed, delete_after=20)



            # ------------ MOB PHASE    |   Mob deal DMG
            
            # LOCK - OUT (Target's lock)
            t_lock = await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.get, f'lock{target_id}'))
            try:
                # De-serialize
                t_lock = t_lock.decode('utf-8')[4:].split('|')

                # If user_id is in lock, continue
                if str(user_id) in t_lock:
                    pass
                # If not, try checking if lock is FULL
                else:
                    # FULL --> Return
                    if len(t_lock) >= int(t_lockon_max):
                        # CE - OUT
                        CE['effect'] = self.CE_effect_encoder(CE['effect'], mode='encode')          # Encode back to string
                        await self.tools.redio_map(f"CE{MSG.author.id}", dict=CE, ttl=CE_ttl+ttl_plus)
                        return
                    # NOT FULL --> Take a slot
                    else:
                        t_lock.append(str(user_id))

                        # Serialize
                        t_lock = 'lock' + '|'.join(t_lock)
                        
                        # LOCK - IN
                        await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.set, f'lock{target_id}', f'lock{MSG.author.id}', ex=charm))
            # If lock doesn't exist, make one
            except (TypeError, AttributeError):
                await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.set, f'lock{target_id}', f'lock{MSG.author.id}', ex=charm))


            # Generate moves ---> Calc dmg
            t_raw_move = random.choices(['b', 'q', 'a'], k=random.choice(range(t_chain)))
            t_dmg, t_dmg_q, bonus, t_icon_sequence = await t_dmg_calc(t_raw_move, w_defend)

            # Take effect
            await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-{t_dmg}, STA=STA-{t_dmg_q} WHERE id='{user_id}';")

            # Inform
            if 'evade' in bonus:
                tEmbed = discord.Embed(color=0xF15C4A)
                tEmbed.add_field(name=f"\n<:evading:615285957889097738> **{MSG.author.mention}** evaded!", value=f"⠀")
                if t_illulink: tEmbed.set_thumbnail(url=t_illulink)
            else:
                #pack_1 = f"\n:dagger: **「`{target_id}` | {t_name}」** ⋙ *{t_dmg}* ⋙ **{MSG.author.mention}**"
                tEmbed = discord.Embed(color=0xF15C4A)
                tEmbed.add_field(name=f":dagger: **「`{target_id}` | {t_name}」**  ⋙**[{t_dmg}]**⋙**{MSG.author.name}**", value=f":dagger: {t_icon_sequence}")
                if t_illulink: tEmbed.set_thumbnail(url=t_illulink)

            
            # Conclusing
            pack_2 = await conclusing(dmg)
            # Inform
            if pack_2: await MSG.channel.send(f"{pack_2}", embed=tEmbed, delete_after=20)
            else: return False

            # CE - OUT
            CE['effect'] = self.CE_effect_encoder(CE['effect'], mode='encode')          # Encode back to string
            await self.tools.redio_map(f"CE{MSG.author.id}", dict=CE, ttl=CE_ttl+ttl_plus)

        await battle()


    async def PVP_melee(self, MSG, target, raw_move, bmode='DIRECT', CE=None, tCE=None, CE_ttl=0, tCE_ttl=0):
        # GET User's info ============================
        name,  LP, STR, cur_PLACE, cur_X, cur_Y, combat_HANDLING, right_hand, left_hand, main_weapon = await self.client.quefe(f"SELECT name,  LP, STR, cur_PLACE, cur_X, cur_Y, combat_HANDLING, right_hand, left_hand, IF(combat_HANDLING IN ('both', 'right'), right_hand, left_hand) FROM personal_info WHERE id='{MSG.author.id}';")
        # Get user's weapon
        try: w_multiplier, w_speed, w_weight = await self.client.quefe(f"SELECT multiplier, speed, weight FROM pi_inventory WHERE existence='GOOD' AND item_id='{main_weapon}';")
        # E: main_weapon is a item_code (e.g. ar13)
        except TypeError: w_multiplier, w_sta, w_speed, w_weight = await self.client.quefe(f"SELECT multiplier, sta, speed, weight FROM pi_inventory WHERE existence='GOOD' AND item_code='{main_weapon}' and user_id='{MSG.author.id}';")
        # GET user's weapon
        if combat_HANDLING == 'both':
            w_defend, w_speed, wd_weight = await self.client.quefe(f"SELECT defend, speed, weight FROM pi_inventory WHERE existence='GOOD' AND (item_id='{left_hand}' OR item_code='{left_hand}') AND user_id='{MSG.author.id}'")
            w_str, w_multiplier, w_weight, w_sta = await self.client.quefe(f"SELECT str, multiplier, weight, sta FROM pi_inventory WHERE existence='GOOD' AND (item_id='{right_hand}' OR item_code='{right_hand}') AND user_id='{MSG.author.id}'")
            w_sta += wd_weight/100
        elif combat_HANDLING == 'right':
            w_str, w_defend, w_speed, w_multiplier, w_weight, w_sta = await self.client.quefe(f"SELECT str, defend, speed, multiplier, weight, sta FROM pi_inventory WHERE existence='GOOD' AND (item_id='{right_hand}' OR item_code='{right_hand}') AND user_id='{MSG.author.id}'")
            w_speed *= 1.2
            w_multiplier += 1
            w_defend *= 2
        elif combat_HANDLING == 'left':
            w_str, w_defend, w_speed, w_multiplier, w_weight, w_sta = await self.client.quefe(f"SELECT str, defend, speed, multiplier, weight, sta FROM pi_inventory WHERE existence='GOOD' AND (item_id='{left_hand}' OR item_code='{left_hand}') AND user_id='{MSG.author.id}'")
            w_speed *= 1.2
            w_multiplier += 1
            w_defend *= 2


        radial = 20             # Take attacker as the middle
        # GET Target's info ============================
        try: t_name, t_right_hand, t_left_hand, t_combat_HANDLING = await self.client.quefe(f"SELECT name, right_hand, left_hand, combat_HANDLING FROM personal_info WHERE id='{target.id}' AND cur_PLACE='{cur_PLACE}' AND cur_X-{radial}<={cur_X} AND {cur_X}<=cur_X+{radial} AND cur_Y-{radial}<={cur_Y} AND {cur_Y}<=cur_Y+{radial};")
        except TypeError: await MSG.channel.send(f"<:osit:544356212846886924> Target's unseen within 20m radius, {MSG.author.mention}!"); return
        # Get target's weapon
        if t_combat_HANDLING == 'both':
            tw_defend, tw_speed = await self.client.quefe(f"SELECT defend, speed FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_left_hand}' AND user_id='{target.id}'")
            tw_multiplier = await self.client.quefe(f"SELECT multiplier FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_right_hand}' AND user_id='{target.id}'"); tw_multiplier = tw_multiplier[0]
        elif t_combat_HANDLING == 'right':
            tw_defend, tw_multiplier, tw_speed = await self.client.quefe(f"SELECT defend, multiplier, speed FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_right_hand}' AND user_id='{target.id}'")
            tw_defend *= 2
        elif t_combat_HANDLING == 'left':
            tw_defend, tw_multiplier, tw_speed = await self.client.quefe(f"SELECT defend, multiplier, speed FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_left_hand}' AND user_id='{target.id}'")
            tw_defend *= 2


        async def dmg_calc(raw_move, pack, ttl_plus=0):
            bonus = []
            icon_sequence = ''
            tw_defend, w_speed = pack

            # tCE - Processing
            try:
                if tCE:
                    tw_defend += tw_defend*float(tCE['defensive'])
                    w_speed -= float(tCE['evasive'])
            # E: Temporary tCE
            except KeyError: pass

            # CE - Processing
            try:
                if CE:
                    w_speed *= float(CE['evasive'])
            # E: Temporary CE
            except KeyError: pass

            # Event: EVADE/mob
            try: evas = float(CE['evasive'])
            except KeyError: evas = 0
            if await self.utils.percenter(tw_speed, total=int(100 + evas)):
                bonus.append('evade')
                return 0, 0, 0, bonus, icon_sequence, ''

            # Invoke the moves
            count = 0
            m_burst = 0
            m_quick = 0
            m_art = 0
            for c in raw_move:
                if c == 'b':
                    ttl_plus += 1.8
                    m_burst += 1.25 + count
                elif c == 'q':
                    ttl_plus += 0.2
                    m_burst += 0.25 + count
                    m_quick += 1 + count
                elif c == 'a':
                    ttl_plus += 2.5
                    m_burst += 0.75 + count
                    m_art += 2*count*5
                icon_sequence += self.moveIcon_dict[c]
                count += 0.2

            # Damage Calc
            if combat_HANDLING == 'both':
                dmg = round(((STR*2+w_str)/3)*w_multiplier*m_burst)
                dmg_q = round(((STR*2+w_str)/3)*w_multiplier*m_quick*(w_weight/100))
            elif combat_HANDLING in ['right', 'left']:
                dmg = round(((STR*2+w_str)/3)*w_multiplier*m_burst)*2
                dmg_q = round(((STR*2+w_str)/3)*w_multiplier*m_quick*(w_weight/100))*2
  
            # Get Damage reduction (tw_defend indirectional proportion with tw_defend_q)
            tw_defend_q = tw_defend
            tw_defend = 200 - tw_defend
            temp_query = ''
            # If victim's defend (tw_defend) exceed 200, the attacker's STA takes dmg
            if tw_defend < 0:
                temp_query += f"UPDATE personal_info SET STA=STA-{round(dmg / 200 * abs(tw_defend))*tw_multiplier} WHERE id='{MSG.author.id}'; "
                tw_defend = 0

            # Get dmgdeal (don't combine, for informing :>)
            dmg = round(dmg / 200 * tw_defend)
            dmg_q = round(dmg_q / 200 * tw_defend_q)

            # Crit
            try:
                if not random.choice(range(int(w_weight/10))): dmg = dmg + dmg/10*w_weight
            except IndexError: pass

            # Combat Environment
            try:
                # Event: Burst
                dmg += int(dmg/100*float(CE['aggressive']))
            except (TypeError, KeyError): pass

            return dmg, dmg_q, m_art, bonus, icon_sequence, temp_query, int(ttl_plus)



        # DMG Calc ==============================
        ttl_plus = 10
        dmg, dmg_q, m_art, bonus, icon_sequence, temp_query, ttl_plus = await dmg_calc(raw_move, (tw_defend, w_speed), ttl_plus=ttl_plus)
        temp_query += f"UPDATE personal_info SET LP=LP-{dmg}, STA=STA-{dmg_q} WHERE id='{target.id}'; "

        # Take effect
        await self.client._cursor.execute(temp_query)
        try: CE['ultimate'] = float(CE['ultimate']) + m_art
        except (TypeError, KeyError): pass

        # Inform
        uEmbed = discord.Embed(color=0xCDEE6E)
        uEmbed.add_field(name=f":dagger: **{name}**  ⋙**[{dmg}]**⋙**「`{target.id}` | {t_name}」**", value=f":dagger: {icon_sequence}")
        await MSG.channel.send(embed=uEmbed, delete_after=20)
        # If INDIRECT, DM the target
        if bmode == 'INDIRECT': await target.send(embed=uEmbed)

        # CE - OUT
        CE['effect'] = self.CE_effect_encoder(CE['effect'], mode='encode')          # Encode back to string
        await self.tools.redio_map(f"CE{MSG.author.id}", dict=CE, ttl=30)

        # tCE - OUT
        tCE['effect'] = self.CE_effect_encoder(tCE['effect'], mode='encode')          # Encode back to string
        await self.tools.redio_map(f"CE{target.id}", dict=tCE, ttl=tCE_ttl+ttl_plus)

        await self.tools.ava_scan(MSG, 'life_check')


    async def PVE_range(self, shots, MSG, style, aDict={}, tDict={}, uDict={}, CE=None):

        """"a_dmg:          Ammo's damage
            target_id:      Mob's id
            t_name:         Mob's name
            w_aura:         Weapon's aura"""

        my_dmgdeal = round(aDict['a_dmg']*shots)

        if style == 'PHYSIC':

            await self.client._cursor.execute(f"UPDATE environ_mob SET lp=lp-{my_dmgdeal} WHERE mob_id='{tDict['target_id']}'; ")

            # Inform, of course :>
            await MSG.channel.send(f"<:gunshot:616136094739726347> **{MSG.author.name}** ⋙ *{my_dmgdeal}* ⋙ **「`{tDict['target_id']}` | {tDict['t_name']}」**!")
    
        elif style == 'MAGIC':

            # AURA comes in
            aura_dict = {'FLAME': 'au_FLAME', 'ICE': 'au_ICE', 'DARK': 'au_DARK', 'HOLY': 'au_HOLY'}        # Normal
            aura_redict = {'FLAME': 'au_ICE', 'ICE': 'au_HOLY', 'DARK': 'au_FLAME', 'HOLY': 'au_DARK'}      # Reversed
            # DMG is directional->UAura, is indirectional->reverseTAura     ||      DMG is then decreased by its oppo's parallel aura
            try: dmgdeal = int(my_dmgdeal*uDict[aura_dict[aDict['w_aura']]]/tDict[aura_redict[aDict['w_aura']]])
            except ZeroDivisionError: dmgdeal = int(my_dmgdeal*tDict[aura_dict[aDict['w_aura']]])

            await self.client._cursor.execute(f"UPDATE environ_mob SET lp=lp-{dmgdeal} WHERE mob_id='{tDict['target_id']}'; ")

            # Inform, of course :>
            await MSG.channel.send(f"<:gunshot:616136094739726347> **{MSG.author.name}** ⋙ *{dmgdeal}* ⋙ **「`{tDict['target_id']}` | {tDict['t_name']}」**!")


    async def PVP_range(self, shots, MSG, style, distance, aDict={}, tDict={}, uDict={}, bmode='DIRECT', CE=None, tCE=None):
        """w_speed, w_aura, a_dmg, a_weight
            target, t_name, target_id, t_combat_handling, t_left_hand, t_right_hand"""

        _style = style
        __bmode = bmode

        # Depend on the distance, make the shooter anonymous
        if distance <= 1000: shooter = MSG.author.name
        else: shooter = 'Someone'

        # Check if the attack is DIRECT. If not, DM the attacked

        # MAGIC
        if _style == 'MAGIC':

            # If the attack is INDIRECT, multiple RECOG by 5
            my_dmgdeal = round(aDict['a_dmg']*shots)

            # AURA comes in
            aura_dict = {'FLAME': 'au_FLAME', 'ICE': 'au_ICE', 'DARK': 'au_DARK', 'HOLY': 'au_HOLY'}        # Normal
            aura_redict = {'FLAME': 'au_ICE', 'ICE': 'au_HOLY', 'DARK': 'au_FLAME', 'HOLY': 'au_DARK'}      # Reversed
            # DMG is directional->UAura, is indirectional->reverseTAura     ||      DMG is then decreased by its oppo's parallel aura
            try: dmgdeal = int(my_dmgdeal*uDict[aura_dict[aDict['w_aura']]]/tDict[aura_redict[aDict['w_aura']]] - my_dmgdeal*tDict[aura_dict[aDict['w_aura']]])
            except ZeroDivisionError: dmgdeal = int(dmgdeal*tDict[aura_dict[aDict['w_aura']]])

            await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{tDict['target_id']}';")
            await MSG.send(f":dagger: **{shooter}** has dealt *{dmgdeal} DMG* to **{tDict['t_name']}**")
            if __bmode == 'INDIRECT': await tDict['target'].send(f":dagger: **{shooter}** has dealt *{dmgdeal} DMG* to **{tDict['t_name']}**"); return  
        
            await self.tools.ava_scan(MSG, 'life_check')

        # PHYSICAL
        else:
            # Recalculate the dmg

            ## Opponent's def
            # Get target's weapon
            if tDict['t_combat_HANDLING'] == 'both':
                tw_defend, tw_multiplier = await self.client.quefe(f"SELECT defend, multiplier, speed FROM pi_inventory WHERE existence='GOOD' AND item_id='{tDict['t_left_hand']}' AND user_id='{tDict['target_id']}'")
            elif tDict['t_combat_HANDLING'] == 'right':
                tw_defend, tw_multiplier = await self.client.quefe(f"SELECT defend, multiplier, speed FROM pi_inventory WHERE existence='GOOD' AND item_id='{tDict['t_right_hand']}' AND user_id='{tDict['target_id']}'")
                tw_defend *= 2
            elif tDict['t_combat_HANDLING'] == 'left':
                tw_defend, tw_multiplier = await self.client.quefe(f"SELECT defend, multiplier, speed FROM pi_inventory WHERE existence='GOOD' AND item_id='{tDict['t_left_hand']}' AND user_id='{tDict['target_id']}'")
                tw_defend *= 2

            async def dmg_calc(shots, pack):
                temp_query = ''
                tw_defend = pack[0]

                dmg = round(aDict['a_dmg']*shots)

                # Get Damage reduction
                # tCE - Processing
                try:
                    # Event: Evasive/Crit
                    tw_defend += tw_defend/100*float(tCE['defensive'])
                except (TypeError, KeyError): pass

                dmgredu = 200 - tw_defend
                # If victim's defend (dmgredu) exceed 200, the attacker's STA takes dmg
                if dmgredu < 0:
                    temp_query += f"UPDATE personal_info SET STA=STA-{round(dmg / 200 * abs(dmgredu))*tw_multiplier} WHERE id='{MSG.author.id}'; "
                    dmgredu = 0

                # Get dmgdeal (don't combine, for informing :>)
                dmg = round(dmg / 200 * dmgredu)

                # CE - Processing
                try:
                    # Event: Evasive/Crit
                    aDict['a_weight'] += aDict['a_weight']/100*float(CE['evasive'])
                except (TypeError, KeyError): pass

                # Crit
                if aDict['w_stealth']: aDict['a_weight'] *= aDict['w_stealth']
                if not random.choice(range(int(aDict['a_weight']/10))): dmg = dmg + dmg/10*aDict['a_weight']

                temp_query += f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{tDict['target_id']}';"

                return dmg, temp_query

            dmgdeal, temp_query = await dmg_calc(shots, (tw_defend))
            await self.client._cursor.execute(temp_query)

            await MSG.send(f":dagger: **{shooter}** has dealt *{dmgdeal} DMG* to **{tDict['t_name']}**")
            if __bmode == 'INDIRECT': await tDict['target'].send(f":dagger: **{shooter}** has dealt *{dmgdeal} DMG* to **{tDict['t_name']}**")
        
            await self.tools.ava_scan(MSG, 'life_check')



    def CE_effect_encoder(self, value, mode='decode'):
        """decode: String to List
            encode: List to String"""

        if mode == 'decode':
            if not value: return []
            elist = []
            for v in value.split(' || '):
                elist.append(v.split(' - '))
            return elist

        else:
            # # Filtering
            # try: value.remove([''])
            # except ValueError: pass

            temp = []
            # print(f"Value into decoder --- {value}")
            for v in value:
                # STR convert (since there are int in v)
                try:
                    temp.append(' - '. join(v))
                except TypeError:
                    temp.append(' - '. join([str(i) for i in v]))
            return ' || '.join(temp)

    async def CE_maker(self, raw_pcm):

        # If CE not found, init one
        CE = {
            "aggressive": 0, "defensive": 0, "evasive": 0, "ultimate": 0, "raw_pcm": '',
            "lock": 'n/a',
            "effect": '',
        }

        count = 0
        for c in raw_pcm:
            if c == 'a': CE['aggressive'] = float(CE['aggressive']) + 1.25 + count
            elif c == 'd': CE['defensive'] = float(CE['defensive']) + 1.25 + count
            elif c == 'e': CE['evasive'] = float(CE['evasive']) + 1.25 + count
            else: return False
            count += 0.2
        CE['raw_pcm'] = raw_pcm
        return CE





def setup(client):
    client.add_cog(avaCombat(client))
