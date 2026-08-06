# 7. Status codes

Everything you've written returns `200 OK`, including the delete you haven't built yet.
Time to fix that.

There are three levels of difficulty here, and they're worth doing in order because the
third one is where the framework runs out of magic.

You'll build the two remaining CRUD endpoints along the way: fetch-one and delete.

## Easy: a fixed non-200 success

A successful delete has nothing sensible to return. There's no resource left to describe,
so returning `{"deleted": true}` is just noise. The right answer is `204 No Content` — "it
worked, and there's deliberately no body".

When an endpoint always returns the same non-200 code, declare it on the decorator:

```python title="main.py"
@app.delete("/pokemon/{slug}", status_code=204)
async def delete_pokemon(slug: SlugPath) -> None:
    del datastore[slug]
```

Better, using the constants:

```python title="main.py" hl_lines="1 3"
from fastapi import status


@app.delete("/pokemon/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pokemon(slug: SlugPath) -> None:
    del datastore[slug]
```

`status.HTTP_204_NO_CONTENT` is just the integer `204`, spelled so the reader doesn't have
to remember. Use whichever you find clearer; the constants win on code review.

Try it, then check `/docs`: the 204 is documented, and there's no response schema — because
`-> None` says there's no body.

## Medium: errors

That delete has a bug. Try deleting something that isn't there.

!!! question "Observe → why?"
    ```bash
    curl -i -X DELETE http://localhost:8000/pokemon/no-such-mon
    ```

    What comes back? Then look at your server's terminal. Then ask: what does the *client*
    now know about what went wrong?

    ??? success "Answer"
        `500 Internal Server Error`, and a traceback in your terminal ending in
        `KeyError: 'no-such-mon'`.

        Your `del datastore[slug]` raised, the exception escaped your function, and FastAPI
        turned it into a generic 500 — which is exactly the right thing for it to do,
        because an unhandled exception genuinely means the server has a bug it didn't
        anticipate.

        And the client learns **nothing useful**. It cannot distinguish "there's no such
        Pokémon, and there never was" from "the database is on fire". Those call for
        completely different reactions: one is a normal outcome you handle, the other is a
        page-someone situation. A 500 collapses them into "something went wrong, good luck".

        Which is the point: **deciding that a missing record is a 404 is your job, not the
        framework's.** The framework can't know whether absence is an error in your domain.

Raise `HTTPException` to send a specific error:

```python title="main.py"
from fastapi import HTTPException, status


@app.delete("/pokemon/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pokemon(slug: SlugPath) -> None:
    if slug not in datastore:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Pokémon with slug {slug!r}")
    del datastore[slug]
```

`raise`, not `return` — which is nice, because it means you can bail out from deep inside a
call stack without threading error values back up through every layer.

Now build the fetch-one endpoint the same way. This is the "read a single record" half of
CRUD's R:

```python title="main.py"
@app.get("/pokemon/{slug}")
async def get_pokemon(slug: SlugPath) -> Pokemon:
    if slug not in datastore:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Pokémon with slug {slug!r}")
    return datastore[slug]
```

```bash
curl -i http://localhost:8000/pokemon/no-such-mon
```

```json
{"detail":"No Pokémon with slug 'no-such-mon'"}
```

The second argument to `HTTPException` becomes `detail` in the JSON. Put something useful
in it — "not found" is less helpful than saying what wasn't found.

!!! tip "Notice how short your error list is"
    Two error cases in the entire API, both of them 404. Contrast with what a
    name-keyed-POST design would have needed:

    - **`409 Conflict`** — someone POSTs a name that already exists. Is that an update? An
      error? A second record? You have to decide, and any answer surprises somebody.
    - **`400 Bad Request`** — the path says `pikachu` and the body says `bulbasaur`. Which
      one wins? You have to pick, document it, and test it.

    Neither of those exists here, and it's not because you handled them well. It's because
    [step 5](05-identifiers.md) arranged for them to be unrepresentable. **The best error
    handling is an error that cannot happen.**

    This is also the answer to "aren't you being a bit precious about URL design" — the
    payoff is measured in error cases you never write.

## Hard: the status code isn't known until runtime

Your PUT is an upsert. So what should it return?

- Created something that wasn't there → **201 Created**
- Replaced something that was → **200 OK**

And it cannot know which until it looks in the datastore. The decorator can't express that,
because `status_code=` holds exactly one number.

The answer is to ask FastAPI for the response object and set the code at request time:

```python title="main.py" hl_lines="2 5 6"
@app.put("/pokemon/{slug}")
async def put_pokemon(slug: SlugPath, update: PokemonUpdate, response: Response) -> Pokemon:
    # 201 if we're creating, 200 if we're replacing. We can't know which until we look,
    # so the status code gets set here rather than on the decorator.
    if slug not in datastore:
        response.status_code = status.HTTP_201_CREATED

    stored = Pokemon(
        slug=slug,
        display_name=update.display_name,
        type1=update.type1,
        type2=update.type2,
    )
    datastore[slug] = stored
    return stored
```

An argument annotated `Response` is a third kind of parameter — not path, not query, not
body. FastAPI recognises the type and hands you the outgoing response so you can modify it.
You still `return` your model as normal; you've just adjusted the envelope.

By now your imports from `fastapi` should be the full set:

```python title="main.py"
from fastapi import FastAPI, HTTPException, Path, Response, status
```

```bash
curl -s -o /dev/null -w '%{http_code}\n' -X PUT localhost:8000/pokemon/vulpix \
  -H 'content-type: application/json' -d '{"display_name":"Vulpix","type1":"fire"}'
# 201

curl -s -o /dev/null -w '%{http_code}\n' -X PUT localhost:8000/pokemon/vulpix \
  -H 'content-type: application/json' -d '{"display_name":"Vulpix","type1":"fire"}'
# 200
```

201 then 200, and `GET /pokemon` shows exactly one Vulpix. That's
[step 5's idempotency](05-identifiers.md#the-rule-youve-heard) demonstrated: the second
request changed the status code but not the world.

!!! tip "What about the `Location` header?"
    [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110#status.201) says a 201 response
    should carry a `Location` header pointing at the newly created resource.

    Here it would be `/pokemon/vulpix` — which is the URL the client just PUT to. It knows.
    Sending it back adds nothing, so it's fine to leave off.

    That's precisely the contrast with the
    [server-generated-id design](05-identifiers.md#case-b-the-client-cant-choose-it), where
    `Location` is the *only* way the client can learn where its data went. Same header, and
    whether it's essential or redundant depends entirely on who owns the identifier.

## Where the automatic docs stop

!!! question "Observe → why?"
    You just made your PUT return 201 sometimes. Go and look at `/docs`, or:

    ```bash
    curl -s localhost:8000/openapi.json | python3 -m json.tool | grep -A2 '"put"'
    ```

    The 201 is **not documented**. The PUT lists 200 and 422 and nothing else.

    Why can't FastAPI see it, when it saw everything else? And what does that tell you
    about where the automatic documentation's limits are?

    ??? success "Answer"
        Because the docs are built by **inspecting the code, not running it**. FastAPI reads
        your function signature: the parameter types, the return annotation, the decorator
        arguments. All of those are static facts available before any request arrives.

        `response.status_code = 201` is inside an `if`. It's a *runtime* decision that
        depends on the contents of your datastore. Nothing static says it can happen, so
        nothing generates documentation for it.

        Declare it yourself:

        ```python
        @app.put(
            "/pokemon/{slug}",
            responses={201: {"description": "Created a new Pokémon"}},
        )
        ```

        This is worth understanding as a general principle rather than a one-off fix.
        **The generated docs see your signature, not your logic.** Everything expressible
        in types comes free; everything decided by a branch, you declare by hand.

        Do the same for your 404s — those are `raise` statements, equally invisible:

        ```python
        @app.get(
            "/pokemon/{slug}",
            responses={404: {"description": "No Pokémon with that slug"}},
        )
        ```

## Polish, while you're in there

Two more decorator arguments worth knowing, both purely for the docs:

```python title="main.py"
@app.get("/pokemon", summary="List Pokémon, optionally filtered by type")
async def get_all_pokemon(type: Type | None = None) -> list[Pokemon]:
    ...
```

`summary=` overrides the name FastAPI derives from your function name. And a **docstring**
becomes the long description, rendered as Markdown:

```python title="main.py"
async def put_pokemon(...) -> Pokemon:
    """Create or replace -- the whole write side of the API.

    Send this twice and you get the same single Pokémon, which is exactly what PUT
    promises and exactly why we don't need a POST.
    """
```

You can also title the whole API:

```python title="main.py"
app = FastAPI(
    title="Pokédex",
    summary="A toy CRUD API, built to demonstrate rather too many FastAPI features.",
)
```

Go and add these to your own endpoints, then look at `/docs` one more time. This is the
version you'd hand to someone.

!!! question "Observe → why? (one last one)"
    Your API has no POST endpoint at all. So what happens if a client tries?

    ```bash
    curl -i -X POST localhost:8000/pokemon \
      -H 'content-type: application/json' -d '{}'
    ```

    ??? success "Answer"
        `405 Method Not Allowed`. Not a 404 — the URL `/pokemon` exists perfectly well, it
        just doesn't do that verb. The distinction is useful: 404 means "no such thing",
        405 means "right thing, wrong request".

        You didn't write that. Routing knows which verbs are registered for each path, so
        it's free.

## Where you are

You have a complete CRUD API:

| | Endpoint | Codes |
|---|---|---|
| **C**/**U** | `PUT /pokemon/{slug}` | 201, 200, 422 |
| **R** | `GET /pokemon`, `GET /pokemon/{slug}` | 200, 404, 422 |
| **D** | `DELETE /pokemon/{slug}` | 204, 404, 422 |

Documented, validated, correct status codes, and an identifier design you can defend.

[Next: what you built, and what's missing →](08-wrap-up.md){ .md-button .md-button--primary }
