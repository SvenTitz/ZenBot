import discord

from discord.ext import commands
from discord.ext.commands import Context
from helpers import db_manager, checks


class ClashClans(commands.Cog, name="clash_clans"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(
        name="clans",
        description="Lets you modify the list of clan aliases",
    )
    async def clans(self, context: Context) -> None:
        """ """
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="You need to specify a subcommand.\n\n**Subcommands:**\n`add` - Adds a clan alias.\n`remove` - Remove a clanalias.\n`show` - Print the clan aliases",
                color=0xE02B2B,
            )
            await context.send(embed=embed)

    @clans.command(
        base="clans",
        name="add",
        description="Lets you add a clan alias",
    )
    @checks.is_admin()
    async def clans_add(self, context: Context, clantag: str, alias: str) -> None:
        if await db_manager.clan_exists(clantag, alias, context.guild.id):
            embed = discord.Embed(
                description=f"Either a clan with alias: **{alias}** or clantag: **{clantag}** already exists.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
            return
        total = await db_manager.add_clan(clantag, alias, context.guild.id)
        embed = discord.Embed(
            description=f"**{alias}** ({clantag}) has been added successfully",
            color=0x9C84EF,
        )
        embed.set_footer(
            text=f"There {'is' if total == 1 else 'are'} now {total} {'clan' if total == 1 else 'clans'} in the list"
        )
        await context.send(embed=embed)

    @clans.command(
        base="clans",
        name="show",
        description="Shows the list of all favourite clans.",
    )
    async def clans_show(self, context: Context) -> None:
        clans = await db_manager.get_clans(context.guild.id)
        if len(clans) == 0:
            embed = discord.Embed(
                description="There are currently no favourite clans.", color=0xE02B2B
            )
            await context.send(embed=embed)
            return

        embed = discord.Embed(title="Clans", color=0x9C84EF)
        for clan in clans:
            embed.add_field(name=f"{clan[1]}", value=clan[0], inline=False)
        await context.send(embed=embed)

    @clans.command(
        base="clans",
        name="remove",
        description="Lets you remove a clan from the list.",
    )
    @checks.is_admin()
    async def clans_remove(self, context: Context, alias: str) -> None:
        if not await db_manager.clan_alias_exists(alias, context.guild.id):
            embed = discord.Embed(
                description=f"**{alias}** is not on the list.", color=0xE02B2B
            )
            await context.send(embed=embed)
            return
        await db_manager.remove_clan(alias, context.guild.id)
        embed = discord.Embed(
            description=f"**{alias}** has been successfully removed from the list",
            color=0x9C84EF,
        )
        await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ClashClans(bot))
