""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

import os

import aiosqlite

DATABASE_PATH = f"{os.path.realpath(os.path.dirname(__file__))}/../database/database.db"


async def get_blacklisted_users() -> list:
    """
    This function will return the list of all blacklisted users.

    :param user_id: The ID of the user that should be checked.
    :return: True if the user is blacklisted, False if not.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT user_id, strftime('%s', created_at) FROM blacklist"
        ) as cursor:
            result = await cursor.fetchall()
            return result


async def is_blacklisted(user_id: int) -> bool:
    """
    This function will check if a user is blacklisted.

    :param user_id: The ID of the user that should be checked.
    :return: True if the user is blacklisted, False if not.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT * FROM blacklist WHERE user_id=?", (user_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result is not None


async def add_user_to_blacklist(user_id: int) -> int:
    """
    This function will add a user based on its ID in the blacklist.

    :param user_id: The ID of the user that should be added into the blacklist.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("INSERT INTO blacklist(user_id) VALUES (?)", (user_id,))
        await db.commit()
        rows = await db.execute("SELECT COUNT(*) FROM blacklist")
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0


async def remove_user_from_blacklist(user_id: int) -> int:
    """
    This function will remove a user based on its ID from the blacklist.

    :param user_id: The ID of the user that should be removed from the blacklist.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM blacklist WHERE user_id=?", (user_id,))
        await db.commit()
        rows = await db.execute("SELECT COUNT(*) FROM blacklist")
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0


async def add_warn(user_id: int, server_id: int, moderator_id: int, reason: str) -> int:
    """
    This function will add a warn to the database.

    :param user_id: The ID of the user that should be warned.
    :param reason: The reason why the user should be warned.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        rows = await db.execute(
            "SELECT id FROM warns WHERE user_id=? AND server_id=? ORDER BY id DESC LIMIT 1",
            (
                user_id,
                server_id,
            ),
        )
        async with rows as cursor:
            result = await cursor.fetchone()
            warn_id = result[0] + 1 if result is not None else 1
            await db.execute(
                "INSERT INTO warns(id, user_id, server_id, moderator_id, reason) VALUES (?, ?, ?, ?, ?)",
                (
                    warn_id,
                    user_id,
                    server_id,
                    moderator_id,
                    reason,
                ),
            )
            await db.commit()
            return warn_id


async def remove_warn(warn_id: int, user_id: int, server_id: int) -> int:
    """
    This function will remove a warn from the database.

    :param warn_id: The ID of the warn.
    :param user_id: The ID of the user that was warned.
    :param server_id: The ID of the server where the user has been warned
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "DELETE FROM warns WHERE id=? AND user_id=? AND server_id=?",
            (
                warn_id,
                user_id,
                server_id,
            ),
        )
        await db.commit()
        rows = await db.execute(
            "SELECT COUNT(*) FROM warns WHERE user_id=? AND server_id=?",
            (
                user_id,
                server_id,
            ),
        )
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0


async def get_warnings(user_id: int, server_id: int) -> list:
    """
    This function will get all the warnings of a user.

    :param user_id: The ID of the user that should be checked.
    :param server_id: The ID of the server that should be checked.
    :return: A list of all the warnings of the user.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        rows = await db.execute(
            "SELECT user_id, server_id, moderator_id, reason, strftime('%s', created_at), id FROM warns WHERE user_id=? AND server_id=?",
            (
                user_id,
                server_id,
            ),
        )
        async with rows as cursor:
            result = await cursor.fetchall()
            result_list = []
            for row in result:
                result_list.append(row)
            return result_list


async def add_clan(clan_tag: str, alias: str, server_id: int) -> int:
    """
    This function will add a clan to the database.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO clans(clan_tag, alias, server_id) VALUES (?, ?, ?)",
            (clan_tag, alias, server_id),
        )
        await db.commit()
        rows = await db.execute("SELECT COUNT(*) FROM clans")
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0


async def clan_tag_exists(clan_tag: str, server_id: int) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT * FROM clans WHERE clan_tag=? AND server_id=?",
            (clan_tag, server_id),
        ) as cursor:
            result = await cursor.fetchone()
            return result is not None


async def clan_alias_exists(alias: str, server_id: int) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT * FROM clans WHERE alias=? AND server_id=?",
            (alias, server_id),
        ) as cursor:
            result = await cursor.fetchone()
            return result is not None


async def clan_exists(clan_tag: str, alias: str, server_id: int) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT * FROM clans WHERE (clan_tag=? OR alias=?) AND server_id=?",
            (clan_tag, alias, server_id),
        ) as cursor:
            result = await cursor.fetchone()
            return result is not None


async def get_clans(server_id: int) -> list:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT clan_tag, alias FROM clans WHERE server_id=?", (server_id,)
        ) as cursor:
            result = await cursor.fetchall()
            return result


async def remove_clan(alias: str, server_id: int) -> None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "DELETE FROM clans WHERE alias=? AND server_id=?",
            (
                alias,
                server_id,
            ),
        )
        await db.commit()


async def add_admin_user(user_id: int, server_id: int) -> int:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO admin_users(user_id, server_id) VALUES (?, ?)",
            (user_id, server_id),
        )
        await db.commit()
        rows = await db.execute("SELECT COUNT(*) FROM admin_users")
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0


async def get_admin_users(server_id: int) -> list:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT user_id FROM admin_users WHERE server_id=?", (server_id,)
        ) as cursor:
            result = await cursor.fetchall()
            return result


async def admin_user_exists(user_id: int, server_id: int) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT * FROM admin_users WHERE user_id=? AND server_id=?",
            (user_id, server_id),
        ) as cursor:
            result = await cursor.fetchone()
            return result is not None


async def remove_admin_user(user_id: int, server_id: int) -> None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "DELETE FROM admin_users WHERE user_id=? AND server_id=?",
            (
                user_id,
                server_id,
            ),
        )
        await db.commit()


async def add_admin_role(role_id: int, server_id: int) -> int:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO admin_roles(role_id, server_id) VALUES (?, ?)",
            (role_id, server_id),
        )
        await db.commit()
        rows = await db.execute("SELECT COUNT(*) FROM admin_roles")
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0


async def get_admin_roles(server_id: int) -> list:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT role_id FROM admin_roles WHERE server_id=?", (server_id,)
        ) as cursor:
            result = await cursor.fetchall()
            return result


async def admin_role_exists(role_id: int, server_id: int) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT * FROM admin_roles WHERE role_id=? AND server_id=?",
            (role_id, server_id),
        ) as cursor:
            result = await cursor.fetchone()
            return result is not None


async def remove_admin_role(role_id: int, server_id: int) -> None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "DELETE FROM admin_roles WHERE role_id=? AND server_id=?",
            (
                role_id,
                server_id,
            ),
        )
        await db.commit()


async def is_admin(user_id: int, role_ids: list, server_id: int) -> bool:
    if await admin_user_exists(user_id, server_id):
        return True

    admin_role_ids = [
        int(admin_role_id[0]) for admin_role_id in await get_admin_roles(server_id)
    ]

    return any(role_id in admin_role_ids for role_id in role_ids)
