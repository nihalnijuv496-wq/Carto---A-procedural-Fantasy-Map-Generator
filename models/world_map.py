import random

from generator.terrain import generate_terrain, classify_biomes
from generator.namegen import generate_unique_names
from models.settlement import make_settlement


class WorldMap:
    def __init__(self, name, width, height, seed):
        self.name = name
        self.width = width
        self.height = height
        self.seed = seed

        self.elevation = None
        self.moisture = None
        self.biomes = None
        self.settlements = []

    def generate(self):
        self.elevation, self.moisture = generate_terrain(
            self.width, self.height, self.seed
        )
        self.biomes = classify_biomes(self.elevation, self.moisture)
        return self

    def _land_cells(self):
        buildable = {"plains", "forest", "mountain"}
        cells = []
        for y in range(self.height):
            for x in range(self.width):
                if self.biomes[y, x] in buildable:
                    cells.append((x, y))
        return cells

    def place_settlements(self, count=6):
        if self.biomes is None:
            raise RuntimeError("Call generate() before placing settlements.")

        rng = random.Random(self.seed + 1000)
        land_cells = self._land_cells()

        if len(land_cells) < count:
            count = len(land_cells)

        chosen_cells = rng.sample(land_cells, count)
        names = generate_unique_names(count, seed=self.seed)

        for (x, y), name in zip(chosen_cells, names):
            population = rng.choice([150, 300, 450, 700, 1200, 2500])
            settlement = make_settlement(name, x, y, population)
            self.settlements.append(settlement)

        return self.settlements

    def summary(self):
        lines = [f"Map '{self.name}' ({self.width}x{self.height}, seed={self.seed})"]
        lines.append(f"  Settlements: {len(self.settlements)}")
        for s in self.settlements:
            lines.append(f"    - {s}")
        return "\n".join(lines)
