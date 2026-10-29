# TODO

## ep2 / 02-auth

- [x] Syntax error in the `check_api_key_value` snippet: missing `:` after `compare_digest(...)`.
- [x] Explain `Depends` (placeholder TODO in the chapter). Short note only; see DI plan below.
- [x] Testing section: state the expected status codes for wrong key vs. missing header.
      Missing header is rejected by `APIKeyHeader` (401 or 403 depending on FastAPI version,
      check the pinned one); wrong key is rejected by our function (401).
- [x] Say explicitly that GET endpoints stay open by choice.
- [-] Show what the `KeyError` crash looks like when `ADMIN_API_KEY` is unset. Reword "Will KeyError".
- [x] `uv run fastapi dev` vs ep1's `fastapi dev main.py`: pick one form.
- [x] Optional add-on exercises: read key + write key; a `TestClient` test for the 401;
      dependency on an `APIRouter` instead of per endpoint.
- [x] (Pedantic, maybe skip) 401 without a `WWW-Authenticate` header violates RFC 9110.
- [x] `check_api_key_value` still returns `api_key`, which nothing uses now. Drop it, or keep
      it as the hook for a later "dependencies return values" example.

## ep2 / 01-middleware

- [x] Task 2 (log all requests): warn that logging `request.headers` now leaks `X-Api-Key`.
- [-] Hand-rolled CORS only sets `Allow-Origin`. The custom header triggers a preflight, so
      browser clients also need `Access-Control-Allow-Headers` (or use `CORSMiddleware`).

## code/ep2/main.py

- [ ] Module docstring (placeholder TODO).
- [x] Comment above `Slug Path` says `Annotated` is "the one piece of intimidating syntax" —
      no longer the only use.
- [x] Trailing whitespace (lines 22-23 and elsewhere).

## DI use cases:
The list is in teaching order. Each item adds one new idea.

1. Shared query parameters (pagination). Put limit and offset in one dependency and use it on all list endpoints. A dependency can take request parameters itself. This is FastAPI's own first example.
2. Load-or-404. get_pokemon_or_404(slug: SlugPath) -> Pokemon. Your GET and DELETE already repeat if slug not in datastore: raise 404, so the refactor is real and easy to see. The new ideas: a dependency returns a useful value, and it can stop the request.
3. Auth. You already have this. It is the "no useful return value → dependencies=[...]" case. Then current user or role: return an identity from the key, and add require_role("write") as a dependency factory. Use this only as an add-on, because closures are too much for this audience.
4. The datastore as a dependency. get_datastore() returns the dict. This is the bridge to persistence: replace the dict with a database and the endpoints do not change. Tests also get a new, empty store each time.
5. Settings. get_settings() with @lru_cache. This connects to your Settings tip box, and it removes the import-time KeyError. Tests can override it.
6. DB session with yield. You already have this. The new idea is setup and teardown around the request. It is like a context manager, and the data people know with.
7. An outbound HTTP client. Use one shared httpx.AsyncClient to get data from pokeapi.co, for example sprites or real stats. It fits the theme, and it is a good thing to fake in tests.
8. A clock. Inject now() for a created_at field, so that tests are deterministic. It is small and clear.
9. The request ID from the middleware. A dependency reads request.state.request_id. This connects to chapter 1, and it gives a cleaner alternative to request.state everywhere.
10. app.dependency_overrides in the testing chapter. This is the payoff that explains why DI exists. Give the full explanation of DI here. By this point the participants have seen items 1–9, so the theory explains things that they already use.

One subtle point for the full explanation: FastAPI caches a dependency for each request. If two dependencies both use get_settings, FastAPI calls it only once per request. This surprises people when the dependency has side effects.
