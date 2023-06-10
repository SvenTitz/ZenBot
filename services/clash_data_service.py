from data.coc_data import Player, Attack
from clients.coc_api import Coc_Api_Client


class Clash_Data_Service:

    def __init__(self) -> None:
        self.__coc_api_client = Coc_Api_Client()

    def __has_clan(self, warData, clantag):
        """
        Checks weather the clan is part of this war
        """
        return warData['clan']['tag'] == clantag or warData['opponent']['tag'] == clantag

    def __process_war_data(self, war_data, clantag, day, players: list[Player]):
        """
        Processes the war data and adds information to the players list
        """
        member_data = war_data['clan'] if war_data['clan']['tag'] == clantag else war_data['opponent']
        enemy_data = war_data['opponent'] if war_data['clan']['tag'] == clantag else war_data['clan']

        for member in member_data['members']:
            # check if the player already exsist in the list
            if (not any(player.tag == member['tag'] for player in players)):
                # player doesn't exist yet -> add him
                players.append(Player(member['name'], member['tag'], member['townhallLevel'], [None, None, None, None, None, None, None]))

            player = next((player for player in players if player.tag == member['tag']), None)
            if (player is None):
                raise Exception('Couldnt find player')

            if ('attacks' not in member):
                # player did not attack this day
                player.attacks[day-1] = Attack(0, 0, None)
                continue

            attack_data = member['attacks'][0]
            attacked_enemy_data = next(enemy for enemy in enemy_data['members'] if enemy['tag'] == attack_data['defenderTag'])
            enemy_object = Player(attacked_enemy_data['name'], attacked_enemy_data['tag'], attacked_enemy_data['townhallLevel'], [])
            player.attacks[day-1] = Attack(attack_data['stars'], attack_data['destructionPercentage'], enemy_object)

        return players

    def __format_for_spreadsheet(self, players: list[Player]) -> list:
        """
        Converts the data from a list of players into a 2D array
        that can be imported into spreadsheets
        """

        data = []
        # add the headers
        days = ['', '']
        headers = ['Player', 'TH']
        for day in range(7):
            days.extend([f'Day {day+1}', '', '', '', ''])
            headers.extend(['Stars', '% Dest', 'TH', '+/-', 'Defence'])

        data.append(days)
        data.append(headers)

        # add the row for each player
        for player in players:
            playerRow = []
            playerRow.append(player.name)
            playerRow.append(player.th_level)
            for day in range(7):
                if (player.attacks[day] is None):
                    # player was not in war this day
                    playerRow.extend(['', '', '', '', '-'])
                    continue

                playerRow.append(player.attacks[day].stars)  # Stars
                playerRow.append(player.attacks[day].destruction)  # % Dest
                if (player.attacks[day].enemy is None):
                    # player did not attack this day
                    playerRow.append('')  # TH
                    playerRow.append('')  # +/-
                else:
                    playerRow.append(player.attacks[day].enemy.th_level)  # TH
                    playerRow.append(player.attacks[day].enemy.th_level - player.th_level)  # +/-

                playerRow.append('-')  # Defence

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
        for warTags in groupJson['rounds']:
            for warTag in warTags['warTags']:

                if (warTag == '#0'):
                    break

                # get the war data and add the relevant information to the players list
                warData = self.__coc_api_client.get_wars(warTag)

                if (self.__has_clan(warData, clantag)):
                    players = self.__process_war_data(warData, clantag, day, players)
                    day += 1
                    break

        # convert the data from a list a players into a 2D array that can be imported into spreadsheets
        data = self.__format_for_spreadsheet(players)
        return data

    def get_clan_name(self, clantag: str) -> str:
        """
        Returns the name of the clan with the given tag
        """
        return self.__coc_api_client.get_clan(clantag)['name']
