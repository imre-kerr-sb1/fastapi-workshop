"""Solution key: the tests from the final section.

Run with `uv run pytest`.

The interesting bit is `store` below. Tests shouldn't touch workshop.db -- they
need their own throwaway data. Rather than reaching into the app to swap out a
global, we tell FastAPI "when an endpoint asks for the store, call this instead".
Same dependency injection seam, used from the other side.
"""

import sqlite3

import pytest
from fastapi.testclient import TestClient

from main import Pokemon, app, pokemon_store
from storage import Store

PIKACHU = {"name": "Pikachu", "type1": "electric", "type2": None}


@pytest.fixture
def store() -> Store[Pokemon]:
    """An empty in-memory store, wired in for the duration of one test."""
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    store = Store(connection, Pokemon)
    app.dependency_overrides[pokemon_store] = lambda: store
    yield store
    app.dependency_overrides.clear()
    connection.close()


@pytest.fixture
def client(store: Store[Pokemon]) -> TestClient:
    return TestClient(app)


def test_list_is_empty_to_begin_with(client: TestClient):
    response = client.get("/pokemon")
    assert response.status_code == 200
    assert response.json() == []


def test_create_then_read_it_back(client: TestClient):
    created = client.post("/pokemon", json=PIKACHU)
    assert created.status_code == 201

    fetched = client.get("/pokemon/Pikachu")
    assert fetched.status_code == 200
    assert fetched.json() == PIKACHU


def test_create_rejects_a_duplicate_name(client: TestClient):
    client.post("/pokemon", json=PIKACHU)
    assert client.post("/pokemon", json=PIKACHU).status_code == 409


def test_missing_pokemon_is_a_404(client: TestClient):
    assert client.get("/pokemon/Missingno").status_code == 404


def test_invalid_type_is_a_422(client: TestClient):
    response = client.post("/pokemon", json={"name": "Pikachu", "type1": "cardboard"})
    assert response.status_code == 422
    # FastAPI tells the caller exactly which field went wrong and why. Print it
    # and have a look -- this is the same body you saw from curl earlier.
    assert response.json()["detail"][0]["loc"] == ["body", "type1"]


def test_put_creates_with_201_and_updates_with_200(client: TestClient):
    created = client.put("/pokemon/Pikachu", json=PIKACHU)
    assert created.status_code == 201

    updated = client.put("/pokemon/Pikachu", json={**PIKACHU, "type2": "steel"})
    assert updated.status_code == 200
    assert updated.json()["type2"] == "steel"


def test_put_rejects_mismatched_names(client: TestClient):
    response = client.put("/pokemon/Raichu", json=PIKACHU)
    assert response.status_code == 400


def test_delete_removes_it(client: TestClient):
    client.post("/pokemon", json=PIKACHU)

    assert client.delete("/pokemon/Pikachu").status_code == 204
    assert client.get("/pokemon/Pikachu").status_code == 404
    assert client.delete("/pokemon/Pikachu").status_code == 404


def test_filtering_by_type_matches_either_slot(client: TestClient):
    client.post("/pokemon", json=PIKACHU)
    client.post("/pokemon", json={"name": "Skarmory", "type1": "steel", "type2": "flying"})

    electric = client.get("/pokemon", params={"type": "electric"}).json()
    assert [p["name"] for p in electric] == ["Pikachu"]

    flying = client.get("/pokemon", params={"type": "flying"}).json()
    assert [p["name"] for p in flying] == ["Skarmory"]
