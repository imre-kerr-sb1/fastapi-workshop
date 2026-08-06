# 5. Who owns the identifier?

No code in this step either. Read it properly anyway — it decides what you build in the
next two, and it's the one genuinely opinionated thing in this workshop.

## The rule you've heard

> "POST is for creating, PUT is for updating."

Nearly everyone learns this. It's wrong — or more charitably, it's a *consequence* of
something else rather than a rule in its own right.

Here's what [the HTTP spec](https://www.rfc-editor.org/rfc/rfc9110) actually says the two
verbs mean:

| | What it means | Idempotent? |
|---|---|---|
| **PUT** | "Make the resource at *this URL* equal this representation." | **Yes.** Twice is the same as once. |
| **POST** | "Here's some data. Process it according to your own rules." | **No.** Twice may do two things. |

Neither definition mentions creating or updating. PUT is about *a URL the client names*.
POST is about *handing the server a job*.

!!! tip "Idempotent, and why you care"
    An operation is idempotent if doing it twice has the same effect as doing it once.
    `d["a"] = 1` is idempotical; `list.append(1)` isn't.

    This is not a purity concern. Networks time out *after* the server has done the work
    but *before* the response gets back. When that happens the client has no idea whether
    it succeeded, and its only options are retry or give up. If your write is idempotent,
    retrying is free and safe. If it isn't, retrying might create a duplicate — and now
    you're building deduplication, request IDs, and a small distributed-systems problem.

    Idempotency is the difference between "retry it" and "write a reconciliation job".

So the useful question is not *which verb creates?* It's:

> ## Who gets to choose the identifier?

Everything follows from the answer.

## Case A: the client can choose it

Sometimes the thing you're storing already has a name that the client knows in advance.
Pokémon do. Coffee beans do. Board games do. Git repositories do — that's why GitHub URLs
are `/{owner}/{repo}` and not `/repo/838271`.

If the client knows the identifier, it knows the URL. And if it knows the URL, it can PUT
to it — whether or not anything is there yet:

```python
@app.put("/pokemon/{slug}")
async def put_pokemon(slug, update):
    ...  # creates if absent, replaces if present
```

This is called an **upsert**, and it means create and update are *the same operation*. You
need exactly one write endpoint, not two. Three things fall out of that:

**You get idempotency for free.** `PUT /pokemon/pikachu` twice gives you one Pikachu. Retry
after a timeout with no anxiety.

**There's no `409 Conflict` to handle.** A conflict is "something's already there and I
don't know what you want me to do about it". Here you said which URL you wanted and you
get it. There is no conflict to have.

**Identity can't contradict itself.** Look at where the identifier appears: in the path,
once. The request body doesn't carry it. So the classic bug — `PUT /pokemon/pikachu` with a
body saying `{"name": "bulbasaur"}` — is not a thing you have to decide about, because
there's nowhere to write it.

!!! tip "That last one is the pattern worth stealing"
    Three paragraphs up, we designed away an entire error case. Not handled it — *removed
    the possibility of it*.

    Notice this is why the model you send will be a different class from the model you get
    back: `PokemonUpdate` has no identifier field, and `Pokemon` does. You'll write both in
    [step 6](06-request-bodies.md).

### But the identifier has to survive being in a URL

If the client picks it, you have to constrain it. Not free text — a **slug**:

```python
SLUG_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"
```

Lowercase letters and digits, in hyphen-separated groups. `pikachu`, `mr-mime`,
`vulpix-alola`, `porygon-z`.

Why not just use the display name? Because display names are hostile to URLs, and it's
worth seeing exactly how:

| Name | Problem |
|---|---|
| `Mr. Mime`, `Type: Null` | Contains a space. Not legal in a URL; something has to silently encode it, and now your identifier has two spellings. |
| `Ho-Oh` vs `ho-oh` | Differ only in case. Are those one record or two? Whatever you answer, someone will assume the other. |
| `Flabébé` | Non-ASCII, and there are two different Unicode encodings of `é` that look identical and compare unequal. |
| `Porygon/Z` (a typo) | Contains a slash, which means it isn't one path segment any more. |

That last one is the interesting failure, so here's what actually happens — verified
against the working code:

`PUT /pokemon/Porygon/Z` doesn't match your route, because `/pokemon/{slug}` expects
exactly one segment after `/pokemon`. You get a **404**, and no, you can't escape your way
out of it: `%2F` doesn't help either, because the server hands your application an
already-decoded path. The slash is a slash by the time anyone can inspect it.

!!! danger "Why that's worse than a 404"
    A 404 is the *good* outcome, and you only get it because the design forbids the slash
    in the first place.

    Consider the alternative design, where clients POST and the server keys records by
    whatever name arrives in the body. Now `Porygon/Z` gets stored happily. It shows up in
    `GET /pokemon`. And it is **permanently unreachable** — no URL you can construct will
    fetch, update or delete it. You have built an API that creates records it cannot
    address, and nothing anywhere reports an error.

    Bugs that report themselves are cheap. This is the other kind.

**You still get readable URLs**, which are genuinely valuable — `/pokemon/vulpix-alola` is
better than `/pokemon/8a91f2c3`. The point isn't to give them up. It's to not let the
*mutable, human-facing label* be the identity:

- **`slug`** — identity. Constrained, stable, in the URL.
- **`display_name`** — for humans. Free text, changeable, allowed to collide.

!!! tip "\"Is Alolan Vulpix a different Pokémon?\""
    A nice illustration if your domain has anything similar. Vulpix is Fire. Alolan Vulpix
    is Ice. Same species, same dex number, different types, different records.

    Both of them want to be called "Vulpix". Under a name-as-identity design, that's a
    collision you have to resolve — and there's no correct answer, because they really are
    both called Vulpix.

    With slugs it's a non-question: `vulpix` and `vulpix-alola` are distinct identities
    with the same label. **Two things can share a name. They cannot share an identity.**
    Conflating the two is what makes it hard.

## Case B: the client can't choose it

Not every domain has a natural name, and some shouldn't let the client pick one at all:

| Domain | Why the server should own the id |
|---|---|
| Incidents, log entries, orders, events | No natural name, and two records can legitimately be identical. "The database went down" is a thing that happens twice. |
| Anything multi-tenant | Client-chosen identifiers are guessable, and they leak information. `/orders/1` tells the world you have had one order. |

Now the client *can't* know the URL before the record exists. PUT-as-upsert stops working,
because you can't name a URL you haven't been given yet.

**This is where POST earns its place.** The client POSTs to the collection, the server
invents an identifier, and the response carries a `Location` header pointing at the new
resource — because that response is the client's only chance to find out where its data
landed.

```
POST /incidents            ------>   201 Created
{"title": "Database down"}           Location: /incidents/0f8b...
                           <------   {"id": "0f8b...", "title": "Database down"}
```

And note what just happened: with server-generated identifiers, "POST creates, PUT
updates" becomes **true**. PUT can only replace something that already exists, because
that's the only case where the client knows a URL.

It's true, but not because it's a rule about verbs. It's true because the server owns the
identifier. That's the whole point of this step: the verb behaviour is downstream of the
identity decision, and if you learn the rule without the reason you'll apply it to case A
as well, where it costs you idempotency for nothing.

??? example "Optional: see the POST design running"
    The [solution key](solution-key.md) includes `main_autoid.py`, a complete
    server-generated-id API for an incident log. It's worth five minutes if case B is your
    situation.

    ```bash
    uv run fastapi dev main_autoid.py --port 8001

    curl -i -X POST localhost:8001/incidents \
      -H 'content-type: application/json' \
      -d '{"title": "Database down", "severity": "high"}'
    ```

    `-i` shows response headers, which is where `Location` lives. Things to notice:

    - **Run it twice.** Two incidents, two different ids. That's correct — the database
      going down twice is two incidents. Contrast with PUT, where twice is indistinguishable
      from once.
    - **The `Location` header is load-bearing.** Copy the path out of it and GET it; that's
      your record. Without the header the client would have to guess, or re-fetch the whole
      collection and diff it.
    - **Its PUT is replace-only** and 404s on an unknown id. That's the honest version of
      "PUT updates".

## Decide, then carry on

Pick one for your domain before continuing:

=== "Client-chosen slug (most domains)"

    Build **`PUT` only**. Create and replace are one endpoint. This is right for Pokémon,
    coffee, board games, climbing routes — anything with a name people already use.

    It's what the rest of this workshop is written for, and what the solution key does.

=== "Server-generated id (log-shaped domains)"

    Build **`POST`** to create, plus a replace-only **`PUT`**. Right for incidents, orders,
    events, anything where two records can be genuinely identical.

    The following steps still apply — your create endpoint is a POST, your 404s key off an
    id instead of a slug, and you skip the slug pattern. Use `main_autoid.py` as your
    reference.

[Next: request bodies →](06-request-bodies.md){ .md-button .md-button--primary }
