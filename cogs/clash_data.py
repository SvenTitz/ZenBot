from typing import List
import discord

from discord import app_commands
from services.clash_data_service import Clash_Data_Service
from services.gspread_service import Gspread_Service
from discord.ext import commands
from discord.ext.commands import Context
from exceptions import WarStillOngoing
from helpers import db_manager


class ClashData(commands.Cog, name="clash_data"):
    def __init__(self, bot):
        self.bot = bot

    """
    Command: cwldata
    """

    @commands.hybrid_command(
        name="cwldata",
        description="Returns a spreadsheet with the CWL attack data for the given clan tag.",
    )
    async def cwldata(
        self, context: Context, clantag: str, spreadsheet_id: str = None
    ) -> None:
        await context.defer()
        try:
            # Collect the data
            clash_data_services = Clash_Data_Service()
            data = clash_data_services.get_cwl_data(clantag)
            name = clash_data_services.get_clan_name(clantag)
            # Write it into a spreadsheet
            gspread_service = Gspread_Service()
            sheet_url = gspread_service.write_cwl_data(data, name, spreadsheet_id)
            await context.send("Here is your speadsheet:\n" + sheet_url)
        except Exception as e:
            self.bot.logger.error(str(e))
            await context.send("Oops. Looks like something went wrong.\n")
            return

    """
    Command: missed attacks
    """

    @commands.hybrid_command(
        name="missed_attacks",
        description="Returns a list of players that missed attacks in the last war.",
    )
    async def missed_attacks(self, context: Context, clantag: str) -> None:
        await context.defer()
        enemy_name = ""
        try:
            clash_data_service = Clash_Data_Service()
            war_data = clash_data_service.find_most_recent_war(clantag)
            if war_data is None:
                raise Exception
            clan_name = clash_data_service.get_clan_name(clantag, war_data)
            enemy_name = clash_data_service.get_current_enemy_clan_name(clantag, war_data)
            players = clash_data_service.get_missed_attacks(clantag, war_data)
            embed = discord.Embed(
                title=f"__***{clan_name}***__ missed attacks in war against __***{enemy_name }***__",
                color=0xFF0000,
            )
            for player in players:
                embed.add_field(
                    name=f"{player.name}: {sum(attack is None for attack in player.attacks)}/{len(player.attacks)}",
                    value="",
                    inline=False,
                )
            await context.send(embed=embed)
        except WarStillOngoing:
            await context.send(f"War against {enemy_name} is still ongoing.")
        except Exception:
            await context.send("Could not find a war that ended recently")

    @cwldata.autocomplete("clantag")
    @missed_attacks.autocomplete("clantag")
    async def clantag_autocompletion(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        data = []
        clans = await db_manager.get_clans(interaction.guild.id)
        for clan in clans:
            data.append(app_commands.Choice(name=f"{clan[1]} ({clan[0]})", value=clan[0]))
        return data


async def setup(bot):
    await bot.add_cog(ClashData(bot))
