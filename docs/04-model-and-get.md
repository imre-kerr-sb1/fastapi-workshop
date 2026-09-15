# 4. Datamodell og et GET-endepunkt

På tide å servere litt mer ekte data. Her har du et valg å gjøre.

## Velg et domene

APIet ditt handler forhåpentligvis om ett eller annet som interesserer deg. Hvis det er noen
knusktørre bankgreier er det helt greit (I don't judge), men det kan egentlig være hva som helst.
Så lenge det er noe du gidder å tenke på de neste to timene.

Hvis du sliter med å velge har du noen eksempler her:

| Domene | Datafelter |
|---|---|
| **Pokémon** | navn, type |
| Kaffeoppskrifter | bønnetype, metode, malingsgrad... |
| Hendelseslogg | tittel, tidspunkt, alvorlighetsgrad |
| Brettspill | tittel, antall spillere, forventet spilletid, rating |

Det er en fordel hvis minst ett av feltene kommer fra et begrenset sett med verdier. Dette kommer vi til å bruke
når vi snakker om enums og validering av disse.

Løsningsforslaget bruker Pokémon, og det gjør også eksemplene underveis. Jeg anbefaler å velge noe annet,
siden det ekstra mentale arbeidet med å "oversette" eksemplene er friksjon som hjelper læring.

## Beskriv datamodellen din med en klasse

FastAPI lener seg tungt på *modeller*. Dette er klasser som forteller hvilke felter dataobjektene dine har,
og hvilken type de er. Dette baserer seg på [Pydantic](https://docs.pydantic.dev/), som ble installert sammen med FastAPI.

```python title="main.py"
from pydantic import BaseModel


class Pokemon(BaseModel):
    display_name: str
    type1: str
    type2: str | None = None
```

Hvis du er vant med SQL, kan du tenke på dette som en tabelldefinisjon med tre kolonner der den siste er nullable.

!!! tip "Python-syntaks"
    `class Pokemon(BaseModel)`

    : Dette er en klassedefinisjon: En beskrivelse av et objekt man kan lage. Denne *arver* fra en annen
      klasse `BaseModel` som kommer fra Pydantic.

    `display_name: str`

    : En **typeannotasjon**. Denne sier noe om hva slags data som hører hjemme her. I standard Python er dette kun
      til for editoren og verktøy som `ty`/`mypy`, og blir ignorert når programmet kjører. Dette er **ikke** tilfelle
      med FastAPI og Pydantic. Typeannotasjoner er et av de sentrale konseptene som får FastAPI til å fungere. Du
      skriver dem, og får gratis validering, feilmeldinger, serialisering/deserialisering, og dokumentasjon.

    `type2: str | None = None`

    : Her har vi også en typeannotasjon, `str | None`, som betyr at feltet kan inneholde en string **eller** være
      `None`. I tillegg har vi en defaultverdi (`None`), som gjør at det er gyldig å ikke spesifisere en verdi for
      `type2`. Uten denne måtte man eksplisitt sendt inn `null` når man skulle sende inn JSON til APIet.

Nå har du en klasse. Lag et par instanser for hånd og legg dem i en liste:

```python title="main.py"
datastore = [
    Pokemon(display_name="Pikachu", type1="electric"),
    Pokemon(display_name="Skarmory", type1="steel", type2="flying"),
]
```

!!! note "Ja, dette er databasen din"
    Alle endringer i den forsvinner hver gang serveren din restartes (ofte). En ekte database har vi ikke tid til
    i denne omgang. (Hint til hva som kommer neste gang.)

## Server listen din

Slett hello world-endepunktet, og bytt det ut med noe slikt:

```python title="main.py"
@app.get("/pokemon")
async def get_all_pokemon() -> list[Pokemon]:
    return datastore
```

```bash
curl http://localhost:8000/pokemon
```

```json
[{"display_name":"Pikachu","type1":"electric","type2":null},
 {"display_name":"Skarmory","type1":"steel","type2":"flying"}]
```

Pydantic-objektene dine kom nok en gang tilbake som JSON, og nok en gang skrev du ikke hvordan — 
det bare skjedde.

Ta en titt på `/docs` nå. Endepunktet ditt er der, og nå har det et schema. Hvilke felter, hvilke typer,
og alt du skrev var en typeannotasjon.

!!! question "Observer → hvorfor?"
    Slett typeannotasjonen for returverdien (`-> list[Pokemon]`), så du står igjen med
    `async def get_all_pokemon():`. Lagre, og se på docs-siden igjen.

    Skjemaet er borte. Alt siden sier er at den skal returnere noe JSON. Kall endepunktet, og observer at
    svaret ser likt ut.

    Så kan du prøve å ha typeannotasjonen der, men returnere [{"tull": "ball"}] i stedet. Se hva som skjer
    hvis du prøver å kalle APIet da. (Det kan hende du må se i loggen til `fastapi dev` for å få det fulle bildet.)

    Hvorfor har disse typeannotasjonene, som vanligvis ikke har noe å si ved kjøretid, så mye å si for hvordan
    FastAPI oppfører seg?

    ??? success "Svar"
        Fordi FastAPI leser dem ved kjøretid, og bruker dem til to oppgaver:

        1. **Serialisering av responsen**, og validering av at det du returnerte stemmer med det du sa
            du skulle returnere
        2. **Generering av docs**

        Typeannotasjonen er ikke bare dokumentasjon for utvikleren, og det er ikke bare en "test". Den er en levende
        del av koden, og garantien din for at dokumentasjon og valideringslogikk aldri kommer ut av synk med resten av
        koden din.

## Et begrenset sett med verdier

Hvis domenet ditt har et felt som kun kan inneholde et begrenset sett med verdier (Pokémon-typer, bryggemetoder,
sjangere), kan du bruke en *enum* for å få dokumentasjon og validering av dette. Hvis Pokémon-typefeltet er en string,
kan du fint motta eller returnere `"cardboard"`. Enums er kuren for dette:

```python title="main.py"
from enum import StrEnum


class Type(StrEnum):
    ELECTRIC = "electric"
    FIRE = "fire"
    WATER = "water"
    GRASS = "grass"
    FLYING = "flying"
    PSYCHIC = "psychic"
    STEEL = "steel"
    ICE = "ice"
```

Så bruker du den i domeneklassen din i stedet for `str`:

```python title="main.py" hl_lines="3 4"
class Pokemon(BaseModel):
    display_name: str
    type1: Type
    type2: Type | None = None
```

`StrEnum` kommer fra standardbiblioteket i Python (3.11+), og elementene i en slik *er* strenger, så
`Type.FIRE == "fire"` er sant, og de kan konverteres smertefritt til og fra strenger i JSON.

Sjekk `/docs`. Typen på feltet er oppdatert, og du kan til og med se hvilke verdier som er mulige.

## Filtrering

Et endepunkt som returnerer alle dataene i databasen din er fint det, men hva om brukeren har lyst til
å bare få et subsett av dem? Dette kan gjøres med et **query-parameter**. Du har sannsynligvis sett et før,
de ser sånn her ut i URLer: `?type=flying`.

Alt du trenger å gjøre for å ta inn et slikt parameter er å legge til et parameter til funksjonen din (NB!
Kun strenger, tall og lignende greier.)

```python title="main.py" hl_lines="2 3 4 5"
@app.get("/pokemon")
async def get_all_pokemon(type: Type | None = None) -> list[Pokemon]:
    if type is None:
        return datastore
    return [p for p in datastore if type in (p.type1, p.type2)]
```

```bash
curl 'http://localhost:8000/pokemon?type=flying'
```

```json
[{"display_name":"Skarmory","type1":"steel","type2":"flying"}]
```

Hvis du ikke sender inn et query-parameter får du alt, på grunn av defaultverdien.

!!! question "Observer → hvorfor?"
    To ting å prøve.

    Først kan du prøve å spørre om en enum-verdi som ikke finnes. Her må du bruke curl, siden Swagger UI ikke lar deg:

    ```bash
    curl -i 'http://localhost:8000/pokemon?type=cardboard'
    ```

    Les hele responsen. Hvor kommer denne feilmeldingen fra? Har funksjonen din kjørt i det hele tatt?

    Så kan du fjerne defaultverdien. Hva skjer i `/docs`, og hvorfor? Prøv å kalle endepunktet uten en verdi i query-parameteret (igjen med curl).

    ??? success "Svar"
        Du får status `422 Unprocessable Entity`, og meldingskroppen er noe sånt som:

        ```json
        {"detail":[{"type":"enum","loc":["query","type"],
                    "msg":"Input should be 'electric', 'fire', ...",
                    "input":"cardboard"}]}
        ```

        Funksjonen din kjørte aldri. Validering skjer først, og hvis det du sender inn ikke stemmer vil FastAPI
        svare med en feilmelding som peker på nøyaktig hva som er feil.

        Hvis du fjerner defaultverdien, vil docs-siden si at parameteret er påkrevd. FastAPI leser ikke bare
        typeannotasjoner, det ser også på default-verdier. Et manglende query-parameter uten defaultverdi er
        en valideringsfeil på lik linje med en feil enum-verdi.

## Hvor er vi

`main.py` bør se ca slik ut:

??? example "Checkpoint: main.py så langt"
    ```python title="main.py"
    from enum import StrEnum

    from fastapi import FastAPI
    from pydantic import BaseModel

    app = FastAPI()


    class Type(StrEnum):
        ELECTRIC = "electric"
        FIRE = "fire"
        WATER = "water"
        GRASS = "grass"
        FLYING = "flying"
        PSYCHIC = "psychic"
        STEEL = "steel"
        ICE = "ice"


    class Pokemon(BaseModel):
        display_name: str
        type1: Type
        type2: Type | None = None


    datastore = [
        Pokemon(display_name="Pikachu", type1="electric"),
        Pokemon(display_name="Skarmory", type1="steel", type2="flying"),
    ]


    @app.get("/pokemon")
    async def get_all_pokemon(type: Type | None = None) -> list[Pokemon]:
        if type is None:
            return datastore
        return [p for p in datastore if type in (p.type1, p.type2)]
    ```

Vi kan nå lese data, kanskje til og med filtrere dem. Dette er R-en i CRUD. Neste steg blir de andre
bokstavene, men først må vi ta en liten pause og snakke om identifikatorer. Dette vil informere hvordan
endepunktet for å opprette data vil se ut.
