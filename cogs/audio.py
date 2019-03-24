import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import asyncio
import random
from time import sleep
from os import listdir
import os
from nltk import word_tokenize

def check_id():
    def inner(ctx):
        return ctx.author.id == 214128381762076672
    return commands.check(inner)

class audio:
    def __init__(self, client):
        self.client = client
        self.channel_socket = []
        self.player_socket = []
        self.task_socket = []
        self.voice_socket = []
        self.volo = []
        self.vol = 1.0

    async def on_ready(self):
        #Create <channel> object in a list
        self.channel_socket.append(self.client.get_channel('493467475493781504'))

    #Join the current <voice_channel> that the user's currently in
    @commands.command(aliases=['>in'])
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        self.channel_socket[0] = channel
        try: self.vc_id = channel.id
        except AttributeError: await ctx.send(":warning: Please connect to a voice channel!")

        #if voice_client != channel:
        #    await voice_client.move_to(channel)
        #else:
        try:
            await channel.connect()
            await ctx.send(f"```Successfully joined voice channel [{channel.name}]!```")
            if ctx.author.voice.channel:
                await self.play(ctx, await self.path_gen_from_FGR('audio/sfx/_asys/joining'))
        except discord.errors.ClientException:
            await ctx.send("You've already been in the same channel as Cli!")
            
    
    #Leave the current <voice_channel>
    @commands.command(pass_context=True, aliases=['>out'])
    async def leave(self, ctx):
        channel = ctx.author.voice.channel
        server = ctx.guild
        voice_client = server.voice_client
        await ctx.invoke(self.client.get_command("stop"))

        if voice_client.channel != channel: await ctx.send(':x:'); return
        if voice_client.is_playing(): await ctx.send('Unable to interupt the audio session'); return

        if ctx.author.voice.channel:
            await self.play(ctx, await self.path_gen_from_FGR('audio/sfx/_asys/leaving'))

        await asyncio.sleep(1)
        await voice_client.disconnect()
        await ctx.send(f"```Successfully disconected voice channel [{channel}]!```")

    #Stop the current audio
    @commands.command(aliases=['>sto'])
    async def stop(self, ctx):
        #Stop the player (and cancel tasks, if available)

        try:
            self.volo.pop(self.volo.index(ctx.guild))
        except ValueError: pass

        if self.player_socket:
            ctx.guild.voice_client.stop()
            try: self.player_socket.pop(0)
            except: pass
        else: await ctx.send("Nothing to be *stopped*!")
        print("<!> PLAYER STOPPED!")
        #if self.task_socket: self.task_socket[0].cancel(); print("<!> TASK STOPPED!")

    #Pause the current audio
    @commands.command(aliases=['>pau'])
    async def pause(self, ctx):
        #Stop the player (and cancel tasks, if available)
        try:
            if self.player_socket: self.player_socket[0].pause(); await ctx.send(":pause_button: **PAUSED**") 
            else: await ctx.send("Nothing to be *paused*!")
        except: await ctx.send("The song may have already been paused!")

    #Resume the currently paused audio
    @commands.command(aliases=['>res'])
    async def resume(self, ctx):
        #Stop the player (and cancel tasks, if available)
        try:
            if self.player_socket: self.player_socket[0].resume(); await ctx.send(":play_pause: **RESUMED**") 
            else: await ctx.send("Nothing to be *resumed*!")
        except: await ctx.send("The song may have already been playing!")

    #Volume adjusting
    @commands.command(pass_context=True, aliases=['>vol'])
    async def volume(self, ctx, *args):
        raw = list(args)
        a = float(raw[0])
        try:
            if a >= 0 and a <= 200:
                self.vol = a/100
                if self.player_socket:
                    if ctx.guild.voice_client.is_playing():
                        self.player_socket[0].volume = a/100
                await ctx.send(f":white_check_mark: Volume set to {a}%")
            else: await ctx.send("Please give a value from `0` - `200` (1 == 1%).")
        except TypeError:
            await ctx.send("Please use an `integer`.")

    @commands.command()
    async def move_here(self, ctx):
        try: ctx.guild.voice_client.move_to(ctx.author.VoiceState.channel.id)
        except: pass

    @commands.command(pass_context=True)
    @commands.cooldown(1, 2.5, type=BucketType.channel)
    async def cli(self, ctx, *args):
        raw = list(args)
        if not ctx.author.voice.channel:
            await ctx.send(f":warning: Please join a voice channel to use this command, {ctx.author.mention}!")
        try: 
            if ctx.guild.voice_client.is_playing(): await ctx.send("Please wait for the audio to end, or use `-stop` to end the current audio."); return
        except AttributeError: await ctx.author.voice.channel.connect()

        try:
            if args[0] == 'stop': self.volo.pop(self.volo.index(ctx.guild))
        except ValueError: await ctx.send("Stop WHAT?"); return

        async def pathenerator(raw):
            paths = []
            for voice_tag in raw:
                #Random audio file name.
                voice_tag = voice_tag.lower()
                if voice_tag == 'moan':
                    paths.append(await self.path_gen_from_FGR('audio/sfx/moan'))  
                elif voice_tag == 'asillya':
                    paths.append(await self.path_gen_from_FGR('audio/bot_voice/illya/Dialogue'))      
                elif voice_tag == 'astohsaka':
                    paths.append(await self.path_gen_from_FGR('audio/bot_voice/rin_tohsaka/Dialogue'))             
                elif voice_tag == 'asaudrey':
                    paths.append(await self.path_gen_from_FGR('audio/bot_voice/Huney_Pop/audrey'))     
                elif voice_tag == 'asbeli':
                    paths.append(await self.path_gen_from_FGR('audio/bot_voice/Huney_Pop/beli'))     
                elif voice_tag == 'asaiko':
                    paths.append(await self.path_gen_from_FGR('audio/bot_voice/Huney_Pop/aiko'))     
                elif voice_tag == 'asceleste':
                    paths.append(await self.path_gen_from_FGR('audio/bot_voice/Huney_Pop/celeste'))   
                elif voice_tag == 'asjessie':
                    paths.append(await self.path_gen_from_FGR('audio/bot_voice/Huney_Pop/jessie'))                
                    
                elif voice_tag == 'gig':
                    paths.append(await self.path_gen_from_FGR('audio/sfx/gig'))  
                elif voice_tag == 'ohaiyo':
                    paths.append(await self.path_gen_from_FGR('audio/sfx/ohaiyo'))  
                elif voice_tag == 'konichiwa':
                    paths.append(await self.path_gen_from_FGR('audio/sfx/konichiwa'))  
                elif voice_tag == 'hen':
                    paths.append(await self.path_gen_from_FGR('audio/sfx/hen'))
                elif voice_tag == 'hi':
                    paths.append(await self.path_gen_from_FGR('audio/sfx/hi'))  
                elif voice_tag == 'thanks':
                    paths.append(await self.path_gen_from_FGR('audio/sfx/thanks'))

                #Specific audio file name.
                elif voice_tag.startswith('meme'):
                    if voice_tag == 'meme':
                        paths.append(await self.path_gen_from_FGR('audio/meme'))  
                    else:
                        try: fname = voice_tag.split('=')[1]
                        except IndexError: await ctx.send(f"{ctx.author.mention}, you're missing `=`. E.g `meme=error` not `meme error`")
                        paths.append(f'audio/meme/{fname}.mp3')
                #elif raw[0] == 'gif':

                #elif voice_tag == 'playpath' and len(raw) >= 2:
                #    path = ' '.join(raw[2:])
                #else:
                #    await ctx.send(":no_entry: Please use the correct syntax!")

            return paths

        try:
            if raw[0] == 'loop' and len(args) > 1 and ctx.guild not in self.volo:
                raw.pop(0)
                self.volo.append(ctx.guild)
                while ctx.guild in self.volo:
                    paths = await pathenerator(raw)
                    await self.appendingplayer_engine(ctx, paths)
            else:
                paths = await pathenerator(raw)
                await self.appendingplayer_engine(ctx, paths)
        except IndexError:
            paths = await pathenerator(raw)
            await self.appendingplayer_engine(ctx, paths)

    @commands.command(pass_context=True)
    @check_id()
    async def yolo(self, ctx, *args):
        #pler = client.loop.create_task(get_play_vc(ctx, "audio/bot_voice/rin_tohsaka/Dialogue"))
        path_in="D:/____ Green Corner ____/Med/Artista/Coldplay"
        delay = 4
        raw = list(args)
        print(raw)
        if raw:
            if raw[0] == 'Med':
                sub_path = ' '.join(raw[1:])
                path_in = f"D:/____ Green Corner ____/Med/{sub_path}"
            elif int(raw[0]) == 1:
                delay = int(raw[0])
                sub_path = ' '.join(raw[1:])
                path_in = f"D:/____ Green Corner ____/Med/{sub_path}"
            else: path_in = ' '.join(raw)
        print(path_in)
        #Create and put the task in the <task_socket> list
        #await self.get_play_vc(ctx, path_in, delay)
        pler = self.client.loop.create_task(self.get_play_vc(ctx, path_in, delay))
        if self.task_socket:
            self.task_socket[0] = pler
        else:
            self.task_socket.append(pler)

    @commands.command(pass_context=True)
    @check_id() 
    async def dir(self, ctx, *args):
        raw = list(args)
        available = ['audio', 'music']
        type = 'path'
        if not raw:
            await ctx.send(f"**Choose `dir [{' | '.join(available)}]` or `dir [browse_type] [{' | '.join(available)}] [your_path]`** \n| arg[browse_type]: Browse `path` or `file` \n| arg[music|audio|..]: Root directory \n| arg[your_path]: Path (e.g. d1\d2\d3. Don't put `\` at the front or end, don't include the root dir. \n**Reading result** \n| <a/> --- Root \n| .\path1 --- Directed path of the Root \n| .\\\path2 ---- Inner path")
            return
        try:
            if raw[0] in available:
                #Scan through the chosen dir
                # Get mother
                if raw[0] == 'music':
                    mother = "D:\____ Green Corner ____\Med"
                elif raw[0] == 'audio':
                    mother = 'audio'
                # Get type and path
                try:
                    # Check if there's type
                    if raw[1] in ['path', 'file']:
                        type = raw[1]
                        # Get path
                        if raw[2]:
                            if raw[1].startswith("""\""""): mother = mother + ' '.join(raw[2:])
                            else: mother = f"D:\____ Green Corner ____\Med\{' '.join(raw[2:])}"                            
                    # Get path
                    else: 
                        if raw[1].startswith("""\""""): mother = mother + ' '.join(raw[1:])
                        else: mother = f"D:\____ Green Corner ____\Med\{' '.join(raw[1:])}"
                except IndexError: pass

                tree = await self.client.loop.run_in_executor(None, self.scan, mother, type)
                msg = await self.dir_pagemaker(ctx, tree, mother)
                await asyncio.sleep(20)
                await msg.delete()
            else: await ctx.send(f"Please use the right syntax `dir [{' | '.join(available)}] [browse_mode] [your_path]`")
        except IndexError:
            await ctx.send(f"Missing 'root_dir' argument!"); return
    
    @commands.command(pass_context=True)
    async def yplay(self, ctx, *args):
        url = ''.join(list(args)[0])
        await self.ytplay(ctx, url)

    @commands.command(pass_context=True)
    async def yplay_test(self, ctx, *args):
        url = ''.join(list(args)[0])
        channel = ctx.author.voice.channel
        server = ctx.message.guild
        #Get the voice_client
        try:
            vc = await channel.connect()
            await ctx.send(f"```Successfully joined voice channel [{channel.name}]!```")
        except:
            vc = server.voice_client
            ctx.send("Cli's already been in the same channel as you!")
            pass
        opts = {'forcejson': True}
        #player = await vc.create_ytdl_player(url, ytdl_options=opts)
        vc.start()

    @commands.command(pass_context=True)
    async def tts(self, ctx, *args):
        paths = []

        raw = word_tokenize(' '.join(args))

        for voice_tag in raw:
            paths.append(f"audio/human_voice/{voice_tag}.mp3")
        await self.appendingplayer_engine(ctx, paths)




    async def dir_pagemaker(self, ctx, list, mother):

        def makeembed(top, least, pages, currentpage):
            line = ''

            line = f"-------------------- oo --------------------\n**" 
            for i in list[top:least]:
                line = line + f"{i}"
            line = line + "**-------------------- oo --------------------" 
            reembed = discord.Embed(title = f"<{mother[2:]}\>", colour = discord.Colour(0x011C3A), description=line)
            reembed.set_footer(text=f"Page {currentpage} of {pages}")
            return reembed
            #else:
            #ctx.send("*Nothing but dust here...*")
    
        async def attachreaction(msg):
            await msg.add_reaction("\U000023ee")    #Top-left
            await msg.add_reaction("\U00002b05")    #Left
            await msg.add_reaction("\U000027a1")    #Right
            await msg.add_reaction("\U000023ed")    #Top-right

        pages = len(list)//10
        if len(list)%10 != 0: pages += 1
        currentpage = 1
        myembed = makeembed(0, 10, pages, currentpage)
        msg = await ctx.send(embed=myembed)
        await attachreaction(msg)

        while True:
            try:    
                reaction, user = await self.client.wait_for_reaction(message=msg, timeout=30)
                if reaction.emoji == "\U000027a1" and user.id == ctx.author.id and currentpage < pages:
                    currentpage += 1
                    myembed = makeembed(currentpage*10-10, currentpage*10, pages, currentpage)
                    await self.client.clear_reactions(msg)
                    await self.client.edit_message(msg, embed=myembed)
                    await attachreaction(msg)
                elif reaction.emoji == "\U00002b05" and user.id == ctx.author.id and currentpage > 1:
                    currentpage -= 1
                    myembed = makeembed(currentpage*10-10, currentpage*10, pages, currentpage)
                    await self.client.clear_reactions(msg)
                    await self.client.edit_message(msg, embed=myembed)
                    await attachreaction(msg)
                elif reaction.emoji == "\U000023ee" and user.id == ctx.author.id and currentpage != 1:
                    currentpage = 1
                    myembed = makeembed(currentpage*10-10, currentpage*10, pages, currentpage)
                    await self.client.clear_reactions(msg)
                    await self.client.edit_message(msg, embed=myembed)
                    await attachreaction(msg)
                elif reaction.emoji == "\U000023ed" and user.id == ctx.author.id and currentpage != pages:
                    currentpage = pages
                    myembed = makeembed(currentpage*10-10, currentpage*10, pages, currentpage)
                    await self.client.clear_reactions(msg)
                    await self.client.edit_message(msg, embed=myembed)
                    await attachreaction(msg)
            except TypeError: 
                pass

    def scan(self, mother, type='path'):
        end = []
        if type == 'path':
            for root, dirs, files in os.walk(mother, topdown=True):
                for name in dirs:
                    end.append(f".\{os.path.join(root.strip(mother), name)} \n")
        elif type == 'file':
            for root, dirs, files in os.walk(mother, topdown=True):
                for name in files:
                    end.append(f".\{os.path.join(root.strip(mother), name)} \n")
        return end


    # PROTOTYPE (DO NOT DELETE)
    #Play the path. This one is for other cmds
    async def play(self, ctx, path):
        channel = ctx.author.voice.channel
        server = ctx.message.guild
        try:
            vc = await channel.connect()
            await ctx.send(f"```Successfully joined voice channel [{channel.name}]!```")
        except:
            vc = server.voice_client
            #await ctx.send("Cli's already been in the same channel as you!")
            pass

        #Check if <player_socket> is not empty, else create and put in new player
        if self.player_socket:
            #Check if the player in <player_socket> is done, else return
            if not vc.is_playing():
                print(f"=======PLAYER is_done=========== {self.player_socket}")
                #Create a <player>. Then replace the old one in <player_socket>
                player = discord.FFmpegPCMAudio(path)
                self.player_socket[0] = player
            else: 
                await self.client.send_message(ctx.message.channel, "Please wait for the audio to end, or use `stop` to end the current audio.")
                return   
        else:
            player = discord.FFmpegPCMAudio(path)
            self.player_socket.append(player)
            print(f"=======PLAYER start=========== {self.player_socket}")
        
        #player.volume = self.vol                         #Volume set
        vc.play(player)

    #This one is specifically for <yolo> (Looping the audio)
    async def get_play_vc(self, ctx, folder, delay=4):
        self.volo.append(ctx.guild)
        while ctx.guild in self.volo:
            aufile_name = await self.file_gen_random(folder)
            await ctx.send(f":arrow_forward: **NOW PLAYING:** `{aufile_name.capitalize()}`")
            await self.play_vc(ctx, f"{folder}/{aufile_name}", delay)
            #await asyncio.sleep(delay)

    #This one is specifically for <yolo> (Looping the audio)
    async def play_vc(self, ctx, path, delay=4):
        await self.client.wait_until_ready()
        #Get <voice_client>. Either through connect or voice_client_in(server)
        try:
            #sthing = client.get_channel('493467475493781504')
            sthing = ctx.author.voice.channel
            print(type(sthing))
            vc = await sthing.connect()
            await self.client.send_message(ctx.message.channel, f"```Successfully joined voice channel [{vc.channel.name}]!```")
        except:
            #vc = asdlnfle.sdkjn(self.client.get_server(id='493467473870454785'))
            vc = ctx.guild.voice_client
            print(f"Channel: JOINED <{vc.channel.name}>")
            #await ctx.send("Cli's already been in the same channel as you!")
        async def a(vc, path):
            #Check if <player_socket> is not empty, else create and put in new player
            if self.player_socket:
                #Check if the player in <player_socket> is done, else return
                if not vc.is_playing():
                    print(f"=======PLAYER is_done=========== {self.player_socket}")
                    #Create a <player>. Then replace the old one in <player_socket>
                    self.player_socket[0] = discord.FFmpegPCMAudio(path)
                else: 
                    await self.client.send_message(ctx.message.channel, "Please wait for the audio to end.")
                    return   
            else:
                self.player_socket.append(discord.FFmpegPCMAudio(path))
                print(f"=======PLAYER start=========== {self.player_socket}")

            #player.volume = self.vol                         #Volume set
            vc.play(self.player_socket[0])
            #Check every x seconds if the player/stream is done. If True, move on, else, again
            while vc.is_playing():
                await asyncio.sleep(2)
                pass
        await a(vc, path)
        #Run a() in executor
        #await self.client.loop.run_in_executor(None, a, vc, path)

    #Play the path. This one is for other cmds
    async def ytplay(self, ctx, url):
        channel = ctx.author.voice.channel
        server = ctx.message.guild
        
        if not channel:
            await self.client.send_message(ctx.message.channel, ":warning: You're currently not in any voice channel."); return

        #Get the voice_client
        try:
            vc = await channel.connect()
            await ctx.send(f"```Successfully joined voice channel [{channel.name}]!```")
        except:
            vc = server.voice_client
            ctx.send("Cli's already been in the same channel as you!")
            pass

        #Check if <player_socket> is not empty, else create and put in new player
        if self.player_socket:
            #Check if the player in <player_socket> is done, else return
            if not vc.is_playing():
                print(f"=======YT_PLAYER is_done=========== {self.player_socket}")
                #Create a <player>. Then replace the old one in <player_socket>
                player = await vc.create_ytdl_player(url)
                self.player_socket[0] = player
            else: 
                await self.client.send_message(ctx.message.channel, "Please wait for the audio to end, or use `stop` to end the current audio.")
                return   
        else:
            player = await vc.create_ytdl_player(url)
            self.player_socket.append(player)
            print(f"=======YT_PLAYER start=========== {self.player_socket}")
        
        #player.volume = self.vol                         #Volume set
        await self.client.send_message(ctx.message.channel, f":arrow_forward: **NOW PLAYING:** `{player.title}` ||  `{player.duration//60}:{player.duration%60}`")
        vc.start()



    # Appending (queued) style player. Best for text-to-speech type, like <tts> and <cli>.
    # INCLUDE: <player_socket> check, <voice_socket> check, <user_in_any_channel> check
    async def appendingplayer_engine(self, ctx, paths):
        # CHECKERS
        try:
            if self.player_socket:
                if not self.player_socket[0].is_done:                 
                    await self.client.send_message(ctx.message.channel, "Another audio session is currently playing. Please wait or use `stop` to end the current audio.")
                    return
            if self.voice_socket:
                if not self.voice_socket[0].is_done:                 
                    await self.client.send_message(ctx.message.channel, "Another audio session is currently playing. Please wait or use `stop` to end the current audio.")
                    return
        except: pass 
        if not ctx.author.voice.channel:
            await self.client.send_message(ctx.message.channel, ":warning: You're currently not in any voice channel.")
        try:
            vc = await ctx.author.voice.channel.connect(ctx.author.voice.channel)
            await ctx.send(f"```Successfully joined voice channel [{ctx.author.voice.channel.name}]!```")
        except:
            vc = ctx.guild.voice_client
            #await ctx.send("Cli's already been in the same channel as you!")
            pass

        for path in paths:
            if await self.ttsplayer_get(ctx, vc, path): print(f"XXXX Unknown: {path}")

        await self.ttsplayer_play(ctx)
       
    #Text-to-speech player get, then append to voice_socket
    async def ttsplayer_get(self, ctx, vc, path):
        
        if not ctx.author.voice.channel: return               # Check if user in a voice_channel
        try:                                                                # If file not found, pass
            player = discord.FFmpegPCMAudio(path)
        except: return False
        self.voice_socket.append(player)

    #Get Text-to-speech player from voice_socket, then play
    async def ttsplayer_play(self, ctx):
        vc = ctx.guild.voice_client

        while self.voice_socket:
            voice = self.voice_socket.pop(0)
            #voice.volume = self.vol                         #Volume set

            #vc.play(discord.FFmpegPCMAudio(path))
            vc.play(voice)
            #Check every x seconds if the player/stream is done. If True, move on, else, again
            while vc.is_playing():
                await asyncio.sleep(0)
                pass




    #Generate random file's name from the path
    async def file_gen_random(self, path):
        file_name = ''
        file_name = await self.client.loop.run_in_executor(None, random.choice, await self.client.loop.run_in_executor(None, listdir, path))
        return file_name

    #Generate path directly from <file_gen_random>
    async def path_gen_from_FGR(self, folder):
        aufile_name = await self.file_gen_random(folder)
        return f"{folder}/{aufile_name}"
    

def setup(client):
    client.add_cog(audio(client))




