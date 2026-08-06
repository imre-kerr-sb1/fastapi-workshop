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
- [workshop-outline.md](workshop-outline.md) — the run sheet for the day. Read the
  timeline reality check at the top before promising anyone three hours.
- [next-time.md](next-time.md) — the follow-up workshop. Persistence and DI lead it, then
  testing.
- [loose-tasks.md](loose-tasks.md) — open questions to settle before the day.
- [code/](code/) — solution keys. `main.py` is the finished API (in-memory, no POST),
  `main_autoid.py` the server-generated-id variant for the optional section 5 demo.
  `storage.py` and `test_main.py` belong to the follow-up.

## Out of scope for now, moved to the follow-up
There *will* be a follow-up, so this is a real plan rather than a wish list — details in
[next-time.md](next-time.md).

- Persistence and dependency injection. Cut from workshop 1 for time — `storage.py` is
  written and works, but `TypeVar`/`Generic`/`yield`-dependencies were the least
  audience-appropriate material in the day. Workshop 1 now ends on a dict in memory, and
  says so. Leads the follow-up.
- Testing. Also cut purely for time, and second in the follow-up, because the DI seam
  from persistence is what makes the tests clean. Not very TDD of us; three hours is
  three hours.
- Async. Possibly very useful since most APIs will call underlying services.
- Authentication and session handling.
