import discord

from services.clash_data_service import Clash_Data_Service
from services.gspread_service import Gspread_Service
from discord.ext import commands
from discord.ext.commands import Context
from exceptions import WarStillOngoing
from helpers import db_manager
from views.clan_selection import ClanSelectorView


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
        self, context: Context, clantag: str = None, spreadsheet_id: str = None
    ) -> None:
        if clantag is None:
            clans = await db_manager.get_clans()
            args = {"spreadsheet_id": spreadsheet_id}
            view = ClanSelectorView(clans, self.__cwldata_callback, **args)
            await context.send("Please choose a clan", view=view)
        else:
            # context.interaction.message = await context.send("thinking...")
            await self.__cwldata_callback(
                clantag, context.interaction, context, spreadsheet_id=spreadsheet_id
            )

    async def __cwldata_callback(
        self,
        clantag: str,
        interaction: discord.Interaction,
        context: Context = None,
        spreadsheet_id: str = None,
    ):
        await interaction.response.defer(ephemeral=False)
        content = None
        try:
            # Collect the data
            clash_data_services = Clash_Data_Service()
            data = clash_data_services.get_cwl_data(clantag)
            name = clash_data_services.get_clan_name(clantag)
            # Write it into a spreadsheet
            gspread_service = Gspread_Service()
            sheet_url = gspread_service.write_cwl_data(data, name, spreadsheet_id)
            content = "Here is your speadsheet:\n" + sheet_url
        except Exception as e:
            self.bot.logger.error(str(e))
            content = "Oops. Looks like something went wrong.\n"

        if context is None:
            await interaction.message.edit(embed=None, view=None, content=content)
        else:
            await context.send(embed=None, view=None, content=content)

    """
    Command: missed attacks
    """

    @commands.hybrid_command(
        name="missed_attacks",
        description="Returns a list of players that missed attacks in the last war.",
    )
    async def missed_attacks(self, context: Context, clantag: str = None) -> None:
        if clantag is None:
            clans = await db_manager.get_clans()
            view = ClanSelectorView(clans, self.__missed_attacks_callback)
            await context.send("Please choose a clan", view=view)
        else:
            # context.interaction.message = await context.send("thinking...")
            await self.__missed_attacks_callback(clantag, context.interaction, context)

    async def __missed_attacks_callback(
        self,
        clantag: str,
        interaction: discord.Interaction,
        context: Context = None,
    ):
        await interaction.response.defer(ephemeral=False)
        enemy_name = ""
        content = None
        embed = None
        view = None
        try:
            clash_data_service = Clash_Data_Service()
            clan_name = clash_data_service.get_clan_name(clantag)
            enemy_name = clash_data_service.get_current_enemy_clan_name(clantag)
            players = clash_data_service.get_missed_attacks(clantag)
            embed = discord.Embed(
                title=f"__***{clan_name}***__ missed attacks in war against __***{enemy_name}***__",
                color=0xFF0000,
            )
            for player in players:
                embed.add_field(
                    name=f"{player.name}: {len(player.attacks)}/2",
                    value="",
                    inline=False,
                )
        except WarStillOngoing:
            content = f"War against {enemy_name} is still ongoing."
        except Exception:
            content = "Something went wrong. Maybe there is no war that ended recently"

        if context is None:
            await interaction.message.edit(embed=embed, view=view, content=content)
        else:
            await context.send(embed=embed, view=view, content=content)


async def setup(bot):
    await bot.add_cog(ClashData(bot))
