# Workshop Outline

Time: 3 hours, with breaks.

Format is "do something, observe what happens, answer why" wherever possible. Every
section has at least one **Observe → why?** prompt. Those are the bit that matters;
the typing is just how we get there.

Solution key lives in [code/](code/) — `main.py` is the finished API, `test_main.py`
the finished tests, `storage.py` the file participants get handed in section 6.

| # | Section | Time | Running total |
|---|---------|------|---------------|
| 1 | Initial setup | 15 min | 0:15 |
| 2 | Hello world | 20 min | 0:35 |
| 3 | Pick your domain + first GET | 20 min | 0:55 |
| — | **Break** | 10 min | 1:05 |
| 4 | Request bodies (+ validation tangents) | 30 min | 1:35 |
| 5 | Status codes | 25 min | 2:00 |
| — | **Break** | 10 min | 2:10 |
| 6 | Persistence, and a taste of DI | 20 min | 2:30 |
| 7 | Testing with TestClient | 25 min | 2:55 |
| 8 | Wrap-up | 5 min | 3:00 |

Sections 6 and 7 are the compressible ones if we're running late — 6 is drop-in-a-file
and 7 can be cut to just the happy-path test. Don't sacrifice 4 or 5.

---

## 1. Initial setup (15 min)

1. Everyone creates a repo (https://github.com/new)
2. Open it in Coder
3. `uv init && uv add "fastapi[standard]"`

Housekeeping while `uv` runs: everything is in ephemeral, reproducible Coder
workspaces, so "works on my machine" shouldn't come up. If something breaks for one
person it should break for everyone.

## 2. Hello world (20 min)

Write this into `main.py`:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
```

`uv run fastapi dev`, and let it rip.

Show how to call it (curl). Then take a look at `/docs` — and point out that nobody
wrote that. It's generated from the code, and it will keep being generated from the
code all afternoon. When it looks wrong, that's a real signal.

Also worth a look: `/openapi.json`, the thing `/docs` is rendering.

**Observe → why?** Change the returned message, save, and curl again without
restarting anything. It changed. Now: what is dev mode actually doing, and what are
the two differences from prod mode?

<details>
<summary>Answer</summary>

Dev mode watches the files and reloads on change, and it only binds to localhost.
Prod mode does neither — no reloading, and it listens on all interfaces.
</details>

## 3. Pick your domain + first GET (20 min)

Everyone picks something to build a CRUD API for. **Not a pet store.** Ideas, but
pick your own if you have one:

- Pokémon (name, primary type, optional secondary type) ← what the solution key uses
- Coffee brews (bean, method, grind, dose, brew time)
- Incident log (title, severity, status, opened-at)
- Board game collection (title, min/max players, playtime, rating)

Whatever you pick, you need a **name-ish field that's unique** — it'll be the key in
the URL path for the rest of the workshop.

Now build one endpoint that lists everything from a hardcoded module-level dict:

```python
datastore: dict[str, Pokemon] = {
    "Pikachu": Pokemon(name="Pikachu", type1="electric"),
}


@app.get("/pokemon")
async def get_all_pokemon() -> list[Pokemon]:
    return list(datastore.values())
```

You'll need a Pydantic model for this. `class Pokemon(BaseModel)`, fields with type
annotations, that's it for now.

**Observe → why?** Delete the `-> list[Pokemon]` return annotation and look at
`/docs` again. The schema is gone — the response is just "some JSON". Put it back and
it returns. Why does an annotation Python barely enforces at runtime end up in the
docs?

<details>
<summary>Answer</summary>

FastAPI reads the annotations to build the OpenAPI schema — the same information it
uses to serialize and validate the response. The type hint isn't decoration, it's the
input to both.
</details>

## 4. Request bodies, and what happens when they're wrong (30 min)

Add POST. The trick to learn here: a parameter annotated with a Pydantic model is the
request body, and FastAPI parses and validates it before your function is called.

```python
@app.post("/pokemon")
async def create_pokemon(to_create: Pokemon) -> Pokemon:
    datastore[to_create.name] = to_create
    return to_create
```

Try it from `/docs` rather than curl — the form is generated from the model.

**Observe → why?** Now send garbage on purpose:

```bash
curl -s localhost:8000/pokemon -H 'content-type: application/json' \
  -d '{"name": "", "type1": "cardboard"}'
```

Read the response body properly, don't just glance at the status. What status code
came back, why that one and not 400, and how did the error know the field *path*?
Then: your endpoint function — did it run at all?

<details>
<summary>Answer</summary>

422. Validation happened before the endpoint was ever called, so the body isn't a
thing your code has to check. The `loc` array is the path to the offending field,
which is how it can point inside nested objects too.
</details>

### Tangents to take here (whiteboard, not slides)

Both of these make the 422 above more interesting, and both show up in `/docs`:

- **Length and value constraints.** `Field(min_length=1, max_length=32)` on the name.
  Numeric fields get `ge` / `le`. Wrap it in `Annotated[str, Field(...)]`.
- **Enums for closed sets.** A `StrEnum` for Pokémon types (or brew method, or
  severity) turns a free-text field into a dropdown in `/docs` and a 422 for anything
  else. Cheapest validation win available.

Have people add one of each to their model and re-send the garbage request. The error
list gets longer and more specific.

## 5. Status codes (25 min)

These map well onto CRUD, in escalating difficulty. Build up the remaining endpoints
as an excuse to hit all three cases.

### Easy: a fixed non-200 success

Creating a thing should be 201, not 200. Deleting should be 204.

```python
@app.post("/pokemon", status_code=201)
# or, more readably
from fastapi import status
@app.post("/pokemon", status_code=status.HTTP_201_CREATED)
```

### Medium: errors

Just raise `HTTPException`. Add the endpoints that need it:

- `GET /pokemon/{name}` → 404 if it isn't there
- `POST /pokemon` → 409 if the name is taken
- `DELETE /pokemon/{name}` → 404 if it isn't there
- `PUT /pokemon/{name}` → 400 if the path name and body name disagree

That last one is worth a minute of discussion: the same information arriving via two
routes means it can conflict, and you have to pick a rule.

**Observe → why?** `DELETE` a name that doesn't exist, *before* adding the 404. With
`datastore.pop(name)` and no check, what status comes back, and what does the client
learn about what went wrong?

<details>
<summary>Answer</summary>

500. The `KeyError` escapes, FastAPI turns any unhandled exception into a generic
500, and the client is told nothing useful — it can't tell "no such item" from "your
database is on fire". Which is why the 404 is your job, not the framework's.
</details>

### Hard: the status code isn't known until runtime

`PUT` should arguably be 201 when it creates and 200 when it replaces. The decorator
can only hold one number, so take a `Response` argument and set the code on it:

```python
async def replace_pokemon(name: str, to_store: Pokemon, response: Response) -> Pokemon:
    ...
    if name not in datastore:
        response.status_code = status.HTTP_201_CREATED
```

**Observe → why?** Do that, then check `/docs`. The 201 isn't documented. Why not,
and what do you have to add to fix it?

<details>
<summary>Answer</summary>

The docs are built by inspecting the code, and nothing static says 201 is possible —
it's decided by a branch at request time. Declare it yourself with
`responses={201: {"description": "..."}}` on the decorator. Good illustration of the
limit of the automatic docs: they see the signature, not the logic.
</details>

## 6. Persistence, and a taste of dependency injection (20 min)

Motivate it with the bug they've probably already hit:

**Observe → why?** POST a few items. Now touch `main.py` — add a blank line, save.
Curl the list endpoint. Everything's gone. Why does editing an unrelated line delete
your data?

<details>
<summary>Answer</summary>

The reloader doesn't patch the running process, it starts a fresh one. The dict is
module state, so it dies with the old process and the new one re-runs the module from
scratch, hardcoded seed data and all.
</details>

So we need storage that outlives the process. **You are not writing it** — grab
[code/storage.py](code/storage.py) and drop it next to `main.py`. It stores any
Pydantic model as JSON in SQLite, so it doesn't care which domain you picked.

Read the docstring on `store_dependency` and wire it up:

```python
pokemon_store = store_dependency(Pokemon)
StoreDep = Annotated[Store[Pokemon], Depends(pokemon_store)]


@app.get("/pokemon")
async def get_all_pokemon(store: StoreDep) -> list[Pokemon]:
    return store.list()
```

Then convert the other endpoints — `store.get/put/delete/list` replace the dict
operations. `get` returns `None` when missing, `delete` returns whether it deleted
anything, which makes the 404s straightforward.

Point out what just happened, because it's the actual lesson: endpoints declare what
they need as an argument, and FastAPI constructs it per request and cleans it up
afterwards. No global, no setup boilerplate in every function. That's dependency
injection, and it's why the next section is easy.

**Observe → why?** POST something, then stop the server entirely and start it again.
Your data's still there. Also: `store` is a parameter like `name` and `to_create` are
— so why doesn't it show up in `/docs` as a query parameter or a request body?

<details>
<summary>Answer</summary>

`Depends` marks it as something FastAPI supplies, not something the client sends, so
it's excluded from the schema. FastAPI splits your parameters into "comes from the
request" and "comes from a dependency" based on the annotation.
</details>

## 7. Testing with TestClient (25 min)

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

That test as written is a trap, though, and it's a deliberate one:

**Observe → why?** Run it against a `workshop.db` that already has data in it. It
fails. And a test that *creates* an item passes the first time and then fails on
every subsequent run. Why, and what's wrong with "just delete the db file first"?

<details>
<summary>Answer</summary>

Tests are sharing real persistent state, so they depend on history and on each other.
Deleting the file works until two tests run in parallel, or until you want to keep
your dev data. The real fix is for tests not to touch that file at all.
</details>

The fix reuses section 6's seam from the other side — `app.dependency_overrides`
tells FastAPI to call something else when an endpoint asks for the store:

```python
@pytest.fixture
def store():
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    app.dependency_overrides[pokemon_store] = lambda: Store(connection, Pokemon)
    yield
    app.dependency_overrides.clear()
```

Now every test gets an empty in-memory database. Have people write tests for the
status codes they built in section 5 — 201 on create, 409 on duplicate, 404 on
missing, 422 on invalid, 204 on delete. Full set in
[code/test_main.py](code/test_main.py).

If there's time, the 422 test is the nice one: assert on
`response.json()["detail"][0]["loc"]` and you're testing the error contract, not just
the status.

## 8. Wrap-up (5 min)

What we didn't cover, roughly in order of how much I'd want a second workshop on it:

- **Async properly.** Everything was `async def` all afternoon and it never mattered,
  because nothing awaited anything. It starts mattering the moment your API calls
  another service.
- **Auth and sessions.**
- **Dependency injection beyond the taste in section 6** — sub-dependencies,
  dependencies with parameters, app-wide dependencies.
- **Background tasks, middleware, routers** for when one `main.py` stops being enough.
