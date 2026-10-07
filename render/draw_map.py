import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

from generator.terrain import BIOME_COLORS
from models.settlement import Village

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

SETTLEMENT_STYLES = {
    "village": {"marker": "o", "color": "#d32f2f", "size": 30},
    "city": {"marker": "s", "color": "#d32f2f", "size": 60},
    "witch_hut": {"marker": "^", "color": "#8e44ad", "size": 50},
    "school": {"marker": "P", "color": "#2980b9", "size": 55},
    "dungeon": {"marker": "X", "color": "#4a0404", "size": 55},
    "palace": {"marker": "*", "color": "#ffd700", "size": 90},
    "portal": {"marker": "D", "color": "#00e5ff", "size": 55},
}

FOUNDING_REASON_STYLES = {
    "mining": {"marker": "v", "color": "#6d4c41"},
    "market": {"marker": "<", "color": "#f1c40f"},
    "crops": {"marker": "p", "color": "#9ccc65"},
}

FOUNDING_REASON_OFFSET = 15


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

    seen_types = set()
    seen_reasons = set()
    for s in world.settlements:
        style = SETTLEMENT_STYLES.get(
            s.settlement_type, {"marker": "o", "color": "#d32f2f", "size": 30}
        )
        ax.scatter(
            s.x,
            s.y,
            marker=style["marker"],
            s=style["size"],
            c=style["color"],
            edgecolors="black",
            zorder=3,
        )
        ax.annotate(
            s.name,
            (s.x, s.y),
            fontsize=7,
            color="white",
            xytext=(3, 3),
            textcoords="offset points",
        )
        seen_types.add(s.settlement_type)

        if isinstance(s, Village) and s.founding_reason in FOUNDING_REASON_STYLES:
            reason_style = FOUNDING_REASON_STYLES[s.founding_reason]
            ax.scatter(
                s.x + FOUNDING_REASON_OFFSET,
                s.y - FOUNDING_REASON_OFFSET,
                marker=reason_style["marker"],
                s=70,
                c=reason_style["color"],
                edgecolors="black",
                linewidths=1.2,
                zorder=4,
            )
            seen_reasons.add(s.founding_reason)

    from matplotlib.lines import Line2D

    legend_handles = [
        Patch(color=BIOME_COLORS[name], label=name.title()) for name in BIOME_ORDER
    ]
    for stype in sorted(seen_types):
        style = SETTLEMENT_STYLES.get(stype, {"marker": "o", "color": "#d32f2f"})
        legend_handles.append(
            Line2D(
                [0],
                [0],
                marker=style["marker"],
                color="w",
                markerfacecolor=style["color"],
                markeredgecolor="black",
                markersize=8,
                label=stype.replace("_", " ").title(),
                linestyle="none",
            )
        )
    for reason in sorted(seen_reasons):
        style = FOUNDING_REASON_STYLES[reason]
        legend_handles.append(
            Line2D(
                [0],
                [0],
                marker=style["marker"],
                color=style["color"],
                markersize=8,
                label=f"Village: {reason}",
                linestyle="none",
            )
        )

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
