import sys


def generate_new_map():
    """Option 1: Generate a brand new procedural map."""
    print("\n[Generate New Map]")
    # TODO: generate the map, save the map and settlements to the database
    print("Not implemented yet — coming once generator/ and models/ are built.")


def load_saved_map():
    """Option 2: Load a previously saved map from the database."""
    print("\n[Load Saved Map]")
    # TODO: list maps, ask user for an id and load it
    print("Not implemented yet — coming once database/ is built.")


def list_saved_maps():
    """Option 3: List all maps currently stored in the database."""
    print("\n[Saved Maps]")
    # TODO: query database/queries.py
    print("Not implemented yet — coming once database/ is built.")


def export_map():
    """Option 4: Export a map's settlements to CSV / save the render as PNG."""
    print("\n[Export Map]")
    # TODO: export map
    print("Not implemented yet — coming once render/ and utils/ are built.")


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
