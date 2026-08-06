"""Solution key: the CRUD API participants build.

Written for an audience whose Python is not necessarily strong, so it avoids things
that are idiomatic but hard to read cold: no model inheritance, no walrus operator, no
`**kwargs` unpacking, and `Annotated` appears exactly once (on the path parameter,
where there's no good alternative).

Two deliberate design points, both from section 5:

1. There is no POST. Identity is a client-chosen slug, so `PUT /pokemon/{slug}` covers
   both create and replace, and a second write verb would earn nothing.
2. `PokemonUpdate` has no slug, because the URL already said which one. Identity
   arriving in one place only means it can never contradict itself.

Data lives in a module-level dict, so it vanishes every time the server reloads. That's
not an oversight -- it's the closing note of the workshop and the opening of the
follow-up. See ../next-time.md.

`main_autoid.py` is the other design (server-generated ids and POST), for the optional
demo in section 5.
"""

from enum import StrEnum
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Response, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Pokédex",
    summary="A toy CRUD API, built to demonstrate rather too many FastAPI features.",
)

# The shape of an identifier: lowercase letters and digits, in hyphen-separated groups.
# URL-safe, unambiguous about capitals, and impossible to get a space or a slash into.
SLUG_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"

# `Annotated` is the one piece of intimidating syntax we can't avoid: it means "a string,
# and here's some extra information about it". The extra information is the rule above,
# which FastAPI uses both to reject bad requests and to document the parameter.
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


# Our entire database. It is a dict, it lives in memory, and it does not survive a
# restart. Section 8 has opinions about that.
datastore: dict[str, Pokemon] = {}


@app.get("/pokemon", summary="List Pokémon, optionally filtered by type")
async def get_all_pokemon(type: Type | None = None) -> list[Pokemon]:
    all_pokemon = list(datastore.values())
    if type is None:
        return all_pokemon
    return [p for p in all_pokemon if type in (p.type1, p.type2)]


@app.get(
    "/pokemon/{slug}",
    summary="Fetch a single Pokémon",
    responses={404: {"description": "No Pokémon with that slug"}},
)
async def get_pokemon(slug: SlugPath) -> Pokemon:
    if slug not in datastore:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Pokémon with slug {slug!r}")
    return datastore[slug]


@app.put(
    "/pokemon/{slug}",
    summary="Create or replace a Pokémon",
    responses={201: {"description": "Created a new Pokémon"}},
)
async def put_pokemon(
    slug: SlugPath, update: PokemonUpdate, response: Response
) -> Pokemon:
    """Create or replace -- the whole write side of the API.

    Send this twice and you get the same single Pokémon, which is exactly what PUT
    promises and exactly why we don't need a POST.
    """
    # 201 if we're creating, 200 if we're replacing. We can't know which until we look,
    # so the status code gets set here rather than on the decorator.
    if slug not in datastore:
        response.status_code = status.HTTP_201_CREATED

    stored = Pokemon(
        slug=slug,
        display_name=update.display_name,
        type1=update.type1,
        type2=update.type2,
    )
    datastore[slug] = stored
    return stored


@app.delete(
    "/pokemon/{slug}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Pokémon",
    responses={404: {"description": "No Pokémon with that slug"}},
)
async def delete_pokemon(slug: SlugPath) -> None:
    if slug not in datastore:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Pokémon with slug {slug!r}")
    del datastore[slug]
