# Solution key

The complete working code. Four files, all runnable.

!!! warning "Read this after trying, not instead of trying"
    The value of this workshop is in the "observe → why?" prompts — predicting what will
    happen, being wrong, and finding out why. Reading finished code skips all of that and
    feels like learning.

    Use this to get unstuck, or to compare against once you're done.

These live in [`code/`](https://github.com/imre-kerr-sb1/fastapi-workshop/tree/main/code)
in the repository, and everything below is included from the real files — so it can't drift
out of sync with what's tested.

| File | What it is |
|---|---|
| `main.py` | The finished API. What [steps 3–7](03-hello-world.md) build. |
| `main_autoid.py` | The other design: server-generated ids and POST. From [step 5](05-identifiers.md). |
| `test_main.py` | 16 tests against `main.py`. [Step 8](08-wrap-up.md) explains why they're not in the workshop. |
| `storage.py` | SQLite persistence with a dependency-injection seam. [Next steps](next-steps.md). |

Run any of them:

```bash
uv run fastapi dev main.py
uv run fastapi dev main_autoid.py --port 8001
uv add --dev pytest && uv run pytest
```

## `main.py`

The API from steps 3–7. Note what it deliberately doesn't have: **no POST**, because
identity is a client-chosen slug and `PUT` covers both create and replace.

It's also written *down* a bit on purpose — no model inheritance, no walrus operator, no
`**kwargs` unpacking, and `Annotated` appears exactly once. Idiomatic FastAPI is denser
than this; that's fine to grow into later.

```python title="main.py"
--8<-- "main.py"
```

## `main_autoid.py`

The [case B design](05-identifiers.md#case-b-the-client-cant-choose-it) — an incident log
where the server owns the identifier. Worth reading side by side with `main.py`; the
differences are all consequences of that one decision:

- There's a `POST`, because the client can't name a URL that doesn't exist yet.
- It sets a `Location` header, because that response is the client's only way to learn the
  id.
- Its `PUT` is **replace-only** and 404s on an unknown id. This is the one arrangement
  where "POST creates, PUT updates" is genuinely true.

```python title="main_autoid.py"
--8<-- "main_autoid.py"
```

## `test_main.py`

Testing is [cut from the workshop](08-wrap-up.md#2-you-wrote-no-tests) and leads the
[follow-up](next-steps.md). This suite passes against `main.py` as written.

The three worth reading first:

- **`test_put_is_idempotent`** — the property [step 5](05-identifiers.md) claimed, in three
  lines.
- **`test_slug_containing_a_slash_never_reaches_the_app`** — asserts the 404 *and* that
  nothing was written. A test for a bug that can't happen, so nobody reintroduces it.
- **`test_two_forms_may_share_a_display_name`** — Alolan Vulpix. Same label, different
  identity, and no 409 to fight.

```python title="test_main.py"
--8<-- "test_main.py"
```

## `storage.py`

Not used by anything in the workshop — this is the persistence layer that
[step 8](08-wrap-up.md#1-your-data-disappears) points at and the
[follow-up](next-steps.md#1-persistence-and-dependency-injection) builds on.

Two things to notice if you read it now:

- **`store_dependency(Pokemon)`** returns a function, and that function is what FastAPI
  calls per request. That's the dependency-injection seam.
- **The `yield`** splits it in two: everything before produces the store, everything after
  runs once your endpoint is done. That's where commit-or-rollback lives, and it's why the
  transaction is correct even when an endpoint raises.

It uses generics (`Store[Pokemon]`), which nothing else here does. Don't be put off — the
idea is small even where the syntax isn't.

```python title="storage.py"
--8<-- "storage.py"
```
