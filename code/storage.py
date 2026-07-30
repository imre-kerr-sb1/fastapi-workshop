"""Persistent storage, pre-made for you.

You are not expected to write this file, only to use it. Skim it if you're
curious, then read the docstring on `store_dependency` -- that's the part you
need.

It stores any Pydantic model as JSON in a SQLite table, keyed by a string of
your choosing. That means it doesn't care what your domain looks like: bring
your own model, get persistence for free.
"""

import json
import sqlite3
from collections.abc import Iterator
from typing import Generic, TypeVar

from pydantic import BaseModel

M = TypeVar("M", bound=BaseModel)

DB_PATH = "workshop.db"


class Store(Generic[M]):
    """A tiny key/value collection of Pydantic models, backed by SQLite."""

    def __init__(self, connection: sqlite3.Connection, model: type[M]) -> None:
        self._connection = connection
        self._model = model
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS items (key TEXT PRIMARY KEY, data TEXT NOT NULL)"
        )

    def list(self) -> list[M]:
        rows = self._connection.execute("SELECT data FROM items ORDER BY key").fetchall()
        return [self._model.model_validate_json(data) for (data,) in rows]

    def get(self, key: str) -> M | None:
        """Return the item, or None if there is no such key."""
        row = self._connection.execute(
            "SELECT data FROM items WHERE key = ?", (key,)
        ).fetchone()
        if row is None:
            return None
        return self._model.model_validate_json(row[0])

    def put(self, key: str, item: M) -> None:
        """Insert the item, replacing any existing item with the same key."""
        self._connection.execute(
            "INSERT OR REPLACE INTO items (key, data) VALUES (?, ?)",
            (key, json.dumps(item.model_dump(mode="json"))),
        )

    def delete(self, key: str) -> bool:
        """Delete the item. Returns True if something was actually deleted."""
        cursor = self._connection.execute("DELETE FROM items WHERE key = ?", (key,))
        return cursor.rowcount > 0


def store_dependency(model: type[M]):
    """Build a FastAPI dependency that hands your endpoints a `Store`.

    Use it like this, once, next to your model:

        from typing import Annotated
        from fastapi import Depends
        from storage import Store, store_dependency

        pokemon_store = store_dependency(Pokemon)
        StoreDep = Annotated[Store[Pokemon], Depends(pokemon_store)]

    Then any endpoint that wants storage just asks for it as an argument:

        @app.get("/pokemon")
        async def get_all_pokemon(store: StoreDep) -> list[Pokemon]:
            return store.list()

    Note what you *didn't* have to do: no global, no setup call in every
    endpoint, no passing a connection down through your own code. You declared
    what you needed and FastAPI built it for you. That's dependency injection.
    """

    def get_store() -> Iterator[Store[M]]:
        # check_same_thread=False because FastAPI runs this dependency in a
        # worker thread, but the endpoint that uses the connection runs on the
        # event loop. Different threads, same connection, and SQLite objects to
        # that by default.
        connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        try:
            # Everything before the yield runs before your endpoint...
            yield Store(connection, model)
        except Exception:
            # ...and if your endpoint blew up, the exception is thrown back in
            # here, so a failed request leaves nothing half-written behind.
            connection.rollback()
            raise
        else:
            # ...otherwise we get here once your endpoint has returned.
            connection.commit()
        finally:
            connection.close()

    return get_store
