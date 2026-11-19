"""Tests for the episode 2 API. Run with `uv run pytest` from this folder.

Every test gets a known admin key and its own empty database in a temporary folder.
The trick is `app.dependency_overrides`: wherever an endpoint asks for `get_admin_api_key`
or `get_db`, FastAPI calls our test version instead. The endpoints don't know and don't care.
"""

import pytest
from fastapi.testclient import TestClient

from db import connect, create_tables, get_db
from main import app, get_admin_api_key

AUTH = {"X-Api-Key": "test-key"}
PIKACHU = {"display_name": "Pikachu", "type1": "electric"}


@pytest.fixture
def client(tmp_path):
    db_path = str(tmp_path / "test.db")

    # Not :memory: -- every connect() to :memory: gets a brand new, empty database,
    # so the table would be gone by the next request.
    connection = connect(db_path)
    create_tables(connection)
    connection.close()

    def get_test_db():
        connection = connect(db_path)
        try:
            yield connection
        finally:
            connection.close()

    app.dependency_overrides[get_admin_api_key] = lambda: "test-key"
    app.dependency_overrides[get_db] = get_test_db
    # No `with TestClient(app)`: that would run the real lifespan, which creates
    # pokedex.db in the current folder. We've already made our tables.
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_starts_empty(client):
    assert client.get("/pokemon").json() == []


def test_put_creates_then_replaces(client):
    first = client.put("/pokemon/pikachu", json=PIKACHU, headers=AUTH)
    assert first.status_code == 201
    assert first.json() == {"slug": "pikachu", "type2": None} | PIKACHU

    second = client.put(
        "/pokemon/pikachu",
        json={"display_name": "Pikachu", "type1": "electric", "type2": "steel"},
        headers=AUTH,
    )
    assert second.status_code == 200
    assert client.get("/pokemon/pikachu").json()["type2"] == "steel"
    assert len(client.get("/pokemon").json()) == 1


def test_filter_by_type(client):
    client.put("/pokemon/pikachu", json=PIKACHU, headers=AUTH)
    client.put(
        "/pokemon/rotom-wash",
        json={"display_name": "Rotom", "type1": "electric", "type2": "water"},
        headers=AUTH,
    )
    client.put("/pokemon/squirtle", json={"display_name": "Squirtle", "type1": "water"}, headers=AUTH)

    water = client.get("/pokemon", params={"type": "water"}).json()
    assert [p["slug"] for p in water] == ["rotom-wash", "squirtle"]


def test_get_missing_is_404(client):
    assert client.get("/pokemon/missingno").status_code == 404


def test_delete(client):
    client.put("/pokemon/pikachu", json=PIKACHU, headers=AUTH)

    assert client.delete("/pokemon/pikachu", headers=AUTH).status_code == 204
    assert client.get("/pokemon/pikachu").status_code == 404
    assert client.delete("/pokemon/pikachu", headers=AUTH).status_code == 404


def test_writes_need_the_right_key(client):
    no_key = client.put("/pokemon/pikachu", json=PIKACHU)
    wrong_key = client.put("/pokemon/pikachu", json=PIKACHU, headers={"X-Api-Key": "nope"})

    assert no_key.status_code == 401
    assert wrong_key.status_code == 401
    assert wrong_key.headers["WWW-Authenticate"] == "APIKey"
    assert client.get("/pokemon").json() == []


def test_auth_is_checked_before_404(client):
    # Otherwise anyone could find out which slugs exist by trying to delete them.
    assert client.delete("/pokemon/missingno").status_code == 401


def test_each_test_gets_a_fresh_database(client):
    # If the override leaked or the database were shared, earlier tests' data would be here.
    assert client.get("/pokemon").json() == []
