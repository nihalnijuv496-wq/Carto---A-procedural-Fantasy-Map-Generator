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
    def settlement_type(self):
        return "settlement"

    def __repr__(self):
        return f"<{self.settlement_type.title()} '{self.name}' pop={self.population} at ({self.x},{self.y})>"

    def to_dict(self):
        # for database inserts and JSON/CSV export.
        return {
            "name": self.name,
            "type": self.settlement_type,
            "x": self.x,
            "y": self.y,
            "population": self.population,
            "notes": None,
        }


class Village(Settlement):
    MAX_POPULATION = 500

    def __init__(self, name, x, y, population=None, founding_reason=None):
        super().__init__(name, x, y, population or Village.MAX_POPULATION // 2)
        self.founding_reason = founding_reason

    @property
    def settlement_type(self):
        return "village"

    def to_dict(self):
        data = super().to_dict()
        data["notes"] = self.founding_reason
        return data


class City(Settlement):
    MIN_POPULATION = 501

    def __init__(self, name, x, y, population=None):
        super().__init__(name, x, y, population or City.MIN_POPULATION * 2)

    @property
    def settlement_type(self):
        return "city"


class WitchHut(Settlement):
    @property
    def settlement_type(self):
        return "witch_hut"


class School(Settlement):
    @property
    def settlement_type(self):
        return "school"


class Dungeon(Settlement):
    @property
    def settlement_type(self):
        return "dungeon"


class Palace(Settlement):
    def __init__(self, name, x, y, population=None):
        super().__init__(name, x, y, population or 5000)

    @property
    def settlement_type(self):
        return "palace"


class Portal(Settlement):
    @property
    def settlement_type(self):
        return "portal"


SPECIAL_CLASSES = {
    "witch_hut": WitchHut,
    "school": School,
    "dungeon": Dungeon,
    "palace": Palace,
    "portal": Portal,
}


def make_settlement(name, x, y, population):
    if population >= City.MIN_POPULATION:
        return City(name, x, y, population)
    return Village(name, x, y, population)


def make_special_settlement(settlement_type, name, x, y):
    return SPECIAL_CLASSES[settlement_type](name, x, y)
