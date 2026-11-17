# 6. Oppsummering

- TODO: what we did: auth, `Depends`, SQLite, tests with overrides
- TODO: the common thread: endpoints ask, FastAPI provides

## I virkeligheten

- TODO: database: Postgres, not SQLite
- TODO: library: SQLAlchemy / SQLModel instead of raw `sqlite3`; `Session` instead of connection, same `Depends` pattern
- TODO: migrations: Alembic
- TODO: tests: a real Postgres in a container (testcontainers), one transaction per test, rolled back
- TODO: don't test against SQLite if production is Postgres
- TODO: settings: pydantic-settings instead of `os.environ`

## Neste gang

- TODO: ep3 teaser
