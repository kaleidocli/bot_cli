from ..configs import SConfig
from imgurpython import ImgurClient

import asyncio
from datetime import datetime, timedelta

import aiomysql
import redis

class avaThirdParty:

    def __init__(self, client=None):
        self.client = client
        self.redio = redis.Redis(host=self.client.myconfig.Redis_host, port=self.client.myconfig.Redis_port)
        self.loop = asyncio.get_event_loop()
        try: self.client.conn, self.client._cursor = self.loop.run_until_complete(self.get_CURSOR())
        except RuntimeError: pass
        self.client.client_id = self.client.myconfig.Imgur_id
        self.client.client_secret = self.client.myconfig.Imgur_secret
        self.client.imgur_client = ImgurClient(self.client.client_id, self.client.client_secret)

    async def get_CURSOR(self):
        print("""<*> Connected DB == "{}.{}" ({})""".format(self.client.myconfig.MySQL_host, self.client.myconfig.MySQL_db, self.client.myconfig.MySQL_port))
        conn = await aiomysql.connect(host=self.client.myconfig.MySQL_host, user=self.client.myconfig.MySQL_user, password=self.client.myconfig.MySQL_pw, port=self.client.myconfig.MySQL_port, db=self.client.myconfig.MySQL_db, autocommit=True)
        _cursor = await conn.cursor()
        return conn, _cursor

    async def cd_check(self, MSG, cmd_tag, warn):
        cdkey = cmd_tag + str(MSG.author.id)
        if self.client.thp.redio.exists(cdkey):
            sec = await self.client.loop.run_in_executor(None, self.client.thp.redio.ttl, cdkey)
            await MSG.channel.send(f"{warn} Please wait `{timedelta(seconds=int(sec))}`."); return False
        else: return True

        #        async def intoSQL(self):
        #            count = 17
        #            for key, pack in self.data['entity']['boss'].items():
        #                await self.client._cursor.execute(f"""INSERT INTO model_mob VALUES ('mb{count}', "{pack['name']}", "{pack['branch']}", {pack['lp']}, {pack['str']}, {pack['chain']}, {pack['speed']}, 'query_goes_here');""")
        #                count += 1


    async def mysqlReload(self):
        await self.client._cursor.close()
        self.client.conn.close()
        self.client.conn, self.client._cursor = await self.get_CURSOR()


