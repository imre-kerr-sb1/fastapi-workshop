# 1. Hva er et HTTP-API?

## En funksjon du kan kalle over et nettverk

Du har allerede brukt HTTP hvis du har sett på en nettside noen gang. Nettlesere snakker HTTP med en server
for å få tilbake HTML som de viser til en bruker. APIer fungerer på samme måte: Et program snakker
HTTP med et API for å sende inn data, få maskinen i den andre enden til å kjøre kode, og for å få data
tilbake.

Slik ser det ut for de som liker diagrammer:

```
  FORESPØRSEL                          SVAR
  GET /pokemon/pikachu       ------>   200 OK
  (verb + path + headers)              {"slug": "pikachu", "type1": "electric"}
                             <------   (status code + headers + body)
```

Forspørsel og svar har forskjellige deler, og alt vi bryr oss om i HTTP omhandler en eller flere av disse:

| Del | Hva er det |
|---|---|
| **Verb** | Hva du vil gjøre |
| **Path** | Hva du vil gjøre det *med* |
| **Request body** | Data som skal håndteres |
| **Request headers** | Metadata om forespørselen |
| **Response body** | Data som APIet sender tilbake |
| **Response headers** | Metadata om svaret |
| **Status code** | Gikk det bra, og hva skjedde? |

### Verb

Det finnes flere, men i denne workshopen bryr vi oss om disse fire.

| Verb | Betyr | SQL-analogi |
|---|---|---|
| `GET` | Gi meg det her | `SELECT` |
| `PUT` | Få denne tingen til å ha denne verdien | `UPDATE` |
| `POST` | Her er noe data, håndter det | `INSERT`/`UPDATE` |
| `DELETE` | Fjern det her | `DELETE` |

Du kan ha hørt at `PUT` er for oppdateringer og `POST` er for å opprette noe nytt. 
Det er en forenkling, og [steg 5](05-identifiers.md) kommer til å handle om akkurat dette.

### Statuskoder

Tre sifre, det første er viktigst:

| Kode | Betyr | Eksempler vi kommer til å se |
|---|---|---|
| **2xx** | OK | `200 OK`, `201 Created`, `204 No Content` |
| **4xx** | *Du* gjorde feil | `404 Not Found`, `422 Unprocessable Content` |
| **5xx** | *Jeg* gjorde feil | `500 Internal Server Error` |

Statuskoder informerer ofte hva klienten skal gjøre videre. 4xx betyr at det sannsynligvis
ikke vil hjelpe å prøve på nytt, 5xx kan fint få et nytt forsøk.

## CRUD

!!! note "La oss ikke snakke om REST"
    Du har kanskje hørt om REST-APIer, og kanskje du tenker at det er det vi lager.
    Du har kanskje også sett bloggposter, diskusjoner, stack overflow-spørsmål e.l. om hva
    REST er og ikke er. Det er skrevet hele bøker om det her, og vi gidder ikke bruke tid på
    det nå. 
    
    I stedet velger vi å være ærlige og kalle det her **CRUD over HTTP**. Det er umulig å
    misforstå, og er som oftest det folk egentlig snakker om når de sier "REST-API".

CRUD er fire ting du kan gjøre med et stykke data. APIet vårt kommer da til å være et tynt lag
oppå et datalager (for eksempel en database).

| | Operasjon | SQL | HTTP-verb | Eksempler |
|---|---|---|---|---|
| **C** | Create | `INSERT` | `PUT` eller `POST` | `PUT /pokemon/pikachu` |
| **R** | Read | `SELECT` | `GET` | `GET /pokemon/pikachu`, `GET /pokemon` |
| **U** | Update | `UPDATE` | `PUT` | `PUT /pokemon/pikachu` |
| **D** | Delete | `DELETE` | `DELETE` | `DELETE /pokemon/pikachu` |

To detaljer å merke seg i tabellen, som vi kommer til å komme tilbake til:

- **To typer "Read"** Hent én, eller hent en liste. Disse har forskjellige stier og forskjellige
    returtyper. Vi kommer til å lage listevarianten først, og enkeltvarianten når vi snakker om
    [statuskoder](07-status-codes.md).
- **Create og Update er samme operasjon** Begge to har `PUT /pokemon/pikachu` som eksempel. Dette
    er med vilje, men ditt API kommer ikke nødvendigvis til å se slik ut. 

## Hva skal du med et rammeverk?

Tenk deg at du bare hadde Python, uten noen bibliotek eller rammeverk overhodet. Hvordan ser
`PUT /pokemon/pikachu` ut? En liten to-do-liste:

1. Aksepter en TCP-forbindelse, og les bytes fra den til du har fått ut alle headerne.
2. Parse den første linja — `PUT /pokemon/pikachu HTTP/1.1`
3. Match stien mot de forskjellige stiene i APIet ditt, og bruk regex for å hente ut et path-parameter (`pikachu`).
4. Prosent-dekoding og annet fjas om hvordan HTTP-stier skal håndteres
5. Parse innkommende data som JSON.
6. **Valider at innkommende data stemmer overens med schemaet du har definert**
7. **Kall funksjonen som faktisk gjør arbeidet (lagrer noe)**
8. Serialiser python-objektet ditt til JSON
9. Skriv statuslinje, headers og JSON-data tilbake i TCP-forbindelsen.
10. Lukk forbindelsen hvis du har lyst til å være ineffektiv. Ellers bør du holde den åpen, 
    men passe på at forespørsler ikke går i beina på hverandre. 
11. Du har også kanskje flere klienter samtidig. Så vi har flere TCP-forbindelser som må sjongleres.
    Og hva enn du gjør må serveren aldri kræsje, så *alt* må ha feilhåndtering.

De eneste punktene du burde trenge å bry deg om er de uthevede. Et rammeverk gjør resten for deg.
FastAPI går enda lengre, og sikrer at det eneste du trenger for punkt 6 er at du har skrevet klasser
og typeannotasjoner.

## FastAPI

Tre punkter som gjør FastAPI spesielt raskt og enkelt å utvikle i:

**1. Du skriver helt vanlige Python-funksjoner.** Det eneste du trenger i tillegg er én dekorator
over funksjonen som sier hvilket verb + sti funksjonen svarer på.

```python
@app.get("/pokemon")
async def list_pokemon() -> list[Pokemon]:
    return everything
```

**2. Typeannotasjoner som gjør noe.** `display_name: str` er ikke bare for autocomplete i VSCode
og en siste avsjekk med `mypy`/`ty`. FastAPI bruker det for å validere requests og forkaste
dårlige data før koden din i det hele tatt ser dem. Du skriver en type, og får parsing, 
validering og fornuftige feilmeldinger gratis. (Det underliggende biblioteket heter 
[Pydantic](https://docs.pydantic.dev/) og lar deg skrive enda mer detaljert valideringslogikk 
hvis du skulle ønske det.)

**3. Dokumentasjonen skriver seg selv.** FastAPI bruker også typeannotasjonene dine til å generere
interaktiv *og* maskinlesbar API-dokumentasjon som aldri havner ute av synk med koden. Vi kommer til
å være mye innom `/docs` for å se alle måtene kodeendringene våre reflekteres der.

Forhåpentligvis høres alt dette supert ut. Nok snakk, på tide å kode.
