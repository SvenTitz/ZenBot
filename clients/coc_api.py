import requests
import json
import urllib.parse
import os

URL_LEAGUE_GROUP = 'https://api.clashofclans.com/v1/clans/{}/currentwar/leaguegroup'
URL_WARS = 'https://api.clashofclans.com/v1/clanwarleagues/wars/{}'
URL_CLAN = 'https://api.clashofclans.com/v1/clans/{}'


class Coc_Api_Client:
    """
    API Documentation: https://developer.clashofclans.com/#/
    """

    headers = ""

    def __init__(self):
        with open(
            f"{os.path.realpath(os.path.dirname(__file__))}/../config.json"
        ) as file:
            data = json.load(file)
        self.headers = {
            'Authorization': f'Bearer {data["coc_api_key"]}'
        }

    def get_league_group(self, clantag: str) -> dict:
        """
        Returns a GET request on the https://api.clashofclans.com/v1/clans/{clantag}/currentwar/leaguegroup endpoint
        """
        return self.__get(URL_LEAGUE_GROUP, clantag)

    def get_wars(self, wartag: str) -> dict:
        """
        Returns a GET request on the https://api.clashofclans.com/v1/clanwarleagues/wars/{wartag} endpoint
        """
        return self.__get(URL_WARS, wartag)

    def get_clan(self, clantag: str) -> dict:
        """
        Returns a GET request on the https://api.clashofclans.com/v1/clans/{} endpoint
        """
        return self.__get(URL_CLAN, clantag)

    def __get(self, url: str, tag: str) -> dict:
        request_url = url.format(urllib.parse.quote(tag))
        r = requests.get(request_url, headers=self.headers)
        return json.loads(r.text)
