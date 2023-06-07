import services.cwl_data_service as cwl_data_services

from discord.ext import commands
from discord.ext.commands import Context


class Clash(commands.Cog, name="clash"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="cwldata", description="test cwl data"
    )
    async def cwldata(self, context: Context, clantag: str) -> None:
        await context.defer()
        text = await cwl_data_services.run(clantag)
        await context.send(text)


async def setup(bot):
    await bot.add_cog(Clash(bot))
