import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

from generator.terrain import BIOME_COLORS

BIOME_ORDER = [
    "deep_ocean",
    "ocean",
    "ice",
    "coast",
    "plains",
    "forest",
    "deep_forest",
    "desert",
    "swamp",
    "mountain",
    "mountain_snow",
    "snowy_land",
]
BIOME_TO_INDEX = {name: i for i, name in enumerate(BIOME_ORDER)}


def _biomes_to_index_grid(biomes):
    height, width = biomes.shape
    index_grid = np.zeros((height, width), dtype=int)
    for y in range(height):
        for x in range(width):
            index_grid[y, x] = BIOME_TO_INDEX[biomes[y, x]]
    return index_grid


def _build_figure(world):
    index_grid = _biomes_to_index_grid(world.biomes)
    cmap = ListedColormap([BIOME_COLORS[name] for name in BIOME_ORDER])

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.imshow(index_grid, cmap=cmap, vmin=0, vmax=len(BIOME_ORDER) - 1, origin="upper")

    for s in world.settlements:
        marker = "s" if s.settlement_type == "city" else "o"
        size = 60 if s.settlement_type == "city" else 30
        ax.scatter(
            s.x, s.y, marker=marker, s=size, c="#d32f2f", edgecolors="black", zorder=3
        )
        ax.annotate(
            s.name,
            (s.x, s.y),
            fontsize=7,
            color="white",
            xytext=(3, 3),
            textcoords="offset points",
        )

    legend_handles = [
        Patch(color=BIOME_COLORS[name], label=name.title()) for name in BIOME_ORDER
    ]
    ax.legend(
        handles=legend_handles, loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=8
    )

    ax.set_title(f"{world.name} (seed={world.seed})")
    ax.set_xticks([])
    ax.set_yticks([])
    fig.tight_layout()
    return fig


def show_map(world):
    fig = _build_figure(world)
    plt.show()
    plt.close(fig)


def save_map(world, filepath):
    fig = _build_figure(world)
    fig.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return filepath
