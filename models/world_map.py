import random

from generator.namegen import generateUniqueNames
from generator.terrain import classifyBiomes, generateTerrain
from models.settlement import (
    FOUNDING_REASONS,
    SPAWN_WEIGHTS,
    Village,
    makeSettlement,
    makeSpecialSettlement,
)

miningBiomes = {"mountain", "mountain_snow"}
marketBiomes = {"coast", "ocean", "deep_ocean"}
cropsBiomes = {"plains", "forest", "deep_forest"}


class WorldMap:
    def __init__(self, name, width, height, seed):
        self.name = name
        self.width = width
        self.height = height
        self.seed = seed

        self.elevation = None
        self.moisture = None
        self.temperature = None
        self.iceNoise = None
        self.biomes = None
        self.settlements = []

    def generate(self):
        self.elevation, self.moisture, self.temperature, self.iceNoise = (
            generateTerrain(self.width, self.height, self.seed)
        )
        self.biomes = classifyBiomes(
            self.elevation, self.moisture, self.temperature, self.iceNoise
        )
        return self

    def landCells(self):
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

    def nearbyBiomes(self, x, y, radius=2):
        found = set()
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    found.add(self.biomes[ny, nx])
        return found

    def pickFoundingReason(self, x, y, rng):
        nearby = self.nearbyBiomes(x, y)
        if nearby & miningBiomes:
            return "mining"
        if nearby & marketBiomes:
            return "market"
        if nearby & cropsBiomes:
            return "crops"
        return rng.choice(FOUNDING_REASONS)

    def placeSettlements(self, count=6):
        if self.biomes is None:
            raise RuntimeError("Call generate() before placing settlements.")

        rng = random.Random(self.seed + 1000)
        landCells = self.landCells()

        if len(landCells) < count:
            count = len(landCells)

        chosenCells = rng.sample(landCells, count)
        names = generateUniqueNames(count, seed=self.seed)

        types = list(SPAWN_WEIGHTS.keys())
        weights = list(SPAWN_WEIGHTS.values())

        for (x, y), name in zip(chosenCells, names):
            settlementType = rng.choices(types, weights=weights, k=1)[0]

            if settlementType == "settlement":
                population = rng.choice([150, 300, 450, 700, 1200, 2500])
                settlement = makeSettlement(name, x, y, population)
                if isinstance(settlement, Village):
                    settlement.foundingReason = self.pickFoundingReason(x, y, rng)
            else:
                settlement = makeSpecialSettlement(settlementType, name, x, y)

            self.settlements.append(settlement)

        return self.settlements

    def summary(self):
        lines = [f"Map '{self.name}' ({self.width}x{self.height}, seed={self.seed})"]
        lines.append(f"  Settlements: {len(self.settlements)}")
        for settlement in self.settlements:
            extra = (
                f" ({settlement.foundingReason})"
                if isinstance(settlement, Village) and settlement.foundingReason
                else ""
            )
            lines.append(f"    - {settlement}{extra}")
        return "\n".join(lines)
