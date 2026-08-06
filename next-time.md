# Next time

Material for the follow-up workshop. Some of it was cut from the first one for time,
some was never in scope.

Rough shape: **testing is the spine**, and most of the other topics can hang off it,
because each one needs a test to show it works. That also fixes the slightly awkward
thing about workshop 1 — it ends with everyone having untested code.

---

## 1. Testing with TestClient — cut from workshop 1

The one that has to happen, and it should go first. Fully written and verified against
the solution key: [code/test_main.py](code/test_main.py) is a working 16-test suite.

`uv add --dev pytest`. Then:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_list_is_empty_to_begin_with():
    response = client.get("/pokemon")
    assert response.status_code == 200
```

No server, no port, no `uv run fastapi dev` in another terminal — the client talks to
the app object directly.

That test as written is a trap, and it's a deliberate one:

**Observe → why?** Run it against a `workshop.db` that already has data in it. It fails.
And a test that *creates* an item passes the first time and then fails on every
subsequent run. Why, and what's wrong with "just delete the db file first"?

<details>
<summary>Answer</summary>

Tests are sharing real persistent state, so they depend on history and on each other.
Deleting the file works until two tests run in parallel, or until you want to keep your
dev data. The real fix is for tests not to touch that file at all.
</details>

The fix reuses the dependency injection seam from workshop 1 section 7, from the other
side — `app.dependency_overrides` tells FastAPI to call something else when an endpoint
asks for the store:

```python
@pytest.fixture
def store():
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    app.dependency_overrides[pokemon_store] = lambda: Store(connection, Pokemon)
    yield
    app.dependency_overrides.clear()
```

Now every test gets an empty in-memory database. Have people write tests for the status
codes they built in workshop 1 section 6 — 201 on create, 200 on replace, 404 on
missing, 422 on an unusable slug, 204 on delete.

The 422 test is the nice one: assert on `response.json()["detail"][0]["loc"]` and you're
testing the error *contract*, not just the status.

### Callbacks to workshop 1 worth making

- **Idempotency is a testable property.** Workshop 1 section 4 claimed PUT-as-upsert
  means "twice is the same as once". That's an assertion begging to be a test, and it's
  three lines: PUT, PUT again, assert one record and a 201-then-200. See
  `test_put_is_idempotent`.
- **The errors that can't happen.** Section 6 pointed out the design has no 409 and no
  path/body 400. Ask people to write tests for those. They can't — there's no request
  that triggers them. More convincing felt than asserted.
- **The tests that exist because of a design choice.** `test_two_forms_may_share_a_display_name`
  and `test_unusable_slug_is_a_422_not_a_404` both encode section 4 decisions. Good
  illustration that tests document intent, not just behaviour.

### Presenter note: recovering state

People will arrive with their workshop 1 repos in wildly different states, and some
without one at all. Have `main.py`, `main_autoid.py` and `storage.py` ready to hand out,
and open with five minutes of "get to a working CRUD API by any means necessary".

---

## 2. Async, properly

The most valuable one after testing. Everything in workshop 1 was `async def` and it
never once mattered, because nothing ever awaited anything — worth admitting explicitly,
since it's a lie of omission we've been living with.

It starts mattering the moment the API calls another service, which is what most real
APIs do all day. Natural exercises:

- Add an endpoint that calls an external HTTP API with `httpx.AsyncClient`.
- **Observe → why?** Do the same thing with blocking `requests` inside `async def`, fire
  20 concurrent requests at it, and watch the throughput collapse. Then `def` instead of
  `async def` and watch it recover — FastAPI runs sync endpoints in a threadpool, so the
  worst case is specifically "blocking call inside `async def`".
- `asyncio.gather` for fanning out to several services at once.
- Where SQLite fits, given `storage.py` is entirely synchronous.

## 3. Dependency injection beyond the taste

Workshop 1 hands people `storage.py` and asks them to use one dependency without
understanding it. Now open the box:

- Sub-dependencies (a dependency that depends on a dependency).
- Dependencies with parameters, i.e. what `store_dependency(Pokemon)` was actually doing.
- Router- and app-level dependencies.
- `yield` dependencies and cleanup semantics — worth revisiting the commit/rollback in
  `storage.py`, which nobody read closely the first time.
- This is also the natural home for **auth**, since that's where DI earns its keep.

## 4. Auth and sessions

Big enough to be its own workshop. Depends on section 3, since FastAPI's auth story is
essentially "dependencies that raise 401".

## 5. Structure, for when one `main.py` stops being enough

- `APIRouter` and splitting by resource.
- Middleware, and how it differs from a dependency (and when each is the right tool).
- Background tasks.
- Settings and config via `pydantic-settings`.

## 6. Leftovers from workshop 1's loose ends

- **`response_model` vs return annotations.** Modern style is annotations, which is what
  workshop 1 teaches, but `response_model` fills older docs and Stack Overflow answers.
  Two minutes so people can read older material without confusion.
- **405 and trailing-slash behaviour.** Both are common real-world confusions, both are
  nearly free to demo, and neither found a home in workshop 1.
- **Separate input/output models properly.** Workshop 1 sections 4–5 introduce
  `PokemonUpdate` for one specific reason (identity lives in the URL). The general
  pattern — never accept server-controlled fields, never return secrets — deserves
  better than a footnote.
- **PATCH**, which workshop 1 never mentions. Now that PUT-as-replace is well understood,
  partial update is a natural follow-on, and `model_dump(exclude_unset=True)` is the
  trick worth knowing.
