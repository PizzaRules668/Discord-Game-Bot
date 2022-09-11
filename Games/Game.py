from disnake.ext import commands
import disnake

import random
import time
import sys


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def games(self, interaction):
        pass

    @games.sub_command(description="Recommend a game to be added")
    async def recommend(interaction, name: str, desc: str, link: str):
        """
        Recommend a game to be added

        Parameters
        ----------
        name: Name of the gameyou want made
        desc: Descript how you would like this implented
        link: link to the game
        """
        pizzaUser = await bot.fetch_user("425797167228387340")

        if pizzaUser.dm_channel == None:
            await pizzaUser.create_dm()

        await pizzaUser.dm_channel.send(f"""{interaction.user.name} recommended adding {name}
{desc}
{link}""")

        await interaction.response.send_message("Recommened")