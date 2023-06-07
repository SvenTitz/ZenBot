from data.coc_data import Player, Attack
from clients.coc_api import Coc_Api_Client


class Cwl_Data_Service:

    def __init__(self) -> None:
        self.__coc_api_client = Coc_Api_Client()

    """
    checks weather the clan is part of this war
    """
    def __has_clan(self, warData, clan_id):
        return warData['clan']['tag'] == clan_id or warData['opponent']['tag'] == clan_id

    """
    processes the war data and adds information to the players list
    """
    def __process_war_data(self, warData, clan_id, day, players: list[Player]):
        member_data = warData['clan'] if warData['clan']['tag'] == clan_id else warData['opponent']
        enemy_data = warData['opponent'] if warData['clan']['tag'] == clan_id else warData['clan']

        for member in member_data['members']:
            # check if the player already exsist in the list
            if (not any(player.tag == member['tag'] for player in players)):
                # player doesn't exist yet -> add him
                players.append(Player(member['name'], member['tag'], member['townhallLevel'], [None, None, None, None, None, None, None]))

            player = next((player for player in players if player.tag == member['tag']), None)
            if (player is None):
                raise Exception('Couldnt find player')

            if ('attacks' not in member):
                player.attacks[day-1] = Attack(0, 0, None)
                continue

            attackData = member['attacks'][0]
            enemyJson = next(enemy for enemy in enemy_data['members'] if enemy['tag'] == attackData['defenderTag'])
            enemyObject = Player(enemyJson['name'], enemyJson['tag'], enemyJson['townhallLevel'], [])
            player.attacks[day-1] = Attack(attackData['stars'], attackData['destructionPercentage'], enemyObject)

        return players

    """
    converts the players list into a csv
    """
    def __create_csv(self, players: list[Player]) -> str:
        header1 = ';;Day1;;;Day2;;;Day3;;;Day4;;;Day5;;;Day6;;;Day7;;;'
        header2 = 'Player;TH;' + 'Stars;%Dest;TH;' * 7

        csv = header1 + '\n' + header2

        for player in players:
            line = f'\n{player.name};{player.TH}'
            for attack in player.attacks:
                line += f';{attack.stars};{attack.destruction};{attack.enemyTH}'
            csv += line

        return csv

    def __format_for_spreadsheet(self, players: list[Player]):
        data = []
        for player in players:
            playerRow = []
            playerRow.append(player.name)
            playerRow.append(player.TH)
            for day in range(7):
                if (player.attacks[day] is None):
                    playerRow.extend(['', '', '', '', '-'])
                    continue

                playerRow.append(player.attacks[day].stars)
                playerRow.append(player.attacks[day].destruction)
                if (player.attacks[day].enemy is None):
                    playerRow.append('')
                else:
                    playerRow.append(player.attacks[day].enemy.TH)
                playerRow.append('')    
                playerRow.append('-')

            data.append(playerRow)
        return data

    def run(self, clantag: str) -> str:
        groupJson = self.__coc_api_client.get_league_group(clantag)

        players = []
        day = 1
        for warTags in groupJson['rounds']:
            for warTag in warTags['warTags']:

                if (warTag == '#0'):
                    break

                warData = self.__coc_api_client.get_wars(warTag)

                if (self.__has_clan(warData, clantag)):
                    players = self.__process_war_data(warData, clantag, day, players)
                    day += 1
                    break

        data = self.__format_for_spreadsheet(players)
        return data
