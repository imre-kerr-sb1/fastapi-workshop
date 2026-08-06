# 8. What you built, and what's missing

## What you built

A working HTTP API. Specifically:

- **Four endpoints** covering all of CRUD, in about 120 lines including docstrings.
- **Validated input.** Bad types, missing fields, out-of-range numbers and unusable
  identifiers are all rejected before your code runs, with machine-readable errors saying
  exactly which field was wrong.
- **Correct status codes**, including one the framework couldn't have guessed.
- **Interactive documentation** you never wrote and cannot forget to update.
- **An identifier design you can defend**, which is the bit most tutorials skip.

Go back to [step 1's four pieces](01-what-is-an-api.md#an-api-is-a-function-call-over-the-network)
— verb, path, body, status code. You have now written all four yourself, deliberately, with
reasons.

The idea worth taking away isn't any particular decorator. It's this: **you wrote types, and
got behaviour.** One `StrEnum` produced a validation rule, an error message and a dropdown
in the docs. One `-> list[Pokemon]` produced serialization and a schema. That's the actual
trick, and everything else in FastAPI is a variation on it.

The second idea, which is more valuable and less about FastAPI: **the best error handling is
an error that can't happen.** Your API has no 409 and no path/body-mismatch 400, and not
because you handled them well.

## What's missing

Two things, and both are missing on purpose.

### 1. Your data disappears

Restart your server and `GET /pokemon`. Empty. It's a dict in memory.

You know where it should go — a database. You probably know more about databases than about
HTTP. So the interesting question isn't the SQL:

!!! question "Observe → why?"
    Suppose you're going to move `datastore` into SQLite. Look at your four endpoints and
    count: how many places would you have to change, and where would you put "open a
    connection, commit the transaction, close it"?

    ??? success "Answer"
        **Every endpoint**, because every one of them reaches out and grabs the global
        `datastore` itself.

        And there's nowhere good for connection handling. You could open a connection at
        module level, but then every request shares it. You could open one per endpoint,
        but that's the same four-places problem plus commit-and-close in every function,
        including on the error paths.

        The real problem isn't SQLite. It's that your endpoints **fetch** their storage
        rather than being **handed** it. That one inversion is what makes the swap hard —
        and it's the same reason your code would be awkward to test, since a test can't
        substitute anything either.

        FastAPI's answer is **dependency injection**: your endpoint declares what it needs
        as a parameter, and FastAPI produces it.

        ```python
        async def get_pokemon(slug: SlugPath, store: PokemonStore) -> Pokemon:
            ...
        ```

        Same rule as everything else in this workshop — the type annotation says what you
        want, and the framework provides it. `store` is a fourth kind of parameter, next to
        path, query and body.

The [solution key](solution-key.md) includes `storage.py`, a finished SQLite version with
that seam in it, if you want to read ahead. It's the first thing in
[where to go next](next-steps.md).

### 2. You wrote no tests

Which is a bit rich, given that the whole workshop was "send a bad request and see what
happens". That *was* testing. You just did it by hand, once, and kept none of it.

`TestClient` lets you write those same requests as a suite that runs in about a second:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_put_is_idempotent():
    assert client.put("/pokemon/vulpix", json=VULPIX).status_code == 201
    assert client.put("/pokemon/vulpix", json=VULPIX).status_code == 200
    assert len(client.get("/pokemon").json()) == 1
```

No server, no port, no second terminal — it talks to the `app` object directly.

The [solution key](solution-key.md) has a complete 16-test suite. Two of its tests are worth
reading even if you never write any yourself:

- **`test_put_is_idempotent`** — the one above. [Step 5](05-identifiers.md) *claimed*
  idempotency; this is three lines that prove it.
- **`test_slug_containing_a_slash_never_reaches_the_app`** — asserts the 404, and then
  asserts the store is still empty. It's a test for a bug that can't happen, which is how
  you stop someone from accidentally reintroducing it.

That second one is the general point: **tests document intent, not just behaviour.** A test
named after a design decision explains why the code is shaped that way, to someone who
wasn't there.

!!! tip "Neither of these is a crisis"
    Plenty of real, useful services have run on one process's memory with no tests, briefly.
    You've built something that works and that you understand, which is the harder part.

    These are just the next two things worth learning, and they're worth learning in that
    order — because the dependency-injection seam you build for the database is exactly
    what makes the tests clean.

## Try one more thing

Before you close the tab, one exercise with no instructions, which is the best kind:

**Add a `PATCH` endpoint** that updates *some* fields of a record and leaves the rest alone.
`PUT` replaces everything; `PATCH` is the partial version.

You'll need to work out how a model can have all-optional fields, and how to tell "the
client sent `null`" apart from "the client didn't mention this field" — which is a genuinely
interesting distinction and the reason `PATCH` is harder than it looks. The search term is
`exclude_unset`.

The [FastAPI docs on partial updates](https://fastapi.tiangolo.com/tutorial/body-updates/#partial-updates-with-patch)
have the answer. Try it before you look.

<div class="grid cards" markdown>

- **[Solution key →](solution-key.md)**

    The complete working code, with the reasoning in the comments.

- **[Where to go next →](next-steps.md)**

    Persistence, testing, async, auth — in the order that makes each one easy.

</div>
