# 4. Your first model, and a GET

Time to serve real data. First you have to decide what it is.

## Pick a domain

Your API is about *something*. Pick it now, and pick something you find mildly interesting
— you're going to be typing its field names for the next two hours.

**Not a pet store.** Every tutorial is a pet store.

Ideas, if nothing springs to mind:

| Domain | Fields |
|---|---|
| **Pokémon** | name, primary type, optional secondary type |
| Coffee brews | bean, method, grind size, dose, brew time |
| Incident log | title, severity, status, opened-at |
| Board games | title, min/max players, playtime, rating |
| Climbing routes | name, grade, crag, bolts, first ascent |

Pokémon is what the [solution key](solution-key.md) uses, so examples here are Pokémon. Use
your own thing — translating as you go is a feature, since it stops you from copy-pasting
your way through without reading.

**Two or three fields is plenty.** One required, one optional, and one that's from a fixed
set of options if your domain has such a thing.

!!! warning "Don't worry about identifiers yet"
    You might be wondering what the URL for a single record should look like. Good
    instinct, and [step 5](05-identifiers.md) is entirely about it. It's a more interesting
    question than it appears, so resist deciding now.

## Describe your data as a class

FastAPI wants a **model**: a class that says what fields your records have and what types
they are. This is [Pydantic](https://docs.pydantic.dev/), which came along with FastAPI.

```python title="main.py"
from pydantic import BaseModel


class Pokemon(BaseModel):
    display_name: str
    type1: str
    type2: str | None = None
```

Read that as a table definition. Three columns; `type2` may be missing.

!!! tip "New Python, one line each"
    `class Pokemon(BaseModel)`

    : A named shape for your data. Like a table's columns, but describing one row. You
      won't write any methods on it — for our purposes it's a description, not a machine.

    `display_name: str`

    : A **type annotation**. It says what kind of value belongs in this field. Plain Python
      largely ignores these at runtime; Pydantic and FastAPI absolutely do not. This is the
      workshop's central trick — you write the type once and get validation, serialization
      and documentation out of it.

    `type2: str | None = None`

    : Two things at once. `str | None` means "a string, or nothing" — the `|` reads as
      "or". `= None` gives it a default, which is what makes the field optional in a
      request. Without the default it'd be required and merely allowed to be null, which is
      a distinction that will bite someone eventually.

You now have a class. Make a couple of instances by hand, right in the file, as your
stand-in database:

```python title="main.py"
datastore = [
    Pokemon(display_name="Pikachu", type1="electric"),
    Pokemon(display_name="Skarmory", type1="steel", type2="flying"),
]
```

!!! note "Yes, it's a module-level list"
    It vanishes every time the server reloads. That's fine for now and it is
    [addressed honestly in step 8](08-wrap-up.md) rather than swept under the rug.

## Serve a list of them

Delete the hello-world endpoint. Replace it with this:

```python title="main.py"
@app.get("/pokemon")
async def get_all_pokemon() -> list[Pokemon]:
    return datastore
```

```bash
curl http://localhost:8000/pokemon
```

```json
[{"display_name":"Pikachu","type1":"electric","type2":null},
 {"display_name":"Skarmory","type1":"steel","type2":"flying"}]
```

Your Pydantic objects came back as JSON, and you wrote no serialization code. That's the
`-> list[Pokemon]` doing it.

Then look at `/docs`. Your endpoint is there, and it now has a **Schema** — the exact shape
of what it returns, with field names and types, expandable. Nobody wrote that either.

!!! question "Observe → why?"
    Delete the `-> list[Pokemon]` return annotation, leaving just
    `async def get_all_pokemon():`. Save, and reload `/docs`.

    The schema is gone. The endpoint now promises nothing more specific than "some JSON".
    Curl it — the *data* is identical.

    Put the annotation back. Then answer: why does a type hint that Python barely enforces
    at runtime end up in an HTML page?

    ??? success "Answer"
        Because FastAPI reads your function's annotations — by literally inspecting the
        function object — and uses them for two different jobs from one source:

        1. **Serializing the response**, and validating that what you returned actually
           matches what you promised.
        2. **Generating the OpenAPI schema** that `/docs` renders.

        The annotation isn't documentation *about* the code, it's an input *to* the code.
        That's the whole reason the docs can't go stale: there's no second place where the
        truth is written down.

        Worth trying if you're curious: return `[{"total": "nonsense"}]` from the annotated
        version and see what happens. FastAPI raises a server-side error rather than
        sending it — you promised `list[Pokemon]` and it holds you to it.

## Now a closed set of options

If your domain has a field that's one of a fixed set — a Pokémon type, a coffee brew
method, a severity — say so. `str` accepts `"cardboard"`. An enum doesn't.

```python title="main.py"
from enum import StrEnum


class Type(StrEnum):
    ELECTRIC = "electric"
    FIRE = "fire"
    WATER = "water"
    GRASS = "grass"
    FLYING = "flying"
    PSYCHIC = "psychic"
    STEEL = "steel"
    ICE = "ice"
```

Then use it in the model instead of `str`:

```python title="main.py" hl_lines="3 4"
class Pokemon(BaseModel):
    display_name: str
    type1: Type
    type2: Type | None = None
```

`StrEnum` is a standard-library class (Python 3.11+) whose members *are* strings, so
`Type.FIRE == "fire"` is true and JSON serialization is free.

Reload `/docs`. Those fields are now dropdowns with your eight options in them.

!!! tip "This is the cheapest validation win available"
    One class, and a whole category of bad data becomes impossible. You'll see it reject
    things in a moment.

## Filtering, i.e. a `WHERE` clause

A list endpoint that can only return everything isn't much use. Let the caller narrow it
down with a **query parameter** — the `?type=flying` part of a URL.

The trick: add an argument to your function that *isn't* in the URL path, and FastAPI makes
it a query parameter.

```python title="main.py" hl_lines="2 3 4 5"
@app.get("/pokemon")
async def get_all_pokemon(type: Type | None = None) -> list[Pokemon]:
    if type is None:
        return datastore
    return [p for p in datastore if type in (p.type1, p.type2)]
```

```bash
curl 'http://localhost:8000/pokemon?type=flying'
```

```json
[{"display_name":"Skarmory","type1":"steel","type2":"flying"}]
```

And with no parameter you still get everything, because of the `= None` default.

Pick a field of *your* domain worth filtering on and do the same. Severity, brew method,
minimum player count — whatever you'd actually want.

!!! question "Observe → why?"
    Two things to try.

    First, ask for a type that doesn't exist:

    ```bash
    curl -i 'http://localhost:8000/pokemon?type=cardboard'
    ```

    Read the whole response, not just the status line. What code came back, and where did
    that error message come from? Did your function run at all?

    Second: look at `/docs`. The parameter is documented, with a dropdown. So — how did
    FastAPI know `type` was a *query* parameter, when it's just a function argument?

    ??? success "Answer"
        **The rejection.** `422 Unprocessable Content`, with a body like:

        ```json
        {"detail":[{"type":"enum","loc":["query","type"],
                    "msg":"Input should be 'electric', 'fire', ...",
                    "input":"cardboard"}]}
        ```

        Your function never ran. Validation happens first, and the enum you declared is
        what generated both the check and the message — including `loc`, which points at
        exactly which part of the request was wrong. [Step 6](06-request-bodies.md) is
        about this in earnest.

        **How it knew.** The path string in the decorator. Anything named in `{braces}`
        there comes from the URL path; every other argument is a query parameter by
        default. You don't declare which is which — the URL pattern and the function
        signature get matched up for you.

        You'll see the path-parameter half of that rule in step 6, when the decorator
        becomes `@app.put("/pokemon/{slug}")` and the function grows a `slug` argument.

## Where you are

`main.py` should look roughly like this:

??? example "Checkpoint: main.py so far"
    ```python title="main.py"
    from enum import StrEnum

    from fastapi import FastAPI
    from pydantic import BaseModel

    app = FastAPI()


    class Type(StrEnum):
        ELECTRIC = "electric"
        FIRE = "fire"
        WATER = "water"
        GRASS = "grass"
        FLYING = "flying"
        PSYCHIC = "psychic"
        STEEL = "steel"
        ICE = "ice"


    class Pokemon(BaseModel):
        display_name: str
        type1: Type
        type2: Type | None = None


    datastore = [
        Pokemon(display_name="Pikachu", type1="electric"),
        Pokemon(display_name="Skarmory", type1="steel", type2="flying"),
    ]


    @app.get("/pokemon")
    async def get_all_pokemon(type: Type | None = None) -> list[Pokemon]:
        if type is None:
            return datastore
        return [p for p in datastore if type in (p.type1, p.type2)]
    ```

You can read your data, filtered. You cannot write any. That's next — but first, ten
minutes of thinking about URLs, because it determines what "write" even looks like.

[Next: who owns the identifier? →](05-identifiers.md){ .md-button .md-button--primary }
