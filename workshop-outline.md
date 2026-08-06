# Workshop Outline

Time: 3 hours, with breaks. **Read the reality check below before committing to that.**

## Audience

Data people, not backend developers. Plan for:

- **Fewer than half know what CRUD stands for.** It gets a section, not an aside.
- **Some have a tenuous grasp of Python.** Decorators, type annotations and classes-with-
  fields all need explaining at the moment they first appear — see "Explaining Python
  inline" below.
- **HTTP is not assumed.** Verbs, status codes, request/response are all new.

The solution keys are written down to this: no generics, no `Depends`, no walrus, no
inheritance between models, and `Annotated` appears exactly once with a comment on it.

Format is "do something, observe what happens, answer why" wherever possible. Every
building section has at least one **Observe → why?** prompt. Those are the bit that
matters; the typing is just how we get there.

Solution key lives in [code/](code/) — `main.py` is the finished API, `main_autoid.py` is
the presenter's file for the optional demo in section 5. `test_main.py` and `storage.py`
belong to the follow-up; see [next-time.md](next-time.md).

**Participant handbook:** [docs/](docs/) is the same material written for someone working
through it alone — one page per section, every "observe → why" with its answer in a
collapsible block. Hand it out as the take-home, and raid it for anything this outline is
too terse about. `uvx zensical serve` to read it.

## Reality check on the timeline

**This does not fit in 3 hours, and previous versions of this outline were lying about
it.** Honest estimates for *this* audience, having cut persistence and DI entirely:

| # | Section | Time | Running total |
|---|---------|------|---------------|
| 1 | What even is an API? | 30 min | 0:30 |
| 2 | Initial setup | 20 min | 0:50 |
| 3 | Hello world | 20 min | 1:10 |
| — | **Break** | 10 min | 1:20 |
| 4 | Your first model + a GET | 30 min | 1:50 |
| 5 | POST, PUT, and who owns the identifier | 10 min | 2:00 |
| 6 | Request bodies, and getting them wrong | 30 min | 2:30 |
| — | **Break** | 10 min | 2:40 |
| 7 | Status codes | 25 min | 3:05 |
| 8 | Wrap-up | 10 min | 3:15 |

**3:15, with no slack.** That's the optimistic read: it assumes setup goes smoothly for
everyone, nobody's `uv` is broken, and no one needs a second explanation of what a
decorator is. For this audience, neither assumption is safe. Realistic worst case is
closer to 3:45.

Persistence and dependency injection are **already cut** to get to this number — they were
25 minutes and by far the least audience-appropriate material in the workshop (`TypeVar`,
`Generic[M]`, `yield`-based dependencies, `Annotated[Store[Pokemon], Depends(...)]`). The
workshop now ends with data in a dict that vanishes on reload, which section 8 turns into
an honest closing note rather than pretending it isn't there.

### So pick a lever, in advance

1. **Ask for 3.5 hours.** Cheapest fix and the one I'd take. You need 3:15 of content;
   asking for 3:30 gives you 15 minutes of real slack.
2. **Cut section 5** (the POST/PUT identity discussion, 10 min) **and section 7's "hard"
   case** (10 min). Lands at ~2:55 in a 3-hour slot. Costs you the workshop's one
   genuinely opinionated idea — worth keeping if you can.
3. **Split into two 2-hour sessions.** Best for the audience, most work for you, and the
   follow-up already exists in [next-time.md](next-time.md).
4. **Pre-do the setup.** If Coder workspaces can ship with the repo scaffolded and
   `uv sync` already run, section 2 drops from 20 minutes to about 5. This is the single
   highest-leverage thing you can do, and it's entirely front-loaded work.

Do **not** plan to absorb the overrun live — with this audience, the thing that gets cut
under time pressure is explanation, which is the whole point of the day.

### If you're running behind anyway

Compress in this order: section 7's "hard" case (the dynamic 201/200) → section 5 →
section 4's filtering exercise. Protect sections 1 and 6: the concepts intro is why this
audience can follow anything at all, and request bodies plus the 422 is the core of
FastAPI's pitch.

### Explaining Python inline

No separate primer — explain each thing where it first appears, and keep it to a sentence:

| Thing | First appears | The one-sentence version |
|---|---|---|
| Decorator | §3, `@app.get("/")` | "The line above a function that says *when* to run it: when someone GETs this URL." |
| Type annotation | §4, `display_name: str` | "A note saying what kind of value goes here. Python mostly ignores it; FastAPI very much doesn't." |
| Class with fields | §4, `class Pokemon(BaseModel)` | "A named shape for your data — like a table's columns, but for one row." |
| `None` / optional | §4, `Type \| None` | "This field may be missing, and that's allowed." |
| `Annotated` | §6, `SlugPath` | "A type plus extra instructions. Ugly, unavoidable, and you only need it once." |

---

## 1. What even is an API? (30 min)

**Talking and drawing. No laptops open yet** — say that out loud, or half the room will
be fighting `uv` while you explain what HTTP is.

Four beats, in this order. Each one answers "why should I care" before it explains "how".

### An HTTP API is a function call over the network (8 min)

Start where the audience already lives: they have all called a function, and most have
opened a URL.

> A web page is a URL that returns HTML for a human to look at. An API is a URL that
> returns data for a *program* to use.

That's genuinely the whole idea. Draw it on the board, request on the left, response on
the right:

```
  REQUEST                              RESPONSE
  GET /pokemon/pikachu       ------>   200 OK
  (verb + path + headers)              {"slug": "pikachu", "type1": "electric"}
                             <------   (status code + headers + body)
```

Four things worth naming, because everything later is one of them:

| Piece | What it is | Analogy |
|---|---|---|
| **Verb** | What you want done | The function name |
| **Path** | What you want it done to | The argument |
| **Body** | The data you're sending, if any | More arguments |
| **Status code** | Did it work | Return value vs exception |

Verbs, the only four we need today: **GET** (fetch), **PUT** (put this here), **POST**
(here, deal with this), **DELETE** (guess). Status codes by first digit is enough for
now: **2xx** fine, **4xx** you messed up, **5xx** I messed up. Section 7 gets specific.

Two framings that land well with data people, use whichever fits the room:

- **It's a SELECT you can't write yourself.** You want someone else's data, they aren't
  giving you database access, so they give you a URL per question instead.
- **You have already consumed an API.** `pandas.read_json("https://...")` was an API
  call. `requests.get(...)` in that one notebook was an API call. Today we're writing the
  other side of that.

**Ask the room** (this is the actual point of the section): *what's on the other end when
you call `requests.get`?* Somebody's function. Today you write the function.

### CRUD (7 min)

> **Let's not get into REST.** If someone says the word, "it's a longer argument than
> we have time for, and you don't need it to build this" is a complete answer. We are
> doing CRUD over HTTP, and that is enough for a working API.

Four things you can do to a record. They have names because you'll see the acronym in
every job ad and half the documentation you read:

| | Operation | SQL | HTTP | Our API |
|---|---|---|---|---|
| **C** | Create | `INSERT` | PUT / POST | `PUT /pokemon/pikachu` |
| **R** | Read | `SELECT` | GET | `GET /pokemon/pikachu`, `GET /pokemon` |
| **U** | Update | `UPDATE` | PUT | `PUT /pokemon/pikachu` |
| **D** | Delete | `DELETE` | DELETE | `DELETE /pokemon/pikachu` |

The SQL column is why this audience gets CRUD for free — they've done all four for
years, just not over a network.

Two notes to plant here, both cashed in later:

- **Read comes in two flavours.** One record, or a list of them. Different URLs,
  different return types. That's why section 4 builds a list endpoint and section 7 adds
  the single-record one.
- **Create and Update are the same row in that table.** Yes, on purpose. That's section
  5, and it's the one genuinely opinionated thing in the workshop.

### What does a framework do for you? (8 min)

Do this as a demo of misery rather than a list. Ask: *suppose you had to serve
`GET /pokemon/pikachu` yourself, from a raw socket. What do you have to do?*

Take answers, then fill in the rest — the point is that the list is long and none of it
is your actual problem:

1. Accept a TCP connection, read bytes until the headers end
2. Parse the request line, `GET /pokemon/pikachu HTTP/1.1`
3. Match that path against your routes, and pull `pikachu` out of it
4. Percent-decode it, and decide what to do with the weird cases
5. Parse the JSON body, if there is one
6. Check the fields exist, have the right types, are in range
7. Produce a sane error if they don't
8. Serialize your Python objects back to JSON
9. Write status line, headers, body, in the right order, with the right lengths
10. Do it all again, concurrently, without falling over

**A framework does 1–5 and 8–10 so you can write 6, 7, and the business logic.** And
FastAPI's pitch is that it does 6 and 7 as well, from your type annotations.

Land it with the thing you'll say all afternoon: **you write the function; the framework
does the plumbing.**

### FastAPI, specifically (5 min)

Why this one, in three claims. They'll see all three before the break:

1. **You write ordinary Python functions.** A decorator says which URL, annotations say
   what goes in and out. There's no framework-shaped class hierarchy to learn.
2. **Type annotations do real work.** The same `display_name: str` that your editor uses
   for autocomplete is what FastAPI uses to validate the request and reject bad data
   before your code runs. Write the type once, get validation free. (Pydantic underneath,
   which some of the room may know from elsewhere.)
3. **The documentation writes itself.** Because the types are machine-readable, FastAPI
   generates an interactive API browser at `/docs`. Nobody maintains it, so it can't go
   stale. This is the thread running through the whole workshop: every time we add
   something, we look at `/docs` and see what changed.

Then stop talking and open the laptops.

---

## 2. Initial setup (20 min)

1. Everyone creates a repo (https://github.com/new)
2. Open it in Coder
3. `uv init && uv add "fastapi[standard]"`

Housekeeping while `uv` runs: everything is in ephemeral, reproducible Coder
workspaces, so "works on my machine" shouldn't come up. If something breaks for one
person it should break for everyone.

## 3. Hello world (20 min)

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

## 4. Your first model, and a GET (30 min)

Everyone picks something to build a CRUD API for. **Not a pet store.** Ideas, but
pick your own if you have one:

- Pokémon (name, primary type, optional secondary type) ← what the solution key uses
- Coffee brews (bean, method, grind, dose, brew time)
- Incident log (title, severity, status, opened-at)
- Board game collection (title, min/max players, playtime, rating)

Just pick the domain and the fields for now. **Don't worry about identifiers yet** —
that's section 5, and it's a more interesting question than it looks.

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

### Then: filtering, i.e. a WHERE clause (10 min)

The list endpoint should let the caller narrow it down. Add a **query parameter** — the
`?type=fire` part of a URL — by giving the function an argument that isn't in the path:

```python
@app.get("/pokemon")
async def get_all_pokemon(type: Type | None = None) -> list[Pokemon]:
    if type is None:
        return datastore
    return [p for p in datastore if type in (p.type1, p.type2)]
```

(`datastore` is still the list from a moment ago. It becomes a dict in section 6, once
we have keys to put things under, and then this needs a `.values()`.)

Everyone picks one field of their own domain worth filtering on. Default `None` means
optional, so `GET /pokemon` keeps working.

**Observe → why?** Look at `/docs` — the parameter is there, with a dropdown if you used
an enum. Now: how did FastAPI know `type` was a query parameter and `slug` will be a path
one, given both are just function arguments?

<details>
<summary>Answer</summary>

The path string in the decorator. Anything named in `{braces}` there comes from the path;
anything left over is a query parameter. Nothing to declare — the URL pattern and the
signature are matched up for you.
</details>

**First cut if you're short on time.** This is the workshop's most droppable ten minutes:
query parameters are the one thing here people can pick up from the docs alone.

## 5. POST, PUT, and who owns the identifier (10 min)

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

## 6. Request bodies, and what happens when they're wrong (30 min)

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
- **`pattern` on the slug**, from section 5. Same mechanism as the length constraints,
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

## 7. Status codes (25 min)

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
duplicate names and a 400 for path/body disagreement — both of which section 5 designed
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
the direct consequence of the design chosen in section 5, and it's the case the decorator
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

## 8. Wrap-up (10 min)

Everyone has a working CRUD API with generated docs, correct status codes, and an
identifier design they can defend. Recap against section 1's four pieces — verb, path,
body, status code — because they've now written all four themselves.

Then the honest bit, said out loud rather than hoped past. **Two things are missing, and
both are missing on purpose.**

1. **Your data vanishes when the server reloads.** It's a dict in memory. Ask the room
   where it *should* go — they'll say a database, and they're right, and they know more
   about databases than about HTTP. The interesting part isn't the SQL, it's the seam:
   right now every endpoint reaches for a global, which is the thing that makes swapping
   in a real database annoying. FastAPI's answer is dependency injection — the store gets
   handed to your function instead of being fetched by it. That's the follow-up's main
   event, and [code/storage.py](code/storage.py) is the finished version if you want to
   peek.
2. **We wrote no tests.** Which is a bit rich given the whole afternoon was "send a bad
   request and see what happens" — that *was* testing, just by hand. `TestClient` lets
   you write those same requests as a suite that runs in a second.
   [code/test_main.py](code/test_main.py) is a working one against the solution key:
   `uv add --dev pytest && uv run pytest`. Read
   `test_slug_containing_a_slash_never_reaches_the_app` if you liked section 5.

Neither of these is a gap you can't ship without; plenty of real services are one dict
and no tests, briefly. But they're the next two things worth learning, and they lead
[next-time.md](next-time.md) in that order.

Everything else we skipped is in there too.
