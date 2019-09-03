import pymysql.err as mysqlError

import random
from os import listdir
from functools import partial

class avaTools:

    def __init__(self, client, utils):
        self.client = client
        self.utils = utils

    async def quefe(self, query, args=None, type='one'):
        """args ---> tuple"""

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


    async def ava_scan(self, MSG, type='all', target_id='n/a'):
        # Get target
        #try: target = await self.client.get_user_info(int(target_id))
        #except discordErrors.NotFound:
        target = MSG.author
        target_id = str(target.id)

        # Readjust the incorrect value
        if type == 'normalize':
            #query = ''
            #if STA > MAX_STA: query = query + f"UPDATE personal_info SET STA=IF(STA>MAX_STA, MAX_STA, STA) WHERE id='{target_id}';"
            #if LP > MAX_LP: query = query + f"UPDATE personal_info SET LP=IF(LP>MAX_LP, MAX_LP, LP) WHERE id='{target_id}';"
            try: await self.client._cursor.execute(f"UPDATE personal_info SET LP=IF(LP>MAX_LP, MAX_LP, LP), STA=IF(STA>MAX_STA, MAX_STA, STA) WHERE id='{target_id}';")
            except mysqlError.InternalError: pass
            return True

        # Status check
        try:
            # pylint: disable=unused-variable
            LP, MAX_LP, STA, MAX_STA, cur_X, cur_Y, stats, dob = await self.quefe(f"SELECT LP, MAX_LP, STA, MAX_STA, cur_X, cur_Y, stats, dob FROM personal_info WHERE id='{target_id}'")
            #LP, MAX_LP, STA, MAX_STA, cur_X, cur_Y, stats, dob = await self.quefe(f"SELECT LP, MAX_LP, STA, MAX_STA, cur_X, cur_Y, stats, dob FROM personal_info WHERE id='{target_id}'")
            # pylint: enable=unused-variable
        except TypeError: await MSG.channel.send(f"You don't have a *character*, **{MSG.author.name}**. Use `incarnate` to create one."); return
        if stats == 'DEAD': 
            #if target_id == MSG.author.id: await MSG.channel.say(f"<:tumbstone:544353849264177172> You. Are. Dead, **{target.mention}**. Have a nice day!"); return
            #else: await MSG.channel.send(f"<:tumbstone:544353849264177172> The target **{target.name}** was dead, **{MSG.author.mention}**. *Press F to pay respect.*"); return
            await MSG.channel.send(f"<:tumbstone:544353849264177172> You. Are. Dead, **{target.mention}**. Have a nice day!"); return

        # Time check
        if type == 'all':
            time_pack = await self.client.loop.run_in_executor(None, self.utils.time_get)

            await self.client._cursor.execute(f"UPDATE personal_info SET age={time_pack[0] - int(dob.split(' - ')[2])} WHERE id='{target_id}';")
            return True
        # STA, LP, sign_in check
        elif type == 'life_check':
            if cur_X < 0 or cur_Y < 0: await MSG.channel.send(f"<:osit:544356212846886924> {target.mention}, please **log in**. Just use command `teleport` anywhere and you'll be signed in the world's map. (e.g. `teleport 1 1`)"); return False
            if STA < 0: await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-{abs(STA)}, STA=0 WHERE id='{target_id}';")
            if LP <= 0:
                # Status reset
                reviq = f"UPDATE personal_info SET stats='DEAD', cur_PLACE='region.0', cur_X=-1, cur_Y=-1, cur_MOB='n/a', cur_USER='n/a', right_hand='ar13', left_hand='ar13', money=0, perks=0, merit=0, deaths=deaths+1 WHERE id='{target_id}';"
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

    #Generate random file's name from the path
    async def file_gen_random(self, path):
        file_name = ''
        file_name = await self.client.loop.run_in_executor(None, random.choice, await self.client.loop.run_in_executor(None, listdir, path))
        return file_name

    async def tele_procedure(self, current_place, user_id, desti_x, desti_y):
        """x, y: float"""
        # Assign the user's id to coord / Resign the user's id from the old coord
        await self.client._cursor.execute(f"UPDATE personal_info SET cur_X={desti_x:.3f}, cur_Y={desti_y:.3f} WHERE id='{user_id}';")
        # Assign the coord to ava
        #self.ava_dict[user_id]['realtime_zone']['current_coord'] = [desti_x, desti_y]

    async def character_generate(self, id, name, dob=[0, 0, 0, 0, 0], player=True, resu=True):
        "YYMMDDHHMM"

        ava = {}

        if not resu:
            ava['name'] = await self.utils.inj_filter(name[0:20])
            ava['dob'] = f"{dob[2]} - {dob[1]} - {dob[0]}"
            ava['age'] = 0
            ava['gender'] = random.choice(['m', 'f'])
            ava['race'] = random.choice(['rc0', 'rc1', 'rc2', 'rc3'])
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
            ava['avatars'] = ['av0', 'av1', 'av2']
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
            ava['perks'] = 5
            auras = {'FLAME': [0.5, 0, 0, 0], 'ICE': [0, 0.5, 0, 0], 'HOLY': [0, 0, 0.5, 0], 'DARK': [0, 0, 0, 0.5]}
            ava['auras'] = auras[r_aura]

            ava['arts'] = {'sword_art': {'chain_attack': 4}, 'pistol_art': {}}

            ava['cur_PLACE'] = 'region.0'
            ava['cur_MOB'] = 'n/a'
            ava['cur_USER'] = 'n/a'
            ava['cur_X'] = -1
            ava['cur_Y'] = -1
            ava['cur_QUEST'] = 'n/a'

            # Inventory     |      Add fist as a default weapon
            await self.client._cursor.execute(f"SELECT func_it_reward('{id}', 'ar13', 1);")
            dfFist = await self.quefe(f"SELECT item_id FROM pi_inventory WHERE user_id='{id}';")
            ava['combat_HANDLING'] = 'both'
            ava['right_hand'] = dfFist[0]
            ava['left_hand'] = dfFist[0]

            await self.quefe(f"INSERT INTO personal_info VALUES ('{id}', '{ava['name']}', '{ava['dob']}', {ava['age']}, '{ava['gender']}', '{ava['race']}', {ava['height']}, {ava['weight']}, '{ava['size']}', 'GREEN', {ava['kills']}, {ava['deaths']}, {ava['charm']}, '{ava['partner']}', {ava['money']}, {ava['merit']}, {ava['perks']}, {ava['EVO']}, {ava['STR']}, {ava['INTT']}, {ava['STA']}, {ava['MAX_STA']}, {ava['LP']}, {ava['MAX_LP']}, {ava['auras'][0]}, {ava['auras'][1]}, {ava['auras'][2]}, {ava['auras'][3]}, '{ava['cur_MOB']}', '{ava['cur_USER']}', '{ava['cur_PLACE']}', {ava['cur_X']}, {ava['cur_Y']}, '{ava['cur_QUEST']}', '{ava['combat_HANDLING']}', '{ava['right_hand']}', '{ava['left_hand']}');")
            await self.quefe(f"INSERT INTO pi_degrees VALUES ('{id}', 'Instinct', NULL);")
            # Guild
            await self.client._cursor.execute(f"INSERT INTO pi_guild VALUES ('{id}', 'region.0', 'iron', 0, 0);")
            # Avatars
            for ava_code in ava['avatars']: await self.client._cursor.execute(f"INSERT INTO pi_avatars VALUES ('{id}', '{ava_code}');")
            await self.client._cursor.execute(f"INSERT INTO pi_backgrounds VALUES ('{id}', 'bg0');")
            await self.client._cursor.execute(f"INSERT INTO cosmetic_preset VALUES (0, '{id}', 'default of {ava['name']}','DEFAULT', 'av0', 'bg0', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF')")
            await self.client._cursor.execute(f"INSERT INTO cosmetic_preset VALUES (0, '{id}', 'default of {ava['name']}', 'CURRENT', 'av0', 'bg0', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF')")
            # Arts
            await self.client._cursor.execute(f"""INSERT INTO pi_arts VALUES ('{id}', 'melee', 'active_chain', 5);
                                                INSERT INTO pi_arts VALUES ('{id}', 'general', 'passive_chain', 5);""")
            #self.ava_dict[id] = ava
            if player: return 0
            else: return 2
        else:
            await self.client._cursor.execute(f"UPDATE personal_info SET LP=1, STA=1, stats='GREEN' WHERE id='{id}'; UPDATE pi_inventory SET existence='GOOD' WHERE user_id='{id}' AND item_code='ar13';")
            return 1

    async def hierarchy_generate(self, child_id, father_id='n/a', mother_id='n/a', guardian_ids=[], chem_value=0):
        guardian_id = ' ||| '.join(guardian_ids)
        await self.client._cursor.execute(f"INSERT INTO environ_hierarchy VALUES (0, '{child_id}', '', '{guardian_id}', {chem_value});")

    async def division_LP(self, b, mb, time=2):
        "Reduct LP an amount of mb/time. If loss > LP, set LP = 1"
        loss = int(mb / time)
        if loss > b: return 1
        return b - loss






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

