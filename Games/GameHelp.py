from disnake.ext import commands
import disnake

from .Game import Game


class GameHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @Game.games.sub_command(description="Help Command for games")
    async def help(self, interaction):
        embed = disnake.Embed(title="Games Help")

        embed.add_field(name="/games checkers", value="Play checkers against friends", inline=True)
        embed.add_field(name="Arugments", value="opponent, bet", inline=True)

        embed.add_field(name="/games connect4", value="Play connect4 against friends", inline=True)
        embed.add_field(name="Arugments", value="opponent, bet", inline=True)

        embed.add_field(name="/games tictactoe", value="Play tictactoe against friends", inline=True)
        embed.add_field(name="Arugments", value="opponent, bet", inline=True)

        await interaction.response.send_message(embed=embed)