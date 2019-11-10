import discord
import pymysql.err as mysqlError
import discord.errors as discordErrors

import random
from os import listdir
import asyncio

from functools import partial

import concurrent
import inspect

class avaTools:

    def __init__(self, client, utils):
        self.client = client
        self.utils = utils


    # RESOURCE INTERACTION ==================================================

    async def quefe(self, query, args=None, type='one'):
        """args ---> tuple"""

        if not self.client: return

        try: await self.client._cursor.execute(query, args=args)
        except RuntimeError: return ''
        #except mysqlError.OperationalError:
        #    loop.call_soon_threadsafe(loop.stop)
        #    conn, self.client._cursor = loop.run_until_complete(geself.client._CURSOR())
        #    await self.client._cursor.execute(query, args=args)
        if type == 'all': resu = await self.client._cursor.fetchall()
        else: resu = await self.client._cursor.fetchone()
        return resu

    async def redio_map(self, key, dict=None, mode='set', ttl=0, getttl=False):
        await asyncio.sleep(0)

        # Set dict into key with expiration ===========
        if mode == 'set':
            await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.hmset, key, dict))
            if ttl: await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.expire, key, ttl))
            return

        # Get dict ====================================
        endict = await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.hgetall, key))
        dedict = {k.decode('utf-8'):v.decode('utf-8') for k, v in endict.items()}

        # Whether get time-to-live of the dict
        if getttl:
            time = await self.client.loop.run_in_executor(None, partial(self.client.thp.redio.ttl, key))
            if not time: return None, None
            else: return dedict, time
        return dedict

    #Generate random file's name from the path
    async def file_gen_random(self, path):
        file_name = ''
        file_name = await self.client.loop.run_in_executor(None, random.choice, await self.client.loop.run_in_executor(None, listdir, path))
        return file_name



    async def ava_scan(self, MSG, type='all', target_id='n/a', target_coord=(), pb_coord=[]):
        """
            target_coord:    (x, y, cur_PLACE)
            pb_coord:        [[x, y, x, y], [x, y, x, y],..]

            <pb>    if pb_coord is provided, return (bool, (type, biome))
                    else return bool only
        """

        # Get target
        #try: target = await self.client.get_user_info(int(target_id))
        #except discordErrors.NotFound:
        target = MSG.author
        target_id = str(target.id)
        await asyncio.sleep(0)
        if not self.client: return

        # Readjust the incorrect value
        if type == 'normalize':
            #query = ''
            #if STA > MAX_STA: query = query + f"UPDATE personal_info SET STA=IF(STA>MAX_STA, MAX_STA, STA) WHERE id='{target_id}';"
            #if LP > MAX_LP: query = query + f"UPDATE personal_info SET LP=IF(LP>MAX_LP, MAX_LP, LP) WHERE id='{target_id}';"
            try: await self.client._cursor.execute(f"UPDATE personal_info SET LP=IF(LP>MAX_LP, MAX_LP, LP), STA=IF(STA>MAX_STA, MAX_STA, STA) WHERE id='{target_id}';")
            except mysqlError.InternalError: pass
            return True
        elif type == 'pb':
            pb_in = False
            # Check info. If not exist, get info.
            if not target_coord:
                target_coord = await self.client.quefe(f"SELECT cur_X, cur_Y, cur_PLACE FROM personal_info WHERE id='{target_id}';")
                if not target_coord: await MSG.channel.send(f"You don't have a *character*, **{MSG.author.name}**. Use `incarnate` to create one, then `tutorial` for... tutorial <:yeee:636045188153868309>"); return
            if not pb_coord:
                pb_coord_temp = await self.client.quefe(f"SELECT PB, type, biome FROM environ WHERE environ_code='{target_coord[2]}';")
                pb_coord_temp2 = pb_coord_temp[0].split(' | ')
                pb_coord = []
                for p in pb_coord_temp2:
                    pb_coord.append(p.split(' - '))
            else:
                pb_in = True
            # Check PB
            for p in pb_coord:
                if float(p[0]) <= float(target_coord[0]) and float(p[1]) <= float(target_coord[1]) and float(p[2]) >= float(target_coord[0]) and float(p[3]) >= float(target_coord[1]):
                    if pb_in:
                        return True
                    else:
                        return True, (pb_coord_temp[1], pb_coord_temp[2])
            if pb_in:
                return False
            else:
                return False, (pb_coord_temp[1], pb_coord_temp[2])


        # Status check
        try:
            LP, MAX_LP, STA, MAX_STA, cur_X, cur_Y, stats, dob = await self.quefe(f"SELECT LP, MAX_LP, STA, MAX_STA, cur_X, cur_Y, stats, dob FROM personal_info WHERE id='{target_id}'")
            #LP, MAX_LP, STA, MAX_STA, cur_X, cur_Y, stats, dob = await self.quefe(f"SELECT LP, MAX_LP, STA, MAX_STA, cur_X, cur_Y, stats, dob FROM personal_info WHERE id='{target_id}'")
        except TypeError: await MSG.channel.send(f"You don't have a *character*, **{MSG.author.name}**. Use `incarnate` to create one, then `tutorial` for... tutorial <:yeee:636045188153868309>"); return
        if stats == 'DEAD': 
            #if target_id == MSG.author.id: await MSG.channel.say(f"<:tumbstone:544353849264177172> You. Are. Dead, **{target.mention}**. Have a nice day!"); return
            #else: await MSG.channel.send(f"<:tumbstone:544353849264177172> The target **{target.name}** was dead, **{MSG.author.mention}**. *Press F to pay respect.*"); return
            await MSG.channel.send(f"<:tumbstone:544353849264177172> You. Are. Dead, **{target.mention}**. Have a nice day!"); return

        # Time check
        if type == 'all':
            time_pack = await self.client.loop.run_in_executor(concurrent.futures.ThreadPoolExecutor(max_workers=2), self.utils.time_get)
            # time_pack = self.utils.time_get()

            await self.client._cursor.execute(f"UPDATE personal_info SET age={time_pack[0] - int(dob.split(' - ')[2])} WHERE id='{target_id}';")
            return True
        # STA, LP, sign_in check
        elif type == 'life_check':
            if cur_X < 0 or cur_Y < 0: await MSG.channel.send(f"<:osit:544356212846886924> {target.mention}, please **log in**. Just use command `teleport` anywhere and you'll be signed in the world's map. (e.g. `teleport 1 1`)"); return False
            if STA < 0: await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-{abs(STA)}, STA=0 WHERE id='{target_id}';")
            if LP <= 0:
                # Status reset
                reviq = f"UPDATE personal_info SET stats='DEAD', cur_PLACE='region.0', cur_X=-1, cur_Y=-1, cur_MOB='n/a', cur_USER='n/a', right_hand='ar13', left_hand='ar13', money=0, merit=IF(merit >= 0, 0, merit), deaths=deaths+1 WHERE id='{target_id}';"
                # Remove FULL and ONGOING quests
                reviq = reviq + f" DELETE FROM pi_quests WHERE user_id='{target_id}' AND stats IN ('FULL', 'ONGOING');"
                # Remove all items but ar13|Fist (Default)
                #reviq = reviq + f" UPDATE pi_inventory SET existence='BAD' WHERE user_id='{target_id}' AND item_code!='ar13';"
                await self.client._cursor.execute(reviq)

                await MSG.channel.send(f"<:tumbstone:544353849264177172> {target.mention}, you are dead. Please re-incarnate.")
                return False
            return True

    async def area_scan(self, ctx, x, y):
        if x <= 1 and y <= 1: return True
        else: return False

    async def tele_procedure(self, current_place, user_id, desti_x, desti_y):
        """x, y: float"""
        # Assign the user's id to coord / Resign the user's id from the old coord
        await self.client._cursor.execute(f"UPDATE personal_info SET cur_X={desti_x:.3f}, cur_Y={desti_y:.3f} WHERE id='{user_id}';")
        # Assign the coord to ava
        #self.ava_dict[user_id]['realtime_zone']['current_coord'] = [desti_x, desti_y]

    async def division_LP(self, b, mb, time=2):
        "Reduct LP an amount of mb/time. If loss > LP, set LP = 1"
        loss = int(mb / time)
        if loss > b: return 1
        return b - loss


    async def world_built(self):
        regions = await self.client.quefe("SELECT environ_code FROM environ", type='all')
        print(regions)

        for region in regions:
            print(region)
            await asyncio.sleep(0.2)
            region = region[0]
            
            # ----------- MOB/BOSS/NPC initialize ------------
            mobs = await self.client.quefe(f"SELECT mob_code, quantity, limit_Ax, limit_Ay, limit_Bx, limit_By FROM environ_diversity WHERE environ_code='{region}';", type='all')

            for mob in mobs:
                print(mob)
                mob = list(mob)
                # MOB
                if mob[0].startswith('mb'):
                    # Quantity of kind in a diversity check
                    qk = await self.client.quefe(f"SELECT COUNT(*) FROM environ_mob WHERE mob_code='{mob[0]}' AND region='{region}';")

                    if int(qk[0]) == mob[1]: continue
                    elif int(qk[0]) < mob[1]: mob[1] -= int(qk[0])
                    
                    # Get the <mob> prototype
                    name, description, branch, lp, str, chain, speed, attack_type, defense_physic, defense_magic, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY, skills, effect, description, lockon_max, illulink = await self.client.quefe(f"SELECT name, description, branch, lp, str, chain, speed, attack_type, defense_physic, defense_magic, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY, skills, effect, description, lockon_max, illulink FROM model_mob WHERE mob_code='{mob[0]}';")
                    try: rewards = rewards.split(' | ')
                    except AttributeError: rewards = []
                    
                    # Mass production
                    for _ in range(mob[1]):
                        # await asyncio.sleep(0.01)
                        # Generating rewards
                        status = []; objecto = []; bingo_list = []
                        # Gacha
                        for reward in rewards:
                            stuff = reward.split(' - ')
                            if await self.utils.percenter(int(stuff[2])):
                                await asyncio.sleep(0)

                                # Stats reward
                                if stuff[0] in ['money', 'perks']:
                                    if stuff[0] == 'money': bingo_list.append(f"<:36pxGold:548661444133126185>{stuff[1]}")
                                    elif stuff[0] == 'perks': bingo_list.append(f"<:perk:632340885996044298>{stuff[1]}")

                                    status.append(f"{stuff[0]}={stuff[0]}+{int(stuff[1])}")
                                # ... other shit
                                else:
                                    objecto.append(f"""SELECT func_it_reward("user_id_here", "{stuff[0]}", {stuff[1]}); SELECT func_ig_reward("user_id_here", "{stuff[0]}", {stuff[1]});""")
                                    bingo_list.append(f"item `{stuff[0]}`")

                        stata = f"""UPDATE personal_info SET {', '.join(status)} WHERE id="user_id_here"; """
                        rewards_query = f"{stata} {' '.join(objecto)}"

                        # Insert the mob to DB
                        await self.client._cursor.execute(f"""INSERT INTO environ_mob VALUES (0, 'mob', '{mob[0]}', "{name}", "{description}", '{branch}', {lp}, {str}, {chain}, {speed}, '{attack_type}', {defense_physic}, {defense_magic}, {au_FLAME}, {au_ICE}, {au_HOLY}, {au_DARK}, '{skills}', '{effect}', '{' | '.join(bingo_list)}', '{rewards_query}', '{region}', {mob[2]}, {mob[3]}, {mob[4]}, {mob[5]}, {lockon_max}, "{illulink}", '');""")
                        counter_get = await self.client.quefe("SELECT MAX(id_counter) FROM environ_mob")
                        await self.client._cursor.execute(f"UPDATE environ_mob SET mob_id='mob.{counter_get[0]}' WHERE id_counter={counter_get[0]};")
                
                # NPC
                elif mob[0].startswith('p'):
                    # Quantity of kind in a diversity check
                    qk = await self.client.quefe(f"SELECT COUNT(*) FROM environ_npc WHERE npc_code='{mob[0]}' AND region='{region}';")
                    if qk[0] == mob[1]: continue
                    elif qk[0] < mob[1]: mob[1] -= qk[0]
                    
                    # Get the <mob> prototype
                    name, branch, lp, str, chain, speed, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY = await self.client.quefe(f"SELECT name, branch, lp, str, chain, speed, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY FROM model_npc WHERE npc_code='{mob[0]}';")
                    if rewards:
                        rewards = rewards.split(' | ')
                        
                        
                        # Mass production
                        for _ in range(mob[1]):
                            # await asyncio.sleep(0.01)
                            # Generating rewards
                            status = []; objecto = []; bingo_list = []
                            for reward in rewards:
                                await asyncio.sleep(0)

                                stuff = reward.split(' - ')
                                if random.choice(range(int(stuff[2]))) == 0:
                                    if stuff[0] == 'money': bingo_list.append(f"<:36pxGold:548661444133126185>{stuff[1]}")

                                    # Stats reward
                                    if stuff[0] in ['money']: status.append(f"{stuff[0]}={stuff[0]}+{int(stuff[1])}")
                                    # ... other shit
                                    else:
                                        # Get item/weapon's info
                                        temp = await self.client.quefe(f"SELECT * FROM model_item WHERE item_code='{stuff[0]}';")
                                        # SERI / UN-SERI check
                                        # SERI
                                        if 'inconsumbale' in temp[2].split(' - '):
                                            #objecto.append(f"""INSERT INTO pi_inventory VALUE ("user_id_here", {', '.join(temp)});""")
                                            objecto.append(f"""SELECT func_it_reward('user_id_here', '{stuff[0]}', '{random.choice(range(stuff[1]))}');""")
                                        # UN-SERI
                                        else:
                                            #objecto.append(f"""UPDATE pi_inventory SET quantity=quantity+{random.choice(range(stuff[1]))} WHERE user_id="user_id_here" AND item_code='{stuff[0]}';""")
                                            objecto.append(f"""SELECT func_ig_reward('user_id_here', '{stuff[0]}', '{random.choice(range(stuff[1]))}');""")
                            stata = f"""UPDATE personal_info SET {', '.join(status)} WHERE id="user_id_here"; """
                            rewards_query = f"{stata} {' '.join(objecto)}"
                    else: rewards_query = ''; bingo_list = []

                    # Insert the mob to DB
                    await self.client._cursor.execute(f"""INSERT INTO environ_npc VALUES (0, 'main', '{mob[0]}', "{name}", '{branch}', {lp}, {str}, {chain}, {speed}, {au_FLAME}, {au_ICE}, {au_DARK}, {au_HOLY}, '{' | '.join(bingo_list)}', '{rewards_query}', '{region}', {mob[2]}, {mob[3]}, {mob[4]}, {mob[5]}, 'n/a', '');""")
                    counter_get = await self.client.quefe("SELECT MAX(id_counter) FROM environ_npc")
                    await self.client._cursor.execute(f"UPDATE environ_npc SET npc_id='npc.{counter_get[0]}' WHERE id_counter={counter_get[0]};")

            # ----------- MAP initialize -------------
            # Obsolete since JSON ver
            """
            map = []
            for x in range(51):
                x = []
                for y in range(51):
                    x.append([])
                map.append(x)
            #Assign user's id onto the map
            for user_id in list(self.ava_dict.keys()):
                try: map[int(self.ava_dict[user_id]['realtime_zone']['current_coord'][0])][int(self.ava_dict[user_id]['realtime_zone']['current_coord'][1])].append(user_id)
                except TypeError: pass
            #Return the map
            self.environ[region]['map'] = map
            """
            
            # ----------- QUESTS initialize ----------
            # Obsolete since JSON ver
            """           
            try: self.environ[region]['characteristic']['quest'] = data_QUESTS
            except KeyError: print("KEY_ERROR")
            """
        
        print("___WORLD built() done")  



    # CHARACTER INIT =======================================================

    async def character_generate(self, id, name, dob=[0, 0, 0, 0, 0], player=True, resu=True, info_pack=[]):
        """
            YYMMDDHHMM
            [race, gender, name]    
        """

        ava = {}

        if not resu:
            if info_pack[2]: ava['name'] = await self.utils.inj_filter(info_pack[2])
            else: ava['name'] = await self.utils.inj_filter(name[0:20])
            ava['dob'] = f"{dob[2]} - {dob[1]} - {dob[0]}"
            ava['age'] = 0
            if info_pack: ava['gender'] = info_pack[1]
            else: ava['gender'] = random.choice(['m', 'f'])
            
            if info_pack: ava['race'] = info_pack[0]
            else: ava['race'] = random.choice(['rc0', 'rc1', 'rc2', 'rc3'])
            r_aura, r_min_H, r_max_H, r_min_W, r_max_W, r_size_1, r_size_2, r_size_3 = await self.quefe(f"SELECT aura, min_H, max_H, min_W, max_W, size_1, size_2, size_3 FROM model_race WHERE race_code='{ava['race']}';")
            if ava['gender'] == 'm':
                ava['height'] = random.choice(range(r_min_H + 10, r_max_H + 10))
                ava['weight'] = random.choice(range(r_min_W + 10, r_max_W + 10))
                ava['size'] = '78 - 80 - 90'
            else:
                ava['height'] = random.choice(range(r_min_H - 10, r_max_H - 10))
                ava['weight'] = random.choice(range(r_min_W - 10, r_max_W - 10))
                r_size_1 = r_size_1.split(' - '); r_size_2 = r_size_2.split(' - '); r_size_3 = r_size_3.split(' - ')
                ava['size'] = f'{random.choice(range(int(r_size_1[0]), int(r_size_1[1])))} - {random.choice(range(int(r_size_2[0]), int(r_size_2[1])))} - {random.choice(range(int(r_size_3[0]), int(r_size_3[1])))}'

            # Charm calc
            ava['charm'] = 10
            if ava['height'] >= 180: ava['charm'] += 5
            elif ava['height'] <= 130: ava['charm'] -= 5
            
            if ava['weight'] <= 35 or ava['weight'] >= 90: ava['charm'] -= 5
            else: ava['charm'] += 5

            szl = ava['size'].split(' - ')
            if int(szl[0]) >= 25: ava['charm'] += 5
            if int(szl[1]) >= 75: ava['charm'] -= 5
            if int(szl[2]) >= 115: ava['charm'] += 5
            
            ava['partner'] = 'n/a'
            ava['avatar'] = 'av0'
            if ava['gender'] == 'f': ava['avatars'] = ['av19', 'av0', 'av1', 'av2']
            else: ava['avatars'] = ['av33', 'av0', 'av1', 'av2']
            ava['EVO'] = 0
            ava['INTT'] = 0
            ava['STA'] = 100
            ava['MAX_STA'] = 100
            ava['STR'] = 0.5
            ava['LP'] = 1000
            ava['MAX_LP'] = 1000        
            ava['kills'] = 0; ava['deaths'] = 0
            ava['money'] = 100
            ava['merit'] = 0
            ava['perks'] = 100
            auras = {'FLAME': [1.5, 0, 0, 0], 'ICE': [0, 1.5, 0, 0], 'HOLY': [0, 0, 1.5, 0], 'DARK': [0, 0, 0, 1.5]}
            ava['auras'] = auras[r_aura]

            ava['arts'] = {'sword_art': {'chain_attack': 3}, 'pistol_art': {}}

            ava['cur_PLACE'] = 'region.0'
            ava['cur_MOB'] = 'n/a'
            ava['cur_USER'] = 'n/a'
            ava['cur_X'] = -1
            ava['cur_Y'] = -1
            ava['cur_QUEST'] = 'n/a'

            # Last check
            await asyncio.sleep(0.2)
            if await self.client._cursor.execute(f"SELECT stats FROM personal_info WHERE id='{id}';") != 0:
                return 3

            # Inventory     |      Add fist as a default weapon
            await self.client._cursor.execute(f"SELECT func_it_reward('{id}', 'ar13', 1);")
            dfFist = await self.quefe(f"SELECT item_id FROM pi_inventory WHERE user_id='{id}';")
            ava['combat_HANDLING'] = 'both'
            ava['right_hand'] = dfFist[0]
            ava['left_hand'] = dfFist[0]
            # Equipment
            await self.quefe(f"INSERT INTO pi_equipment VALUES (0, '{id}', 'Untitled', 'belt', 'n/a'); INSERT INTO pi_equipment VALUES (0, '{id}', 'Untitled', 'belt', 'n/a');")

            await self.quefe(f"INSERT INTO personal_info VALUES ('{id}', '{ava['name']}', '{ava['dob']}', {ava['age']}, '{ava['gender']}', '{ava['race']}', {ava['height']}, {ava['weight']}, '{ava['size']}', 'GREEN', {ava['kills']}, {ava['deaths']}, {ava['charm']}, '{ava['partner']}', {ava['money']}, {ava['merit']}, {ava['perks']}, {ava['EVO']}, {ava['STR']}, {ava['INTT']}, {ava['STA']}, {ava['MAX_STA']}, {ava['LP']}, {ava['MAX_LP']}, {ava['auras'][0]}, {ava['auras'][1]}, {ava['auras'][2]}, {ava['auras'][3]}, '{ava['cur_MOB']}', '{ava['cur_USER']}', '{ava['cur_PLACE']}', {ava['cur_X']}, {ava['cur_Y']}, '{ava['cur_QUEST']}', '{ava['combat_HANDLING']}', '{ava['right_hand']}', '{ava['left_hand']}');")
            await self.quefe(f"INSERT INTO pi_degrees VALUES (0, '{id}', 'Instinct', NULL);")
            # Guild
            await self.client._cursor.execute(f"INSERT INTO pi_guild VALUES ('{id}', 'n/a', 'iron', 0, 0);")
            # Avatars
            for ava_code in ava['avatars']: await self.client._cursor.execute(f"INSERT INTO pi_avatars VALUES ('{id}', '{ava_code}');")
            await self.client._cursor.execute(f"INSERT INTO pi_backgrounds VALUES ('{id}', 'bg0');")
            await self.client._cursor.execute(f"INSERT INTO pi_fonts VALUES ('{id}', 'fnt0');")
            await self.client._cursor.execute(f"INSERT INTO cosmetic_preset VALUES (0, '{id}', 'default of {ava['name']}', 'DEFAULT', '{ava['avatars'][0]}', 'bg0', 'fnt0', 2.6, '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF')")
            await self.client._cursor.execute(f"INSERT INTO cosmetic_preset VALUES (0, '{id}', 'default of {ava['name']}', 'CURRENT', '{ava['avatars'][0]}', 'bg0', 'fnt0', 2.6, '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF')")
            # Arts
            await self.client._cursor.execute(f"""SELECT func_aa_reward('{id}', 'aa0', 1);
                                                    SELECT func_aa_reward('{id}', 'aa1', 1);""")

            if player: return 0
            else: return 2
        else:
            await self.client._cursor.execute(f"UPDATE personal_info SET LP=1, STA=1, stats='GREEN' WHERE id='{id}'; UPDATE pi_inventory SET existence='GOOD' WHERE user_id='{id}' AND item_code='ar13';")
            return 1

    async def hierarchy_generate(self, child_id, father_id='n/a', mother_id='n/a', guardian_ids=[], chem_value=0):
        guardian_id = ' ||| '.join(guardian_ids)
        await self.client._cursor.execute(f"INSERT INTO environ_hierarchy VALUES (0, '{child_id}', '', '{guardian_id}', {chem_value});")

    async def incarnateData_collect(self, ctx, aui):
        """Gather RACE and GENDER from user"""

        # Get race info ========================================
        re_race = await self.incarnateRace_collect(ctx, aui)
        if not re_race: return False

        # Get gender info ========================================
        re_gender = await self.incarnateGender_collect(ctx)
        if not re_gender: return False

        # Get name info ========================================
        re_name = await self.incarnateName_collect(ctx)
        if not re_name: return False

        return re_race, re_gender, re_name

    async def incarnateRace_collect(self, ctx, aui):
        """aui: aura icon"""

        # Get race info ========================================
        rundle = await self.client.quefe("SELECT race_code, name, aura, min_W, max_W, illulink, min_H, max_H FROM model_race ORDER BY race_code ASC;", type='all')

        # Prep
        def makeembed_race(items, top, least, pages, currentpage):
            item = items[top:least][0]

            reembed = discord.Embed(title=f"RACE :: [`{item[0]}`| **{item[1]}**]", description=f"╟ `HEIGHT` · {item[6]}~{item[7]} m\n╟ `WEIGHT` · {item[3]}~{item[4]} kg", colour=0x36393E)
            reembed.set_thumbnail(url=aui[item[2]])
            if item[5]: reembed.set_image(url=item[5])

            return reembed, item[0]

        # ROLL race
        await ctx.send(f"> {ctx.author.mention}, please choose yourself a **race**.")
        re_race = await self.pagiMainMicro(ctx, rundle, makeembed_race, item_per_page=1, timeout=60)
        if not re_race: return False
        else: return re_race

    async def incarnateGender_collect(self, ctx):
        # Prep =============================================
        def makeembed_gender(items, top, least, pages, currentpage):
            """[gender, illulink]"""

            reembed = discord.Embed(colour=0x36393E)
            reembed.set_image(url=items[top:least][0][1])

            return reembed, items[top:least][0][0]

        # ROLL gender
        await ctx.send(f"> {ctx.author.mention}, please choose yourself a **gender**.")
        re_gender = await self.pagiMainMicro(ctx, (('f', 'https://imgur.com/2X1E62g.png'), ('m', 'https://imgur.com/RPQ6cd9.png')), makeembed_gender, item_per_page=1, timeout=60, extra_button=["\U00002b05", '\U0001f44b', "\U000027a1"])
        if not re_gender: return False
        else: return re_gender

    async def incarnateName_collect(self, ctx):
        # NAME ==============================================
        await ctx.send(f"> {ctx.author.mention}, please give yourself a **name** within 20 characters. (Type `default` to use your user name)")
        try: raw = await self.client.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=60)
        except asyncio.TimeoutError: return False
        re_name = await self.utils.inj_filter(raw.content)
        if re_name == 'default': re_name = ctx.author.name
        return re_name



    # PAGINATOR ============================================================
    async def pagiButton(self, timeout=15, check=None):
        try:
            if check:
                done, pending = await asyncio.wait([self.client.wait_for('reaction_add', timeout=timeout, check=check), self.client.wait_for('reaction_remove', timeout=timeout, check=check)], return_when=asyncio.FIRST_COMPLETED)
            else:
                done, pending = await asyncio.wait([self.client.wait_for('reaction_add', timeout=timeout), self.client.wait_for('reaction_remove', timeout=timeout)], return_when=asyncio.FIRST_COMPLETED)
        except (asyncio.TimeoutError, concurrent.futures._base.TimeoutError, TimeoutError, concurrent.futures.TimeoutError):
            return

        try:
            fut = done.pop()

            fut = fut.result()

            for future in pending:
                future.cancel()

            return fut
        except asyncio.TimeoutError:
            for future in pending:
                future.cancel()
            raise asyncio.TimeoutError

    async def pageButtonAdd(self, msg, reaction=["\U000023ee", "\U00002b05", "\U000027a1", "\U000023ed"], extra=[], extra_replace=False):
        """
        Extra           (List) List of addition button. \n
        Extra_replace   (Bool) Whether Extra overwrites the main button"""

        if extra_replace:
            for charCode in extra:
                await msg.add_reaction(charCode)
        else:
            for charCode in reaction + extra:
                await msg.add_reaction(charCode)

    async def pageTurner(self, msg, reaction, user, pageInfoPack):
        """cursor, pages, emli = pageInfoPack"""

        cursor, pages, emli = pageInfoPack

        if reaction.emoji == "\U000027a1":
            if cursor < pages - 1: cursor += 1
            else: cursor = 0
        elif reaction.emoji == "\U00002b05":
            if cursor > 0: cursor -= 1
            else: cursor = pages - 1
        
        elif reaction.emoji == "\U000023ee" and cursor != 0:
            cursor = 0
        elif reaction.emoji == "\U000023ed" and cursor != pages - 1:
            cursor = pages - 1
        
        return cursor

    async def pagiMain(self, ctx, items, makeembed, item_per_page=5, extra_button=["\U000023ee", "\U00002b05", "\U000027a1", "\U000023ed"], pageTurner=None, cursor=0, timeout=15, delete_on_exit=True, pair=False, pair_sample=0):
        """
            This function is for makeembed() function that return single embed

            cursor:       (Int)  Starting cursor in the embeds list
            makembed:     (Func/Coro) Generator for one page with specific format.  
            extra_button: (List) Replacing buttons for the paginator.
            pageTurner:   (Coro) Custom behaviour for buttons - especially for extra buttons, isntead of standard behiviour. Return cursor.
            pair:         (Bool) Check if items is given more than one package (e.g. cmd quest, quests)
            pair_sample:  (Int)  Index number of the element in <items> to check for length of pages"""

        if not pair:
            pages = int(len(items)/item_per_page)
            if len(items)%item_per_page != 0: pages += 1
        else:
            pages = int(len(items[pair_sample])/item_per_page)
            if len(items[pair_sample])%item_per_page != 0: pages += 1
        currentpage = 1
        if not delete_on_exit: timeout = None

        # Embedding items ============
        emli = []
        for _ in range(pages):
            if inspect.iscoroutinefunction(makeembed):
                myembed = await makeembed(items, currentpage*item_per_page-item_per_page, currentpage*item_per_page, pages, currentpage)
            else:
                myembed = makeembed(items, currentpage*item_per_page-item_per_page, currentpage*item_per_page, pages, currentpage)
            emli.append(myembed)
            currentpage += 1

        # Send
        try:
            if pages > 1:
                if not emli[cursor]: await ctx.send(":spider_web::spider_web: Empty result... :spider_web::spider_web:"); return
                msg = await ctx.send(embed=emli[cursor])
                await self.pageButtonAdd(msg, reaction=extra_button)
            else:
                msg = await ctx.send(embed=emli[0])
        # except discordErrors.HTTPException:
        except IndexError:
            await ctx.send(":spider_web::spider_web: Empty result... :spider_web::spider_web:"); return

        # Button-ing
        while True:
            try:
                reaction, user = await self.pagiButton(check=lambda r, u: r.message.id == msg.id and u.id == ctx.author.id, timeout=timeout)
                if not pageTurner:
                    cursor = await self.pageTurner(msg, reaction, user, (cursor, pages, emli))
                else:
                    cursor = await pageTurner(msg, reaction, user, (cursor, pages, emli))
                await msg.edit(embed=emli[cursor])

            except concurrent.futures.TimeoutError:
                if delete_on_exit:
                    try: await msg.delete()
                    except discordErrors.NotFound: pass
                return
            # Rate-limit
            await asyncio.sleep(0.35)

    async def pagiMainMicro(self, ctx, items, makeembed, item_per_page=5, extra_button=["\U000023ee", "\U00002b05", '\U0001f44b', "\U000027a1", "\U000023ed"], pageTurner=None, cursor=0, timeout=15, delete_on_exit=True, pair=False, pair_sample=0):
        """
            This function is for makeembed() function that return micro_embed --> [embed, value]

            cursor:       (Int)  Starting cursor in the embeds list
            makembed:     (Func/Coro) Generator for one page with specific format.  
            extra_button: (List) Replacing buttons for the paginator.
            pageTurner:   (Coro) Custom behaviour for buttons - especially for extra buttons, isntead of standard behiviour. Return cursor.
            pair:         (Bool) Check if items is given more than one package (e.g. cmd quest, quests)
            pair_sample:  (Int)  Index number of the element in <items> to check for length of pages"""

        if not pair:
            pages = int(len(items)/item_per_page)
            if len(items)%item_per_page != 0: pages += 1
        else:
            pages = int(len(items[pair_sample])/item_per_page)
            if len(items[pair_sample])%item_per_page != 0: pages += 1
        currentpage = 1
        if not delete_on_exit: timeout = None

        # Embedding items ============
        emli = []
        for _ in range(pages):
            if inspect.iscoroutinefunction(makeembed):
                micro_embed = await makeembed(items, currentpage*item_per_page-item_per_page, currentpage*item_per_page, pages, currentpage)
            else:
                micro_embed = makeembed(items, currentpage*item_per_page-item_per_page, currentpage*item_per_page, pages, currentpage)
            emli.append(micro_embed)
            currentpage += 1

        # Send
        try:
            if pages > 1:
                if (not emli[cursor][0] and not isinstance(emli[cursor][0], discord.Embed)) or not emli[cursor][1]: await ctx.send(":spider_web::spider_web: Empty result... :spider_web::spider_web:"); return
                msg = await ctx.send(embed=emli[cursor][0])
                await self.pageButtonAdd(msg, reaction=extra_button)
            else:
                msg = await ctx.send(embed=emli[0][0])
        # except discordErrors.HTTPException:
        except IndexError:
            await ctx.send(":spider_web::spider_web: Empty result... :spider_web::spider_web:"); return

        # Button-ing
        while True:
            try:
                reaction, user = await self.pagiButton(check=lambda r, u: r.message.id == msg.id and u.id == ctx.author.id, timeout=timeout)

                # Choose
                if reaction.emoji == '\U0001f44b':
                    return emli[cursor][1]

                if not pageTurner:
                    cursor = await self.pageTurner(msg, reaction, user, (cursor, pages, emli))
                else:
                    cursor = await pageTurner(msg, reaction, user, (cursor, pages, emli))
                await msg.edit(embed=emli[cursor][0])

            except concurrent.futures.TimeoutError:
                if delete_on_exit:
                    try: await msg.delete()
                    except discordErrors.NotFound: pass
                return
            # Rate-limit
            await asyncio.sleep(0.35)





    # Obsolete from JSON ver
    """async def ava_manip(self, MSG, function, *args):
        · def stt_adjust(parameter, adjustment, value)
           · def stt_check(path)    ---    Dict only, seperate by /
        user_id = str(MSG.author.id)

        def stt_adjust(parameter, adjustment, value):
            if adjustment == 'add': self.ava_dict[user_id][parameter] += int(value)
            elif adjustment == 'subtract': self.ava_dict[user_id][parameter] += int(value)
            elif adjustment == 'multiply': self.ava_dict[user_id][parameter] = int(self.ava_dict[user_id][parameter]*value)
            elif adjustment == 'divide': self.ava_dict[user_id][parameter] = int(self.ava_dict[user_id][parameter]//value)

        def stt_check(path, creation_perm, endpoint=''):
            a = path.split('/')
            copy = self.ava_dict[user_id][a[0]]
            # Traverse. In case trarvesing is jammed, create the following nodes if permitted
            for node in a[1:]:
                try: copy = copy[node]
                except KeyError: 
                    if creation_perm == 1: 
                        # Make extra node
                        extra_node = {}; stuff = {}
                        for minode in reversed(a[a.index(node) + 1:]):
                            if a.index(minode) == -1: stuff = endpoint; continue
                            # Wrap stuff inside extra_node, labeled with minode. Then make extra_node a stuff
                            extra_node[minode] = stuff
                            stuff = extra_node
                        
                        print(extra_node)
                        print(self.ava_dict[user_id][a[0]])
                        # Replicate old one/nối dài 
                        old_node = {}; stuff_2 = []
                        print(a[1:a.index(node) + 1])
                        for minode in a[1:a.index(node) + 1]:
                            if a.index(minode) == 1: stuff_2.append(self.ava_dict[user_id][a[0]]); print("HERERERERRRRRRRR")
                            elif a.index(minode) == a.index(node): 
                                print("HUUUUUUUURURUR")
                                print(node)
                                print(minode)
                                #old_node = stuff_2[-1]
                                #stuff_2.append(old_node[node])
                                old_node = stuff_2[-1]
                                #thing[node] = extra_node
                                old_node[a[a.index(minode) - 1]] = {node: extra_node}
                                stuff_2[-1] = old_node
                            else: 
                                print("HEEEEEEEEEEE???")
                                old_node = stuff_2[-1]
                                #old_node[minode] = {node: extra_node}
                                old_node[a[a.index(minode) - 1]] = {node: extra_node}
                                stuff_2.append(old_node) 

                        print(stuff_2)
                        somenode = ''
                        if len(stuff_2) > 1:
                            for binode, minode in zip(reversed(stuff_2), reversed(a[1:a.index(node) + 1])):
                                stuff_2.reverse()
                                prev_binode = stuff_2[stuff_2.index(binode) - 1]
                                if not somenode: prev_binode[minode] = binode; somenode = prev_binode
                                else:
                                    prev_binode[minode] = somenode; somenode = prev_binode

                            self.ava_dict[user_id][a[0]] = somenode                        
                        
                    else: raise KeyError
                    print(self.ava_dict[user_id][a[0]])
                    return endpoint
            return copy

        if function == 'stt_adjust': stt_adjust(args[0], args[1], float(args[2]))
        # args[1]:Permission    args[2]:enpoint
        elif function == 'stt_check': 
            try: return stt_check(args[0], args[1], args[2])
            except IndexError: 
                try: return stt_check(args[0], args[1])
                except IndexError: return stt_check(args[0], 0)
    """                

