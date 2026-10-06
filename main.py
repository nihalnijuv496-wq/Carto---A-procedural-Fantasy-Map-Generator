import os
import random
import sys

from models.world_map import WorldMap
from database.db import init_db
from database.queries import (
    save_world,
    get_all_maps,
    get_map_by_id,
    get_settlements_for_map,
    delete_map,
    get_total_population,
    get_largest_settlement,
    count_settlements_by_type,
)
from models.world_map import WorldMap
from models.settlement import make_settlement
from render.draw_map import save_map, show_map

OUTPUT_DIR = "output"


def _ask_int(prompt, default):
    raw = input(prompt).strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        print(f"Not a number, using default ({default}).")
        return default


def _print_map_list(maps):
    for row in maps:
        print(
            f"  id={row['id']}  {row['name']}  "
            f"({row['width']}x{row['height']}, seed={row['seed']})  "
            f"created={row['created_at']}"
        )


def generate_new_map():
    print("\n[Generate New Map]")

    name = input("Map name (blank for 'Untitled'): ").strip() or "Untitled"

    width = _ask_int("Width (default 100): ", default=1000)
    height = _ask_int("Height (default 100): ", default=1000)
    settlement_count = _ask_int("Number of settlements (default 6): ", default=6)

    seed = random.randint(0, 999_999)

    world = WorldMap(name, width, height, seed)
    world.generate()
    world.place_settlements(count=settlement_count)

    map_id = save_world(world)

    print(
        f"\nGenerated and saved '{name}' as map id={map_id} (seed={seed}, {width}x{height})."
    )
    show_map(world=world)
    print(world.summary())


def _load_world_from_db(map_id):
    map_row = get_map_by_id(map_id)
    if map_row is None:
        return None

    world = WorldMap(
        map_row["name"], map_row["width"], map_row["height"], map_row["seed"]
    )
    world.generate()

    for row in get_settlements_for_map(map_id):
        settlement = make_settlement(row["name"], row["x"], row["y"], row["population"])
        world.settlements.append(settlement)

    return world


def load_saved_map():
    print("\n[Load Saved Map]")

    maps = get_all_maps()
    if not maps:
        print("No saved maps yet — generate one first (option 1).")
        return

    _print_map_list(maps)
    map_id = _ask_int("Enter map id to load: ", default=maps[0]["id"])

    world = _load_world_from_db(map_id)
    if world is None:
        print("No map found with that id.")
        return

    print(f"\nLoaded '{world.name}' (seed={world.seed}, {world.width}x{world.height}).")
    show_map(world=world)
    print(world.summary())


def list_saved_maps():
    print("\n[Saved Maps]")
    maps = get_all_maps()
    if not maps:
        print("No saved maps yet — generate one first (option 1).")
        return
    _print_map_list(maps)


def manage_maps():
    while True:
        print("\n===== Manage Maps =====")
        print("1. List all maps")
        print("2. View details for a map (settlements, population)")
        print("3. Delete a map")
        print("4. Back to main menu")

        choice = input("> ").strip()

        if choice == "1":
            _manage_list_maps()
        elif choice == "2":
            _manage_view_map_details()
        elif choice == "3":
            _manage_delete_map()
        elif choice == "4":
            return
        else:
            print("Invalid choice, please enter a number from 1-4.")


def _manage_list_maps():
    print("\n[Saved Maps]")
    maps = get_all_maps()
    if not maps:
        print("No saved maps yet — generate one first (option 1).")
        return
    _print_map_list(maps)


def _manage_view_map_details():
    print("\n[Map Details]")
    maps = get_all_maps()
    if not maps:
        print("No saved maps yet — generate one first (option 1).")
        return

    _print_map_list(maps)
    map_id = _ask_int("Enter map id to view: ", default=maps[0]["id"])

    map_row = get_map_by_id(map_id)
    if map_row is None:
        print("No map found with that id.")
        return

    total_pop = get_total_population(map_id)
    largest = get_largest_settlement(map_id)
    type_counts = count_settlements_by_type(map_id)

    print(
        f"\n{map_row['name']}  ({map_row['width']}x{map_row['height']}, seed={map_row['seed']})"
    )
    print(f"  Total population: {total_pop}")
    print(f"  Settlements by type: {type_counts or 'none'}")
    if largest:
        print(
            f"  Largest settlement: {largest['name']} ({largest['type']}, pop={largest['population']})"
        )


def _manage_delete_map():
    print("\n[Delete Map]")
    maps = get_all_maps()
    if not maps:
        print("No saved maps yet — nothing to delete.")
        return

    _print_map_list(maps)
    map_id = _ask_int("Enter map id to delete: ", default=maps[0]["id"])

    map_row = get_map_by_id(map_id)
    if map_row is None:
        print("No map found with that id.")
        return

    confirm = (
        input(
            f"Delete '{map_row['name']}' (id={map_id}) and all its settlements? [y/N]: "
        )
        .strip()
        .lower()
    )
    if confirm == "y":
        delete_map(map_id)
        print("Deleted.")
    else:
        print("Cancelled.")


def export_map():
    print("\n[Export Map]")

    maps = get_all_maps()
    if not maps:
        print("No maps to export yet - generate one first (option 1).")
        return

    _print_map_list(maps)
    map_id = _ask_int("Enter map id to export: ", default=maps[0]["id"])

    world = _load_world_from_db(map_id)
    if world is None:
        print("No map found with that id.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"{world.name.replace(' ', '_')}_{world.seed}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)

    save_map(world, filepath)
    print(f"Saved to {filepath}")


MENU_ACTIONS = {
    "1": generate_new_map,
    "2": load_saved_map,
    "3": manage_maps,
    "4": export_map,
}


def print_menu():
    print("\n===== Carto =====")
    print("1. Generate new map")
    print("2. Load saved map")
    print("3. Manage maps")
    print("4. Export map(PNG)")
    print("5. Exit")


def main():
    init_db()
    print("Welcome to Cartor - a procedural fantasy map generator.")

    while True:
        print_menu()
        choice = input("> ").strip()

        if choice == "5":
            print("Goodbye!")
            sys.exit(0)

        action = MENU_ACTIONS.get(choice)
        if action:
            action()
        else:
            print("Invalid choice, please enter a number from 1-5.")


if __name__ == "__main__":
    main()
