from services.clash_data_service import Clash_Data_Service
from services.gspread_service import Gspread_Service
from discord.ext import commands
from discord.ext.commands import Context


class Clash(commands.Cog, name="clash"):
    def __init__(self, bot):
        self.bot = bot

    """
    Command: cwldata
    """
    @commands.hybrid_command(
        name="cwldata", description="test cwl data"
    )
    async def cwldata(self, context: Context, clantag: str,  spreadsheet_id: str = None) -> None:
        await context.defer()
        try:
            clash_data_services = Clash_Data_Service()
            data = clash_data_services.get_cwl_data(clantag)
            name = clash_data_services.get_clan_name(clantag)
            gspread_service = Gspread_Service()
            sheet_url = gspread_service.write_cwl_data(data, name, spreadsheet_id)
            await context.send('Here is your speadsheet:\n' + sheet_url)
        except Exception:
            await context.send('Oops. Looks like something went wrong.\n')
            return


async def setup(bot):
    await bot.add_cog(Clash(bot))
