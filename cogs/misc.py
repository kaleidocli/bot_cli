import sys
import random
from io import BytesIO
import asyncio
from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors
import aiohttp
from PIL import Image
from transliterate import translit

from utils import checks


class misc(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.minikeylist = []
        self.msg_bank = []
        self.char_dict = {'a': '\U0001f1e6', 'b': '\U0001f1e7', 'c': '\U0001f1e8', 'd': '\U0001f1e9', 'e': '\U0001f1ea', 'f': '\U0001f1eb', 'g': '\U0001f1ec', 'h': '\U0001f1ed', 'i': '\U0001f1ee', 'j': '\U0001f1ef', 'k': '\U0001f1f0',
            'l': '\U0001f1f1', 'm': '\U0001f1f2', 'n': '\U0001f1f3', 'o': '\U0001f1f4', 'p': '\U0001f1f5', 'q': '\U0001f1f6', 'r': '\U0001f1f7', 's': '\U0001f1f8', 't': '\U0001f1f9', 'u': '\U0001f1fa', 'v': '\U0001f1fb', 'w': '\U0001f1fc', 'x': '\U0001f1fd', 'y': '\U0001f1fe', 'z': '\U0001f1ff'}
        self.msg_bank = []; self.memo_mode = False; self.cur_learning = []
        self.chrisId = 427063788546555916
        self.chrisOwnerId = 246938839720001536
        self.chrisGuildId = 336642139381301249
        self.chrisAlphaSample = tuple(" abcdefghijklmnopqrstuvwxyz1234567890-+.,")
        self.userAlphaSample = {
            'е': 'e',
            'с': 'c'
        }
        self.predictedAnswer = ''
        self.chrisQuizPrefix = "My sentence is: "
        self.isAntiChrisOn = False
        self.chrisLatestQuiz = None
        self.antiChrisMsgBank = []

        self.guesser = []

        self.act_gif = {
                'yay': 'https://imgur.com/dvKPLJH.gif',
                'mumu': 'https://imgur.com/UEA7ME0.gif',
                'yaya': 'https://imgur.com/BsHjshO.gif',
                'huray': 'https://imgur.com/oayh25M.gif',
                'nom': 'https://imgur.com/QzH4Irq.gif',
                'shake': 'https://imgur.com/yG86BOm.gif',
                'eto': 'https://imgur.com/nmjwmiW.gif',
                'sneak': 'https://imgur.com/QzotxLT.gif',
                'scared': 'https://imgur.com/6a1v0oK.gif',
                'aaa': 'https://imgur.com/2xS3kXK.gif',
                'snack': 'https://imgur.com/eCfbVBK.gif',
                'zzz': 'https://imgur.com/N1Sv2hC.gif',
                'confused': 'https://i.imgur.com/vWz8KOL.gif',
                'roger': 'https://i.imgur.com/2pN0IfK.gif',
                'angry': 'https://i.imgur.com/wnX6kax.gif',
                'arigatou': 'https://i.imgur.com/wGiluXP.gif',
                'welcome': 'https://i.imgur.com/rPxyRO0.gif',
                'thumbsup': 'https://imgur.com/XZ5gQ4r.gif',
                'sad': 'https://imgur.com/ZeuaOeB.png'
                }






# ================== EVENTS ==================

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.isAntiChrisOn and message.guild.id == self.chrisGuildId:
            # Record all message
            self.antiChrisMsgBank.insert(0, message)

            if message.author.id == self.chrisId:
                # Answer
                if self.predictedAnswer and message.mentions:
                    # Get winner
                    winner = None
                    for u in message.mentions:
                        if u.id not in (self.chrisId, self.chrisOwnerId):
                            winner = u
                            break
                    if not winner:
                        print("Winner not found")
                        return
                    # Get last message of winner
                    ansMsg = None
                    for msg in self.antiChrisMsgBank:
                        if msg.author.id == winner.id:
                            if len(msg.content) >= 25:
                                ansMsg = msg.content
                    if not ansMsg:
                        print("ansMsg not found")
                        return
                    print(f"<!> ansMsg: {ansMsg}")
                    await self.learnSingularity(self.chrisLatestQuiz, ansMsg)

                # Quiz
                elif message.content.startswith(self.chrisQuizPrefix):
                    # Reset
                    self.predictedAnswer = ''

                    notAplha = []
                    singularities = []
                    quizContent = message.content[len(self.chrisQuizPrefix):]
                    # Scan n Clean notAphabet chars
                    for c in quizContent:
                        if not c.isalpha() and c != ' ':
                            notAplha.append(c)
                    for n in notAplha:
                        quizContent = quizContent.replace(n, '')
                    
                    # Clean singularities               # Singularity is a alphabet character that has the same looking, but different tham normal LATIN character
                    # quizContent = translit(u"{}".format(quizContent), reversed=True)

                    # Record singularities          # Singularity is a alphabet character that has the same looking, but different tham normal LATIN character
                    print("HEREEEEE 1")
                    self.chrisLatestQuiz = quizContent
                    singularities = await self.scanSingularity(quizContent)
                    print("HEREEEEE 2")
                    quizContent = await self.fixSingularity(quizContent, singularities)
                    self.predictedAnswer = quizContent

                    await message.channel.send("**`Predicted answer`** -- {}\n**`Singularities`** -- {}".format(quizContent, ' - '.join(singularities)))

    async def scanSingularity(self, s):
        sing = []

        # Record
        for c in s:
            if c not in self.chrisAlphaSample:
                sing.append(c)
        return list(set(sing))

    async def fixSingularity(self, s, sings):
        for sing in sings:
            # Sing. is recorded
            print("HEREEEEE 3")
            try:
                s = s.replace(sing, self.userAlphaSample[sing])
            # If not, leave it be
            except KeyError:
                pass
        return s

    async def learnSingularity(self, quizContent, trueAnswer):
        if not self.predictedAnswer:
            return ()
        for cPre, cAns, cQui in zip(self.predictedAnswer, trueAnswer, quizContent):
            if cAns != cAns:
                self.userAlphaSample[cQui] = cAns
                print(f"<!> [{cPre}] wrong --- setting Sing's key [{cQui}] -> [{cAns}]")







# ================== TRIVIA SYS ==================


    @commands.command()
    async def ping(self, ctx, *args):
        embed = discord.Embed(description=f":stopwatch: **`-{round(self.client.latency*1000, 2)}`** ms", color=0xFFC26F)
        await ctx.send(embed=embed)

    @commands.command()
    async def aknalumos(self, ctx, *args):
        await ctx.send("Aknalumos' best friend.")


    @commands.command()
    @checks.check_author()
    async def braillize(self, ctx, *args):
        session = aiohttp.ClientSession()
        raw = list(args)
        if raw:
            try: 
                size = int(raw[0])
                if size < 2: size = 2
            except: size = 2
        else: size = 2
        package = ctx.message.attachments
        print(package)
        
        def magic(Image_obj, size):
            average = lambda x: sum(x)/len(x) if len(x) > 0 else 0
            start = 0x2800
            char_width = size             #DF=10
            char_height = char_width * 2
            dither = 0              #DF=10
            sensitivity = 0.72       #DF=0.8
            char_width_divided = round(char_width / 2)
            char_height_divided = round(char_height / 4)
            #filename = "../Pictures/Anthony Foxx official portrait.jpg"
            #filename = "../Pictures/bait k.jpg"
            #filename = "sample.png"

            base = Image_obj
            match = lambda a, b: a < b if "--invert" in sys.argv else a > b
            def image_average(x1, y1, x2, y2):
                return average([average(base.getpixel((x, y))[:3]) for x in range(x1, x2) for y in range(y1, y2)])
            def convert_index(x):
                return {3: 6, 4: 3, 5: 4, 6: 5}.get(x, x)

            seq = ''; allseq = ''

            for y in range(0, base.height - char_height - 1, char_height):
                for x in range(0, base.width - char_width - 1, char_width):
                    byte = 0x0
                    index = 0
                    for xn in range(2):
                        for yn in range(4):
                            avg = image_average(x + (char_height_divided * xn), y + (char_width_divided * yn), x + (char_height_divided * (xn + 1)), y + (char_width_divided * (yn + 1)))
                            if match(avg + random.randint(-dither, dither), sensitivity * 0xFF):
                                byte += 2**convert_index(index)
                            index += 1
                    # ONE ROW
                    seq = seq + chr(start + byte)
                # ALL ROWS
                allseq = allseq + seq + '\n'
                seq = ''
            return allseq
        #H1068 W800

        async with session.get(package[0]['proxy_url']) as resp:
            bmage = await resp.read()
            bmg = BytesIO(bmage)
            #img = Image.frombytes('RGBA', (package[0]['height'], package[0]['width']), bmage)
            img = Image.open(bmg)

            a = magic(img, size)
            with open('imaging/ascii_out.txt', 'w', encoding='utf-8') as f:
                f.write(a)
            await ctx.send_file(file=('result.png', 'imaging/ascii_out.txt'))
            print('DONE')
    
    @commands.command()
    async def say(self, ctx, *args):
        raw = list(args)

        if not args: await ctx.send('Say WOTTTTT??'); return

        if random.choice([True, False]):
            random.shuffle(raw)
            try: await ctx.message.delete()
            except discordErrors.Forbidden: pass
            await ctx.send(f"{' '.join(raw)}".lower().capitalize())
        elif self.msg_bank:
            try: 
                temp = random.choice(self.msg_bank)
                try: await ctx.message.delete()
                except discordErrors.Forbidden: pass
                await ctx.send(temp.content)
            except AttributeError:
                temp = random.choice(self.msg_bank)
                try: await ctx.message.delete()
                except discordErrors.Forbidden: pass
                await ctx.send(embed=temp.embeds[0])
        else:
            random.shuffle(raw)
            try: await ctx.message.delete()
            except discordErrors.Forbidden: pass
            await ctx.send(f"{' '.join(raw)}".lower().capitalize())

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.guild)
    async def stick(self, ctx, *args):
        try: msg = await ctx.channel.get_message(int(args[0]))
        except IndexError: await ctx.send("Missing `message_id`"); return
        except ValueError: await ctx.send("Invalid `message_id`"); return

        try: sticker = ''.join(args[1:])
        except IndexError: await ctx.send("Missing `sticker`"); return

        count = 0; limit = 10
        for stick in sticker:
            if count > limit: return
            await msg.add_reaction(self.char_dict[stick.lower()])
            count += 1

    @commands.command(aliases=['ctd'])
    @checks.check_author()
    async def countdown(self, ctx, *args):
        try: duration = int(args[0])
        except IndexError: await ctx.send(":warning: Missing `duration`"); return
        except TypeError: await ctx.send(":warning: Invalid `duration`"); return

        msg_a = ' '.join(args[1:])
        try: answer = msg_a.split(' || ')[1]
        except IndexError: answer = ''
        try: msg = msg_a.split(' || ')[0]
        except IndexError: msg = msg

        for tick in range(duration):
            await ctx.send(f"**{msg}** :stopwatch: **`{duration - tick}`** secs", delete_after=1)
            await asyncio.sleep(1)

        if answer: await ctx.send(answer)

    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.guild)
    async def typestuff(self, ctx, *args):
        try: await self.client.get_channel(int(args[0])).trigger_typing(); return
        except (IndexError, TypeError): pass
        await ctx.trigger_typing()

    @commands.command()
    @commands.cooldown(1, 2, type=BucketType.user)
    async def act(self, ctx, *args):

        if not args: await ctx.send(f"`{'` `'.join(self.act_gif.keys())}`"); return

        temb = discord.Embed(colour=0x36393E)
        try: temb.set_image(url=self.act_gif[args[0]])
        except KeyError: return
        await ctx.send(embed=temb)


    @commands.command()
    @commands.cooldown(1, 10, type=BucketType.guild)
    async def minikey(self, ctx, *args):
        max_player = 3
        players = {}

        # Players get
        try:
            max_player = int(args[0])
            if max_player < 2: max_player = 2
        except (ValueError, IndexError): pass

        if ctx.channel.id in self.minikeylist: await ctx.send(":warning: Game's already started in this channel!"); return
        self.minikeylist.append(ctx.channel.id)

        introm = await ctx.send(f":key:**`{max_player}`**:key: `minigame`|**WHO GOT THE KEY** :key:**`{max_player}`**:key:")
        await introm.add_reaction('\U0001f511')
        await asyncio.sleep(1)
        def RC(reaction, user):
            return reaction.emoji == '\U0001f511' and user.id not in list(players.keys())

        # Queueing
        while True:
            try: pack = await self.client.wait_for('reaction_add', timeout=10, check=RC)       # reaction, user
            except asyncio.TimeoutError:
                if len(list(players.keys())) >= 3: max_player = len(list(players.keys()))
                else: await ctx.send(f":warning: Requires **{max_player}** to start!"); self.minikeylist.remove(ctx.channel.id); return

            cur_player = max_player
            players[pack[1].id] = [False, pack[1]]
            await introm.edit(content=introm.content+f"\n:key: [**{pack[1].name}**] has joined the game.")
            if len(list(players.keys())) == max_player: break

        # Whisper
        while True:
            KEYER = random.choice(list(players.keys()))
            players[KEYER] = [True, players[KEYER][1]]
            try: await players[KEYER][1].send(":key: <---- *Keep it*"); break
            except discordErrors.Forbidden: pass

        await ctx.send(f":key::key::key: Alright, **{max_player} seekers!** Ping who you doubt. Ping wrong, you're dead, or else, hoo-ray~~ **GAME START!!**")

        def MC(message):
            try: tar = message.mentions[0]
            except (TypeError, IndexError): return False
            return message.author.id in list(players.keys()) and tar.id in list(players.keys())

        while True:
            try: resp = await self.client.wait_for('message', timeout=180, check=MC)
            except asyncio.TimeoutError: await ctx.send(":warning: Game ended due to afk."); break
            
            # SEEKER
            if not players[resp.author.id][0]:
                if players[resp.mentions[0].id][0]: await ctx.send(f"<:laurel:495914127609561098> **SEEKER WON!** Congrats, {resp.author.mention}! You caught the *keeper* ----> ||{resp.mentions[0]}||!!"); break
                else:
                    await ctx.send(f"{resp.author.mention}... ***OOF***"); cur_player -= 1
                    del players[resp.author.id]
            
            # KEEPER
            else:
                pock = players[resp.mentions[0].id]
                if pock[0]: await ctx.send(f"<:laurel:495914127609561098> **SEEKER WON!** The *keeper* killed themselves.. GG {resp.author.mention}"); break
                else:
                    await ctx.send(f"{pock[1].mention}... ***KILLED***"); cur_player -= 1
                    del players[pock[1].id]

            if cur_player == 1:
                await ctx.send(f"<:laurel:495914127609561098> **KEEPER WON!** Nice one, {players[KEYER][1].mention}!"); break

        self.minikeylist.remove(ctx.channel.id)

    @commands.command()
    @checks.check_author()
    async def memorize(self, ctx, *args):

        # Console
        try:
            if args[0] == 'stop':
                if not self.cur_learning[0].cancelled():
                    self.cur_learning[0].cancel()
                    await ctx.send(":white_check_mark:")
                    self.memo_mode = False; return
                else: await ctx.send(":x:"); return
        except IndexError: pass

        # Memo mode check
        if self.memo_mode: await ctx.send("Chotto chotto, i've already been memorizing another channel!"); return

        # Channel's id      ||      Default count
        try: channel_id = int(args[0])
        except IndexError: channel_id = ctx.channel.id
        except ValueError: await ctx.send(":warning: Invalid channel's id"); return
        try: 
            df_count = int(args[1])
            if df_count >= 1000:
                df_count = int(args[1])
        except (IndexError, ValueError): df_count = 25

        # Init
        await ctx.send(f"Memorizing anxima {df_count} of channel **`{channel_id}`**...")
        self.memo_mode = True
        self.msg_bank = []
        a = self.client.loop.create_task(self.memorizing(channel_id, df_count))
        try: self.cur_learning[0] = a
        except IndexError: self.cur_learning.append(a)

    @commands.command()
    @commands.cooldown(1, 10, type=BucketType.guild)
    async def guessNumber(self, ctx, *args):
        if ctx.author.id in self.guesser:
            await ctx.send(":x: Finish your current game :>")
            return

        try:
            limit = int(args[0])
            if limit > 1000000000:
                limit = 1000000000
        except ValueError:
            return
        except IndexError:
            limit = 1000000000

        startPoint = datetime.now()
        guesses = 0
        number = random.randint(0, limit)
        
        await ctx.send(f"<a:question_spinning:643263711833882655> Guess a number within 0 to {limit:,}. (:arrow_double_up: means guess higher, :arrow_double_down: means guess lower)")
        while True:
            msg = await self.client.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=30)
            if msg.content == 'quit':
                await msg.add_reaction('\U000023f9')
                return
            try:
                guess = int(msg.content)
            except ValueError: continue

            if number > guess:
                await msg.add_reaction('\U000023eb')
            elif number < guess:
                await msg.add_reaction('\U000023ec')
            else:
                break

            guesses += 1

        endPoint = datetime.now()
        await ctx.send(f":tada: **Correct!** (`{(endPoint - startPoint).total_seconds():.2f} seconds` / `[{guesses} guesses]`)")



    @commands.command()
    async def suggest(self, ctx, *args):
        await ctx.send("Your idea was submitted!")







# ================== TOOLS ==================

    @commands.command()
    @checks.check_author()
    async def anti_chris(self, ctx, *args):
        if self.isAntiChrisOn:
            self.isAntiChrisOn = False
            self.antiChrisMsgBank = []
            await ctx.send(":x:")
        else:
            self.isAntiChrisOn = True
            await ctx.send(":white_check_mark:")

    @commands.command()
    @checks.check_author()
    async def uChrisBank(self, ctx, *args):
        try:
            self.userAlphaSample[args[0]] = args[1]
            await ctx.send(f"`{args[0]}` --> `{args[1]}`")
        except KeyError:
            pass



# ================== TOOLS ==================

    async def memorizing(self, channel_id, df_count):
        count = 0

        def C_check(m):
            return m.channel.id == channel_id

        while count < df_count:
            msg = await self.client.wait_for('message', check=C_check)

            # Mention check
            if msg.mentions: continue

            # Attachment check
            try: msg.content = msg.attachments[0].url
            except IndexError: pass
                
            print(count)
            self.msg_bank.append(msg)
            count += 1
        self.memo_mode = False



def setup(client):
    client.add_cog(misc(client))

