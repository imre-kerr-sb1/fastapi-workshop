# Workshop Outline

Time: 3 hours, with breaks.

Format is "do something, observe what happens, answer why" wherever possible. Every
section has at least one **Observe → why?** prompt. Those are the bit that matters;
the typing is just how we get there.

Solution key lives in [code/](code/) — `main.py` is the finished API, `storage.py` is the
file participants get handed in section 7, `main_autoid.py` is the presenter's file for
the optional live demo in section 4. `test_main.py` is for the follow-up workshop, not
this one; see [next-time.md](next-time.md).

| # | Section | Time | Running total |
|---|---------|------|---------------|
| 1 | Initial setup | 15 min | 0:15 |
| 2 | Hello world | 20 min | 0:35 |
| 3 | Pick your domain + first GET | 20 min | 0:55 |
| — | **Break** | 10 min | 1:05 |
| 4 | POST, PUT, and who owns the identifier | 10 min | 1:15 |
| 5 | Request bodies (+ validation tangents) | 30 min | 1:45 |
| 6 | Status codes | 25 min | 2:10 |
| — | **Break** | 10 min | 2:20 |
| 7 | Persistence, and a taste of DI | 20 min | 2:40 |
| — | **Slack** | 15 min | 2:55 |
| 8 | Wrap-up | 5 min | 3:00 |

**Section 4 is a discussion, not an exercise** — ten minutes of talking, deliberately
placed before anyone writes a write endpoint. It's where people choose whether their
identifiers are client-chosen or server-generated, because that choice changes which
endpoints they build in section 5. Getting it right up front is much cheaper than
refactoring into it later.

That 15 minutes of slack is real, not padding. It exists because this outline has been
over budget twice already. If the day runs clean, spend it on the optional POST /
auto-generated-ID / `Location` header demo in section 4 — otherwise it absorbs overrun.

Compress in this order if you're still behind: 7 (it's drop-in-a-file and the DI point
survives being rushed), then 2. Don't sacrifice 5 — request bodies plus the 422 is the
actual core of the workshop.

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

Just pick the domain and the fields for now. **Don't worry about identifiers yet** —
that's section 4, and it's a more interesting question than it looks.

Now build one endpoint that lists everything from a hardcoded module-level list:

```python
datastore = [
    Pokemon(display_name="Pikachu", type1="electric"),
]


@app.get("/pokemon")
async def get_all_pokemon() -> list[Pokemon]:
    return datastore
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

## 4. POST, PUT, and who owns the identifier (10 min)

**Talking only. No typing.** Ten minutes, and it decides what everyone builds next.

Open with the rule everyone has heard:

> "POST is for creating, PUT is for updating."

It's wrong, or at least it's a consequence rather than a rule. The actual distinction in
the spec is:

- **PUT** — "make the resource at *this URI* equal this representation." The client says
  where. Idempotent: send it twice, same result as once.
- **POST** — "process this, according to your own rules." The server decides what happens
  and where anything ends up. Not idempotent.

So the real question isn't which verb creates. It's **who gets to choose the
identifier?**

### If the client can choose it

Then the client already knows the URI, so it can PUT to it — whether or not anything is
there yet. Create and replace are the same operation, and you need exactly one write
endpoint:

```python
@app.put("/pokemon/{slug}")
async def put_pokemon(slug: SlugPath, update: PokemonUpdate) -> Pokemon:
    ...   # creates if absent, replaces if present
```

You get several things for free, which is the point worth labouring:

- **Idempotency.** Retry it after a timeout and you can't accidentally create a second
  one. That's a real distributed-systems property, not a purity argument.
- **No 409.** Nothing to conflict with — you asked for a specific URI and you got it.
- **No path/body disagreement.** Identity arrives in exactly one place, so it can't
  contradict itself. (Hence `PokemonUpdate` having no `slug` field.)

### But the identifier has to be URL-safe

If the client picks it, constrain it — a *slug*, not free text:

```python
SLUG_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"
```

Two minutes on why, because the failure is worse than it looks. A display name is the
wrong thing to put in a URL: `Type: Null` and `Mr. Mime` contain spaces (not legal in a
URL — something has to silently encode them), `Ho-Oh` vs `ho-oh` differ only in case, and
a name with a slash in it — say a typo'd `Porygon-Z` — produces a path with an extra
segment that matches no route at all. Verified against the solution key: it's a 404, and
no amount of `%2F` escaping helps, because the ASGI spec hands the server an
already-decoded path.

Keep the readable URL — those are genuinely good, it's why GitHub ships
`/{owner}/{repo}`. Just don't let the *mutable, human-facing* label be the identity.
Slug for identity, `display_name` for humans, free to change and free to collide.

> **Optional, if it comes up** — someone will ask about Pokémon forms, or hit the same
> thing in their own domain. Vulpix is Fire; Alolan Vulpix is Ice. Same species, same dex
> number, different types. Two records, both wanting to be called "Vulpix" — which is
> fine now, because `vulpix` and `vulpix-alola` are different *identities* with the same
> *label*. Two things can share a name; they can't share an identity. Sixty seconds, and
> only if asked.

### If the client can't choose it

Some domains have no natural identifier, or shouldn't let the client pick one:

| Domain | Why |
|---|---|
| Incidents, log entries, orders | No natural name, and two can be genuinely identical |
| Anything multi-tenant | Client-chosen ids leak information and are guessable |

Then the server generates it — and *now* PUT-as-upsert stops working, because the client
can't name a URI it doesn't know yet. That's exactly when POST earns its place, and it
returns a `Location` header, because the response is the client's only chance to learn
where the thing landed.

**Note the asymmetry:** with server-generated ids, "POST creates, PUT updates" becomes
true. Not because it's a rule about verbs, but because the server owns the identifier.

> Presenter note: this is the **optional live demo**, and only if there's appetite or
> someone asks. [code/main_autoid.py](code/main_autoid.py) is ready to run:
>
> ```bash
> uv run fastapi dev main_autoid.py --port 8001
> curl -i -X POST localhost:8001/incidents -H 'content-type: application/json' \
>   -d '{"title": "Database down", "severity": "high"}'
> ```
>
> `-i` to show the `Location` header. Run it twice: two incidents, two ids, because
> "the database went down again" is a real event. Contrast with PUT, where twice is
> indistinguishable from once. Verified working, including that the `Location` URL is
> actually fetchable. Budget 5–10 min from the slack; skip freely.

### Everyone decides now

Before moving on, each person picks one for their domain:

- **Client-chosen slug** → build `PUT` only. This is what the solution key does and it's
  the right default for Pokémon, coffee, board games.
- **Server-generated id** → build `POST` plus a replace-only `PUT`. Right for incidents
  and anything log-shaped. Use `main_autoid.py` as your reference.

Everything from here on is written for the slug version. If you went the other way, your
create endpoint is a POST and your 404s are on the id — otherwise identical.

## 5. Request bodies, and what happens when they're wrong (30 min)

Now build the write endpoint you just chose. The trick to learn here: a parameter
annotated with a Pydantic model is the request body, and FastAPI parses and validates it
before your function is called.

```python
@app.put("/pokemon/{slug}")
async def put_pokemon(slug: str, update: PokemonUpdate) -> Pokemon:
    stored = Pokemon(slug=slug, **update.model_dump())
    datastore[slug] = stored          # a dict again now that we have keys
    return stored
```

Note the two models. `PokemonUpdate` is what comes in — no `slug`, because the URL
already said which one. `Pokemon` is what goes out, identity included. Splitting input
from output is a FastAPI idiom you'll meet constantly; this is the cheapest possible
first reason to want it.

Try it from `/docs` rather than curl — the form is generated from the model.

**Observe → why?** Now send garbage on purpose:

```bash
curl -s -X PUT localhost:8000/pokemon/pikachu -H 'content-type: application/json' \
  -d '{"display_name": "", "type1": "cardboard"}'
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

- **Length and value constraints.** `Field(min_length=1, max_length=32)` on the display
  name. Numeric fields get `ge` / `le`. Wrap it in `Annotated[str, Field(...)]`.
- **Enums for closed sets.** A `StrEnum` for Pokémon types (or brew method, or
  severity) turns a free-text field into a dropdown in `/docs` and a 422 for anything
  else. Cheapest validation win available.
- **`pattern` on the slug**, from section 4. Same mechanism as the length constraints,
  and it's what makes an unusable identifier impossible rather than merely unfortunate.

Have people add one of each to their model and re-send the garbage request. The error
list gets longer and more specific.

**Observe → why?** Put the slug pattern on the *path parameter* too
(`Annotated[str, Path(pattern=SLUG_PATTERN)]`), then try `PUT /pokemon/Pikachu` with a
capital P. You get a 422 rather than a 404. Why is that the better answer?

<details>
<summary>Answer</summary>

They're different problems and deserve different replies. 404 says "there's nothing
here, maybe try another id" — which invites a retry. 422 says "that string cannot be an
identifier in this API", so retrying is pointless until the client fixes it. Verified:
`/pokemon/Pikachu` → 422, `/pokemon/no-such-mon` → 404.
</details>

## 6. Status codes (25 min)

These map well onto CRUD, in escalating difficulty. Build the remaining endpoints
(`GET` one, `DELETE`) as an excuse to hit all three cases.

### Easy: a fixed non-200 success

Deleting should be 204 — no content, because there's nothing sensible left to return.

```python
@app.delete("/pokemon/{slug}", status_code=204)
# or, more readably
from fastapi import status
@app.delete("/pokemon/{slug}", status_code=status.HTTP_204_NO_CONTENT)
```

### Medium: errors

Just raise `HTTPException`:

- `GET /pokemon/{slug}` → 404 if it isn't there
- `DELETE /pokemon/{slug}` → 404 if it isn't there

Notice how short that list is. A name-keyed POST design would also need a 409 for
duplicate names and a 400 for path/body disagreement — both of which section 4 designed
away rather than handled. Worth pointing at explicitly: **the best error handling is an
error that can't happen.**

**Observe → why?** `DELETE` a slug that doesn't exist, *before* adding the 404. With
`del datastore[slug]` and no check, what status comes back, and what does the client
learn about what went wrong?

<details>
<summary>Answer</summary>

500. The `KeyError` escapes, FastAPI turns any unhandled exception into a generic
500, and the client is told nothing useful — it can't tell "no such item" from "your
database is on fire". Which is why the 404 is your job, not the framework's.
</details>

### Hard: the status code isn't known until runtime

Your `PUT` is an upsert, so it has to answer 201 when it created something and 200 when
it replaced something — and it can't know which until it looks. This isn't a nicety; it's
the direct consequence of the design chosen in section 4, and it's the case the decorator
can't express, since it holds one number. Take a `Response` argument and set the code on
it at request time:

```python
async def put_pokemon(slug: SlugPath, update: PokemonUpdate, response: Response) -> Pokemon:
    if slug not in datastore:
        response.status_code = status.HTTP_201_CREATED
    ...
```

Aside worth thirty seconds: RFC 9110 says a 201 should carry a `Location` header pointing
at the new resource. Here it would just repeat the request URI, so it adds nothing and we
leave it off — which is precisely the difference from the POST design, where `Location` is
the *only* way the client learns the id.

**Observe → why?** Do that, then check `/docs`. The 201 isn't documented. Why not,
and what do you have to add to fix it?

<details>
<summary>Answer</summary>

The docs are built by inspecting the code, and nothing static says 201 is possible —
it's decided by a branch at request time. Declare it yourself with
`responses={201: {"description": "..."}}` on the decorator. Good illustration of the
limit of the automatic docs: they see the signature, not the logic.
</details>

## 7. Persistence, and a taste of dependency injection (20 min)

Motivate it with the bug they've probably already hit:

**Observe → why?** PUT a few items. Now touch `main.py` — add a blank line, save.
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
injection.

Flag the payoff even though we're not collecting it today: this same seam is how you
swap the real database for a throwaway one in tests, without touching a line of app
code. That's where the follow-up workshop starts.

**Observe → why?** PUT something, then stop the server entirely and start it again.
Your data's still there. Also: `store` is a parameter like `slug` and `update` are — so
why doesn't it show up in `/docs` as a query parameter or a request body?

<details>
<summary>Answer</summary>

`Depends` marks it as something FastAPI supplies, not something the client sends, so
it's excluded from the schema. FastAPI splits your parameters into "comes from the
request" and "comes from a dependency" based on the annotation.
</details>

## 8. Wrap-up (5 min)

Everyone has a persistent CRUD API with generated docs, correct status codes, and an
identifier design they can defend. That's a good afternoon.

Then the honest bit: **we wrote no tests.** Say so out loud rather than hoping nobody
notices — three hours is three hours, and testing is the first thing on the list for the
follow-up. The good news is that section 7 already did the hard part: because the store
arrives by dependency injection, `app.dependency_overrides` lets tests swap in an
in-memory database without touching your app code. The seam is built; we just didn't use
it yet.

Anyone who wants to get ahead: [code/test_main.py](code/test_main.py) is a working suite
against the solution key. `uv add --dev pytest && uv run pytest`.

Everything else we skipped is in [next-time.md](next-time.md).
