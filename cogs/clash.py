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
    async def cwldata(self, context: Context, clantag: str) -> None:
        await context.defer()
        cwl_data_services = Clash_Data_Service()
        text = cwl_data_services.run(clantag)
        await context.send(text[:2000])

    """
    Command: test
    """
    @commands.hybrid_command(
        name="test", description="test"
    )
    async def test(self, context: Context, clantag: str, spreadsheet_id: str) -> None:
        await context.defer()
        clash_data_services = Clash_Data_Service()
        data = clash_data_services.run(clantag)
        gspread_service = Gspread_Service()
        gspread_service.test(data, spreadsheet_id)
        await context.send('done')


async def setup(bot):
    await bot.add_cog(Clash(bot))
