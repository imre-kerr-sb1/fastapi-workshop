# 3. Hello world

Now you serve a URL.

## Eight lines

Replace everything in `main.py` with this:

```python title="main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
```

Then:

```bash
uv run fastapi dev
```

You'll get something like:

```
 ⚡️ Starting FastAPI in development mode

 🐍 Using import string: main:app (auto-discovered)

 🌐 Server started at http://127.0.0.1:8000
    Documentation at http://127.0.0.1:8000/docs

INFO:     Will watch for changes in these directories: ['/your/path']
INFO:     Application startup complete.
```

Leave it running. Open a **second terminal** for everything below — you'll need the first
one to keep serving.

```bash
curl http://localhost:8000/
```

```json
{"message":"Hello World"}
```

That's an API. A program asked a URL a question and got data back.

## Reading those eight lines

Three things there are probably new, so here they are one at a time.

`app = FastAPI()`

: Your application object. It's a registry: every URL you define gets attached to it, and
  the web server asks it what to do with incoming requests.

`@app.get("/")`

: A **decorator** — a line starting with `@` directly above a function definition. It
  takes the function and does something with it. This one registers the function with
  `app`, saying: *when someone sends a GET to `/`, call this.*

    You don't call `root()` yourself, ever. FastAPI calls it for you when a matching
    request arrives. That inversion is the main mental shift in web programming: you write
    functions and hand them over, rather than calling them.

`async def`

: For now, a wart you can ignore. It matters when your function needs to wait for
  something slow (another API, a database) so the server can handle other requests
  meanwhile. Nothing in this workshop waits for anything, so `def` would work identically
  — but `async def` is what you'll see in every FastAPI example, so let's stay
  recognisable. [Next steps](next-steps.md) has the real story.

The return value is a dict, and it came back as JSON. FastAPI serialized it for you — that's
item 8 from [the plumbing list](01-what-is-an-api.md#what-does-a-framework-do-for-you).

## The part that sells the framework

With the server still running, open <http://localhost:8000/docs> in a browser.

You get a full interactive API browser. Your endpoint is listed. You can expand it, hit
**Try it out**, **Execute**, and see the response — no curl needed.

**Nobody wrote that page.** It is generated from your code, and it will keep being
generated from your code for the rest of this workshop. Every step from here adds something
and then looks at `/docs` to see what changed.

Now look at the thing behind it:

```bash
curl http://localhost:8000/openapi.json
```

```json
{"openapi":"3.1.0","info":{"title":"FastAPI","version":"0.1.0"},
 "paths":{"/":{"get":{"summary":"Root","operationId":"root__get", ...
```

This is an [OpenAPI](https://www.openapis.org/) document — a standard, machine-readable
description of your API. `/docs` is just a viewer for it. Since it's a standard, other
tools eat it too: client library generators, API gateways, test tools, Postman.

!!! tip "Notice what it got for free"
    `"summary": "Root"` came from your function *name*. FastAPI is already scraping
    everything it can from the code. Add a docstring to `root()` and reload the page — it
    becomes the endpoint's description.

    This is worth internalising early: **the docs are a mirror of your code**. When they
    look wrong or thin, it's because the code didn't say enough.

## Dev mode

!!! question "Observe → why?"
    Change `"Hello World"` to something else. Save the file. Don't touch the terminal
    running the server. Now curl again:

    ```bash
    curl http://localhost:8000/
    ```

    It changed. Two questions:

    1. What is `fastapi dev` doing that made that work?
    2. Try reaching your server from another device on your network — your phone, a
       colleague's laptop — using your machine's IP instead of `localhost`. It won't work.
       Why not, and is that a bug?

    ??? success "Answer"
        **1.** It's watching your files and restarting the server whenever one changes.
        You can see it in the startup output: `Will watch for changes in these
        directories`. Look at your server terminal after saving and you'll see it reload.

        **2.** Dev mode binds only to `127.0.0.1` — the loopback address, reachable only
        from your own machine. That's a deliberate safety default, not a bug: a
        development server has debugging conveniences you don't want exposed, and you
        haven't thought about security yet because you're eight lines in.

        Production is `fastapi run`, which binds `0.0.0.0` (all interfaces) and does not
        reload. Those are the two differences, and both make sense in both directions: you
        want reloading while writing and not while serving; you want narrow binding while
        writing and wide binding while serving.

!!! tip "Port already in use?"
    ```bash
    uv run fastapi dev --port 8001
    ```
    Then adjust the URLs below accordingly.

## Where you are

You have a running web server that answers one URL with one hardcoded message, plus
generated documentation. Next you'll give it actual data to serve.

[Next: your first model →](04-model-and-get.md){ .md-button .md-button--primary }
