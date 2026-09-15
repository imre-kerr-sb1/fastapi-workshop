# 3. Hello world

Veldig lite kode (men skriv den selv), og en del snakking om hva alt betyr.

## Fem linjer kode

Bytt ut hele innholdet i `main.py` med dette:

```python title="main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
```

Så kjører du:

```bash
uv run fastapi dev
```

Du bør se noe sånt som:

```
 ⚡️ Starting FastAPI in development mode

 🐍 Using import string: main:app (auto-discovered)

 🌐 Server started at http://127.0.0.1:8000
    Documentation at http://127.0.0.1:8000/docs

INFO:     Will watch for changes in these directories: ['/your/path']
INFO:     Application startup complete.
```

La det kjøre, og åpne en ny terminal. 

```bash
curl http://localhost:8000/
```

```json title="output"
{"message":"Hello World"}
```

Gratulerer, du har laget et API! Et program (`curl`) snakket HTTP med programmet ditt og fikk data tilbake.

## Forklaring av koden

Tre ting å være oppmerksom på:

`app = FastAPI()`

: Et objekt som representerer applikasjonen din (APIet ditt). Dette objektet husker på alle
  funksjonene du har registrert som *ruter* i APIet, og kaller riktig funksjon når en forespørsel
  kommer inn.

`@app.get("/")`

: Dette er en **dekorator**: En Python-sak som tar inn en funksjon og gjør noe med den. Noen dekoratorer
  modifiserer funksjoner, mens denne bare forteller `app` om at funksjonen finnes og at det er denne som skal
  kalles når det kommer en `GET`-forespørsel til stien `/`.

  Legg merke til at det ikke står noen kall til funksjonen `root` noe sted i koden din. Å kalle funksjonen er
  ikke din jobb. Du bare skriver den og forteller FastAPI om den, så er det webserveren sin oppgave å kalle den.

`async def`

: Ikke relevant for nå, men hvis du er nysgjerrig: `async def` betyr at funksjonen kan *suspenderes* mens
  den venter på at noe skal skje. Ofte skal et API vente på svar fra en eller annen prosess som kan kjøre i
  bakgrunnen, f.eks. et kall til et annet API eller en databasespørring. `async def` sammen med `await` lar serveren
  gjøre annet arbeid (svare på andre forespørsler) mens man venter.

Returverdien fra `root` er en dict, mens svaret du fikk var JSON, uten at du trengte å kalle `json.dumps` eller
andre funksjoner. FastAPI håndterte serialisering for deg.

## Dokumentasjon

La serveren fortsette å kjøre, og åpne [http://localhost:8000/docs](http://localhost:8000/docs) i nettleseren din.

Du skal se en interaktiv docs-side for APIet ditt. Her kan du se alle endepunktene dine (bare ett for øyeblikket),
du har knapper for å gjøre testkall, og kan se svaret rett i nettleseren uten å bruke `curl`.

**Denne siden skrev ikke du.** Den ble generert fra koden din, og alle tingene du legger til i APIet ditt
vil bli reflektert der. Derfor er det også en god idé å sjekke innom her hver gang du legger til noe. Ser det
tynt eller feil ut? Da er det sannsynligvis noe som mangler i koden!

Ta også en titt på dataene som ligger bak:

```bash
curl http://localhost:8000/openapi.json
```

```json
{"openapi":"3.1.0","info":{"title":"FastAPI","version":"0.1.0"},
 "paths":{"/":{"get":{"summary":"Root","operationId":"root__get", ...
```

Dette er et [OpenAPI](https://www.openapis.org/)-dokument — En maskinlesbar beskrivelse
av APIet ditt. `/docs` er bare fremvisning. OpenAPI brukes også av kodegeneratorer, testverktøy, Postman, 
og andre docs-fremvisere (ta for eksempel en titt på [https://localhost:8000/redoc](https://localhost:8000/redoc).)

!!! tip "Grei dokumentasjon ut av boksen, fantastisk dokumentasjon med litt innsats"
    Legg merke til at det står `/ Root` på endepunktet ditt. Dette ble hentet fra funksjonsnavnet, men det er
    ikke nødvendigvis det du har lyst til å vise til konsumenter. Prøv å legge til en docstring til funksjonen og se hva som skjer da.
