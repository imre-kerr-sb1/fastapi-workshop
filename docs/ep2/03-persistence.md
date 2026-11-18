# 4. Database

- TODO: the dict dies on every reload (callback to ep1 wrap-up)
- TODO: why SQLite: one file, in the stdlib, no server. Real life = Postgres (see wrap-up)
- TODO: plan for the chapter: plumbing is handed out, you write the SQL

## Oppsettet: `db.py`

- TODO: copy this into `db.py` next to `main.py`; not the interesting part

```python title="db.py"
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
    connection = connect(DB_PATH)
    create_tables(connection)
    connection.close()
    yield  # The app runs while we're paused here.


def get_db():
    connection = connect(DB_PATH)
    try:
        yield connection
    finally:
        connection.close()


DbConnection = Annotated[sqlite3.Connection, Depends(get_db)]
```

### `lifespan`

- TODO: runs once at startup, code after `yield` at shutdown
- TODO: no request yet → no `Depends` here; we call our own functions
- TODO: `CREATE TABLE IF NOT EXISTS` = our whole "migration system", and its limit

```python title="main.py" hl_lines="6"
from db import DbConnection, lifespan

app = FastAPI(
    title="Pokédex",
    summary="A toy CRUD API, built to demonstrate rather too many FastAPI features.",
    lifespan=lifespan,
)
```

### `get_db` og `yield`

- TODO: before `yield` = before the endpoint, after = when the request is done
- TODO: `finally` → closed even when the endpoint raises
- TODO: one connection per request

### `DbConnection`

- TODO: same trick as `SlugPath`: a name for "connection, from `get_db`"

## SQL i egne funksjoner

- TODO: connection as first argument, like `pd.read_sql(query, conn)`
- TODO: no HTTP in here: no status codes, no `HTTPException`
- TODO: why not inline in the endpoint: reuse (GET, PUT both need the lookup)

```python title="main.py"
def row_to_pokemon(row: sqlite3.Row) -> Pokemon:
    return Pokemon(
        slug=row["slug"],
        display_name=row["display_name"],
        type1=row["type1"],
        type2=row["type2"],
    )


def fetch_pokemon(connection: sqlite3.Connection, slug: str) -> Pokemon | None:
    row = connection.execute("SELECT * FROM pokemon WHERE slug = ?", (slug,)).fetchone()
    if row is None:
        return None
    return row_to_pokemon(row)
```

- TODO: `?` placeholders, never f-strings (SQL injection; data people know this)

## Tilkoblingen i et endepunkt

```python title="main.py" hl_lines="6"
@app.get(
    "/pokemon/{slug}",
    summary="Fetch a single Pokémon",
    responses={404: {"description": "No Pokémon with that slug"}},
)
async def get_pokemon(slug: SlugPath, connection: DbConnection) -> Pokemon:
    pokemon = fetch_pokemon(connection, slug)
    if pokemon is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Pokémon with slug {slug!r}")
    return pokemon
```

- TODO: the endpoint asks, FastAPI calls `get_db`, endpoint never opens/closes anything
- TODO: the 404 lives here, not in `fetch_pokemon`: HTTP stuff in endpoints, SQL in functions

## Skriving og `commit`

- TODO: writes need `connection.commit()`, or they vanish when the connection closes
- TODO: commit in the write function, not after `yield` in `get_db` (could run after the response is sent)

## Oppgaver

1. TODO: swap the dict for SQLite: `db.py`, `lifespan`, single GET (code above)
2. TODO: list endpoint: write `fetch_all_pokemon` with the type filter
    - TODO: hint: `:type IS NULL OR :type IN (type1, type2)`
3. TODO: PUT as upsert, keep 201 vs 200
    - TODO: hint: `INSERT ... ON CONFLICT (slug) DO UPDATE`, `excluded.`; like `MERGE`
4. TODO: DELETE with 404, one query
    - TODO: hint: `cursor.rowcount`
5. TODO: restart the server, data survives. Open `pokedex.db` in your favourite SQL tool
6. TODO (bonus): pagination: `limit`/`offset` as one dependency, used by the list endpoint
7. TODO (bonus): fetch-or-404 as a dependency, so `get_pokemon` receives a `Pokemon`
    - TODO: hint: same shape as `check_api_key_value`, but it returns something

!!! tip "Endre tabeller senere"
    - TODO: `IF NOT EXISTS` can't alter an existing table
    - TODO: small: `PRAGMA user_version`. Real: Alembic
