import discord

from services.clash_data_service import Clash_Data_Service
from services.gspread_service import Gspread_Service
from discord.ext import commands
from discord.ext.commands import Context
from exceptions import WarStillOngoing


class Clash(commands.Cog, name="clash"):
    def __init__(self, bot):
        self.bot = bot

    """
    Command: cwldata
    """
    @commands.hybrid_command(
        name="cwldata", description="Returns a spreadsheet with the CWL attack data for the given clan tag."
    )
    async def cwldata(self, context: Context, clantag: str,  spreadsheet_id: str = None) -> None:
        await context.defer()
        try:
            # Collect the data
            clash_data_services = Clash_Data_Service()
            data = clash_data_services.get_cwl_data(clantag)
            name = clash_data_services.get_clan_name(clantag)
            # Write it into a spreadsheet
            gspread_service = Gspread_Service()
            sheet_url = gspread_service.write_cwl_data(data, name, spreadsheet_id)
            await context.send('Here is your speadsheet:\n' + sheet_url)
        except Exception as e:
            self.bot.logger.error(str(e))
            await context.send('Oops. Looks like something went wrong.\n')
            return

    """
    Command: messed attacks
    """
    @commands.hybrid_command(
        name="missed_attacks", description="Returns a list of players that missed attacks in the last war."
    )
    async def missed_attacks(self, context: Context, clantag: str) -> None:
        await context.defer()
        enemy_name = ''
        try:
            clash_data_service = Clash_Data_Service()
            enemy_name = clash_data_service.get_current_enemy_clan_name(clantag)
            players = clash_data_service.get_missed_attacks(clantag)
            embed = discord.Embed(title=f"Missed attacks in war agains {enemy_name}", color=0xFF0000)
            for player in players:
                embed.add_field(name=f'{player.name}: {len(player.attacks)}/2', value='', inline=False)
            await context.send(embed=embed)
        except WarStillOngoing:
            await context.send(f"War against {enemy_name} is still ongoing.")
        # except Exception:
        #     await context.send("Could not find a war that ended recently")


async def setup(bot):
    await bot.add_cog(Clash(bot))
