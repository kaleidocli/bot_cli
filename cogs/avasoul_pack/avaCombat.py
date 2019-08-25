import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors

import random
import asyncio

from .avaTools import avaTools
from .avaUtils import avaUtils

class avaCombat:
    def __init__(self, client):
        self.client = client
        self.utils = avaUtils(self.client)
        self.tools = avaTools(self.client, self.utils)


    async def on_ready(self):
        print("|| Combat ---- READY!")



    # This function handles the Mob phase
    # Melee PVE     |      Start the mob phase.
    async def PVE(self, MSG, target_id):
        # Lock-on check. If 'n/a', proceed PVE. If the mob has already locked on other, return.
        try:
            t_name, t_speed, t_str, t_chain = await self.client.quefe(f"SELECT name, speed, str, chain FROM environ_mob WHERE mob_id='{target_id}' AND lockon='n/a';")
            # Set lock-on, as the target is user_id
            await self.client._cursor.execute(f"UPDATE environ_mob SET lockon='{MSG.author.id}' WHERE mob_id='{target_id}';")
        except TypeError: return

        name, evo, STA, MAX_STA, user_id, cur_PLACE, cur_X, cur_Y, cur_MOB, combat_HANDLING, right_hand, left_hand = await self.client.quefe(f"SELECT name, evo, STA, MAX_STA, id, cur_PLACE, cur_X, cur_Y, cur_MOB, combat_HANDLING, right_hand, left_hand FROM personal_info WHERE id='{MSG.author.id}';")
        message_obj = False
        try: await MSG.delete()
        except discordErrors.Forbidden: pass

        async def conclusing():
            # REFRESHING ===========================================
            name, LP, STA, user_id, cur_PLACE = await self.client.quefe(f"SELECT name, LP, STA, id, cur_PLACE FROM personal_info WHERE id='{MSG.author.id}';")
            #name, LP, STA, MAX_STA, user_id, cur_PLACE, cur_X, cur_Y, cur_MOB, combat_HANDLING, right_hand, left_hand = await self.client.quefe(f"SELECT name, LP, STA, MAX_STA, id, cur_PLACE, cur_X, cur_Y, cur_MOB, combat_HANDLING, right_hand, left_hand FROM personal_info WHERE id='{MSG.author.id}';")
            t_lp, t_name = await self.client.quefe(f"SELECT lp, name FROM environ_mob WHERE mob_id='{target_id}';")
            #t_lp, t_name, t_speed, t_str, t_chain = await self.client.quefe(f"SELECT lp, name, speed, str, chain FROM environ_mob WHERE mob_id='{target_id}';")


            if not await self.tools.ava_scan(MSG, type='life_check'):
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

            msg = f"╔═══════════\n╟:heartpulse:`{LP}` :muscle:`{STA}` ⠀⠀ |〖**{name}**〗\n╟:heartpulse:`{t_lp}`⠀⠀⠀⠀⠀⠀⠀⠀|〖**{t_name}**〗\n╚═══════════"
            return msg

        async def vanishing():
            # Looting
            mob_code, rewards, reward_query, region, t_Ax, t_Ay, t_Bx, t_By = await self.client.quefe(f"SELECT mob_code, rewards, reward_query, region, limit_Ax, limit_Ay, limit_Bx, limit_By FROM environ_mob WHERE mob_id='{target_id}';")
            await self.client._cursor.execute(reward_query.replace('user_id_here', str(MSG.author.id)))

            await MSG.channel.send(f"<:chest:507096413411213312> Congrats **{MSG.author.mention}**, you've received **{rewards.replace(' | ', '** and **')}** from **「`{target_id}` | {t_name}」**!")
            
            # Get the <mob> prototype
            name, branch, lp, strr, chain, speed, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY, t_evo = await self.client.quefe(f"SELECT name, branch, lp, str, chain, speed, rewards, au_FLAME, au_ICE, au_DARK, au_HOLY, evo FROM model_mob WHERE mob_code='{mob_code}';")
            rewards = rewards.split(' | ')

            # Generating rewards
            status = []; objecto = []; bingo_list = []
            for reward in rewards:
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
                            objecto.append(f"""INSERT INTO pi_inventory VALUE ("user_id_here", {', '.join(temp)});""")
                        # UN-SERI
                        else: objecto.append(f"""UPDATE pi_inventory SET quantity=quantity+{random.choice(range(stuff[1]))} WHERE user_id="user_id_here" AND item_code='{stuff[0]}';""")
            # Merit calc
            merrire = t_evo - evo + 1
            if merrire < 0: merrire = 0
            else:
                if target_id.startswith('boss'): merrire = int(merrire/2*10)
            stata = f"""UPDATE personal_info SET {', '.join(status)}, merrit=merrit+{merrire} WHERE id="user_id_here"; """
            rewards_query = f"{stata} {' '.join(objecto)}"

            # Remove the old mob from DB
            await self.client._cursor.execute(f"DELETE FROM environ_mob WHERE mob_id='{target_id}';")

            # Insert the mob to DB
            await self.client._cursor.execute(f"""INSERT INTO environ_mob VALUES (0, 'mob', '{mob_code}', "{name}", '{branch}', {lp}, {strr}, {chain}, {speed}, {au_FLAME}, {au_ICE}, {au_DARK}, {au_HOLY}, '{' | '.join(bingo_list)}', '{rewards_query}', '{region}', {t_Ax}, {t_Ay}, {t_Bx}, {t_By}, 'n/a');""")
            counter_get = await self.client.quefe("SELECT MAX(id_counter) FROM environ_mob")
            await self.client._cursor.execute(f"UPDATE environ_mob SET mob_id='mob.{counter_get[0]}' WHERE id_counter={counter_get[0]};")

            return branch

        # ------------ MOB PHASE    |   Mobs attack, user defend
        async def battle(message_obj):

            async def attack():
                mmoves = [random.choice(['a', 'd', 'b']) for move in range(t_chain)]
                
                # Decoding moves, as well as checking the moves. Get the counter_move
                counter_mmove = []
                for move in mmoves:
                    if move == 'a': counter_mmove.append('d')
                    elif move == 'd': counter_mmove.append('b')
                    elif move == 'b': counter_mmove.append('a')

                dmg = t_str
                return dmg, mmoves, counter_mmove

            # ======================================================

            if not await conclusing(): return False

            dmg, mmove, counter_mmove = await attack()

            decl_msg = await MSG.channel.send(f":crossed_swords: **{t_name}** ⋙ `{' '.join(mmove)}` ⋙ {MSG.author.mention} ")

            # Wait for response moves
            def UCc_check(m):
                return m.author == MSG.author and m.channel == MSG.channel and m.content.startswith('!')
            
            try:
                msg = await self.client.wait_for('message', timeout=t_speed, check=UCc_check)            #timeout=10
                await decl_msg.delete()
            except asyncio.TimeoutError:
                dmgdeal = round(dmg*len(mmove))
                await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                pack_1 = f":dagger: **「`{target_id}` | {t_name}」** ⋙ ***{dmgdeal} DMG*** ⋙ {MSG.author.mention}!"
                pack_2 = await conclusing()
                if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                else: msg_pack = False
                if message_obj: await message_obj.delete()
                await decl_msg.delete()
                return msg_pack

            try: await msg.delete()
            except: pass

            # Fleeing method    |     Success rate base on user's current STA
            if msg.content == '!flee':
                if STA <= 0: rate = MAX_STA//1 + 1
                else: rate = MAX_STA//STA + 1
                # Succesfully --> End battling session
                if random.choice(range(int(rate))) == 0:
                    await MSG.channel.send(f"{MSG.author.mention}, you've successfully escape from the mob!")
                    # Erase the current_enemy lock on off the target_id
                    await self.client._cursor.execute(f"UPDATE personal_info SET cur_MOB='n/a' WHERE id='{user_id}'; UPDATE environ_mob SET lockon='n/a' WHERE mob_id='{target_id}'")
                    return False
                # Fail ---> Continue, with the consequences
                else:
                    dmgdeal = round(dmg*len(mmove))*2
                    await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                    pack_1 = f"\n:dagger::dagger: As **{name}** failed to flee, **「`{target_id}` | {t_name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                    else: msg_pack = False
                    if message_obj: await message_obj.delete()
                    return msg_pack
            # Switching method      |      Switching_range=5m
            elif msg.content.startswith('!switch'):
                # E: No switchee found
                try: switchee = msg.mentions[0]
                except IndexError:
                    dmgdeal = round(dmg*len(mmove))*2
                    await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                    pack_1 = f"\n:dagger::dagger: As **{name}** found no one to switch, **「`{target_id}` | {t_name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                    else: msg_pack = False
                    if message_obj: await message_obj.delete()
                    return msg_pack
                # E: Different region
                try:
                    sw_cur_PLACE, sw_cur_X, sw_cur_Y = await self.client.quefe(f"SELECT cur_PLACE, cur_X, cur_Y FROM personal_info WHERE id='{switchee.id}' AND cur_MOB='n/a'; ")
                    if cur_PLACE != sw_cur_PLACE: 
                        await MSG.channel.send(f"<:osit:544356212846886924> {switchee.mention} and {MSG.author.mention}, you have to be in the same region!")
                        dmgdeal = round(dmg*len(mmove))*2
                        await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                        pack_1 = f"\n:dagger::dagger: As **{name}** failed to switch, **「`{target_id}` | {t_name}」** has dealt a critical DMG of *{dmgdeal}*!"
                        pack_2 = await conclusing()
                        if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                        else: msg_pack = False                       
                        if message_obj: await message_obj.delete()
                        return msg_pack                        
                ## E: Switchee doesn't have ava
                except TypeError:
                    await MSG.channel.send(f"<:osit:544356212846886924> User **{switchee.name}** is busy!")
                    dmgdeal = round(dmg*len(mmove))*2
                    await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                    pack_1 = f"\n:dagger::dagger: As **{name}** tried to switch with a ghost, **「`{target_id}` | {t_name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                    else: msg_pack = False                       
                    if message_obj: await message_obj.delete()
                    return msg_pack                                            
                # E: Out of switching_range
                if await self.utils.distance_tools(cur_X, cur_Y, sw_cur_X, sw_cur_Y) > 5:
                    await MSG.channel.send(f"<:osit:544356212846886924> {switchee.mention} and {MSG.author.mention}, you can only switch within *5 metres*!")
                    dmgdeal = round(dmg*len(mmove))*2
                    await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                    pack_1 = f"\n:dagger::dagger: As **{name}** failed to switch, **「`{target_id}` | {t_name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                    else: msg_pack = False                     
                    if message_obj: await message_obj.delete()
                    return msg_pack

                # Wait for response
                def UC_check2(m):
                    return m.author == switchee and m.channel == MSG.channel and m.mentions


                try: switch_resp = await self.client.wait_for('message', timeout=5, check=UC_check2)
                # E: No response
                except asyncio.TimeoutError:
                    dmgdeal = round(dmg*len(mmove))*2
                    await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                    pack_1 = f"\n:dagger::dagger: As **{name}** failed to switch, **「`{target_id}` | {t_name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                    else: msg_pack = False                     
                    if message_obj: await message_obj.delete()
                    return msg_pack                        
                # E: Wrong user
                if MSG.author not in switch_resp.mentions:
                    dmgdeal = round(dmg*len(mmove))*2
                    await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                    pack_1 = f"\n:dagger::dagger: As **{name}** failed to switch, **「`{target_id}` | {t_name}」** has dealt a critical DMG of *{dmgdeal}*!"
                    pack_2 = await conclusing()
                    if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                    else: msg_pack = False                    
                    if message_obj: await message_obj.delete()
                    return msg_pack                                
                
                # Proceed duo-teleportation
                await self.tools.tele_procedure(cur_PLACE, str(switchee.id), cur_X, cur_Y)
                await self.tools.tele_procedure(cur_PLACE, user_id, sw_cur_X, sw_cur_Y)
                # End the switcher PVE-session
                ## Remove the current_enemy lock-on of the switcher
                await self.client._cursor.execute(f"UPDATE personal_info SET cur_MOB='n/a' WHERE id='{user_id}'; UPDATE environ_mob SET lockon='n/a' WHERE mob_id='{target_id}';")
                # Proceed PVE-session re-focus
                await MSG.channel.send(f":arrows_counterclockwise: {MSG.author.mention} and {switchee.mention}, **SWITCH!!**")
                return [switch_resp, target_id]

                

            # Measuring response moves
            hit_count = 0
            response_content = msg.content[1:]; diff = len(counter_mmove) - len(response_content)      # Measuring the length of the response
            if diff > 0: response_content += '-'*diff                                              # Balancing the length (if needed)
            for move, response_move in zip(counter_mmove, response_content):
                if move != response_move: hit_count += 1
            print(f"HIT COUNT: {hit_count} ----- {response_content} ------ {counter_mmove}")

            # Conduct dealing dmg   |  Conduct dealing STA dmg
            if hit_count == 0:
                dmgdeal = t_str*len(counter_mmove)

                if STA > 0:
                    # Deal
                    if combat_HANDLING == 'both':
                        w_defend = await self.client.quefe(f"SELECT defend FROM pi_inventory WHERE existence='GOOD' AND (item_id='{left_hand}' OR item_code='{left_hand}') AND user_id='{user_id}'"); w_defend = w_defend[0]
                        dmgredu = 100 - w_defend
                    elif combat_HANDLING == 'right':
                        w_defend = await self.client.quefe(f"SELECT defend FROM pi_inventory WHERE existence='GOOD' AND (item_id='{right_hand}' OR item_code='{right_hand}') AND user_id='{user_id}'"); w_defend = w_defend[0]
                        dmgredu = 100 - w_defend*2
                    elif combat_HANDLING == 'left':
                        w_defend = await self.client.quefe(f"SELECT defend FROM pi_inventory WHERE existence='GOOD' AND (item_id='{left_hand}' OR item_code='{left_hand}') AND user_id='{user_id}'"); w_defend = w_defend[0]
                        dmgredu = 100 - w_defend*2
                    # Check STA
                    tem = round(dmgdeal / 100 * dmgredu)
                    if tem > STA:
                        await self.client._cursor.execute(f"UPDATE personal_info SET STA=0 WHERE id='{user_id}';")
                    else: await self.client._cursor.execute(f"UPDATE personal_info SET STA=STA-{tem} WHERE id='{user_id}';")
                
                # Inform
                pack_1 = f"\n:shield: {MSG.author.mention} ⌫ **「`{target_id}`|{t_name}」**"
                pack_2 = await conclusing()
                if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                else: msg_pack = False
                if message_obj: await message_obj.delete()
                return msg_pack

            else:
                dmgdeal = t_str*hit_count 

                # Deal
                if combat_HANDLING == 'both':
                    w_defend = await self.client.quefe(f"SELECT defend FROM pi_inventory WHERE existence='GOOD' AND (item_id='{left_hand}' OR item_code='{left_hand}') AND user_id='{user_id}'"); w_defend = w_defend[0]
                    dmgredu = 200 - w_defend
                elif combat_HANDLING == 'right':
                    w_defend = await self.client.quefe(f"SELECT defend FROM pi_inventory WHERE existence='GOOD' AND (item_id='{right_hand}' OR item_code='{right_hand}') AND user_id='{user_id}'"); w_defend = w_defend[0]
                    dmgredu = 200 - w_defend
                elif combat_HANDLING == 'left':
                    w_defend = await self.client.quefe(f"SELECT defend FROM pi_inventory WHERE existence='GOOD' AND (item_id='{left_hand}' OR item_code='{left_hand}') AND user_id='{user_id}'"); w_defend = w_defend[0]
                    dmgredu = 200 - w_defend

                # Get dmgdeal for informing :>
                dmgdeal = round(dmgdeal / 200 * dmgredu)
                await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}';")

                # Inform
                pack_1 = f"\n:dagger: **「`{target_id}` | {t_name}」** ⋙ *{dmgdeal} DMG* ⋙ **{MSG.author.mention}**"
                pack_2 = await conclusing()
                if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                else: msg_pack = False
                if message_obj: await message_obj.delete()
                return msg_pack

        if target_id != cur_MOB:
            await self.client._cursor.execute(f"UPDATE personal_info SET cur_MOB='{target_id}' WHERE id='{user_id}'; ")

            # Init the fight
            message_obj = await battle(message_obj)
            while isinstance(message_obj, discord.message.Message):
                message_obj = await battle(message_obj)
            print(message_obj)
            if message_obj:
                print("SSSSSSSSSSSSSSSSSSSSSSSSSS")
                await self.PVE(message_obj[0], message_obj[1])
        else:
            await self.client._cursor.execute(f"UPDATE personal_info SET cur_MOB='{target_id}' WHERE id='{user_id}'; ")


    # This function handles the Mob phase
    # Melee PVE     |      Start the mob phase.
    async def PVE_training(self, ctx, dummy_config=['d0', 'Dummy', 10, 1, 6]):

        # GETTING USER's STATS
        name, user_id, combat_HANDLING, right_hand, left_hand, cur_X, cur_Y, cur_PLACE = await self.client.quefe(f"SELECT name, id, combat_HANDLING, right_hand, left_hand, cur_X, cur_Y, cur_PLACE FROM personal_info WHERE id='{ctx.author.id}';")
        streakpoint = 0

        # STANDARD MOB's STATS
        try:
            target_id, t_name, t_speed, t_str, t_chain = dummy_config
            # Set lock-on, as the target is user_id
            #await self.client._cursor.execute(f"UPDATE environ_mob SET lockon='{MSG.author.id}' WHERE mob_id='{target_id}';")
        except TypeError: return

        message_obj = False
        try: await ctx.message.delete()
        except discordErrors.Forbidden: pass

        # ------------ MOB PHASE    |   Mobs attack, user defend
        async def battle(message_obj, streakpoint):

            async def attack():
                mmoves = [random.choice(['a', 'd', 'b']) for move in range(t_chain)]
                
                # Decoding moves, as well as checking the moves. Get the counter_move
                counter_mmove = []
                for move in mmoves:
                    if move == 'a': counter_mmove.append('d')
                    elif move == 'd': counter_mmove.append('b')
                    elif move == 'b': counter_mmove.append('a')

                dmg = t_str
                return dmg, mmoves, counter_mmove

            # ======================================================

            #if not await conclusing(): return False

            dmg, mmove, counter_mmove = await attack()

            decl_msg = await ctx.message.channel.send(f":crossed_swords: **{t_name}** ⋙ `{' '.join(mmove)}` ⋙ {ctx.author.mention} ")

            # Wait for response moves
            def UCc_check(m):
                return m.author == ctx.author and m.channel == ctx.message.channel and m.content.startswith('!')
            
            try:
                msg = await self.client.wait_for('message', timeout=t_speed, check=UCc_check)            #timeout=10
                await decl_msg.delete()
            except asyncio.TimeoutError:
                dmgdeal = round(dmg*len(mmove))
                #await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}'; ")
                pack_1 = f":dagger: **「`{target_id}` | {t_name}」** ⋙ ***{dmgdeal} DMG*** ⋙ {ctx.author.mention}!⠀⠀⠀"
                #pack_2 = await conclusing()
                #if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                #else: msg_pack = False
                msg_pack = await ctx.message.channel.send(f"{pack_1}")
                if message_obj: await message_obj.delete()
                await decl_msg.delete()
                return msg_pack, streakpoint

            try: await msg.delete()
            except: pass

            if msg.content.startswith('!leave'):
                await ctx.send(f":checkered_flag: Training session left.\n|| Streak point: **{streakpoint}**")
                return False, streakpoint

            # Measuring response moves
            hit_count = 0
            response_content = msg.content[1:]; diff = len(counter_mmove) - len(response_content)      # Measuring the length of the response
            if diff > 0: response_content += '-'*diff                                              # Balancing the length (if needed)
            for move, response_move in zip(counter_mmove, response_content):
                if move != response_move: hit_count += 1
            print(f"HIT COUNT: {hit_count} ----- {response_content} ------ {counter_mmove}")

            # Conduct dealing dmg   |  Conduct dealing STA dmg
            if hit_count == 0:
                streakpoint += 1
                dmgdeal = t_str*len(counter_mmove)

                #if STA > 0:
                # Deal
                if combat_HANDLING == 'both':
                    w_defend = await self.client.quefe(f"SELECT defend FROM pi_inventory WHERE existence='GOOD' AND (item_id='{left_hand}' OR item_code='{left_hand}') AND user_id='{user_id}'"); w_defend = w_defend[0]
                    dmgredu = 100 - w_defend
                elif combat_HANDLING == 'right':
                    w_defend = await self.client.quefe(f"SELECT defend FROM pi_inventory WHERE existence='GOOD' AND (item_id='{right_hand}' OR item_code='{right_hand}') AND user_id='{user_id}'"); w_defend = w_defend[0]
                    dmgredu = 100 - w_defend*2
                elif combat_HANDLING == 'left':
                    w_defend = await self.client.quefe(f"SELECT defend FROM pi_inventory WHERE existence='GOOD' AND (item_id='{left_hand}' OR item_code='{left_hand}') AND user_id='{user_id}'"); w_defend = w_defend[0]
                    dmgredu = 100 - w_defend*2
                # Check STA
                #tem = round(dmgdeal / 100 * dmgredu)
                #if tem > STA:
                #    await self.client._cursor.execute(f"UPDATE personal_info SET STA=0 WHERE id='{user_id}';")
                #else: await self.client._cursor.execute(f"UPDATE personal_info SET STA=STA-{tem} WHERE id='{user_id}';")
                
                # Inform
                pack_1 = f"\n**{streakpoint} `SREAK!`**\n:shield: {ctx.author.mention} ⌫ **「`{target_id}`|{t_name}」**"
                #pack_2 = await conclusing()
                #if pack_2: msg_pack = await ctx.message.channel.send(f"{pack_1}\n{pack_2}")
                #else: msg_pack = False
                msg_pack = await ctx.message.channel.send(f"{pack_1}")
                if message_obj: await message_obj.delete()
                return msg_pack, streakpoint

            else:
                streakpoint = 0
                dmgdeal = t_str*hit_count 

                # Deal
                if combat_HANDLING == 'both':
                    w_defend = await self.client.quefe(f"SELECT defend FROM pi_inventory WHERE existence='GOOD' AND (item_id='{left_hand}' OR item_code='{left_hand}') AND user_id='{user_id}'"); w_defend = w_defend[0]
                    dmgredu = 200 - w_defend
                elif combat_HANDLING == 'right':
                    w_defend = await self.client.quefe(f"SELECT defend FROM pi_inventory WHERE existence='GOOD' AND (item_id='{right_hand}' OR item_code='{right_hand}') AND user_id='{user_id}'"); w_defend = w_defend[0]
                    dmgredu = 200 - w_defend
                elif combat_HANDLING == 'left':
                    w_defend = await self.client.quefe(f"SELECT defend FROM pi_inventory WHERE existence='GOOD' AND (item_id='{left_hand}' OR item_code='{left_hand}') AND user_id='{user_id}'"); w_defend = w_defend[0]
                    dmgredu = 200 - w_defend

                # Get dmgdeal for informing :>
                dmgdeal = round(dmgdeal / 200 * dmgredu)
                #await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{user_id}';")

                # Inform
                pack_1 = f"\n**STREAK FAILED**\n:dagger: **「`{target_id}` | {t_name}」** ⋙ *{dmgdeal} DMG* ⋙ **{ctx.author.mention}**"
                #pack_2 = await conclusing()
                #if pack_2: msg_pack = await MSG.channel.send(f"{pack_1}\n{pack_2}")
                #else: msg_pack = False
                msg_pack = await ctx.message.channel.send(f"{pack_1}")
                if message_obj: await message_obj.delete()
                return msg_pack, streakpoint

        #if target_id != cur_MOB:
            #await self.client._cursor.execute(f"UPDATE personal_info SET cur_MOB='{target_id}' WHERE id='{user_id}'; ")

            # Init the fight
        afk_count = 0
        message_obj, tempstreakpoint = await battle(message_obj, streakpoint)
        streakpoint += tempstreakpoint
        while isinstance(message_obj, discord.message.Message):
            message_obj, tempstreakpoint = await battle(message_obj, streakpoint)
            if not tempstreakpoint:
                streakpoint = 0; afk_count += 1
                if afk_count == 5: await ctx.send(f":checkered_flag: Training session ended due to inactivity. \nStreak point : **{streakpoint}**"); return
            else: streakpoint = tempstreakpoint; afk_count = 0
        if message_obj: 
            await self.PVE(message_obj[0], message_obj[1])
        else: pass
            #await self.client._cursor.execute(f"UPDATE personal_info SET cur_MOB='{target_id}' WHERE id='{user_id}'; ")



    # ============= !< BATTLE >! ==================
    # <!> CONCEPTS
    # ---- WEAPON ----
    ### We value a melee mainly by 3 elements: SPEED, MULTIPLIER, STA              
    ### We value a range_weapon mainly by AMMUNITION and 4 elements: RANGE, ACCURACY, FIRE_RATE, STEALTH.
    ### We value a kind of ammunition mainly by 3 elements: SPEED, DMG, MONEY

    # ---- BATTLING ----
    ### A PVE (of all kind of weapons) battle session consists of two phases: 1.User 2.Mob. 
    ### A PVP (of all kind of weapons) battle session consists of one phase only: The user phase, as the attacking side
    ###### A melee PVE will lead to a melee single-phase or multi-phase battle
    ###### A range_weapon PVE will (maybe, eventually) lead to a melee single-phase or multi-phase battle


    # This function/command handles the User's MELEE phase
    # Melee PVE |      Start the USER MELEE phase.     |          Melee PVP |       Start the USER MELEE attacking phase.
    @commands.command(pass_context=True, aliases=['atk'])
    @commands.cooldown(1, 3, type=BucketType.user)
    async def attack(self, ctx, *args):
        """ -avaattack [moves] [target]
            -avaattack [moves]              
            <!> ONE target of each creature type at a time. Mobs always come first, then user. Therefore you can't fight an user while fighting a mob
            <!> DO NOT lock on current_enemy at the beginning. Do it at the end."""
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        raw = list(args); __mode = 'PVP'

        # HANDLING CHECK =====================================
        try:
            note = {'both': '<:right_hand:521197677346553861><:left_hand:521197732162043922>', 'right': '<:right_hand:521197677346553861>', 'left': '<:left_hand:521197732162043922>'}

            await ctx.send(f'{note[raw[0]]} Changed to **{raw[0].upper()} hand** pose')
            await self.client._cursor.execute(f"UPDATE personal_info SET combat_HANDLING='{raw[0].lower()}' WHERE id='{str(ctx.message.author.id)}';"); return
        # E: Pose not given
        except IndexError: await ctx.send(f"<:osit:544356212846886924> **{ctx.message.author.name}**, missing arguments!"); return
        # E: Moves given, not pose
        except KeyError: pass

        # Get main_weapon, handling     |      as well as checking coord
        try: combat_HANDLING, main_weapon = await self.client.quefe(f"SELECT combat_HANDLING, IF(combat_HANDLING IN ('both', 'right'), right_hand, left_hand) FROM personal_info WHERE id='{str(ctx.message.author.id)}' AND cur_X>1 AND cur_Y>1;")
        # E: User in PB
        except TypeError: await ctx.send("<:osit:544356212846886924> You can't fight inside **Peace Belt**!"); return

        # Check if it's a PVP or PVE call
        # Then get the target (Mob/User)

        # Get user's info (always put last, for the sake of efficience)
        name, cur_MOB, cur_PLACE, cur_X, cur_Y, STA, STR = await self.client.quefe(f"SELECT name, cur_MOB, cur_PLACE, cur_X, cur_Y, STA, STR FROM personal_info WHERE id='{str(ctx.message.author.id)}';")


        # INPUT CHECK =========================================
        target = None; target_id = None; raw_move = None

        for copo in raw:
            # PVP   |    USING MENTION
            if copo.startswith('<@'):
                target = ctx.message.mentions[0]; target_id = str(target.id)
                __bmode = 'DIRECT'

            # PVE   |    USING MOB'S ID
            elif copo.startswith('mob.') or copo.startswith('boss'):
                # If there's no current_enemy   |   # If there is, and the target is the current_enemy
                if cur_MOB == 'n/a' or copo == cur_MOB:
                    if copo == 'boss': 
                        target = await self.client.quefe(f"SELECT mob_id FROM environ_mob WHERE branch='boss' AND region='{cur_PLACE}';"); target = target[0]; __mode = 'PVE'; target_id = target
                    else: target = copo; __mode = 'PVE'; target_id = target
                # If there is, but the target IS NOT the current_enemy
                elif copo != cur_MOB:
                    await ctx.send(f"<:osit:544356212846886924> Please finish your current fight with the `{cur_MOB}`!"); return



            # PVP   |    USING USER'S ID
            else:
                try:
                    try: 
                        target = await self.client.get_user(int(copo))
                        if not target: await ctx.send("<:osit:544356212846886924> User's not found"); return
                        target_id = target.id
                    except (discordErrors.NotFound, discordErrors.HTTPException, TypeError): await ctx.send("<:osit:544356212846886924> Invalid user's id!"); return
                    __bmode = 'INDIRECT'
                # MOVES     |      acabcbabbba
                except ValueError: 
                    raw_move = copo

        # In case target is not given, current_enemy is used
        if not target:
            # Mobs first. If there's no mob in current_enemy, then randomly pick one
            if cur_MOB == 'n/a':
                target = random.choice(await self.client.quefe(f"SELECT mob_id FROM environ_mob WHERE region='{cur_PLACE}';", type='all'))[0]
                target_id = target
                __mode = 'PVE'
            else:
                target = cur_MOB
                target_id = target
                __mode = 'PVE'
        
        if not raw_move: raw_move = random.choice(['a', 'b', 'd'])           #await ctx.send(f"<:osit:544356212846886924> Please make your move!"); return


        # TARGET CHECK =========================================

        if __mode == 'PVP': 
            # Check if target has a ava     |      GET TARGET's INFO
            try: t_cur_X, t_cur_Y, t_cur_PLACE = await self.client.quefe(f"SELECT cur_X, cur_Y, cur_PLACE FROM personal_info WHERE id='{target_id}' AND cur_PLACE='{cur_PLACE}';")
            # E: Invalid target, or target's not in the same region
            except TypeError:
                await ctx.send("<:osit:544356212846886924> Target don't have an ava, or you and the target are not in the same region!"); return t_cur_X, t_cur_Y, t_cur_PLACE

        elif __mode == 'PVE':
            # Check if target is a valid mob       |       GET TARGET's INFO
            try: t_Ax, t_Ay, t_Bx, t_By, t_name = await self.client.quefe(f"SELECT limit_Ax, limit_Ay, limit_Bx, limit_By, name FROM environ_MOB WHERE mob_id='{target_id}' AND region='{cur_PLACE}';")
            # E: Invalid target, or target's not in the same region
            except TypeError: await ctx.send(f"<:osit:544356212846886924> There is no `{target_id}` around! Perhap you should check your surrounding..."); return

            # Check if the user is in the mob's diversity
            if cur_X < t_Ax or cur_Y < t_Ay or cur_X > t_Bx or cur_Y > t_By:
                print(cur_X, cur_Y)
                print(t_Ax, t_Ay, t_Bx, t_By, t_name)
                await ctx.send(f"<:osit:544356212846886924> **{ctx.message.author.name}**, you can't engage the mob from your current location!"); return


        # WEAPON CHECK ==========================

        # Get weapon info
        try: w_multiplier, w_sta, w_speed = await self.client.quefe(f"SELECT multiplier, sta, speed FROM pi_inventory WHERE existence='GOOD' AND item_id='{main_weapon}';")
        # E: main_weapon is a item_code (e.g. ar13)
        except TypeError: w_multiplier, w_sta, w_speed = await self.client.quefe(f"SELECT multiplier, sta, speed FROM pi_inventory WHERE existence='GOOD' AND item_code='{main_weapon}' and user_id='{ctx.author.id}';")

        # STA filter
        if len(raw_move)*w_sta <= STA:
            if w_sta >= 100: await self.client._cursor.execute(f"UPDATE personal_info SET STA=STA-2 WHERE id='{str(ctx.message.author.id)}';")
            else: await self.client._cursor.execute(f"UPDATE personal_info SET STA=STA-1 WHERE id='{str(ctx.message.author.id)}';")
        else: await ctx.send(f"<:osit:544356212846886924> {ctx.author.mention}, out of `STA`!"); return

        # Checking the length of moves
        moves_to_check = await self.client.quefe(f"SELECT value FROM pi_arts WHERE user_id='{str(ctx.message.author.id)}' AND art_type='sword' AND art_name='chain_attack';")
        if len(raw_move) > moves_to_check[0]:
            await ctx.send(f"<:osit:544356212846886924> You cannot perform a `{len(raw_move)}-chain` attack, **{ctx.message.author.name}**!"); return

        # NOW THE FUN BEGIN =========================================

        counter_move = []

        # Decoding moves, as well as checking the moves. Get the counter_move
        for move in raw_move:
            if move == 'a': counter_move.append('d')
            elif move == 'd': counter_move.append('b')
            elif move == 'b': counter_move.append('a')
            else: await ctx.send(f"<:osit:544356212846886924> Invalid move! (move no. `{raw_move.index(move) + 1}` -> `{move}`)"); return
        
        # PVP use target, with personal_info =============================
        async def PVP():
            # If the duo share the same server, send msg to that server. If not, DM the attacked
            if __bmode == 'DIRECT': inbox = ctx.message
            else: inbox = await target.send(ctx.message.content)

            await inbox.add_reaction('\U00002694')

            radial = 20             # Take attacker as the middle
            # GET TARGET's INFO the second time
            try: t_name, t_right_hand, t_left_hand, t_combat_HANDLING, t_STA = await self.client.quefe(f"SELECT name, right_hand, left_hand, combat_HANDLING, STA FROM personal_info WHERE id='{target_id}' AND cur_PLACE='{cur_PLACE}' AND cur_X-{radial}<={cur_X} AND {cur_X}<=cur_X+{radial} AND cur_Y-{radial}<={cur_Y} AND {cur_Y}<=cur_Y+{radial};")
            except TypeError: await inbox.channel.send(f"<:osit:544356212846886924> Unable to find the target within 20m radius, {inbox.author.mention}!"); return

            # Wait for move recognition     |      The more STA consumed, the less time you have to recognize moves. Therefore, if you attack too many times, you'll be more vulnerable
            # RECOG is based on opponent's STA     |      RECOG = oppo's STA / 30
            RECOG = t_STA / 30

            # If the attack is INDIRECT, multiple RECOG by 5
            if __bmode == 'INDIRECT': RECOG = RECOG*5

            def RUM_check(reaction, user):
                return user == target and reaction.message.id == inbox.id and str(reaction.emoji) == '\U00002694'

            if RECOG < 1: RECOG = 1
            try: await self.client.wait_for('reaction_add', check=RUM_check, timeout=RECOG)
            except asyncio.TimeoutError:
                dmgdeal = round(STR*w_multiplier*len(counter_move))
                await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{target_id}';")
                await ctx.send(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{t_name}**"); return


            # Wait for response moves       |        SPEED ('speed') of the sword
            SPEED = w_speed

            def UCc_check(m):
                return m.author == target and m.channel == inbox.channel and m.content.startswith('!')

            try: msg = await self.client.wait_for('message', timeout=SPEED, check=UCc_check)
            except asyncio.TimeoutError:
                dmgdeal = round(STR*w_multiplier*len(counter_move))
                await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{target_id}';")
                await ctx.send(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{target.name}**"); return
            
            # Measuring response moves
            hit_count = 0
            response_content = msg.content[1:]; diff = len(counter_move) - len(response_content)      # Measuring the length of the response
            if diff > 0: response_content += '-'*diff
            for move, response_move in zip(counter_move, response_content):
                if move != response_move: hit_count += 1

            # Conduct dealing dmg   |  Conduct dealing STA dmg
            if hit_count == 0:
                await ctx.send(f"\n:shield: **{target.mention}** ⌫ **{name}**")

                # Recalculate the dmg, since hit_count == 0                
                ## Player's dmg
                if combat_HANDLING == 'both':
                    dmgdeal = round(STR*w_multiplier*len(counter_move))
                elif combat_HANDLING in ['right', 'left']:
                    dmgdeal = round(STR*w_multiplier*len(counter_move))*2
                ## Opponent's def
                if t_combat_HANDLING == 'both':
                    try:
                        tw_defend, tw_multiplier = await self.client.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND (item_code='{t_left_hand}' OR item_id='{t_left_hand}') AND user_id='{target_id}'")
                        dmgredu = 100 - tw_defend
                    except KeyError: dmgredu = 100    
                elif t_combat_HANDLING == 'right':
                    try:
                        tw_defend, tw_multiplier = await self.client.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND (item_code='{t_right_hand}' OR item_id='{t_right_hand}') AND user_id='{target_id}'")
                        dmgredu = 100 - tw_defend*2
                    except KeyError: dmgredu = 100
                elif t_combat_HANDLING == 'left':
                    try:
                        tw_defend, tw_multiplier = await self.client.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND (item_code='{t_left_hand}' OR item_id='{t_left_hand}') AND user_id='{target_id}'")
                        dmgredu = 100 - tw_defend*2
                    except KeyError: dmgredu = 100
                
                # If dmgredu > 0, backfire the attacker. If dmgredu >= 0, all dmg are neutralized
                temp_query = ''
                if dmgredu > 0:
                    temp_query += f"UPDATE personal_info SET STA=STA-{round(dmgdeal / 100 * abs(dmgredu))*tw_multiplier} WHERE id='{str(ctx.message.author.id)}'; "
                    dmgredu = 0

                temp_query += f"UPDATE personal_info SET STA=STA-{round(dmgdeal / 100 * dmgredu)} WHERE id='{target_id}'; "
                await self.client._cursor.execute(temp_query)

            else:

                # Recalculate the dmg             
                ## Player's dmg
                if combat_HANDLING == 'both':
                    dmgdeal = round(STR*w_multiplier*hit_count)
                elif combat_HANDLING in ['right', 'left']:
                    dmgdeal = round(STR*w_multiplier*hit_count)*2
                ## Opponent's def
                if t_combat_HANDLING == 'both':
                    tw_defend, tw_multiplier = await self.client.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_left_hand}' AND user_id='{target_id}'")
                    dmgredu = 200 - tw_defend
                elif t_combat_HANDLING == 'right':
                    tw_defend, tw_multiplier = await self.client.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_right_hand}' AND user_id='{target_id}'")
                    dmgredu = 200 - tw_defend*2
                elif t_combat_HANDLING == 'left':
                    tw_defend, tw_multiplier = await self.client.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_left_hand}' AND user_id='{target_id}'")
                    dmgredu = 200 - tw_defend*2

                # If dmgredu > 0, backfire the attacker. If dmgredu >= 0, all dmg are neutralized
                temp_query = ''
                if dmgredu < 0:
                    temp_query += f"UPDATE personal_info SET STA=STA-{round(dmgdeal / 200 * abs(dmgredu))*tw_multiplier} WHERE id='{str(ctx.message.author.id)}'; "
                    dmgredu = 0

                # Get dmgdeal (don't combine, for informing :>)
                dmgdeal = round(dmgdeal / 200 * dmgredu)
                temp_query += f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{target_id}'; "
                await self.client._cursor.execute(temp_query)

                await ctx.send(f":dagger: **{ctx.message.author.name}** has dealt *{dmgdeal} DMG* to **{t_name}**")
        
            await self.tools.ava_scan(ctx.message, 'life_check')

        # PVE use target_id, with environ_mob ======================
        if __mode == 'PVE':
            # ------------ USER PHASE   |   User deal DMG 
            my_dmgdeal = round(STR*w_multiplier*len(counter_move))
            # Inform, of course :>
            await self.client._cursor.execute(f"UPDATE environ_mob SET lp=lp-{my_dmgdeal} WHERE mob_id='{target_id}'; ")
            await ctx.send(f":dagger: **{name}** has dealt *{my_dmgdeal} DMG* to **「`{target_id}` | {t_name}」**!", delete_after=8)

        if __mode == 'PVP':
            await PVP()
        elif __mode == 'PVE':
            await self.PVE(ctx.message, target_id)
        else: print("<<<<< OH SHIET >>>>>>>")

    @commands.command()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def aim(self, ctx, *args):
        # >Aim <coord_X> <coord_Y> <shots(optional)>      |      >Aim <@user/mob_name> <shots(optional)>       |          >Aim (defaul - shot=1)
        if not await self.tools.ava_scan(ctx.message, type='life_check'): return

        # HANDLING CHECK =====================================
        raw = list(args)
        try:
            note = {'both': '<:right_hand:521197677346553861><:left_hand:521197732162043922>', 'right': '<:right_hand:521197677346553861>', 'left': '<:left_hand:521197732162043922>'}

            await ctx.send(f'{note[raw[0]]} Changed to **{raw[0].upper()} hand** pose')
            await self.client._cursor.execute(f"UPDATE personal_info SET combat_HANDLING='{raw[0].lower()}' WHERE id='{str(ctx.message.author.id)}';"); return
        # E: Pose not given
        except IndexError: await ctx.send(f"<:osit:544356212846886924> **{ctx.message.author.name}**, please make your moves!"); return
        # E: Moves given, not pose
        except KeyError: pass


        # USER's INFO get ===================================================
        __mode = 'PVP'
        shots = 1

        # Get info     |      as well as checking coord
        try: user_id, name, cur_PLACE, cur_X, cur_Y, cur_MOB, main_weapon, combat_HANDLING, STA, LP = await self.client.quefe(f"SELECT id, name, cur_PLACE, cur_X, cur_Y, cur_MOB, IF(combat_HANDLING IN ('both', 'right'), right_hand, left_hand), combat_HANDLING, STA, LP FROM personal_info WHERE id='{str(ctx.message.author.id)}' AND cur_X>1 AND cur_Y>1;")
        # E: User in PB
        except TypeError: await ctx.send("<:osit:544356212846886924> You can't fight inside **Peace Belt**!"); return


        # INPUT ===============================================================

        # Get weapon's info
        w_round, w_firing_rate, w_sta, w_rmin, w_rmax, w_accu_randomness, w_accu_range, w_stealth, w_aura, w_multiplier, w_tags = await self.client.quefe(f"SELECT round, firing_rate, sta, range_min, range_max, accuracy_randomness, accuracy_range, stealth, aura, multiplier, tags FROM pi_inventory WHERE existence='GOOD' AND item_id='{main_weapon}';")
        w_tags = w_tags.split(' - ')
        if 'magic' in w_tags: _style = 'MAGIC'
        else: _style = 'PHYSIC'

        ### ALL ELEMENT GET     (target, coord, shots) 
        try:
            target = ''
            print("HEH")
            # @User, shots provided
            if raw[0].startswith('<@'):
                print("JUST HERE")
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

            else: await ctx.send("<:osit:544356212846886924> Please use 5-digit or lower coordinates!")       

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

        # ... or none of them, then we should randomly pick one :v        
        except IndexError:
            print("HER HERE")
            # Mobs first. If there's no mob in cur_MOB, then randomly pick one
            if cur_MOB == 'n/a':
                target_id = random.choice(await self.client.quefe(f"SELECT mob_id FROM environ_mob WHERE limit_Ax<{cur_X}<limit_Bx  AND limit_Ay<{cur_Y}<limit_By AND region='{cur_PLACE}';", type='all'))
                target_id = target_id[0]
                target = target_id
                __mode = 'PVE'
            # If there is, use cur_MOB
            else:
                target_id = cur_MOB
                target = target_id
                __mode = 'PVE'     

            if _style == 'PHYSIC':
                # Get shots (if available and possible)
                try: shots = int(raw[0])
                except (IndexError, TypeError): pass
         


        # TARGET CHECK =========================================================
        # (as well as init some variables)

        # Check if target has a ava
        if __mode == 'PVP': 
            # Check if target has a ava     |      GET TARGET's INFO
            try: t_cur_X, t_cur_Y, t_cur_PLACE, t_combat_HANDLING, t_right_hand, t_left_hand = await self.client.quefe(f"SELECT cur_X, cur_Y, cur_PLACE, combat_HANDLING, right_hand, left_hand FROM personal_info WHERE id='{target_id}' AND cur_PLACE='{cur_PLACE}';")
            # E: Invalid target, or target's not in the same region
            except TypeError:
                await ctx.send("<:osit:544356212846886924> Target don't have an ava, or you and the target are not in the same region!"); return

        elif __mode == 'PVE':
            # Check if target is a valid mob       |       GET TARGET's INFO
            try: t_Ax, t_Ay, t_Bx, t_By, t_name = await self.client.quefe(f"SELECT limit_Ax, limit_Ay, limit_Bx, limit_By, name FROM environ_MOB WHERE mob_id='{target_id}' AND region='{cur_PLACE}';")
            # E: Invalid target, or target's not in the same region
            except TypeError: await ctx.send(f"<:osit:544356212846886924> There is no `{target_id}` around! Perhap you should check your surrounding..."); return

            # Check if the user is in the mob's diversity
            if cur_X < t_Ax or cur_Y < t_Ay or cur_X > t_Bx or cur_Y > t_By:
                print(t_Ax, t_Ay, t_Bx, t_By, t_name)
                await ctx.send(f"<:osit:544356212846886924> **{ctx.message.author.name}**, you can't engage the mob from your current location!"); return


        # WEAPON CHECK ===========================================================

        # Distance get/check
        if __mode == 'PVP': 
            distance = await self.utils.distance_tools(cur_X, cur_Y, t_cur_X, t_cur_Y)
            if distance > w_rmax or distance < w_rmin: await ctx.send(f"<:osit:544356212846886924> **{ctx.message.author.name}**, the target is out of your weapon's range!"); return
        elif __mode == 'PVE':
            distance = 1                    # There is NO distance in a PVE battle, therefore the accuracy will always be at its lowest

        # AMMUNITION
        if shots > w_firing_rate: await ctx.send(f"<:osit:544356212846886924> **{ctx.message.author.name}**, your weapon cannot perform `{shots}` shots in a row!"); return
        
        # Get ammu's info
        try:
            a_name, a_tags, a_speed, a_rlquery, a_dmg, a_quantity = await self.client.quefe(f"SELECT name, tags, speed, reload_query, dmg, quantity FROM pi_inventory WHERE existence='GOOD' AND item_code='{w_round}' AND user_id='{user_id}';")
            a_tags = a_tags.split(' - ')
        # E: Ammu not found --> Unpack error
        except TypeError: 
            if w_round not in ['am5', 'am6'] :
                a_name = await self.client.quefe(f"SELECT name FROM model_item WHERE item_code='{w_round}';")
                await ctx.send(f"<:osit:544356212846886924> {ctx.message.author.mention}, OUT OF `{w_round} | {a_name}`!"); return
            else:
                a_name, a_tags, a_speed, a_rlquery, a_dmg = await self.client.quefe(f"SELECT name, tags, speed, reload_query, dmg FROM model_item WHERE item_code='{w_round}';")


        # Check shots VS quantity of the ammu_type. RELOAD.
        # MAGIC
        if w_round == 'am5':                    # LP -------------------- If kamikaze, halt them
            if LP <= shots*amount:
                await ctx.send(f"<:osit:544356212846886924> **{ctx.message.author.name}**, please don't kill yourself..."); return
            else:
                a_rlquery = a_rlquery.replace('quantity_here', str(shots*amount)).replace('user_id_here', user_id)
                await self.client._cursor.execute(a_rlquery)
        elif w_round == 'am6':                  # STA -------------------- If kamikaze, take the rest of the STA, split it into shots. Then decrease STA
            if STA <= shots*amount:
                amount = STA//shots
                a_rlquery = a_rlquery.replace('quantity_here', str(shots*amount)).replace('user_id_here', user_id)
                await self.client._cursor.execute(a_rlquery)
            else:
                a_rlquery = a_rlquery.replace('quantity_here', str(shots*amount)).replace('user_id_here', user_id)
                await self.client._cursor.execute(a_rlquery)            
        # PHYSIC
        else:
            if a_quantity <= shots:
                shots = a_quantity
                await self.client._cursor.execute(f"UPDATE pi_inventory SET existence='BAD' WHERE item_code='{w_round}' AND user_id='{user_id}';")
            else:
                a_rlquery = a_rlquery.replace('quantity_here', str(shots)).replace('user_id_here', user_id)
                await self.client._cursor.execute(a_rlquery)

        # Filtering shots bases on STA remaining. If using physical, STA's decreased        |          No filtering, while using magic. STA's NOT decreased (for using weapon).
        if _style == 'PHYSIC':
            if shots*w_sta < STA:
                if w_sta >= 100:
                    await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-20 WHERE id='{user_id}';")
                else: 
                    await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-10 WHERE id='{user_id}';")
            else:
                shots = STA//w_sta

        
        # PREPARING !!! =======================================================
        # Re-calc randomness
        if combat_HANDLING != 'both':
            w_accu_randomness = w_accu_randomness//2

        # Filtering shots
        bingos = 0
        for i in range(shots):
            if distance < w_accu_range:
                if random.choice(range(w_accu_randomness)) == 0: bingos += 1
            else:
                if random.choice(range(w_accu_randomness*(distance / w_accu_range))) == 0: bingos += 1
        print(f"BINGO: {bingos}")
        shots = bingos
        if shots == 0: 
            await ctx.send(f":interrobang: {ctx.message.author.mention}, you shot a lot but hit nothing...")
            if __bmode == 'INDIRECT': await target.send(f":sos: **Someone** is trying to hurt you, {target.mention}!")
            return

        #dmgdeal = ammu['dmg']*shots

        # PVP use target, with ava_dict =================================
        async def PVP():
            # PVE() already has a deletion. Please don't put this else where
            try: await ctx.message.delete()
            except discordErrors.Forbidden: pass

            if distance < 100: a = 1
            else: a = distance/100
            
            # MAGIC
            if _style == 'MAGIC':
                verb = 'curse'
                field = '⠀'*int(shots)*w_stealth*int(a)        # <--- Braille white-space

                for shot in range(shots):
                    while True:
                        hole = random.choice(range(len(field)))
                        if field[hole] == '⠀': break
                    
                    if hole != 0:
                        field = field[:hole] + '·' + field[(hole + 1):]   # OOOOOOOOOOOOO
                    elif hole == len(field):
                        field = field[:hole] + '·'
                    else:
                        field = '·' + field[(hole + 1):]
            # PHYSICAL
            else:
                verb = 'shoot'
                field = '0'*int(shots)*w_stealth*int(a)
                counter_shot = []

                for shot in range(shots):
                    while True:
                        hole = random.choice(range(len(field)))
                        if field[hole] == 'O': break
                    counter_shot.append(str(hole)[-1])
                    
                    if hole != 0:
                        field = field[:hole] + '0' + field[(hole + 1):]   # OOOOOOOOOOOOO
                    elif hole == len(field):
                        field = field[:hole] + '0'
                    else:
                        field = '0' + field[(hole + 1):]


            # Depend on the distance, make the shooter anonymous
            if distance <= 1000: shooter = ctx.message.author.name
            else: shooter = 'Someone'

            # Check if the attack is DIRECT. If not, DM the attacked
            if __bmode == 'DIRECT': 
                inbox = await ctx.send(f""":sos: **{shooter}** is trying to *{verb}* you, {target.mention}!```css
{field}```""")
            else: 
                inbox = await target.send(f""":sos: **{shooter}** is trying to *{verb}* you, {target.mention}!```css
{field}```""")

            # MAGIC
            if _style == 'MAGIC':
                # Generate model moves
                model_moves = field.replace('⠀', '0').replace('·', '1')

                # Wait for response moves       |        SPEED ('speed') of the bullet aka. <ammu>
                def UCc_check(m):
                    return m.author == target and m.channel == inbox.channel and m.content == f"!{model_moves}"
                
                SPEED = a_speed
                # If the attack is INDIRECT, multiple RECOG by 5
                if __bmode == 'INDIRECT': SPEED = SPEED*5
                try: msg = await self.client.wait_for('message', timeout=SPEED, check=UCc_check)
                except asyncio.TimeoutError:
                    dmgdeal = a_dmg*shots*amount

                    # AURA comes in
                    aura_dict = {'FLAME': 'au_FLAME', 'ICE': 'au_ICE', 'DARK': 'au_DARK', 'HOLY': 'au_HOLY'}
                    aura = await self.client.quefe(f"SELECT {aura_dict[w_aura]} FROM personal_info WHERE id='{user_id}';")
                    t_aura = await self.client.quefe(f"SELECT {aura_dict[w_aura]} FROM personal_info WHERE id='{target_id}';")
                    # Re-calc dmgdeal
                    try: dmgdeal = int(dmgdeal*t_aura[0]/aura[0])
                    except ZeroDivisionError: dmgdeal = int(dmgdeal*t_aura)

                    await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{target_id}';")
                    await ctx.send(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{t_name}**")
                    if __bmode == 'INDIRECT': await target.send(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{t_name}**")
                    return
                else:
                    await ctx.send(f"\n--------------------\n:shield: **{target.mention}** has successfully *neutralized* all **{name}**'s spells!")
                    if __bmode == 'INDIRECT': await target.send(f"\n--------------------\n:shield: **{target.mention}** has successfully *neutralized* all **{name}**'s spells!")
                    return
            
                await self.tools.ava_scan(ctx.message, 'life_check')

            # PHYSICAL
            else:
                # Wait for response moves       |        SPEED ('speed') of the bullet aka. <ammu>
                def UC_check(m):
                    return m.author == target and m.channel == inbox.channel and m.content.startswith('!')
                
                SPEED = a_speed
                # If the attack is INDIRECT, multiple RECOG by 5
                if __bmode == 'INDIRECT': SPEED = SPEED*5
                try: msg = await self.client.wait_for('message', timeout=SPEED, check=UC_check)
                except asyncio.TimeoutError:
                    dmgdeal = a_dmg*shots
                    await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{target_id}';")
                    await ctx.send(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{t_name}**")
                    if __bmode == 'INDIRECT': await target.send(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{t_name}**")
                    return

                # Measuring response moves
                hit_count = 0
                response_content = msg.content[1:]              # Measuring the length of the response
                # Fixing the length of response_content
                response_content = response_content + 'o'*(len(counter_shot) - len(response_content))

                # HIT COUNTER
                for shot, resp in zip(counter_shot, response_content):
                    if shot != resp: hit_count += 1

                # Conduct dealing dmg   |  Conduct dealing STA dmg
                dmgdeal = a_dmg*hit_count
                if hit_count == 0:
                    await ctx.send(f"\n:shield: **{target.mention}** ⌫ **{name}**")
                    if __bmode == 'INDIRECT': await target.send(f"\n:shield: **{target.mention}** ⌫ **{name}**")

                    # Recalculate the dmg, since hit_count == 0                
                    ## Player's dmg
                    dmgdeal = round(a_dmg*len(counter_shot))
                    ## Opponent's def
                    if t_combat_HANDLING == 'both':
                        tw_defend, tw_multiplier = await self.client.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_left_hand}' AND user_id='{target_id}'")
                        dmgredu = 100 - tw_defend
                    elif t_combat_HANDLING == 'right':
                        tw_defend, tw_multiplier = await self.client.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_right_hand}' AND user_id='{target_id}'")
                        dmgredu = 100 - tw_defend*2
                    elif t_combat_HANDLING == 'left':
                        tw_defend, tw_multiplier = await self.client.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_left_hand}' AND user_id='{target_id}'")
                        dmgredu = 100 - tw_defend*2                    
                    # If dmgredu >= 0, all dmg are neutralized
                    if dmgredu < 0:
                        dmgredu = 0

                    await self.client._cursor.execute(f"UPDATE personal_info SET STA=STA-{round(dmgdeal / 100 * dmgredu)} WHERE id='{target_id}';")
                else:
                    # Recalculate the dmg             
                    ## Player's dmg
                    dmgdeal = round(a_dmg*hit_count)
                    ## Opponent's def
                    if t_combat_HANDLING == 'both':
                        try:
                            tw_defend, tw_multiplier = await self.client.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_left_hand}' AND user_id='{target_id}'")
                            dmgredu = 200 - tw_defend
                        except KeyError: dmgredu = 200
                    elif t_combat_HANDLING == 'right':
                        try:
                            tw_defend, tw_multiplier = await self.client.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_left_hand}' AND user_id='{target_id}'")
                            dmgredu = 200 - tw_defend*2
                        except KeyError: dmgredu = 200
                    elif t_combat_HANDLING == 'left':
                        try:
                            tw_defend, tw_multiplier = await self.client.quefe(f"SELECT defend, multiplier FROM pi_inventory WHERE existence='GOOD' AND item_id='{t_left_hand}' AND user_id='{target_id}'")
                            dmgredu = 200 - tw_defend*2
                        except KeyError: dmgredu = 200

                    # If dmgredu > 0, backfire the attacker. If dmgredu >= 0, all dmg are neutralized
                    if dmgredu < 0:
                        await self.client._cursor.execute(f"UPDATE personal_info SET STA=STA-{round(dmgdeal / 200 * abs(dmgredu))*tw_multiplier} WHERE id='{user_id}';")
                        dmgredu = 0

                    # Get dmgdeal, for informing :>
                    dmgdeal = round(dmgdeal / 200 * dmgredu)
                    await self.client._cursor.execute(f"UPDATE personal_info SET LP=LP-{dmgdeal} WHERE id='{target_id}';")

                    await ctx.send(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{t_name}**")
                    if __bmode == 'INDIRECT': await target.send(f":dagger: **{name}** has dealt *{dmgdeal} DMG* to **{t_name}**")
            
                await self.tools.ava_scan(ctx.message, 'life_check')

        # PVE use target_id, with environ_mob ============================
        async def first_PVE():
            if _style == 'PHYSIC':
                # ------------ USER PHASE   |   User deal DMG 
                my_dmgdeal = round(a_dmg*len(shots))
                # Inform, of course :>
                await self.client._cursor.execute(f"UPDATE environ_mob SET lp=lp-{my_dmgdeal} WHERE mob_id='{target_id}'; ")
                await ctx.send(f":dagger: **{name}** ⋙ *{my_dmgdeal} DMG* ⋙ **「`{target_id}` | {t_name}」**!")
            elif _style == 'MAGIC':
                my_dmgdeal = a_dmg*shots*amount

                # AURA comes in
                aura_dict = {'FLAME': 'au_FLAME', 'ICE': 'au_ICE', 'DARK': 'au_DARK', 'HOLY': 'au_HOLY'}
                aura = await self.client.quefe(f"SELECT {aura_dict[w_aura]} FROM personal_info WHERE id='{user_id}';")
                t_aura = await self.client.quefe(f"SELECT {aura_dict[w_aura]} FROM environ_mob WHERE mob_id='{target_id}';")
                # Re-calc dmgdeal
                try: dmgdeal = int(my_dmgdeal*t_aura[0]/aura[0])
                except ZeroDivisionError: dmgdeal = int(my_dmgdeal*t_aura[0])

                # Inform, of course :>
                await self.client._cursor.execute(f"UPDATE environ_mob SET lp=lp-{dmgdeal} WHERE mob_id='{target_id}'; ")
                await ctx.send(f":dagger: **{name}** ⋙ *{dmgdeal} DMG* ⋙ **「`{target_id}` | {t_name}」**!")


        if __mode == 'PVP':
            await PVP()
        elif __mode == 'PVE':
            await first_PVE()
            await self.PVE(ctx.message, target_id)
        else: print("<<<<< OH SHIET >>>>>>>")



def setup(client):
    client.add_cog(avaCombat(client))


