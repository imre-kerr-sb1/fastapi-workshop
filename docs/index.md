# Build a CRUD API with FastAPI

By the end of this you will have written a working HTTP API: something another program can
call over the network to create, read, update and delete records. It'll have interactive
documentation you never wrote, it'll reject bad input before your code ever sees it, and
you'll be able to explain why its URLs look the way they do.

It takes about three hours at a comfortable pace.

## Who this is for

People who write Python but not web services. If you've used `requests.get()` or
`pandas.read_json()` to pull data from somewhere, you've been on the *client* side of an
API. This is the other side.

You need:

- **Python you can read.** Functions, dicts, lists, classes-you-mostly-just-use. Anything
  more exotic than that gets explained where it appears — decorators, type annotations and
  `Annotated` all get a paragraph at the point you first meet them.
- **A terminal.** And [`uv`](https://docs.astral.sh/uv/), which [step 2](02-setup.md)
  installs.

You do **not** need to know HTTP, what a status code is, what CRUD stands for, or
anything about REST. Those are the content, not the prerequisites.

## How to work through it

Each step has three kinds of thing in it:

!!! note "Do this"
    Something to type and run. These are cumulative — each step builds on the file from
    the last one.

!!! question "Observe → why?"
    Break something on purpose, look at what happens, then work out why before you open
    the answer. **These are the actual point.** Anyone can copy code off a page; the
    reason this workshop exists is the ten seconds where you predict what will happen and
    find out you were wrong.

    Answers are always there in a collapsible block. Try to guess first anyway.

!!! tip "Aside"
    Context, alternatives, and the occasional opinion. Skippable, but they're where the
    "why" lives.

Two things worth knowing before you start:

- **You pick the domain.** In [step 4](04-model-and-get.md) you'll choose what your API is
  about. Everything after that is your data, not mine. The examples use Pokémon, which is
  what the [solution key](solution-key.md) implements.
- **Type it, don't paste it.** Slower, and it's the difference between reading and
  learning. Especially the bits you don't understand yet.

## The steps

<div class="grid cards" markdown>

- **[1. What even is an API?](01-what-is-an-api.md)**

    No code. What HTTP actually is, what CRUD means, and what a framework saves you from.

- **[2. Setting up](02-setup.md)**

    `uv`, a project, and FastAPI installed.

- **[3. Hello world](03-hello-world.md)**

    Four lines that serve a URL. Then the documentation you didn't write.

- **[4. Your first model, and a GET](04-model-and-get.md)**

    Pick a domain. Describe your data as a class. Serve a list of it.

- **[5. Who owns the identifier?](05-identifiers.md)**

    No code, ten minutes, and it decides the shape of everything after it.

- **[6. Request bodies, and getting them wrong](06-request-bodies.md)**

    Accepting data, and watching FastAPI reject garbage on your behalf.

- **[7. Status codes](07-status-codes.md)**

    404, 204, and the one case where the framework can't guess for you.

- **[8. What you built, and what's missing](08-wrap-up.md)**

    An honest accounting, plus the two things to learn next.

</div>

The complete working code is in the [solution key](solution-key.md) if you get stuck or
want to compare notes. Try not to read ahead in it — the wrong-then-fixed path is most of
the value.

!!! tip "This was originally an instructor-led workshop"
    Which is why it's structured in timed steps. If you're reading it solo, ignore the
    timings and go at whatever pace you like — the "observe → why" prompts replace the
    person who would otherwise be asking you those questions out loud.
