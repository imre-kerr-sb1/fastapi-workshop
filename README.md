# fastapi-workshop

A loose collection of notes, code snippets and experiments that will hopefully coalesce into a useful workshop sometime before
September 17.

## Principles

Everything is done in ephemeral, reproducible workspaces in Coder, so there should be very little "works on my machine".

Tasks should be (at least sometimes) more interesting than just "do what the slides say".

- Do something, observe what happens, ANSWER WHY <- The important bit
- Goal state without instructions. Requires people to read docs so I dunno...

Just following the docs is fine but kinda boring.

## Auto docs
A large part of (at least what I find) is cool about FastAPI is the automatic OpenAPI docs. So for a lot of what we do, we should take a look at how it affects the docs.

Input/output data shapes, status codes, default values, descriptions, examples...

Sometimes we can use the docs as motivation. Response type isn't defined? Let's see how to define it!

## Layout
- [workshop-outline.md](workshop-outline.md) — the run sheet for the day.
- [next-time.md](next-time.md) — the follow-up workshop. Testing leads it.
- [loose-tasks.md](loose-tasks.md) — open questions to settle before the day.
- [code/](code/) — solution keys. `main.py` is the finished API, `main_autoid.py` the
  server-generated-id variant for the optional section 4 demo, `storage.py` the drop-in
  file participants are handed, `test_main.py` the follow-up's answer key.

## Out of scope for now, moved to the follow-up
There *will* be a follow-up, so this is a real plan rather than a wish list — details in
[next-time.md](next-time.md).

- Testing. Cut from workshop 1 purely for time, and it leads the follow-up. Not very TDD
  of us; three hours is three hours.
- Async. Possibly very useful since most APIs will call underlying services.
- Authentication and session handling.
- Dependency injection properly. Workshop 1 gives a taste via the handed-out
  `storage.py`; the follow-up opens the box.
