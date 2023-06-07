from dataclasses import dataclass


@dataclass
class Attack:
    stars: int
    destruction: int
    enemyTH: int

    def __init__(self, stars: int, destruction: int, enemyTH: int):
        self.stars = stars
        self.destruction = destruction
        self.enemyTH = enemyTH


@dataclass
class Player:
    name: str
    tag: str
    TH: int
    attacks: list[Attack]

    def __init__(self, name: str, tag: str, TH: int, attacks: list[Attack]):
        self.name = name
        self.tag = tag
        self.TH = TH
        self.attacks = attacks
