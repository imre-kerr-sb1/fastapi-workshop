# Where to go next

Ordered, because the order matters — each one makes the next easier. The first two are the
ones that turn what you built into something you'd actually deploy.

## 1. Persistence and dependency injection

**Do this one first.** Not because databases are exciting, but because the *shape* of the
fix is the most useful thing left to learn about FastAPI.

The problem, restated from [step 8](08-wrap-up.md#1-your-data-disappears): your endpoints
reach out and grab a global. Dependency injection inverts that — the endpoint declares what
it needs and FastAPI produces it:

```python
pokemon_store = store_dependency(Pokemon)
StoreDep = Annotated[Store[Pokemon], Depends(pokemon_store)]


@app.get("/pokemon")
async def get_all_pokemon(store: StoreDep) -> list[Pokemon]:
    return store.list()
```

Same rule as everything else in the workshop: the annotation says what you want, the
framework provides it. `store` is just a fourth kind of parameter, alongside path, query
and body.

Work through [`storage.py`](solution-key.md#storagepy) in the solution key and convert your
own API to use it. Things to make sure you understand rather than just copy:

- **`yield` in a dependency.** Everything before the `yield` runs before your endpoint;
  everything after runs once it's done. That's where commit-or-rollback belongs, and it's
  why the transaction stays correct even when an endpoint raises.
- **Why the endpoint bodies barely change.** `datastore[slug]` becomes `store.get(slug)`.
  The whole storage swap is confined to one file, which is the payoff.
- **`Annotated[Store[Pokemon], Depends(...)]`** is the densest line of code in this
  workshop. Read it out loud once: "a store of Pokémon, which FastAPI should get by calling
  this."
- **`.gitignore` needs `workshop.db`** before you commit your database by accident.

📖 [FastAPI: Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/) ·
[Dependencies with yield](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/)

## 2. Testing

Second, because it's much nicer once you've done the first — and that's not a coincidence,
it's the main argument for dependency injection.

Start by just running the [existing suite](solution-key.md#test_mainpy) against your own
API and watching it fail on your field names. Then write your own for the status codes you
built: 201 on create, 200 on replace, 404 on missing, 422 on an unusable identifier, 204 on
delete.

The trap worth walking into deliberately: point `TestClient` at your new SQLite store and
run the suite twice. It passes, then fails, because the second run finds the first run's
data. "Delete the file first" works until you want to keep your dev data or run tests in
parallel. The real fix:

```python
@pytest.fixture
def store():
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    app.dependency_overrides[pokemon_store] = lambda: Store(connection, Pokemon)
    yield
    app.dependency_overrides.clear()
```

`app.dependency_overrides` tells FastAPI to call something *else* when an endpoint asks for
the store — so every test gets an empty in-memory database, and your app code doesn't know
the difference. That's the moment dependency injection stops being an abstract virtue.

Then write one assertion on `response.json()["detail"][0]["loc"]`. You're now testing the
error *contract* rather than just the status code, which is the thing your clients actually
depend on.

📖 [FastAPI: Testing](https://fastapi.tiangolo.com/tutorial/testing/) ·
[Testing dependencies with overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/)

## 3. Async, properly

Time to cash the cheque from [step 3](03-hello-world.md#reading-those-eight-lines).

Everything you wrote was `async def` and it never once mattered, because nothing ever
awaited anything. It starts mattering the moment your API calls *another* service — which is
what most real APIs do all day.

Worth doing as an experiment rather than reading about:

1. Add an endpoint that calls some external API with `httpx.AsyncClient` and `await`.
2. Now write the same thing with blocking `requests` inside `async def`. Fire 20 concurrent
   requests at it and watch throughput collapse.
3. Change *only* `async def` to `def`. Watch it recover.

That third step is the surprising one, and it's the practical rule: FastAPI runs plain `def`
endpoints in a threadpool, so the pathological case is specifically **a blocking call inside
`async def`**. If you're not going to `await`, plain `def` is safer.

Then `asyncio.gather` for fanning out to several services at once, which is where async
actually earns its keep.

📖 [FastAPI: Concurrency and async/await](https://fastapi.tiangolo.com/async/)

## 4. Auth

Big enough to be its own project, and it depends on understanding dependencies — because
FastAPI's auth story is essentially "a dependency that raises 401".

That's genuinely most of it. A dependency inspects the request, finds a token or doesn't,
and either returns the current user or raises. Put it on the endpoint, the router, or the
whole app.

📖 [FastAPI: Security](https://fastapi.tiangolo.com/tutorial/security/)

## 5. Structure, once one file isn't enough

Your `main.py` is about 120 lines. At 600 you'll want:

- **`APIRouter`** — split endpoints across files by resource, mount them on the app.
- **Middleware**, and how it differs from a dependency. Rule of thumb: middleware for things
  that apply to *every* request regardless of what it is (logging, CORS, timing);
  dependencies for things an endpoint *needs* (a store, a user).
- **`BackgroundTasks`** — do something after the response is sent.
- **`pydantic-settings`** — config from environment variables, validated by the same
  machinery as your request bodies.

📖 [FastAPI: Bigger applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)

## Loose ends from the workshop

Small things that didn't fit anywhere:

**`response_model=` vs return annotations.** You used `-> list[Pokemon]`. Older code and
most Stack Overflow answers use `response_model=list[Pokemon]` on the decorator instead.
They do the same job; annotations are the modern style. Worth knowing so older material
doesn't confuse you. There's one case the decorator still handles better: returning a
different type than you declare, e.g. a `dict` from the function with a model as the schema.

**Trailing slashes.** `GET /pokemon` and `GET /pokemon/` are different URLs. Try both
against your API: the one you didn't register answers `307 Temporary Redirect` pointing at
the one you did. Handy, until it isn't — a redirect on a `POST` or `PUT` is a place where
clients differ about whether to resend the body.

**`PATCH`.** The [step 8 exercise](08-wrap-up.md#try-one-more-thing). `PUT` replaces
everything, `PATCH` updates some fields. The hard part is distinguishing "the client sent
null" from "the client didn't mention this field", and the answer is
`model_dump(exclude_unset=True)`.

**Input/output models, properly.** You split `PokemonUpdate` from `Pokemon` for one narrow
reason. The general pattern is broader and more important: never accept a field the client
shouldn't control (`is_admin`, `created_at`), never return one it shouldn't see
(`password_hash`). Inheritance from a shared base cuts the duplication.

📖 [FastAPI: Extra models](https://fastapi.tiangolo.com/tutorial/extra-models/) ·
[Response model](https://fastapi.tiangolo.com/tutorial/response-model/)

---

## The two things worth remembering

If you forget all of the above:

**Write the type, get the behaviour.** Validation, serialization, documentation and
dependency injection are all the same mechanism — you declare what something is, and the
framework does the work. When you find yourself writing plumbing, check whether an
annotation would have done it.

**The best error handling is an error that can't happen.** Your API has no 409 and no
path/body-mismatch 400, and that's a design achievement rather than a coding one. It's also
the one idea here that transfers to code that has nothing to do with the web.
