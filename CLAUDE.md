# CLAUDE.md

## Language

All responses, new code, and new docs in **English**. The existing handbook (`docs/`),
`README.md`, `slides/` and `mkdocs.yml` are Norwegian; don't translate them unless asked.

## What this is

A self-paced FastAPI workshop series in episodes. Each episode starts from the previous
episode's solution key. Everything is split per episode: `docs/epN/`, `code/epN/`,
`slides/epN/`. `docs/index.md` is the landing page linking the episodes.

Episode 1 (~3 hours): participants build a CRUD API (Pokémon example) from scratch.

- `docs/ep1/` — the handbook, one numbered page per step, built with zensical (`mkdocs.yml`).
- `slides/ep1/slides.md` — Marp slides; presenter notes live in HTML comments.
- `code/ep1/main.py` — the solution key. Client-chosen slugs, `PUT` as upsert, deliberately
  no `POST`, in-memory dict datastore. Written for weak-Python readers: no inheritance
  between models, no walrus, no `**kwargs`, `Annotated` only once.
- `code/ep1/main_autoid.py` — presenter demo of the opposite design (server UUIDs + `POST`).

Episode 2: persistence, DI and testing (teased in `docs/ep1/08-wrap-up.md`). Its start
point is `code/ep2/main.py`, a copy of the episode 1 solution key. All of `code/` shares
one uv project (`code/pyproject.toml`, already has pytest).

## Commands

```bash
uv run zensical serve        # handbook at localhost:8000 (run from repo root)
uv run zensical build -s     # strict build; catches broken links/snippet paths
cd code/ep1 && uv run fastapi dev main.py
```

`docs/ep1/solution-key.md` includes files from `code/` via `pymdownx.snippets` with
`base_path: code` (so paths look like `ep1/main.py`), resolved relative to the CWD — so always build from the repo root.
