import numpy as np

BIOME_COLORS = {
    "deep_ocean": "#101038",
    "ocean": "#3c3cb4",
    "ice": "#a0a0ff",
    "coast": "#f7e9a0",
    "plains": "#8db360",
    "forest": "#056621",
    "deep_forest": "#004113",
    "desert": "#faeac1",
    "swamp": "#2c422b",
    "mountain": "#737373",
    "mountain_snow": "#e0e0e0",
    "snowy_land": "#ffffff",
}

DEEP_OCEAN_MAX = 0.18
OCEAN_MAX = 0.30
COAST_MAX = 0.35
MOUNTAIN_MIN = 0.75
SNOW_PEAK_MIN = 0.90
COLD_MAX = 0.05
HOT_MIN = 0.70
DESERT_MOISTURE_MAX = 0.35
SWAMP_MOISTURE_MIN = 0.60
SWAMP_MAX_ELEVATION = 0.50
FOREST_MOISTURE_MIN = 0.55
DEEP_FOREST_ELEV_MIN = 0.55

SPECK_RADIUS = 6
SPECK_PASSES = 1

ICE_MIN_REACH = 1
ICE_REACH_FRACTION = 0.02
ICE_MAX_REACH_FLOOR = 3
ICE_SHORE_LINK = 2


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


def _normalize(grid):
    return (grid - grid.min()) / (grid.max() - grid.min())


def _normalize_stretched(grid, low_pct=2, high_pct=98):
    """Like _normalize, but ignores the rarest extremes so values spread out
    across 0..1 instead of bunching up around 0.5."""
    lo, hi = np.percentile(grid, [low_pct, high_pct])
    return np.clip((grid - lo) / (hi - lo), 0.0, 1.0)


def _low_res_field(width, height, seed, scale, smooth_passes=2):
    rng = np.random.default_rng(seed)
    low_h = max(2, height // scale + 2)
    low_w = max(2, width // scale + 2)
    raw = _bilinear_upscale(rng.random((low_h, low_w)), height, width)
    return _smooth(raw, passes=smooth_passes)


def _layered_noise(
    width, height, seed, big_scale=8, detail_scale=3, detail_weight=0.25
):
    big_layer = _low_res_field(width, height, seed, big_scale, smooth_passes=0)
    detail_layer = _low_res_field(
        width, height, seed + 7, detail_scale, smooth_passes=0
    )
    combined = (1 - detail_weight) * big_layer + detail_weight * detail_layer
    return _smooth(combined, passes=2)


def _generate_elevation(width, height, seed):
    continent = _low_res_field(
        width, height, seed, scale=max(width, height) // 2, smooth_passes=4
    )
    texture = _layered_noise(
        width, height, seed, big_scale=14, detail_scale=6, detail_weight=0.15
    )

    elevation = 0.85 * continent + 0.15 * texture
    elevation = _normalize(elevation)

    lake_noise = _low_res_field(
        width, height, seed + 500, scale=max(width, height) // 5, smooth_passes=3
    )
    lake_noise = _normalize(lake_noise)
    is_solid_land = elevation > 0.45
    is_lake = is_solid_land & (lake_noise > 0.94)
    elevation = np.where(is_lake, 0.10, elevation)

    elevation = elevation**1.5
    return elevation


def _generate_temperature(width, height, seed):
    """Pure noise. No latitude, so cold regions can appear anywhere."""
    noise = _layered_noise(
        width, height, seed, big_scale=20, detail_scale=5, detail_weight=0.2
    )
    return _normalize_stretched(noise)


def _generate_ice_noise(width, height, seed):
    """Random 0..1 field that decides how far ice spreads from snow."""
    noise = _layered_noise(
        width,
        height,
        seed + 3000,
        big_scale=max(4, max(width, height) // 20),
        detail_scale=max(2, max(width, height) // 60),
        detail_weight=0.4,
    )
    return _normalize(noise)


def generate_terrain(width, height, seed):
    elevation = _generate_elevation(width, height, seed)
    moisture = _normalize(
        _layered_noise(width, height, seed + 1000, big_scale=21, detail_scale=4)
    )
    temperature = _generate_temperature(width, height, seed + 2000)
    ice_noise = _generate_ice_noise(width, height, seed)

    return elevation, moisture, temperature, ice_noise


def _distance_from_mask(mask, max_dist):
    """For every cell, the number of steps (8-directional) to the nearest True
    cell in `mask`, capped at max_dist + 1 for anything farther away."""
    dist = np.full(mask.shape, max_dist + 1, dtype=np.int32)
    dist[mask] = 0
    reached = mask.copy()
    frontier = mask.copy()

    for step in range(1, max_dist + 1):
        p = np.pad(frontier, 1)
        grown = (
            p[:-2, 1:-1]
            | p[2:, 1:-1]
            | p[1:-1, :-2]
            | p[1:-1, 2:]
            | p[:-2, :-2]
            | p[:-2, 2:]
            | p[2:, :-2]
            | p[2:, 2:]
        )
        new = grown & ~reached
        if not new.any():
            break
        dist[new] = step
        reached |= new
        frontier = new

    return dist


def _window_count(mask, radius):
    """Number of True cells in the (2r+1)x(2r+1) window around every cell."""
    p = np.pad(mask.astype(np.int32), radius)
    c = p.cumsum(axis=0).cumsum(axis=1)
    c = np.pad(c, ((1, 0), (1, 0)))
    h, w = mask.shape
    k = 2 * radius + 1
    return c[k : k + h, k : k + w] - c[0:h, k : k + w] - c[k : k + h, 0:w] + c[0:h, 0:w]


def _remove_specks(biomes, radius=None, passes=None):
    """Majority filter over land biomes: tiny isolated patches get absorbed by
    whatever surrounds them. Water and coast are left untouched."""
    radius = SPECK_RADIUS if radius is None else radius
    passes = SPECK_PASSES if passes is None else passes
    land = [
        "plains",
        "forest",
        "deep_forest",
        "desert",
        "swamp",
        "mountain",
        "mountain_snow",
        "snowy_land",
    ]
    for _ in range(passes):
        is_land = np.isin(biomes, land)
        counts = np.stack([_window_count(biomes == name, radius) for name in land])
        winner = np.array(land, dtype=object)[counts.argmax(axis=0)]
        own = np.stack([biomes == name for name in land]).argmax(axis=0)
        own_count = np.take_along_axis(counts, own[None], axis=0)[0]
        change = is_land & (counts.max(axis=0) > own_count)
        biomes = np.where(change, winner, biomes)
    return biomes


def _apply_ice(biomes, elevation, ice_noise):
    height, width = elevation.shape

    is_snow = (biomes == "snowy_land") | (biomes == "mountain_snow")
    if not is_snow.any():
        return biomes

    max_reach = max(ICE_MAX_REACH_FLOOR, int(max(width, height) * ICE_REACH_FRACTION))

    max_shore = max_reach * ICE_SHORE_LINK
    dist_to_snow = _distance_from_mask(is_snow, max_shore)
    shore_reach = ICE_MIN_REACH + ice_noise * (max_shore - ICE_MIN_REACH)
    snowy_shore = (biomes == "coast") & (dist_to_snow <= shore_reach)
    biomes[snowy_shore] = "snowy_land"
    is_snow = is_snow | snowy_shore

    dist = _distance_from_mask(is_snow, max_reach)
    reach = ICE_MIN_REACH + ice_noise * (max_reach - ICE_MIN_REACH)
    is_water = elevation < OCEAN_MAX
    biomes[is_water & (dist <= reach)] = "ice"
    return biomes


def classify_biomes(elevation, moisture, temperature, ice_noise):
    e, m, t = elevation, moisture, temperature

    conditions = [
        e < DEEP_OCEAN_MAX,
        e < OCEAN_MAX,
        e < COAST_MAX,
        (e > SNOW_PEAK_MIN) | ((e > MOUNTAIN_MIN) & (t < COLD_MAX)),
        e > MOUNTAIN_MIN,
        t < COLD_MAX,
        (t > HOT_MIN) & (m < DESERT_MOISTURE_MAX),
        (m > SWAMP_MOISTURE_MIN) & (t > 0.4) & (e < SWAMP_MAX_ELEVATION),
        (m > FOREST_MOISTURE_MIN) & (e > DEEP_FOREST_ELEV_MIN),
        m > FOREST_MOISTURE_MIN,
    ]
    choices = [
        "deep_ocean",
        "ocean",
        "coast",
        "mountain_snow",
        "mountain",
        "snowy_land",
        "desert",
        "swamp",
        "deep_forest",
        "forest",
    ]

    biomes = np.select(conditions, choices, default="plains").astype(object)

    biomes = _remove_specks(biomes)

    return _apply_ice(biomes, elevation, ice_noise)
