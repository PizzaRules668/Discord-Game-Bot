from disnake.ext import commands
import disnake

import os
from dotenv import load_dotenv

from Games.TicTacToe import TicTacToe
from Games.Connect4 import Connect4
from Games.Checkers import Checkers

from Games.Game import Game
from Games.GameHelp import GameHelp

intents = disnake.Intents.default()
intents.members = True

bot = commands.InteractionBot(intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_command_error(message, error):
    print(f"{error}")

bot.add_cog(Game(bot))
bot.add_cog(GameHelp(bot))

bot.add_cog(Checkers(bot))
bot.add_cog(Connect4(bot))
bot.add_cog(TicTacToe(bot))

if __name__ == "__main__":
    load_dotenv()

    bot.run(os.getenv("TOKEN"))
