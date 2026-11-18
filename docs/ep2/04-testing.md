# 4. Testing

- TODO: pytest is already installed; `TestClient` calls the API without a server
- TODO: this is the payoff for `Depends`

## En naiv test

```python title="test_main.py"
import os

# main.py reads this at import time, so it has to be set before the import below.
os.environ["ADMIN_API_KEY"] = "test-key"

from fastapi.testclient import TestClient

from main import app

AUTH = {"X-Api-Key": "test-key"}
PIKACHU = {"display_name": "Pikachu", "type1": "electric"}


def test_put_creates():
    with TestClient(app) as client:  # `with` runs lifespan, so the table exists
        response = client.put("/pokemon/testachu", json=PIKACHU, headers=AUTH)
    assert response.status_code == 201
```

```bash
uv run pytest
```

- TODO: run it twice. Second run fails: 200, not 201. Why?
- TODO: the test wrote into your real `pokedex.db` (look: `testachu` is in your API now)
- TODO: tests must not share data with each other or with you

## `dependency_overrides`

- TODO: "wherever someone asks for `get_db`, call this instead"
- TODO: the endpoints don't change at all
- TODO: pytest fixture: runs before each test that asks for it (same idea as `Depends`!)
- TODO: `tmp_path`: a new empty folder per test, from pytest

```python title="test_main.py"
import pytest

from db import connect, create_tables, get_db


@pytest.fixture
def client(tmp_path):
    db_path = str(tmp_path / "test.db")

    connection = connect(db_path)
    create_tables(connection)
    connection.close()

    def get_test_db():
        connection = connect(db_path)
        try:
            yield connection
        finally:
            connection.close()

    app.dependency_overrides[get_db] = get_test_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_put_creates(client):
    response = client.put("/pokemon/testachu", json=PIKACHU, headers=AUTH)
    assert response.status_code == 201
```

- TODO: why not `:memory:`: new empty database per connection, table gone next request
- TODO: `with` is gone: it would run the real `lifespan` → creates `pokedex.db`; the fixture made the table already
- TODO: `.clear()` so the next test starts clean

## Hvorfor dependency injection, igjen

- TODO: callback to "Hvorfor?" in chapter 3: now they've seen it
- TODO: the endpoints never knew which database they got

## Oppgaver

1. TODO: replace the naive test with the fixture version
2. TODO: PUT twice → 201, then 200, and the change is stored
3. TODO: GET of a missing slug → 404
4. TODO: DELETE, then GET → 404; DELETE again → 404
5. TODO: filter by type
6. TODO: wrong key and missing key → 401
7. TODO (bonus): DELETE of a missing slug without a key → 401, not 404. Why does that matter?
8. TODO (bonus): `@pytest.mark.parametrize` for the type filter
