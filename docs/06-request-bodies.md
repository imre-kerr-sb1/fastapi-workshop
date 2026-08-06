# 6. Request bodies, and getting them wrong

Now you accept data. This is the step where FastAPI's central trick pays off, and the most
interesting part of it is watching it reject things.

Written for the client-chosen-slug design from [step 5](05-identifiers.md). If you went the
server-generated-id route, everything here applies — your endpoint is a `POST` to
`/pokemon` and there's no slug pattern.

## Two models, not one

You need a second model: one for what comes **in**, one for what goes **out**.

```python title="main.py"
class PokemonUpdate(BaseModel):
    """What a client sends us. No slug: the URL already said which Pokémon."""

    display_name: str
    type1: Type
    type2: Type | None = None


class Pokemon(BaseModel):
    """What we store and send back: the client's data plus its identity."""

    slug: str
    display_name: str
    type1: Type
    type2: Type | None = None
```

The only difference is `slug`, and that difference is the whole argument from
[step 5](05-identifiers.md): identity arrives in the URL, so the body has nowhere to
contradict it.

!!! tip "This feels like duplication, and it isn't"
    Splitting input from output is a FastAPI idiom you'll meet constantly, and the reasons
    stack up fast: never accept a field the client shouldn't control, never return a field
    the client shouldn't see (`password_hash`, internal flags), and let created-at
    timestamps be server-owned.

    This is the cheapest possible first version of that: one field's difference, one
    concrete reason. You can share the common fields via inheritance later; spelling both
    out is clearer while you're learning what the split is *for*.

Your datastore also needs to change shape. It was a list; now you have keys, so make it a
dict:

```python title="main.py"
datastore: dict[str, Pokemon] = {}
```

Which means the list endpoint needs `.values()`:

```python title="main.py" hl_lines="3"
@app.get("/pokemon")
async def get_all_pokemon(type: Type | None = None) -> list[Pokemon]:
    all_pokemon = list(datastore.values())
    if type is None:
        return all_pokemon
    return [p for p in all_pokemon if type in (p.type1, p.type2)]
```

Starting empty is fine — you're about to be able to add things.

## The write endpoint

```python title="main.py"
@app.put("/pokemon/{slug}")
async def put_pokemon(slug: str, update: PokemonUpdate) -> Pokemon:
    stored = Pokemon(
        slug=slug,
        display_name=update.display_name,
        type1=update.type1,
        type2=update.type2,
    )
    datastore[slug] = stored
    return stored
```

Look at the two arguments, because they get their values from completely different places
and nothing in the signature says so:

- **`slug: str`** is a **path parameter**, because `{slug}` appears in the decorator's URL.
- **`update: PokemonUpdate`** is the **request body**, because its type is a Pydantic model.

That's the rule in full: named in the path → path parameter. A Pydantic model → the body.
Anything else → a query parameter.

By the time your function runs, the JSON body has been parsed, every field checked against
its type, and an error returned to the client if any of it was wrong. You never see a bad
request.

Try it:

```bash
curl -X PUT http://localhost:8000/pokemon/pikachu \
  -H 'content-type: application/json' \
  -d '{"display_name": "Pikachu", "type1": "electric"}'
```

```json
{"slug":"pikachu","display_name":"Pikachu","type1":"electric","type2":null}
```

Then `curl http://localhost:8000/pokemon` and there it is.

!!! tip "Use `/docs` instead of curl for this"
    Go to <http://localhost:8000/docs>, expand your PUT, hit **Try it out**. The form is
    generated from `PokemonUpdate` — with a dropdown for the enum and a pre-filled example
    body. It's genuinely faster than writing curl commands, and it's the same OpenAPI
    schema doing it.

## Now send garbage on purpose

This is the important bit of the whole workshop.

!!! question "Observe → why?"
    ```bash
    curl -i -X PUT http://localhost:8000/pokemon/pikachu \
      -H 'content-type: application/json' \
      -d '{"display_name": "", "type1": "cardboard"}'
    ```

    Read the entire response body, not just the status. Then:

    1. What status code came back, and why that one rather than `400 Bad Request`?
    2. How did the error know the *name* of the field that was wrong?
    3. Did your function run at all? How could you prove it either way?

    ??? success "Answer"
        **1.** `422 Unprocessable Content`. The distinction is real, if fine-grained: `400`
        means the request was malformed — you couldn't even parse it. Here the request was
        perfectly well-formed JSON that FastAPI understood completely; it was just *wrong*
        about your data's rules. Different problem, different code. Send genuinely broken
        JSON like `-d '{"display_name":'` and you'll get a 422 too, but with
        `"type": "json_invalid"`.

        **2.** From the model. Look at the `loc` array in the response:

        ```json
        {"detail": [
          {"type": "enum", "loc": ["body", "type1"],
           "msg": "Input should be 'electric', 'fire', ...", "input": "cardboard"}
        ]}
        ```

        `["body", "type1"]` is a *path* to the offending value — which part of the request,
        then which field. That's why it works for nested objects and lists too: you'd get
        `["body", "moves", 2, "power"]`. Machine-readable, and it's a *contract* your
        clients can rely on.

        **3.** It didn't. Stick a `print("ran!")` at the top and try again — nothing. That's
        the point worth carrying away: **validating the request body is not your job.** By
        the time your code executes, the data is the shape you asked for. You never write
        `if "display_name" not in body`.

        Also notice it reported **both** errors, not just the first. Pydantic collects them
        all, so a client can fix everything in one round trip.

## Constrain the fields

The enum already rejects `"cardboard"`. Now tighten the free-text field with `Field`:

```python title="main.py" hl_lines="4 5 6 7 8 9 10 11 12 13"
from pydantic import BaseModel, Field


class PokemonUpdate(BaseModel):
    display_name: str = Field(
        min_length=1,
        max_length=64,
        description="Shown to humans. May change, and may collide with others.",
        examples=["Vulpix"],
    )
    type1: Type = Field(description="The primary type.")
    type2: Type | None = Field(
        default=None, description="The secondary type, for dual-type Pokémon."
    )
```

`Field` attaches rules and metadata to one field. The useful ones:

| Argument | Applies to | Effect |
|---|---|---|
| `min_length` / `max_length` | strings, lists | Rejects too-short/too-long |
| `ge` / `le` / `gt` / `lt` | numbers | Rejects out-of-range |
| `pattern` | strings | Rejects anything not matching a regex |
| `default` | anything | Makes the field optional |
| `description` | anything | Shows up in `/docs` |
| `examples` | anything | Pre-fills the `/docs` form |

Add a couple to *your* model — a length limit, and a range on any numeric field (a coffee
dose isn't negative; a board game's rating is 1–10). Then re-send your garbage request and
watch the error list get longer and more specific.

Reload `/docs` too. Your descriptions are there, the constraints are documented, and the
example is pre-filled in the form. One `Field` call, three places it shows up.

## Constrain the path parameter too

[Step 5](05-identifiers.md#but-the-identifier-has-to-survive-being-in-a-url) argued that
the identifier must be URL-safe. Right now nothing enforces that — `PUT /pokemon/Pikachu`
with a capital P quietly creates a second record.

Enforce it. This needs one piece of syntax that's genuinely awkward, so here it is on its
own line with a name:

```python title="main.py"
from typing import Annotated

from fastapi import FastAPI, Path

SLUG_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"
SlugPath = Annotated[str, Path(pattern=SLUG_PATTERN, description="The Pokémon's slug.")]
```

Then use it in place of `str`:

```python title="main.py" hl_lines="2"
@app.put("/pokemon/{slug}")
async def put_pokemon(slug: SlugPath, update: PokemonUpdate) -> Pokemon:
    ...
```

!!! tip "`Annotated`, explained once"
    `Annotated[str, X]` means **"a `str`, plus this extra information `X`"**. Python's type
    system ignores `X` entirely; tools that care about it — here, FastAPI — read it.

    So `Annotated[str, Path(pattern=...)]` is "a string, and by the way it comes from the
    path and must match this pattern". Naming it `SlugPath` means you write the ugly part
    once and use a readable name everywhere else.

    You may wonder why this isn't `slug: str = Path(pattern=...)`, matching the `Field`
    style above. Because a Python argument with a default can't come before one without —
    and `update: PokemonUpdate` has no default. `Annotated` sidesteps that entirely, which
    is why modern FastAPI code prefers it. It's the only place in this workshop you need
    it.

Now the bad identifiers are impossible rather than merely unwise:

!!! question "Observe → why?"
    Four requests. Predict each status code before you run it.

    ```bash
    # a capital letter
    curl -s -o /dev/null -w '%{http_code}\n' -X PUT localhost:8000/pokemon/Pikachu \
      -H 'content-type: application/json' -d '{"display_name":"Pikachu","type1":"electric"}'

    # a space
    curl -s -o /dev/null -w '%{http_code}\n' -X PUT 'localhost:8000/pokemon/mr%20mime' \
      -H 'content-type: application/json' -d '{"display_name":"Mr. Mime","type1":"psychic"}'

    # a slash
    curl -s -o /dev/null -w '%{http_code}\n' -X PUT localhost:8000/pokemon/Porygon/Z \
      -H 'content-type: application/json' -d '{"display_name":"Porygon-Z","type1":"psychic"}'

    # a slash, escaped
    curl -s -o /dev/null -w '%{http_code}\n' -X PUT 'localhost:8000/pokemon/Porygon%2FZ' \
      -H 'content-type: application/json' -d '{"display_name":"Porygon-Z","type1":"psychic"}'
    ```

    The first two behave one way and the last two behave differently. Why? And then the
    more interesting question: `GET /pokemon` afterwards — is it empty?

    ??? success "Answer"
        `422`, `422`, `404`, `404`.

        **The first two are validation failures.** The request reached your route, the
        `slug` was extracted, and the pattern rejected it. `loc` is `["path", "slug"]` —
        note it says `path`, not `body`, which is how a client can tell which part of the
        request to fix.

        **The last two never reach your route at all.** `/pokemon/Porygon/Z` has an extra
        path segment, and `/pokemon/{slug}` matches exactly one. No route matches, so it's a
        routing failure — 404 — and it happens *before* validation, which is why you get a
        different code.

        And `%2F` doesn't rescue it, because by the time your application sees the path it
        has already been percent-decoded. The escape works at the transport layer and is
        gone by the time routing happens. You cannot put a slash inside a single path
        segment. Ever.

        **`GET /pokemon` is empty.** That's the part that matters. Every one of those four
        requests was rejected without writing anything, so there's no record in your store
        that you can't address. Compare with the [failure mode from
        step 5](05-identifiers.md#but-the-identifier-has-to-survive-being-in-a-url), where
        the unaddressable record gets stored happily and nothing complains.

Add `SlugPath` to your `Pokemon` output model's `slug` field too — as a plain `Field(pattern=...)`
this time, since it's not a path parameter there:

```python title="main.py"
class Pokemon(BaseModel):
    slug: str = Field(pattern=SLUG_PATTERN, examples=["vulpix-alola"])
    ...
```

Belt and braces: it documents the shape in `/docs`, and it means a bug elsewhere in your
code can't sneak a bad slug into the store either.

!!! question "Observe → why? (the design question)"
    `PUT /pokemon/Pikachu` gives 422. `GET /pokemon/no-such-mon` will give 404 once you
    build it in the next step. Both are "there's nothing at that URL".

    Why is 422 the better answer for the first one?

    ??? success "Answer"
        Because they're different problems and a client should react differently.

        **404** says "nothing is here right now" — which is a fact about the *state* of the
        server, and it invites a retry. Maybe someone will create it. Maybe you should
        create it. Try again later and it might work.

        **422** says "that string cannot be an identifier in this API" — a fact about the
        *rules*, which won't change. Retrying is pointless until the client fixes its
        request. And the response body says exactly what the rule was.

        One of those is worth a retry loop and the other is worth a bug report. Telling a
        client which is which is most of what status codes are for.

## Where you are

You can create and replace records, with validated input, documented in `/docs`. Every
endpoint returns 200.

That last part is wrong, and it's the next step.

[Next: status codes →](07-status-codes.md){ .md-button .md-button--primary }
