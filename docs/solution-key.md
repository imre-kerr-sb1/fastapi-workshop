# Løsningsforslag

Det komplette APIet, i to varianter avhengig av hva slags ID-regime du velger.

For å kjøre dem:

```bash
cd code
uv run fastapi dev main.py
uv run fastapi dev main_autoid.py
```

## `main.py`

APIet fra steg 3-7. Endepunkter for GET all, GET single, DELETE, og et PUT-endepunkt
som håndterer både create og delete.

Det kunne vært skrevet enda mer fancy. Arv, mer bruk av `Annotated`... Men jeg har holdt
meg til det mest grunnleggende for å fokusere på FastAPI spesifikt.

```python title="main.py"
--8<-- "main.py"
```

## `main_autoid.py`

Designet for [case B i steg 5](05-identifiers.md#b-klienten-kan-ikke-velge) — en
hendelseslogg der serveren bestemmer ID. Verdt å lese og sammenligne med `main.py`.

- Den har `POST` for å håndtere creates.
- `POST`-endepunktet returnerer en `Location`-header, sånn at klienten får vite hvor
  nyopprettede objekter bor.
- `PUT` er kun for oppdateringer, og svarer 404 dersom IDen ikke finnes.

```python title="main_autoid.py"
--8<-- "main_autoid.py"
```
