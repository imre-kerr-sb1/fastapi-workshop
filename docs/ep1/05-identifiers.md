# 5. Identifikatorer - Hvem bestemmer?

Ingen kode i dette steget.

## Regelen du kanskje har hørt

> "POST lager nye objekter, PUT oppdaterer dem"

Dette er sant for en hel haug med APIer, men er absolutt ingen regel.

Dette er hva [specen](https://www.rfc-editor.org/rfc/rfc9110) faktisk sier:

| | Hva det betyr | Idempotent? |
|---|---|---|
| **PUT** | "Få ressursen på *denne URLen* til å være lik det jeg sender inn" | Ja  |
| **POST** | "Her er noe data. Håndter det i følge dine egne regler" | Nei |

Ingen av disse definisjonene sier noe om å opprette eller oppdatere noe.

!!! tip "Idempotente operasjoner"
    En operasjon er idempotent hvis effekten av å gjøre den flere ganger er den samme som å gjøre den én gang.
    `d["a"] = 1` er idempotent; `list.append(1)` er ikke det.

    Dette er et viktig tema i API-design, fordi nettverk er upålitelige. Hvis et kall til et idempotent
    endepunkt timer ut eller feiler, kan klienten bare prøve på nytt. Hvis endepunktet ikke er idempotent, er ikke dette trygt.
    Da må man inn og sjekke hva effekten av det feilede kallet er, som kan være vanskelig eller til og med umulig.

Så "opprett eller oppdater" er ikke riktig spørsmål å stille. Spørsmålet du bør stille er:

> Hvem bestemmer hva identifikatoren er, altså hvilken URL nye objekter skal finnes på?

## A: Klienten velger

Noen ganger har tingen du skal lagre et navn som klienten allerede vet om. Hvis dette navnet kan brukes som en
unik identifikator, kan den også vite URLen. Og hvis den allerede vet URLen, kan den gjøre en PUT. Uavhengig av om
det finnes noe der allerede eller ikke:

```python
@app.put("/pokemon/{slug}")
async def put_pokemon(slug, update):
    ...  # oppdater hvis det finnes noe her alt, oppdater hvis ikke
```

Dette kalles en **upsert**, og det betyr at oppretting og oppdatering er *samme operasjon*. Du skriver
ett endepunkt som håndterer begge deler. Dette betyr at du får idempotens helt gratis.

Det betyr også at identifikatoren nødvendigvis er trygg for URLer. URLer kan ikke inneholde vilkårlige tegn. La oss si
du gikk for et annet design: POST til `/pokemon`, og navnet brukes som identifikator. Hva skjer med:

- Mr. Mime eller Type: Null (ja det er en Pokémon som heter det)
- Flabébé (Visste du at det finnes to codepoints for é i Unicode?)
- Noen er uforsiktige med casing, og sender inn "Ho-oh" (ikke "Ho-Oh") 

I alle disse tilfellene risikerer du stygge og ulogiske URLer, duplikate data eller verre. Å håndtere dette
involverer å lage regler for hvordan du oversetter navn til noe som kan brukes i en URL.

## B: Klienten kan ikke velge

Ikke alle domener har naturlige navn på ting. Og selv om man kunne latt klienten sende inn noe vilkårlig, er det ikke sikkert dette er en god idé.

Hendelser, logginnslag og bestillinger er alle eksempler på dette. De er bare et stykke data uten en naturlig nøkkel, og to prikk like datapunkter kan i noen tilfeller være helt gyldig.

I disse tilfellene kan ikke klienten vite URLen på forhånd, og PUT som upsert fungerer ikke lenger.

**Det er her du har lyst til å bruke POST.** Klienten POSTer til URLen som representerer en samling med data,
APIet finner på en identifikator, og sender denne tilbake. Gjerne både i responsdataene og i Location-headeren:

```
POST /incidents            ------>   201 Created
{"title": "Database down"}           Location: /incidents/0f8b...
                           <------   {"id": "0f8b...", "title": "Database down"}
```

Her ser vi et eksempel der "POST oppretter" **er** sant. Dette er ikke noe iboende i HTTP-verbet POST, men
en konsekvens av hva som gir mening for akkurat dette domenet. 

??? example "Et fullt eksempel på POST-varianten"
    [Løsningsforslaget](solution-key.md) inkluderer `main_autoid.py`, et komplett eksempel for domenet
    "hendelseslogg". Det er verdt å ta en titt på oppførselen hvis domenet ditt har samme form:

    ```bash
    uv run fastapi dev main_autoid.py --port 8001

    curl -i -X POST localhost:8001/incidents \
      -H 'content-type: application/json' \
      -d '{"title": "Database down", "severity": "high"}'
    ```

    `-i` får curl til å vise respons-headers, inkludert `Location` som vi er opptatt av. Noen ting å merke seg:

    - **Kjør kallet flere ganger.** To hendelser, to forskjellige IDer. Dette gir mening i dette domenet, siden
      en database faktisk kan gå ned både én og to ganger.
    - **Location-headeren er nyttig** Kopier stien og gjør et GET-kall. Du får tilbake samme objektet som du sendte inn.
      Uten dette ville du måttet gjette (umulig), eller hente hele listen med hendelser og lete.
    - **PUT-endepunktet er kun for oppdatering**, og gir 404 Not Found for en ukjent ID. Ikke lenger en upsert, bare en update.

## Hva passer ditt domene?

Velg en variant for domenet ditt før du fortsetter:

=== "Klienten velger (mest vanlig)"

    Bare lag et PUT-endepunkt, og gi det upsert-semantikk. Passer for Pokémon, kaffe, brettspill,
    git-repoer, og mye mer.

    Løsningsforslaget og eksemplene fremover gjør dette.

=== "Server-generert id (logg-aktige domener)"

    Lag to endepunkter: POST for å opprette ting og PUT for å oppdatere dem. Passer for domener hvor
    dataene er "en ting skjedde", ikke "en ting finnes". Hendelseslogger, ordre, alle domener hvor to distinkte
    ting kan se prikk like ut.

    Noen detaljer blir annerledes med denne varianten. POST-endepunktet ditt må finne på ID-er selv, 
    og sende tilbake en Location-header. PUT-endepunktet ditt må svare 404 for ukjente IDer. Se på 
    `main_autoid.py` i løsningsforslaget hvis du sitter fast.
