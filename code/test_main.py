"""Solution key for the testing section -- which is in the FOLLOW-UP workshop.

Testing was cut from workshop 1 for time (see ../next-time.md). This file is kept
because it's written and passing: it's the answer key for the follow-up, and the
"get ahead if you want" handout at the end of workshop 1.

Run with `uv add --dev pytest && uv run pytest`.

Note the `client` fixture reaching into the app to clear a global. That works, and it's
also the motivation for the follow-up's first real lesson: tests shouldn't have to know
your storage is a module-level dict.
"""

import pytest
from fastapi.testclient import TestClient

import main
from main import app

# The request body: no slug, because the URL says which one. See section 5.
VULPIX = {"display_name": "Vulpix", "type1": "fire", "type2": None}
ALOLAN = {"display_name": "Vulpix", "type1": "ice", "type2": None}


@pytest.fixture
def client() -> TestClient:
    """A client against an empty datastore.

    Workshop 1 stores data in a module-level dict, so tests have to clear it between
    runs. In the follow-up we replace this with dependency injection, which is a much
    better answer -- see next-time.md.
    """
    main.datastore.clear()
    return TestClient(app)


def test_list_is_empty_to_begin_with(client: TestClient):
    response = client.get("/pokemon")
    assert response.status_code == 200
    assert response.json() == []


def test_put_creates_then_reads_back(client: TestClient):
    created = client.put("/pokemon/vulpix", json=VULPIX)
    assert created.status_code == 201

    fetched = client.get("/pokemon/vulpix")
    assert fetched.status_code == 200
    assert fetched.json() == {"slug": "vulpix", **VULPIX}


def test_put_is_idempotent(client: TestClient):
    """The whole reason the API has no POST: twice is the same as once."""
    assert client.put("/pokemon/vulpix", json=VULPIX).status_code == 201
    assert client.put("/pokemon/vulpix", json=VULPIX).status_code == 200
    assert len(client.get("/pokemon").json()) == 1


def test_put_replaces_in_place(client: TestClient):
    client.put("/pokemon/vulpix", json=VULPIX)
    updated = client.put("/pokemon/vulpix", json={**VULPIX, "type2": "psychic"})
    assert updated.status_code == 200
    assert updated.json()["type2"] == "psychic"


def test_upsert_201_carries_no_location_header(client: TestClient):
    """RFC 9110 wants Location on a 201 -- unless it would just repeat the request URI."""
    created = client.put("/pokemon/vulpix", json=VULPIX)
    assert created.status_code == 201
    assert "location" not in {k.lower() for k in created.headers}


def test_two_forms_may_share_a_display_name(client: TestClient):
    """Alolan Vulpix. Same label, different identity -- and no 409 to fight."""
    assert client.put("/pokemon/vulpix", json=VULPIX).status_code == 201
    assert client.put("/pokemon/vulpix-alola", json=ALOLAN).status_code == 201

    by_slug = {p["slug"]: p["type1"] for p in client.get("/pokemon").json()}
    assert by_slug == {"vulpix": "fire", "vulpix-alola": "ice"}


def test_missing_pokemon_is_a_404(client: TestClient):
    assert client.get("/pokemon/no-such-mon").status_code == 404


@pytest.mark.parametrize(
    "bad_slug",
    ["Vulpix", "vulpix alola", "Type: Null", "trailing ", "flabébé"],
    ids=["uppercase", "space", "colon-and-space", "trailing-space", "non-ascii"],
)
def test_unusable_slug_is_a_422_not_a_404(client: TestClient, bad_slug: str):
    """"That can't be an identifier" and "nothing is here" are different answers."""
    assert client.put(f"/pokemon/{bad_slug}", json=VULPIX).status_code == 422


def test_slug_containing_a_slash_never_reaches_the_app(client: TestClient):
    """The bug section 5 designs away: an extra path segment matches no route.

    404 from routing rather than 422 from validation -- and crucially, nothing is
    written, so there's no unaddressable row left behind.
    """
    assert client.put("/pokemon/Porygon/Z", json=VULPIX).status_code == 404
    assert client.put("/pokemon/Porygon%2FZ", json=VULPIX).status_code == 404
    assert client.get("/pokemon").json() == []


def test_invalid_type_is_a_422(client: TestClient):
    response = client.put(
        "/pokemon/vulpix", json={"display_name": "Vulpix", "type1": "cardboard"}
    )
    assert response.status_code == 422
    # FastAPI tells the caller exactly which field went wrong and why.
    assert response.json()["detail"][0]["loc"] == ["body", "type1"]


def test_delete_removes_it(client: TestClient):
    client.put("/pokemon/vulpix", json=VULPIX)

    assert client.delete("/pokemon/vulpix").status_code == 204
    assert client.get("/pokemon/vulpix").status_code == 404
    assert client.delete("/pokemon/vulpix").status_code == 404


def test_filtering_by_type_matches_either_slot(client: TestClient):
    client.put("/pokemon/vulpix", json=VULPIX)
    client.put(
        "/pokemon/skarmory",
        json={"display_name": "Skarmory", "type1": "steel", "type2": "flying"},
    )

    fire = client.get("/pokemon", params={"type": "fire"}).json()
    assert [p["slug"] for p in fire] == ["vulpix"]

    flying = client.get("/pokemon", params={"type": "flying"}).json()
    assert [p["slug"] for p in flying] == ["skarmory"]
