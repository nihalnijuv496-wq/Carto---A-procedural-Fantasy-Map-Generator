SPAWN_WEIGHTS = {
    "settlement": 55,
    "witch_hut": 8,
    "school": 6,
    "dungeon": 8,
    "palace": 8,
    "portal": 6,
}

FOUNDING_REASONS = ["crops", "mining", "market"]


class Settlement:

    def __init__(self, name, x, y, population=0):
        self.name = name
        self.x = x
        self.y = y
        self.population = population

    @property
    def settlementType(self):
        return "settlement"

    def __repr__(self):
        return f"<{self.settlementType.title()} '{self.name}' pop={self.population} at ({self.x},{self.y})>"

    def toDict(self):
        return {
            "name": self.name,
            "type": self.settlementType,
            "x": self.x,
            "y": self.y,
            "population": self.population,
            "notes": None,
        }


class Village(Settlement):
    MAX_POPULATION = 500

    def __init__(self, name, x, y, population=None, foundingReason=None):
        super().__init__(name, x, y, population or Village.MAX_POPULATION // 2)
        self.foundingReason = foundingReason

    @property
    def settlementType(self):
        return "village"

    def toDict(self):
        data = super().toDict()
        data["notes"] = self.foundingReason
        return data


class City(Settlement):
    MIN_POPULATION = 501

    def __init__(self, name, x, y, population=None):
        super().__init__(name, x, y, population or City.MIN_POPULATION * 2)

    @property
    def settlementType(self):
        return "city"


class WitchHut(Settlement):
    @property
    def settlementType(self):
        return "witch_hut"


class School(Settlement):
    @property
    def settlementType(self):
        return "school"


class Dungeon(Settlement):
    @property
    def settlementType(self):
        return "dungeon"


class Palace(Settlement):
    def __init__(self, name, x, y, population=None):
        super().__init__(name, x, y, population or 5000)

    @property
    def settlementType(self):
        return "palace"


class Portal(Settlement):
    @property
    def settlementType(self):
        return "portal"


specialClasses = {
    "witch_hut": WitchHut,
    "school": School,
    "dungeon": Dungeon,
    "palace": Palace,
    "portal": Portal,
}


def makeSettlement(name, x, y, population):
    if population >= City.MIN_POPULATION:
        return City(name, x, y, population)
    return Village(name, x, y, population)


def makeSpecialSettlement(settlementType, name, x, y):
    return specialClasses[settlementType](name, x, y)
