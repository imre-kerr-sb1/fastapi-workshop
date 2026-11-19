# fastapi-workshop

En workshop-serie der du bygger et fungerende HTTP-API med FastAPI, fra bunnen av. Hver episode
tar ca. tre timer, og du trenger bare grunnleggende Python — resten forklares underveis.

- **Episode 1:** Et CRUD-API med validering, statuskoder og identifikator-design. Dataene ligger i
  minnet.
- **Episode 2:** Autentisering, dependency injection, en ekte database (SQLite) og automatiske
  tester. Starter der episode 1 slapp.

## Var du ikke med på workshopen, eller gikk du tom for tid?

Hele workshopen finnes som en **selvgående håndbok**, og du kan gjøre den helt på egen hånd.
Ingen instruktør nødvendig. Den ligger på [fastapi.kerror.net](https://fastapi.kerror.net), eller
du kan kjøre den lokalt:

```bash
uv run zensical serve
```

Åpne [http://localhost:8000](http://localhost:8000), velg en episode og start på kapittel 1. Hvert
kapittel bygger videre på det forrige.

Gikk du tom for tid midt i workshopen? Se hvilket kapittel du var på i [docs/ep1/](docs/ep1/) eller
[docs/ep2/](docs/ep2/) (filnavnene er nummererte), og fortsett derfra.

Sitter du fast, eller vil du sjekke koden din mot en fasit? Løsningsforslagene ligger i
[code/](code/). For episode 1 finnes det også på [docs/ep1/solution-key.md](docs/ep1/solution-key.md).
Har du ikke koden fra episode 1, kan du starte episode 2 med [code/ep1/main.py](code/ep1/main.py).

## Layout

- [docs/](docs/) — håndboken, på norsk. Bygget med [zensical](https://zensical.org/), én
  side per kapittel, én mappe per episode.
- [slides/](slides/) — presentasjonene til den instruktørledede workshopen, som
  [Marp](https://marp.app/)-markdown. Se [slides/README.md](slides/README.md).
- [code/](code/) — løsningsforslag, én mappe per episode.
  - `ep1/main.py` er det ferdige APIet fra episode 1 (in-memory, ingen POST).
    `ep1/main_autoid.py` er varianten med server-genererte IDer fra steg 5.
  - `ep2/` er det ferdige APIet fra episode 2: `main.py` (endepunkter og SQL), `db.py`
    (databaseoppsett) og `test_main.py` (testene).

## Kjøre koden selv

Episode 1:

```bash
cd code/ep1
uv run fastapi dev main.py
```

Episode 2 trenger en API-nøkkel, og lager en SQLite-fil (`workshop.db`) i mappa der du kjører den:

```bash
cd code/ep2
ADMIN_API_KEY=superhemmeligverdi uv run fastapi dev main.py
uv run pytest
```

Testene trenger ikke miljøvariabelen, og rører ikke databasefila.

Se [docs/ep1/02-setup.md](docs/ep1/02-setup.md) hvis du ikke har `uv` installert ennå.

## Bygge håndboken

```bash
uv run zensical serve      # http://localhost:8000, live reload
uv run zensical build -s   # strict: feiler på ødelagte lenker og anker
```

Kjør fra rot-mappa i repoet. [docs/ep1/solution-key.md](docs/ep1/solution-key.md) inkluderer koden
direkte fra [code/](code/) med snippets, så den kan ikke komme ut av synk — men
`pymdownx.snippets` løser `base_path` relativt til arbeidsmappa, så bygging fra et annet sted
knekker det. `-s` fanger opp dette.
