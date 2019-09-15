import discord
from discord.ext import commands
import discord.errors as discordErrors

import operator
import random
import asyncio

class tictactoe(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.ticks = []
        self.cord = []; self.collu = []
        self.slot_char = '--'

    def sequantumize(self, seq_socket, type):

        sequantum_socket = []
        # Make a copy (for filtering purpose)
        temp_socket2 = seq_socket
        # Filter the COPY
        for seq in seq_socket:
            for i in range(temp_socket2.count(seq) - 1):
                temp_socket2.remove(seq)
        # Pass the filtered COPY back to <seq_socket>
        seq_socket = temp_socket2
        
        # Transforming from seqs of <ticker> into <sequantum>, put it into <sequantum> socket
        for seq in seq_socket:
            # Ghost filtering
            ghosted_ticks = list([tick for tick in seq if tick.ghosted])
            # If ghosted
            if ghosted_ticks: sequantum_socket.append(sequantum(seq, type, ghosted=True, ghost_ticks=ghosted_ticks))
            # Else
            else: sequantum_socket.append(sequantum(seq, type))
        # Make a copy of the <tick>, remove duplicants and ITSELF in the socket,
        # make the copy into a <sequantum> obj, then put back to the socket
        # Return <sequantum>  socket
        return sequantum_socket   

    @commands.command(aliases=['ttt'])
    async def tictactoe(self, ctx, *args):
        border = "**0**     **1**     **2**     **3**     **4**     **5**    **6**     **7**     **8**    **9**\n===========================\n"
        table = border; iC = 0 
        winning_condition = False
        delay = 50
        raw = list(args)
        size_X = 10; size_Y = 10
        try:
            for i in raw:
                if i.startswith('delay='):
                    a = i.split('=')
                    delay = int(a[1])
                elif i.startswith('X='):
                    a = i.split('=')
                    size_X = int(a[1])
                elif i.startswith('Y='):
                    a = i.split('=')
                    size_Y = int(a[1])
        except: pass

        async def clean_up():
            self.cord = []; self.collu = []; self.ticks = []

        for i in range(size_X):
            for o in range(size_Y):
                self.collu.append(self.slot_char)
            self.cord.append(self.collu)
            self.collu = []
        for collumn in self.cord: table = table + '    '.join(collumn) +  f"  |  **{iC}** " + '\n'; iC += 1
        msg = await ctx.channel.send(table)

        while True:    
            try:
                table = border; iC = 0
                # Manually catch the <tick_obj>. If caught, use <tick_obj>.behalf instead
                for collumn in self.cord: 
                    coll = ''
                    for slot in collumn:
                        try:
                            coll = coll + slot + '    '
                        except TypeError:
                            coll = coll + slot.behalf + '    '
                    table = table + coll +  f"  |  **{iC}** " + '\n'; iC += 1
                await msg.edit(content=table)

                # Check winning_condition
                if winning_condition: await clean_up(); await ctx.channel.send("**CONGRATS!** I'm upset. It's your fault :<"); return

                # Check if player mischeck on their prev check or bot's check
                while True:  
                    try:
                        def U_check(m):
                            return m.author.id == ctx.author.id and m.channel == ctx.channel
                        respond = await self.client.wait_for('message', check=U_check, timeout=delay)
                        if respond.content == 'resign':
                            await ctx.channel.send(f"You coward! Don't expect me to let you run next time, {ctx.message.author.mention}!")
                            await clean_up(); return
                        elif respond.content == 'reboard':
                            await msg.delete()
                            msg_temp = await ctx.send(table)
                            msg = msg_temp
                    except asyncio.TimeoutError:              # In case wait_for_message time out
                        await ctx.message.channel.send(f"How could you *afk* to me like that, {ctx.message.author.mention}? :<")
                        await clean_up(); return
                    try:
                        in_cord = respond.content.split(' ')
                        # Check if players dont check at X and O
                        if not self.cord[int(in_cord[0])][int(in_cord[1])] == 'O' and not isinstance(self.cord[int(in_cord[0])][int(in_cord[1])], ticker):
                            try: await respond.delete(); break
                            except discordErrors.Forbidden: break
                        else:
                            try: await respond.delete(); break 
                            except discordErrors.Forbidden: break
                    except (IndexError, ValueError, TypeError): pass

                # Create <tick_obj>, then add to <ticks_list>
                self.ticks.append(ticker(in_cord[0], in_cord[1], self.cord))

                # Commence
                self.cord[self.ticks[-1].x][self.ticks[-1].y] = self.ticks[-1] #self.ticks[-1].behalf

                maindiagonalseq_socket = []; antidiagonalseq_socket = []; horizontalseq_socket = []; verticalseq_socket = []

                # Initially run 4 directions scan of each tick to get sequences 
                # (maindiagonal, antidiagonal, vertical, horizontal)
                for tick in self.ticks:
                    seq = []
                    maindiagonalseq_socket.append(tick.main_diagonal(seq, tick.x, tick.y))
                    antidiagonalseq_socket.append(tick.anti_diagonal(seq, tick.x, tick.y))
                    horizontalseq_socket.append(tick.horizontal(seq, tick.x, tick.y))
                    verticalseq_socket.append(tick.vertical(seq, tick.x, tick.y))

              
                maindiagonalsequantum_socket = []; antidiagonalsequantum_socket = []; verticalsequantum_socket = []; horizontalsequantum_socket = []

                maindiagonalsequantum_socket = self.sequantumize(maindiagonalseq_socket, 'maindiagonal')
                antidiagonalsequantum_socket = self.sequantumize(antidiagonalseq_socket, 'antidiagonal')
                verticalsequantum_socket = self.sequantumize(horizontalseq_socket, 'horizontal')
                horizontalsequantum_socket = self.sequantumize(verticalseq_socket, 'vertical')

                allsequantum_socket = maindiagonalsequantum_socket + antidiagonalsequantum_socket + verticalsequantum_socket + horizontalsequantum_socket

                #sorted(allsequantum_socket, key=lambda sequan: sequan.seq_length, reverse=True)
                
                # Danger ranking (R1, R2, R3, R4)
                R1 = []; R2 = []; R3 = []; R4 = []
                for sequantum in allsequantum_socket:
                    if sequantum.seq_length == 1: R1.append(sequantum)
                    elif sequantum.seq_length == 2: R2.append(sequantum)
                    elif sequantum.seq_length == 3: R3.append(sequantum)
                    elif sequantum.seq_length == 4: R4.append(sequantum)
                    elif sequantum.seq_length == 5 and not sequantum.ghosted: winning_condition = True    # <<<<<<<<<<<<<< WIN >>>>>>>>>>>>>

                # Commence analizing and defensing
                # Getting need-to-handle address, priotizing from rank R4 to R1
                address = []; R_lock = False
                r4code = ''; r3code = ''
                if R4:
                    # Full addr >> Full ghost >> Half ghost >> Half addr
                    full_seq = []; full_ghost = []; half_ghost = []; half_seq = []
                    # Filtering seq type
                    for sequantum in R4:
                        if sequantum.ghosted:
                            # Random pick a tick
                            ghost_tick = random.choice(sequantum.ghost_ticks)
                            # If all three are empty
                            if self.cord[ghost_tick.x][ghost_tick.y] == self.slot_char and self.cord[sequantum.nhead_x][sequantum.nhead_y] == self.slot_char and self.cord[sequantum.ntail_x][sequantum.ntail_y] == self.slot_char:
                                full_ghost.append(ghost_tick)
                            # If one of two heads is empty AND ghost point is empty
                            elif self.cord[ghost_tick.x][ghost_tick.y] == self.slot_char and self.cord[sequantum.nhead_x][sequantum.nhead_y] != self.cord[sequantum.ntail_x][sequantum.ntail_y]:
                                half_ghost.append(ghost_tick)
                            continue

                        if self.cord[sequantum.nhead_x][sequantum.nhead_y] == self.slot_char and self.cord[sequantum.ntail_x][sequantum.ntail_y] == self.slot_char:
                            full_seq.append(sequantum)
                        elif self.cord[sequantum.nhead_x][sequantum.nhead_y] != self.cord[sequantum.ntail_x][sequantum.ntail_y]:
                            half_seq.append(sequantum)

                    # Extract seq
                    if full_seq:
                        for sequantum in full_seq:
                            if self.cord[sequantum.nhead_x][sequantum.nhead_y] == self.slot_char:
                                address.append((sequantum.nhead_x, sequantum.nhead_y))
                            if self.cord[sequantum.ntail_x][sequantum.ntail_y] == self.slot_char:
                                address.append((sequantum.ntail_x, sequantum.ntail_y))
                        r4code = 'r4fs'
                    elif full_ghost:
                        for sequantum in full_ghost:
                            address.append((sequantum.x, sequantum.y))
                        r4code = 'r4fg'
                    elif half_ghost:
                        for sequantum in half_ghost:
                            address.append((sequantum.x, sequantum.y))
                        r4code = 'r4hg'
                    elif half_seq:
                        for sequantum in half_seq:
                            if self.cord[sequantum.nhead_x][sequantum.nhead_y] == self.slot_char:
                                address.append((sequantum.nhead_x, sequantum.nhead_y))
                            if self.cord[sequantum.ntail_x][sequantum.ntail_y] == self.slot_char:
                                address.append((sequantum.ntail_x, sequantum.ntail_y))
                        r4code = 'r4hs'

                    if address: R_lock = True
                if R3:
                    # Full addr >> Full ghost >> Half ghost >> Half addr
                    full_seq = []; full_ghost = []; half_ghost = []; half_seq = []
                    # Filtering seq type
                    for sequantum in R3:
                        if sequantum.ghosted:
                            # Random pick a tick
                            ghost_tick = random.choice(sequantum.ghost_ticks)
                            # If all three are empty
                            if self.cord[ghost_tick.x][ghost_tick.y] == self.slot_char and self.cord[sequantum.nhead_x][sequantum.nhead_y] == self.slot_char and self.cord[sequantum.ntail_x][sequantum.ntail_y] == self.slot_char:
                                full_ghost.append(ghost_tick)
                            # If one of two heads is empty AND ghost point is empty
                            elif self.cord[ghost_tick.x][ghost_tick.y] == self.slot_char and self.cord[sequantum.nhead_x][sequantum.nhead_y] != self.cord[sequantum.ntail_x][sequantum.ntail_y]:
                                half_ghost.append(ghost_tick)
                            continue

                        if self.cord[sequantum.nhead_x][sequantum.nhead_y] == self.slot_char and self.cord[sequantum.ntail_x][sequantum.ntail_y] == self.slot_char:
                            full_seq.append(sequantum)
                        elif self.cord[sequantum.nhead_x][sequantum.nhead_y] != self.cord[sequantum.ntail_x][sequantum.ntail_y]:
                            half_seq.append(sequantum)

                    # Extract seq
                    if full_seq and r4code not in ('r4fs', 'r4fg', 'r4hs'):
                        for sequantum in full_seq:
                            if self.cord[sequantum.nhead_x][sequantum.nhead_y] == self.slot_char:
                                address.append((sequantum.nhead_x, sequantum.nhead_y))
                            if self.cord[sequantum.ntail_x][sequantum.ntail_y] == self.slot_char:
                                address.append((sequantum.ntail_x, sequantum.ntail_y))
                        r3code = 'r3fs'
                    elif full_ghost and r4code not in ('r4fs', 'r4fg', 'r4hg', 'r4hs'):
                        for sequantum in full_ghost:
                            address.append((sequantum.x, sequantum.y))
                        r3code = 'r3fg'
                    elif half_ghost and r4code not in ('r4fs', 'r4fg', 'r4hg', 'r4hs'):
                        for sequantum in half_ghost:
                            address.append((sequantum.x, sequantum.y))
                        r3code = 'r3hg'
                    elif half_seq and r4code not in ('r4fs', 'r4fg', 'r4hg', 'r4hs'):
                        for sequantum in half_seq:
                            if self.cord[sequantum.nhead_x][sequantum.nhead_y] == self.slot_char:
                                address.append((sequantum.nhead_x, sequantum.nhead_y))
                            if self.cord[sequantum.ntail_x][sequantum.ntail_y] == self.slot_char:
                                address.append((sequantum.ntail_x, sequantum.ntail_y))
                        r3code = 'r3hs'

                    if address: R_lock = True

                # EMERGENCE camp =========


                if R2 and R_lock == False:
                    for sequantum in R2:
                        if self.cord[sequantum.nhead_x][sequantum.nhead_y] == self.slot_char:
                            address.append((sequantum.nhead_x, sequantum.nhead_y))
                        if self.cord[sequantum.ntail_x][sequantum.ntail_y] == self.slot_char:
                            address.append((sequantum.ntail_x, sequantum.ntail_y))   
                    if address: R_lock = True
                if R1 and R_lock == False:
                    for sequantum in R1:
                        if self.cord[sequantum.nhead_x][sequantum.nhead_y] == self.slot_char:
                            address.append((sequantum.nhead_x, sequantum.nhead_y))
                        if self.cord[sequantum.ntail_x][sequantum.ntail_y] == self.slot_char:
                            address.append((sequantum.ntail_x, sequantum.ntail_y))   
                    if address: R_lock = True 

                # Pick randomly                               
                try:
                    print("---------------")
                    print(f"MOVES: {address}")
                    movement_x, movement_y = random.choice(address)
                    print(f"BOT_MOVE: {movement_x} {movement_y}")
                except IndexError: print("INDEX ERRORRRRRRR")

                # Move
                self.cord[movement_x][movement_y] = 'O'
                        

                print("++")
                print(f"TICKS: {len(self.ticks)}")
                if R3:
                    for x in R3:
                        print(f"HEAD: {x.head.x}/{x.head.y} || TAIL: {x.tail.x}/{x.tail.y}") 

                
            except IndexError: pass



class ticker:
    def __init__(self, x, y, cord, ghosted=False):
        self.x = int(x)
        self.y = int(y)
        self.cord = cord
        self.ghosted = ghosted
        self.behalf = 'X'
        self.restricted_char = ['--', 'O']
    
    def main_diagonal(self, seq, x, y):
        seq_1 = []; seq_2 = []
        seq_1 = self.down_right(seq_1, x, y)
        seq_2 = self.top_left(seq_2, x, y)
        return list(set(seq_1 + seq_2))

    def anti_diagonal(self, seq, x, y):
        seq_1 = []; seq_2 = []
        seq_1 = self.down_left(seq_1, x, y)
        seq_2 = self.top_right(seq_2, x, y)
        return list(set(seq_1 + seq_2))

    def horizontal(self, seq, x, y):
        seq_1 = []; seq_2 = []
        seq_1 = self.horizontal_left(seq_1, x, y)
        seq_2 = self.horizontal_right(seq_2, x, y)
        return list(set(seq_1 + seq_2))

    def vertical(self, seq, x, y):
        seq_1 = []; seq_2 = []
        seq_1 = self.vertical_up(seq_1, x, y)
        seq_2 = self.vertical_down(seq_2, x, y)
        return list(set(seq_1 + seq_2))

    # ========= MAIN_DIAG
    def down_right(self, seq, x, y, step=0, steps=1):
        # The tick checks if the next slot have a tick
        if self.cord[x + 1][y + 1] not in self.restricted_char:
            # If not stepping, move to the NEXT slot
            if not step: seq = self.cord[x + 1][y + 1].down_right(seq, self.cord[x + 1][y + 1].x, self.cord[x + 1][y + 1].y, step=step, steps=steps)
            # If steeping, STOP and RESET stepping
            else: seq = self.cord[x + 1][y + 1].down_right(seq, self.cord[x + 1][y + 1].x, self.cord[x + 1][y + 1].y, step=-1, steps=-1)

            # Put ITS OWN tick into the seq
            if isinstance(self.cord[x][y], ticker): seq.append(self.cord[x][y])
            else: seq.append(ticker(x, y, self.cord, ghosted=True))
            # Pass the seq back
            return seq
        # If not, put ITS OWN tick into the seq, then pass back
        else:
            # Over-stepping, using ghosting ticker
            if step < steps:
                ghost_temp = ticker(x + 1, y + 1, self.cord, ghosted=True)
                seq = ghost_temp.down_right(seq, ghost_temp.x, ghost_temp.y, step=step+1)
            # Over-stepping done, but nothing found
            elif step == steps and steps > 0:
                return seq

            if isinstance(self.cord[x][y], ticker): seq.append(self.cord[x][y])
            else: seq.append(ticker(x, y, self.cord, ghosted=True))
            return seq

    def top_left(self, seq, x, y, step=0, steps=1):
        # The tick checks if the next slot have a tick
        if self.cord[x - 1][y - 1] not in self.restricted_char:
            # If not stepping, move to the NEXT slot
            if not step: seq = self.cord[x - 1][y - 1].top_left(seq, self.cord[x - 1][y - 1].x, self.cord[x - 1][y - 1].y, step=step, steps=steps)
            # If steeping, STOP and RESET stepping
            else: seq = self.cord[x - 1][y - 1].top_left(seq, self.cord[x - 1][y - 1].x, self.cord[x - 1][y - 1].y, step=-1, steps=-1)

            # Put ITS OWN tick into the seq
            if isinstance(self.cord[x][y], ticker): seq.append(self.cord[x][y])
            else: seq.append(ticker(x, y, self.cord, ghosted=True))
            # Pass the seq back
            return seq
        # If not, put ITS OWN tick into the seq, then pass back
        else:
            # Over-stepping, using ghosting ticker
            if step < steps:
                ghost_temp = ticker(x - 1, y - 1, self.cord, ghosted=True)
                seq = ghost_temp.top_left(seq, ghost_temp.x, ghost_temp.y, step=step+1)
            # Over-stepping done, but nothing found
            elif step == steps and steps > 0:
                return seq

            if isinstance(self.cord[x][y], ticker): seq.append(self.cord[x][y])
            else: seq.append(ticker(x, y, self.cord, ghosted=True))
            return seq

    # ========= ANTI_DIAG
    def down_left(self, seq, x, y, step=0, steps=1):
        # The tick checks if the next slot have a tick
        if self.cord[x - 1][y + 1] not in self.restricted_char:
            # If not stepping, move to the NEXT slot
            if not step: seq = self.cord[x - 1][y + 1].down_left(seq, self.cord[x - 1][y + 1].x, self.cord[x - 1][y + 1].y, step=step, steps=steps)
            # If steeping, STOP and RESET stepping
            else: seq = self.cord[x - 1][y + 1].down_left(seq, self.cord[x - 1][y + 1].x, self.cord[x - 1][y + 1].y, step=-1, steps=-1)

            # Put ITS OWN tick into the seq
            if isinstance(self.cord[x][y], ticker): seq.append(self.cord[x][y])
            else: seq.append(ticker(x, y, self.cord, ghosted=True))
            # Pass the seq back
            return seq
        # If not, put ITS OWN tick into the seq, then pass back
        else:
            # Over-stepping, using ghosting ticker
            if step < steps:
                ghost_temp = ticker(x - 1, y + 1, self.cord, ghosted=True)
                seq = ghost_temp.down_left(seq, ghost_temp.x, ghost_temp.y, step=step+1)
            # Over-stepping done, but nothing found
            elif step == steps and steps > 0:
                return seq

            if isinstance(self.cord[x][y], ticker): seq.append(self.cord[x][y])
            else: seq.append(ticker(x, y, self.cord, ghosted=True))
            return seq

    def top_right(self, seq, x, y, step=0, steps=1):
        # The tick checks if the next slot have a tick
        if self.cord[x + 1][y - 1] not in self.restricted_char:
            # If not stepping, move to the NEXT slot
            if not step: seq = self.cord[x + 1][y - 1].top_right(seq, self.cord[x + 1][y - 1].x, self.cord[x + 1][y - 1].y, step=step, steps=steps)
            # If steeping, STOP and RESET stepping
            else: seq = self.cord[x + 1][y - 1].top_right(seq, self.cord[x + 1][y - 1].x, self.cord[x + 1][y - 1].y, step=-1, steps=-1)

            # Put ITS OWN tick into the seq
            if isinstance(self.cord[x][y], ticker): seq.append(self.cord[x][y])
            else: seq.append(ticker(x, y, self.cord, ghosted=True))
            # Pass the seq back
            return seq
        # If not, put ITS OWN tick into the seq, then pass back
        else:
            # Over-stepping, using ghosting ticker
            if step < steps:
                ghost_temp = ticker(x + 1, y - 1, self.cord, ghosted=True)
                seq = ghost_temp.top_right(seq, ghost_temp.x, ghost_temp.y, step=step+1)
            # Over-stepping done, but nothing found
            elif step == steps and steps > 0:
                return seq

            if isinstance(self.cord[x][y], ticker): seq.append(self.cord[x][y])
            else: seq.append(ticker(x, y, self.cord, ghosted=True))
            return seq

    # ========= HORIZONTAL
    def horizontal_right(self, seq, x, y, step=0, steps=1):
        # The tick checks if the next slot have a tick
        if self.cord[x][y + 1] not in self.restricted_char:
            # If not stepping, move to the NEXT slot
            if not step: seq = self.cord[x][y + 1].horizontal_right(seq, self.cord[x][y + 1].x, self.cord[x][y + 1].y, step=step, steps=steps)
            # If steeping, STOP and RESET stepping
            else: seq = self.cord[x][y + 1].horizontal_right(seq, self.cord[x][y + 1].x, self.cord[x][y + 1].y, step=-1, steps=-1)

            # Put ITS OWN tick into the seq
            if isinstance(self.cord[x][y], ticker): seq.append(self.cord[x][y])
            else: seq.append(ticker(x, y, self.cord, ghosted=True))
            # Pass the seq back
            return seq
        # If not, put ITS OWN tick into the seq, then pass back
        else:
            # Over-stepping, using ghosting ticker
            if step < steps:
                ghost_temp = ticker(x, y + 1, self.cord, ghosted=True)
                seq = ghost_temp.horizontal_right(seq, ghost_temp.x, ghost_temp.y, step=step+1)
            # Over-stepping done, but nothing found
            elif step == steps and steps > 0:
                return seq

            if isinstance(self.cord[x][y], ticker): seq.append(self.cord[x][y])
            else: seq.append(ticker(x, y, self.cord, ghosted=True))
            return seq

    def horizontal_left(self, seq, x, y, step=0, steps=1):
        # The tick checks if the next slot have a tick
        if self.cord[x][y - 1] not in self.restricted_char:
            # If not stepping, move to the NEXT slot
            if not step: seq = self.cord[x][y - 1].horizontal_left(seq, self.cord[x][y - 1].x, self.cord[x][y - 1].y, step=step, steps=steps)
            # If steeping, STOP and RESET stepping
            else: seq = self.cord[x][y - 1].horizontal_left(seq, self.cord[x][y - 1].x, self.cord[x][y - 1].y, step=-1, steps=-1)

            # Put ITS OWN tick into the seq
            if isinstance(self.cord[x][y], ticker): seq.append(self.cord[x][y])
            else: seq.append(ticker(x, y, self.cord, ghosted=True))
            # Pass the seq back
            return seq
        # If not, put ITS OWN tick into the seq, then pass back
        else:
            # Over-stepping, using ghosting ticker
            if step < steps:
                ghost_temp = ticker(x, y - 1, self.cord, ghosted=True)
                seq = ghost_temp.horizontal_left(seq, ghost_temp.x, ghost_temp.y, step=step+1)
            # Over-stepping done, but nothing found
            elif step == steps and steps > 0:
                return seq
                
            if isinstance(self.cord[x][y], ticker): seq.append(self.cord[x][y])
            else: seq.append(ticker(x, y, self.cord, ghosted=True))
            return seq

    # ========= VERTICAL
    def vertical_up(self, seq, x, y, step=0, steps=1):
        # The tick checks if the next slot have a tick
        if self.cord[x - 1][y] not in self.restricted_char:
            # If not stepping, move to the NEXT slot
            if not step: seq = self.cord[x - 1][y].vertical_up(seq, self.cord[x - 1][y].x, self.cord[x - 1][y].y, step=step, steps=steps)
            # If steeping, STOP and RESET stepping
            else: seq = self.cord[x - 1][y].vertical_up(seq, self.cord[x - 1][y].x, self.cord[x - 1][y].y, step=-1, steps=-1)

            # Put ITS OWN tick into the seq
            if isinstance(self.cord[x][y], ticker): seq.append(self.cord[x][y])
            else: seq.append(ticker(x, y, self.cord, ghosted=True))
            # Pass the seq back
            return seq
        # If not, put ITS OWN tick into the seq, then pass back
        else:
            # Over-stepping, using ghosting ticker
            if step < steps:
                ghost_temp = ticker(x - 1, y, self.cord, ghosted=True)
                seq = ghost_temp.vertical_up(seq, ghost_temp.x, ghost_temp.y, step=step+1)
            # Over-stepping done, but nothing found
            elif step == steps and steps > 0:
                return seq

            if isinstance(self.cord[x][y], ticker): seq.append(self.cord[x][y])
            else: seq.append(ticker(x, y, self.cord, ghosted=True))
            return seq

    def vertical_down(self, seq, x, y, step=0, steps=1):
        # The tick checks if the next slot have a tick
        if self.cord[x + 1][y] not in self.restricted_char:
            # If not stepping, move to the NEXT slot
            if not step: seq = self.cord[x + 1][y].vertical_down(seq, self.cord[x + 1][y].x, self.cord[x + 1][y].y, step=step, steps=steps)
            # If steeping, STOP and RESET stepping
            else: seq = self.cord[x + 1][y].vertical_down(seq, self.cord[x + 1][y].x, self.cord[x + 1][y].y, step=-1, steps=-1)

            # Put ITS OWN tick into the seq
            if isinstance(self.cord[x][y], ticker): seq.append(self.cord[x][y])
            else: seq.append(ticker(x, y, self.cord, ghosted=True))
            # Pass the seq back
            return seq
        # If not, put ITS OWN tick into the seq, then pass back
        else:
            # Over-stepping, using ghosting ticker
            if step < steps:
                ghost_temp = ticker(x + 1, y, self.cord, ghosted=True)
                seq = ghost_temp.vertical_down(seq, ghost_temp.x, ghost_temp.y, step=step+1)
            # Over-stepping done, but nothing found
            elif step == steps and steps > 0:
                return seq

            if isinstance(self.cord[x][y], ticker): seq.append(self.cord[x][y])
            else: seq.append(ticker(x, y, self.cord, ghosted=True))
            return seq



class sequantum:
    def __init__(self, seq, type, ghosted=False, ghost_ticks=[]):
        self.seq = seq
        #print(f"SEQ {type}: {seq}")
        self.type = type
        self.ghosted = ghosted
        self.ghost_ticks = ghost_ticks
        self.seq_length = len(self.seq)
        # Getting head and tail of a <sequantum>
        self.head, self.tail, self.nhead_x, self.nhead_y, self.ntail_x, self.ntail_y = self.sorting(self.seq, self.type)

    def sorting(self, seq, type):
        head = [seq[0]]
        tail = [seq[0]]
        if type == 'horizontal':
            for tick in seq:
                if tick.y > head[0].y: head[0] = tick
                elif tick.y < tail[0].y: tail[0] = tick
            nextto_head_x = head[0].x
            nextto_head_y = head[0].y + 1
            nextto_tail_x = tail[0].x
            nextto_tail_y = tail[0].y - 1
        elif type == 'vertical':
            for tick in seq:
                if tick.x > head[0].x: head[0] = tick
                elif tick.x < tail[0].x: tail[0] = tick
            nextto_head_x = head[0].x + 1
            nextto_head_y = head[0].y 
            nextto_tail_x = tail[0].x - 1
            nextto_tail_y = tail[0].y
        elif type == 'maindiagonal':
            for tick in seq:
                if tick.x > head[0].x: head[0] = tick
                elif tick.x < tail[0].x: tail[0] = tick
            nextto_head_x = head[0].x + 1
            nextto_head_y = head[0].y + 1
            nextto_tail_x = tail[0].x - 1
            nextto_tail_y = tail[0].y - 1
        elif type == 'antidiagonal':
            for tick in seq:
                if tick.x > head[0].x: head[0] = tick
                elif tick.x < tail[0].x: tail[0] = tick
            nextto_head_x = head[0].x + 1
            nextto_head_y = head[0].y - 1
            nextto_tail_x = tail[0].x - 1
            nextto_tail_y = tail[0].y + 1

        return head[0], tail[0], nextto_head_x, nextto_head_y, nextto_tail_x, nextto_tail_y
                
            
            


def setup(client):
    client.add_cog(tictactoe(client))

            











