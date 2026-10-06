import numpy as np

BIOME_COLORS = {
    "ocean": "#1f4e8c",
    "coast": "#e8d9a0",
    "plains": "#8bc34a",
    "forest": "#2e7d32",
    "mountain": "#8d8d8d",
    "snow": "#ffffff",
}


def _bilinear_upscale(low_res, out_height, out_width):
    low_h, low_w = low_res.shape

    ys = np.linspace(0, low_h - 1, out_height)
    xs = np.linspace(0, low_w - 1, out_width)

    y0 = np.floor(ys).astype(int)
    x0 = np.floor(xs).astype(int)
    y1 = np.clip(y0 + 1, 0, low_h - 1)
    x1 = np.clip(x0 + 1, 0, low_w - 1)

    yf = (ys - y0).reshape(-1, 1)
    xf = (xs - x0).reshape(1, -1)

    top_left = low_res[np.ix_(y0, x0)]
    top_right = low_res[np.ix_(y0, x1)]
    bottom_left = low_res[np.ix_(y1, x0)]
    bottom_right = low_res[np.ix_(y1, x1)]

    top = top_left * (1 - xf) + top_right * xf
    bottom = bottom_left * (1 - xf) + bottom_right * xf
    return top * (1 - yf) + bottom * yf


def _smooth(grid, passes=2):
    result = grid.copy()
    for _ in range(passes):
        up = np.roll(result, -1, axis=0)
        down = np.roll(result, 1, axis=0)
        left = np.roll(result, -1, axis=1)
        right = np.roll(result, 1, axis=1)
        result = (result + up + down + left + right) / 5.0
    return result


def _layered_noise(
    width, height, seed, big_scale=10, detail_scale=3, detail_weight=0.25
):
    rng = np.random.default_rng(seed)

    big_h = max(2, height // big_scale + 2)
    big_w = max(2, width // big_scale + 2)
    big_layer = _bilinear_upscale(rng.random((big_h, big_w)), height, width)

    detail_h = max(2, height // detail_scale + 2)
    detail_w = max(2, width // detail_scale + 2)
    detail_layer = _bilinear_upscale(rng.random((detail_h, detail_w)), height, width)

    combined = (1 - detail_weight) * big_layer + detail_weight * detail_layer
    return _smooth(combined, passes=2)


def _continent_mask(width, height, seed, scale=14):
    rng = np.random.default_rng(seed)
    low_h = max(2, height // scale + 2)
    low_w = max(2, width // scale + 2)
    raw = _bilinear_upscale(rng.random((low_h, low_w)), height, width)
    return _smooth(raw, passes=4)


def generate_terrain(width, height, seed):
    continent = _continent_mask(width, height, seed, scale=14)
    texture = _layered_noise(width, height, seed, big_scale=8, detail_scale=3)

    elevation = 0.75 * continent + 0.25 * texture

    moisture = _layered_noise(width, height, seed + 1000, big_scale=10, detail_scale=4)

    elevation = (elevation - elevation.min()) / (elevation.max() - elevation.min())
    moisture = (moisture - moisture.min()) / (moisture.max() - moisture.min())

    elevation = elevation**1.5

    return elevation, moisture


def classify_biomes(elevation, moisture):
    height, width = elevation.shape
    biomes = np.empty((height, width), dtype=object)

    for y in range(height):
        for x in range(width):
            e = elevation[y, x]
            m = moisture[y, x]

            if e < 0.30:
                biomes[y, x] = "ocean"
            elif e < 0.35:
                biomes[y, x] = "coast"
            elif e > 0.95:
                biomes[y, x] = "snow"
            elif e > 0.80:
                biomes[y, x] = "mountain"
            elif m > 0.5:
                biomes[y, x] = "forest"
            else:
                biomes[y, x] = "plains"

    return biomes
