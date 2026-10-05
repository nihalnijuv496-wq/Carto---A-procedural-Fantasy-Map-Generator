class Settlement:

    def __init__(self, name, x, y, population):
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
        """for database inserts and JSON/CSV export."""
        return {
            "name": self.name,
            "type": self.settlement_type,
            "x": self.x,
            "y": self.y,
            "population": self.population,
        }


class Village(Settlement):
    MAX_POPULATION = 500

    def __init__(self, name, x, y, population=None):
        if population is None:
            population = Village.MAX_POPULATION // 2
        super().__init__(name, x, y, population)

    @property
    def settlement_type(self):
        return "village"


class City(Settlement):
    MIN_POPULATION = 501

    def __init__(self, name, x, y, population=None):
        if population is None:
            population = City.MIN_POPULATION * 2
        super().__init__(name, x, y, population)

    @property
    def settlement_type(self):
        return "city"


def make_settlement(name, x, y, population):
    if population >= City.MIN_POPULATION:
        return City(name, x, y, population)
    return Village(name, x, y, population)
