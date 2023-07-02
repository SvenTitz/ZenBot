import discord
from discord.utils import get
from discord.ext import commands
from discord.ext.commands import Context
from helpers import db_manager

from helpers import checks, db_manager


class Administration(commands.Cog, name="administration"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(
        name="admin",
        description="",
    )
    async def admin(self, context: Context) -> None:
        """ """
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="admin",
                color=0xE02B2B,
            )
            await context.send(embed=embed)

    @admin.command(
        base="admin",
        name="add_user",
        description="",
    )
    @checks.is_admin()
    async def admin_add_user(self, context: Context, user: discord.User) -> None:
        """ """
        if await db_manager.admin_user_exists(user.id, context.guild.id):
            embed = discord.Embed(
                description=f"**{user.name}** is already an admin.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
            return
        total = await db_manager.add_admin_user(user.id, context.guild.id)
        embed = discord.Embed(
            description=f"**{user.name}** has been added successfully",
            color=0x9C84EF,
        )
        embed.set_footer(
            text=f"There {'is' if total == 1 else 'are'} now {total} {'user' if total == 1 else 'users'} in the list"
        )
        await context.send(embed=embed)

    @admin.command(
        base="admin",
        name="add_role",
        description="",
    )
    @checks.is_admin()
    async def admin_add_role(self, context: Context, role: discord.Role) -> None:
        """ """
        if await db_manager.admin_role_exists(role.id, context.guild.id):
            embed = discord.Embed(
                description=f"**{role.name}** is already an admin.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
            return
        total = await db_manager.add_admin_role(role.id, context.guild.id)
        embed = discord.Embed(
            description=f"**{role.name}** has been added successfully",
            color=0x9C84EF,
        )
        embed.set_footer(
            text=f"There {'is' if total == 1 else 'are'} now {total} {'role' if total == 1 else 'roles'} in the list"
        )
        await context.send(embed=embed)

    @admin.command(
        base="admin",
        name="show_users",
        description="Shows the list of all admin users.",
    )
    async def admin_users_show(self, context: Context) -> None:
        users_ids = await db_manager.get_admin_users(context.guild.id)
        if len(users_ids) == 0:
            embed = discord.Embed(
                description="There are currently no admin users.", color=0xE02B2B
            )
            await context.send(embed=embed)
            return

        embed = discord.Embed(title="Admin Users", color=0x9C84EF)
        for user_id in users_ids:
            id = int(user_id[0])
            user = await self.bot.fetch_user(id)
            embed.add_field(
                name=f"**{user.display_name}** ({user.name})", value="", inline=False
            )
        await context.send(embed=embed)

    @admin.command(
        base="admin",
        name="show_roles",
        description="Shows the list of all admin roles.",
    )
    async def admin_roles_show(self, context: Context) -> None:
        roles_ids = await db_manager.get_admin_roles(context.guild.id)
        if len(roles_ids) == 0:
            embed = discord.Embed(
                description="There are currently no admin users.", color=0xE02B2B
            )
            await context.send(embed=embed)
            return

        embed = discord.Embed(title="Admin Roles", color=0x9C84EF)
        for role_id in roles_ids:
            role = get(context.guild.roles, id=int(role_id[0]))
            embed.add_field(name=f"{role.name}", value="", inline=False)
        await context.send(embed=embed)

    @admin.command(
        base="admin",
        name="remove_user",
        description="Lets you remove a user as admin.",
    )
    @checks.is_admin()
    async def admin_remove_user(self, context: Context, user: discord.User) -> None:
        if not await db_manager.admin_user_exists(user.id, context.guild.id):
            embed = discord.Embed(
                description=f"**{user.name}** is not an admin.", color=0xE02B2B
            )
            await context.send(embed=embed)
            return
        await db_manager.remove_admin_user(user.id, context.guild.id)
        embed = discord.Embed(
            description=f"**{user.name}** has been successfully removed as an admin",
            color=0x9C84EF,
        )
        await context.send(embed=embed)

    @admin.command(
        base="admin",
        name="remove_role",
        description="Lets you remove a role as admin.",
    )
    @checks.is_admin()
    async def admin_remove_role(self, context: Context, role: discord.Role) -> None:
        if not await db_manager.admin_role_exists(role.id, context.guild.id):
            embed = discord.Embed(
                description=f"**{role.name}** is not an admin.", color=0xE02B2B
            )
            await context.send(embed=embed)
            return
        await db_manager.remove_admin_role(role.id, context.guild.id)
        embed = discord.Embed(
            description=f"**{role.name}** has been successfully removed as an admin",
            color=0x9C84EF,
        )
        await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Administration(bot))
