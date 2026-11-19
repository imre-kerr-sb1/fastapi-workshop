# 3. Database

Så langt har vi brukt en dict som datalager i CRUD-APIet vårt. Dette har fungert greit som et
pedagogisk verktøy, men det har noen klare svakheter i den virkelige verden, som at alle dataene
man skriver forsvinner hver gang APIet restartes. Det er på tide å introdusere en skikkelig database.

Vi velger å bruke SQLite, en såkalt "embedded database" som følger med standardbiblioteket i Python.
"Embedded" betyr at databasen kjører i samme prosess som applikasjonen som bruker den, som igjen
betyr at vi ikke trenger å styre med å kjøre opp en separat prosess med Postgres eller lignende.
Kommer du fra dataområdet har du kanskje hørt at "DuckDB er SQLite for analytiske data"? Vi kan snu
på det og si at SQLite er DuckDB for transaksjonelle data.

Dette kapittelet introduserer en del konsepter fort og gæli, dette måtte til for å rekke alt sammen
innenfor tiden til workshopen. Anbefaler å notere deg og lete opp ting du ikke forstår i ettertid.

## Oppsettet: `db.py`

Kopier denne koden inn i en ny fil som du kaller `db.py`. Endre `CREATE TABLE`-spørringen til å
passe til ditt eget domene.

```python title="db.py" hl_lines="12-17"
import sqlite3
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI

DB_PATH = "workshop.db"

# `IF NOT EXISTS` makes this safe to run on every startup: a fresh file gets the table,
# an existing one is left alone.
SCHEMA = """
CREATE TABLE IF NOT EXISTS pokemon (
    slug TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    type1 TEXT NOT NULL,
    type2 TEXT
)
"""


def connect(path: str) -> sqlite3.Connection:
    # FastAPI may open the connection in one thread and run the endpoint in another.
    # That's safe here because no two requests ever share a connection.
    connection = sqlite3.connect(path, check_same_thread=False)
    # Lets us read columns by name: row["slug"] instead of row[0].
    connection.row_factory = sqlite3.Row
    return connection


def create_tables(connection: sqlite3.Connection) -> None:
    connection.execute(SCHEMA)
    connection.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    connection = connect(DB_PATH)
    create_tables(connection)
    connection.close()
    yield  # The app runs while we're paused here.


def get_db():
    connection = connect(DB_PATH)
    try:
        yield connection # Everything before `yield` runs before the endpoint; everything after, after
    finally: # This block runs even if the endpoint raises an exception
        connection.close()


# Type-alias, same trick we used with `SlugPath`
DbConnection = Annotated[sqlite3.Connection, Depends(get_db)]
```

### Initialisering med `lifespan`

Vi trenger et sted å kjøre `CREATE TABLE`-spørringen vår. Aktuelle alternativer:

- Gjør det helt utenfor APIet med et tredjeparts verktøy (sqlite CLI, SQL Tools i VS Code...)
- Kjør det rett i main.py
- Bruk et databasemigrasjonsverktøy, f.eks [Alembic](https://alembic.sqlalchemy.org)
- FastAPIs egen mekanisme for oppgaver som skal gjøres ved oppstart og avslutning: `lifespan`

Vi velger det siste, siden dette tross alt er en workshop om FastAPI.

`lifespan` er en async-funksjon du kan sende inn til appen din (`FastAPI`-objektet), og kjører ved
oppstart. Inne i denne funksjonen må man ha en `yield`, som betyr "paus funksjonen her". "Pausen"
er at APIet kjører, og alt som kommer etter `yield` kjøres når appen skal stoppe.

Selve funksjonen er definert i `db.py` (forrige avsnitt). Legg merke til at denne *ikke* får
databaseforbindelsen med dependency injection. DI skjer kun når FastAPI håndterer et HTTP-kall.

Legg til disse linjene for å registrere lifespan-funksjonen.

```python title="main.py" hl_lines="1 6"
from db import DbConnection, lifespan

app = FastAPI(
    title="Pokédex",
    summary="A toy CRUD API, built to demonstrate rather too many FastAPI features.",
    lifespan=lifespan,
)
```

## SQL i egne funksjoner

Skriv noen funksjoner for å lese, lagre og oppdatere objekter i databasen din. Ved lesing trenger
du også en funksjon som kan konvertere fra databaserader (dict-aktig type) til domeneobjekter.
Det går an å bruke et ORM-bibliotek som [SQLAlchemy](http://sqlalchemy.org/) til dette, men vi
holder det enkelt. (At jeg har en personlig vendetta mot ORMer har ingen ting med saken å gjøre.)

Vi holder SQL-koden separat fra endepunktsfunksjonene, og blander heller ikke inn HTTP-konsepter
(`HTTPException` eller statuskoder) i SQL-funksjonene. Dette prinsippet (SLAP = Single Level of
Abstraction Principle) hjelper med kodegjenbruk og testbarhet.

SQL-funksjonene tar inn en databaseforbindelse som første argument. Dette gjør at hvis et endepunkt
må kalle flere SQL-funksjoner kan den gjenbruke samme forbindelse.

```python title="main.py"
import sqlite3


def row_to_pokemon(row: sqlite3.Row) -> Pokemon:
    return Pokemon(
        slug=row["slug"],
        display_name=row["display_name"],
        type1=row["type1"],
        type2=row["type2"],
    )


def fetch_pokemon(connection: sqlite3.Connection, slug: str) -> Pokemon | None:
    row = connection.execute("SELECT * FROM pokemon WHERE slug = :slug", {"slug": slug}).fetchone()
    if row is None:
        return None
    return row_to_pokemon(row)
```

!!! warning "Parameter-binding"
    Hvis spørringen din trenger å inneholde parametre som `slug`-parametret over, må du bruke
    parameter-binding. Limer du strenger rett inn i spørringer risikerer du å være sårbar for SQL-
    injection-angrep. Du får også dårligere ytelse fordi databasen ikke kan cache kompilerte
    spørringer.

    Du må altså aldri finne på å skrive kode som dette her:

    ```python
    row = connection.execute(f"SELECT * FROM pokemon WHERE slug = {slug}").fetchone()
    ```


## Injiser tilkoblingen i et endepunkt

```python title="main.py" hl_lines="6"
@app.get(
    "/pokemon/{slug}",
    summary="Fetch a single Pokémon",
    responses={404: {"description": "No Pokémon with that slug"}},
)
async def get_pokemon(slug: SlugPath, connection: DbConnection) -> Pokemon:
    pokemon = fetch_pokemon(connection, slug)
    if pokemon is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Pokémon with slug {slug!r}")
    return pokemon
```

Her ser vi dependency injection i aksjon. FastAPI kaller `get_db` for deg, og endepunktet trenger
bare å bruke forbindelsen det får.

Her ser vi også den andre siden av SLAP-poenget i forrige avsnitt. SQL-funksjonen returnerer `None`,
og endepunktet bestemmer hva det betyr i HTTP-verden.

## Skriving og `commit`

Når du skriver funksjonene som skal skrive data, må du huske å avslutte med `connection.commit()`
(dersom alt gikk bra). Dette er fordi sqlite3-modulen i python åpner en transaksjon for deg når du
kjører en spørring som oppdaterer data (`INSERT`, `UPDATE` eller `DELETE`). Dersom 
`connection.close()` kalles uten en `connection.commit()` først, vil alle endringer bli rullet
tilbake.

Det finnes også noe som heter autocommit som kjører commit etter hver oppdatering, men dette må man
be om eksplisitt:

```python
# Python <= 3.11
sqlite3.connect(path, isolation_level=None)

# Python >= 3.12
sqlite3.connect(path, autocommit=True)
```

## Oppgaver

1. Lag `db.py`, `lifespan`-funksjon, og hent enkeltobjekter fra databasen. (Koden over, kan hende du
    har gjort dette alt.)
2. Skriv en SQL-funksjon for PUT-endepunktet. (Gjør denne tidlig, så har du data å teste resten med.)
    - Hint: 201 vs 200 for upsert-semantikk. Beste måten å få til dette er to spørringer:
    `UPDATE`, sjekk rowcount, `INSERT`. `cursor.rowcount` forteller hvor mange rader en spørring
    berørte.
3. Skriv en SQL-funksjon for liste-endepunktet, med filtrering hvis du trenger det.
4. Skriv en SQL-funksjon for DELETE-endepunktet.
    - Hint: Endepunktet skal returnere 404 dersom det ikke fantes noe å slette. `rowcount` hjelper
    deg her også.
5. Nå som alle endepunktene bruker databasen, kan du slette `datastore`. Restart serveren og sjekk
    at dataene fortsatt ligger der. Du kan også "koble til" databasen med SQLite CLI:
    ```bash
    sudo apt install sqlite3  # Debian/Ubuntu/WSL. Already installed on macOS
    sqlite3 workshop.db
    ```

!!! tip "Trenger du å endre tabeller senere?"
    Hvis du glemmer en kolonne eller trenger å endre noe etter opprettelse, holder det ikke å oppdatere
    `CREATE TABLE`-spørringen. Legg heller til en `ALTER TABLE` i `create_tables`.

    Dette kan bli komplekst over tid, og er et godt argument for å se på databasemigrasjonsverktøy.
    Noen kandidater:

    - [Alembic](https://alembic.sqlalchemy.org/): Python, del av SQLAlchemy, kan autogenerere migrasjoner fra modeller
    - [yoyo-migrations](https://ollycope.com/software/yoyo/latest/): Python, en mappe med vanlige `.sql`-filer
    - [dbmate](https://github.com/amacneil/dbmate): frittstående program, ren SQL med up/down-seksjoner
    - [Flyway](https://github.com/flyway/flyway): originalen, fungerer sammen med alle språk
    - [`PRAGMA user_version`](https://www.sqlite.org/pragma.html#pragma_user_version): gjør-det-selv-varianten i SQLite
