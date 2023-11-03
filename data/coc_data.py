from dataclasses import dataclass


@dataclass
class Attack:
    stars: int
    destruction: int
    enemy: 'Player'

    def __init__(self, stars: int, destruction: int, enemy: 'Player'):
        self.stars = stars
        self.destruction = destruction
        self.enemy = enemy


@dataclass
class Player:
    name: str
    tag: str
    th_level: int
    attacks: list[Attack]

    def __init__(self, name: str, tag: str, TH: int, attacks: list[Attack]):
        self.name = name
        self.tag = tag
        self.th_level = TH
        self.attacks = attacks


@dataclass
class MissedAttackTask:
    clan_tag: str
    channel_id: int
    server_id: int


@dataclass
class MissedAttackTaskData:
    clan_tag: str
    war_end_time: float
