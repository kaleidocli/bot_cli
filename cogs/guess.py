import discord
from discord.ext import commands
import random
import json
from discord.ext.commands.cooldowns import BucketType
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
from functools import partial
import asyncio
import aiomysql
#import concurrent

async def get_CURSOR():
    conn = await aiomysql.connect(host='localhost', user='root', password='mysql', port=3307, db='mycli', autocommit=True)
    _cursor = await conn.cursor()
    return conn, _cursor

loop = asyncio.get_event_loop()    
conn, _cursor = loop.run_until_complete(get_CURSOR())

def check_id():
    def inner(ctx):
        return ctx.author.id == 214128381762076672       
    return commands.check(inner)

class guess(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.guess_socket = []          #For guess
        self.guess_dictall = {}         #For guess_all
        # self.guess_socket_plugin()
        # self.guess_socket_pluginall()
        self.client_id = '594344297452325'
        self.client_secret = '2e29f3c50797fa6d5aad8b5bef527b214683a3ff'
        self.imgur_client = ImgurClient(self.client_id, self.client_secret)
        #self.client.load_extension('error_handling')



    @commands.command(pass_context=True, aliases=['quiz'])
    @commands.cooldown(1, 10, type=BucketType.user)
    async def guess(self, ctx):
        id, question, answer, illulink = await self.quefe(f"SELECT id, question, answer, illulink FROM tz_quiz WHERE guild_id='{ctx.guild.id}' ORDER BY rand() LIMIT 1;")

        msg_box = discord.Embed(
            title = question,
            colour = discord.Colour(0x011C3A),
        )
        msg_box.set_footer(text=f"Quiz id ({id})")
        if illulink:
            msg_box.set_image(url=illulink)                     #Image quiz
        else: pass                                                      #Text quiz
        await ctx.send(embed=msg_box)

        #Generate the hint. Then send it.
        hint_list = []
        for c in answer:
            if c == ' ': hint_list.append(c)
            else: hint_list.append('⊙')
        hint = ''.join(hint_list)
        await ctx.send(f":bulb: **HINT:** {hint}")

        def UMCc_check(m):
            return m.channel == ctx.channel and m.author == ctx.author and m.content.lower() == answer

        try: await self.client.wait_for('message', timeout=15, check=UMCc_check)
        except asyncio.TimeoutError:
            await ctx.send("<:fufu:508437298808094742> Duh loserrrrr")
            await _cursor.execute(f"UPDATE tz_quiz SET lose=lose+1 WHERE user_id='{ctx.author.id}';")
            return

        await ctx.send("**Congrats!!!**")
        await _cursor.execute(f"UPDATE tz_quiz SET win=win+1 WHERE user_id='{ctx.author.id}';")
        return

    @commands.command(aliases=['quiz_add'])
    async def guess_add(self, ctx, *args):
        delay = 30

        def UMCc_check(m):
            return m.channel == ctx.channel and m.author == ctx.author

        try:
            await ctx.send("**Quiz?**")
            quiz = await self.client.wait_for('message', timeout=delay, check=UMCc_check)

            await ctx.send("**Answer?**")
            answer = await self.client.wait_for('message', timeout=delay, check=UMCc_check)

            await ctx.send("**Illustration link? (type `none` to omit)**")
            illulink = await self.client.wait_for('message', timeout=delay, check=UMCc_check)
            if illulink.content != 'none':
                try:
                    img = await self.client.loop.run_in_executor(None, self.imgur_client.upload_from_url, illulink.content)
                    illulink = img['link']
                except ImgurClientError:
                    #Invalid link
                    await ctx.send(":warning: Invalid link!"); return
            else: illulink = 'n/a'
            await _cursor.execute(f"""INSERT INTO tz_quiz VALUES (0, "{quiz.content}", "{answer.content}", "{illulink}", 0, 0, '{ctx.author.id}', '{ctx.guild.id}');""")
            await ctx.send(":white_check_mark: Successfully added!"); return
        except asyncio.TimeoutError: await ctx.send(":warning: Request timed out!"); return

    """
        #In a_in list, 0=question 1=answer 2=link
        raw = list(args)
        quiz_obj = {}

        #if '=' not in a_in:
        #    await self.client.say(":no_entry_sign: Please use the right syntax.")
        #    pass
        a_in = ' '.join(raw).split(' == ')
        print(a_in)
        
        #Adding five elements of a quiz_obj
        try:
            img = await self.client.loop.run_in_executor(None, self.imgur_client.upload_from_url, f"{a_in[2]}")
            print(img)
            quiz_obj['link'] = img['link']
        except ImgurClientError:
            #Invalid link
            await self.client.send_message(ctx.message.channel, "Invalid link!"); return
        except IndexError: 
            #Check if a_in[1] or a_in[0] is a link. If not, continue, else return
            try:
                if 'https://' in a_in[0] or 'https://' in a_in[1]:
                    await self.client.send_message(ctx.message.channel, "Invalid syntax!"); return
                else:
                    quiz_obj['link'] = 'n/a'
            except IndexError:
                await self.client.send_message(ctx.message.channel, f"{ctx.message.author.mention}, please give me something to add. \n`guess_add <Questions> == <Answer> == <Img_link(Optional)>")
        quiz_obj['question'] = a_in[0]
        quiz_obj['answer'] = a_in[1].lower()
        quiz_obj['user_id'] = ctx.message.author.id
        quiz_obj['server_id'] = ctx.guild.id
        quiz_obj['win'] = '0'; quiz_obj['lose'] = '0'
        if self.guess_socket:
            quiz_obj['id'] = str(int(self.guess_socket[-1]['id']) + 1)
        else:
            quiz_obj['id'] = '0'

        self.guess_socket.append(quiz_obj)
        await self.client.send_message(ctx.message.channel, f"Added quiz with id `{quiz_obj['id']}`")
        
        #    try:    
        #        #Update <answer> list (if exist), append the value into the answer list
        #        self.guess_dict[' '.join(a_in[:int(a_in.index('='))]).lower()].append(img['link'])
        #        await self.client.send_message(ctx.message.channel, "Adding as an `image` quiz..")
        #    except KeyError:
        #        #Create <answer> list. Parse the <answer> list to the <key>
        #        self.guess_dict[' '.join(a_in[:int(a_in.index('='))]).lower()] = [img['link']]
        #        await self.client.send_message(ctx.message.channel, "Adding as an `image` quiz...")

        #Update the .json
        await self.client.loop.run_in_executor(None, self.updating)

        await self.client.say(":white_check_mark: Successfully added!")"""

    @commands.command(pass_context=True)
    @check_id()
    async def guess_del(self, ctx, *args):
        try:
            id = list(args)[0]
        except IndexError: await self.client.send_message(ctx.message.channel, "Please give the quiz' `id`!")
        
        for a in self.guess_socket:
            if a['id'] == id:
                del self.guess_socket[self.guess_socket.index(a)]
                #Update the .json
                await self.client.loop.run_in_executor(None, self.updating)

                #Send the last copies of the item
                dumper = partial(json.dumps, a, indent=4, sort_keys=True)
                line = await self.client.loop.run_in_executor(None, dumper)
                await self.client.send_message(ctx.message.author,f":notepad_spiral: **LAST COPIES OF THE DELETED QUIZ** id `{id}`")
                await self.client.send_message(ctx.message.author, f"""```json
                                                                        {line}```""")

                await self.client.send_message(ctx.message.channel, f":white_check_mark: Quiz with id=`{id}` deleted!"); return
        await self.client.send_message(ctx.message.channel, f":x: Quiz with id=`{id}` not found!")

    @commands.command(pass_context=True)
    @check_id()
    async def guess_applyall_newentry(self, ctx, *args):

        try:
            raw2 = ' '.join(args).split(' == ')
            for quiz_obj in self.guess_socket:
                quiz_obj[raw2[0]] = raw2[1]
        except IndexError: await self.client.send_message(ctx.message.channel, ":x: Wrong syntax!"); return
        
        # Update the .json
        await self.client.loop.run_in_executor(None, self.updating)
        await self.client.send_message(ctx.message.channel, f":white_check_mark: *Added* the new entry `{raw2[0]}` with default value `{raw2[1]}`!")

    @commands.command(pass_context=True)
    @check_id()
    async def guess_applyall_delentry(self, ctx, *args):
        str_in = ' '.join(args)


        try:
            for quiz_obj in self.guess_socket:
                del quiz_obj[str_in]
        except: await self.client.send_message(ctx.message.channel, f":x: Entry `{str_in}` not found!"); return
            
        # Update the .json
        await self.client.loop.run_in_executor(None, self.updating)
        await self.client.send_message(ctx.message.channel, f":white_check_mark: *Deleted* entry `{str_in}` with its value!")


    @commands.command(pass_context=True)
    @check_id()
    async def guess_edit(self, ctx, *args):
        raw = list(args)
        try:
            id = raw[0]
        except IndexError: await self.client.send_message(ctx.message.channel, ":x: Please give the quiz' `id`!")

        try:
            entry = raw[1]
        except IndexError: await self.client.send_message(ctx.message.channel, ":x: Please give the quiz' `entry`!")

        try:
            fixation = ' '.join(raw[2:])
        except IndexError: await self.client.send_message(ctx.message.channel, ":x: Please give the `fixation` for the quiz!")

        for a in self.guess_socket:
            if a['id'] == id:
                if entry in list(a.keys()): 
                    a[entry] = fixation
                    await self.client.send_message(ctx.message.channel, ":white_check_mark: **FIXED**!")
                    msg = await self.client.send_message(ctx.message.channel, f"""```json
                                                                                        {entry}: {a.get(raw[1])}```""")
                    await asyncio.sleep(2.5); await self.client.delete_message(msg); return
                else: await self.client.send_message(ctx.message.channel, f":x: `{entry}` entry not found!"); return

        await self.client.send_message(ctx.message.channel, f":x: Quiz id `{id}` not found!")

    @commands.command(pass_context=True)
    @check_id()
    async def guess_get(self, ctx, *args):
        try:
            id = list(args)[0]
        except IndexError: await self.client.send_message(ctx.message.channel, "Please give the quiz' `id`!")

        for a in self.guess_socket:
            if a['id'] == id: 
                dumper = partial(json.dumps, a, indent=4, sort_keys=True)
                line = await self.client.loop.run_in_executor(None, dumper)
                await self.client.send_message(ctx.message.author, f"""```json
                                                                        {line}```""")
                return
        await self.client.send_message(ctx.message.channel, "Quiz_id not found!")

    @commands.command(pass_context=True)
    @check_id()
    async def guesses(self, ctx):
        #dumper = partial(json.dumps, self.guess_socket, indent=4, sort_keys=True)
        #line = await self.client.loop.run_in_executor(None, dumper)
        #await self.client.send_message(ctx.message.author, f"""```json
        #                                                            {line}```""")

        async def makebox(top, least, pages, currentpage):


            dumper = partial(json.dumps, self.guess_socket[top:least], indent=4, sort_keys=True)
            content = await self.client.loop.run_in_executor(None, dumper)
            line = f"""```json
                            {content}``` \n`Page {currentpage} of {pages}`"""
            return line
            #else:
            #    await client.say("*Nothing but dust here...*")
        
        async def attachreaction(msg):
            await self.client.add_reaction(msg, "\U000023ee")    #Top-left
            await self.client.add_reaction(msg, "\U00002b05")    #Left
            await self.client.add_reaction(msg, "\U000027a1")    #Right
            await self.client.add_reaction(msg, "\U000023ed")    #Top-right

        pages = len(self.guess_socket)//5
        if len(self.guess_socket)%5 != 0: pages += 1
        currentpage = 1
        mybox = await makebox(0, 5, pages, currentpage)
        msg = await self.client.send_message(ctx.message.author, mybox)
        await attachreaction(msg)

        while True:
            try:    
                reaction, user = await self.client.wait_for_reaction(message=msg, timeout=30)
                if reaction.emoji == "\U000027a1" and user.id == ctx.message.author.id and currentpage < pages:
                    currentpage += 1
                    mybox = await makebox(currentpage*5-5, currentpage*5, pages, currentpage)
                    await self.client.edit_message(msg, mybox)
                elif reaction.emoji == "\U00002b05" and user.id == ctx.message.author.id and currentpage > 1:
                    currentpage -= 1
                    mybox = await makebox(currentpage*5-5, currentpage*5, pages, currentpage)
                    await self.client.edit_message(msg, mybox)
                elif reaction.emoji == "\U000023ee" and user.id == ctx.message.author.id and currentpage != 1:
                    currentpage = 1
                    mybox = await makebox(currentpage*5-5, currentpage*5, pages, currentpage)
                    await self.client.edit_message(msg, mybox)
                elif reaction.emoji == "\U000023ed" and user.id == ctx.message.author.id and currentpage != pages:
                    currentpage = pages
                    mybox = await makebox(currentpage*5-5, currentpage*5, pages, currentpage)
                    await self.client.edit_message(msg, mybox)
            except TypeError: 
                break



    @commands.command(pass_context=True)
    async def guess_add_all(self, ctx, *args):
        #In a_in list, 0=question 1=answer 2=link
        raw = list(args)
        quiz_obj = {}
        guess_socketall = []
        #guess_socketall_temp = self.guess_dictall[]

        #if '=' not in a_in:
        #    await self.client.say(":no_entry_sign: Please use the right syntax.")
        #    pass
        a_in = ' '.join(raw).split(' == ')
        print(a_in)
        


        #Adding five elements of a quiz_obj
        try:
            img = await self.client.loop.run_in_executor(None, self.imgur_client.upload_from_url, f"{a_in[2]}")
            print(img)
            quiz_obj['link'] = img['link']
        except ImgurClientError:
            #Invalid link
            await self.client.send_message(ctx.message.channel, "Invalid link!"); return
        except IndexError: 
            #Check if a_in[1] or a_in[0] is a link. If not, continue, else return
            if 'https://' in a_in[0] or 'https://' in a_in[1]:
                await self.client.send_message(ctx.message.channel, "Invalid syntax!"); return
            else:
                quiz_obj['link'] = 'n/a'
        quiz_obj['question'] = a_in[0]
        quiz_obj['answer'] = a_in[1].lower()
        quiz_obj['user_id'] = ctx.message.author.id
        quiz_obj['server_id'] = ctx.guild.id
        quiz_obj['win'] = '0'; quiz_obj['lose'] = '0'
        if self.guess_dictall['id_count']:
            quiz_obj['id'] = str(int(self.guess_dictall['id_count']) + 1)
            self.guess_dictall['id_count'] = quiz_obj['id']
        else:
            self.guess_dictall['id_count'] = "0"
            quiz_obj['id'] = '0'

        #Check if there's the server_id's <layer_server>. If true, next
        if quiz_obj['server_id'] in list(self.guess_dictall.keys()):
            #Check if there's a user_id's <layer_user>. If true, append <quiz_obj> to the <guess_socketall>.
            if quiz_obj['user_id'] in list(self.guess_dictall[quiz_obj['server_id']].keys()):
                self.guess_dictall[quiz_obj['server_id']][quiz_obj['user_id']].append(quiz_obj)
            #Else, put the <quiz_obj> in the socket <guess_socketall>, then put <guess_socketall> in a new <layer_user>
            else:
                guess_socketall = [quiz_obj]
                self.guess_dictall[quiz_obj['server_id']] = guess_socketall
        #Else, do the whole freaking thing, starting from create a new <layer_server>
        else:
            #Put the <quiz_obj> in the socket <guess_socketall>
            guess_socketall.append(quiz_obj)
            
            #Nest <guess_socketall> inside 2 dict
            layer_user = {}
            layer_user[quiz_obj['user_id']] = guess_socketall
            self.guess_dictall[quiz_obj['server_id']] = layer_user

        await self.client.send_message(ctx.message.channel, f"Added quiz with id `{quiz_obj['id']}`")
        
        #Update the .json
        await self.client.loop.run_in_executor(None, self.updatingall)

        await self.client.say(":white_check_mark: Successfully added!")

        #  { 'server_id':
        #      { 'user_id':
        #          [ <quiz_obj> ] <----- <guess_socketall>
        #      }
        #  }
    
    @commands.command(pass_context=True)
    @commands.cooldown(1, 10, type=BucketType.user)
    async def guess_ser(self, ctx):
        hint_list = []; hint = ''

        #Get a random <quiz_obj> from <guess_socketall> from random <layer_user> from SERVER'S id
        try:
            layer_user = self.guess_dictall[ctx.guild.id]
        except KeyError:
            await self.client.send_message(ctx.message.channel, "Your server does not have any quizes!")
        quiz_obj = random.choice(layer_user[random.choice(list(layer_user.keys()))])
        print(quiz_obj)
        #Get user from quiz_obj['user_id']
        user = await self.client.get_user_info(quiz_obj['user_id'])

        #Get pack (image_link/text) from the guess_dict, wrap it in the embed. Then send the embed.
        #pack = random.choice(self.guess_dict[key])
        msg_box = discord.Embed(
            title = quiz_obj['question'],
            colour = discord.Colour(0x011C3A),
        )
        msg_box.set_footer(text=f"Quiz id {quiz_obj['id']} by {user.name}", icon_url=user.avatar_url)
        if quiz_obj['link'] != 'n/a':
            msg_box.set_image(url=quiz_obj['link'])                     #Image quiz
        else: pass                                                      #Text quiz
        await self.client.say(embed=msg_box)

        #Generate the hint. Then send it.
        for c in quiz_obj['answer']:
            if c == ' ': hint_list.append(c)
            else: hint_list.append('-')
        hint = ''.join(hint_list)
        await self.client.say(f":bulb: **HINT:** {hint}")
        
        #Check in wait_for_message (This must be put after the <quiz_obj> is created)
        def msg_lower(msg):
            if msg.content.lower() == quiz_obj['answer']:
                return True
            else:
                return False

        #Wait for the answer
        answer = await self.client.wait_for_message(timeout=15, channel=ctx.message.channel, author=ctx.message.author, check=msg_lower)
        if not answer:
            await self.client.say("**Duh loseerrrrr**")
            quiz_obj['lose'] = str(int(quiz_obj['lose']) + 1)
        elif answer.content.lower() == quiz_obj['answer'].lower():
                await self.client.say("**Congrats!!!**")
                quiz_obj['win'] = str(int(quiz_obj['win']) + 1)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 10, type=BucketType.user)
    async def guess_all(self, ctx):
        hint_list = []; hint = ''

        #Get a random <quiz_obj> from <guess_socketall> from random <layer_user> from random <layer_server>
        b = list(self.guess_dictall.keys()); b.remove('id_count')
        layer_user = self.guess_dictall[random.choice(b)]
        quiz_obj = random.choice(layer_user[random.choice(list(layer_user.keys()))])
        print(quiz_obj)
        #Get user from quiz_obj['user_id']
        user = await self.client.get_user_info(quiz_obj['user_id'])

        #Get pack (image_link/text) from the guess_dict, wrap it in the embed. Then send the embed.
        #pack = random.choice(self.guess_dict[key])
        msg_box = discord.Embed(
            title = quiz_obj['question'],
            colour = discord.Colour(0x011C3A),
        )
        msg_box.set_footer(text=f"Quiz id {quiz_obj['id']} by {user.name}", icon_url=user.avatar_url)
        if quiz_obj['link'] != 'n/a':
            msg_box.set_image(url=quiz_obj['link'])                     #Image quiz
        else: pass                                                      #Text quiz
        await ctx.send(embed=msg_box)

        #Generate the hint. Then send it.
        for c in quiz_obj['answer']:
            if c == ' ': hint_list.append(c)
            else: hint_list.append('-')
        hint = ''.join(hint_list)
        await self.client.say(f":bulb: **HINT:** {hint}")
        
        #Check in wait_for_message (This must be put after the <quiz_obj> is created)
        def msg_lower(msg):
            if msg.content.lower() == quiz_obj['answer']:
                return True
            else:
                return False

        #Wait for the answer
        answer = await self.client.wait_for_message(timeout=15, channel=ctx.message.channel, author=ctx.message.author, check=msg_lower)
        if not answer:
            await self.client.say("**Duh loseerrrrr**")
            quiz_obj['lose'] = str(int(quiz_obj['lose']) + 1)
        elif answer.content.lower() == quiz_obj['answer'].lower():
                await self.client.say("**Congrats!!!**")
                quiz_obj['win'] = str(int(quiz_obj['win']) + 1)

    @commands.command(pass_context=True, aliases=['quizes'])
    @commands.cooldown(1, 10, type=BucketType.user)
    async def guesses_all(self, ctx):
        info = ''

        #srvr is <layer_server>
        srvr_gen = (self.guess_dictall[s] for s in list(self.guess_dictall.keys()) if s == ctx.guild.id)
        srvr = list(srvr_gen)[0]
        #usr is <guess_socketall>
        usr_gen = (srvr[u] for u in list(srvr.keys()) if u == ctx.message.author.id)
        usr = list(usr_gen)[0]
        #qo is <quiz_obj>
        for qo in usr:
            try:    
                proportion = (float(qo['win'])/float(sum([int(qo['win']), int(qo['lose'])])))*100
            except ZeroDivisionError: proportion = 0
            info += f"| `{qo['id']}`:  `{qo['question']}` with `{proportion}%` win percentage\n"
        
        box_small = discord.Embed(
            title = f":notepad_spiral: List of **{ctx.message.author.name}**'s quizes",
            description = f"{info}",
            colour = discord.Colour(0x011C3A)
        )
        await self.client.say(embed=box_small)


    async def quefe(self, query, args=None, type='one'):
        """args ---> tuple"""

        await _cursor.execute(query, args=args)
        if type == 'all': resu = await _cursor.fetchall()
        else: resu = await _cursor.fetchone()
        return resu

    def updating(self):
        with open('game/q/q.json', 'w') as f:
            json.dump(self.guess_socket, f, indent=4)

    def updatingall(self):
        with open('game/q/qall.json', 'w') as f:
            json.dump(self.guess_dictall, f, indent=6)
    
    """
    def guess_socket_plugin(self):
        with open('game/q/q.json') as f:
            try:
                self.guess_socket = json.load(f)
            except: print("ERROR at <guess_dict_plugin()>")

    def guess_socket_pluginall(self):
        with open('game/q/qall.json') as f:
            try:
                self.guess_dictall = json.load(f)
            except: print("ERROR at <guess_dict_pluginall()>")
    """


def setup(client):
    client.add_cog(guess(client))



