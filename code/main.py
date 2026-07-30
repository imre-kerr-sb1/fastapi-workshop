"""Solution key: the CRUD API at the end of the workshop.

Participants build their own version of this for a domain of their choosing.
This is the reference implementation, in the state it should be in after the
final section. Earlier sections stop short of this:

- after "Request bodies":  no Field constraints, no enum, no docs polish
- after "Status codes":    the responses below, but a module-level dict
- after "Persistence":     everything except the query parameters
"""

from enum import StrEnum
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

from storage import Store, store_dependency

app = FastAPI(
    title="Pokédex",
    summary="A toy CRUD API, built to demonstrate rather too many FastAPI features.",
)


class Type(StrEnum):
    """Not all eighteen. Nobody needs a workshop about Fairy typing."""

    ELECTRIC = "electric"
    FIRE = "fire"
    WATER = "water"
    GRASS = "grass"
    FLYING = "flying"
    PSYCHIC = "psychic"
    STEEL = "steel"


class Pokemon(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=32,
            description="Unique. Doubles as the identifier in the URL path.",
            examples=["Pikachu"],
        ),
    ]
    type1: Annotated[Type, Field(description="The primary type.")]
    type2: Annotated[
        Type | None,
        Field(default=None, description="The secondary type, for dual-type Pokémon."),
    ]


pokemon_store = store_dependency(Pokemon)
StoreDep = Annotated[Store[Pokemon], Depends(pokemon_store)]


@app.get("/pokemon", summary="List Pokémon, optionally filtered by type")
async def get_all_pokemon(
    store: StoreDep,
    type: Annotated[
        Type | None,
        Query(description="Only return Pokémon with this type, primary or secondary."),
    ] = None,
) -> list[Pokemon]:
    all_pokemon = store.list()
    if type is None:
        return all_pokemon
    return [p for p in all_pokemon if type in (p.type1, p.type2)]


@app.get(
    "/pokemon/{name}",
    summary="Fetch a single Pokémon by name",
    responses={404: {"description": "No Pokémon by that name"}},
)
async def get_pokemon(name: str, store: StoreDep) -> Pokemon:
    found = store.get(name)
    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Pokémon named {name!r}")
    return found


@app.post(
    "/pokemon",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Pokémon",
    responses={409: {"description": "That name is already taken"}},
)
async def create_pokemon(to_create: Pokemon, store: StoreDep) -> Pokemon:
    if store.get(to_create.name) is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"{to_create.name!r} already exists"
        )
    store.put(to_create.name, to_create)
    return to_create


@app.put(
    "/pokemon/{name}",
    summary="Replace a Pokémon, creating it if it doesn't exist",
    responses={
        201: {"description": "Created a new Pokémon"},
        400: {"description": "Path name and body name disagree"},
    },
)
async def replace_pokemon(
    name: str, to_store: Pokemon, store: StoreDep, response: Response
) -> Pokemon:
    if name != to_store.name:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Path says {name!r} but body says {to_store.name!r}",
        )
    # The interesting case: the status code isn't known until we've looked. Ask
    # for a `Response` argument and set it there. Note that the declared
    # status_code (200 by default) becomes the *documented* default, so the 201
    # has to be spelled out in `responses` above to show up in the docs.
    if store.get(name) is None:
        response.status_code = status.HTTP_201_CREATED
    store.put(name, to_store)
    return to_store


@app.delete(
    "/pokemon/{name}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Pokémon",
    responses={404: {"description": "No Pokémon by that name"}},
)
async def delete_pokemon(name: str, store: StoreDep) -> None:
    if not store.delete(name):
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Pokémon named {name!r}")
