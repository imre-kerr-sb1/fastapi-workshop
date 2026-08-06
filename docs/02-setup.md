# 2. Setting up

Three commands. Budget ten minutes, most of which is downloading.

## Get `uv`

[`uv`](https://docs.astral.sh/uv/) manages Python versions, virtual environments and
dependencies. If you've used `pip` and `venv` separately, it's both, and faster.

=== "macOS / Linux"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "Windows"

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

=== "Already have it"

    ```bash
    uv --version
    ```

    Anything 0.5 or newer is fine.

## Make a project

```bash
uv init fastapi-workshop
cd fastapi-workshop
uv add "fastapi[standard]"
```

That's it. You now have a `pyproject.toml`, a pinned Python version, a lockfile, and
FastAPI installed into a virtual environment `uv` manages for you. You never activate it —
`uv run` does that.

!!! note "`uv init` leaves you a `main.py`"
    It contains a `main()` that prints a greeting. Delete the contents; you're about to
    write something else in that file. Keep the filename.

!!! tip "What did `[standard]` get me?"
    FastAPI is the framework, but it can't listen on a port by itself. `[standard]` pulls
    in the rest of what you need to actually run one:

    - **`uvicorn`** — the web server. This is the thing that opens a socket and speaks
      HTTP. FastAPI just tells it what to say.
    - **`fastapi-cli`** — the `fastapi dev` command you'll use in the next step.
    - **`httpx`** — an HTTP client, used by the test tooling.
    - **`jinja2`**, **`python-multipart`** and friends — templates and form parsing, which
      you won't need today.

    Without `[standard]` you'd have the framework and no way to serve it.

## Check it worked

```bash
uv run python -c "import fastapi; print(fastapi.__version__)"
```

A version number means you're done. Anything 0.115 or newer behaves as described here.

!!! question "Observe → why?"
    Run `ls -a`. There's a `.venv` directory you didn't ask for, and a `uv.lock` you
    didn't write. Then look at `pyproject.toml`, which lists `fastapi[standard]` and
    nothing else — but `uv.lock` is hundreds of lines.

    Why two files? What does each one answer?

    ??? success "Answer"
        `pyproject.toml` records **what you asked for**: "some version of FastAPI that
        works". `uv.lock` records **what you got**: every package in the tree, pinned to
        an exact version and hash, including things you never named like `uvicorn` and
        `pydantic`.

        You edit the first one. The second one is generated, and it's what makes the
        install reproducible on someone else's machine next year. Commit both.

## A note on where things live

Everything in this workshop happens in one file. That's deliberate — `main.py` is going to
end up around 120 lines and it will all fit on two screens, which makes it much easier to
see the whole shape of an API at once.

Splitting into routers and modules is a real thing you'll want eventually, and it's
[in the next steps](next-steps.md). Not today.

[Next: hello world →](03-hello-world.md){ .md-button .md-button--primary }
