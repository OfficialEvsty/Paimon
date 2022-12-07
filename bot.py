import time

import discord
import json
import asyncio
import asyncpg
from commands.profile import Profile
from leveling import Leveling
from data.database import Database


class Config:
    def __init__(self, cfg: dict) -> None:
        self.token = cfg['TOKEN']
        self.postgresql_user = cfg['POSTGRESQL_USER']
        self.postgresql_pass = cfg['POSTGRESQL_PASS']
        self.host = cfg['HOST']
        self.port = cfg['PORT']
        self.dbname = cfg['DATABASE']
        self.min_xp_msg = cfg['MIN_XP_MSG']
        self.max_xp_msg = cfg['MAX_XP_MSG']
        self.ignoring_xp_time = cfg['IGNORING_XP_TIME']


class Bot:

    def __init__(self):
          with open('config.json', 'r') as f:
              self.cfg = Config(json.loads(f.read()))

          intents = discord.Intents.default()
          intents.message_content = True

          self.client = discord.Client(intents=intents)
          self.db = Database(self.cfg.dbname, self.cfg.postgresql_user, self.cfg.postgresql_pass, self.cfg.host, self.cfg.port)
          self.leveling = Leveling(self, self.cfg.min_xp_msg, self.cfg.max_xp_msg, self.cfg.ignoring_xp_time)


    cmds_dict = {}
    utilities = None

    def startup(self):

        @self.client.event
        async def on_ready():
            await self.db.connect()
            print("We have logged in as {0.user}".format(self.client))

        @self.client.event
        async def on_message(msg):

            if msg.author == self.client.user:
              return
            await self.leveling.add_message_xp(msg.author.id)


            start = time.monotonic()
            if msg.content.startswith("@"):
              sign = msg.content.split()
              cmd_name = sign[0][1:]
              if len(sign) > 1:
                kwargs = []
                kwargs.append(msg)
                kwargs.append(sign[1:])
              else:
                kwargs = []
                kwargs.append(msg)

              command = self.cmds_dict["cmd_" + cmd_name]
              await command(*kwargs)
            end = time.monotonic()
            print("on_msg", end - start)

            self.leveling.ignoring_user_list.append(msg.author.id)
            await asyncio.sleep(self.leveling.ignoring_time)
            self.leveling.ignoring_user_list.remove(msg.author.id)









