"""Database plumbing. Handed to participants ready-made: the interesting part is using it.

One connection per request, opened by `get_db` and closed when the request is done.
The table is created at startup by `lifespan`, which FastAPI runs once before the first
request.
"""

import sqlite3
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI

DB_PATH = "pokedex.db"

# `IF NOT EXISTS` makes this safe to run on every startup: a fresh file gets the table,
# an existing one is left alone.
SCHEMA = """
CREATE TABLE IF NOT EXISTS pokemon (
    slug TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    type1 TEXT NOT NULL,
    type2 TEXT
)
"""


def connect(path: str) -> sqlite3.Connection:
    # FastAPI may open the connection in one thread and run the endpoint in another.
    # That's safe here because no two requests ever share a connection.
    connection = sqlite3.connect(path, check_same_thread=False)
    # Lets us read columns by name: row["slug"] instead of row[0].
    connection.row_factory = sqlite3.Row
    return connection


def create_tables(connection: sqlite3.Connection) -> None:
    connection.execute(SCHEMA)
    connection.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # No `Depends` here: there is no request yet, so FastAPI has nothing to inject into.
    # We just call our own functions.
    connection = connect(DB_PATH)
    create_tables(connection)
    connection.close()
    yield  # The app runs while we're paused here.


def get_db():
    # Everything before `yield` runs before the endpoint, everything after runs when the
    # request is done -- even if the endpoint raised an exception.
    connection = connect(DB_PATH)
    try:
        yield connection
    finally:
        connection.close()


# Same trick as `SlugPath`: one name for "a connection, and FastAPI gets it from get_db".
DbConnection = Annotated[sqlite3.Connection, Depends(get_db)]
