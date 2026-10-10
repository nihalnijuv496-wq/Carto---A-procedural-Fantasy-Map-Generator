import random

from generator.terrain import generate_terrain, classify_biomes
from generator.namegen import generate_unique_names
from models.settlement import (
    make_settlement,
    make_special_settlement,
    Village,
    SPAWN_WEIGHTS,
    FOUNDING_REASONS,
)

MINING_BIOMES = {"mountain", "mountain_snow"}
MARKET_BIOMES = {"coast", "ocean", "deep_ocean"}
CROPS_BIOMES = {"plains", "forest", "deep_forest"}


class WorldMap:
    def __init__(self, name, width, height, seed):
        self.name = name
        self.width = width
        self.height = height
        self.seed = seed

        self.elevation = None
        self.moisture = None
        self.temperature = None
        self.ice_noise = None
        self.biomes = None
        self.settlements = []

    def generate(self):
        self.elevation, self.moisture, self.temperature, self.ice_noise = (
            generate_terrain(self.width, self.height, self.seed)
        )
        self.biomes = classify_biomes(
            self.elevation, self.moisture, self.temperature, self.ice_noise
        )
        return self

    def _land_cells(self):
        buildable = {
            "plains",
            "forest",
            "deep_forest",
            "desert",
            "swamp",
            "snowy_land",
            "mountain",
        }
        cells = []
        for y in range(self.height):
            for x in range(self.width):
                if self.biomes[y, x] in buildable:
                    cells.append((x, y))
        return cells

    def _nearby_biomes(self, x, y, radius=2):
        found = set()
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    found.add(self.biomes[ny, nx])
        return found

    def _pick_founding_reason(self, x, y, rng):
        nearby = self._nearby_biomes(x, y)
        if nearby & MINING_BIOMES:
            return "mining"
        if nearby & MARKET_BIOMES:
            return "market"
        if nearby & CROPS_BIOMES:
            return "crops"
        return rng.choice(FOUNDING_REASONS)

    def place_settlements(self, count=6):
        if self.biomes is None:
            raise RuntimeError("Call generate() before placing settlements.")

        rng = random.Random(self.seed + 1000)
        land_cells = self._land_cells()

        if len(land_cells) < count:
            count = len(land_cells)

        chosen_cells = rng.sample(land_cells, count)
        names = generate_unique_names(count, seed=self.seed)

        types = list(SPAWN_WEIGHTS.keys())
        weights = list(SPAWN_WEIGHTS.values())

        for (x, y), name in zip(chosen_cells, names):
            settlement_type = rng.choices(types, weights=weights, k=1)[0]

            if settlement_type == "settlement":
                population = rng.choice([150, 300, 450, 700, 1200, 2500])
                settlement = make_settlement(name, x, y, population)
                if isinstance(settlement, Village):
                    settlement.founding_reason = self._pick_founding_reason(x, y, rng)
            else:
                settlement = make_special_settlement(settlement_type, name, x, y)

            self.settlements.append(settlement)

        return self.settlements

    def summary(self):
        lines = [f"Map '{self.name}' ({self.width}x{self.height}, seed={self.seed})"]
        lines.append(f"  Settlements: {len(self.settlements)}")
        for s in self.settlements:
            extra = (
                f" ({s.founding_reason})"
                if isinstance(s, Village) and s.founding_reason
                else ""
            )
            lines.append(f"    - {s}{extra}")
        return "\n".join(lines)

    def summary(self):
        lines = [f"Map '{self.name}' ({self.width}x{self.height}, seed={self.seed})"]
        lines.append(f"  Settlements: {len(self.settlements)}")
        for s in self.settlements:
            lines.append(f"    - {s}")
        return "\n".join(lines)
