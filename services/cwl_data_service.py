from data.coc_data import Player, Attack
from clients.coc_api import Coc_Api_Client


coc_api_client = Coc_Api_Client()


def has_clan(warData, clan_id):
    return warData['clan']['tag'] == clan_id or warData['opponent']['tag'] == clan_id


def process_war_data(warData, clan_id, players: list[Player]):
    member_data = warData['clan'] if warData['clan']['tag'] == clan_id else warData['opponent']
    enemy_data = warData['opponent'] if warData['clan']['tag'] == clan_id else warData['clan']

    for member in member_data['members']:
        # check if the player already exsist in the list
        if (not any(player.tag == member['tag'] for player in players)):
            # player doesn't exist yet -> add him
            players.append(Player(member['name'], member['tag'], member['townhallLevel'], []))

        player = next((player for player in players if player.tag == member['tag']), None)
        if (player is None):
            raise Exception('Couldnt find player')

        if ('attacks' not in member):
            break

        attackData = member['attacks'][0]
        enemy = next(enemy for enemy in enemy_data['members'] if enemy['tag'] == attackData['defenderTag'])
        player.attacks.append(Attack(attackData['stars'], attackData['destructionPercentage'], enemy['townhallLevel']))

    return players


def create_csv(players: list[Player]) -> str:
    header1 = ';;Day1;;;Day2;;;Day3;;;Day4;;;Day5;;;Day6;;;Day7;;;'
    header2 = 'Player;TH;' + 'Stars;%Dest;TH;' * 7

    csv = header1 + '\n' + header2

    for player in players:
        line = f'\n{player.name};{player.TH}'
        for attack in player.attacks:
            line += f';{attack.stars};{attack.destruction};{attack.enemyTH}'
        csv += line

    return csv


async def run(clantag: str) -> str:
    groupJson = coc_api_client.get_league_group(clantag)

    players = []

    for warTags in groupJson['rounds']:
        for warTag in warTags['warTags']:

            if (warTag == '#0'):
                break

            warData = coc_api_client.get_wars(warTag)

            if (has_clan(warData, clantag)):
                players = process_war_data(warData, clantag, players)
                break

    return create_csv(players)
