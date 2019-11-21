from ..configs import SConfig
from imgurpython import ImgurClient

import asyncio
from datetime import datetime, timedelta

import aiomysql
import redis

class avaThirdParty:

    def __init__(self, client=None):
        self.client = client
        self.configs = SConfig()
        self.redio = redis.Redis(host=self.configs.Redis_host, port=self.configs.Redis_port)
        self.loop = asyncio.get_event_loop()
        self.client.conn, self.client._cursor = self.loop.run_until_complete(self.get_CURSOR())
        self.client.client_id = self.configs.Imgur_id
        self.client.client_secret = self.configs.Imgur_secret
        self.client.imgur_client = ImgurClient(self.client.client_id, self.client.client_secret)

    async def get_CURSOR(self):
        conn = await aiomysql.connect(host=self.configs.MySQL_host, user=self.configs.MySQL_user, password=self.configs.MySQL_pw, port=self.configs.MySQL_port, db=self.configs.MySQL_db, autocommit=True)
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


