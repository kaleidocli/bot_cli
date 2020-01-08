import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import discord.errors as discordErrors

import asyncio
import inspect



class avaDBC(commands.Cog):
    def __init__(self, client):
        from .avaTools import avaTools
        from .avaUtils import avaUtils

        self.client = client

        self.client.DBC['model_mail'] = {}
        self.client.DBC['player'] = {}
        self.client.DBC['dbcf'] = {}
        self.cacheMethod = {
            'model_mail': self.cacheMail,
            'personal_info': self.cachePersonalInfo,
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
# All DBCF must be coroutine, and take *args as arguments

    async def dbcf_sendMail(self, *args):
        """
            0: user_id
            1: mail_code
        """

        return await self.client.DBC['personal_info'][args[0]].mailBox.updateMail(self.client, args[0], args[1])

    async def dbcf_getPersonalInfo(self, user_id):
        """
            user_id:        (str) User's ID

            Returning False means user's not initialized in DB
        """

        # DBCF
        try:
            return self.client.DBC['personal_info'][user_id]
        
        # DB
        except KeyError:
            # Personal Info
            pi_res = await self.client.quefe(f"SELECT id, name, gender, dob FROM personal_info WHERE id='{user_id}';")
            try: p = c_PersonalInfo(pi_res)
            except TypeError: return False

            # Mailbox
            m_res = await self.client.quefe(f"""SELECT mail_read, mail_unread, DM, trash, pin FROM pi_mailbox WHERE user_id='{user_id}';""")
            if m_res:
                # Caching
                p.mailBox = mailBox(config={'DM': m_res[2].split(' - ')})
                try:
                    rmt = m_res[0].split(' - ')
                    for rm in rmt:
                        a = rm.split('.')
                        try: p.mailBox.readMail[int(a[0])] = a[1]
                        # E: Defective mail_code filter (Missing ordera)
                        except IndexError: pass
                except AttributeError: pass
                await asyncio.sleep(0)
                try:
                    urmt = m_res[1].split(' - ')
                    for urm in urmt:
                        b = urm.split('.')
                        try: p.mailBox.unreadMail[int(b[0])] = b[1]
                        # E: Defective mail_code filter (Missing ordera)
                        except IndexError: pass
                except AttributeError: pass
                await asyncio.sleep(0)
                try:
                    utt = m_res[3].split(' - ')
                    for ut in utt:
                        c = ut.split('.')
                        try: p.mailBox.trash[int(c[0])] = c[1]
                        # E: Defective mail_code filter (Missing ordera)
                        except IndexError: pass
                except AttributeError: pass
                await asyncio.sleep(0)
                try:
                    upt = m_res[4].split(' - ')
                    for up in upt:
                        d = up.split('.')
                        try: p.mailBox.trash[int(d[0])] = d[1]
                        # E: Defective mail_code filter (Missing ordera)
                        except IndexError: pass
                except AttributeError: pass
                await p.mailBox.setMailCounter()
            else:
                # Init
                p.mailBox = mailBox()
                await self.client.quefe(f"""INSERT INTO pi_mailbox VALUES ('{user_id}', '', '', '', '', '{" - ".join(p.mailBox.config["DM"])}');""")

            return p



# ================== CACHE TOOL ==================

    async def cacheAll(self):
        for v in self.cacheMethod.values():
            await v()

    async def cacheDBCF(self):
        temp = [func for func in inspect.getmembers(avaDBC, predicate=inspect.iscoroutinefunction) if func[1].__name__.startswith('dbcf')]
        for t in temp:
            self.client.DBC['dbcf'][t[0]] = t[1]

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

    async def cacheMail(self):
        self.client.DBC['model_mail'] = await self.cacheMail_tool()

    async def cacheMail_tool(self):
        temp = {}

        res = await self.client.quefe("SELECT mail_code, sender, content, tag FROM model_mail;", type='all')
        for r in res:
            await asyncio.sleep(0)
            temp[r[0]] = c_Mail(r)

        return temp



def setup(client):
    client.add_cog(avaDBC(client))






# ================== CLASS ==================

class c_PersonalInfo:
    def __init__(self, pack):
        self.id, self.name, self.gender, self.dob = pack

        self.mailBox = None

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
            try: client.DBC['model_mail'][mail_code]
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

            return True
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
        
            
