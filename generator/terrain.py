import numpy as np

BIOME_COLORS = {
    "ocean": "#1f4e8c",
    "coast": "#e8d9a0",
    "plains": "#8bc34a",
    "forest": "#2e7d32",
    "mountain": "#8d8d8d",
    "snow": "#ffffff",
}


def _random_grid(width, height, seed):
    rng = np.random.default_rng(seed)
    return rng.random((height, width))


def _smooth(grid, passes=4):
    """
    Simple box-blur smoothing.
    Repeatedly replaces each cell with the average of itself and its 4 neighbors.
    """

    result = grid.copy()
    for _ in range(passes):
        up = np.roll(result, -1, axis=0)
        down = np.roll(result, 1, axis=0)
        left = np.roll(result, -1, axis=1)
        right = np.roll(result, 1, axis=1)
        result = (result + up + down + left + right) / 5.0
    return result


def generate_terrain(width, height, seed):
    """
    Returns:
        elevation (np.ndarray) with shape (height, width), values in [0, 1]
        moisture  (np.ndarray) with shape (height, width), values in [0, 1]
    """
    elevation = _smooth(_random_grid(width, height, seed))
    moisture = _smooth(_random_grid(width, height, seed + 1))
    # seed + 1 so they are not identical

    # Normalize both back to [0, 1]
    elevation = (elevation - elevation.min()) / (elevation.max() - elevation.min())
    moisture = (moisture - moisture.min()) / (moisture.max() - moisture.min())

    return elevation, moisture


def classify_biomes(elevation, moisture):
    height, width = elevation.shape
    biomes = np.empty((height, width), dtype=object)

    for y in range(height):
        for x in range(width):
            e = elevation[y, x]
            m = moisture[y, x]

            if e < 0.35:
                biomes[y, x] = "ocean"
            elif e < 0.40:
                biomes[y, x] = "coast"
            elif e > 0.85:
                biomes[y, x] = "snow"
            elif e > 0.70:
                biomes[y, x] = "mountain"
            elif m > 0.5:
                biomes[y, x] = "forest"
            else:
                biomes[y, x] = "plains"

    return biomes
