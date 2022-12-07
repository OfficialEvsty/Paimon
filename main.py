import psycopg2
from bot import Bot
from commands.cmd_profile import *
from commands.user_info import *
from commands.cmd_main import *
import commands.cmd_main as com


bot = Bot()

def cmds_register():
    cmds = {name: cmd for (name, cmd) in globals().items() if name.startswith("cmd_") is True}
    print(len(cmds), "commands registered.")
    print(cmds)
    bot.cmds_dict = cmds

cmds_register()

if __name__ == "__main__":
    bot.startup()
    bot.client.run(bot.cfg.token)
    pass

con = psycopg2.connect(
    database="Paimon",
    user="postgres",
    password="8080",
    host="127.0.0.1",
    port="5432"
)





print("Database opened successfully")