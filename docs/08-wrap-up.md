# 8. Oppsummering, og ideer til neste gang

## Hva du bygde

Et fullstendig HTTP-API. Mer spesifikt:

- **Fire endepunkter** som til sammen utgjør CRUD.
- **Validert input.** Feil typer, manglende felter og uønskede data avvises før koden din
    ser dem, og APIet svarer med maskinlesbare feilmeldinger.
- **Riktige statuskoder,** inkludert noen rammeverket ikke klarte å gjette selv..
- **Interaktiv dokumentasjon** du ikke skrev, og således ikke kan glemme å oppdatere.

Dette har blitt gjentatt mye, men jeg vil si det en siste gang: **Du skrev typer og fikk
oppførsel.** Én `StrEnum` ga deg validering, fornuftige feilmeldinger og en dropdown i
docs-siden. Én `-> list[Pokemon]` ga deg serialisering og validering av output-data.

## Hva mangler

Masse (sjekk ut [https://pokeapi.co/](https://pokeapi.co/)), men to ting peker seg ut:

### 1. Dataene dine forsvinner hver gang du oppdaterer koden

Dette har du sikkert merket. "Databasen" din er bare en dict i minnet, og er ikke lagret
på disk noe sted.

En ekte database hadde vært bedre. SQLen til denne blir ganske grunnleggende
(INSERT/SELECT/UPDATE/DELETE mapper 1-til-1 med CRUD). Men det er mer kode som må til enn
bare SQL.

Hvis du vil bruke en database, hvordan ser koden din som nå bare bruker `datastore` ut?
Hvor oppretter du databaseforbindelser? Hva med transaksjonshåndtering?

Dette kan bli veldig mye duplisert kode, og du risikerer å gjøre noen uheldige valg. Hvis
du bare har én databaseforbindelse, kan APIet ditt bare håndtere én forespørsel av gangen.
Hvis du lager en forbindelse for hvert kall, blir endepunktene dine treige og kan overbelaste
databasen hvis du har mye trafikk.

Løsningen (i hvertfall på dupliseringsproblemet) kalles **dependency injection**. Koden din
sier hva den trenger, og FastAPI sørger for at det er tilgjengelig.

```python
async def get_pokemon(slug: SlugPath, store: PokemonStore) -> Pokemon:
    ...
```

Nok en gang gjør typeannotasjoner jobben for deg. Du gir FastAPI en måte å lage `PokemonStore`
og sier at funksjonen trenger en, så håndterer FastAPI resten.

### 2. Du skrev ingen tester

Du gjorde riktignok masse manuell testing, men vi kan bedre. Automatiske tester sørger
for at APIet ditt oppfører seg riktig etter hvert som koden endrer seg.

`TestClient` lar deg skrive alle testene og kjøre dem mot en isolert server, alle i én jafs
på under et sekund.

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_put_is_idempotent():
    assert client.put("/pokemon/vulpix", json=VULPIX).status_code == 201
    assert client.put("/pokemon/vulpix", json=VULPIX).status_code == 200
    assert len(client.get("/pokemon").json()) == 1
```

Du trenger ikke spinne opp `fastapi dev` i terminalen. `TestClient` snakker direkte med `app`.

## Extra credit

Hvis du har tid til overs, eller vil prøve deg på noe hjemme, se om du får til det her:

**Lag et `PATCH`-endepunkt** som oppdaterer *noen* felter og lar resten stå uforandret.
`PUT` erstatter hele objektet. `PATCH` lar deg bare sende inn det som skal endres.

Du må finne ut hvordan gjøre alle feltene valgfrie, og hvordan se forskjell på "klienten
sendte `null`" og "klienten nevnte ikke dette feltet i det hele tatt". Du får ett hint:
`model_dump` og `exclude_unset`.

Hvis du sitter fast har 
[FastAPI-dokumentasjonen](https://fastapi.tiangolo.com/tutorial/body-updates/#partial-updates-with-patch)
svaret. Prøv selv før du titter.
