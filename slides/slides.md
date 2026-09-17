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

# Bygg et CRUD-API med FastAPI

### En workshop om HTTP, FastAPI og API-design

<!--
Velkommen! Kort om deg selv.

Si tydelig: dette er en gjør-workshop, ikke en se-på-workshop. Alle skal ha en
bærbar oppe og kode med. Vi bygger et ekte, fungerende API i løpet av dagen.

Nevn tidsbudsjett: ca. 2,5-3 timer med en pause. Hvis vi går bakpå, sier du det høyt
og kutter heller forklaring enn kode -- folk lærer mest av å skrive selv.
-->

---

## Hva skal vi bygge?

- Et HTTP-API: noe et annet program kan snakke med for å lese og skrive data
- CRUD: opprett, les, oppdater, slett
- Interaktiv dokumentasjon vi ikke skriver selv
- Validering vi (nesten) ikke skriver selv

<!--
Dette er pitchen. Ikke gå i detalj her -- det kommer et helt steg om "hva er et API".
Poenget nå er å gi et bilde av hva vi lander på til slutt, sånn at resten av dagen
har et sted å bygge mot.
-->

---

## Forkunnskaper

- Python: funksjoner, dicts, lister, enkle klasser
- **Ikke** nødvendig: HTTP, APIer, CRUD, REST -- alt dette er innhold i dag
- Nye konsepter forklares når de dukker opp (dekoratorer, typeannotasjoner, `Annotated`)

<!--
Spør gjerne rommet: hvem har skrevet et API før? Hvem vet hva CRUD står for?
Kalibrer tempoet etter svaret. Denne workshopen er skrevet for at færre enn
halvparten vet hva CRUD er -- det er helt normalt og forventet.
-->

---

## Hvordan vi jobber

- **Du velger domene** (steg 4). Eksemplene her bruker Pokémon.
- **Skriv koden selv.** Ikke kopier fra slidene, ikke la Copilot skrive den.
- **Observer → hvorfor?** Vi bryter ting med vilje, og spør hvorfor etterpå.

<!--
Dette er den viktigste sliden i hele decket for hvordan dagen kommer til å kjennes.
Understrek at det er greit å velge noe annet enn Pokémon -- kaffe, brettspill,
hendelseslogger er alle gode. Den ekstra jobben med å "oversette" fra eksemplene
er faktisk bra for læringen.

Nevn også: hele workshopen finnes som en selvgående håndbok (zensical-siden) hvis
noen henger etter eller vil gå i sitt eget tempo -- den er en trygg fallback, ikke
plan A.
-->

---

## Mens jeg snakker: gjør dette nå

1. Lag et nytt repo: [github.com/new](https://github.com/new)
2. Åpne et Coder-workspace fra det

Steg 1 har ingen kode -- god tid til å bli klar før vi faktisk skal skrive noe.

<!--
Dette er en ren logistikk-slide. Poenget er at oppsett-tiden (git-repo + Coder-
workspace, som normalt tar noen minutter og involverer venting) skjer i bakgrunnen
mens du holder steg 1, som er rent snakk uten kode. Da er alle klare til å skrive
kode når steg 2 faktisk starter.

Si høyt: "dette trenger ikke være ferdig før om 20-30 minutter, bare sett det i
gang nå så det jobber i bakgrunnen." Gå rundt og hjelp de som sitter fast med
GitHub-innlogging eller lignende mens du snakker gjennom steg 1.
-->

---

<!-- _class: divider -->

# Steg 1

## Hva er et HTTP-API?

<!--
Ingen kode i dette steget. Rent snakke- og tavlesteg. Sett dere ned, lukk lokket,
la oss tegne litt.
-->

---

## Et funksjonskall over nettverk

En nettside: en URL som gir tilbake HTML, til et menneske.

Et API: en URL som gir tilbake **data**, til et **program**.

```
  FORESPØRSEL                          SVAR
  GET /pokemon/pikachu       ------>   200 OK
  (verb + path + headers)              {"slug": "pikachu", "type1": "electric"}
                             <------   (status code + headers + body)
```

<!--
Tegn dette på tavla mens du snakker, ikke bare vis sliden. Be folk tenke på en
nettside de har besøkt -- den gjorde akkurat dette, bare at svaret var HTML og
mottakeren en nettleser i stedet for et program.

Ramme å bruke hvis folk henger: "Dette er en SELECT du ikke kan skrive selv."
Eller: "Du har allerede brukt et API -- requests.get() i en notebook er nøyaktig
dette diagrammet."
-->

---

## Delene av en forespørsel

| Del | Hva er det |
|---|---|
| **Verb** | Hva du vil gjøre |
| **Path** | Hva du vil gjøre det *med* |
| **Body** | Data som skal håndteres |
| **Status code** | Gikk det bra, og hva skjedde? |

<!--
Alt vi snakker om resten av dagen er en av disse fire. Det er verdt å si det høyt:
"husk denne tabellen, vi kommer tilbake til hver rad."
-->

---

## Verb

| Verb | Betyr | SQL-analogi |
|---|---|---|
| `GET` | Gi meg det her | `SELECT` |
| `PUT` | Få denne tingen til å ha denne verdien | `UPDATE` |
| `POST` | Her er noe data, håndter det | `INSERT`/`UPDATE` |
| `DELETE` | Fjern det her | `DELETE` |

<!--
Du har kanskje hørt "PUT er for oppdateringer, POST er for å opprette noe nytt".
Det er en forenkling -- helt steg 5 handler om nettopp dette. Ikke gå i dybden nå,
bare plant fluesoppen.
-->

---

## Statuskoder

| Kode | Betyr | Eksempler |
|---|---|---|
| **2xx** | OK | `200`, `201`, `204` |
| **4xx** | *Du* gjorde feil | `404`, `422` |
| **5xx** | *Jeg* gjorde feil | `500` |

Statuskoden sier ofte hva klienten bør gjøre videre: 4xx betyr sannsynligvis ikke
lønner det seg å prøve på nytt, 5xx kan fint få et nytt forsøk.

<!--
Steg 7 blir konkret. Nå holder det med "det første sifferet betyr noe".
-->

---

## CRUD

> Let's not get into REST.

CRUD = fire ting du kan gjøre med et stykke data.

| | Operasjon | SQL | HTTP-verb |
|---|---|---|---|
| **C** | Create | `INSERT` | `PUT`/`POST` |
| **R** | Read | `SELECT` | `GET` |
| **U** | Update | `UPDATE` | `PUT` |
| **D** | Delete | `DELETE` | `DELETE` |

<!--
Hvis noen spør om REST: "det er skrevet hele bøker om det, vi gidder ikke bruke tid
på det i dag." Vi kaller det CRUD over HTTP, som er ærligere og også som oftest det
folk egentlig mener når de sier REST-API.

Hvis SQL-kolonnen gir mening for noen i rommet, forstår de allerede CRUD -- de har
gjort alle fire i årevis, bare ikke over et nettverk.
-->

---

## To detaljer å huske

- **To typer "Read":** hent én, eller hent en liste. Forskjellige stier,
  forskjellige returtyper.
- **Create og Update kan være samme operasjon.** `PUT /pokemon/pikachu` opprettet
  eller oppdaterte, avhengig av om den fantes. Dette er med vilje -- steg 5.

<!--
Dette er den ene setningen i hele workshopen som er en reell mening, ikke bare et
faktum om HTTP: "opprett og oppdater kan være samme endepunkt." Kom tilbake til
denne setningen i steg 5.
-->

---

## Hva gjør et rammeverk for deg?

Tenk deg at du bare hadde Python, ingen bibliotek. `PUT /pokemon/pikachu`:

1. Aksepter en TCP-forbindelse, les bytes til headerne er ferdige
2. Parse forespørselslinja
3. Match stien mot rutene dine, hent ut path-parameteret
4. Prosent-dekoding og annet fjas
5. Parse body som JSON
6. **Valider dataene mot et skjema**
7. **Kall funksjonen som gjør arbeidet**
8. Serialiser svaret til JSON
9. Skriv status, headers, body tilbake
10. Gjør alt dette samtidig, for flere klienter, uten å kræsje

<!--
Ta imot forslag fra rommet før du viser listen -- spør "hva må dere gjøre selv hvis
dere skulle bygget dette fra et rått socket?" La dem streve litt.

De eneste punktene som er DIN jobb er 6 og 7 (uthevet). Resten er rammeverkets jobb.
FastAPI går enda lengre: for punkt 6 er alt du trenger klasser og typeannotasjoner.
-->

---

## FastAPI, spesifikt

1. **Vanlige Python-funksjoner.** Én dekorator sier hvilket verb + sti.
2. **Typeannotasjoner som gjør noe.** Validering, feilmeldinger, parsing -- gratis.
3. **Dokumentasjonen skriver seg selv.**

```python
@app.get("/pokemon")
async def list_pokemon() -> list[Pokemon]:
    return everything
```

<!--
Dette er de tre punktene som selger FastAPI. Alle tre kommer til å bli konkrete i
løpet av de neste tre stegene -- ikke prøv å overbevise nå, bare varsle at det
kommer.

Nok snakk -- åpne laptopene.
-->

---

<!-- _class: divider -->

# Steg 2

## Prosjektoppsett

<!--
Kort steg. Mens uv laster ned ting kan du gå litt rundt og se at alle får det til.
-->

---

## Installer `uv`

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` håndterer dependency-versjoner og virtuelle Python-miljøer. Mye enklere enn
`pip` + `venv`.

(Sitter du i Coder? Dette er ferdig installert i workspace.)

<!--
Windows-folk: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
(stå klar til å hjelpe hvis noen sitter på Windows uten WSL)
-->

---

## Lag et prosjekt

```bash
uv init fastapi-workshop
cd fastapi-workshop
uv add "fastapi[standard]"
```

Du har nå `pyproject.toml`, `uv.lock`, en `.venv`, og én Python-fil (`main.py`).

Behold `main.py`, men slett innholdet -- det bytter vi ut i neste steg.

<!--
[standard] drar inn uvicorn (webserveren), fastapi-cli (kommandoene vi bruker),
httpx (testing), jinja2/python-multipart (templates/forms, bruker vi ikke i dag).
Den eneste egentlig nødvendige er uvicorn.
-->

---

## Sjekk at det virket

```bash
uv run python -c "import fastapi; print(fastapi.__version__)"
```

Fikk du et versjonsnummer? Da er du klar.

<!--
Gå rundt nå og sjekk at alle er på grønt før du går videre. Dette er det siste
punktet der "alle er synkronisert" faktisk betyr noe -- fra nå av bygger alle sitt
eget API, og det er helt greit at de drar litt fra hverandre i tempo.
-->

---

<!-- _class: divider -->

# Steg 3

## Hello world

<!--
Første kode. Skriv den selv på skjermen mens de skriver med deg -- ikke lim inn.
-->

---

## Fem linjer kode

```python
# main.py
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
```

```bash
uv run fastapi dev
```

<!--
Skriv den fra scratch på skjermen. Poenget er ikke hastighet, det er at alle ser
hver linje bli født.
-->

---

## Test den

```bash
curl http://localhost:8000/
```

```json
{"message":"Hello World"}
```

Gratulerer -- dette er et API. Et program snakket HTTP med programmet ditt og fikk
data tilbake.

<!--
La den kjøre i ett terminalvindu, åpne et nytt for curl. Dette mønsteret (server i
ett vindu, kall i et annet) gjelder resten av dagen.
-->

---

## Hva betyr koden?

`app = FastAPI()`
: Objektet som representerer APIet. Husker alle ruter, kaller riktig funksjon.

`@app.get("/")`
: En **dekorator**. Sier: kall denne funksjonen når det kommer en GET til `/`.
  Du kaller aldri `root()` selv -- det er webserverens jobb.

`async def`
: Ikke relevant i dag. Lar serveren gjøre annet arbeid mens funksjonen venter på
  noe (en database, et annet API). Ingenting vi skriver i dag venter på noe.

<!--
Legg merke til: ingen kall til root() noe sted i koden. Dette er den viktigste
mentale vendingen i webprogrammering -- du skriver funksjonen og gir den bort,
du kaller den ikke selv.
-->

---

## Dokumentasjonen

Åpne [http://localhost:8000/docs](http://localhost:8000/docs) i nettleseren.

- Interaktiv side, med endepunktet ditt listet
- **Ingen skrev denne siden.** Den er generert fra koden.
- Se også `/openapi.json` -- maskinlesbar beskrivelse, det `/docs` faktisk viser

<!--
Dette er throughlinen i hele workshopen: hver gang vi legger til noe, sjekker vi
/docs og ser hva som endret seg. Hvis den ser feil eller tynn ut, er det et reelt
signal om at noe mangler i koden.
-->

---

## Observer → hvorfor?

Endre meldingen i koden. Lagre. Kall `curl` igjen -- **uten å restarte noe**.

Den endret seg. Hvorfor? Og hva skjer om du prøver å nå serveren fra en annen
maskin på nettverket?

<!--
SVAR: fastapi dev overvåker filene og restarter automatisk. Den binder seg også
bare til 127.0.0.1 (localhost) -- en bevisst sikkerhetsdefault, siden dev-modus har
bekvemmeligheter du ikke vil ha eksponert. Produksjonsmodus (fastapi run) gjør
motsatt: binder 0.0.0.0, reloader ikke.
-->

---

<!-- _class: divider -->

# Steg 4

## Datamodell og et GET-endepunkt

<!--
Her velger alle domene. Gi dem litt tid, sjekk at ingen sitter fast på valget.
-->

---

## Velg et domene

| Domene | Datafelter |
|---|---|
| **Pokémon** | navn, type |
| Kaffeoppskrifter | bønnetype, metode, malingsgrad |
| Hendelseslogg | tittel, tidspunkt, alvorlighetsgrad |
| Brettspill | tittel, antall spillere, spilletid, rating |

Minst ett felt bør ha et begrenset sett med verdier (til enums senere).

<!--
Anbefal noe annet enn Pokémon -- den ekstra oversettingsjobben hjelper læringen.
Løsningsforslaget og eksemplene i dag bruker Pokémon.
-->

---

## Beskriv datamodellen

```python
from pydantic import BaseModel


class Pokemon(BaseModel):
    display_name: str
    type1: str
    type2: str | None = None
```

Tenk SQL: en tabelldefinisjon med tre kolonner, der den siste er nullable.

<!--
Pydantic ble installert sammen med FastAPI[standard]. BaseModel er superklassen alle
modellene våre kommer til å arve fra i dag.
-->

---

## Python-syntaks

`class Pokemon(BaseModel)`
: En klassedefinisjon som *arver* fra Pydantics `BaseModel`.

`display_name: str`
: En **typeannotasjon**. I vanlig Python: kun for editoren. I FastAPI/Pydantic:
  validering, feilmeldinger, serialisering, dokumentasjon -- gratis.

`type2: str | None = None`
: `str | None` betyr streng **eller** `None`. `= None` gjør feltet valgfritt.

<!--
Dette er det sentrale konseptet for hele dagen: typeannotasjoner er ikke pynt.
FastAPI leser dem og gjør ting med dem. Understrek dette hver gang det er relevant
fremover.
-->

---

## Datalageret vårt

```python
datastore = [
    Pokemon(display_name="Pikachu", type1="electric"),
    Pokemon(display_name="Skarmory", type1="steel", type2="flying"),
]
```

Dette *er* databasen din i dag. Alt forsvinner ved restart. (Hint til neste gang.)

<!--
Ikke gjem denne begrensningen -- si det rett ut nå, og igjen i steg 8. En ekte
database er neste workshop.
-->

---

## Server listen

```python
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

<!--
Pydantic-objektene ble JSON uten at vi skrev noen serialiseringskode. Sjekk /docs
sammen med rommet -- endepunktet har nå et skjema, generert fra returtypen.
-->

---

## Observer → hvorfor?

Slett `-> list[Pokemon]`. Se på `/docs` igjen. Skjemaet er borte.

Sett den tilbake, men returner `[{"tull": "ball"}]` i stedet for `datastore`.
Kall endepunktet. Hva skjer?

<!--
SVAR: FastAPI leser annotasjonen ved kjøretid og bruker den til to ting:
1) serialisering + validering av responsen, 2) generering av docs. Den er ikke bare
dokumentasjon for utvikleren -- det er en levende del av koden. Det gale svaret gir
en 500-feil fra serveren, fordi du lovet list[Pokemon] og brøt løftet.
-->

---

## Et begrenset sett med verdier

```python
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

```python
class Pokemon(BaseModel):
    display_name: str
    type1: Type          # ikke str
    type2: Type | None = None
```

<!--
StrEnum kommer fra standardbiblioteket (3.11+). Type.FIRE == "fire" er sant, så
JSON-konvertering er smertefri. Sjekk /docs -- feltet er nå en dropdown.
-->

---

## Filtrering

```python
@app.get("/pokemon")
async def get_all_pokemon(type: Type | None = None) -> list[Pokemon]:
    if type is None:
        return datastore
    return [p for p in datastore if type in (p.type1, p.type2)]
```

```bash
curl 'http://localhost:8000/pokemon?type=flying'
```

Et **query-parameter**: et funksjonsargument som ikke er del av stien.

<!--
Alt du gjør er å legge til et argument til funksjonen. FastAPI ser at "type" ikke
står i {braces} i dekoratoren, og gjør det til et query-parameter automatisk.
-->

---

## Observer → hvorfor?

```bash
curl -i 'http://localhost:8000/pokemon?type=cardboard'
```

Les hele responsen. Hvor kommer feilmeldingen fra? Kjørte funksjonen din?

<!--
SVAR: 422 Unprocessable Entity. Funksjonen kjørte aldri -- validering skjer først.
detail[].loc peker på nøyaktig hvilket felt som var feil ("query", "type").

Bonus-spørsmål hvis tid: fjern defaultverdien (= None). Hva skjer i /docs, og hva
skjer om du kaller uten parameteret? Svar: parameteret blir påkrevd -- FastAPI ser
også på defaultverdier, ikke bare typer.
-->

---

## Sjekkpunkt: `main.py` så langt

```python
from enum import StrEnum
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Type(StrEnum):
    ELECTRIC = "electric"; FIRE = "fire"; WATER = "water"; GRASS = "grass"
    FLYING = "flying"; PSYCHIC = "psychic"; STEEL = "steel"; ICE = "ice"

class Pokemon(BaseModel):
    display_name: str
    type1: Type
    type2: Type | None = None

datastore = [Pokemon(display_name="Pikachu", type1="electric")]

@app.get("/pokemon")
async def get_all_pokemon(type: Type | None = None) -> list[Pokemon]:
    if type is None:
        return datastore
    return [p for p in datastore if type in (p.type1, p.type2)]
```

<!--
Gi rommet 30 sekunder til å diffe mot sin egen kode. Dette er R-en i CRUD, ferdig.
Neste steg er en liten tankepause før vi skriver mer kode.
-->

---

<!-- _class: divider -->

# Steg 5

## Identifikatorer -- hvem bestemmer?

<!--
Ingen kode i dette steget! Si det høyt. Dette er det ene stedet i dag hvor vi
faktisk diskuterer design, ikke bare bygger.
-->

---

## Regelen du kanskje har hørt

> "POST lager nye objekter, PUT oppdaterer dem"

Sant for en hel haug med APIer. **Ingen regel.**

<!--
La denne påstanden stå litt i lufta. Spør: er det noen som har hørt dette før?
Hvem har brukt det som en fast regel? Vi kommer straks til å nyansere det.
-->

---

## Hva specen faktisk sier

| | Betyr | Idempotent? |
|---|---|---|
| **PUT** | "Ressursen på *denne URLen* skal bli lik dette" | Ja |
| **POST** | "Her er data. Håndter det etter egne regler" | Nei |

Ingen av definisjonene sier noe om å opprette eller oppdatere.

<!--
Idempotent: gjør du det flere ganger, er effekten den samme som å gjøre det én
gang. d["a"] = 1 er idempotent, list.append(1) er ikke.

Dette er ikke en akademisk detalj -- nettverk er upålitelige. Timer et idempotent
kall ut, kan klienten bare prøve på nytt uten bekymring. Er kallet ikke idempotent,
er ikke dette trygt.
-->

---

## Det egentlige spørsmålet

> Hvem bestemmer identifikatoren -- altså hvilken URL et nytt objekt skal ha?

<!--
Dette er kjernen i hele steget. Alt følger av svaret på dette spørsmålet, ikke av
hvilket verb som "egentlig" oppretter noe.
-->

---

## A: Klienten velger

```python
@app.put("/pokemon/{slug}")
async def put_pokemon(slug, update):
    ...  # oppretter hvis det ikke finnes, oppdaterer hvis det gjør
```

Dette kalles en **upsert**. Opprett og oppdater = samme operasjon = ett endepunkt.

Idempotens gratis. Ingen 409 Conflict å håndtere.

<!--
Passer for Pokémon, kaffe, brettspill, git-repoer -- alt med et navn klienten
allerede kjenner. Er dette valget riktig for domenet ditt, gjør du bare ett
PUT-endepunkt fremover.
-->

---

## Konsekvens: identifikatoren må tåle en URL

Med POST og navn-som-ID, hva skjer med:

- `Mr. Mime` eller `Type: Null` (ja, ekte Pokémon-navn -- mellomrom i URLer?)
- `Flabébé` (to forskjellige Unicode-kodepunkt for é...)
- `Ho-oh` vs. `Ho-Oh` (kun forskjell i casing)

<!--
Alle disse gir stygge/ulogiske URLer, duplikate data, eller verre. Håndtering av
dette krever regler for å oversette navn til noe URL-vennlig -- det er akkurat det
en "slug" er (URL-sikker, lowercase, bindestreker). Vi kommer tilbake til dette i
steg 6 når vi skal begrense path-parameteret.
-->

---

## B: Klienten kan ikke velge

Hendelser, logginnslag, bestillinger: ingen naturlig nøkkel, og to identiske
datapunkter kan være helt gyldig.

```
POST /incidents            ------>   201 Created
{"title": "Database down"}           Location: /incidents/0f8b...
                           <------   {"id": "0f8b...", "title": "..."}
```

Her er "POST oppretter" **sant** -- ikke fordi POST betyr det, men fordi serveren
eier identifikatoren.

<!--
Klienten kan ikke vite URLen på forhånd, så PUT-som-upsert fungerer ikke lenger.
POST + Location-header er svaret: serveren finner på en ID og forteller klienten
hvor tingen landet.

Live-demo hvis tid: main_autoid.py
  uv run fastapi dev main_autoid.py --port 8001
  curl -i -X POST localhost:8001/incidents -H 'content-type: application/json' \
    -d '{"title": "Database down", "severity": "high"}'
Kjør den to ganger -- to hendelser, to forskjellige IDer. Vis Location-headeren med -i.
-->

---

## Velg din variant

**Klienten velger (mest vanlig)**
: Ett PUT-endepunkt, upsert-semantikk. Pokémon, kaffe, brettspill.

**Server-generert ID (logg-aktige domener)**
: POST for å opprette, PUT bare for å oppdatere (404 på ukjent ID).
  Hendelseslogger, ordre.

<!--
Be alle bestemme seg nå, før vi går videre. De resterende stegene er skrevet for
slug-varianten -- server-ID-folket må justere litt selv (POST i stedet for PUT for
create, 404 på ID i stedet for slug-validering).
-->

---

<!-- _class: divider -->

# Steg 6

## Request bodies

<!--
Nå skriver vi kode igjen. Dette er steget der validering virkelig skinner.
-->

---

## To modeller

```python
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

Kun forskjell: `slug`. URLen sier allerede hvem det er -- body trenger ikke gjenta.

<!--
Er ikke dette duplisert kode? Jo, litt -- men å splitte input/output-modeller er et
mønster du ser igjen og igjen i API-utvikling: du vil ikke returnere interne felter,
og servergenererte felter (created_at, IDer) skal serveren styre, ikke klienten.
-->

---

## Datastore blir en dict

```python
datastore: dict[str, Pokemon] = {
    "pikachu": Pokemon(display_name="Pikachu", type1="electric"),
}
```

```python
@app.get("/pokemon")
async def get_all_pokemon(type: Type | None = None) -> list[Pokemon]:
    all_pokemon = list(datastore.values())
    ...
```

<!--
Nå som objektene har IDer, trenger vi en nøkkel å lagre dem under. Husk å bytte ut
.values() i GET-all-endepunktet -- lett å glemme.
-->

---

## Upsert-endepunktet

```python
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

<!--
Legg merke til de to argumentene: slug er et path-parameter ({slug} i stien),
update er request body (en Pydantic-modell). Regelen: navngitt i stien →
path-parameter. Pydantic-modell → body. Alt annet → query-parameter.
-->

---

## Test det

```bash
curl -X PUT http://localhost:8000/pokemon/charmander \
  -H 'content-type: application/json' \
  -d '{"display_name": "Charmander", "type1": "fire"}'
```

```json
{"slug":"charmander","display_name":"Charmander","type1":"fire","type2":null}
```

Bruk gjerne `/docs` i stedet for curl -- **Try it out** genererer formularet fra
modellen.

<!--
Alt av parsing, validering og feilrapportering skjer FØR koden din blir kalt. Dette
er verdt å si høyt igjen -- det er det samme prinsippet som i steg 4, nå på en body
i stedet for et query-parameter.
-->

---

## Observer → hvorfor?

```bash
curl -i -X PUT http://localhost:8000/pokemon/pikachu \
  -H 'content-type: application/json' \
  -d '{"display_name": "", "type1": "cardboard"}'
```

Les hele responsen.

1. Hvilken statuskode? Hvorfor ikke `400 Bad Request`?
2. Hvordan kan klienten bruke svaret til å rette feilen?

<!--
SVAR 1: 422 Unprocessable Entity. 400 hadde ikke vært feil, men 422 er mer
spesifikt -- forespørselen var korrekt utformet, men brøt en regel.

SVAR 2: se på "loc"-arrayen i responsen -- ["body", "type1"] er en STI til feltet
som var feil. Fungerer på nøstede felter/lister også. Detail er en liste, så flere
feil rapporteres i ett svar.
-->

---

## Validering med `Field`

```python
class PokemonUpdate(BaseModel):
    display_name: str = Field(
        min_length=1,
        max_length=64,
        description="Shown to humans.",
        examples=["Vulpix"],
    )
    type1: Type = Field(description="The primary type.")
```

| Argument | Gjelder | Effekt |
|---|---|---|
| `min_length`/`max_length` | strenger, lister | Lengdebegrensning |
| `ge`/`le`/`gt`/`lt` | tall | Verdibegrensning |
| `pattern` | strenger | Regex-sjekk |

<!--
Legg til noe i egen modell nå: lengdebegrensning på et fritekstfelt, gyldig
tallområde på et tallfelt. Send garbage-requesten på nytt og se feillisten vokse.
Sjekk /docs også -- descriptions og examples vises der.
-->

---

## Begrens path-parameteret også

```python
from typing import Annotated
from fastapi import Path

SLUG_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"
SlugPath = Annotated[str, Path(pattern=SLUG_PATTERN)]
```

```python
@app.put("/pokemon/{slug}")
async def put_pokemon(slug: SlugPath, update: PokemonUpdate) -> Pokemon:
    ...
```

<!--
Akkurat nå gir PUT /pokemon/pikachu og PUT /pokemon/Pikachu deg to forskjellige
rader. SlugPath fikser det.

Annotated[str, X] betyr "en str, pluss ekstra info X". Typesjekkere ignorerer X,
FastAPI bruker den. Vi bruker den her (i stedet for slug: str = Path(...)) fordi et
argument uten defaultverdi ikke kan komme etter et argument med defaultverdi i
Python -- update har ingen default, så Path(...) som default ville krasjet.
-->

---

## Observer → hvorfor?

Fire kall, gjett status før du kjører:

```bash
# stor bokstav                  # mellomrom
PUT /pokemon/Pikachu             PUT /pokemon/mr%20mime
# slash                         # slash, escaped
PUT /pokemon/Porygon/Z           PUT /pokemon/Porygon%2FZ
```

Og etterpå: er `GET /pokemon` tom?

<!--
SVAR: 422, 422, 404, 404. De to første er valideringsfeil -- de når endepunktet,
men mønsteret avviser dem (loc: ["path", "slug"]). De to siste når aldri ruten:
/pokemon/{slug} matcher bare ETT segment, og %2F hjelper ikke fordi stien allerede
er prosent-dekodet før ruting skjer. Man kan ALDRI ha en slash i ett path-segment.

GET /pokemon er tom etter alle fire -- ingen av dem ble skrevet til lageret. Dette
er selve poenget fra steg 5: en dårlig identifikator er nå umulig å lagre, ikke
bare ubeleilig.
-->

---

<!-- _class: divider -->

# Steg 7

## Statuskoder

<!--
Tre nivåer av vanskelighetsgrad. Bygg GET-single og DELETE her.
-->

---

## Lett: suksess, men ikke 200

```python
from fastapi import status


@app.delete("/pokemon/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pokemon(slug: SlugPath) -> None:
    del datastore[slug]
```

En sletting har ikke noe fornuftig å returnere. `204 No Content`.

<!--
Når et endepunkt alltid returnerer samme kode, sett den på dekoratoren. status.HTTP_204_NO_CONTENT er bare tallet 204, spelt ut for lesbarhet.
-->

---

## Observer → hvorfor?

```bash
curl -i -X DELETE http://localhost:8000/pokemon/no-such-mon
```

(før du legger inn en sjekk) -- hva får klienten? Hva ser du i terminalen?

<!--
SVAR: 500 Internal Server Error, med en KeyError i stacktracen. FastAPI hadde ingen
god måte å mappe dette til riktig statuskode. Klienten kan ikke skille "ingen slik
Pokémon" fra "databasen tok fyr" -- det er DIN jobb å avgjøre at en manglende rad
er en 404, ikke rammeverkets.
-->

---

## Middels: feilhåndtering

```python
from fastapi import HTTPException, status


@app.delete("/pokemon/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pokemon(slug: SlugPath) -> None:
    if slug not in datastore:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Pokémon with slug {slug!r}")
    del datastore[slug]
```

`raise`, ikke `return` -- bobler automatisk opp gjennom kall-lag.

<!--
Bygg GET single på samme måte nå (samme 404-mønster). Merk hvor kort feillisten er
-- et navn-som-ID-design hadde også trengt en 409 for duplikate navn og en 400 for
path/body-motsigelse. Steg 5 designet bort begge. Den beste feilhåndteringen er en
feil som ikke kan skje.
-->

---

## Vanskelig: statuskoden er ukjent til koden har kjørt

```python
async def put_pokemon(slug: SlugPath, update: PokemonUpdate, response: Response) -> Pokemon:
    if slug not in datastore:
        response.status_code = status.HTTP_201_CREATED
    stored = Pokemon(slug=slug, display_name=update.display_name,
                      type1=update.type1, type2=update.type2)
    datastore[slug] = stored
    return stored
```

`Response` som argument: FastAPI gir deg respons-objektet, du justerer metadata.

<!--
PUTen er en upsert. 201 hvis vi oppretter, 200 hvis vi oppdaterer -- og vi vet ikke
hvilken før vi har sett i lageret. Response er verken path, query eller body -- en
fjerde type parameter FastAPI kjenner på typen.

201 første gang, 200 andre gang -- kjør curl to ganger for å vise det live.
-->

---

## Manuell dokumentasjon

201-statusen er ikke i `/docs` -- kun 200 og 422 er der.

```python
@app.put(
    "/pokemon/{slug}",
    responses={201: {"description": "Created a new Pokémon"}},
)
```

<!--
SVAR (hvorfor): dokumentasjonen bygges ved å INSPISERE koden, ikke ved å kjøre den.
Alt som kan leses ut fra signaturen alene (typer, dekoratorer) dokumenteres
automatisk. En status satt inne i en if-branch er usynlig for rammeverket -- den må
deklareres manuelt. Samme gjelder 404-ene fra raise-linjene.
-->

---

## Siste touch

```python
@app.get("/pokemon", summary="List Pokémon, optionally filtered by type")
async def get_all_pokemon(type: Type | None = None) -> list[Pokemon]:
    ...
```

`summary=` gir kort beskrivelse. En **docstring** blir lengre beskrivelse (Markdown).

**Bonus:** prøv `POST /pokemon` -- APIet har ingen POST. Hva skjer?

<!--
SVAR (bonus): 405 Method Not Allowed, ikke 404. Stien finnes, den svarer bare ikke
på det verbet. 404 = "tingen finnes ikke", 405 = "tingen finnes, feil verb". Gratis,
fra ruting.
-->

---

## Hva har vi laget?

| | Endepunkt | Statuskoder |
|---|---|---|
| **C**/**U** | `PUT /pokemon/{slug}` | 201, 200, 422 |
| **R** | `GET /pokemon`, `GET /pokemon/{slug}` | 200, 404, 422 |
| **D** | `DELETE /pokemon/{slug}` | 204, 404, 422 |

Dokumentert, validert, riktige statuskoder. Et komplett CRUD-API.

<!--
La denne stå litt. Sammenlign med sliden fra "hva skal vi bygge?" helt i starten --
si "dette er akkurat det vi lovet, og det er alt sammen deres egen kode."
-->

---

<!-- _class: divider -->

# Steg 8

## Oppsummering

<!--
Rolig avslutning. Ikke rush -- dette er der læringen "setter seg".
-->

---

## Hva du bygde

- Fire endepunkter som til sammen utgjør CRUD
- Validert input -- feil avvises før koden din ser dem
- Riktige statuskoder, inkludert noen rammeverket ikke kunne gjette
- Interaktiv dokumentasjon du ikke skrev

**Den ene setningen å ta med seg:** du skrev typer, og fikk oppførsel.

<!--
Én StrEnum ga validering, feilmeldinger OG en dropdown i docs. Én -> list[Pokemon]
ga serialisering OG et skjema. Det er selve trikset.
-->

---

## Hva mangler #1: dataene forsvinner

"Databasen" er en dict i minnet. Ingenting overlever en restart.

Hvor ville du opprettet databaseforbindelser? Hva med transaksjoner? Hvor mye kode
må endres for å bruke SQLite i stedet?

```python
async def get_pokemon(slug: SlugPath, store: PokemonStore) -> Pokemon:
    ...
```

Løsningen kalles **dependency injection** -- koden sier hva den trenger, FastAPI
sørger for at det er der.

<!--
Ikke løs dette nå -- dette ER teaseren for neste workshop. Nevn at det fort blir
mye duplisert kode uten DI: én global forbindelse = APIet håndterer bare én
forespørsel av gangen, én forbindelse per kall = trege endepunkter.
-->

---

## Hva mangler #2: ingen tester

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_put_is_idempotent():
    assert client.put("/pokemon/vulpix", json=VULPIX).status_code == 201
    assert client.put("/pokemon/vulpix", json=VULPIX).status_code == 200
    assert len(client.get("/pokemon").json()) == 1
```

Vi testet manuelt hele dagen. `TestClient` gjør det automatisk, uten en kjørende
server.

<!--
Dette beviser faktisk noe steg 5 bare PÅSTOD -- at PUT-upsert er idempotent. Tre
linjer kode, én ordentlig test.
-->

---

## Ekstraoppgave

Lag et **`PATCH`**-endepunkt som oppdaterer *noen* felter, lar resten stå.

Hint: `model_dump(exclude_unset=True)`.

FastAPI-dokumentasjonen har svaret hvis du sitter fast -- prøv selv først.

<!--
Denne er for de som er raskt ferdig eller vil fortsette hjemme. Ikke bruk
workshop-tid på å gå gjennom løsningen med mindre alle er skikkelig i mål og har
tid til overs.
-->

---

<!-- _class: lead -->

## Neste workshop

Persistens (ekte database), dependency injection, og testing.

Bevisst ikke bygget ut i dag -- så det er en grunn til å komme tilbake.

<!--
Selg denne litt! Ikke bare "det kommer mer" -- si konkret hva som venter og hvorfor
det er den naturlige neste tingen (samme kode, samme API, men nå persistent og
testet).
-->

---

<!-- _class: lead -->
<!-- _paginate: false -->

# Takk for i dag!

Håndboka finnes fortsatt om du vil gå gjennom stegene på egen hånd, eller sjekke
koden din mot fasiten.

### github.com/imre-kerr-sb1/fastapi-workshop

<!--
Pek til docs/-mappa i repoet (zensical serve). Spør om det er noe siste spørsmål,
og rund av. Bra jobbet!
-->
