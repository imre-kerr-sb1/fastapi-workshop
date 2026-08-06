# 1. What even is an API?

No code in this step. It's all groundwork, and skipping it is a false economy: everything
in the next seven steps is one of the four pieces introduced here.

## An API is a function call over the network

Start from something you've done. A web page is a URL that returns HTML for a human to
look at. An API is a URL that returns **data for a program to use**.

That's genuinely the whole idea. Here's the entire mechanism:

```
  REQUEST                              RESPONSE
  GET /pokemon/pikachu       ------>   200 OK
  (verb + path + headers)              {"slug": "pikachu", "type1": "electric"}
                             <------   (status code + headers + body)
```

A client sends a request. A server sends back a response. Every single thing in this
workshop is one of four pieces of that exchange:

| Piece | What it is | The function-call analogy |
|---|---|---|
| **Verb** | What you want done | The function name |
| **Path** | What you want it done *to* | The argument |
| **Body** | Data you're sending along, if any | More arguments |
| **Status code** | Whether it worked | Return value, or an exception |

### Verbs

There are more, but four cover everything here:

| Verb | Means | Rough Python equivalent |
|---|---|---|
| `GET` | Give me this | `x = d["key"]` |
| `PUT` | Make this thing be this value | `d["key"] = value` |
| `POST` | Here's some data, deal with it | `list.append(value)` |
| `DELETE` | Remove this | `del d["key"]` |

That `PUT` vs `POST` distinction looks obvious and is the single most commonly misunderstood
thing in HTTP. [Step 5](05-identifiers.md) is entirely about it.

### Status codes

Three digits, and the first one tells you almost everything:

| Range | Means | Examples you'll write |
|---|---|---|
| **2xx** | Fine | `200 OK`, `201 Created`, `204 No Content` |
| **4xx** | *You* messed up | `404 Not Found`, `422 Unprocessable Content` |
| **5xx** | *I* messed up | `500 Internal Server Error` |

The 4xx/5xx split matters more than it looks: it tells a client whether retrying could
possibly help. [Step 7](07-status-codes.md) makes all of these concrete.

!!! tip "Two framings, if you come from data work"
    **An API is a `SELECT` you can't write yourself.** You want someone else's data. They
    aren't going to give you database access. So they give you a URL per question instead,
    and the URL is the query.

    **You've already used plenty of APIs.** Every `requests.get(...)` in a notebook, every
    `pandas.read_json("https://...")`. So here's the question worth sitting with for a
    second: *what is on the other end of that call?*

    Somebody's function. In three hours it'll be yours.

## CRUD

!!! note "Let's not get into REST"
    You will meet the word REST constantly, usually applied to any API at all. It's a
    real thing with a real definition, and arguing about what qualifies is a genuine
    industry pastime that you don't need in order to build a working API.

    We're doing **CRUD over HTTP**. That's a smaller, more useful idea, and it's what
    most things called "REST APIs" actually are.

CRUD is four things you can do to a record. You have done all four for years — just to a
database, rather than over a network:

| | Operation | SQL | HTTP verb | In the API you're about to write |
|---|---|---|---|---|
| **C** | Create | `INSERT` | `PUT` or `POST` | `PUT /pokemon/pikachu` |
| **R** | Read | `SELECT` | `GET` | `GET /pokemon/pikachu`, `GET /pokemon` |
| **U** | Update | `UPDATE` | `PUT` | `PUT /pokemon/pikachu` |
| **D** | Delete | `DELETE` | `DELETE` | `DELETE /pokemon/pikachu` |

If the SQL column makes sense to you, you already understand CRUD. That's the whole
acronym. It's in every job ad and half of all documentation, and it means "the four
obvious things".

Two details in that table to file away, because both come back later:

- **Read comes in two flavours.** Fetch one record, or fetch a list. Different URLs,
  different return types — `/pokemon/pikachu` vs `/pokemon`. You'll build the list one in
  [step 4](04-model-and-get.md) and the single-record one in [step 7](07-status-codes.md).
- **Create and Update are the same row.** Look again: `PUT /pokemon/pikachu` appears
  twice. That's not sloppiness, it's the design this workshop argues for, and
  [step 5](05-identifiers.md) is where it gets argued.

## What does a framework do for you?

Suppose you had to serve `GET /pokemon/pikachu` with no framework at all. Just a socket,
and bytes arriving on it. Your to-do list:

1. Accept a TCP connection, read bytes until the headers end
2. Parse the request line — `GET /pokemon/pikachu HTTP/1.1`
3. Match that path against your routes, and pull `pikachu` out of it
4. Percent-decode it, and decide what to do about the strange cases
5. Parse the JSON body, if there is one
6. **Check the fields exist, have the right types, and are in range**
7. **Produce a sensible error if they don't**
8. Serialize your Python objects back to JSON
9. Write the status line, the headers, and the body, in that order, with correct lengths
10. Do all of it again, concurrently, without falling over

Ten items, and **only two of them are your problem** — the bold ones, and even those are
only your problem because they're about *your* data.

A web framework does 1–5 and 8–10. FastAPI's specific pitch is that it does 6 and 7 as
well, generated from your type annotations.

The one-line version, which will be true of everything you write today:

> **You write the function. The framework does the plumbing.**

## FastAPI, specifically

Three claims. You'll have seen all of them in action within about twenty minutes.

**1. You write ordinary Python functions.** A decorator above the function says which URL
it answers. That's it. There's no framework-shaped class hierarchy to inherit from, no
config file mapping URLs to handlers.

```python
@app.get("/pokemon")
async def list_pokemon() -> list[Pokemon]:
    return everything
```

**2. Type annotations do real work.** The same `display_name: str` that gives you editor
autocomplete is what FastAPI uses to validate incoming requests and reject bad data
*before your function is called*. You write the type once and get parsing, validation and
error messages from it. (This is [Pydantic](https://docs.pydantic.dev/) underneath, which
you may already have met elsewhere.)

**3. The documentation writes itself.** Because those types are machine-readable, FastAPI
generates an interactive API browser at `/docs`. Nobody maintains it, so it cannot go
stale. This is the thread running through the whole workshop: every time you add
something, look at `/docs` and see what changed.

!!! tip "Why the docs are the throughline"
    It's the fastest feedback loop available. You don't have to trust that your annotation
    did something — you can look at a rendered page and see it. And when the docs look
    wrong, that's real information: it means the code says something you didn't mean.

Enough talking.

[Next: setting up →](02-setup.md){ .md-button .md-button--primary }
