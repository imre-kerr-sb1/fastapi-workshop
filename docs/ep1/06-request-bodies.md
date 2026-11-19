# 6. Request bodies

På tide å motta data fra klienten. I dette steget kommer vi til å se enda mer av styrken til
FastAPIs bruk av typer, og hvordan dette igjen hjelper både klienter og API-utviklere.

Eksemplene antar at du har gått for "klienten velger ID"-varianten i 
[steg 5](./05-identifiers.md). Hvis ikke er det meste likt, men du trenger både et POST- og
et PUT-endepunkt. Validering av IDer utgår i så fall.

## To modeller

Nå trenger du to modeller. En for det du tar inn, og en for det du returnerer.

```python title="main.py"
class PokemonUpdate(BaseModel):
    display_name: str
    type1: Type
    type2: Type | None = None


class Pokemon(BaseModel):
    slug: str
    display_name: str
    type1: Type
    type2: Type | None = None
```

Den eneste forskjellen er feltet `slug`. Poenget er at ved en PUT til `/pokemon/{slug}`
inneholder URLen allerede IDen. Hvis vi har den to steder, er det mulig for disse to å motsi
hverandre.

!!! tip "Er ikke dette duplisert kode?"
    Å splitte input- og output-modeller er et mønster du vil se igjen og igjen i API-utvikling.
    Årsakene er mange: Dupliserings-argumentet over, du vil ikke returnere hemmelige eller 
    interne felter, servergenererte felter som created_at eller automatiske IDer skal styres
    av serveren.

    Det går an å gjøre koden kortere og mer DRY ved hjelp av *arv*. Vi holder det enkelt for nå,
    men dette kan være aktuelt å gjøre i fremtiden. Bare vær obs på hva som skjer hvis 
    input-modellen også inneholder felter som ikke finnes i output-modellen.

Datalageret ditt må også endres. Nå som objektene dine har IDer, må du gå fra en liste til en
dict:

```python title="main.py"
datastore: dict[str, Pokemon] = {
    "pikachu": Pokemon(slug="pikachu", display_name="Pikachu", type1="electric"),
    "skarmory": Pokemon(slug="skarmory", display_name="Skarmory", type1="steel", type2="flying"),
}
```

"GET all"-endepunktet skal fortsatt returnere en liste, så bruk `.values()`:

```python title="main.py" hl_lines="3"
@app.get("/pokemon")
async def get_all_pokemon(type: Type | None = None) -> list[Pokemon]:
    all_pokemon = list(datastore.values())
    if type is None:
        return all_pokemon
    return [p for p in all_pokemon if type in (p.type1, p.type2)]
```

## Upsert-endepunktet

```python title="main.py"
@app.put("/pokemon/{slug}")
async def put_pokemon(slug: str, update: PokemonUpdate) -> Pokemon:
    stored = Pokemon(
        slug=slug,
        display_name=update.display_name,
        type1=update.type1,
        type2=update.type2,
    )
    datastore[slug] = stored
    return stored
```

Legg godt merke til de to argumentene. Begge to er argumenter, men de kommer fra helt
forskjellige steder.

- **`slug: str`** er et **path-parameter**, siden det står `{slug}` i stien til endepunktet.
- **`update: PokemonUpdate`** er **request body**, siden typen er en Pydantic-modell.

Dette er regelen FastAPI bruker for å bestemme: navngitt i stien → path-parameter. 
Pydantic-model → request body. Noe annet → et query-parameter.

Og som alltid: Alt av parsing, validering, og eventuell feilrapportering til klienten skjer **før** koden din blir kalt

Test koden nå:

```bash
curl -X PUT http://localhost:8000/pokemon/charmander \
  -H 'content-type: application/json' \
  -d '{"display_name": "Charmander", "type1": "fire"}'
```

```json
{"slug":"charmander","display_name":"Charmander","type1":"fire","type2":null}
```

Så kan du gjøre `curl http://localhost:8000/pokemon` og se at det du sendte inn har 
blitt lagret.

!!! tip "Bruk `/docs` i stedet for curl"
    Åpne docs-siden, og trykk **Try it out**. Du får et skjema du kan fylle ut med alle
    feltene i modellen, og en dropdown for eventuelle enum-verdier. Mye mer behagelig enn å
    manuelt skrive inn JSON i terminalen.

## Send inn dårlige data



!!! question "Observer → hvorfor?"
    ```bash
    curl -i -X PUT http://localhost:8000/pokemon/pikachu \
      -H 'content-type: application/json' \
      -d '{"display_name": "", "type1": "cardboard"}'
    ```

    Les hele responsen, ikke bare statusen.

    1. Hvilken statuskode fikk du? Hvorfor akkurat denne og ikke bare `400 Bad Request`?
    2. Hvordan kan klienten bruke informasjonen i svaret til å rette opp feil?

    ??? success "Svar"
        **1.** `422 Unprocessable Entity`. `400` hadde ikke vært feil i henhold til specen,
        men `422` er mer spesifikt. Det betyr at forespørselen var riktig utformet, men brøt
        en eller annen regel som gjorde at mottakeren (APIet) nektet å prosessere den.
        
        **2.** Se på `loc`-arrayen i responsen:

        ```json
        {"detail": [
          {"type": "enum", "loc": ["body", "type1"],
           "msg": "Input should be 'electric', 'fire', ...", "input": "cardboard"}
        ]}
        ```

        `["body", "type1"]` er en *sti* til feltet som er feil. Hvilken del av forespørselen,
        Og hvilket felt. Det fungerer med nøstede felter og lister også: Hvis du har en liste
        med angrep Pokémonen kan, kunne du fått en valideringsfeil for
        `["body", "moves", 2, "power"]`.

        Legg også merke til at `detail` er en liste. Har du flere valideringsfeil, svarer
        FastAPI med alle sammen.

## Validering for de andre feltene

Enum-feltene gir allerede noe validering. Men det finnes et fritekstfelt også. For å få
validering av dette kan vi bruke `Field`:

```python title="main.py" hl_lines="4 5 6 7 8 9 10 11 12 13"
from pydantic import BaseModel, Field


class PokemonUpdate(BaseModel):
    display_name: str = Field(
        min_length=1,
        max_length=64,
        description="Shown to humans. May change, and may collide with others.",
        examples=["Vulpix"],
    )
    type1: Type = Field(description="The primary type.")
    type2: Type | None = Field(
        default=None, description="The secondary type, for dual-type Pokémon."
    )
```

`Field` beriker et felt med regler og metadata. Dette er de mest nyttige:

| Argument | Gjelder for | Detaljer |
|---|---|---|
| `min_length` / `max_length` | strenger, lister |
| `ge` / `le` / `gt` / `lt` | tall |
| `pattern` | strenger | Sjekker feltet mot en regex |
| `default` | * | Gjør feltet valgfritt |
| `description` | * | Vises i `/docs` |
| `examples` | * | Vises i `/docs` |

Legg til noen i din modell også. Lengdebegrensning på fritekstfelt, gyldige tallverdier...
Så kan du prøve å sende inn ugyldige data og se feilmeldingene bli flere og mer spesifikke.

Sjekk docs-siden også. Beskrivelsene dine vises, skjemaet er ferdigutfylt med eksemplene dine,
og begrensningene er dokumentert.

## Begrens path-parameteret også

I steg 5 sa vi at en ID må være trygg for URLer. Selv om dette teknisk sett er oppfylt siden
vi får IDen inn fra en URL, er det sannsynligvis lurt å begrense det ytterligere. Akkurat nå
vil `PUT /pokemon/pikachu` og `PUT /pokemon/Pikachu` gi deg to stykker.

Her må vi bruke litt guffen syntaks, men man blir vant til det:

```python title="main.py"
from typing import Annotated

from fastapi import FastAPI, Path

SLUG_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"
SlugPath = Annotated[str, Path(pattern=SLUG_PATTERN, description="The Pokémon's slug.")]
```

Så bruker du `SlugPath` i stedet for `str`:

```python title="main.py" hl_lines="2"
@app.put("/pokemon/{slug}")
async def put_pokemon(slug: SlugPath, update: PokemonUpdate) -> Pokemon:
    ...
```

!!! tip "`Annotated`"
    `Annotated[str, X]` betyr **"en `str`, pluss følgende ekstra informasjon: `X`"**. 
    Typesjekkingsverktøy ignorerer `X` og ser bare på `str`, mens andre verktøy (som FastAPI)
    bruker den.

    Så koden over kan leses som "en streng, og forresten kommer den fra URL-stien og må
    matche denne regexen". Vi gir den et navn `SlugPath` sånn at vi kan skrive den gufne koden
    ett sted og bruke noe lesbart ellers.

    Du lurer kanskje på hvorfor vi ikke bare bruker `slug: str = Path(pattern=...)` sånn som 
    med feltene i modellen vår. Dette er på grunn av reglene for funksjonsargumenter i Python. 
    Et argument med defaultverdi kan ikke komme før et argument uten.

Nå er de dårlige IDene umulig å sende inn.

Oppdater feltet i modellen din også. Denne gangen bare med `Field`:

```python title="main.py"
class Pokemon(BaseModel):
    slug: str = Field(pattern=SLUG_PATTERN, examples=["vulpix-alola"])
    ...
```

Dette er belte og bukseseler, med gratis dokumentasjon på kjøpet. Glemmer du validering ett
sted i koden, kan dette redde deg.

## Hvor er vi nå?

Du kan opprette og oppdatere data, med input validert mot både typer og begrensninger,
og alt er dokumentert. Alle endepunkter returnerer status 200 med mindre de får inn dårlige
data.

Det siste punktet er et område som kan forbedres, og det skal vi se på i neste steg.
