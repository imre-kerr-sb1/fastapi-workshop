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

## Out of scope for now, but possible future workshop
- Async. Possibly very useful since most APIs will call underlying services.
- Authentication and session handling.
- Dependency injection? Need to understand it myself first.
