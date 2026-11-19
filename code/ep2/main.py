"""Solution key for episode 2: the episode 1 API, now with auth and a real database.

Two things changed since episode 1, and both go through `Depends`:

1. Writes need an API key (`check_api_key_value`).
2. The dict is gone. Every endpoint asks for a `DbConnection` and passes it on to small
   plain functions that hold the SQL. HTTP stuff (status codes, 404s) stays in the
   endpoints; the SQL functions know nothing about requests.

Because both the admin key and the database arrive through `Depends`, the tests can
swap them out with `app.dependency_overrides`. See `test_main.py`.
"""

import os
import secrets
import sqlite3
from enum import StrEnum
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, Response, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from db import DbConnection, lifespan

app = FastAPI(
    title="Pokédex",
    summary="A toy CRUD API, built to demonstrate rather too many FastAPI features.",
    lifespan=lifespan,
)

auth_scheme = APIKeyHeader(name="X-Api-Key")

def get_admin_api_key() -> str:
    # A dependency rather than a module-level constant, so tests can override it.
    # KeyError (a 500) if the environment variable is not set: we do *not* want a default.
    return os.environ["ADMIN_API_KEY"]


def check_api_key_value(
    api_key: Annotated[str, Depends(auth_scheme)],
    admin_api_key: Annotated[str, Depends(get_admin_api_key)],
) -> None:
    if not secrets.compare_digest(api_key, admin_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect API Key",
            # Same as FastAPI sends for a missing header. Required by RFC 9110.
            headers={"WWW-Authenticate": "APIKey"},
        )


# The shape of an identifier: lowercase letters and digits, in hyphen-separated groups.
# URL-safe, unambiguous about capitals, and impossible to get a space or a slash into.
SLUG_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"

# `Annotated` means "a string, and here's some extra information about it". The extra
# information is the rule above, which FastAPI uses both to reject bad requests and to
# document the parameter.
SlugPath = Annotated[str, Path(pattern=SLUG_PATTERN, description="The Pokémon's slug.")]


class Type(StrEnum):
    """A closed set of options. Anything else is rejected before our code runs."""

    ELECTRIC = "electric"
    FIRE = "fire"
    WATER = "water"
    GRASS = "grass"
    FLYING = "flying"
    PSYCHIC = "psychic"
    STEEL = "steel"
    ICE = "ice"


class PokemonUpdate(BaseModel):
    """What a client sends us. No slug: the URL already said which Pokémon."""

    display_name: str = Field(
        min_length=1,
        max_length=64,
        description="Shown to humans. May change, and may collide with others.",
        examples=["Vulpix"],
    )
    type1: Type = Field(description="The primary type.")
    type2: Type | None = Field(
        default=None, description="The secondary type, for dual-type Pokémon."
    )


class Pokemon(BaseModel):
    """What we store and send back: the client's data plus the identity it lives under."""

    slug: str = Field(
        pattern=SLUG_PATTERN,
        description="Stable identifier, chosen by the client.",
        examples=["vulpix-alola"],
    )
    display_name: str
    type1: Type
    type2: Type | None = None


# --- SQL ---------------------------------------------------------------------------
# Plain functions, connection first. No HTTP in here: these know nothing about requests,
# status codes or FastAPI.


def row_to_pokemon(row: sqlite3.Row) -> Pokemon:
    return Pokemon(
        slug=row["slug"],
        display_name=row["display_name"],
        type1=row["type1"],
        type2=row["type2"],
    )


def fetch_pokemon(connection: sqlite3.Connection, slug: str) -> Pokemon | None:
    row = connection.execute("SELECT * FROM pokemon WHERE slug = :slug", {"slug": slug}).fetchone()
    if row is None:
        return None
    return row_to_pokemon(row)


def fetch_all_pokemon(connection: sqlite3.Connection, type: Type | None) -> list[Pokemon]:
    rows = connection.execute(
        """
        SELECT * FROM pokemon
        WHERE :type IS NULL OR :type IN (type1, type2)
        ORDER BY slug
        """,
        {"type": type},
    ).fetchall()
    return [row_to_pokemon(row) for row in rows]


def save_pokemon(connection: sqlite3.Connection, pokemon: Pokemon) -> bool:
    """True if the Pokémon is new."""
    values = {
        "slug": pokemon.slug,
        "display_name": pokemon.display_name,
        "type1": pokemon.type1,
        "type2": pokemon.type2,
    }
    # Try to update first. If no row was touched, it didn't exist, so insert it.
    # Safe in SQLite: the UPDATE takes the write lock (even when it matches nothing) and
    # keeps it until commit, so nobody can insert the same slug in between.
    cursor = connection.execute(
        """
        UPDATE pokemon
        SET display_name = :display_name, type1 = :type1, type2 = :type2
        WHERE slug = :slug
        """,
        values,
    )
    created = cursor.rowcount == 0
    if created:
        connection.execute(
            """
            INSERT INTO pokemon (slug, display_name, type1, type2)
            VALUES (:slug, :display_name, :type1, :type2)
            """,
            values,
        )
    connection.commit()
    return created


def delete_pokemon_row(connection: sqlite3.Connection, slug: str) -> bool:
    """True if there was a row to delete."""
    cursor = connection.execute("DELETE FROM pokemon WHERE slug = :slug", {"slug": slug})
    connection.commit()
    return cursor.rowcount > 0


# --- Endpoints ---------------------------------------------------------------------


@app.get("/pokemon", summary="List Pokémon, optionally filtered by type")
async def get_all_pokemon(connection: DbConnection, type: Type | None = None) -> list[Pokemon]:
    return fetch_all_pokemon(connection, type)


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


@app.put(
    "/pokemon/{slug}",
    summary="Create or replace a Pokémon",
    responses={201: {"description": "Created a new Pokémon"}},
    dependencies=[Depends(check_api_key_value)],
)
async def put_pokemon(
    slug: SlugPath, update: PokemonUpdate, response: Response, connection: DbConnection
) -> Pokemon:
    """Create or replace -- the whole write side of the API.

    Send this twice and you get the same single Pokémon, which is exactly what PUT
    promises and exactly why we don't need a POST.
    """
    stored = Pokemon(
        slug=slug,
        display_name=update.display_name,
        type1=update.type1,
        type2=update.type2,
    )
    # 201 if we created it, 200 if we replaced it. We can't know which until we've
    # written, so the status code gets set here rather than on the decorator.
    if save_pokemon(connection, stored):
        response.status_code = status.HTTP_201_CREATED
    return stored


@app.delete(
    "/pokemon/{slug}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Pokémon",
    responses={404: {"description": "No Pokémon with that slug"}},
    dependencies=[Depends(check_api_key_value)],
)
async def delete_pokemon(slug: SlugPath, connection: DbConnection) -> None:
    # No separate "does it exist?" query: the DELETE itself tells us.
    if not delete_pokemon_row(connection, slug):
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Pokémon with slug {slug!r}")
