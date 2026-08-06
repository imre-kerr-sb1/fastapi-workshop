"""Solution key: the CRUD API participants build.

Note what isn't here: there is no POST. Identity is a client-chosen slug, so
`PUT /pokemon/{slug}` covers both create and replace, and a second write verb would
earn nothing. Section 4 is the argument for that; this is the result.

Earlier sections stop short of this:

- after section 3:  the model and the list endpoint only, from a hardcoded dict
- after section 5:  every endpoint, but still a module-level dict
- after section 6:  the status codes below
- after section 7:  this file

`main_autoid.py` is the other design -- server-generated IDs and POST -- for when a
domain can't let the client choose the identifier.
"""

from enum import StrEnum
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, Query, Response, status
from pydantic import BaseModel, Field

from storage import Store, store_dependency

app = FastAPI(
    title="Pokédex",
    summary="A toy CRUD API, built to demonstrate rather too many FastAPI features.",
)

# The identifier's shape, written down once. Lowercase alphanumerics in hyphen-separated
# groups: URL-safe, unambiguous about case, and impossible to get a space or a slash
# into. Both the model field and the path parameter reuse it, so the rule lives in one
# place and shows up in the docs twice.
SLUG_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"

Slug = Annotated[
    str,
    Field(
        min_length=1,
        max_length=32,
        pattern=SLUG_PATTERN,
        description="Stable identifier, chosen by the client. Lowercase, digits, hyphens.",
        examples=["vulpix-alola"],
    ),
]

# Same rule on the path parameter. This is what makes a malformed identifier a 422
# ("that is not a valid slug") instead of a 404 ("nothing here") -- different problems
# that deserve different answers.
SlugPath = Annotated[str, Path(pattern=SLUG_PATTERN, description="The Pokémon's slug.")]


class Type(StrEnum):
    """Not all eighteen. Nobody needs a workshop about Fairy typing."""

    ELECTRIC = "electric"
    FIRE = "fire"
    WATER = "water"
    GRASS = "grass"
    FLYING = "flying"
    PSYCHIC = "psychic"
    STEEL = "steel"
    ICE = "ice"


class PokemonUpdate(BaseModel):
    """What a client sends. Deliberately has no slug: the URL already said which one."""

    display_name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=64,
            description="Shown to humans. May change, and may collide with others.",
            examples=["Vulpix"],
        ),
    ]
    type1: Annotated[Type, Field(description="The primary type.")]
    type2: Annotated[
        Type | None,
        Field(default=None, description="The secondary type, for dual-type Pokémon."),
    ]


class Pokemon(PokemonUpdate):
    """What we store and return: the client's data plus the identity it lives under."""

    slug: Slug


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
    "/pokemon/{slug}",
    summary="Fetch a single Pokémon",
    responses={404: {"description": "No Pokémon with that slug"}},
)
async def get_pokemon(slug: SlugPath, store: StoreDep) -> Pokemon:
    found = store.get(slug)
    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Pokémon with slug {slug!r}")
    return found


@app.put(
    "/pokemon/{slug}",
    summary="Create or replace a Pokémon",
    responses={201: {"description": "Created a new Pokémon"}},
)
async def put_pokemon(
    slug: SlugPath, update: PokemonUpdate, store: StoreDep, response: Response
) -> Pokemon:
    """Upsert. This is the whole write side of the API.

    Idempotent: sending the same request twice leaves the same single Pokémon behind,
    which is exactly what PUT promises. And there is nothing to validate about the
    identifier, because it only arrives in one place.
    """
    # The status code isn't knowable from the signature -- it depends on what's already
    # there -- so it gets set on the Response object at request time.
    if store.get(slug) is None:
        response.status_code = status.HTTP_201_CREATED
        # RFC 9110 wants a Location header on a 201, *unless* it would just repeat the
        # request URI. Here it would, so we leave it off. See main_autoid.py for the
        # case where it carries real information.
    store.put(slug, to_store := Pokemon(slug=slug, **update.model_dump()))
    return to_store


@app.delete(
    "/pokemon/{slug}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Pokémon",
    responses={404: {"description": "No Pokémon with that slug"}},
)
async def delete_pokemon(slug: SlugPath, store: StoreDep) -> None:
    if not store.delete(slug):
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Pokémon with slug {slug!r}")
