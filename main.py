import os
import random
import sys

from models.world_map import WorldMap
from render.draw_map import show_map

OUTPUT_DIR = "output"

session_maps = []


def _ask_int(prompt, default):
    """falling back to a default on blank/invalid entry."""
    raw = input(prompt).strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        print(f"Not a number, using default ({default}).")
        return default


def generate_new_map():
    """Option 1: Generate a brand new procedural map."""
    print("\n[Generate New Map]")

    name = input("Map name (blank for 'Untitled'): ").strip() or "Untitled"

    width = _ask_int("Width (default 40): ", default=40)
    height = _ask_int("Height (default 30): ", default=30)
    settlement_count = _ask_int("Number of settlements (default 6): ", default=6)

    seed = random.randint(0, 999_999)

    world = WorldMap(name, width, height, seed)
    world.generate()
    world.place_settlements(count=settlement_count)

    session_maps.append(world)

    # print(f"\nGenerated '{name}' (seed={seed}, {width}x{height}).")
    show_map(world=world)
    # print(world.summary())

    # TODO: once database/ exists, save this map + its settlements here


def load_saved_map():
    """Option 2: Load a previously saved map from the database."""
    print("\n[Load Saved Map]")
    # TODO: list maps, ask user for an id and load it


def list_saved_maps():
    """Option 3: List all maps currently stored in the database."""
    print("\n[Saved Maps]")
    # TODO: query database/queries.py


def export_map():
    """Option 4: Export a map's settlements to CSV / save the render as PNG."""
    print("\n[Export Map]")
    # TODO: export map


MENU_ACTIONS = {
    "1": generate_new_map,
    "2": load_saved_map,
    "3": list_saved_maps,
    "4": export_map,
}


def print_menu():
    print("\n===== Cartographer =====")
    print("1. Generate new map")
    print("2. Load saved map")
    print("3. List saved maps")
    print("4. Export map")
    print("5. Exit")


def main():
    # TODO: once database/db.py exists, call init_db() here
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
