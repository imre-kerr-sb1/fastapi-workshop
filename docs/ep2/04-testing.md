# 4. Testing

Vi skal nå se på hvordan vi kan skrive automatiske tester for APIet vårt, i stedet for å gjøre
manuelle kall hele tiden. All "testbarheten" vi snakket om i kapittelet om dependency injection
vil forhåpentligvis gjøre seg gjeldende her.

To verktøy vil hjelpe oss på ferden: `TestClient`, som følger med FastAPI og lar oss gjøre kall
mot endepunktene våre uten å faktisk involvere HTTP, og `pytest` som er et mye brukt rammeverk for
å skrive tester i Python.

## Installer pytest
Aller først kan vi legge til pytest i prosjektet vårt. Det er god praksis å legge avhengigheter som
ikke brukes i produksjon i sin egen dependency-gruppe:

```bash
uv add --group dev pytest
```

## Den første testen
La oss starte med å teste at autentisering fungerer, nærmere bestemt at manglende autentisering
skal gi en 401-status:

```python title="test_main.py"
from fastapi.testclient import TestClient

from main import app

PIKACHU = {"display_name": "Pikachu", "type1": "electric"}


def test_missing_auth_is_401():
    client = TestClient(app)
    response = client.put("/pokemon/testachu", json=PIKACHU)
    assert response.status_code == 401
```

```bash
uv run pytest
```

Du vil se at testen ikke kjører en gang. I stedet feiler koden allerede på `from main import app`,
fordi `ADMIN_API_KEY` ikke er satt i miljøet.

Du kan så klart "fikse" dette med å kjøre `ADMIN_API_KEY=tullball uv run pytest`, men det er bedre
praksis å skrive koden din slik at testene kan kjøre med så få eksterne avhengigheter som mulig.

## API-nøkkelen som avhengighet

Vi har lyst til at admin-nøkkelen skal hentes fra en miljøvariabel når vi kjører applikasjonen, men
ikke når vi tester. Dette kan vi få til med "dependency overrides", men da må admin-nøkkelen først
være en avhengighet!

Skriv om linja hvor du leser miljøvariabelen til å være en funksjon, og legg til denne som en
avhengighet i `check_api_key_value`:

```python title="main.py" hl_lines="1-2 7"
def get_admin_api_key() -> str:
    return os.environ["ADMIN_API_KEY"]


def check_api_key_value(
    api_key: Annotated[str, Depends(auth_scheme)],
    admin_api_key: Annotated[str, Depends(get_admin_api_key)],
) -> None:
    if not secrets.compare_digest(api_key, admin_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect API Key",
            headers={"WWW-Authenticate": "APIKey"},
        )
```

Vi har mistet noe her, nemlig at appen ikke lenger kræsjer ved oppstart om miljøvariabelen mangler.
Hvis du vil at den skal gjøre det, kan du legge inn et kall til `get_admin_api_key` i
`lifespan`-funksjonen.

Nå kan du overstyre hvordan FastAPI henter nøkkelen:

```python title="test_main.py" hl_lines="3 7"
from fastapi.testclient import TestClient

from main import app, get_admin_api_key

PIKACHU = {"display_name": "Pikachu", "type1": "electric"}

app.dependency_overrides[get_admin_api_key] = lambda: "test-key"


def test_missing_key_is_401():
    client = TestClient(app)
    response = client.put("/pokemon/testachu", json=PIKACHU)
    assert response.status_code == 401


def test_wrong_key_is_401():
    client = TestClient(app)
    response = client.put("/pokemon/testachu", json=PIKACHU, headers={"X-Api-Key": "nope"})
    assert response.status_code == 401
```

`dependency_overrides` sier til FastAPI: "Når noen ber om funksjon x, kall funksjon y i stedet".
Legg merke til at dette er en dict hvor nøkkelen er **selve funksjonen**, ikke bare navnet.

!!! question "Hvorfor ikke bare sette miljøvariabelen?"
    Dette kan gjøres på en del forskjellige måter, som alle er dårlige idéer i varierende grad:

    #### Kjør testene med miljøvariabelen satt
    Dette krever at man gjør dette overalt hvor tester skal kjøres. Lyst til å kjøre tester med
    "Run tests" i et IDE? Da må IDEet konfigureres til det. Låser deg også til én verdi for 
    hele test-kjøringen.

    #### Kall `os.environ[...] = ...` før du importerer app-objektet
    Veldig grisete å mutere global tilstand i en test (annet enn `app.dependency_overrides` som
    faktisk er ment å brukes sånn), og det bryter med de fleste stilguider å gjøre noe som helst
    før man er ferdig med imports. Du får også her problemet med å være låst til én verdi, med
    bonusen at alle test-filene dine må inkludere samme kodelinje med samme verdi for nøkkelen.
    Rekkefølgen pytest kjører tester i er ikke definert.

    #### Bruk `monkeypatch.setenv`
    Denne kan forsvares, men introduserer en tett kobling mellom testene og det at
    konfigurasjons­verdien kommer fra en bestemt miljøvariabel. Også inkompatibelt med
    caching av `pydantic-settings` som 
    [FastAPI-dokumentasjonen](https://fastapi.tiangolo.com/advanced/settings/#creating-the-settings-only-once-with-lru-cache)
    anbefaler at man bruker i mer komplekse tilfeller.


## Happy path-test for PUT-endepunktet

Nå kan vi prøve å teste et endepunkt som skriver:

```python title="test_main.py"
AUTH = {"X-Api-Key": "test-key"}


def test_put_creates():
    with TestClient(app) as client:  # `with` runs lifespan, so the table exists
        response = client.put("/pokemon/testachu", json=PIKACHU, headers=AUTH)
    assert response.status_code == 201
```

Ser ut til å fungere, men prøv å kjøre testen på nytt. Da feiler den plutselig, fordi statuskoden
er 200 (ikke 201). Og se i APIet eller databasen. `testachu` finnes på ekte nå, fordi testen skrev
til den ekte databasen.

Vi vil at tester skal være isolerte. Både fra flere kjøringer av seg selv, fra andre tester, og fra
"den virkelige verden". Fiksen er det samme som vi gjorde med API-nøkkelen: Vi må overskrive en
avhengighet, denne gangen `get_db`.

## En egen database per test

Pytest har en mekanisme som ligner på FastAPIs dependency injection. Denne kalles "fixtures", og
fungerer ved at man legger dekoratoren `@pytest.fixture` på en funksjon. Så lager man tester som
tar et parameter med samme navn som funksjonen. Litt annen fremgangsmåte enn i FastAPI, men effekten
er den samme.

For enkelhetens skyld legger vi alt i én fixture som `yield`er en `TestClient`-instans. Hvis du
synes dette er mye å ha i én funksjon, kan du splitte den opp ved å la fixtures ta inn fixtures.
(Igjen, akkurat som dependency injection i FastAPI.)

```python title="test_main.py"
import pytest
from fastapi.testclient import TestClient

from db import connect, create_tables, get_db
from main import app, get_admin_api_key

AUTH = {"X-Api-Key": "test-key"}
PIKACHU = {"display_name": "Pikachu", "type1": "electric"}


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


def test_put_creates(client):
    response = client.put("/pokemon/testachu", json=PIKACHU, headers=AUTH)
    assert response.status_code == 201
```

Her skjer det en del ting, så la oss forklare litt:

### `tmp_path`
Dette er en innebygd fixture i pytest som gir stien til en midlertidig mappe (typisk under `/tmp`).
Denne er unik for hver test som kjøres, og det er slik vi sørger for at testene ikke ser hverandres
databaser.

### `create_tables`
Siden vi ikke kjører `with TestClient(app)`, kjører ikke lifespan-funksjonen, så vi må kalle denne
funksjonen selv for at tabellen vår skal finnes.

### `app.dependency_overrides.clear()`
Denne linja ligger etter `yield`, og kjører følgelig etter at testen er ferdig. Slik sørger vi for
at vi starter med helt blanke ark for hver test.


## Hvorfor dependency injection, igjen

- TODO: callback to "Hvorfor?" in chapter 2: now they've seen it
- TODO: the endpoints never knew which key or which database they got

## Oppgaver

1. TODO: get to the fixture version yourself, one step at a time (code above)
2. TODO: move the two 401 tests over to the fixture
3. TODO: PUT twice → 201, then 200, and the change is stored
4. TODO: GET of a missing slug → 404
5. TODO: DELETE, then GET → 404; DELETE again → 404
6. TODO: filter by type
7. TODO (bonus): DELETE of a missing slug without a key → 401, not 404. Why does that matter?
8. TODO (bonus): `@pytest.mark.parametrize` for the type filter
