from datetime import datetime

from database.db import get_connection


def insert_map(name, seed, width, height):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO maps (name, seed, width, height, created_at) VALUES (?, ?, ?, ?, ?)",
        (name, seed, width, height, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    map_id = cur.lastrowid
    conn.close()
    return map_id


def insert_settlement(map_id, settlement):
    data = settlement.to_dict()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO settlements (map_id, name, type, x, y, population) VALUES (?, ?, ?, ?, ?, ?)",
        (map_id, data["name"], data["type"], data["x"], data["y"], data["population"]),
    )
    conn.commit()
    conn.close()


def save_world(world, map_id=None):
    map_id = insert_map(world.name, world.seed, world.width, world.height)
    for settlement in world.settlements:
        insert_settlement(map_id, settlement)
    return map_id


def get_all_maps():
    """Return every saved map as a list of sqlite3.Row (dict-like access)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM maps ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_map_by_id(map_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM maps WHERE id = ?", (map_id,))
    row = cur.fetchone()
    conn.close()
    return row


def get_settlements_for_map(map_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM settlements WHERE map_id = ?", (map_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_total_population(map_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT SUM(population) AS total FROM settlements WHERE map_id = ?", (map_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row["total"] or 0


def get_largest_settlement(map_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM settlements WHERE map_id = ? ORDER BY population DESC LIMIT 1",
        (map_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def count_settlements_by_type(map_id):
    """Return {type: count} for a map, e.g. {'village': 4, 'city': 2}."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT type, COUNT(*) AS count FROM settlements WHERE map_id = ? GROUP BY type",
        (map_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return {row["type"]: row["count"] for row in rows}


def delete_map(map_id):
    """Delete a map and all its settlements"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM maps WHERE id = ?", (map_id,))
    conn.commit()
    conn.close()
