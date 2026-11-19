---
marp: true
theme: default
paginate: true
size: 16:9
lang: nb
style: |
  section {
    font-size: 27px;
  }
  section.lead h1 {
    font-size: 2em;
  }
  section pre {
    font-size: 0.6em;
    line-height: 1.35;
  }
  section code {
    font-size: 0.95em;
  }
  section.divider {
    background: #1f2430;
    color: white;
  }
  section.divider h1 {
    color: white;
  }
  section.divider h2 {
    color: #9fb3d9;
  }
---

<!-- _class: lead -->
<!-- _paginate: false -->

# FastAPI: Episode 2

### Autentisering, Dependency Injection, Database og Testing

<!--
Velkommen tilbake! Spør hvem som var med forrige gang, og hvem som er helt ny.
De nye klarer seg fint med løsningsforslaget fra episode 1.

Tidsbudsjett: ca. 20 minutter snakk, resten er egen jobbing med håndboka.
-->

---

## Struktur på workshopen

- Tar utgangspunkt i APIet dere bygde forrige gang (eller løsningsforslaget)
- Jeg presenterer temaene kjapt nå (20-30 minutter)
- Dere jobber med implementering resten av tiden

<!--
Si tydelig at det er meningen at ting går fort nå. Alt står i håndboka, så de
trenger ikke notere kode. Poenget med snakkinga er at de skal kjenne igjen ting
når de leser det senere.
-->

---

## Mens jeg snakker

...kan dere godt fyre opp et Coder-workspace og finne frem koden fra forrige gang.

<!--
Samme triks som sist: oppsett i bakgrunnen mens du snakker. Ikke vent på at alle
er klare, det er ingen kode de skal skrive mens du presenterer.

Ingen kode fra forrige gang? Løsningsforslaget ligger i code/ep1 i repoet.
-->

---

<!-- _class: divider -->

# Kapittel 1

## Autentisering

<!--
Ca. 4 minutter. Dette er også første gang de ser Depends -- ikke forklar det
ordentlig her, det er neste kapittel.
-->

---

## Alle kan slette alt

Akkurat nå kan hvem som helst som når APIet ditt gjøre `PUT` og `DELETE`.

- I dag: en **API-nøkkel** i en header
- Finnes også: HTTP Basic, OAuth2, OpenID Connect, ...
- GET-endepunktene lar vi være åpne (ditt valg)

<!--
Ikke gå inn på OAuth2 og venner. Hvis noen spør: FastAPI har god dokumentasjon på
alle sammen, lenke i håndboka. API-nøkkel er det enkleste som faktisk er nyttig.
-->

---

## Sjekk nøkkelen

```python
from fastapi.security import APIKeyHeader

auth_scheme = APIKeyHeader(name="X-Api-Key")

# KeyError hvis variabelen mangler. Bra! Vi vil ikke ha en default her.
ADMIN_API_KEY = os.environ["ADMIN_API_KEY"]


def check_api_key_value(api_key: Annotated[str, Depends(auth_scheme)]) -> None:
    if not secrets.compare_digest(api_key, ADMIN_API_KEY):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect API Key")
```

```bash
ADMIN_API_KEY=superhemmeligverdi uv run fastapi dev main.py
```

<!--
To ting å peke på:

1. compare_digest i stedet for !=. Vanlig != avbryter så fort den finner et tegn
   som ikke stemmer, og det kan man i teorien måle seg frem til. Timing-angrep.
2. Nøkkelen kommer fra en miljøvariabel, og det er ingen default. Hold på denne,
   den kommer tilbake og biter oss i testkapittelet.
-->

---

## Koble den på endepunktene

```python
@app.put(
    "/pokemon/{slug}",
    summary="Create or replace a Pokémon",
    dependencies=[Depends(check_api_key_value)],
)
async def put_pokemon(slug: SlugPath, update: PokemonUpdate, response: Response) -> Pokemon:
    ...
```

`Depends`: "Kall denne funksjonen for meg før endepunktet kjører."

Bonus: knappen **Authorize** og hengelåser i `/docs`.

<!--
Vis gjerne docs-siden live hvis du har den oppe. Hengelåsene er en fin
demonstrasjon av at FastAPI vet om avhengigheten, ikke bare kjører den.

Manglende nøkkel og feil nøkkel gir begge 401, men fra hvert sitt sted:
APIKeyHeader avviser manglende header, funksjonen vår avviser feil verdi.
-->

---

<!-- _class: divider -->

# Kapittel 2

## Dependency injection

<!--
Ca. 5 minutter. Det viktigste kapittelet, men også det mest abstrakte. Hold det
konkret, resten av episoden er eksempler på det samme.
-->

---

## Du har gjort dette hele tiden

```python
@app.get("/something")
def get_something(q: str) -> list[Something]:
    ...
```

"Jeg trenger en string fra query-parameteret `q`."

Du sier **hva** du trenger. FastAPI finner ut **hvordan** du får det.

`Depends` gjør det samme for dine egne ting.

<!--
Dette er hele poenget med DI, og de har allerede brukt det i en hel workshop uten
å tenke over det. Path-parametre, query-parametre og body kommer "magisk" inn i
funksjonen. Depends er samme magi, bare at kilden er en funksjon du har skrevet
selv.

Kommer du fra Spring eller lignende: dette er mye enklere. Ingen container, ingen
beans. Bare "kall denne funksjonen per request og gi meg svaret".
-->

---

## Avhengigheter med avhengigheter

```python
def inner_dependency(n: int, m: int) -> int:  # Hentes fra query-parametre
    return n + m


def outer_dependency(dependency: Annotated[int, Depends(inner_dependency)]) -> int:
    return dependency + 1


@app.get("/my-endpoint")
def my_endpoint(dependency: Annotated[int, Depends(outer_dependency)]) -> list[Something]:
    ...
```

Samme regler som for endepunkter, så langt innover du vil.

<!--
Gå baklengs gjennom kjeden: endepunktet trenger outer, outer trenger inner, inner
trenger n og m fra URLen. FastAPI løser opp alt sammen før endepunktet kjører.

Pek på at check_api_key_value var akkurat dette: den trengte auth_scheme, som
trengte en header.
-->

---

## Hvorfor?

- **Kortere kode.** Rammeverket gjør det kjedelige, i riktig rekkefølge.
- **DRY.** Én funksjon, brukt på alle endepunktene som trenger den.
- **Testbarhet.** Kommer i kapittel 4, og det er der det blir gøy.

<!--
Ikke selg testbarhet for hardt nå. Det er gulroten for slutten, og det er mye mer
overbevisende når de ser det enn når du sier det.
-->

---

<!-- _class: divider -->

# Kapittel 3

## Database

<!--
Ca. 6 minutter. Dette er der de kommer til å bruke mest tid. De kan SQL, så
fokuser på det som er nytt: hvor forbindelsen kommer fra.
-->

---

## SQLite

- Følger med Python, ingen server å kjøre opp
- "Embedded": databasen kjører i samme prosess som APIet
- Én fil på disk

SQLite er DuckDB for transaksjonelle data.

<!--
Dataene fra forrige gang forsvant ved hver restart. Nå skal de ligge i en fil.

I virkeligheten hadde du brukt Postgres eller lignende, men det er bare
plumbing. Mønsteret er det samme.
-->

---

## `db.py`: ferdig oppsett

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    connection = connect(DB_PATH)
    create_tables(connection)  # CREATE TABLE IF NOT EXISTS
    connection.close()
    yield  # Appen kjører mens vi står pauset her


def get_db():
    connection = connect(DB_PATH)
    try:
        yield connection  # Før yield: før endepunktet. Etter: etterpå.
    finally:
        connection.close()


DbConnection = Annotated[sqlite3.Connection, Depends(get_db)]
```

<!--
Denne filen får de ferdig i håndboka, de trenger ikke skrive den selv.

- lifespan kjører én gang ved oppstart. Ingen Depends her: det finnes ingen
  request ennå, så FastAPI har ingenting å injisere i.
- get_db åpner en forbindelse per request og lukker den etterpå, også hvis
  endepunktet kaster en exception.
- DbConnection er samme triks som SlugPath fra forrige gang.

CREATE TABLE IF NOT EXISTS er hele migrasjonssystemet vårt. Hvis noen spør om
Alembic og venner: tipsboks i håndboka.
-->

---

## SQL i egne funksjoner

```python
def fetch_pokemon(connection: sqlite3.Connection, slug: str) -> Pokemon | None:
    row = connection.execute("SELECT * FROM pokemon WHERE slug = :slug", {"slug": slug}).fetchone()
    if row is None:
        return None
    return row_to_pokemon(row)


@app.get("/pokemon/{slug}")
async def get_pokemon(slug: SlugPath, connection: DbConnection) -> Pokemon:
    pokemon = fetch_pokemon(connection, slug)
    if pokemon is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Pokémon with slug {slug!r}")
    return pokemon
```

SQL-funksjonen vet ingenting om HTTP. Endepunktet bestemmer hva `None` betyr.

<!--
Endepunktet ber om en DbConnection og sender den videre. Det åpner og lukker
aldri noe selv.

Forbindelsen som første argument er sånn de fleste dataengineers allerede jobber,
f.eks. pd.read_sql(query, conn).

Og nei, vi bruker ikke ORM. Du vet hva jeg mener om ORMer.
-->

---

## Tre ting som biter

- **`commit()`.** sqlite3 åpner en transaksjon for deg. Lukker du uten commit, er
  endringene borte.
- **Parameter-binding.** `:slug`, aldri f-strings.
- **201 vs 200 i PUT.** `UPDATE` først, sjekk `rowcount`, så `INSERT` hvis ingenting
  ble oppdatert.

<!--
commit-tingen er den de faktisk kommer til å gå på. "Dataene mine forsvinner" =
glemt commit.

Parameter-binding vet de sikkert fra før, men si det likevel. SQL injection er
fortsatt et ting.

rowcount-trikset dukker opp i oppgavene for både DELETE og PUT. Det er en fin
ting å ha sett én gang før de setter i gang.
-->

---

<!-- _class: divider -->

# Kapittel 4

## Testing

<!--
Ca. 5 minutter. Her betaler DI seg. Fortell det som en historie: hver test vi
prøver å skrive feiler på en ny måte, og fiksen er hver gang den samme.
-->

---

## Den første testen

```python
from fastapi.testclient import TestClient

from main import app


def test_missing_auth_is_401():
    client = TestClient(app)
    response = client.put("/pokemon/testachu", json=PIKACHU)
    assert response.status_code == 401
```

Kjører ikke en gang: `KeyError: 'ADMIN_API_KEY'` på `from main import app`.

<!--
Her kommer miljøvariabelen tilbake og biter, som lovet.

Spør rommet hvorfor. Svaret: os.environ leses når main.py importeres, altså før
noen test kjører.

Du kan "fikse" det med ADMIN_API_KEY=tullball uv run pytest, men det er en dårlig
idé. Håndboka har en boks om hvorfor.
-->

---

## Du kan bare overstyre det du injiserer

```python
def get_admin_api_key() -> str:
    return os.environ["ADMIN_API_KEY"]


def check_api_key_value(
    api_key: Annotated[str, Depends(auth_scheme)],
    admin_api_key: Annotated[str, Depends(get_admin_api_key)],
) -> None:
    ...
```

```python
# test_main.py
app.dependency_overrides[get_admin_api_key] = lambda: "test-key"
```

"Når noen ber om `get_admin_api_key`, kall denne i stedet."

<!--
Dette er hovedpoenget i hele testkapittelet. En global variabel kan ikke
overstyres. En avhengighet kan.

Nøkkelen i dicten er selve funksjonen, ikke navnet.

Prisen: appen kræsjer ikke lenger ved oppstart hvis variabelen mangler. Du får en
500 ved første kall som trenger den i stedet.
-->

---

## Happy path

```python
def test_put_creates():
    with TestClient(app) as client:
        response = client.put("/pokemon/testachu", json=PIKACHU, headers=AUTH)
    assert response.status_code == 201
```

Grønn! Kjør den igjen: `assert 200 == 201`.

Testen skrev til den ekte databasen. `testachu` finnes nå på ekte.

<!--
La dem tenke litt før du sier svaret. Andre gang fantes testachu allerede, så PUT
ga 200.

Tester skal være isolerte: fra seg selv, fra andre tester, og fra den virkelige
verden. Fiksen er den samme som for nøkkelen: overstyr get_db.
-->

---

## En egen database per test

```python
@pytest.fixture
def client(tmp_path):
    db_path = str(tmp_path / "test.db")
    connection = connect(db_path)
    create_tables(connection)
    connection.close()

    def get_test_db():
        connection = connect(db_path)
        try:
            yield connection
        finally:
            connection.close()

    app.dependency_overrides[get_admin_api_key] = lambda: "test-key"
    app.dependency_overrides[get_db] = get_test_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

<!--
Fixtures er pytests egen versjon av dependency injection. Testen tar et parameter
som heter client, og pytest kaller fixturen for å lage den.

- tmp_path: en ny, tom mappe per test, fra pytest.
- create_tables selv, fordi vi ikke bruker with TestClient og lifespan derfor ikke
  kjører.
- Alt etter yield kjører etter testen, så neste test starter blankt.

Ikke :memory: -- hver forbindelse til :memory: får sin egen tomme database, så
tabellen er borte ved neste request. Står i håndboka.
-->

---

## Endepunktene endret seg ikke

Ikke én linje.

De vet ikke hvilken nøkkel som er riktig, eller hvilken database de snakker med.
De sier hva de trenger, og noen andre bestemmer hva de får.

**Alt du vil kunne bytte ut i en test bør komme inn via `Depends`.**

<!--
Dette er sliden hele episoden har bygget mot. Ta en pause her.

Koble tilbake til "Hvorfor?"-sliden i kapittel 2: nå har de sett det.
-->

---

## I virkeligheten

- Postgres i stedet for SQLite
- SQLAlchemy/SQLModel, eller rå SQL med psycopg (mitt valg)
- Migrasjoner med Alembic, Flyway, dbmate, ...
- Tester mot en ekte Postgres i en container, én transaksjon per test

Mønsteret med `Depends` og `dependency_overrides` er det samme.

<!--
Kort. Poenget er at det de lærer i dag ikke er leketøy, det er det samme mønsteret
som brukes i ekte prosjekter. Bare med tyngre verktøy.

Ikke test mot SQLite hvis du kjører Postgres i produksjon. Dialektene er
forskjellige nok til at testene kan bli grønne mens produksjon feiler.
-->

---

<!-- _class: lead -->
<!-- _paginate: false -->

# Deres tur!

### fastapi.kerror.net/ep2

Start med kapittel 1. Kom deg til testing, selv om databasen ikke er helt ferdig.

<!--
La denne sliden stå oppe resten av workshopen.

Gå rundt og hjelp. Rundt 45 minutter før slutt: si høyt at de som fortsatt sitter
i databasekapittelet bør hoppe over til testing. Det er der poenget med hele
episoden ligger, og testene fungerer fint på et halvferdig API.
-->
