import requests
import json
import urllib.parse
import os

url_league_group = 'https://api.clashofclans.com/v1/clans/{}/currentwar/leaguegroup'
url_wars = 'https://api.clashofclans.com/v1/clanwarleagues/wars/{}'


class Coc_Api_Client:

    headers = ""

    def __init__(self):
        with open(
            f"{os.path.realpath(os.path.dirname(__file__))}/../config.json"
        ) as file:
            data = json.load(file)
        self.headers = {
            'Authorization': f'Bearer {data["coc_api_key"]}'
        }

    def get_league_group(self, clantag: str) -> str:
        return self.get(url_league_group, clantag)

    def get_wars(self, wartag: str) -> str:
        return self.get(url_wars, wartag)

    def get(self, url: str, tag: str) -> str:
        request_url = url.format(urllib.parse.quote(tag))
        r = requests.get(request_url, headers=self.headers)
        return json.loads(r.text)

    
