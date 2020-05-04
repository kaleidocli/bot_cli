import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors
from pymysql import err as mysqlError

import asyncio
import inspect






class avaDBC(commands.Cog):
    def __init__(self, client):
        from .avaTools import avaTools
        from .avaUtils import avaUtils

        self.client = client

        self.client.DBC['self'] = self
        self.client.DBC['meta'] = {}
        self.client.DBC['meta']['class'] = {}

        self.client.DBC['model_mail'] = {}
        self.client.DBC['player'] = {}
        self.client.DBC['dbcf'] = {}
        self.client.DBC['model_NPC'] = {}
        self.client.DBC['model_conversation'] = {}
        self.client.DBC['model_item'] = {}
        self.cacheMethod = {
            'model_NPC': self.cacheNPC,
            'model_conversation': self.cacheConversation,
            'model_mail': self.cacheMail,
            'personal_info': self.cachePersonalInfo,
            'model_mob': self.cacheMob,
            'model_item': self.cacheItem,
            'dbcf': self.cacheDBCF
        }

        print("|| DBC ---- READY!")






# ================== EVENTS ==================

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(9)
        await self.reloadSetup()

    async def reloadSetup(self):
        await self.cacheAll()
        print("|| DBC ---- RELOADED!")






# ================== DBC FUNC ==================
# <!> ATTENTION <!>
# All DBCF must be coroutine, and take *args as arguments
# All DBCF when called outside of avaDBC, must be called through avaTools.DBCF_executor()

    async def dbcf_sendMail(self, *args):
        """
            0: user_id
            1: mail_code

            raise AttributeError if user_not_found
            raise KeyError if mail_not_found
            raise ValueError if user_id is invalid
        """

        resp = await self.client.DBC['dbcf']['dbcf_getPersonalInfo'](self, args[0]).mailBox.updateMail(self.client, args[0], args[1])
        if isinstance(resp, list): await self.client.get_user(int(args[0])).send(f":envelope_with_arrow: You got mail! Use command `mail` to check it out! (Tags: ||`{'` `'.join(resp)}`||)")

    async def dbcf_getPersonalInfo(self, *args):
        """
            user_id:        (str) User's ID

            Returning False means user's not initialized in DB
        """

        user_id = args[0]

        # DBCF
        try:
            return self.client.DBC['personal_info'][user_id]
        
        # DB
        except KeyError:
            # Personal Info
            pi_res = await self.client.quefe(f"SELECT id, name, gender, dob FROM personal_info WHERE id='{user_id}';")
            try:
                p = c_PersonalInfo(pi_res)
            except ZeroDivisionError:
                return False

            # Init stuff
            await p.initMailBox(self.client, user_id)
            await p.initChildNick(self.client, user_id)

            return p






# ================== CACHE TOOL ==================

    async def cacheAll(self):
        for v in self.cacheMethod.values():
            await v()
        await self.cacheDBCC()



    # ================== DBC_CLASS ==================
    async def cacheDBCC(self):
        self.client.DBC['meta']['class'] = {
                                            'c_Conversation': c_Conversation,
                                            'c_NPC': c_NPC,
                                            'c_PersonalInfo': c_PersonalInfo,
                                            'c_Mail': c_Mail
                                            }



    # ================== DBC_FUNC ==================
    async def cacheDBCF(self):
        temp = [func for func in inspect.getmembers(avaDBC, predicate=inspect.iscoroutinefunction) if func[1].__name__.startswith('dbcf')]
        for t in temp:
            self.client.DBC['dbcf'][t[0]] = t[1]



    # ================== PI ==================
    async def cachePersonalInfo(self):
        self.client.DBC['personal_info'] = await self.cachePersonalInfo_tool()

    async def cachePersonalInfo_tool(self):
        temp = {}

        res = await self.client.quefe("SELECT id FROM personal_info;", type='all')
        for r in res:
            await asyncio.sleep(0)

            p = await self.dbcf_getPersonalInfo(r[0])

            # Finalize
            temp[p.id] = p

        return temp



    # ================== MAIL ==================
    async def cacheMail(self):
        self.client.DBC['model_mail'] = await self.cacheMail_tool()

    async def cacheMail_tool(self):
        temp = {}

        res = await self.client.quefe("SELECT mail_code, sender, content, tag FROM model_mail;", type='all')
        for r in res:
            await asyncio.sleep(0)
            temp[r[0]] = c_Mail(r)

        return temp



    # ================== NPC ==================
    async def cacheNPC(self):
        self.client.DBC['model_NPC'] = await self.cacheNPC_tool()
        self.client.DBC['model_NPC']['narrator'] = c_NPC(None, narrator=True)

    async def cacheConversation(self):
        self.client.DBC['model_conversation'] = await self.cacheConversation_tool()

    async def cacheNPC_tool(self):
        temp = {}

        res = await self.client.quefe("SELECT npc_code, name, description, branch, evo, lp, str, chain, speed, au_FLAME, au_ICE, au_HOLY, au_DARK, rewards, illulink FROM model_NPC;", type='all')
        for r in res:
            await asyncio.sleep(0)
            temp[r[0]] = c_NPC(r)

        return temp

    async def cacheConversation_tool(self):
        temp = {}

        res = await self.client.quefe("SELECT ordera, conv_code, type, line, node_1, node_2, effect_query FROM model_converstation;", type='all')
        for r in res:
            await asyncio.sleep(0)
            temp[r[1]] = c_Conversation(r)

        return temp

    

    # ================== MOB ==================
    async def cacheMob(self):
        self.client.DBC['model_mob'] = await self.cacheMob_tool()

    async def cacheMob_tool(self):
        temp = {}

        res = await self.client.quefe("""SELECT mob_code, 
                                                name, 
                                                description, 
                                                branch, 
                                                evo,
                                                lp, 
                                                str, 
                                                chain, 
                                                speed, 
                                                attack_type, 
                                                defense_physic, 
                                                defense_magic, 
                                                au_FLAME, 
                                                au_ICE, 
                                                au_HOLY, 
                                                au_DARK, 
                                                skills, 
                                                effect, 
                                                lockon_max,
                                                rewards, 
                                                illulink,
                                                distance_min,
                                                distance_max,
                                                tags
                                                FROM model_mob;""", type='all')
        for r in res:
            await asyncio.sleep(0)
            temp[r[0]] = c_Mob(r)

        return temp

    # ================== ITEM ==================
    async def cacheItem(self):
        self.client.DBC['model_item'] = await self.cacheItem_tool()

    async def cacheItem_tool(self):
        temp = {}

        # Ingredient
        res = await self.client.quefe("""SELECT ingredient_code,
                                                name,
                                                description,
                                                tags,
                                                weight,
                                                defend,
                                                multiplier,
                                                str,
                                                intt,
                                                sta,
                                                speed,
                                                round,
                                                accuracy_randomness,
                                                accuracy_range,
                                                range_min,
                                                range_max,
                                                firing_rate,
                                                reload_query,
                                                effect_query,
                                                infuse_query,
                                                order_query,
                                                passive_query,
                                                ultima_query,
                                                quantity,
                                                price,
                                                dmg,
                                                stealth,
                                                evo,
                                                aura,
                                                craft_value,
                                                origin,
                                                origin_base,
                                                illulink
                                                FROM model_ingredient;""", type='all')
        for r in res:
            await asyncio.sleep(0)
            temp[r[0]] = c_Item(r, rootTable='ingredient')

        # Item
        res2 = await self.client.quefe("""SELECT item_code,
                                                name,
                                                description,
                                                tags,
                                                weight,
                                                defend,
                                                multiplier,
                                                str,
                                                intt,
                                                sta,
                                                speed,
                                                round,
                                                accuracy_randomness,
                                                accuracy_range,
                                                range_min,
                                                range_max,
                                                firing_rate,
                                                reload_query,
                                                effect_query,
                                                infuse_query,
                                                order_query,
                                                passive_query,
                                                ultima_query,
                                                quantity,
                                                price,
                                                dmg,
                                                stealth,
                                                evo,
                                                aura,
                                                craft_value,
                                                origin,
                                                origin_base,
                                                illulink
                                                FROM model_item;""", type='all')
        for r in res2:
            await asyncio.sleep(0)
            temp[r[0]] = c_Item(r)

        return temp




def setup(client):
    client.add_cog(avaDBC(client))






# ================== CLASS ==================

class c_PersonalInfo:
    def __init__(self, pack):
        self.id, self.name, self.gender, self.dob = pack

        self.mailBox = None
        self.childNick = {}

    async def initMailBox(self, client, user_id):
        # Mailbox
        m_res = await client.quefe(f"""SELECT mail_read, mail_unread, DM, trash, pin FROM pi_mailbox WHERE user_id='{user_id}';""")
        if m_res:
            # Caching
            self.mailBox = mailBox(config={'DM': m_res[2].split(' - ')})
            try:
                rmt = m_res[0].split(' - ')
                for rm in rmt:
                    a = rm.split('.')
                    try: self.mailBox.readMail[int(a[0])] = a[1]
                    # E: Defective mail_code filter (Missing ordera)
                    except IndexError: pass
            except AttributeError: pass
            await asyncio.sleep(0)
            try:
                urmt = m_res[1].split(' - ')
                for urm in urmt:
                    b = urm.split('.')
                    try: self.mailBox.unreadMail[int(b[0])] = b[1]
                    # E: Defective mail_code filter (Missing ordera)
                    except IndexError: pass
            except AttributeError: pass
            await asyncio.sleep(0)
            try:
                utt = m_res[3].split(' - ')
                for ut in utt:
                    c = ut.split('.')
                    try: self.mailBox.trash[int(c[0])] = c[1]
                    # E: Defective mail_code filter (Missing ordera)
                    except IndexError: pass
            except AttributeError: pass
            await asyncio.sleep(0)
            try:
                upt = m_res[4].split(' - ')
                for up in upt:
                    d = up.split('.')
                    try: self.mailBox.trash[int(d[0])] = d[1]
                    # E: Defective mail_code filter (Missing ordera)
                    except IndexError: pass
            except AttributeError: pass
            await self.mailBox.setMailCounter()
        else:
            # Init
            self.mailBox = mailBox()
            await client._cursor.execute(f"""INSERT INTO pi_mailbox VALUES ('{user_id}', '', '', '', '', '{" - ".join(self.mailBox.config["DM"])}');""")

    async def initChildNick(self, client, user_id):
        nicks = await client.quefe(f"SELECT child_id, nick FROM pi_childnick WHERE user_id='{self.id}';", type='all')
        for n in nicks:
            self.childNick[n[1]] = n[0]
    
    async def addChildNick(self, client, child_id, nick):
        nick = nick[:16]

        # DB
        try:
            await client._cursor.execute(f"INSERT INTO pi_childnick VALUES ('{self.id}', '{child_id}', '{nick}');")
        # E: Child already had nick, or nick already exists --> Update child for nick
        except mysqlError.IntegrityError:
            try:
                if not await client._cursor.execute(f"UPDATE pi_childnick SET child_id='{child_id}' WHERE nick='{nick}' AND user_id='{self.id}';"):
                    await client._cursor.execute(f"UPDATE pi_childnick SET nick='{nick}' WHERE child_id='{child_id}' AND user_id='{self.id}';")
                    del self.childNick[await self.lookupChildNick(child_id=child_id)]
            # E: Child already had nick ---> Update nick for child
            except mysqlError.IntegrityError:
                await client._cursor.execute(f"UPDATE pi_childnick SET nick='{nick}' WHERE child_id='{child_id}' AND user_id='{self.id}';")
                del self.childNick[await self.lookupChildNick(child_id=child_id)]

        self.childNick[nick] = child_id
    
    async def removeChildNick(self, client, child_id=None, nick=None):

        # Nick given
        if nick:
            try:
                del self.childNick[nick]
            except KeyError:
                return False
            await client._cursor.execute(f"DELETE FROM pi_childnick WHERE nick='{nick}';")
        
        # child_id given
        elif child_id:
            res = await self.lookupChildNick(child_id=child_id)
            if not res: return False
            del self.childNick[res]
            await client._cursor.execute(f"DELETE FROM pi_childnick WHERE child_id='{child_id}';")
        return True

    async def lookupChildNick(self, child_id=None, nick=None):
        if nick:
            try:
                return self.childNick[nick]             # Return CHILD_ID
            except KeyError:
                return False
        elif child_id:
            for k, v in self.childNick.items():
                await asyncio.sleep(0)
                if v == child_id:
                    return k        # Return NICK

            return False
            


class c_Mail:
    def __init__(self, pack):
        self.mail_code, self.sender, self.content, self.tag = pack
        self.tag = self.tag.split(' - ')

class mailBox:
    def __init__(self, config=None):
        if config == None:
            self.config = {
                'DM': ['main_quest']
            }
        else:
            self.config = config

        self.readMail = {}
        self.unreadMail = {}
        self.pin = {}
        self.trash = {}
        self.rmEntry = []
        self.urmEntry = []
        self.pEntry = []
        self.tEntry = []

        self.tag = []
        self.mailCounter = 0
        self.CHANGING = False       # Prevent corrupting data



    async def getMail(self, client, ordera):
        try: ordera = int(ordera)
        except ValueError: return False
        try: return client.DBC['model_mail'][self.unreadMail[ordera]]
        except KeyError: pass
        try: return client.DBC['model_mail'][self.readMail[ordera]]
        except KeyError: pass
        try: return client.DBC['model_mail'][self.trash[ordera]]
        except KeyError: pass
        try: return client.DBC['model_mail'][self.pin[ordera]]
        except KeyError: pass
        return False

    async def updateMail(self, client, user_id, mail_code):
        while self.CHANGING:
            if not self.CHANGING:
                self.CHANGING = True
                break
            await asyncio.sleep(0.5)
        try:
            try: mail = client.DBC['model_mail'][mail_code]
            except KeyError:
                self.CHANGING = False
                print("<!> Unknown mail_code"); return False

            # Check limit urm
            await asyncio.sleep(0)
            if len(self.urmEntry) >= 100:
                self.readMail[self.urmEntry[0]] = self.unreadMail[self.urmEntry[0]]
                del self.unreadMail[self.urmEntry[0]]
                del self.urmEntry[0]
            # Check limit rm
            if len(self.rmEntry) >= 200:
                self.trash[self.rmEntry[0]] = self.readMail[self.rmEntry[0]]
                self.tEntry.append(self.rmEntry[0])
                del self.readMail[self.rmEntry[0]]
                del self.rmEntry[0]

            # Entry
            self.urmEntry.append(self.mailCounter)
            await self.refreshEntry(trash=True)
            self.mailCounter += 1

            self.unreadMail[self.mailCounter] = mail_code
            await client.quefe(f"""UPDATE pi_mailbox SET mail_unread="{' - '.join(('.'.join((str(ii) for ii in i)) for i in self.unreadMail.items()))}", mail_read="{' - '.join(('.'.join((str(ii) for ii in i)) for i in self.readMail.items()))}" WHERE user_id='{user_id}';""")

            tt = []
            for t in mail.tag:
                if t in self.config['DM']: tt.append(t)
            if tt: return tt
            else: return True
        finally: self.CHANGING = False

    async def setRead(self, client, user_id, orderas):
        f = []
        
        for ordera in orderas:
            await asyncio.sleep(0)
            try: ordera = int(ordera)
            except ValueError: continue
            # Check limit
            if len(self.rmEntry) >= 200:
                self.trash[self.rmEntry[0]] = self.readMail[self.rmEntry[0]]
                self.tEntry.append(self.rmEntry[0])
                del self.readMail[self.rmEntry[0]]
                del self.rmEntry[0]

            try: 
                self.readMail[ordera] = self.unreadMail[ordera]
                del self.unreadMail[ordera]
            except KeyError: print("<!> Unknown mail_code"); f.append(f"{ordera} (unknown)")

            

        if f: return f
        await self.refreshEntry()
        await client.quefe(f"""UPDATE pi_mailbox SET mail_unread="{' - '.join(('.'.join((str(ii) for ii in i)) for i in self.unreadMail.items()))}", mail_read="{' - '.join(('.'.join((str(ii) for ii in i)) for i in self.readMail.items()))}" WHERE user_id='{user_id}';""")

    async def moveToTrash(self, client, user_id, orderas):
        f = []

        for ordera in orderas:
            await asyncio.sleep(0)
            try: ordera = int(ordera)
            except ValueError: continue
            # Check limit
            if len(self.tEntry) >= 100:
                del self.trash[self.tEntry[0]]
                del self.tEntry[0]

            try:
                # rm
                await asyncio.sleep(0)
                self.trash[ordera] = self.readMail[ordera]
                del self.readMail[ordera]
                self.rmEntry.remove(ordera)
                self.tEntry.append(ordera)
                await self.refreshEntry(trash=True, pin=True)
            except KeyError:
                # urm
                try:
                    await asyncio.sleep(0)
                    self.trash[ordera] = self.unreadMail[ordera]
                    del self.unreadMail[ordera]
                    self.urmEntry.remove(ordera)
                    self.tEntry.append(ordera)
                    await self.refreshEntry(trash=True, pin=True)
                # p
                except KeyError:
                    await asyncio.sleep(0)
                    try: self.trash[ordera] = self.pin[ordera]
                    except KeyError: f.append(f"{ordera} (unknown)")
                    del self.pin[ordera]
                    self.pEntry.remove(ordera)
                    self.tEntry.append(ordera)
                    await self.refreshEntry(trash=True, pin=True)

        await client.quefe(f"""UPDATE pi_mailbox SET pin="{' - '.join(('.'.join((str(ii) for ii in i)) for i in self.pin.items()))}", mail_unread="{' - '.join(('.'.join((str(ii) for ii in i)) for i in self.unreadMail.items()))}", mail_read="{' - '.join(('.'.join((str(ii) for ii in i)) for i in self.readMail.items()))}", trash="{' - '.join(('.'.join((str(ii) for ii in i)) for i in self.trash.items()))}" WHERE user_id='{user_id}';""")                

    async def recoverTrash(self, client, user_id, orderas):
        f = []

        for ordera in orderas:
            await asyncio.sleep(0)
            try: ordera = int(ordera)
            except ValueError: continue
            # Check limit
            if len(self.rmEntry) >= 100:
                f.append(f"{ordera} (already full)")
            else:
                # rm
                try: self.readMail[ordera] = self.trash[ordera]
                except KeyError: f.append(f"{ordera} (unknown)")
                del self.trash[ordera]
                self.tEntry.remove(ordera)

                self.rmEntry.append(ordera)
        if f: return f
        await self.refreshEntry(trash=True, pin=True)
        await client.quefe(f"""UPDATE pi_mailbox SET trash="{' - '.join(('.'.join((str(ii) for ii in i)) for i in self.trash.items()))}", mail_read="{' - '.join(('.'.join((str(ii) for ii in i)) for i in self.readMail.items()))}" WHERE user_id='{user_id}';""")
 
    async def moveToPin(self, client, user_id, orderas):
        f = []

        for ordera in orderas:
            await asyncio.sleep(0)
            try: ordera = int(ordera)
            except ValueError: continue
            # Check limit
            if len(self.pin) >= 50: return ["all mails (already full)"]


            try:
                # rm
                await asyncio.sleep(0)
                self.pin[ordera] = self.readMail[ordera]
                del self.readMail[ordera]
                self.rmEntry.remove(ordera)
                self.pEntry.append(ordera)
            except KeyError:
                # urm
                try:
                    await asyncio.sleep(0)
                    self.pin[ordera] = self.unreadMail[ordera]
                    del self.unreadMail[ordera]
                    self.urmEntry.remove(ordera)
                    self.pEntry.append(ordera)
                # t
                except KeyError:
                    await asyncio.sleep(0)
                    try: self.pin[ordera] = self.trash[ordera]
                    except KeyError: f.append(f"{ordera} (unknown)")
                    del self.trash[ordera]
                    self.tEntry.remove(ordera)
                    self.pEntry.append(ordera)

        await client.quefe(f"""UPDATE pi_mailbox SET pin="{' - '.join(('.'.join((str(ii) for ii in i)) for i in self.pin.items()))}", mail_unread="{' - '.join(('.'.join((str(ii) for ii in i)) for i in self.unreadMail.items()))}", mail_read="{' - '.join(('.'.join((str(ii) for ii in i)) for i in self.readMail.items()))}", trash="{' - '.join(('.'.join((str(ii) for ii in i)) for i in self.trash.items()))}" WHERE user_id='{user_id}';""")                

        await self.refreshEntry(trash=True, pin=True)
        return True

    async def refreshEntry(self, trash=False, pin=False):
        if trash:
            self.tEntry = sorted(self.trash.keys())
            await asyncio.sleep(0)
        if pin:
            self.pEntry = sorted(self.pin.keys())
            await asyncio.sleep(0)
        self.rmEntry = sorted(self.readMail.keys())
        await asyncio.sleep(0)
        self.urmEntry = sorted(self.unreadMail.keys())

    async def setMailCounter(self):
        await self.refreshEntry(trash=True, pin=True)
        try:
            if self.urmEntry:
                self.mailCounter = self.urmEntry[-1]
            if self.rmEntry:
                if self.rmEntry[-1] > self.mailCounter:
                    self.mailCounter = self.rmEntry[-1]
            if self.tEntry:
                if self.tEntry[-1] > self.mailCounter:
                    self.mailCounter = self.tEntry[-1]
            if self.pEntry:
                if self.pEntry[-1] > self.mailCounter:
                    self.mailCounter = self.pEntry[-1]

        except IndexError: pass
        
class c_NPC:
    def __init__(self, pack, narrator=False):
        """
        npc_code, name, description, branch, evo, lp, strr, chain, speed, au_FLAME, au_ICE, au_HOLY, au_DARK, rewards, illulink = pack
        """
        self.narrator = narrator
        if not narrator: self.npc_code, self.name, self.description, self.branch, self.evo, self.lp, self.strr, self.chain, self.speed, self.au_FLAME, self.au_ICE, self.au_HOLY, self.au_DARK, self.rewards, self.illulink = pack
        else: self.npc_code, self.name, self.description, self.branch, self.evo, self.lp, self.strr, self.chain, self.speed, self.au_FLAME, self.au_ICE, self.au_HOLY, self.au_DARK, self.rewards, self.illulink = ('n/a', 'n/a', 'n/a', 'n/a', 1, 1, 1, 1, 1, 1, 1, 1, 1, '', '')
        self.illulink = self.illulink.split(' <> ')
        self.search_name = self.name.lower()

    def check(self, npc_code='', name=''):
        if npc_code and npc_code == self.npc_code: return True
        if name and name in self.search_name: return True
        return False

class c_Conversation:
    def __init__(self, pack):
        """
        ordera, conv_code, type, line, node_1, node_2, effect_query

        <TURN> in a <conversation> is a series of lines that has the same speaker
        """

        self.ordera, self.conv_code, self.type, lines, self.node_1, self.node_2, self.effect_query = pack

        # Partial conv split
        self.line = []
        for il in lines.split(' ||| '):
            # Turns of conv       (author, (line1, line2,), illulink)
            a = il.split(' --- ')
            if len(a) < 3: a.append('')
            elif a[2] == 'n/a': a[2] = ''
            # Line
            a[1] = tuple(a[1].split(' >>> '))
            self.line.append(tuple(a))

        # Multi-node
        try: self.node_1 = self.node_1.split(' - ')
        except AttributeError: self.node_1 = []
        try: self.node_2 = self.node_2.split(' - ')
        except AttributeError: self.node_2 = []

class c_Mob:
    def __init__(self, pack):
        self.mob_code, self.name, self.description, self.branch, self.evo, self.lp, self.str, self.chain, self.speed, self.attack_type, self.defense_physic, self.defense_magic, self.au_FLAME, self.au_ICE, self.au_HOLY, self.au_DARK, self.skills, effectTemp, self.lockon_max, rewardsTemp, self.illulink, self.distance_min, self.distance_max, self.tags = pack

        # Effect
        effectTemp2 = []
        for e in effectTemp.split(' || '):
            effectTemp2.append(tuple(e.split(' - ')))
        self.effect = tuple(effectTemp2)

        # Rewards       # [(type/code, quantity, percentage), ..]
        rewardsTemp2 = []
        for e in rewardsTemp.split(' | '):
            rewardsTemp2.append(tuple(e.split(' - ')))
        self.rewards = tuple(rewardsTemp2)

        # Tags
        tagsTemp = []
        for t in self.tags.split(' - '):
            tagsTemp.append(t)
        self.tags = tagsTemp

class c_Item:
    def __init__(self, pack, rootTable='item'):
        self.item_code, self.name, self.description, self.tags, self.weight, \
                        self.defend, self.multiplier, self.str, self.intt, \
                        self.sta, self.speed, self.round, self.accuracy_randomness, \
                        self.accuracy_range, self.range_min, self.range_max, self.firing_rate, \
                        self.reload_query, self.effect_query, self.infuse_query, self.order_query, \
                        self.passive_query, self.ultima_query, self.quantity, self.price, \
                        self.dmg, self.stealth, self.evo, self.aura, \
                        self.craft_value, self.origin, self.origin_base, self.illulink = pack
        self.rootTable = rootTable

        # Tags
        tagsTemp = []
        for t in self.tags.split(' - '):
            tagsTemp.append(t)
        self.tags = tagsTemp
