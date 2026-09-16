# 7. Statuskoder

Alt du har skrevet så langt returnerer `200 OK`. Men det finnes mer spesifikke "OK"-koder
enn det, og det skal vi se på nå.

Vi skal se på tre forskjellige tilfeller:

## Lett: Suksess, men noe annet enn 200

En sletting som gikk bra har ikke noe fornuftig data å returnere. Ressursen finnes ikke
lenger, så det gir ikke mening å returnere det som akkurat ble slettet. `{"deleted": true}`
er bare støy. Riktig svar i slike tilfeller er `204 No Content`.

Når et endepunkt alltid returnerer samme status ved suksess, kan du skrive det i dekoratoren:

```python title="main.py"
@app.delete("/pokemon/{slug}", status_code=204)
async def delete_pokemon(slug: SlugPath) -> None:
    del datastore[slug]
```

Eller enda bedre, med en navngitt konstant:

```python title="main.py" hl_lines="1 3"
from fastapi import status


@app.delete("/pokemon/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pokemon(slug: SlugPath) -> None:
    del datastore[slug]
```

`status.HTTP_204_NO_CONTENT` er bare tallet `204`. Hvis du og alle på teamet ditt kan alle
HTTP-koder på rams kan du fint bare bruke tallet direkte.

Som alltid: sjekk docs. Statusen er dokumentert.

## Middels: Feilhåndtering i din egen kode

Det slette-endepunktet har en bug. Prøv å slette noe som ikke finnes.

!!! question "Observer → hvorfor?"
    ```bash
    curl -i -X DELETE http://localhost:8000/pokemon/no-such-mon
    ```

    Hva får klienten tilbake? Og hva ser du i loggen til serveren din? Nå er spørsmålet:
    Hvordan skal klienten forholde seg til dette?

    ??? success "Svar"
        `500 Internal Server Error`, og en stacktrace i terminalen som ender i
        `KeyError: 'no-such-mon'`.

        `del datastore[slug]` kastet en feil, og FastAPI hadde ingen god måte å mappe
        dette til riktig HTTP-status. Fra klientens perspektiv kan en `500` bety hva som
        helst: midlertidig hikke, databasen tok fyr... Ingen ting tilsier at det faktisk
        var klienten som sendte inn en ID som ikke fantes. 

For å sende en bedre feilmelding bruker du `HTTPException`:

```python title="main.py"
from fastapi import HTTPException, status


@app.delete("/pokemon/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pokemon(slug: SlugPath) -> None:
    if slug not in datastore:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Pokémon with slug {slug!r}")
    del datastore[slug]
```

`raise`, ikk `return`. Kjekt hvis du har flere lag med funksjonskall. Feilmeldingen bobler opp
automatisk, uten at du trenger å træ den gjennom alle lagene manuelt.

Nå kan du lage "GET single"-endepunktet på samme måte:

```python title="main.py"
@app.get("/pokemon/{slug}")
async def get_pokemon(slug: SlugPath) -> Pokemon:
    if slug not in datastore:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Pokémon with slug {slug!r}")
    return datastore[slug]
```

```bash
curl -i http://localhost:8000/pokemon/no-such-mon
```

```json
{"detail":"No Pokémon with slug 'no-such-mon'"}
```

## Vanskelig: Suksess, men statuskoden er ikke kjent før koden din har kjørt

PUTen din er en upsert. Hva bør den returnere?

- Opprettet noe nytt → **201 Created**
- Oppdaterte noe som fantes allerede → **200 OK**

Det er ingen ting galt med `200 OK` for begge disse. Men vi prøver å være så spesifikke som
mulig (og lære FastAPI).

FastAPI vet ikke hva som skjer inni funksjonen din, så dette må du returnere manuelt.
Måten du gjør dette er å ta inn **responsen** som et argument, og sette statuskoden på
denne selv.

```python title="main.py" hl_lines="1 4 7 8"
from fastapi import FastAPI, HTTPException, Path, Response, status

@app.put("/pokemon/{slug}")
async def put_pokemon(slug: SlugPath, update: PokemonUpdate, response: Response) -> Pokemon:
    # 201 if we're creating, 200 if we're replacing. We can't know which until we look,
    # so the status code gets set here rather than on the decorator.
    if slug not in datastore:
        response.status_code = status.HTTP_201_CREATED

    stored = Pokemon(
        slug=slug,
        display_name=update.display_name,
        type1=update.type1,
        type2=update.type2,
    )
    datastore[slug] = stored
    return stored
```

Vi snakket tidligere om forskjellige funksjonsargumenter og hvordan FastAPI håndterer dem.
`Response` håndteres spesielt. Det er verken et path-parameter, query-parameter eller request
body. I stedet gir FastAPI deg respons-objektet som den kommer til å sende tilbake. Merk at
du fortsatt bare returnerer modellobjektet som vanlig. Du modifiserer bare metadataene.

```bash
curl -s -o /dev/null -w '%{http_code}\n' -X PUT localhost:8000/pokemon/vulpix \
  -H 'content-type: application/json' -d '{"display_name":"Vulpix","type1":"fire"}'
# 201

curl -s -o /dev/null -w '%{http_code}\n' -X PUT localhost:8000/pokemon/vulpix \
  -H 'content-type: application/json' -d '{"display_name":"Vulpix","type1":"fire"}'
# 200
```

Først 201, så 200, og `GET /pokemon` har kun én Vulpix.

## Manuell dokumentasjon

!!! question "Observer → hvorfor?"
    PUT-endepunktet ditt returnerer nå HTTP 201 noen ganger. Se i dokumentasjonen til endepunktet.

    201 **er ikke dokumentert**. De eneste statusene som står der er 200 og 422.

    Hvorfor ser ikke FastAPI 201-statusen, når den så alt annet? Og hva forteller det deg om
    begrensningene til den automatiske dokumentasjonen?

    ??? success "Svar"
        Fordi dokumentasjonen bygges ved å **inspisere koden, ikke ved å kjøre den**.
        FastAPI leser signaturen til funksjonen din, men den kan ikke vite hva som skjer når
        den faktisk kjører.

        Hvis du vil ha dette dokumentert, må du fortelle FastAPI om det selv:

        ```python
        @app.put(
            "/pokemon/{slug}",
            responses={201: {"description": "Created a new Pokémon"}},
        )
        ```

        Dette er et generelt prinsipp. Hvis det kan leses kun ut fra signaturen til endepunktene
        dine — Input-/returtyper, dekoratorer — Kan FastAPI dokumentere det automatisk. Alt
        annet må legges inn manuelt.

        Gjør det samme for 404-statusene i GET-single og DELETE. Dette er `raise`-linjer inne
        i funksjonene dine, og således også usynlige for rammeverket.

        ```python
        @app.get(
            "/pokemon/{slug}",
            responses={404: {"description": "No Pokémon with that slug"}},
        )
        ```

## Litt mer manuell dokumentasjon

To ting til som kan ta dokumentasjonen din til neste nivå:

```python title="main.py"
@app.get("/pokemon", summary="List Pokémon, optionally filtered by type")
async def get_all_pokemon(type: Type | None = None) -> list[Pokemon]:
    ...
```

`summary=` blir en kort beskrivelse i endepunktslista, og erstatter defaulten som bare er
funksjonsnavnet. En **docstring** blir en lengre beskrivelse som vises som Markdown:

```python title="main.py"
async def put_pokemon(...) -> Pokemon:
    """Create or replace -- the whole write side of the API.

    Send this twice and you get the same single Pokémon, which is exactly what PUT
    promises and exactly why we don't need a POST.
    """
```

Du kan også legge inn en tittel og beskrivelse (og mer!) for selve APIet:

```python title="main.py"
app = FastAPI(
    title="Pokédex",
    summary="A toy CRUD API, built to demonstrate rather too many FastAPI features.",
)
```

!!! question "Observer → hvorfor? (siste nå)"
    APIet ditt har ingen POST-endepunkter. Hva skjer hvis en klient prøver allikevel?

    ```bash
    curl -i -X POST localhost:8000/pokemon \
      -H 'content-type: application/json' -d '{}'
    ```

    ??? success "Svar"
        `405 Method Not Allowed`. Ikke 404! Stien `/pokemon` finnes, men den svarer ikke på
        det verbet. 404 er "tingen finnes ikke", mens 405 er "tingen finnes, men feil verb".

## Hva har vi laget?

Du har et fullstendig CRUD-API:

| | Endepunkt | Statuskoder |
|---|---|---|
| **C**/**U** | `PUT /pokemon/{slug}` | 201, 200, 422 |
| **R** | `GET /pokemon`, `GET /pokemon/{slug}` | 200, 404, 422 |
| **D** | `DELETE /pokemon/{slug}` | 204, 404, 422 |

Dokumentert, validert, riktige statuskoder. Rett og slett etter alle kunstens regler.
