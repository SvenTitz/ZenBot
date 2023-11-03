from typing import List
from services.clash_data_service import Clash_Data_Service
from datetime import datetime, timedelta, timezone
from helpers import db_manager
from discord.ext.commands import Bot
from data.coc_data import MissedAttackTask
from logging import Logger
import discord


class Bot_Task_Service:
    def __init__(self, bot: Bot, logger: Logger) -> None:
        self.__clash_data_service = Clash_Data_Service()
        self.__bot = bot
        self.__logger = logger

    async def missed_attack_task(self):
        cur_timestamp = datetime.now().timestamp()
        threshold_timestamp = (datetime.now() - timedelta(minutes=15)).timestamp()

        data = await db_manager.get_missed_attacks_task_data()
        tasks = await db_manager.get_all_missed_attacks_tasks()

        for entry in data:
            if entry.war_end_time < threshold_timestamp:
                self.__logger.warning(f"Could not find data for {entry.clan_tag}. Removing it from the task list.")
                tasks = await self.__remove_tasks_for_clan(tasks, entry.clan_tag)
            elif entry.war_end_time < cur_timestamp:
                if await self.__send_missed_attack_info(tasks, entry.clan_tag):
                    await db_manager.remove_missed_attacks_task_data(entry.clan_tag)

        for task in tasks:
            if await db_manager.missed_attacks_task_data_exists(task.clan_tag):
                continue
            war_data = self.__clash_data_service.get_current_war(task.clan_tag)
            if war_data is not None:
                end_timestamp = datetime.strptime(war_data["endTime"], "%Y%m%dT%H%M%S.%fZ").replace(tzinfo=timezone.utc).timestamp()
                self.__logger.info(f"Add missed attack task for clan {task.clan_tag} and endtime {end_timestamp}")
                await db_manager.add_missed_attacks_task_data(task.clan_tag, end_timestamp)

    async def __remove_tasks_for_clan(self, tasks: List[MissedAttackTask], clan_tag: str) -> List[MissedAttackTask]:
        updated_tasks = []
        for task in tasks:
            if (task.clan_tag == clan_tag):
                channel = self.__bot.get_channel(task.channel_id)
                if channel is not None:
                    embed = discord.Embed(
                        description=f"Could not get missed attack data for last war of Clan {task.clan_tag}.\nMaybe a new war was started too quickly.",
                        color=0xE02B2B,
                    )
                    await channel.send(embed=embed)
            else:
                updated_tasks.append(task)
        await db_manager.remove_missed_attacks_task_data(clan_tag)
        return updated_tasks

    async def __send_missed_attack_info(self, tasks: List[MissedAttackTask], clan_tag: str) -> bool:
        try:
            war_data = self.__clash_data_service.find_most_recent_ended_war(clan_tag)
            clan_name = self.__clash_data_service.get_clan_name(clan_tag, war_data)
            enemy_name = self.__clash_data_service.get_current_enemy_clan_name(clan_tag, war_data)
            players = self.__clash_data_service.get_missed_attacks(clan_tag, war_data)
        except Exception as e:
            self.__logger.error(e)
            return False

        content = f"__***{clan_name}***__ missed attacks in war against __***{enemy_name}***__\n"
        for player in players:
            content += f"- {player.name}: {sum(attack is None for attack in player.attacks)}/{len(player.attacks)}\n"

        for task in tasks:
            if task.clan_tag == clan_tag:
                channel = self.__bot.get_channel(task.channel_id)
                if channel is not None:
                    await channel.send(content)
        return True
