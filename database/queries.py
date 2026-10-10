from datetime import datetime

from database.db import getConnection


def insertMap(name, seed, width, height):
    conn = getConnection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO maps (name, seed, width, height, created_at) VALUES (?, ?, ?, ?, ?)",
        (name, seed, width, height, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    mapId = cur.lastrowid
    conn.close()
    return mapId


def insertSettlement(mapId, settlement):
    data = settlement.toDict()
    conn = getConnection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO settlements (map_id, name, type, x, y, population, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            mapId,
            data["name"],
            data["type"],
            data["x"],
            data["y"],
            data["population"],
            data["notes"],
        ),
    )
    conn.commit()
    conn.close()


def saveWorld(world, mapId=None):
    mapId = insertMap(world.name, world.seed, world.width, world.height)
    for settlement in world.settlements:
        insertSettlement(mapId, settlement)
    return mapId


def getAllMaps():
    conn = getConnection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM maps ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows  # dict like


def getMapById(mapId):
    conn = getConnection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM maps WHERE id = ?", (mapId,))
    row = cur.fetchone()
    conn.close()
    return row


def getSettlementsForMap(mapId):
    conn = getConnection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM settlements WHERE map_id = ?", (mapId,))
    rows = cur.fetchall()
    conn.close()
    return rows


def getTotalPopulation(mapId):
    conn = getConnection()
    cur = conn.cursor()
    cur.execute(
        "SELECT SUM(population) AS total FROM settlements WHERE map_id = ?", (mapId,)
    )
    row = cur.fetchone()
    conn.close()
    return row["total"] or 0


def getLargestSettlement(mapId):
    conn = getConnection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM settlements WHERE map_id = ? ORDER BY population DESC LIMIT 1",
        (mapId,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def countSettlementsByType(mapId):
    conn = getConnection()
    cur = conn.cursor()
    cur.execute(
        "SELECT type, COUNT(*) AS count FROM settlements WHERE map_id = ? GROUP BY type",
        (mapId,),
    )
    rows = cur.fetchall()
    conn.close()
    return {row["type"]: row["count"] for row in rows}


def deleteMap(mapId):
    conn = getConnection()
    cur = conn.cursor()
    cur.execute("DELETE FROM maps WHERE id = ?", (mapId,))
    conn.commit()
    conn.close()
