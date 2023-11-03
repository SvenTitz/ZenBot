from typing import List
import discord

from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from helpers import db_manager, checks


class ClashTasks(commands.Cog, name="clash_tasks"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(
        name="task_missed_attacks",
        description="#############",
    )
    @checks.is_admin()
    async def task_missed_attacks(self, context: Context) -> None:
        """ """
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="You need to specify a subcommand.\n\n**Subcommands:**\n`add` - Adds a clan alias.\n`remove` - Remove a clanalias.\n`show` - Print the clan aliases",
                color=0xE02B2B,
            )
            await context.send(embed=embed)

    @task_missed_attacks.command(
        base="task_missed_attacks",
        name="add",
        description="#################",
    )
    async def add_task_missed_attacks(self, context: Context, clantag: str, channel: discord.TextChannel = None) -> None:
        if (channel is None):
            channel = context.channel

        """ """
        if await db_manager.missed_attacks_task_exists(clantag, channel.id, context.guild.id):
            embed = discord.Embed(
                description=f"A missed attack task for {clantag} already exists in <#{channel.id}>",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
            return
        await db_manager.add_missed_attacks_task(clantag, channel.id, context.guild.id)
        embed = discord.Embed(
            description=f"Missed attack task for **{clantag}** in <#{channel.id}> has been added successfully",
            color=0x9C84EF,
        )
        await context.send(embed=embed)

    @task_missed_attacks.command(
        base="task_missed_attacks",
        name="remove",
        description="########",
    )
    async def remove_task_missed_attacks(self, context: Context, clantag: str, channel: discord.TextChannel) -> None:
        if (channel is None):
            channel = context.channel

        if not await db_manager.missed_attacks_task_exists(clantag, channel.id, context.guild.id):
            embed = discord.Embed(
                description=f"Task for {clantag} in  <#{channel.id}> does not exist.", color=0xE02B2B
            )
            await context.send(embed=embed)
            return
        await db_manager.remove_missed_attacks_task(clantag, channel.id, context.guild.id)
        embed = discord.Embed(
            description=f"Task for {clantag} in  <#{channel.id}> has been successfully removed",
            color=0x9C84EF,
        )
        await context.send(embed=embed)

    @task_missed_attacks.command(
        base="task_missed_attacks",
        name="list",
        description="#######",
    )
    async def list_task_missed_attacks(self, context: Context) -> None:
        tasks = await db_manager.get_missed_attacks_tasks(context.guild.id)
        if len(tasks) == 0:
            embed = discord.Embed(
                description="There are currently no missed attack tasks.", color=0xE02B2B
            )
            await context.send(embed=embed)
            return

        embed = discord.Embed(title="Missed Attack Tasks", color=0x9C84EF)
        for task in tasks:
            clantag = task[0]
            channel_id = int(task[1])
            # channel = discord.utils.get(channels, id=int(task[1]))
            embed.add_field(
                name=f"**{clantag}** in <#{channel_id}>", value="", inline=False
            )
        await context.send(embed=embed)

    @add_task_missed_attacks.autocomplete("clantag")
    @remove_task_missed_attacks.autocomplete("clantag")
    async def clantag_autocompletion(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        data = []
        clans = await db_manager.get_clans(interaction.guild.id)
        for clan in clans:
            data.append(app_commands.Choice(name=f"{clan[1]} ({clan[0]})", value=clan[0]))
        return data


async def setup(bot):
    await bot.add_cog(ClashTasks(bot))
