from data.coc_data import Player, Attack
from clients.coc_api import Coc_Api_Client


class Clash_Data_Service:
    def __init__(self) -> None:
        self.__coc_api_client = Coc_Api_Client()

    def __has_clan(self, warData, clantag):
        """
        Checks weather the clan is part of this war
        """
        return (
            warData["clan"]["tag"] == clantag or warData["opponent"]["tag"] == clantag
        )

    def __separate_clan_member_data(self, war_data, clantag) -> tuple:
        member_data = (
            war_data["clan"]
            if war_data["clan"]["tag"] == clantag
            else war_data["opponent"]
        )
        enemy_data = (
            war_data["opponent"]
            if war_data["clan"]["tag"] == clantag
            else war_data["clan"]
        )
        return member_data, enemy_data

    def __process_member_attack_data(
        self, member, enemy_data, player: Player, day=None
    ) -> None:
        for attack in member["attacks"]:
            attacked_enemy_data = next(
                enemy
                for enemy in enemy_data["members"]
                if enemy["tag"] == attack["defenderTag"]
            )
            enemy_object = Player(
                attacked_enemy_data["name"],
                attacked_enemy_data["tag"],
                attacked_enemy_data["townhallLevel"],
                [],
            )
            if day is None:  # regular war
                index = member["attacks"].index(attack)
                player.attacks[index] = Attack(
                        attack["stars"], attack["destructionPercentage"], enemy_object
                    )
            else:  # cwl war
                player.attacks[day - 1] = Attack(
                    attack["stars"], attack["destructionPercentage"], enemy_object
                )

    def __process_member_war_data(self, member, enemy_data, players, num_attacks: int, day=None) -> None:
        # check if the player already exists in the list
        if not any(player.tag == member["tag"] for player in players):
            # player doesn't exist yet -> add him
            if day is None:
                players.append(
                    Player(member["name"], member["tag"], member["townhallLevel"], [None] * num_attacks)
                )
            else:
                players.append(
                    Player(
                        member["name"],
                        member["tag"],
                        member["townhallLevel"],
                        [None] * 7,
                    )
                )

        player = next(
            (player for player in players if player.tag == member["tag"]), None
        )
        if player is None:
            raise Exception("Could not find player")

        if "attacks" not in member:
            # player did not attack this day
            if day is not None:  # cwl has dummy attacks, regular war just empty attacks
                player.attacks[day - 1] = Attack(0, 0, None)
            return

        self.__process_member_attack_data(member, enemy_data, player, day)

    def __process_regular_war_data(self, war_data, clantag, num_attacks: int):
        """
        Processes the war data and return a player list
        """
        member_data, enemy_data = self.__separate_clan_member_data(war_data, clantag)

        players = []

        for member in member_data["members"]:
            self.__process_member_war_data(member, enemy_data, players, num_attacks)

        return players

    def __process_cwl_war_data(
        self, war_data, clantag, day, players: list[Player] = None
    ):
        """
        Processes the cwl war data and returns a player list with the additional information
        """
        member_data, enemy_data = self.__separate_clan_member_data(war_data, clantag)

        if players is None:
            players = []

        for member in member_data["members"]:
            self.__process_member_war_data(member, enemy_data, players, 1, day)

        return players

    def __format_for_spreadsheet(self, players: list[Player]) -> list:
        """
        Converts the data from a list of players into a 2D array
        that can be imported into spreadsheets
        """

        data = []
        # add the headers
        days = ["", ""]
        headers = ["Player", "TH"]
        for day in range(7):
            days.extend([f"Day {day+1}", "", "", "", ""])
            headers.extend(["Stars", "% Dest", "TH", "+/-", "Defence"])

        data.append(days)
        data.append(headers)

        # add the row for each player
        for player in players:
            playerRow = []
            playerRow.append(player.name)
            playerRow.append(player.th_level)
            for day in range(7):
                if player.attacks[day] is None:
                    # player was not in war this day
                    playerRow.extend(["", "", "", "", "-"])
                    continue

                playerRow.append(player.attacks[day].stars)  # Stars
                playerRow.append(player.attacks[day].destruction)  # % Dest
                if player.attacks[day].enemy is None:
                    # player did not attack this day
                    playerRow.append("")  # TH
                    playerRow.append("")  # +/-
                else:
                    playerRow.append(player.attacks[day].enemy.th_level)  # TH
                    playerRow.append(
                        player.attacks[day].enemy.th_level - player.th_level
                    )  # +/-

                playerRow.append("-")  # Defence

            data.append(playerRow)
        return data

    def get_cwl_data(self, clantag: str) -> list:
        """
        Compiles the CWL attack data for the given clantag and returns it as a 2D list of data,
        that can later be imported into spreadsheets.
        """

        groupJson = self.__coc_api_client.get_league_group(clantag)

        players = []
        day = 1

        # find the correct war from each day
        for warTags in groupJson["rounds"]:
            for warTag in warTags["warTags"]:
                if warTag == "#0":
                    break

                # get the war data and add the relevant information to the players list
                warData = self.__coc_api_client.get_wars(warTag)

                if self.__has_clan(warData, clantag):
                    players = self.__process_cwl_war_data(
                        warData, clantag, day, players
                    )
                    day += 1
                    break

        # convert the data from a list a players into a 2D array that can be imported into spreadsheets
        data = self.__format_for_spreadsheet(players)
        return data

    def get_clan_name(self, clantag: str, war_data=None) -> str:
        """
        Returns the name of the clan with the given tag
        """
        if war_data is None:
            clan = self.__coc_api_client.get_clan(clantag)
        else:
            clan, _ = self.__separate_clan_member_data(war_data, clantag)

        return clan["name"]

    def get_current_enemy_clan_name(self, clantag: str, war_data) -> str:
        _, enemy_data = self.__separate_clan_member_data(war_data, clantag)

        return enemy_data["name"]

    def get_enemy_clan_tag(self, clantag: str, war_data) -> str:
        _, enemy_data = self.__separate_clan_member_data(war_data, clantag)

        return enemy_data["tag"]

    def get_current_war_player_data(self, clantag: str) -> list:
        war_data = self.__coc_api_client.get_clan_current_war(clantag)

        num_attacks = war_data["attacksPerMember"] if "attacksPerMember" not in war_data else 1

        return self.__process_regular_war_data(war_data, clantag, num_attacks)

    def get_missed_attacks(self, clantag: str, war_data) -> list:
        num_attacks = war_data["attacksPerMember"] if "attacksPerMember" in war_data else 1

        players = self.__process_regular_war_data(war_data, clantag, num_attacks)

        return filter(lambda player: sum(attack is not None for attack in player.attacks) < num_attacks, players)

    def get_current_war(self, clantag: str) -> dict:
        war_data = self.__coc_api_client.get_clan_current_war(clantag)
        if "state" in war_data and (war_data["state"] == "preparation" or war_data["state"] == "inWar"):
            return war_data

        cwl_group = self.__coc_api_client.get_league_group(clantag)
        if "rounds" in cwl_group:
            war_data = self.__find_current_cwl_war(clantag, cwl_group)
            if war_data is not None:
                return war_data

        return None

    def find_most_recent_ended_war(self, clantag: str):
        # first check current war
        war_data = self.__coc_api_client.get_clan_current_war(clantag)
        if "state" in war_data and war_data["state"] == "warEnded":
            return war_data

        # check cwl
        cwl_group = self.__coc_api_client.get_league_group(clantag)
        if "rounds" in cwl_group:
            # find last war that ended in cwl
            war_data = self.__find_most_recent_cwl_war(clantag, cwl_group)
            if war_data is not None:
                return war_data

        return None

    def __find_current_cwl_war(self, clantag: str, cwl_group: dict):
        wars = self.__get_all_cwl_wars(clantag, cwl_group)
        if len(wars) <= 0:
            return None
        sorted_wars = sorted(wars, key=lambda w: w["startTime"])
        for war in sorted_wars:
            if "state" in war and (war["state"] == "inWar" or war["state"] == "preparation"):
                return war
        return None

    def __find_most_recent_cwl_war(self, clantag: str, cwl_group: dict):
        wars = self.__get_all_cwl_wars(clantag, cwl_group)
        if len(wars) <= 0:
            return None
        sorted_wars = sorted(wars, key=lambda w: w["startTime"], reverse=True)
        for war in sorted_wars:
            if war["state"] == "warEnded":
                return war
        return None

    def __get_all_cwl_wars(self, clantag: str, cwl_group: dict) -> list:
        wars = []
        for warTags in cwl_group["rounds"]:
            for warTag in warTags["warTags"]:
                if warTag == "#0":
                    break
                warData = self.__coc_api_client.get_wars(warTag)

                if self.__has_clan(warData, clantag):
                    wars.append(warData)

        return wars
