import wavelink
from discord import app_commands
import discord
import json
import discord.app_commands
import asyncio

import music.custom_music
from leveling import Leveling
from data.database import Database
import utilities.card_backgrounds.logic.Cards as utilities
from item_system.generator import Generator
import shop_system.market

import aiohttp


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


class Bot(discord.Client):

    db: Database = None
    bot = None
    generator: Generator = None
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.synced = False
        self.tree = app_commands.CommandTree(self)
        with open('config.json', 'r') as f:
            self.cfg = Config(json.loads(f.read()))

        Bot.db = Database(self.cfg.dbname, self.cfg.postgresql_user, self.cfg.postgresql_pass, self.cfg.host,
                           self.cfg.port)
        Bot.generator = Generator()
        Bot.bot = self
        self.leveling = Leveling(self.cfg.min_xp_msg, self.cfg.max_xp_msg, self.cfg.ignoring_xp_time)

        utilities.init_cards_list()
        print(utilities.cards_list)

        #delete later




    def startup(self):

        @self.event
        async def on_ready():
            await Bot.db.connect()
            await self.wait_until_ready()
            if not self.synced:
                await self.tree.sync(guild=None)
                print("Синхронизировалось")
                self.synced = True

            await wavelink.NodePool.create_node(
                bot=self,
                host="nonssl.freelavalink.ga",
                port=80,
                password="www.freelavalink.ga"
            )
            print("We have logged in as {0.user}".format(self))

        @self.event
        async def on_wavelink_node_ready(node: wavelink.Node):
            print(f"{node.identifier} is ready!")

        @self.event
        async def on_wavelink_track_end(player, track: wavelink.Track, reason):
            if not player.queue.is_empty:
                next_track = player.queue.get()
                await player.play(next_track)
            else:
                await player.disconnect()

        @self.event
        async def on_message(msg):

            if msg.author == self.user:
                return
            await self.leveling.add_message_xp(msg.guild, msg.author)

            if msg.author.id not in self.leveling.ignoring_user_list:
                self.leveling.ignoring_user_list.append(msg.author.id)
                print(self.leveling.ignoring_user_list)
                await asyncio.sleep(self.leveling.ignoring_time)
                self.leveling.ignoring_user_list.remove(msg.author.id)
